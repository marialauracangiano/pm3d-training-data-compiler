# src/analytics_pipeline/processing/cache.py

from pathlib import Path
from datetime import datetime, timedelta
from analytics_pipeline.config.logging_config import logger


def has_valid_folder_cache(
    folder: Path,
    *,
    max_age: timedelta | None = None,
) -> bool:
    """
    A biomass cache is valid if:
    - Folder exists
    - Contains at least one CSV
    - Newest CSV is newer than max_age (if provided)
    Logs reasoning for debugging.
    """
    logger.info("Checking cache for folder: %s", folder)

    if not folder.exists():
        logger.info("❌ Folder does not exist.")
        return False

    csv_files = list(folder.glob("*.csv"))
    if not csv_files:
        logger.info("❌ No CSV files in folder.")
        return False

    newest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
    age = datetime.now() - datetime.fromtimestamp(newest_file.stat().st_mtime)

    if max_age is not None and age > max_age:
        logger.info(
            "❌ Cache stale: newest file %s is %s {age} old, (max allowed %s).",
            newest_file.name,
            age,
            max_age,
        )

        return False

    logger.info(
        "✅ Cache valid: newest file %s is %s old.",
        newest_file.name,
        age,
    )
    return True


def has_valid_file_cache(
    path: Path,
    *,
    max_age: timedelta | None = None,
) -> bool:
    logger.info("Checking cache for file: %s", path)

    if not path.exists():
        logger.info("❌ File does not exist.")
        return False

    if max_age is None:
        logger.info("✅ Cache valid: no maximum age specified.")
        return True

    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    age = datetime.now() - mtime

    if age > max_age:
        logger.info(
            "❌ Cache stale: file is %s old (max allowed %s).",
            age,
            max_age,
        )
        return False

    logger.info(
        "✅ Cache valid: file is %s old.",
        age,
    )
    return True
