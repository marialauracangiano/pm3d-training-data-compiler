# src/analytics_pipeline/processing/cache.py

from pathlib import Path
from datetime import datetime, timedelta


def has_valid_cache(
    folder: Path,
    *,
    max_age: timedelta | None = timedelta(days=1),
) -> bool:
    """
    A biomass cache is valid if:
    - Folder exists
    - Contains at least one CSV
    - Newest CSV is newer than max_age (if provided)
    Logs reasoning for debugging.
    """
    print(f"Checking cache for folder: {folder}")

    if not folder.exists():
        print("❌ Folder does not exist.")
        return False

    csv_files = list(folder.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files in folder.")
        return False

    newest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
    age = datetime.now() - datetime.fromtimestamp(newest_file.stat().st_mtime)

    if max_age is not None and age > max_age:
        print(f"❌ Cache stale: newest file {newest_file.name} is {age} old, max allowed {max_age}.")
        return False

    print(f"✅ Cache valid: newest file {newest_file.name} is {age} old.")
    return True


def has_valid_file_cache(
    path: Path,
    max_age: timedelta | None = None,
) -> bool:
    if not path.exists():
        return False

    if max_age is None:
        return True

    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    age = datetime.now() - mtime
    return age <= max_age