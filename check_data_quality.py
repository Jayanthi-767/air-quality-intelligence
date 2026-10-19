
import pandas as pd
from sqlalchemy import create_engine

from backend.app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

query = """
SELECT city, parameter, value, unit, measured_at, station_id, source
FROM air_quality_measurements
WHERE source = 'WAQI'
"""

df = pd.read_sql_query(query, engine)

if df.empty:
    print("No WAQI readings found. Run python fetch_waqi.py first.")
    raise SystemExit(0)

df["measured_at"] = pd.to_datetime(df["measured_at"], errors="coerce")

print("\n=== DATA QUALITY REPORT ===")
print("Total rows:", len(df))
print("Duplicate rows:", int(df.duplicated().sum()))
print("Missing values by column:")
print(df.isna().sum().to_string())

print("\nInvalid numeric values:", int((~df["value"].apply(
    lambda x: pd.notna(x) and x >= 0
)).sum()))

print("\nRows per parameter:")
print(df.groupby("parameter").size().to_string())

print("\nDate range:")
print("First:", df["measured_at"].min())
print("Last: ", df["measured_at"].max())

# Export the real readings for analysis in Excel or other tools.
output_file = "waqi_air_quality.csv"
df.to_csv(output_file, index=False)

print("\nCSV exported to:", output_file)
print("Review the report before using the data for conclusions.")
