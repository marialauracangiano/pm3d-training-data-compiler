# src/analytics_pipeline/postgres/engine.py

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from analytics_pipeline.config.config import ConfigError, get_db_config
from analytics_pipeline.config.logging_config import logger


def create_pg_engine() -> Engine:
    """
    Create and return a SQLAlchemy Postgres engine using project config.
    """
    try:
        config = get_db_config()

        connection_url = (
            f"postgresql+psycopg2://"
            f"{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}"
            f"/{config['database']}"
            "?sslmode=require"
        )

        engine = create_engine(connection_url)

        logger.debug("Postgres engine created.")
        return engine

    except ConfigError:
        logger.exception("Database configuration is invalid.")
        raise

    except Exception:
        logger.exception("Unexpected error while creating Postgres engine.")
        raise


def test_connection(engine: Engine) -> None:
    """
    Test the Postgres connection by executing a trivial query.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("Postgres connection successful.")

    except Exception:
        logger.exception("Postgres connection failed.")
        raise RuntimeError("Postgres connection failed")
