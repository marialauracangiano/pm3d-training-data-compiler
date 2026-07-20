# src/analytics_pipeline/processing/adapters/biomass_adapter.py

import pandas as pd

from analytics_pipeline.processing.transforms.biomass_format import (
    transform_biomass_wide_to_long,
)


def to_standard_biomass_format(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    format_type = config.get("format")

    if format_type == "wide":
        wide_cfg = config.get("wide_format")

        if wide_cfg is None:
            raise ValueError("Missing wide_format config for wide dataset")

        return transform_biomass_wide_to_long(
            df,
            {"wide_format": wide_cfg},
        )

    return df
