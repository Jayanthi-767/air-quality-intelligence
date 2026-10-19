
from backend.app.database import Base, engine
from backend.app.models import AirQualityMeasurement

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
print("Table: air_quality_measurements")
