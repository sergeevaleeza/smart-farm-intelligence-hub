from qgis.core import (
    QgsApplication, QgsProject, QgsVectorLayer, QgsRasterLayer,
    QgsLayerTreeLayer, QgsSingleBandPseudoColorRenderer,
    QgsRasterShader, QgsColorRampShader, QgsRasterBandStats
)
from qgis.PyQt.QtGui import QColor
import os
import numpy as np
from osgeo import gdal
import getpass

# Silence GDAL warning
gdal.UseExceptions()

def export_qgis_project(db_path="data/weekly_pipeline.db", output_qgz="data/SmartFarm.qgz"):
    # Fix for WSL: Create user-owned runtime dir
    runtime_dir = f"/tmp/qgis-{getpass.getuser()}"
    os.makedirs(runtime_dir, exist_ok=True)
    os.chmod(runtime_dir, 0o700)  # Secure
    os.environ['XDG_RUNTIME_DIR'] = runtime_dir

    QgsApplication.setPrefixPath("/usr", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    project = QgsProject.instance()

    # 1. Field boundaries
    fields_layer = QgsVectorLayer("data/raw/fields.geojson", "Farm Fields", "ogr")
    if not fields_layer.isValid():
        print("Fields layer invalid")
        qgs.exitQgis()
        return
    project.addMapLayer(fields_layer, False)

    # 2. Mock NDVI raster
    os.makedirs("data/processed", exist_ok=True)
    tif_path = "data/processed/ndvi_latest.tif"
    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(tif_path, 100, 100, 1, gdal.GDT_Float32)
    ds.SetGeoTransform([-89.0, 0.0001, 0, 40.6, 0, -0.0001])
    band = ds.GetRasterBand(1)
    data = np.random.uniform(0.3, 0.8, (100, 100))
    band.WriteArray(data)
    ds = None

    ndvi_raster = QgsRasterLayer(tif_path, 'NDVI (Latest)')
    if not ndvi_raster.isValid():
        print("Raster invalid")
        qgs.exitQgis()
        return
    project.addMapLayer(ndvi_raster, False)

    # 3. Style NDVI
    shader = QgsRasterShader()
    color_ramp = QgsColorRampShader()
    color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
    color_ramp.setColorRampItemList([
        QgsColorRampShader.ColorRampItem(0.0, QColor(165, 0, 38), 'Stressed'),
        QgsColorRampShader.ColorRampItem(0.4, QColor(255, 255, 192), 'Moderate'),
        QgsColorRampShader.ColorRampItem(0.8, QColor(0, 104, 55), 'Healthy')
    ])
    shader.setRasterShaderFunction(color_ramp)
    renderer = QgsSingleBandPseudoColorRenderer(ndvi_raster.dataProvider(), 1, shader)
    ndvi_raster.setRenderer(renderer)

    # 4. Layer tree
    root = project.layerTreeRoot()
    root.insertLayer(0, ndvi_raster)
    root.insertLayer(0, fields_layer)

    # 5. Save
    project.write(output_qgz)
    print(f"QGIS project saved: {output_qgz}")
    qgs.exitQgis()