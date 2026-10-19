
import pandas as pd
from sqlalchemy import create_engine

from backend.app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

query = """
SELECT
    city,
    parameter,
    value,
    unit,
    measured_at
FROM air_quality_measurements
WHERE source = 'WAQI'
ORDER BY measured_at
"""

df = pd.read_sql_query(query, engine)

if df.empty:
    print("No WAQI data found. Run python fetch_waqi.py first.")
else:
    print("\n=== WAQI DATASET OVERVIEW ===")
    print("Total readings:", len(df))
    print("Cities:", ", ".join(df["city"].dropna().unique()))

    print("\n=== READINGS BY POLLUTANT ===")
    print(df.groupby("parameter")["value"].agg(
        ["count", "mean", "min", "max"]
    ).round(2))

    print("\n=== LATEST READINGS ===")
    latest = (
        df.sort_values("measured_at")
        .groupby("parameter")
        .tail(1)
        .sort_values("parameter")
    )

    print(latest[[
        "parameter", "value", "unit", "measured_at"
    ]].to_string(index=False))

    print("\nNote: AQI is an index; pollutant concentrations use their own units.")
