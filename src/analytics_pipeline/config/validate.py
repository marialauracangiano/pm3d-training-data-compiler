# src/analytics_pipeline/config/validate.py

class ConfigValidationError(Exception):
    """Raised when configuration is invalid."""
    pass


def require_keys(config: dict, required_keys: list, context: str):
    """Ensure required keys exist in config."""
    missing = [key for key in required_keys if key not in config]

    if missing:
        raise ConfigValidationError(
            f"Missing required keys in {context}: {missing}"
        )


def require_nested_keys(config: dict, nested_keys: dict, context: str):
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
            raise ConfigValidationError(
                f"Missing section '{parent}' in {context}"
            )

        missing = [k for k in keys if k not in config[parent]]

        if missing:
            raise ConfigValidationError(
                f"Missing keys in {context}.{parent}: {missing}"
            )


def require_type(value, expected_type, name: str):
    if not isinstance(value, expected_type):
        raise ConfigValidationError(
            f"Invalid type for '{name}': expected {expected_type}, got {type(value)}"
        )