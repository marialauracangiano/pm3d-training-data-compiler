# src/analytics_pipeline/processing/datasets/image_master.py

import pandas as pd
from analytics_pipeline.processing.acquisition.postgres import get_image_data
from analytics_pipeline.processing.transforms.image import clean_image_data
from analytics_pipeline.config.logging_config import logger


def build_image_master(
    *,
    refresh: bool = False, 
    cleaning_config: dict,
) -> pd.DataFrame:
    """
    Build the image master dataset.

    This function:
    - Retrieves image data from Postgres (with caching)
    - Loads it into a pandas DataFrame
    - Acts as the public API for image-based datasets

    Parameters
    ----------
    refresh : bool, default False
        If True, forces re-querying Postgres and rebuilding the CSV cache.

    Returns
    -------
    pd.DataFrame
        Image master dataframe
    """
    logger.info("Building image master dataset...")

    csv_path = get_image_data(refresh=refresh)
    logger.info(f"Loading image data from {csv_path}")

    df = pd.read_csv(csv_path)
    df = clean_image_data(
        df,
        **cleaning_config,
    )

    logger.info(
        f"Image master loaded with {len(df)} rows and {len(df.columns)} columns"
    )

    return df
