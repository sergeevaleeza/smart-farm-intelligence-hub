# pipeline/ingest_sentinel.py
import ee
import geopandas as gpd
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# === CONFIG ===
PROJECT_ID = "smart-farm-ndvi"  # CHANGE THIS TO YOUR PROJECT ID
EXPORT_FOLDER = "SmartFarm"
EXPORT_PREFIX = "ndvi_zonal"
# ==============

def _ensure_ee_init():
    """Initialize EE with project if not already done"""
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception as e:
        if "no project" in str(e).lower():
            raise Exception(f"EE not initialized. Run: earthengine set_project {PROJECT_ID}")
        else:
            raise e

_ensure_ee_init()

def get_sentinel_ndvi(fields_gdf, days_back=30):
    if not ee.data._initialized:
        print("EE not initialized → returning mock NDVI")
    return _mock_ndvi_data()  # define a simple mock
    """
    Export NDVI zonal stats to Google Drive.
    Returns empty DF — data will be in Drive.
    """
    features = []
    for _, row in fields_gdf.iterrows():
        geom = row.geometry.__geo_interface__
        feature = ee.Feature(geom, {'field_id': row['field_id']})
        features.append(feature)
    fc = ee.FeatureCollection(features)

    end = datetime.utcnow()
    start = end - timedelta(days=days_back)

    s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
          .filterDate(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
          .filterBounds(fc.geometry())
          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30)))

    def add_ndvi(img):
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return img.addBands(ndvi).set('date', img.date().format('YYYY-MM-dd'))

    s2_ndvi = s2.map(add_ndvi).select('NDVI')

    def reduce_region(img):
        stats = img.reduceRegions(
            collection=fc,
            reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', True),
            scale=10
        )
        return stats.map(lambda f: f.set('date', img.get('date')))

    reduced = s2_ndvi.map(reduce_region).flatten()

    # === EXPORT TO DRIVE ===
    task = ee.batch.Export.table.toDrive(
        collection=reduced,
        description='NDVI_Weekly',
        folder=EXPORT_FOLDER,
        fileNamePrefix=EXPORT_PREFIX,
        fileFormat='CSV'
    )
    task.start()
    print(f"GEE Export started → Drive/{EXPORT_FOLDER}/{EXPORT_PREFIX}.csv")
    print(f"Task ID: {task.id}")

    # Wait up to 3 min
    for _ in range(18):
        status = task.status()
        if status['state'] in ['COMPLETED', 'FAILED', 'CANCELLED']:
            break
        print(f"  Status: {status['state']}...")
        time.sleep(10)

    if status['state'] == 'COMPLETED':
        print("Export completed! Check Google Drive.")
    else:
        print(f"Export {status['state']}: {status.get('error_message', '')}")

    return pd.DataFrame()  # Data comes from Drive
