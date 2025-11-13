import sqlite3
import pandas as pd
import geopandas as gpd
import os
from .ingest_usda import get_usda_yield
from .ingest_noaa import get_noaa_weather
from .ingest_sentinel import get_sentinel_ndvi

def init_db(conn):
    """Create schema from sql/schema.sql"""
    schema_path = 'sql/schema.sql'
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    print("Database schema initialized")

def merge_to_db():
    db_path = "data/weekly_pipeline.db"
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # INIT SCHEMA
    init_db(conn)
    
    # 1. USDA
    usda_df = get_usda_yield()
    usda_df.to_sql('usda_yield', conn, if_exists='replace', index=False)
    
    # 2. NOAA
    weather_df = get_noaa_weather()
    
    # Force correct dtypes
    weather_df['date'] = pd.to_datetime(weather_df['date']).dt.date  # → date, not datetime
    if 'tmax' in weather_df.columns:
        weather_df['tmax'] = pd.to_numeric(weather_df['tmax'], errors='coerce')
    if 'tmin' in weather_df.columns:
        weather_df['tmin'] = pd.to_numeric(weather_df['tmin'], errors='coerce')
    if 'prcp' in weather_df.columns:
        weather_df['prcp'] = pd.to_numeric(weather_df['prcp'], errors='coerce')
    if 'gdd' in weather_df.columns:
        weather_df['gdd'] = pd.to_numeric(weather_df['gdd'], errors='coerce')

    # Ensure all columns exist
    for col in ['tmax', 'tmin', 'prcp', 'gdd']:
        if col not in weather_df.columns:
            weather_df[col] = pd.NA

    weather_df = weather_df[['date', 'tmax', 'tmin', 'prcp', 'gdd']]
    weather_df.to_sql('weather_daily', conn, if_exists='replace', index=False)
    print(f"NOAA: {len(weather_df)} records saved")
    
    # 3. Fields (from GeoJSON)
    fields_path = "data/raw/fields.geojson"
    if not os.path.exists(fields_path):
        from create_sample_fields import create_sample_fields
        create_sample_fields()
    fields_gdf = gpd.read_file(fields_path)
    fields_df = fields_gdf[['field_id', 'crop_2025']].copy()
    fields_df.to_sql('farm_fields', conn, if_exists='replace', index=False)
    
# 4. NDVI
    ndvi_csv = os.path.join(processed_dir, "ndvi_zonal.csv")
    if os.path.exists(ndvi_csv):
        df = pd.read_csv(ndvi_csv)
        print(f"NDVI CSV columns: {list(df.columns)}")  # DEBUG

        # Auto-map
        col_map = {}
        for old, new in [('mean', 'ndvi_mean'), ('NDVI_mean', 'ndvi_mean'),
                         ('stdDev', 'ndvi_std'), ('NDVI_stdDev', 'ndvi_std'),
                         ('cloud_cover', 'cloud_cover'), ('CLOUDY_PIXEL_PERCENTAGE', 'cloud_cover')]:
            if old in df.columns:
                col_map[old] = new

        required = ['field_id', 'date', 'ndvi_mean', 'ndvi_std']
        missing = [c for c in required if c not in col_map.values() and c not in df.columns]
        if missing:
            print(f"NDVI CSV missing: {missing}")
        else:
            df = df.rename(columns=col_map)
            # Only select columns that exist
            cols_to_use = [c for c in ['field_id', 'date', 'ndvi_mean', 'ndvi_std', 'cloud_cover'] if c in df.columns]
            df = df[cols_to_use].copy()
            df['date'] = pd.to_datetime(df['date']).dt.date
            # Fill missing cloud_cover
            if 'cloud_cover' not in df.columns:
                df['cloud_cover'] = 0.0
            df.to_sql('sentinel_ndvi', conn, if_exists='append', index=False)
            print(f"Loaded {len(df)} NDVI records")
    else:
        print(f"NDVI CSV not found: {ndvi_csv}")

    conn.close()
    print(f"Database: {db_path}")