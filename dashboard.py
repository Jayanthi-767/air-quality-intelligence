
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from backend.app.database import DATABASE_URL

st.set_page_config(
    page_title="Air Quality Intelligence",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 Air Quality Intelligence")
st.caption("Hyderabad, India | Data source: WAQI")

@st.cache_data(ttl=60)
def load_data():
    engine = create_engine(DATABASE_URL)

    query = """
    SELECT parameter, value, unit, measured_at, station_id
    FROM air_quality_measurements
    WHERE source = 'WAQI'
    ORDER BY measured_at DESC
    """

    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)

    if not df.empty:
        df["measured_at"] = pd.to_datetime(df["measured_at"])

    return df

df = load_data()

if df.empty:
    st.warning("No WAQI readings found. Run python fetch_waqi.py first.")
    st.stop()

# Keep the most recent saved reading for each parameter.
latest = df.drop_duplicates(subset=["parameter"], keep="first")

st.subheader("Latest available readings")

# Show AQI separately from pollutant concentrations.
aqi = latest[latest["parameter"] == "AQI"]
if not aqi.empty:
    item = aqi.iloc[0]
    st.metric("Air Quality Index (AQI)", f"{item['value']:g}")

pollutants = latest[latest["parameter"] != "AQI"]

if not pollutants.empty:
    columns = st.columns(min(len(pollutants), 4))

    for index, (_, row) in enumerate(pollutants.iterrows()):
        with columns[index % len(columns)]:
            st.metric(
                row["parameter"],
                f"{row['value']:g} {row['unit']}",
            )

    st.subheader("Latest pollutant readings")
    st.bar_chart(
        pollutants.set_index("parameter")["value"]
    )
    st.caption(
        "Pollutants have different units and health thresholds. "
        "The bar chart compares reported numbers only; it does not "
        "rank health risk."
    )

st.subheader("Saved readings over time")

parameter_options = sorted(df["parameter"].unique())
selected_parameter = st.selectbox(
    "Choose a parameter",
    parameter_options,
    index=parameter_options.index("PM2.5")
    if "PM2.5" in parameter_options else 0,
)

history = (
    df[df["parameter"] == selected_parameter]
    .sort_values("measured_at")
)

if not history.empty:
    st.line_chart(
        history.set_index("measured_at")["value"]
    )
    st.caption(f"Unit: {history['unit'].iloc[-1]}")

st.subheader("Raw data")
st.dataframe(df, use_container_width=True)

st.caption(
    "Readings reflect the data saved in your local database, "
    "not necessarily the current live conditions."
)

if st.button("Refresh dashboard"):
    st.cache_data.clear()
    st.rerun()
