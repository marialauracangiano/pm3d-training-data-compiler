# src/analytics_pipeline/postgres/client.py

from sqlalchemy.engine import Engine
import pandas as pd

from analytics_pipeline.postgres.engine import create_pg_engine
from analytics_pipeline.config.logging_config import logger


def run_query(
    sql: str,
    *,
    engine: Engine | None = None,
) -> pd.DataFrame:
    """
    Execute a SQL query against Postgres and return the result as a DataFrame.

    Parameters
    ----------
    sql : str
        SQL query to execute.
    engine : sqlalchemy.Engine | None
        Optional engine to reuse. If None, a new engine is created.

    Returns
    -------
    pd.DataFrame
    """
    try:
        if engine is None:
            engine = create_pg_engine()
            logger.debug("Created new Postgres engine for query execution.")

        df = pd.read_sql_query(sql, engine)
        logger.info("Postgres query executed successfully.")

        return df

    except Exception:
        logger.exception("Postgres query execution failed.")
        raise
