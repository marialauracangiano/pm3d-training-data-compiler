# run_pipeline.py

import argparse

from analytics_pipeline.config.logging_config import logger

# Import pipeline steps
from scripts.build_biomass_master import run as run_biomass
from scripts.build_image_master import run as run_image
from scripts.build_calibration_dataset import run as run_calibration
from scripts.build_calibration_report import run as run_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run analytics pipeline"
    )

    parser.add_argument(
        "step",
        nargs="?",
        default="all",
        choices=["biomass", "image", "calibration", "report", "all"],
        help="Pipeline step to run (default: all)",
    )

    parser.add_argument(
        "--protocol",
        help="Protocol name (optional for image step)",
    )
    
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh external data (biomass/image)",
    )

    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Enable diagnostics (calibration)",
    )

    return parser.parse_args()


# --- Individual steps ---

def run_step_biomass(args):        
    logger.info("Running biomass step")

    run_biomass(
        config_file=f"{args.protocol}.yaml",
        refresh=args.refresh,
    )

def run_step_image(args):
    logger.info("Running image step")
    run_image(
        protocol=args.protocol,
        refresh=args.refresh,
    )

def run_step_calibration(args):
    logger.info("Running calibration step")
    run_calibration(
        protocol=args.protocol,
        diagnostics=args.diagnostics,
        )


def run_step_report(args):
    if not args.diagnostics:
        raise ValueError(
            "Report generation requires diagnostics. Run calibration with --diagnostics first."
        )
        
    logger.info("Running report step")

    run_report(
        protocol=args.protocol,
    )
    
def validate_args(args):
    if (
        args.step in {"all", "biomass", "calibration", "report"}
        and args.protocol is None
    ):
        raise ValueError(
            "--protocol is required for this pipeline step."
        )

# --- Full pipeline ---

def run_all(args):
    logger.info("🚀 Running full pipeline")

    logger.info("Step 1: Biomass")
    run_step_biomass(args)

    logger.info("Step 2: Image")
    run_step_image(args)

    logger.info("Step 3: Calibration")
    run_step_calibration(args)

    if args.diagnostics:
        logger.info("Step 4: Report")
        run_step_report(args)
    else:
        logger.info(
            "Skipping report generation "
            "(run with --diagnostics to generate report)"
        )

    logger.info("✅ Pipeline completed successfully")


# --- Entry point ---

def main():
    args = parse_args()

    validate_args(args)

    steps = {
        "biomass": run_step_biomass,
        "image": run_step_image,
        "calibration": run_step_calibration,
        "report": run_step_report,
        "all": run_all,
    }

    steps[args.step](args)


if __name__ == "__main__":
    main()