# src/analytics_pipeline/processing/transforms/image.py

import pandas as pd
from analytics_pipeline.config.logging_config import logger


def clean_image_data(
    df: pd.DataFrame,
    *,
    user_type_value: str,
    columns_to_keep: list[str],
    drop_zero_distance: bool = True,
) -> pd.DataFrame:
    """
    Clean and normalize image data in preparation for merging.

    This function performs reusable, mechanical transformations only.
    Project-specific meaning (user types, column lists) must be supplied
    by the caller.

    Steps:
    - Filter by user type
    - Select a subset of columns
    - Drop rows with invalid set distance
    - Normalize merge-critical dtypes
    """

    logger.info("Starting image data cleaning")
    df = df.copy()

    initial_rows = len(df)

    # ------------------------------------------------------------------
    # 1. Filter by user type
    # ------------------------------------------------------------------
    if "user_type" not in df.columns:
        raise KeyError("Column 'user_type' not found in image data")

    df = df[df["user_type"] == user_type_value]
    logger.info(
        f"Filtered user_type='{user_type_value}': "
        f"{initial_rows} → {len(df)} rows"
    )

    # ------------------------------------------------------------------
    # 2. Select required columns
    # ------------------------------------------------------------------
    missing_cols = set(columns_to_keep) - set(df.columns)
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    df = df[columns_to_keep].copy()

    # ------------------------------------------------------------------
    # 3. Drop invalid set_distance rows
    # ------------------------------------------------------------------
    if drop_zero_distance:
        if "set_distance" not in df.columns:
            raise KeyError(
                "Column 'set_distance' required when drop_zero_distance=True"
            )

        before = len(df)
        df = df[
            df["set_distance"].notna() &
            (df["set_distance"] != 0)
        ]
        logger.info(
            f"Dropped {before - len(df)} rows with zero/null set_distance"
        )

    # ------------------------------------------------------------------
    # 4. Normalize merge-critical dtypes
    # ------------------------------------------------------------------
    if "timing" in df.columns:
        df["timing"] = df["timing"].astype("Int64")

    logger.info(
        f"Image cleaning complete: {initial_rows} → {len(df)} rows"
    )

    return df
