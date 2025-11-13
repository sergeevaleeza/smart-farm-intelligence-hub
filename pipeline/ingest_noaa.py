import requests
import pandas as pd
from datetime import datetime, timedelta
from .config import load_config
import os
import json
import geopandas as gpd  # ← ADD THIS

# Cache file
CACHE_FILE = "data/.noaa_station_cache.json"

def find_best_station(lat, lon, token, max_distance_km=60):
    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/stations"
    headers = {'token': token}
    params = {
        'datasetid': 'GHCND',
        'datatypeid': 'TMAX',
        'limit': 1000,
        'extent': f"{lat-1},{lon-1},{lat+1},{lon+1}",
        'units': 'standard'
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=20)
        if r.status_code != 200:
            print(f"Station search failed: {r.status_code}")
            return None
        data = r.json().get('results', [])
        if not data:
            return None

        candidates = []
        for s in data:
            if s.get('maxdate', '') >= '2025-01-01' and s.get('datacoverage', 0) > 0.9:
                station_id = s['id']
                name = s['name']
                distance = ((s['latitude'] - lat)**2 + (s['longitude'] - lon)**2)**0.5 * 111
                if distance <= max_distance_km:
                    candidates.append((distance, station_id, name))

        if not candidates:
            return None
        candidates.sort()
        best_id = candidates[0][1]
        print(f"Best NOAA station: {best_id} ({candidates[0][2]}) @ {candidates[0][0]:.1f} km")
        return best_id
    except Exception as e:
        print(f"Station search error: {e}")
        return None

def load_cached_station():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            if data.get('expires', 0) > datetime.now().timestamp():
                return data['station_id']
    return None

def save_cached_station(station_id):
    os.makedirs("data", exist_ok=True)
    cache = {
        'station_id': station_id,
        'expires': (datetime.now() + timedelta(days=30)).timestamp()
    }
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_noaa_weather():
    cfg = load_config()
    token = cfg['data_sources']['noaa']['token']

    if token == "YOUR_NOAA_TOKEN_HERE":
        print("NOAA token missing → using mock data")
        return _mock_weather()

    # === PRIORITIZE CONFIG STATION ===
    config_station = cfg['data_sources']['noaa'].get('station_id')
    if config_station:
        print(f"Using config station: {config_station}")
        # Test if it works
        test_data = _fetch_noaa_data(config_station, token)
        if test_data:
            print(f"Config station works: {len(test_data)} records")
            station_id = config_station
        else:
            print(f"Config station failed → auto-detecting")
            station_id = _get_or_find_station(token)
    else:
        station_id = _get_or_find_station(token)

    # Fetch data
    data = _fetch_noaa_data(station_id, token)
    if not data:
        print("No data from any station → using mock")
        return _mock_weather()

    print(f"NOAA: {len(data)} records from {station_id}")
    df = pd.DataFrame(data)
    df = df[df['datatype'].isin(['TMAX', 'TMIN', 'PRCP'])]
    if df.empty:
        return _mock_weather()

    df = df.pivot(index='date', columns='datatype', values='value').reset_index()
    df['date'] = pd.to_datetime(df['date'])

    # ROBUST GDD
    df['gdd'] = 0.0
    if 'TMAX' in df.columns and 'TMIN' in df.columns:
        tmax = df['TMAX'].fillna(70)
        tmin = df['TMIN'].fillna(50)
        avg = (tmax + tmin) / 2
        df['gdd'] = avg.clip(lower=50, upper=86) - 50
    else:
        print("NOAA: TMAX/TMIN missing → GDD = 0.0")

    # Safe rename
    rename_map = {}
    if 'PRCP' in df.columns: rename_map['PRCP'] = 'prcp'
    if 'TMAX' in df.columns: rename_map['TMAX'] = 'tmax'
    if 'TMIN' in df.columns: rename_map['TMIN'] = 'tmin'
    df = df.rename(columns=rename_map)

    cols = ['date']
    for c in ['tmax', 'tmin', 'prcp', 'gdd']:
        if c in df.columns:
            cols.append(c)
    return df[cols].dropna(subset=['date'])

def _fetch_noaa_data(station_id, token):
    """Fetch raw data from NOAA (helper)"""
    end = datetime.today().strftime('%Y-%m-%d')
    start = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    params = {
        'datasetid': 'GHCND',
        'stationid': station_id,
        'startdate': start,
        'enddate': end,
        'datatypeid': 'TMAX,TMIN,PRCP',
        'limit': 1000,
        'units': 'standard'
    }
    headers = {'token': token}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=20)
        if r.status_code == 401:
            return None
        r.raise_for_status()
        return r.json().get('results', [])
    except:
        return None

def _get_or_find_station(token):
    """Get cached or auto-detect station"""
    station_id = load_cached_station()
    if station_id:
        return station_id

    # Auto-detect
    try:
        fields_gdf = gpd.read_file("data/raw/fields.geojson")
        centroid = fields_gdf.unary_union.centroid
        lat, lon = centroid.y, centroid.x
    except:
        lat, lon = 40.49, -88.99  # McLean County

    station_id = find_best_station(lat, lon, token)
    if station_id:
        save_cached_station(station_id)
    return station_id

def _get_or_find_station(token):
    """Get cached or auto-detect station"""
    station_id = load_cached_station()
    if station_id:
        return station_id

    # Auto-detect
    try:
        fields_gdf = gpd.read_file("data/raw/fields.geojson")
        centroid = fields_gdf.unary_union.centroid
        lat, lon = centroid.y, centroid.x
    except:
        lat, lon = 40.49, -88.99  # McLean County

    station_id = find_best_station(lat, lon, token)
    if station_id:
        save_cached_station(station_id)
    return station_id

def _mock_weather():
    dates = pd.date_range(end=datetime.today(), periods=5, freq='D')
    return pd.DataFrame({
        'date': dates,
        'tmax': [55, 58, 60, 57, 54],
        'tmin': [38, 40, 42, 39, 37],
        'prcp': [0.0, 0.1, 0.0, 0.3, 0.0],
        'gdd': [1.5, 4.0, 6.0, 3.0, 0.5]
    })