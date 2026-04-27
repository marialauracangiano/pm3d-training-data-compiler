# scripts/build_calibration_report.py 
import pandas as pd
from pathlib import Path

import plotly.express as px
from jinja2 import Environment, FileSystemLoader

from analytics_pipeline.config.logging_config import logger
from analytics_pipeline.paths import PROCESSED_DIR, PROJECT_ROOT


REPORTS_DIR = PROJECT_ROOT / "reports"
TEMPLATES_DIR = PROJECT_ROOT / "reports" / "templates"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_diagnostics():
    logger.info("Loading diagnostic CSVs")

    reconciliation = pd.read_csv(PROCESSED_DIR / "diagnostics/calibration_reconciliation.csv")
    coverage_aff = pd.read_csv(PROCESSED_DIR / "diagnostics/coverage_by_affiliation.csv")
    coverage_year_aff = pd.read_csv(PROCESSED_DIR / "diagnostics/coverage_by_year_affiliation.csv")

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
        reconciliation
        .assign(status=lambda df: df["missing_source"].fillna("matched"))
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


def render_report(summary, plots):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("calibration_report.html")

    html = template.render(
        summary=summary,
        plots=plots,
    )

    output_path = REPORTS_DIR / "calibration_report.html"
    output_path.write_text(html)

    logger.info("✅ Calibration report written to %s", output_path)


def main():
    reconciliation, coverage_aff, coverage_year_aff = load_diagnostics()

    summary = build_summary(reconciliation)
    plots = build_plots(reconciliation, coverage_aff, coverage_year_aff)

    render_report(summary, plots)


if __name__ == "__main__":
    main()
