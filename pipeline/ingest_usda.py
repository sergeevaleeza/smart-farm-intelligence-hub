import requests
import pandas as pd
from io import StringIO
from .config_CORRECT import load_config

def get_usda_yield():
    cfg = load_config()
    url = "https://quickstats.nass.usda.gov/api/api_GET"
    params = {
        'key': cfg['data_sources']['usda']['api_key'],
        'commodity_desc': 'CORN',
        'year__GE': 2020,
        'state_name': 'ILLINOIS',
        'county_name': 'MCLEAN',
        'statisticcat_desc': 'YIELD',
        'format': 'CSV'
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))  # ← Fixed: use io.StringIO
        df = df[['year', 'Value']].rename(columns={'Value': 'yield_bu_acre'})
        df['commodity'] = 'Corn'
        return df
    except Exception as e:
        print(f"USDA failed: {e}")
        # Mock data
        return pd.DataFrame([
            {'year': 2023, 'yield_bu_acre': 198.0, 'commodity': 'Corn'},
            {'year': 2024, 'yield_bu_acre': 202.0, 'commodity': 'Corn'}
        ])