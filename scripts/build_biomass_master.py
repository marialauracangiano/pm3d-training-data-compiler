# scripts/build_biomass_master.py

import argparse
from pathlib import Path

from analytics_pipeline.processing.datasets import build_biomass_master
from analytics_pipeline.processing.acquisition.biomass_drive import get_biomass_folder
from analytics_pipeline.config.config import require_env_var
from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.processing.transforms.plot_id import build_plot_id
from analytics_pipeline.config.load import load_yaml
from analytics_pipeline.config.validate import require_keys, require_type
from analytics_pipeline.processing.schema.validate import validate_biomass_schema


def run(refresh: bool = False):
    logger.info("Loading biomass configuration from YAML")
    config = load_yaml("biomass_b4i.yaml")

    # --- Validation ---
    require_keys(
        config,
        [
            "years",
            "affiliation_source_column",
            "affiliation_map",
            "rename_map",
            "columns_to_keep",
        ],
        "biomass config",
    )

    require_type(config["years"], list, "years")
    require_type(config["affiliation_map"], dict, "affiliation_map")
    require_type(config["rename_map"], dict, "rename_map")

    # --- Extract config AFTER validation ---
    years = config["years"]

    cleaning_config = {
        "affiliation_source_column": config["affiliation_source_column"],
        "affiliation_map": config["affiliation_map"],
        "rename_map": config["rename_map"],
        "columns_to_keep": config["columns_to_keep"],
        "drop_zero_weight": config.get("drop_zero_weight", True),
    }   

    # --- Build year → folder_id map from env ---
    year_drive_map = {
        year: require_env_var(f"GOOGLE_DRIVE_BIOMASS_{year}_FOLDER_ID")
        for year in years
    }

    folder_map = {}

    for year, folder_id in year_drive_map.items():
        logger.info("Fetching biomass folder for year %s", year)

        local_path = get_biomass_folder(
            year=year,
            folder_id=folder_id,
            refresh=refresh,
        )

        folder_map[year] = local_path
        logger.info("Folder for %s: %s", year, local_path)

    logger.info("Building biomass master dataset")

    master_df = build_biomass_master(
        folder_map,
        cleaning_config=cleaning_config,
        config=config,
    )

    # Build standardized plot_id
    master_df = build_plot_id(
        master_df,
        config,
    )

    validate_biomass_schema(master_df)

    logger.info(
        "Master dataframe has %d rows and %d columns",
        len(master_df),
        len(master_df.columns),
    )

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = output_dir / "biomass_master.csv"

    logger.info("Saving master CSV to %s", output_csv)

    master_df.to_csv(output_csv, index=False)

    logger.info("✅ Saved %d rows to %s", len(master_df), output_csv)


# --- CLI wrapper (kept minimal) ---

def parse_args():
    parser = argparse.ArgumentParser(
        description="Build biomass dataset"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-download from Google Drive",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run(refresh=args.refresh)


if __name__ == "__main__":
    main()