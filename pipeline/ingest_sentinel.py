import ee
import os
import json
from pathlib import Path
import geopandas as gpd
import pandas as pd
from datetime import datetime, timedelta

# === SECURE EE AUTH ===
def _init_ee():
    """Initialize EE using service account from secrets"""
    try:
        # 1. Streamlit Cloud Secrets
        if "EE_PRIVATE_KEY" in os.environ:
            key_data = json.loads(os.environ["EE_PRIVATE_KEY"])
            service_account = os.environ.get("EE_SERVICE_ACCOUNT")
            credentials = ee.ServiceAccountCredentials(service_account, key_data=key_data)
            ee.Initialize(credentials)
            print(f"EE: Initialized with service account {service_account}")
            return True

        # 2. Local ee_key.json
        key_path = Path("ee_key.json")
        if key_path.exists():
            credentials = ee.ServiceAccountCredentials(email=None, key_file=str(key_path))
            ee.Initialize(credentials)
            print("EE: Initialized with ee_key.json")
            return True

        # 3. Fallback: Try user auth (local only)
        try:
            ee.Initialize()
            print("EE: Initialized with user auth (local only)")
            return True
        except:
            pass

    except Exception as e:
        print(f"EE Auth failed: {e}")
        return False

    return False

# Initialize at import
_ee_ready = _init_ee()

def get_sentinel_ndvi(fields_gdf, days_back=30):
    if not _ee_ready:
        print("EE not available → returning mock NDVI")
        # Return mock data for demo
        dates = pd.date_range(end=datetime.now(), periods=days_back, freq='5D')
        mock_data = []
        for _, field in fields_gdf.iterrows():
            for date in dates:
                mock_data.append({
                    'field_id': field['field_id'],
                    'date': date.date(),
                    'ndvi_mean': 0.3 + 0.4 * (date.dayofyear / 365) + 0.1 * (field.name % 3)
                })
        return pd.DataFrame(mock_data)

    # === REAL EE CODE BELOW ===
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Convert GDF to EE FeatureCollection
        features = []
        for _, row in fields_gdf.iterrows():
            geom = row.geometry.__geo_interface__
            feature = ee.Feature(geom, {'field_id': row['field_id']})
            features.append(feature)
        fc = ee.FeatureCollection(features)

        # Sentinel-2
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                      .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                      .filterBounds(fc)
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

        def calculate_ndvi(image):
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            return image.addBands(ndvi)

        collection = collection.map(calculate_ndvi)

        def zonal_stats(image):
            stats = image.reduceRegions(
                collection=fc,
                reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', True),
                scale=10
            )
            date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
            return stats.map(lambda f: f.set('date', date))

        results = collection.map(zonal_stats).flatten()

        # Get data
        data = results.getInfo()['features']
        records = []
        for feat in data:
            props = feat['properties']
            if 'NDVI' in props:
                records.append({
                    'field_id': props['field_id'],
                    'date': props['date'],
                    'ndvi_mean': props['NDVI'],
                    'ndvi_std': props.get('NDVI_stdDev', None)
                })
        return pd.DataFrame(records)

    except Exception as e:
        print(f"EE query failed: {e}")
        return pd.DataFrame()  # empty
    