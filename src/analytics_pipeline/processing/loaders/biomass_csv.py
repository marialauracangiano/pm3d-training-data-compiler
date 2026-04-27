# src/analytics_pipeline/processing/loaders/biomass_csv.py

import pandas as pd
from typing import List
from pathlib import Path


def load_biomass_folder(folder_path: str, header_row_index: int = 3) -> pd.DataFrame:
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
        f for f in folder.iterdir()
        if f.suffix == ".csv" and not f.name.startswith(".")
    )

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in folder: {folder_path}")

    df_list: List[pd.DataFrame] = []

    # --- Load first file with header ---
    first = pd.read_csv(csv_files[0], header=header_row_index)
    expected_columns = list(first.columns)
    df_list.append(first)

    # --- Load others without header ---
    for file in csv_files[1:]:
        df = pd.read_csv(file, skiprows=header_row_index + 1, header=None)

        # Match column counts
        if df.shape[1] > len(expected_columns):
            df = df.iloc[:, :len(expected_columns)]
        elif df.shape[1] < len(expected_columns):
            raise ValueError(
                f"File {file} has fewer columns ({df.shape[1]}) than expected ({len(expected_columns)})"
            )

        df.columns = expected_columns
        df["source_file"] = file.name
        df_list.append(df)

    return pd.concat(df_list, ignore_index=True)
