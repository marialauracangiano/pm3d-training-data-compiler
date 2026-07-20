# src/analytics_pipeline/processing/transforms/biomass_format.py

import pandas as pd


def transform_biomass_wide_to_long(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Converts wide-format biomass cover crop data into long format.
    Each species group becomes a row.
    """
    wide_config = config["wide_format"]
    groups = wide_config["groups"]
    base_cols = wide_config["base_columns"]

    rows = []
    for _, row in df.iterrows():

        base_data = {col: row[col] for col in base_cols}

        for group in groups:

            weight = row.get(group["weight_column"])

            if pd.isna(weight) or weight == 0:
                continue

            if group["name"] == "other":
                species = "Other"
            else:
                species = row.get(group["species_column"])

            if pd.isna(species):
                continue

            output_row = {
                **base_data,
                "species": species,
                "dry_weight_g": weight,
            }

            rows.append(output_row)

    return pd.DataFrame(rows)
