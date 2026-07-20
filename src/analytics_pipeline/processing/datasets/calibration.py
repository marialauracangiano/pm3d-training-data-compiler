# src/analytics_pipeline/processing/datasets/calibration.py

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd
import hashlib

from analytics_pipeline.config.logging_config import logger


def build_calibration_dataset(
    biomass_df: pd.DataFrame,
    image_df: pd.DataFrame,
    *,
    merge_keys: List[str] | None = None,
    diagnostics: bool = False,
    output_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Build a calibration dataset by reconciling biomass and image data.

    This function performs an outer join to reconcile datasets and,
    optionally, generates diagnostic tables to inspect mismatches.
    The returned DataFrame contains only matched rows (inner join semantics).

    Parameters
    ----------
    biomass_df : pd.DataFrame
        Cleaned biomass master dataset.
    image_df : pd.DataFrame
        Cleaned image master dataset.
    merge_keys : list[str]
        Columns used to reconcile datasets. Must be provided.
    diagnostics : bool, default False
        If True, generate reconciliation and coverage diagnostics.
    output_dir : Path, optional
        Directory to write diagnostic CSVs.
        Required if diagnostics=True.

    Returns
    -------
    pd.DataFrame
        Model-ready calibration dataset (matched rows only).
    """
    if merge_keys is None:
        raise ValueError("merge_keys must be provided to build_calibration_dataset")
    keys = merge_keys
    _validate_merge_keys(biomass_df, image_df, keys)

    merged = _merge_biomass_and_images(biomass_df, image_df, keys)

    if diagnostics:
        if output_dir is None:
            raise ValueError("output_dir must be provided when diagnostics=True")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        diagnostics_tables = _generate_diagnostics(merged, keys)
        _write_diagnostics(diagnostics_tables, output_dir)

    calibration_df = _extract_calibration_dataset(merged)

    return calibration_df


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------


def _validate_merge_keys(
    biomass_df: pd.DataFrame,
    image_df: pd.DataFrame,
    merge_keys: List[str],
) -> None:
    """Ensure all merge keys exist in both datasets."""
    missing_biomass = set(merge_keys) - set(biomass_df.columns)
    missing_image = set(merge_keys) - set(image_df.columns)

    if missing_biomass or missing_image:
        raise KeyError(
            "Merge key validation failed:\n"
            f"  Missing in biomass_df: {sorted(missing_biomass)}\n"
            f"  Missing in image_df: {sorted(missing_image)}"
        )


def _merge_biomass_and_images(
    biomass_df: pd.DataFrame,
    image_df: pd.DataFrame,
    merge_keys: List[str],
) -> pd.DataFrame:
    """
    Perform an outer join between biomass and image datasets
    for reconciliation diagnostics.

    Adds:
    - _merge: pandas merge indicator (internal use)
    - missing_source: human-readable indicator of which dataset is missing
    """
    merged = biomass_df.merge(
        image_df,
        on=merge_keys,
        how="outer",
        indicator=True,
        suffixes=("_biomass", "_image"),
    )

    # Human-readable missing source
    merged["missing_source"] = (
        merged["_merge"]
        .astype(str)
        .map(
            {
                "left_only": "image",
                "right_only": "biomass",
                "both": None,
            }
        )
    )

    return merged


def _extract_calibration_dataset(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the model-ready calibration dataset (matched rows only).
    """
    calibration_df = merged_df.loc[merged_df["_merge"] == "both"].copy()

    # Drop merge diagnostics from final dataset
    calibration_df = calibration_df.drop(
        columns=["_merge", "missing_source"],
        errors="ignore",
    )

    return calibration_df


def _make_sample_id(row: pd.Series, merge_keys: List[str]) -> str:
    key = "|".join(str(row[k]) for k in merge_keys)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------


def _generate_diagnostics(
    merged_df: pd.DataFrame,
    merge_keys: List[str],
) -> Dict[str, pd.DataFrame]:
    """
    Generate diagnostic tables for reconciliation analysis.
    """
    diagnostics: Dict[str, pd.DataFrame] = {}

    merged_df = merged_df.copy()

    merged_df["sample_id"] = merged_df.apply(
        lambda row: _make_sample_id(row, merge_keys),
        axis=1,
    )

    # 1. Full reconciliation table
    diagnostics["calibration_reconciliation"] = merged_df.copy()

    # 2. Non-matching rows
    non_matching = merged_df.loc[merged_df["_merge"] != "both"].copy()

    # 3. Mismatch summary
    group_cols = merge_keys.copy()
    mismatch_summary = (
        non_matching.groupby(group_cols, dropna=False)
        .agg(
            count=("missing_source", "size"),
            missing_source=(
                "missing_source",
                lambda x: ", ".join(sorted(set(x))),
            ),
        )
        .reset_index()
    )

    diagnostics["mismatch_summary"] = mismatch_summary

    # 4. Coverage by affiliation (if present)
    if "affiliation" in merged_df.columns:
        coverage_affiliation = (
            merged_df.groupby(
                ["affiliation", "missing_source"],
                dropna=False,
                observed=True,
            )
            .agg(
                row_count=("sample_id", "size"),
                sample_count=("sample_id", "nunique"),
            )
            .reset_index()
        )
        diagnostics["coverage_by_affiliation"] = coverage_affiliation

    # 5. Coverage by year + affiliation (if present)
    if {"current_year", "affiliation"}.issubset(merged_df.columns):
        coverage_year_affiliation = (
            merged_df.groupby(
                ["current_year", "affiliation", "missing_source"],
                dropna=False,
                observed=True,
            )
            .agg(
                row_count=("sample_id", "size"),
                sample_count=("sample_id", "nunique"),
            )
            .reset_index()
        )
        diagnostics["coverage_by_year_affiliation"] = coverage_year_affiliation

    return diagnostics


def _write_diagnostics(
    diagnostics: Dict[str, pd.DataFrame],
    output_dir: Path,
) -> None:
    """
    Write diagnostic tables to CSV. under output_dir/diagnostics.
    """

    diagnostics_dir = output_dir / "diagnostics"
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing diagnostics to {diagnostics_dir}")

    for name, df in diagnostics.items():
        output_path = diagnostics_dir / f"{name}.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Saved diagnostic: {output_path.name}")
