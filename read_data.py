
from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import AirQualityMeasurement

db = SessionLocal()

try:
    statement = select(AirQualityMeasurement).order_by(
        AirQualityMeasurement.id
    )

    measurements = db.scalars(statement).all()

    print(f"Total measurements: {len(measurements)}")
    print("-" * 45)

    for item in measurements:
        print(f"ID: {item.id}")
        print(f"City: {item.city}, {item.country}")
        print(f"Pollutant: {item.parameter}")
        print(f"Value: {item.value} {item.unit}")
        print(f"Measured at: {item.measured_at}")
        print(f"Source: {item.source}")
        print("-" * 45)

finally:
    db.close()
