"""
Configuration settings for the Weather Aggregator.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
os.makedirs(DATA_DIR, exist_ok=True)

# FMI API Settings
FMI_API_KEY = os.getenv("FMI_API_KEY", "")
FMI_API_ENDPOINT = "https://opendata.fmi.fi/wfs"

# Default parameters
DEFAULT_LOCATION = "Helsinki"
DEFAULT_START_DATE = "2023-01-01"
DEFAULT_END_DATE = "2023-12-31"
DEFAULT_PARAMETERS = ["temperature", "humidity", "wind_speed"]

# Timeout for API requests (in seconds)
REQUEST_TIMEOUT = 30

# Cache settings
CACHE_ENABLED = True
CACHE_DIR = DATA_DIR / "cache"
CACHE_EXPIRY_DAYS = 7


def validate_config():
    """Validate the configuration settings."""
    if not FMI_API_KEY:
        raise ValueError(
            "FMI_API_KEY is not set. Please set it in the .env file or "
            "environment variables."
        )

    # Create necessary directories
    for directory in [DATA_DIR, CACHE_DIR]:
        os.makedirs(directory, exist_ok=True)

    return True
