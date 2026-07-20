# tests/test_load.py

import pytest
import yaml

import analytics_pipeline.config.load as config_load


def test_load_yaml(tmp_path, monkeypatch):
    # Create temporary config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    test_config = {
        "protocol": "test_protocol",
        "years": [2025, 2026],
    }

    yaml_file = config_dir / "test.yaml"

    with open(yaml_file, "w") as f:
        yaml.safe_dump(test_config, f)

    # Redirect PROJECT_ROOT to temporary directory
    monkeypatch.setattr(
        config_load,
        "PROJECT_ROOT",
        tmp_path,
    )

    result = config_load.load_yaml("test.yaml")

    assert isinstance(result, dict)
    assert result["protocol"] == "test_protocol"
    assert result["years"] == [2025, 2026]


def test_load_yaml_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        config_load,
        "PROJECT_ROOT",
        tmp_path,
    )

    with pytest.raises(FileNotFoundError):
        config_load.load_yaml("missing.yaml")