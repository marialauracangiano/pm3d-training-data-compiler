# scripts/build_calibration_report.py
import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px
from jinja2 import Environment, FileSystemLoader

from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.paths import (
    PROJECT_ROOT,
    protocol_processed_dir,
)

TEMPLATES_DIR = PROJECT_ROOT / "reports" / "templates"


def load_diagnostics(processed_dir: Path):
    logger.info("Loading diagnostic CSVs")

    diagnostics_dir = processed_dir / "diagnostics"

    reconciliation = pd.read_csv(diagnostics_dir / "calibration_reconciliation.csv")

    coverage_aff = pd.read_csv(diagnostics_dir / "coverage_by_affiliation.csv")

    coverage_year_aff = pd.read_csv(
        diagnostics_dir / "coverage_by_year_affiliation.csv"
    )

    return reconciliation, coverage_aff, coverage_year_aff


def build_summary(reconciliation: pd.DataFrame) -> dict:
    total_rows = len(reconciliation)
    matched = (reconciliation["missing_source"].isna()).sum()
    missing = total_rows - matched

    pct_matched = matched / total_rows * 100 if total_rows else 0

    return {
        "total_rows": total_rows,
        "matched": matched,
        "missing": missing,
        "pct_matched": round(pct_matched, 1),
    }


def build_plots(reconciliation, coverage_aff, coverage_year_aff):
    plots = {}

    # Overall coverage
    coverage_counts = (
        reconciliation.assign(status=lambda df: df["missing_source"].fillna("matched"))
        .groupby("status")
        .size()
        .reset_index(name="count")
    )

    plots["overall_coverage"] = px.bar(
        coverage_counts,
        x="status",
        y="count",
        title="Overall data coverage",
    ).to_html(full_html=False)

    # Coverage by affiliation
    plots["coverage_by_affiliation"] = px.bar(
        coverage_aff,
        x="affiliation",
        y="row_count",
        color="missing_source",
        title="Coverage by affiliation",
    ).to_html(full_html=False)

    # Coverage over time
    plots["coverage_over_time"] = px.bar(
        coverage_year_aff,
        x="current_year",
        y="row_count",
        color="missing_source",
        facet_col="affiliation",
        title="Coverage over time by affiliation",
    ).to_html(full_html=False)

    return plots


def render_report(summary, plots, output_dir: Path):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("calibration_report.html")

    html = template.render(
        summary=summary,
        plots=plots,
    )

    report_dir = output_dir / "report"
    report_dir.mkdir(parents=True, exist_ok=True)

    output_path = report_dir / "calibration_report.html"
    output_path.write_text(html)

    logger.info("✅ Calibration report written to %s", output_path)


def run(protocol: str):
    logger.info("Building calibration report")

    processed_dir = protocol_processed_dir(protocol.upper())

    reconciliation, coverage_aff, coverage_year_aff = load_diagnostics(processed_dir)

    summary = build_summary(reconciliation)
    plots = build_plots(reconciliation, coverage_aff, coverage_year_aff)

    render_report(summary, plots, processed_dir)


def parse_args():
    parser = argparse.ArgumentParser(description="Build calibration report")

    parser.add_argument(
        "--protocol",
        help="Protocol to build the report for",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    run(protocol=args.protocol)


if __name__ == "__main__":
    main()
