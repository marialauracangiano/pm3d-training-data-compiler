# src/analytics_pipeline/processing/transforms/plot_id.py

import pandas as pd


def build_plot_id(df: pd.DataFrame, protocol_config: dict, source: str) -> pd.DataFrame:
    """
    Build a standardized plot_id column from the protocol configuration.

    Supports either:
    - an existing column
    - a composite identifier built from multiple columns
    """
    if source not in protocol_config["plot_id"]:
        raise ValueError(f"No plot_id configuration defined for source '{source}'.")

    plot_config = protocol_config["plot_id"][source]

    # -----------------------------------
    # Existing plot_id column
    # -----------------------------------

    if plot_config["type"] == "existing":
        source_column = plot_config["column"]
        df["plot_id"] = df[source_column].astype(str)
        return df

    # -----------------------------------
    # Unsupported plot_id type
    # -----------------------------------

    if plot_config["type"] != "composite":
        raise ValueError(f"Unsupported plot_id type: {plot_config['type']}")

    # -----------------------------------
    # Composite plot_id
    # -----------------------------------

    separator = plot_config.get("separator", "_")

    parts = []

    for component in plot_config["components"]:

        column = component["column"]
        prefix = component.get("prefix", "")

        part = df[column].astype(str)

        if "strip_prefix" in component:
            part = part.str.removeprefix(component["strip_prefix"])

        if component.get("strip_leading_zeros", False):
            part = part.str.lstrip("0").replace("", "0")

        part = prefix + part

        parts.append(part)

    df["plot_id"] = pd.concat(parts, axis=1).agg(separator.join, axis=1)

    return df
