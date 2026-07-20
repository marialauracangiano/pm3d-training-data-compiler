#tests/test_plot_id.py

import pandas as pd

from analytics_pipeline.processing.transforms.plot_id import build_plot_id


def test_composite_plot_id():
    df = pd.DataFrame(
        {
            "transect_id": [202],
            "set_set_number": [1],
        }
    )

    config = {
        "plot_id": {
            "image": {
                "type": "composite",
                "separator": "-",
                "components": [
                    {
                        "column": "transect_id",
                    },
                    {
                        "column": "set_set_number",
                    },
                ],
            }
        }
    }

    result = build_plot_id(
        df,
        config,
        source="image",
    )

    assert result.loc[0, "plot_id"] == "202-1"