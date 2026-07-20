# src/analytics_pipeline/processing/loaders/biomass_csv.py

from pathlib import Path
from typing import List

import pandas as pd

from analytics_pipeline.config.logging_config import logger


def load_biomass_folder(
    folder_path: Path | str, header_row_index: int = 3
) -> pd.DataFrame:
    """
    Load and vertically concatenate all biomass CSVs inside a folder.

    Parameters
    ----------
    folder_path : str
        Absolute or relative path to folder containing CSV files.
    header_row_index : int
        Row index (0-based) to use as the header in the FIRST file.

    Returns
    -------
    pd.DataFrame
    """

    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    csv_files = sorted(
        f for f in folder.iterdir() if f.suffix == ".csv" and not f.name.startswith(".")
    )

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in folder: {folder_path}")

    df_list: List[pd.DataFrame] = []

    # --- Load first file with header ---
    logger.info("Loading %d biomass CSV files from %s", len(csv_files), folder)

    first_file = csv_files[0]

    first_df = pd.read_csv(first_file, header=header_row_index)

    expected_columns = first_df.columns.tolist()

    first_df["source_file"] = first_file.name

    df_list.append(first_df)

    # --- Load others without header ---
    for file in csv_files[1:]:
        df = pd.read_csv(file, skiprows=header_row_index + 1, header=None)

        # Match column counts
        if df.shape[1] > len(expected_columns):
            df = df.iloc[:, : len(expected_columns)]
        elif df.shape[1] < len(expected_columns):
            raise ValueError(
                f"File {file} has fewer columns ({df.shape[1]}) than expected ({len(expected_columns)})"
            )

        df.columns = expected_columns
        df["source_file"] = file.name
        df_list.append(df)

    master_df = pd.concat(df_list, ignore_index=True)

    logger.info(
        "Loaded %d rows from %d biomass files",
        len(master_df),
        len(csv_files),
    )

    return master_df


def load_biomass_file(file_path: Path | str, header_row_index: int = 3) -> pd.DataFrame:
    """
    Load a single biomass CSV file (useful for testing or debugging).
    """
    return pd.read_csv(file_path, header=header_row_index)
