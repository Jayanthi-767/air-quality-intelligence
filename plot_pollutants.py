
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

from backend.app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

query = """
SELECT parameter, value, unit, measured_at
FROM air_quality_measurements
WHERE source = 'WAQI'
  AND parameter != 'AQI'
ORDER BY measured_at
"""

df = pd.read_sql_query(query, engine)

if df.empty:
    print("No WAQI pollutant readings found.")
    raise SystemExit(0)

df["measured_at"] = pd.to_datetime(df["measured_at"])

# Use the most recent observation for each pollutant.
latest = (
    df.sort_values("measured_at")
    .groupby("parameter")
    .tail(1)
    .sort_values("value", ascending=False)
)

print("\nLatest available pollutant readings:")
print(latest[["parameter", "value", "unit", "measured_at"]].to_string(index=False))

# Display units in each label because different pollutants may use different units.
labels = [
    f"{row.parameter} ({row.unit})"
    for row in latest.itertuples()
]

plt.figure(figsize=(9, 5))
plt.bar(labels, latest["value"])
plt.title("Latest Available Hyderabad Pollutant Readings")
plt.xlabel("Pollutant and reported unit")
plt.ylabel("Reported concentration")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()

plt.savefig("waqi_pollutant_comparison.png", dpi=150)
plt.show()

print("\nChart saved to waqi_pollutant_comparison.png")
