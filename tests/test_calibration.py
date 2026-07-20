#tests/test_calibration.py

import pandas as pd

from analytics_pipeline.processing.datasets.calibration import (
    build_calibration_dataset,
)


def test_build_calibration_dataset():
    biomass_df = pd.DataFrame(
        {
            "affiliation": [
                "MD-Mirsky",
                "MD-Mirsky",
            ],
            "plot_id": [
                "101",
                "102",
            ],
            "current_year": [
                2025,
                2025,
            ],
            "species": [
                "Cereal rye",
                "Crimson clover",
            ],
            "dry_weight_g": [
                10.5,
                5.0,
            ],
        }
    )

    image_df = pd.DataFrame(
        {
            "affiliation": [
                "MD-Mirsky",
                "MD-Mirsky",
            ],
            "plot_id": [
                "101",
                "999",
            ],
            "current_year": [
                2025,
                2025,
            ],
            "timing": [
                1,
                1,
            ],
            "set_distance": [
                10,
                20,
            ],
        }
    )

    result = build_calibration_dataset(
        biomass_df,
        image_df,
        merge_keys=[
            "affiliation",
            "plot_id",
            "current_year",
        ],
    )

    # Only the matching plot should remain
    assert len(result) == 1

    assert result.iloc[0]["plot_id"] == "101"

    assert result.iloc[0]["species"] == "Cereal rye"

    assert result.iloc[0]["dry_weight_g"] == 10.5

    assert result.iloc[0]["set_distance"] == 10