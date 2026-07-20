import os
from pathlib import Path

from dotenv import load_dotenv

from analytics_pipeline.paths import PROJECT_ROOT

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")


class ConfigError(Exception):
    """Custom error for missing configuration values."""

    pass


def require_env_var(var_name: str) -> str:
    value = os.getenv(var_name)

    if value is None:
        raise ConfigError(f"Missing required environment variable: {var_name}")
    return value


def get_google_auth_paths() -> dict[str, Path]:
    return {
        "credentials_path": PROJECT_ROOT / require_env_var("GOOGLE_CREDENTIALS_PATH"),
        "token_path": PROJECT_ROOT / require_env_var("GOOGLE_TOKEN_PATH"),
    }


def get_db_config() -> dict[str, str | int]:
    return {
        "user": require_env_var("DB_USER"),
        "password": require_env_var("DB_PASS"),
        "host": require_env_var("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "database": require_env_var("DB_NAME"),
    }


def get_env() -> str:
    return os.getenv("ENV", "development")
