# scripts/build_image_master.py

import argparse
from pathlib import Path

from analytics_pipeline.processing.datasets.image_master import build_image_master
from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.config.load import load_yaml
from analytics_pipeline.config.validate import require_keys, require_type


def run(refresh: bool = False):
    logger.info("Loading image configuration from YAML")
    config = load_yaml("image.yaml")

    # --- Validation ---
    require_keys(
        config,
        ["user_type_value", "columns_to_keep"],
        "image config",
    )

    require_type(config["columns_to_keep"], list, "columns_to_keep")

    # --- Extract config AFTER validation ---
    image_cleaning_config = {
        "user_type_value": config["user_type_value"],
        "columns_to_keep": config["columns_to_keep"],
        "drop_zero_distance": config.get("drop_zero_distance", True),
    }

    logger.info("Starting image master build pipeline")

    df = build_image_master(
        refresh=refresh,
        cleaning_config=image_cleaning_config,
    )

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = output_dir / "image_master.csv"

    logger.info("Saving image master CSV to %s", output_csv)

    df.to_csv(output_csv, index=False)

    logger.info(
        "✅ Saved image master dataset with %d rows and %d columns",
        len(df),
        len(df.columns),
    )


# --- CLI wrapper ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build image master dataset from Postgres"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-querying Postgres instead of using cached CSV",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run(refresh=args.refresh)


if __name__ == "__main__":
    main()