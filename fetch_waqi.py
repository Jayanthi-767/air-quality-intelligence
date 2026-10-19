
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models import AirQualityMeasurement

load_dotenv()

TOKEN = os.getenv("WAQI_API_TOKEN")
API_URL = "https://api.waqi.info/feed/hyderabad/"

# Map WAQI pollutant names to our database parameter names.
POLLUTANTS = {
    "pm25": ("PM2.5", "µg/m³"),
    "pm10": ("PM10", "µg/m³"),
    "no2": ("NO2", "µg/m³"),
    "so2": ("SO2", "µg/m³"),
    "o3": ("O3", "µg/m³"),
    "co": ("CO", "mg/m³"),
}


def fetch_and_save():
    if not TOKEN:
        raise RuntimeError(
            "WAQI_API_TOKEN is missing. Check your .env file."
        )

    response = requests.get(
        API_URL,
        params={"token": TOKEN},
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()

    if result.get("status") != "ok":
        raise RuntimeError(
            f"WAQI API returned: {result.get('status')}"
        )

    data = result["data"]
    station = data.get("city", {}).get("name", "Hyderabad")
    station_id = str(data.get("idx", "")) or None

    # Use the timestamp supplied by WAQI for this station's data.
    time_info = data.get("time", {})
    measured_at_text = time_info.get("iso") or time_info.get("s")

    if not measured_at_text:
        raise RuntimeError("WAQI response has no measurement timestamp.")

    measured_at = datetime.fromisoformat(
        measured_at_text.replace("Z", "+00:00")
    )

    # Store timezone-aware timestamps consistently in UTC.
    if measured_at.tzinfo is None:
        measured_at = measured_at.replace(tzinfo=timezone.utc)
    measured_at = measured_at.astimezone(timezone.utc).replace(tzinfo=None)

    iaqi = data.get("iaqi", {})
    rows_to_save = []

    # Save only pollutant readings actually supplied by WAQI.
    for key, (parameter, unit) in POLLUTANTS.items():
        item = iaqi.get(key)

        if not isinstance(item, dict) or "v" not in item:
            continue

        try:
            value = float(item["v"])
        except (TypeError, ValueError):
            continue

        if value < 0:
            continue

        rows_to_save.append(
            AirQualityMeasurement(
                city="Hyderabad",
                country="India",
                station_id=station_id,
                parameter=parameter,
                value=value,
                unit=unit,
                measured_at=measured_at,
                source="WAQI",
            )
        )

    # Save AQI separately because it is an index, not a concentration.
    aqi = data.get("aqi")
    if isinstance(aqi, (int, float)) and not isinstance(aqi, bool) and aqi >= 0:
        rows_to_save.append(
            AirQualityMeasurement(
                city="Hyderabad",
                country="India",
                station_id=station_id,
                parameter="AQI",
                value=float(aqi),
                unit="AQI",
                measured_at=measured_at,
                source="WAQI",
            )
        )

    if not rows_to_save:
        print("WAQI returned no usable readings to save.")
        return

    db: Session = SessionLocal()
    try:
        # Avoid saving the same station/parameter/timestamp twice.
        saved = 0
        skipped = 0

        for row in rows_to_save:
            existing = (
                db.query(AirQualityMeasurement)
                .filter(
                    AirQualityMeasurement.station_id == row.station_id,
                    AirQualityMeasurement.parameter == row.parameter,
                    AirQualityMeasurement.measured_at == row.measured_at,
                    AirQualityMeasurement.source == row.source,
                )
                .first()
            )

            if existing:
                skipped += 1
            else:
                db.add(row)
                saved += 1

        db.commit()

        print("WAQI data fetch completed.")
        print("Station:", station)
        print("New readings saved:", saved)
        print("Existing readings skipped:", skipped)
        print("Token was not displayed.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        fetch_and_save()
    except requests.RequestException as error:
        print("Network/API request failed:", type(error).__name__)
    except Exception as error:
        print("Could not save readings:", str(error))
