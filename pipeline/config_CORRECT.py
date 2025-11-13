import os
from pathlib import Path

def load_config():
    return {
        "farm": {
            "name": "Central IL 500-Acre Farm",
            "state": "Illinois",
            "county": "McLean",
            "fields_shp": "data/raw/fields.geojson"
        },
        "data_sources": {
            "usda": {
                "api_key": os.getenv("USDA_API_KEY", "0696B91F-31C8-3E89-99FD-C3B4CDF2F1CB")
            },
            "noaa": {
                "station_id": "GHCND:USC00116200", # NORMAL 4 NE, IL US
                "token": os.getenv("NOAA_TOKEN", "rylTRkJKBikRommhgVkESWUQDnZueXLu")  # ← ADD THIS
            },
            "sentinel": {
                "username": os.getenv("COPERNICUS_USER", "sergeevaleeza@gmail.com"),
                "password": os.getenv("COPERNICUS_PASS", "SERG120liza!")
            }
        }
    }
