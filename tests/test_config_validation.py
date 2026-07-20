# tests/test_config_validation.py

import pytest

from analytics_pipeline.config.validate import (
    ConfigValidationError,
    require_keys,
    require_nested_keys,
    require_type,
)


def test_require_keys_passes_when_keys_exist():
    config = {
        "biomass": {},
        "image": {},
    }

    require_keys(
        config,
        ["biomass", "image"],
        "pipeline config",
    )


def test_require_keys_fails_when_key_missing():
    config = {
        "biomass": {},
    }

    with pytest.raises(ConfigValidationError):
        require_keys(
            config,
            ["biomass", "image"],
            "pipeline config",
        )


def test_require_nested_keys_passes():
    config = {
        "calibration": {
            "merge_keys": [],
            "output": {},
        }
    }

    require_nested_keys(
        config,
        {
            "calibration": [
                "merge_keys",
                "output",
            ],
        },
        "pipeline config",
    )


def test_require_nested_keys_fails():
    config = {
        "calibration": {
            "merge_keys": [],
        }
    }

    with pytest.raises(ConfigValidationError):
        require_nested_keys(
            config,
            {
                "calibration": [
                    "merge_keys",
                    "output",
                ],
            },
            "pipeline config",
        )


def test_require_type_passes():
    require_type(
        ["plot_id", "timing"],
        list,
        "merge_keys",
    )


def test_require_type_fails():
    with pytest.raises(ConfigValidationError):
        require_type(
            "plot_id",
            list,
            "merge_keys",
        )