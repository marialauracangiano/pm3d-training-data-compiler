# src/analytics_pipeline/postgres/datasets.py

import pandas as pd
from sqlalchemy.engine import Engine

from analytics_pipeline.postgres.client import run_query
from analytics_pipeline.config.logging_config import logger


def load_image_data(
    *,
    engine: Engine | None = None,
) -> pd.DataFrame:
    """
    Load image data and associated metadata from Postgres.

    Returns
    -------
    pd.DataFrame
        Image-level dataset used across the analytics pipeline.
    """
    sql = """
        SELECT *
        FROM all_package_data_latest;
    """

    logger.info("Loading dataset: image_data")

    df = run_query(sql, engine=engine)

    logger.info(
        "Loaded %d rows and %d columns from image_data",
        len(df),
        len(df.columns),
    )

    return df
