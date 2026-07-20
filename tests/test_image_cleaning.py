#tests/test_image_cleaning.py

import pandas as pd

from analytics_pipeline.processing.transforms.image import (
    clean_image_data,
)


def test_clean_image_data():
    df = pd.DataFrame(
        {
            "user_type": [
                "researcher",
                "researcher",
                "installer",
                "researcher",
            ],
            "plot_id": [
                "101",
                "102",
                "103",
                "104",
            ],
            "timing": [
                1.0,
                2.0,
                1.0,
                3.0,
            ],
            "set_distance": [
                10,
                0,
                5,
                None,
            ],
            "extra_column": [
                "remove",
                "remove",
                "remove",
                "remove",
            ],
        }
    )

    config = {
        "filters": {
            "user_type": "researcher",
        },
        "columns_to_keep": [
            "plot_id",
            "timing",
            "set_distance",
        ],
    }

    result = clean_image_data(
        df,
        **config,
    )

    # Only one valid researcher row remains
    assert len(result) == 1

    # Verify correct row survived
    assert result.iloc[0]["plot_id"] == "101"

    # Verify columns were reduced
    assert list(result.columns) == [
        "plot_id",
        "timing",
        "set_distance",
    ]

    # Verify timing normalization
    assert str(result["timing"].dtype) == "Int64"

    # Verify invalid distances were removed
    assert result["set_distance"].iloc[0] == 10