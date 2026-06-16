# src/analytics_pipeline/processing/transforms/plot_id.py

import pandas as pd


def build_plot_id(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Build standardized plot_id column from config.
    """

    plot_config = config["plot_id"]

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

            part = prefix + df[column].astype(str)

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