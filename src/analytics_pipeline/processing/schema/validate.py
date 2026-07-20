# src/analytics_pipeline/processing/schema/validate.py

import pandas as pd
from .biomass_schema import PAIRING_COLUMNS


def validate_biomass_schema(df: pd.DataFrame) -> None:
    """
    Ensure the biomass dataset contains all required pairing columns.
    """
    missing = sorted(col for col in PAIRING_COLUMNS if col not in df.columns)

    if missing:
        raise ValueError(f"Missing required biomass columns: {sorted(missing)}")
