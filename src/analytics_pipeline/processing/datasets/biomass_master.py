# src/analytics_pipeline/processing/datasets/biomass_master.py

from pathlib import Path

import pandas as pd

from analytics_pipeline.processing.adapters.biomass_adapter import (
    to_standard_biomass_format,
)
from analytics_pipeline.processing.transforms.biomass import clean_biomass_data

from ..loaders.biomass_csv import load_biomass_folder


def build_biomass_master(
    folder_map: dict[int, Path],
    *,
    biomass_config: dict,
    cleaning_config: dict,
) -> pd.DataFrame:
    """
    Build standardized biomass master dataset.

    Parameters
    ----------
    folder_map : dict[int, Path]
        Mapping of year to downloaded biomass folder.

    biomass_config : dict
        Protocol-specific biomass configuration.

    cleaning_config : dict
        Standard biomass cleaning parameters.

    Returns
    -------
    pd.DataFrame
        Combined standardized biomass dataset.
    """
    if not folder_map:
        raise ValueError("folder_map is empty")

    frames = []

    for year in sorted(folder_map):
        folder = folder_map[year]

        # Load raw biomass files
        df = load_biomass_folder(folder)

        # Convert protocol-specific formats to standard biomass format
        df = to_standard_biomass_format(
            df,
            biomass_config,
        )

        # Apply common cleaning rules
        df = clean_biomass_data(
            df,
            **cleaning_config,
        )

        df = df.loc[:, ~df.columns.duplicated()]

        df["current_year"] = int(year)
        frames.append(df)

    return pd.concat(frames, ignore_index=True)
