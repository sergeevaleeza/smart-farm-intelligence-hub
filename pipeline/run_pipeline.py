import logging
from .clean_merge import merge_to_db
from .export_qgis import export_qgis_project

logging.basicConfig(filename='pipeline.log', level=logging.INFO)

def run_weekly_pipeline():
    logging.info("Pipeline started")
    try:
        merge_to_db()
        export_qgis_project()
        logging.info("Pipeline + QGIS export succeeded")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_weekly_pipeline()
