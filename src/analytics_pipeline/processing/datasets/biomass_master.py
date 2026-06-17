# src/analytics_pipeline/processing/datasets/biomass_master.py

import numpy as np
import pandas as pd
from pathlib import Path
from ..loaders.biomass_csv import load_biomass_folder
from analytics_pipeline.processing.transforms.biomass import clean_biomass_data
from analytics_pipeline.processing.adapters.biomass_adapter import (
    to_standard_biomass_format,
)


def build_biomass_master(folder_map: dict[int, Path], *, config: dict, cleaning_config: dict) -> pd.DataFrame:
    """
    Given a dict mapping {year: folder_path}, load all biomass CSVs
    and produce a combined dataset.

    Parameters
    ----------
    folder_map : dict[int, str]
        Example: {2024: "data/biomass_b4i_2024", 2025: "data/biomass_b4i_2025"}

    Returns
    -------
    pd.DataFrame
    """
    if not folder_map:
        raise ValueError("folder_map is empty") 

    frames = []

    for year in sorted(folder_map):
        folder = folder_map[year]
        df = load_biomass_folder(folder)
        df = to_standard_biomass_format(df, config)
        df = clean_biomass_data(
            df,
            **cleaning_config,
        )
        
        df = df.loc[:, ~df.columns.duplicated()]

        df["current_year"] = np.int64(year)
        frames.append(df)

    return pd.concat(frames, ignore_index=True)
