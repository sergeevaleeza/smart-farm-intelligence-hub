# **[Smart Farm Intelligence Hub](https://smart-farm-intelligence-app.streamlit.app/)

Predict, monitor, and optimize performance on a 500-acre corn–soybean rotation farm in Central Illinois.  
This repository contains an end-to-end precision-agriculture data pipeline, geospatial analysis engine, machine-learning forecasting models, and an interactive Streamlit dashboard.

The goal is to transform raw agricultural datasets into actionable weekly recommendations for yield optimization, input cost reduction, and climate resilience.

---

## Current Status (MVP)
The repository includes the initial implementation of the Smart Farm Intelligence Hub, with:

### 1. Data Ingestion & Cleaning
- Python ETL scripts for integrating multi-source agricultural datasets.
- USDA, NASA POWER/NOAA weather data, Sentinel-2 NDVI, and soil datasets.
- Standardized data schema prepared for SQLite storage.

### 2. Geospatial Crop Health Engine (Initial Version)
- NDVI ingestion and basic preprocessing.
- Field boundary support using GeoPandas.
- Early development of zonal NDVI analysis and stress detection.

### 3. Forecasting Model Framework (Skeleton)
- Framework setup for Prophet and Random Forest forecasting.
- Preliminary feature engineering for weather, NDVI, and crop growth metrics.

### 4. Streamlit Dashboard (Initial Build)
- Basic dashboard structure ready for integration.
- Sections prepared for maps, charts, and weekly recommendations.

### 5. Documentation & Project Roadmap
- Clear directory structure.
- Plans for expanded modules and future work.

---

## Project Overview
This capstone project spans 8 weeks of development from raw data ingestion to a deployable precision-agriculture dashboard.

### Capstone Timeline
| Week | Deliverable | Tools |
|------|-------------|-------|
| 1–2  | Data ingestion, ETL, cleaning | Python, pandas, SQL, Jupyter |
| 3–4  | Geospatial analysis | GeoPandas, Sentinel-2, QGIS |
| 5–6  | Forecasting, ML models | Prophet, scikit-learn |
| 7    | Streamlit dashboard | Streamlit, Plotly |
| 8    | Final report & deployment | Git, GitHub Pages |

---

## Core Components

### 1. Automated Data Pipeline
Integrates and unifies:
- USDA NASS weekly crop progress  
- NASA POWER / NOAA daily weather  
- Copernicus Sentinel-2 NDVI, LAI, 10m composites  
- Simulated John Deere equipment data  
- SoilGrid / SSURGO soil properties  

Data are stored in SQLite and updated on a weekly schedule.

---

### 2. Geospatial Crop Health Engine
- Computes zonal NDVI trends per field or management zone.
- Detects stress events based on historical averages.
- Overlays soil drainage and texture to explain anomalies.
- Exports GeoJSON for QGIS visualization.

---

### 3. Yield Forecasting (Hybrid ML + Time Series)
Yield model uses:
- NDVI peak values
- Growing Degree Days (GDD)
- Rainfall deficit
- Soil nutrient estimates
- Crop variety data

Approach:
- Prophet for baseline seasonality and trend.
- Random Forest for non-linear interactions.
- Validated against USDA county yields (2020–2024).

Outputs include 90-day yield forecasts with confidence intervals.

---

### 4. Prescriptive Recommendations Engine
Auto-generates weekly in-season recommendations such as:
- Nitrogen top-dress  
- Fungicide scouting alerts  
- Irrigation scheduling  

Triggers are derived from NDVI deviations, humidity conditions, GDD thresholds, and moisture deficits.

---

### 5. Streamlit Dashboard
Interactive app includes:
- NDVI maps and field boundaries
- Time-series charts
- Alerts and recommendations
- Auto-generated PDF field reports

To be deployed on Streamlit Community Cloud.

---

### 6. Ethics & Sustainability Module
Includes:
- Carbon footprint calculations for nitrogen fertilizer
- Water use efficiency metrics
- Soil organic matter trend scoring

A written ethics brief addresses:
- Satellite data bias (cloud cover, temporal gaps)
- Fairness considerations for smallholder farms

---

## Planned / Future Work

### Soil Moisture Sensor Integration
- Real sensor data integration (IoT).
- Volumetric water content (VWC) + soil temperature.
- Incorporation into irrigation recommendations and stress detection.

### Forecasting Enhancements
- Ensemble models (e.g., LSTM + Prophet).
- Confidence intervals and uncertainty quantification.

### Dashboard Additions
- Real-time feeds for soil sensors.
- Exportable field reports.
- Role-based user interface for farm stakeholders.

This will enable full real-world operational decision support.

---

### Additional Future Enhancements
- Ensemble forecasting (LSTM + Prophet)
- Drone imagery ingestion module
- Multi-field comparative analytics
- Data quality and anomaly scoring engine
- Automated QGIS project generation
- GitHub Actions for scheduled pipeline runs
- Mobile-friendly field scouting mode

---

## Repository Structure

```
smart-farm-intelligence-hub/
|
├── data/                         
├── pipeline/                     
├── sql/                          
├── LICENSE                       
├── README.md                     
├── config.toml                   
├── create_sample_fields.py       
├── main.py                      
├── pipeline.log                  
├── pyproject.toml                
├── requirements.txt              
├── streamlit_app.py              
├── test_part1.sh
```

---

## Final Deliverables
- Live Streamlit dashboard  
- Public GitHub repository with full documentation  
- 10-page technical capstone report (PDF)  
- 5-minute video walkthrough  
- QGIS project file (.qgz)

---

## Usage

### Local Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/sergeevaleeza/smart-farm-intelligence-hub.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run streamlit_app.py
   ```

---

## Contributing
This project is under active development. Contributions are welcome. 
Open issues or submit a pull request with your improvements.

---

## License
This project is released under the MIT License.

---
