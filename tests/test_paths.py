#tests/test_paths.py

from analytics_pipeline.paths import (
    protocol_processed_dir,
    biomass_protocol_subdir,
)


def test_protocol_processed_dir():
    path = protocol_processed_dir("b4i")

    assert path.name == "B4I"
    assert path.exists()


def test_biomass_protocol_subdir():
    path = biomass_protocol_subdir(
        "b4i",
        2025,
    )

    assert path.name == "2025"
    assert path.parent.name == "b4i"
    assert path.exists()