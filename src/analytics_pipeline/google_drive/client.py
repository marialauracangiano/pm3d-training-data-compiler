# src/analytics_pipeline/google_drive/client.py
import io
import pandas as pd
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from analytics_pipeline.google_drive.auth import authenticate_google_api
from analytics_pipeline.config.logging_config import logger


def get_drive_service():
    """
    Authenticate and return a Google Drive API service instance.
    """
    creds = authenticate_google_api()
    return build("drive", "v3", credentials=creds)


def list_sheets_in_folder(folder_id, drive_service=None):
    """
    List all Google Sheets in a given folder.
    
    Parameters:
        folder_id (str): ID of the Drive folder
        drive_service: optional authenticated Drive service
    Returns:
        list of dicts: each dict has 'id' and 'name' keys
    """
    if drive_service is None:
        drive_service = get_drive_service()

    query = (
        f"'{folder_id}' in parents and trashed = false"
    )

    results = drive_service.files().list(
        q=query,
        fields="files(id, name, mimeType)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    files = results.get("files", [])
    spreadsheet_files = [
        f for f in files
        if f["mimeType"] in {
            "application/vnd.google-apps.spreadsheet",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
    ]
    
    logger.info(f"Found {len(spreadsheet_files)} spreadsheet(s) in folder {folder_id}.")
    return spreadsheet_files


def download_sheet_as_csv(file_id, file_name, mime_type, save_path, drive_service=None):
    """
    Download a spreadsheet and save locally as CSV.

    Supports:
    - Google Sheets
    - Excel (.xlsx)
    
    Parameters:
        file_id (str): ID of the Google Sheet
        file_name (str): Name to save CSV as
        save_path (str or Path): folder to save CSV
        drive_service: optional authenticated Drive service
    Returns:
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
    if mime_type == "application/vnd.google-apps.spreadsheet":

        request = drive_service.files().export_media(
            fileId=file_id,
            mimeType="text/csv",
        )

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        fh.seek(0)

        with open(output_file, "wb") as f:
            f.write(fh.read())

    # --------------------------------------------------
    # Excel file -> download then convert to CSV
    # --------------------------------------------------
    elif mime_type == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):

        request = drive_service.files().get_media(
            fileId=file_id
        )

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        fh.seek(0)

        df = pd.read_excel(fh)

        df.to_csv(output_file, index=False)

    else:
        raise ValueError(
            f"Unsupported spreadsheet type: {mime_type}"
        )

    logger.info(f"Downloaded: {output_file}")

    return output_file


def upload_file(local_path, folder_id=None, mime_type="text/csv", drive_service=None):
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
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name",
        supportsAllDrives=True
    ).execute()

    logger.info(f"Uploaded '{local_path.name}' to Drive (ID: {uploaded['id']})")
    return uploaded["id"]
