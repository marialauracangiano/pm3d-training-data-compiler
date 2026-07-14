# src/analytics_pipeline/processing/acquisition/biomass_drive.py

from pathlib import Path
from datetime import timedelta
import shutil

from analytics_pipeline.google_drive.manager import DriveManager
from analytics_pipeline.processing.cache import has_valid_cache
#from analytics_pipeline.paths import biomass_subdir
from analytics_pipeline.paths import biomass_protocol_subdir

CACHE_MAX_AGE = timedelta(days=1)

def get_biomass_folder(
    *,
    protocol: str,
    year: int,
    folder_id: str,
    refresh: bool = False,
    max_age: timedelta | None = timedelta(days=1),
) -> Path:
    """
    Return a local biomass folder, downloading from Drive if needed.
    
    Assumes DriveManager downloads into the biomass raw data directory.
    """
    #output_folder = biomass_subdir(str(year))
    output_folder = biomass_protocol_subdir(protocol, year)
    manager = DriveManager()
    
    print(f"Checking cache for {output_folder}, refresh={refresh}")

    # --- Use cache if valid and not forcing refresh ---
    if not refresh and has_valid_cache(output_folder, max_age=CACHE_MAX_AGE):
        print(f"✅ Using cached folder: {output_folder}")
        return output_folder

    # --- If refresh requested, remove existing folder ---
    if refresh and output_folder.exists():
        print(f"♻️ Refresh requested: removing existing folder {output_folder}")
        shutil.rmtree(output_folder)

    # --- Otherwise folder is missing or cache stale ---
    if not output_folder.exists():
        print(f"🕒 Cache missing or stale: downloading folder from Drive")

    # --- Download from Google Drive ---
    downloaded_folder = manager.download_folder(
        folder_id=folder_id,
        output_folder=output_folder,
    )

    print(f"✅ Downloaded folder to {downloaded_folder}")
    return downloaded_folder