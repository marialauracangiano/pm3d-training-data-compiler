import logging
from pathlib import Path
from analytics_pipeline.paths import PROJECT_ROOT

LOG_DIR = PROJECT_ROOT / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)  # ensure logs folder exists
LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,  # default logging level
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # also print to console
    ]
)

logger = logging.getLogger(__name__)