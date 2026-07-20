#tests/test_biomass_cleaning.py

import pandas as pd

from analytics_pipeline.processing.transforms.biomass import (
    clean_biomass_data,
)


def test_clean_biomass_data():
    df = pd.DataFrame(
        {
            "Image Name (from PlantMap3D app)": [
                "DV-Testing_sample1",
                "DE-VanGessel_sample2",
                "DV-Testing_sample3",
                "DV-Testing_sample4",
            ],
            "Sample Date": [
                "2025-05-01",
                "2025-05-02",
                "2025-05-03",
                "2025-05-04",
            ],
            "Mix name": [
                "Mix A",
                "Mix B",
                "Mix C",
                "Mix D",
            ],
            "Dry Weight": [
                10.5,
                20.0,
                0,
                None,
            ],
            "Extra Column": [
                "remove",
                "remove",
                "remove",
                "remove",
            ],
        }
    )

    result = clean_biomass_data(
        df,
        affiliation_source_column="Image Name (from PlantMap3D app)",
        affiliation_map={
            "DV-Testing": "DV",
            "DE-VanGessel": "DE",
        },
        rename_map={
            "Sample Date": "sample_date",
            "Mix name": "mix_name",
            "Dry Weight": "dry_weight_g",
        },
        columns_to_keep=[
            "affiliation",
            "sample_date",
            "mix_name",
            "dry_weight_g",
        ],
    )

    # Two rows should remain
    # Rows with zero and null dry weight are removed
    assert len(result) == 2

    # Verify affiliation extraction and mapping
    assert result["affiliation"].tolist() == [
        "DV",
        "DE",
    ]

    # Verify renamed columns
    assert list(result.columns) == [
        "affiliation",
        "sample_date",
        "mix_name",
        "dry_weight_g",
    ]

    # Verify invalid biomass rows were removed
    assert result["dry_weight_g"].tolist() == [
        10.5,
        20.0,
    ]