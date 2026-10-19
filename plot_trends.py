
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

from backend.app.database import DATABASE_URL

# Load real WAQI PM2.5 readings from SQLite.
engine = create_engine(DATABASE_URL)

query = """
SELECT measured_at, value, unit
FROM air_quality_measurements
WHERE source = 'WAQI'
  AND parameter = 'PM2.5'
ORDER BY measured_at
"""

df = pd.read_sql_query(query, engine)

if df.empty:
    print("No WAQI PM2.5 readings found yet.")
    print("Run: python fetch_waqi.py")
else:
    df["measured_at"] = pd.to_datetime(df["measured_at"])

    plt.figure(figsize=(10, 5))
    plt.plot(
        df["measured_at"],
        df["value"],
        marker="o",
        label="PM2.5",
    )

    plt.title("Hyderabad Air Quality — PM2.5")
    plt.xlabel("Measurement time")
    plt.ylabel(f"PM2.5 ({df['unit'].iloc[0]})")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    output_file = "waqi_pm25_trend.png"
    plt.savefig(output_file, dpi=150)
    print("Chart saved to:", output_file)
    print("Number of readings:", len(df))

    plt.show()
