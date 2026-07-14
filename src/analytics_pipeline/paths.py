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
IMAGE_DIR = RAW_DIR/ "image" # <--- All postgress data go here

# -----------------------------------------------------------
# Ensure directories exist
# -----------------------------------------------------------

for p in [DATA_DIR, RAW_DIR, PROCESSED_DIR, BIOMASS_DIR, IMAGE_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------
# Simple helpers
# -----------------------------------------------------------

def data_file(name: str) -> Path:
    """Return a file inside the data directory."""
    return DATA_DIR / name

def raw_file(name: str) -> Path:
    """Return a file inside the raw data directory."""
    return RAW_DIR / name

def processed_file(name: str) -> Path:
    """Return a file inside the processed data directory."""
    return PROCESSED_DIR / name

def biomass_subdir(dirname: str) -> Path:
    """Return a subdirectory inside raw/biomass/<dirname>."""
    d = BIOMASS_DIR / dirname
    d.mkdir(parents=True, exist_ok=True)
    return d

def biomass_protocol_subdir(protocol: str, year: str | int) -> Path:
    """
    Return:
    data/raw/biomass/<protocol>/<year>
    """
    d = BIOMASS_DIR / protocol / str(year)
    d.mkdir(parents=True, exist_ok=True)
    return d

def protocol_processed_dir(protocol: str) -> Path:
    """
    Return processed/<protocol>/.
    """
    d = PROCESSED_DIR / protocol.upper()
    d.mkdir(parents=True, exist_ok=True)
    return d

def raw_image_file() -> Path:
    """
    Return:
    data/raw/image/image_master.csv
    """
    return IMAGE_DIR / "image_master.csv"