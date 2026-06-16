# src/analytics_pipeline/processing/transforms/biomass_format.py

import pandas as pd

def transform_biomass_wide_to_long(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Converts wide-format biomass cover crop data into long format.
    Each species group becomes a row.
    """
    groups = config["wide_format"]["groups"]
    base_cols = config["wide_format"]["base_columns"]

    rows = []

    for _, row in df.iterrows():

        base_data = {col: row[col] for col in base_cols}

        for g in groups:

            weight = row.get(g["weight_column"])

            if pd.isna(weight) or weight == 0:
                continue

            if g["name"] == "other":
                species = "other"
            else:
                species = row.get(g["species_column"])

            if pd.isna(species):
                continue

            rows.append({
                **base_data,
                "species": species,
                "dry_weight_g": weight,
            })

    return pd.DataFrame(rows)