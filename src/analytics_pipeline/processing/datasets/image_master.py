# src/analytics_pipeline/processing/datasets/image_master.py

import pandas as pd

from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.processing.acquisition.postgres import get_image_data
from analytics_pipeline.processing.transforms.image import clean_image_data


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
    - Applies image cleaning rules
    - Returns the standardized image dataset

    Parameters
    ----------
    refresh : bool, default False
        If True, forces re-querying Postgres and rebuilding the CSV cache.

    cleaning_config : dict
        Image cleaning configuration.

    Returns
    -------
    pd.DataFrame
        Standardized image master dataframe.
    """
    logger.info("Building image master dataset...")

    csv_path = get_image_data(refresh=refresh)
    logger.info("Loading image data from %s", csv_path)

    # Load cached Postgres export
    df = pd.read_csv(csv_path, low_memory=False)

    # Apply protocol-independent cleaning rules
    df = clean_image_data(
        df,
        **cleaning_config,
    )

    logger.info(
        "Image master loaded with %d rows and %d columns",
        len(df),
        len(df.columns),
    )

    return df
