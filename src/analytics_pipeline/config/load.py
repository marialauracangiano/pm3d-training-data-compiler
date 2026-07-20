# src/analytics_pipeline/config/load.py

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_yaml(relative_path: str) -> dict:
    """
    Load a YAML configuration file from the project's config directory.
    """
    path = PROJECT_ROOT / "config" / relative_path

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
