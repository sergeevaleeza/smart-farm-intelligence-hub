# create_sample_fields.py
import geopandas as gpd
from shapely.geometry import Polygon
import os

def create_sample_fields():
    os.makedirs("data/raw", exist_ok=True)
    poly1 = Polygon([
        (-88.995, 40.515), (-88.985, 40.515),
        (-88.985, 40.505), (-88.995, 40.505), (-88.995, 40.515)
    ])
    poly2 = Polygon([
        (-88.975, 40.515), (-88.965, 40.515),
        (-88.965, 40.505), (-88.975, 40.505), (-88.975, 40.515)
    ])
    gdf = gpd.GeoDataFrame([
        {'field_id': 'F1', 'crop_2025': 'Corn'},
        {'field_id': 'F2', 'crop_2025': 'Soybeans'}
    ], geometry=[poly1, poly2], crs="EPSG:4326")
    gdf.to_file("data/raw/fields.geojson", driver="GeoJSON")
    print("Sample fields saved: data/raw/fields.geojson")

if __name__ == "__main__":
    create_sample_fields()