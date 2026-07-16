# src/analytics_pipeline/processing/transforms/plot_id.py

import pandas as pd


def build_plot_id(df: pd.DataFrame, config: dict, source: str) -> pd.DataFrame:
    """
    Build standardized plot_id column from config.
    """
    if source not in config["plot_id"]:
        raise ValueError(
            f"No plot_id configuration defined for source '{source}'."
        )

    plot_config = config["plot_id"][source]

    # -----------------------------------
    # Existing plot_id column
    # -----------------------------------

    if plot_config["type"] == "existing":

        source_column = plot_config["column"]

        df["plot_id"] = df[source_column].astype(str)

    # -----------------------------------
    # Composite plot_id
    # -----------------------------------

    elif plot_config["type"] == "composite":

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

        df["plot_id"] = (
            pd.concat(parts, axis=1)
            .agg(separator.join, axis=1)
        )

    else:
        raise ValueError(
            f"Unsupported plot_id type: {plot_config['type']}"
        )
    

    return df