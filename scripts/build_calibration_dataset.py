# scripts/build_calibration_dataset.py

import argparse
import pandas as pd

from analytics_pipeline.processing.datasets.calibration import build_calibration_dataset
from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.config.load import load_yaml
from analytics_pipeline.config.validate import (
    require_keys,
    # require_nested_keys,
    require_type,
)
from analytics_pipeline.paths import protocol_processed_dir


def run(protocol: str, diagnostics: bool = False):
    logger.info("Loading calibration configuration from YAML")
    config = load_yaml("pipeline.yaml")

    require_keys(
        config,
        ["calibration"],
        "pipeline config",
    )

    calibration_config = config["calibration"]
    protocol = protocol.upper()
    processed_dir = protocol_processed_dir(protocol)

    require_keys(
        calibration_config,
        [
            "merge_keys",
            "output",
            "diagnostics",
        ],
        "calibration config",
    )

    require_keys(
        calibration_config["output"],
        ["filename"],
        "calibration output config",
    )

    require_keys(
        calibration_config["diagnostics"],
        [
            "default_enabled",
            "folder",
        ],
        "calibration diagnostics config",
    )

    require_type(
        calibration_config["merge_keys"],
        list,
        "calibration.merge_keys",
    )

    merge_keys = calibration_config["merge_keys"]

    biomass_path = processed_dir / "biomass_master.csv"
    image_path = processed_dir / "image_master.csv"

    output_filename = calibration_config["output"]["filename"]

    diagnostics_enabled = (
        diagnostics or calibration_config["diagnostics"]["default_enabled"]
    )

    # --- Ensure output dir exists ---
    processed_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading biomass master CSV from '%s'", biomass_path)
    biomass_df = pd.read_csv(biomass_path)
    logger.info(
        "Loaded biomass master with %d rows and %d columns",
        len(biomass_df),
        len(biomass_df.columns),
    )

    logger.info("Loading image master CSV from '%s'", image_path)
    image_df = pd.read_csv(image_path)
    logger.info(
        "Loaded image master with %d rows and %d columns",
        len(image_df),
        len(image_df.columns),
    )

    logger.info("Output directory set to '%s'", processed_dir)
    logger.info("Building calibration dataset using merge keys: %s", merge_keys)

    calibration_df = build_calibration_dataset(
        biomass_df,
        image_df,
        merge_keys=merge_keys,
        diagnostics=diagnostics_enabled,
        output_dir=processed_dir,
    )

    calibration_csv = processed_dir / output_filename

    calibration_df.to_csv(calibration_csv, index=False)

    logger.info(
        "✅ Saved calibration dataset with %d rows to '%s'",
        len(calibration_df),
        calibration_csv,
    )

    if diagnostics_enabled:
        diagnostics_path = processed_dir / calibration_config["diagnostics"]["folder"]
        logger.info("✅ Diagnostic CSVs have been saved to '%s'", diagnostics_path)


# --- CLI wrapper ---


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build calibration dataset from biomass and image masters"
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Generate diagnostic CSVs",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run(diagnostics=args.diagnostics)


if __name__ == "__main__":
    main()
