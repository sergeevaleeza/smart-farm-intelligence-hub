import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from pipeline import train_yield_model, load_config
from twilio.rest import Client

config = load_config()
yield_df, hist = train_yield_model()

st.set_page_config(page_title="Smart Farm", layout="wide")
st.title("Smart Farm Yield Intelligence Hub")

# Load data
@st.cache_data
def load_data():
    conn = sqlite3.connect("data/weekly_pipeline.db")
    ndvi = pd.read_sql("SELECT field_id, date, ndvi_mean FROM sentinel_ndvi", conn)
    weather = pd.read_sql("SELECT date, tmax, tmin, prcp, gdd FROM weather_daily", conn)
    fields = pd.read_sql("SELECT field_id, crop_2025 FROM farm_fields", conn)
    conn.close()
    ndvi['date'] = pd.to_datetime(ndvi['date'])
    weather['date'] = pd.to_datetime(weather['date'])
    return ndvi, weather, fields

ndvi, weather, fields = load_data()

# Yield forecast
yield_df, hist = train_yield_model()

# Historical Comparison + Yield Benchmarking
try:
    hist_ndvi, county_avg = get_benchmarks()
    current_ndvi = latest_ndvi['ndvi_mean'].iloc[-1]
    st.metric("vs. 2024 NDVI", f"{current_ndvi:.2f}", f"{current_ndvi - hist_ndvi:+.2f}")
    st.metric("vs. County Avg", f"{pred:.1f} bu/acre", f"{pred - county_avg:+.1f}")
except Exception as e:
    st.warning("Benchmarks unavailable (DB empty)")

# Sidebar
st.sidebar.header("Field Selector")
field_ids = ndvi['field_id'].unique()
selected_field = st.sidebar.selectbox("Choose Field", field_ids)

# Main
col1, col2 = st.columns(2)

with col1:
    st.subheader("NDVI Trend")
    field_ndvi = ndvi[ndvi['field_id'] == selected_field]
    fig1 = px.line(field_ndvi, x='date', y='ndvi_mean', title=f"NDVI - {selected_field}")
    fig1.add_hline(y=0.7, line_dash="dash", line_color="orange")
    st.plotly_chart(fig1, use_container_width=True)

    # Yield
    pred = yield_df[yield_df['field_id'] == selected_field]['yield_pred'].iloc[0]
    st.metric("2026 Yield Forecast", f"{pred} bu/acre", f"+{pred-hist:.1f} vs avg")

with col2:
    st.subheader("Weather & GDD")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=weather['date'], y=weather['gdd'], name='GDD', fill='tozeroy'))
    fig2.add_trace(go.Scatter(x=weather['date'], y=weather['prcp']*10, name='PRCP (x10)', yaxis='y2'))
    fig2.update_layout(yaxis2=dict(title="PRCP (in)", overlaying='y', side='right'))
    st.plotly_chart(fig2, use_container_width=True)

# Map
st.subheader("Farm Map")
import geopandas as gpd
gdf = gpd.read_file("data/raw/fields.geojson")
gdf = gdf.merge(yield_df, on='field_id')
fig = px.choropleth_mapbox(gdf, geojson=gdf.geometry, locations=gdf.index, color='yield_pred',
                           mapbox_style="carto-positron", zoom=12, center={"lat": 40.49, "lon": -88.99},
                           color_continuous_scale="YlGn", title="Yield Forecast")
st.plotly_chart(fig, use_container_width=True)

# Alerts
latest_ndvi = ndvi.sort_values('date').groupby('field_id').tail(1)
drops = latest_ndvi[latest_ndvi['ndvi_mean'] < 0.6]
if not drops.empty:
    st.error(f"ALERT: {len(drops)} fields below NDVI 0.6!")

st.subheader("Recommendations")
if not drops.empty:
    for _, drop in drops.iterrows():
        rec = "Scout for pests" if drop['ndvi_mean'] < 0.5 else "Check irrigation"
        st.warning(f"Field {drop['field_id']}: {rec} (NDVI: {drop['ndvi_mean']:.2f})")

# Weather-based recs
latest_weather = weather.tail(1)
if latest_weather['prcp'].iloc[0] < 0.1 and latest_weather['gdd'].iloc[0] > 20:
    st.info("Hot & dry: Schedule irrigation for all fields")

# Add SMS Alerts
#if st.button("Send SMS Alert"):
#    client = Client("ACxxx", "your_token")
#    client.messages.create(
#        to="+15551234567",
#        from_="+15559876543",
#        body=f"NDVI Drop Alert: Field {selected_field} = {field_ndvi['ndvi_mean'].iloc[-1]:.2f}"
#    )
#   st.success("SMS Sent!")

if st.button("Generate Weekly Report"):
    # PDF export (using reportlab)
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas("weekly_report.pdf", pagesize=letter)
    c.drawString(100, 750, f"Smart Farm Report - {datetime.now().date()}")
    c.drawString(100, 700, f"F1 Yield: {pred} bu/acre")
    c.save()
    st.download_button("Download PDF", data=open("weekly_report.pdf", "rb"), file_name="weekly_report.pdf")

# CSV Export
st.download_button("Export Data", data=yield_df.to_csv(), file_name="yields.csv")