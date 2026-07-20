# src/analytics_pipeline/processing/transforms/image.py

import pandas as pd

from analytics_pipeline.config.logging_config import logger


def clean_image_data(
    df: pd.DataFrame,
    *,
    filters: dict[str, str],
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
    # 1. Apply protocol filters
    # ------------------------------------------------------------------
    if not filters:
        logger.info("No image filters specified. Keeping all image records.")
    else:

        for column, value in filters.items():

            if column not in df.columns:
                raise KeyError(f"Column '{column}' not found in image data")

            before = len(df)

            df = df[df[column] == value]

            logger.info(
                "Filtered %s='%s': %d → %d rows",
                column,
                value,
                before,
                len(df),
            )
    # ------------------------------------------------------------------
    # 2. Select required columns
    # ------------------------------------------------------------------
    missing_cols = set(columns_to_keep) - set(df.columns)
    if missing_cols:
        raise KeyError(f"Missing required columns: {sorted(missing_cols)}")

    df = df.loc[:, columns_to_keep].copy()

    # ------------------------------------------------------------------
    # 3. Drop invalid set_distance rows
    # ------------------------------------------------------------------
    if drop_zero_distance:
        if "set_distance" not in df.columns:
            raise KeyError(
                "Column 'set_distance' required when drop_zero_distance=True"
            )

        before = len(df)

        valid_distance = df["set_distance"].notna() & (df["set_distance"] != 0)

        df = df.loc[valid_distance]

        logger.info(
            "Dropped %d rows with zero/null set_distance",
            before - len(df),
        )

    # ------------------------------------------------------------------
    # 4. Normalize merge-critical dtypes
    # ------------------------------------------------------------------
    if "timing" in df.columns:
        df["timing"] = df["timing"].astype("Int64")

    logger.info(
        "Image cleaning complete: %d → %d rows",
        initial_rows,
        len(df),
    )

    return df
