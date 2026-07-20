#tests/test_biomass_format.py

import pandas as pd

from analytics_pipeline.processing.transforms.biomass_format import (
    transform_biomass_wide_to_long,
)


def test_transform_biomass_wide_to_long():
    df = pd.DataFrame(
        {
            "affiliation": ["MD-Mirsky"],
            "plot_id": ["101"],
            "current_year": [2025],
            "Species 1": ["Cereal rye"],
            "Weight 1": [10.5],
            "Species 2": ["Crimson clover"],
            "Weight 2": [5.0],
            "Other Weight": [2.5],
        }
    )

    config = {
        "wide_format": {
            "base_columns": [
                "affiliation",
                "plot_id",
                "current_year",
            ],
            "groups": [
                {
                    "name": "species_1",
                    "species_column": "Species 1",
                    "weight_column": "Weight 1",
                },
                {
                    "name": "species_2",
                    "species_column": "Species 2",
                    "weight_column": "Weight 2",
                },
                {
                    "name": "other",
                    "weight_column": "Other Weight",
                },
            ],
        }
    }

    result = transform_biomass_wide_to_long(df, config)

    assert len(result) == 3

    assert set(result["species"]) == {
        "Cereal rye",
        "Crimson clover",
        "Other",
    }

    assert set(result["dry_weight_g"]) == {
        10.5,
        5.0,
        2.5,
    }

    assert all(
        col in result.columns
        for col in [
            "affiliation",
            "plot_id",
            "current_year",
            "species",
            "dry_weight_g",
        ]
    )