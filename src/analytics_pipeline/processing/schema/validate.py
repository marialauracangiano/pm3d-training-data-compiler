# src/analytics_pipeline/processing/schema/validate.py

import pandas as pd
from .biomass_schema import PAIRING_COLUMNS


def validate_biomass_schema(df: pd.DataFrame) -> None:
    missing = [col for col in PAIRING_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(
            f"Biomass schema validation failed. Missing pairing columns: {missing}"
        )