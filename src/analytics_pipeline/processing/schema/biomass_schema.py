# src/analytics_pipeline/processing/schema/biomass_schema.py

# -------------------------------------------------------
# Columns required for joining / identity / merging logic
# -------------------------------------------------------
PAIRING_COLUMNS = [
    "affiliation",
    "plot_id",
    "current_year",
]

# timing is standardized but NOT required
OPTIONAL_PAIRING_COLUMNS = [
    "timing",
]

# -------------------------------------------------------
# Scientific payload (flexible, evolves over time)
# -------------------------------------------------------
SCIENTIFIC_COLUMNS = [
    "species",
    "dry_weight_g",
]

# -------------------------------------------------------
# Full recommended output schema (union of everything)
# -------------------------------------------------------
STANDARD_BIOMASS_COLUMNS = (
    PAIRING_COLUMNS + OPTIONAL_PAIRING_COLUMNS + SCIENTIFIC_COLUMNS
)