# src/analytics_pipeline/processing/acquisition/postgres.py

from pathlib import Path
from datetime import timedelta
import pandas as pd

from analytics_pipeline.processing.cache import has_valid_file_cache
from analytics_pipeline.paths import raw_image_file
from analytics_pipeline.postgres.client import create_pg_engine
from analytics_pipeline.config.logging_config import logger

CACHE_MAX_AGE = timedelta(days=1)


def get_image_data(
    *,
    refresh: bool = False,
    max_age: timedelta = CACHE_MAX_AGE,
) -> Path:
    """
    Returns a local CSV file containing image/package data from Postgres.
    Downloads fresh data if cache is invalid or --refresh is requested.
    """
    output_file = raw_image_file()

    logger.debug("Checking cache for %s (refresh=%s)", output_file, refresh)

    # Use cached file if valid and not forcing refresh
    if not refresh and has_valid_file_cache(output_file, max_age=max_age):
        logger.info("✅ Using cached file: %s", output_file)
        return output_file

    # If refresh requested or cache stale, remove existing file
    if output_file.exists():
        logger.info("♻️ Refresh requested or cache stale: removing %s", output_file)
        output_file.unlink()

    # Fetch data from Postgres
    logger.info("🕒 Fetching fresh data from Postgres...")

    engine = create_pg_engine()

    query = "SELECT * FROM all_package_data_latest;"  # can be customized if needed
    df = pd.read_sql_query(query, engine)

    # Ensure output folder exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save CSV
    df.to_csv(output_file, index=False)
    logger.info("✅ Saved %d rows to %s", len(df), output_file)

    return output_file
