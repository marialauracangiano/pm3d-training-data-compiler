# src/analytics_pipeline/google_drive/client.py
import io
from pathlib import Path

import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.google_drive.auth import authenticate_google_api

GOOGLE_SHEET_MIME = "application/vnd.google-apps.spreadsheet"
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_drive_service():
    """
    Authenticate and return a Google Drive API service instance.
    """
    creds = authenticate_google_api()
    return build("drive", "v3", credentials=creds)


def _download_to_memory(request) -> io.BytesIO:
    """
    Download a Drive request into an in-memory buffer.
    """
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    return buffer


def list_sheets_in_folder(
    folder_id: str,
    drive_service=None,
) -> list[dict]:
    """
    List all Google Sheets in a given folder.

    Parameters
    ----------
        folder_id (str): ID of the Drive folder
        drive_service: optional authenticated Drive service
    Returns
    ----------
        list of dicts: each dict has 'id' and 'name' keys
    """
    if drive_service is None:
        drive_service = get_drive_service()

    query = f"'{folder_id}' in parents and trashed = false"

    results = (
        drive_service.files()
        .list(
            q=query,
            fields="files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )

    files = results.get("files", [])
    spreadsheets = [
        f
        for f in files
        if f["mimeType"]
        in {
            GOOGLE_SHEET_MIME,
            EXCEL_MIME,
        }
    ]

    logger.info("Found %d spreadsheet(s) in folder %s.", len(spreadsheets), folder_id)
    return spreadsheets


def download_sheet_as_csv(
    file_id: str,
    file_name: str,
    mime_type: str,
    save_path: Path | str,
    drive_service=None,
) -> Path:
    """
    Download a spreadsheet and save locally as CSV.

    Supports:
    - Google Sheets
    - Excel (.xlsx)

    Parameters
    ----------
        file_id (str): ID of the Google Sheet
        file_name (str): Name to save CSV as
        save_path (str or Path): folder to save CSV
        drive_service: optional authenticated Drive service
    Returns
    ----------
        Path to the downloaded CSV
    """
    if drive_service is None:
        drive_service = get_drive_service()

    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    output_file = save_path / f"{file_name}.csv"

    # --------------------------------------------------
    # Google Sheet -> export directly as CSV
    # --------------------------------------------------
    if mime_type == GOOGLE_SHEET_MIME:

        request = drive_service.files().export_media(
            fileId=file_id,
            mimeType="text/csv",
        )

        buffer = _download_to_memory(request)

        with output_file.open("wb") as f:
            f.write(buffer.read())

    # --------------------------------------------------
    # Excel file -> download then convert to CSV
    # --------------------------------------------------
    elif mime_type == (EXCEL_MIME):

        request = drive_service.files().get_media(fileId=file_id)

        buffer = _download_to_memory(request)

        df = pd.read_excel(buffer)
        df.to_csv(output_file, index=False)

    else:
        raise ValueError(f"Unsupported spreadsheet type: {mime_type}")

    # logger.info(f"Downloaded spreadsheet to %s", output_file)

    return output_file


def upload_file(
    local_path: Path | str,
    folder_id: str | None = None,
    mime_type="text/csv",
    drive_service=None,
) -> str:
    """
    Upload a local file to Google Drive.
    """
    if drive_service is None:
        drive_service = get_drive_service()

    local_path = Path(local_path)
    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")

    file_metadata = {"name": local_path.name}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(str(local_path), mimetype=mime_type)
    uploaded = (
        drive_service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, name",
            supportsAllDrives=True,
        )
        .execute()
    )

    logger.info("Uploaded '%s' to Drive (ID: %s)", local_path.name, uploaded["id"])
    return uploaded["id"]
