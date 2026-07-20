#tests/test_cache.py

from pathlib import Path
from datetime import timedelta

from analytics_pipeline.processing.cache import (
    has_valid_folder_cache,
    has_valid_file_cache,
)


def test_valid_folder_cache(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text("a,b\n1,2")

    assert has_valid_folder_cache(
        tmp_path,
        max_age=timedelta(days=1),
    )


def test_invalid_folder_cache(tmp_path):
    assert not has_valid_folder_cache(
        tmp_path,
        max_age=timedelta(days=1),
    )


def test_valid_file_cache(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text("a,b\n1,2")

    assert has_valid_file_cache(
        file,
        max_age=timedelta(days=1),
    )