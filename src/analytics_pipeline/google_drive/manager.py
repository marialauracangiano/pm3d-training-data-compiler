# src/analytics_pipeline/google_drive/manager.py
# from datetime import datetime, timedelta
from pathlib import Path
import shutil

from analytics_pipeline.google_drive.client import (
    get_drive_service,
    list_sheets_in_folder,
    download_sheet_as_csv,
)
from analytics_pipeline.config.logging_config import logger

class DriveManager:
    """
    High-level interface for interacting with Google Drive.
    Handles downloading files, caching folders, and converting spreadsheets to CSVs.
    """

    def __init__(self, service=None):
        # Create and store the Drive service when the manager is created
        self.service = service or get_drive_service()

    def download_folder(self, folder_id: str, output_folder: Path, ) -> Path:
        """
        Download all spreadsheets from a Google Drive folder into: data/biomass/<output_name>

        Parameters
        ----------
        folder_id : str
            Google Drive folder ID to download from.
        output_name : str
            Name of the local folder to save spreadsheets in.

        Returns
        -------
        Path : Local path to downloaded folder
        """
        output_folder = Path(output_folder)

        if output_folder.exists():
            shutil.rmtree(output_folder)
            
        output_folder.mkdir(parents=True, exist_ok=True)

        # ----------------------------------------------------
        # List spreadsheets
        # ----------------------------------------------------
        sheets = list_sheets_in_folder(folder_id, self.service)
        logger.info(f"Found {len(sheets)} sheet(s). Downloading...")

        # ----------------------------------------------------
        # Download each sheet as CSV
        # ----------------------------------------------------
        for sheet in sheets:
            name = sheet["name"]

            if "template" in name.lower():
                logger.info(f"Skipping template: {name}")
                continue

            download_sheet_as_csv(
                file_id=sheet["id"],
                file_name=name,
                mime_type=sheet["mimeType"],
                save_path=output_folder,
                drive_service=self.service,
            )

        logger.info(f"✅ All sheets downloaded to {output_folder}")
        return output_folder
