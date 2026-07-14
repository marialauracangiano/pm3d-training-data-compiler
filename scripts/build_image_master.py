# scripts/build_image_master.py

import argparse
from pathlib import Path

from analytics_pipeline.processing.datasets.image_master import build_image_master
from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.config.load import load_yaml
from analytics_pipeline.config.validate import require_keys, require_type
from analytics_pipeline.paths import protocol_processed_dir


def run(protocol: str | None = None, refresh: bool = False):
    logger.info("Loading image configuration from YAML")
    config = load_yaml("image.yaml")
    
    if protocol is None:
        protocol_name = "UNFILTERED"
        protocol_filters = {}
    else:
        
        protocol = protocol.upper()

        if protocol not in config["filters"]:
            raise ValueError(
                f"No filters defined for protocol '{protocol}' in image.yaml"
            )

        protocol_name = protocol
        protocol_filters = config["filters"][protocol]

    # --- Validation ---
    require_keys(
        config,
        ["filters", "columns_to_keep"],
        "image config",
    )

    require_type(config["columns_to_keep"], list, "columns_to_keep")
    require_type(config["filters"], dict, "filters")

    # --- Extract config AFTER validation ---
    image_cleaning_config = {
        "filters": protocol_filters,
        "columns_to_keep": config["columns_to_keep"],
        "drop_zero_distance": config.get("drop_zero_distance", True),
    }

    logger.info("Starting image master build pipeline")

    df = build_image_master(
        refresh=refresh,
        cleaning_config=image_cleaning_config,
    )

    output_dir = protocol_processed_dir(protocol_name)

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
    
    parser.add_argument(
        "--protocol",
        default="b4i",
        help="Protocol name (e.g. b4i, calib_cover_crops)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run(
        protocol=args.protocol,
        refresh=args.refresh,
    )


if __name__ == "__main__":
    main()