# pipeline/yield_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import sqlite3
import warnings
warnings.filterwarnings("ignore")

def train_yield_model(db_path="data/weekly_pipeline.db"):
    conn = sqlite3.connect(db_path)
    
    # Load data
    ndvi = pd.read_sql("SELECT field_id, date, ndvi_mean FROM sentinel_ndvi", conn)
    weather = pd.read_sql("SELECT date, gdd FROM weather_daily", conn)
    fields = pd.read_sql("SELECT field_id, crop_2025 FROM farm_fields", conn)
    usda = pd.read_sql("SELECT year, yield_bu_acre FROM usda_yield WHERE commodity='Corn'", conn)
    
    conn.close()

    # Prep NDVI: latest + trend
    ndvi['date'] = pd.to_datetime(ndvi['date'])
    latest = ndvi.sort_values('date').groupby('field_id').tail(1)
    trend = ndvi.groupby('field_id').apply(
        lambda x: np.polyfit(range(len(x)), x['ndvi_mean'], 1)[0] if len(x) > 3 else 0
    ).reset_index(name='ndvi_trend')

    # GDD to date
    weather['date'] = pd.to_datetime(weather['date'])
    gdd_total = weather['gdd'].sum()

    # Merge
    df = latest.merge(trend, on='field_id').merge(fields, on='field_id')
    df['gdd_total'] = gdd_total
    df['ndvi_latest'] = df['ndvi_mean']
    df = df[['field_id', 'ndvi_latest', 'ndvi_trend', 'gdd_total', 'crop_2025']]

    # Historical baseline
    hist_yield = usda['yield_bu_acre'].mean()

    # Simple model: NDVI + GDD → yield
    X = df[['ndvi_latest', 'ndvi_trend', 'gdd_total']]
    y = np.array([hist_yield + (row['ndvi_latest'] - 0.7) * 100 + row['ndvi_trend'] * 1000 
                  for _, row in df.iterrows()])

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Predict
    preds = model.predict(X)
    df['yield_pred'] = preds
    df['yield_pred'] = df['yield_pred'].round(1)

    return df[['field_id', 'yield_pred']], hist_yield
