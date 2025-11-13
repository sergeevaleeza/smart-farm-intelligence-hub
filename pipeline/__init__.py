# pipeline/__init__.py
from pipeline.config import load_config
from pipeline.ingest_usda import get_usda_yield
from pipeline.ingest_noaa import get_noaa_weather
from pipeline.clean_merge import merge_to_db
from pipeline.yield_model import train_yield_model, get_benchmarks  # ← ADD THIS
from pipeline.ingest_sentinel import get_sentinel_ndvi

__all__ = [
    "load_config",
    "get_usda_yield",
    "get_noaa_weather",
    "merge_to_db",
    "train_yield_model",
    "get_benchmarks",        # ← ADD THIS
    "get_sentinel_ndvi"
]