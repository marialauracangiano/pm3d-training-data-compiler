# src/analytics_pipeline/paths.py

from pathlib import Path

# -----------------------------------------------------------
# Base directories
# -----------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Domain-specific directories
BIOMASS_DIR = RAW_DIR / "biomass"   # <--- All Drive downloads go here
IMAGE_DIR = RAW_DIR / "image" # <--- All postgress data go here

# -----------------------------------------------------------
# Ensure directories exist
# -----------------------------------------------------------

# for p in [DATA_DIR, RAW_DIR, PROCESSED_DIR, BIOMASS_DIR, IMAGE_DIR]:
#     p.mkdir(parents=True, exist_ok=True)

for path in (
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    BIOMASS_DIR,
    IMAGE_DIR,
):
    path.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------
# Simple helpers
# -----------------------------------------------------------

def biomass_protocol_subdir(protocol: str, year: str | int) -> Path:
    """Return the cached raw image CSV path."""
    path = BIOMASS_DIR / protocol / str(year)
    path.mkdir(parents=True, exist_ok=True)
    return path

def protocol_processed_dir(protocol: str) -> Path:
    """Return the processed directory for a protocol."""
    path = PROCESSED_DIR / protocol.upper()
    path.mkdir(parents=True, exist_ok=True)
    return path

def raw_image_file() -> Path:
    """Return the raw image CSV file path."""
    return IMAGE_DIR / "image_master.csv"