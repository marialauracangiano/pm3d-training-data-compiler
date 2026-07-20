# src/analytics_pipeline/processing/acquisition/biomass_drive.py

from pathlib import Path
from datetime import timedelta
import shutil

from analytics_pipeline.google_drive.manager import DriveManager
from analytics_pipeline.processing.cache import has_valid_folder_cache
from analytics_pipeline.paths import biomass_protocol_subdir
from analytics_pipeline.config.logging_config import logger

CACHE_MAX_AGE = timedelta(days=1)


def get_biomass_folder(
    *,
    protocol: str,
    year: int,
    folder_id: str,
    refresh: bool = False,
    max_age: timedelta = CACHE_MAX_AGE,
) -> Path:
    """
    Return a local biomass folder, downloading from Drive if needed.

    Assumes DriveManager downloads into the biomass raw data directory.
    """
    output_folder = biomass_protocol_subdir(protocol, year)
    manager = DriveManager()

    logger.info(
        "Checking cache for %s (refresh=%s)",
        output_folder,
        refresh,
    )

    # --- Use cache if valid and not forcing refresh ---
    if not refresh and has_valid_folder_cache(output_folder, max_age=max_age):
        logger.info("Using cached folder: %s", output_folder)
        return output_folder

    # --- If refresh requested, remove existing folder ---
    if refresh and output_folder.exists():
        logger.info("♻️ Refreshing cache. Removing %s", output_folder)
        shutil.rmtree(output_folder)

    # --- Download from Google Drive ---
    if not output_folder.exists():
        logger.info("⬇️ Downloading biomass folder from Drive")

    # --- Download from Google Drive ---
    downloaded_folder = manager.download_folder(
        folder_id=folder_id,
        output_folder=output_folder,
    )

    logger.info("✅ Downloaded folder to %s", downloaded_folder)
    return downloaded_folder
