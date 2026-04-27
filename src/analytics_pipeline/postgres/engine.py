# src/analytics_pipeline/postgres/engine.py

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from analytics_pipeline.config.config import get_db_config, ConfigError
from analytics_pipeline.config.logging_config import logger


def create_pg_engine() -> Engine:
    """
    Create and return a SQLAlchemy Postgres engine using project config.
    """
    try:
        config = get_db_config()

        engine = create_engine(
            f"postgresql+psycopg2://{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
            "?sslmode=require"
        )

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

        logger.info("✅ Postgres connection successful.")

    except Exception:
        logger.exception("❌ Postgres connection failed.")
        raise RuntimeError("Postgres connection failed")
