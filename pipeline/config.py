import toml
import os
from pathlib import Path

def load_config():
    config_path = Path("config.toml")
    if not config_path.exists():
        raise FileNotFoundError("config.toml not found!")

    config = toml.load(config_path)

    # === SECURE OVERRIDE: GitHub Secrets / Streamlit Secrets / .env ===
    usda_key = (
        os.getenv("USDA_API_KEY") or
        os.getenv("USDA_KEY") or
        config["data_sources"]["usda"]["api_key"]
    )
    noaa_token = (
        os.getenv("NOAA_TOKEN") or
        os.getenv("NOAA_KEY") or
        config["data_sources"]["noaa"]["token"]
    )

    config["data_sources"]["usda"]["api_key"] = usda_key
    config["data_sources"]["noaa"]["token"] = noaa_token

    return config
