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
    Clean and normalize biomass data into the standard biomass schema.

    All protocol-specific behavior (column names, mappings, retained columns)
    is supplied through the protocol configuration.

    Steps
    -----
    1. Extract affiliation
    2. Map affiliation values
    3. Rename columns
    4. Keep required columns
    5. Optionally remove zero-weight samples
    """

    logger.info("Starting biomass data cleaning")

    df = df.copy()
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
    df["affiliation"] = df["affiliation"].map(affiliation_map).fillna(df["affiliation"])

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
            raise KeyError("Column 'dry_weight_g' required when drop_zero_weight=True")

        before = len(df)
        df = df[df["dry_weight_g"].notna() & (df["dry_weight_g"] != 0)]
        logger.info(
            "Dropped %d rows with zero/null dry weight",
            before - len(df),
        )

    logger.info(
        "Biomass cleaning complete: %d → %d rows",
        initial_rows,
        len(df),
    )

    return df
