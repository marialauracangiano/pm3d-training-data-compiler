# src/analytics_pipeline/config/validate.py

from typing import Any


class ConfigValidationError(Exception):
    """Raised when  a configuration file is invalid."""

    pass


def require_keys(config: dict, required_keys: list[str], context: str) -> None:
    """Ensure required keys exist in config."""
    missing = sorted(key for key in required_keys if key not in config)

    if missing:
        raise ConfigValidationError(f"Missing required keys in {context}: {missing}")


def require_nested_keys(
    config: dict,
    nested_keys: dict[str, list[str]],
    context: str,
) -> None:
    """
    Validate nested structure.

    Example:
    nested_keys = {
        "inputs": ["biomass", "image"],
        "output": ["default_dir", "filename"]
    }
    """
    for parent, keys in nested_keys.items():
        if parent not in config:
            raise ConfigValidationError(f"Missing section '{parent}' in {context}")

        missing = sorted(k for k in keys if k not in config[parent])

        if missing:
            raise ConfigValidationError(
                f"Missing keys in {context}.{parent}: {missing}"
            )


def require_type(
    value: Any,
    expected_type: type,
    name: str,
) -> None:
    if not isinstance(value, expected_type):
        raise ConfigValidationError(
            f"Invalid type for '{name}': "
            f"expected {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )
