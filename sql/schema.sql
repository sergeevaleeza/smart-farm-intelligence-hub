-- Drop and recreate tables
DROP TABLE IF EXISTS farm_fields;
DROP TABLE IF EXISTS sentinel_ndvi;
DROP TABLE IF EXISTS weather_daily;
DROP TABLE IF EXISTS usda_yield;

-- Farm fields
CREATE TABLE farm_fields (
    field_id TEXT PRIMARY KEY,
    crop_2025 TEXT
);

-- NDVI
CREATE TABLE sentinel_ndvi (
    field_id TEXT,
    date DATE,
    ndvi_mean REAL,
    ndvi_std REAL,
    cloud_cover REAL DEFAULT 0,
    FOREIGN KEY (field_id) REFERENCES farm_fields(field_id)
);

-- Weather: ALL COLUMNS OPTIONAL (safe for partial data)
CREATE TABLE weather_daily (
    date DATE PRIMARY KEY,
    tmax REAL,
    tmin REAL,
    prcp REAL,
    gdd REAL
);

-- USDA
CREATE TABLE usda_yield (
    year INTEGER,
    commodity TEXT,
    yield_bu_acre REAL
);