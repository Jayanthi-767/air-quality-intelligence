
from datetime import datetime, timezone

from backend.app.database import SessionLocal
from backend.app.models import AirQualityMeasurement

# Open a database session
db = SessionLocal()

try:
    measurement = AirQualityMeasurement(
        city="Hyderabad",
        country="India",
        station_id=None,
        parameter="PM2.5",
        value=32.5,
        unit="µg/m³",
        measured_at=datetime.now(timezone.utc),
        source="manual-demo",
    )

    # Save the measurement
    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    print("Measurement saved successfully!")
    print("ID:", measurement.id)
    print("City:", measurement.city)
    print("Pollutant:", measurement.parameter)
    print("Value:", measurement.value, measurement.unit)
    print("Source:", measurement.source)

finally:
    db.close()
