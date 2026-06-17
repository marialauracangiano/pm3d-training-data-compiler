# src/analytics_pipeline/processing/transforms/biomass.py

import pandas as pd
from analytics_pipeline.config.logging_config import logger


def clean_biomass_data(
    df: pd.DataFrame,
    *,
    affiliation_source_column: str,
    affiliation_map: dict[str, str],
    rename_map: dict[str, str],
    columns_to_keep: list[str],
    drop_zero_weight: bool = True,
) -> pd.DataFrame:
    """
    Clean and normalize biomass data in preparation for merging.

    This function performs mechanical, reusable transformations only.
    Project-specific meaning (mappings, column choices) must be provided
    by the caller.

    Steps:
    - Extract affiliation from a source column
    - Map affiliation values using provided mapping
    - Rename columns
    - Drop invalid biomass rows
    """

    logger.info("Starting biomass data cleaning")
    df = df.copy()
    
    if "wide_format" in locals():
        raise ValueError(
        "Wide format handling has been moved out of clean_biomass_data(). "
        "Please convert data BEFORE calling this function."
    )
    
    initial_rows = len(df)

    # ------------------------------------------------------------------
    # 1. Extract affiliation from source column
    # ------------------------------------------------------------------
    if affiliation_source_column not in df.columns:
        raise KeyError(
            f"Affiliation source column '{affiliation_source_column}' not found"
        )

    df["affiliation"] = (
        df[affiliation_source_column]
        .astype(str)
        .str.split("_", n=1)
        .str[0]
        .where(df[affiliation_source_column].notna())
    )

    # ------------------------------------------------------------------
    # 2. Map frontend affiliation → backend affiliation
    # ------------------------------------------------------------------
    df["affiliation"] = df["affiliation"].map(
        affiliation_map
    ).fillna(df["affiliation"])

    # ------------------------------------------------------------------
    # 3. Rename columns
    # ------------------------------------------------------------------
    df = df.rename(columns=rename_map)
    df = df[columns_to_keep]

    # ------------------------------------------------------------------
    # 4. Drop invalid biomass rows
    # ------------------------------------------------------------------
    if drop_zero_weight:
        if "dry_weight_g" not in df.columns:
            raise KeyError(
                "Column 'dry_weight_g' required when drop_zero_weight=True"
            )

        before = len(df)
        df = df[df["dry_weight_g"].notna() & (df["dry_weight_g"] != 0)]
        logger.info(f"Dropped {before - len(df)} rows with zero/null dry weight")

    logger.info(
        f"Biomass cleaning complete: {initial_rows} → {len(df)} rows"
    )

    return df
