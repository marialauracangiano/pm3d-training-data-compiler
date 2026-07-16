# scripts/build_image_master.py

import argparse

from analytics_pipeline.processing.datasets.image_master import build_image_master
from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.config.load import load_yaml
from analytics_pipeline.config.validate import require_keys, require_type
from analytics_pipeline.paths import protocol_processed_dir
from analytics_pipeline.processing.transforms.plot_id import build_plot_id


def run(protocol: str | None = None, refresh: bool = False):
    logger.info("Loading image configuration from YAML")
    
    pipeline_config = load_yaml("pipeline.yaml")
    
    require_keys(
        pipeline_config,
        ["image"],
        "pipeline config",
    )
    
    image_config = pipeline_config["image"]
    
    if protocol is None:
        logger.info("Loading unfiltered image configuration")
        protocol_name = "UNFILTERED"
        protocol_config = None
        protocol_filters = {}

    else:
        logger.info(
            "Loading image configuration for protocol '%s'",
            protocol,
        )

        protocol_config = load_yaml(f"{protocol.lower()}.yaml")
        
        require_keys(
            protocol_config,
            [
                "image",
                "plot_id",
            ],
            "protocol config",
        )

        protocol_name = protocol.upper()
        protocol_filters = protocol_config["image"].get("filters", {})
        
    # --- Validation ---
    require_keys(
        image_config,
        ["columns_to_keep"],
        "image config",
    )

    require_type(
        image_config["columns_to_keep"],
        list,
        "columns_to_keep",
    )

    # --- Extract config AFTER validation ---
    image_cleaning_config = {
        "filters": protocol_filters,
        "columns_to_keep": image_config["columns_to_keep"],
        "drop_zero_distance": image_config.get("drop_zero_distance", True),
    }

    logger.info("Starting image master build pipeline")

    df = build_image_master(
        refresh=refresh,
        cleaning_config=image_cleaning_config,
    )
    if protocol is not None:
        df = build_plot_id(
            df,
            protocol_config,
            source="image",
        )

    output_dir = protocol_processed_dir(protocol_name)
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
    
    parser.add_argument(
        "--protocol",
        # default="b4i",
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