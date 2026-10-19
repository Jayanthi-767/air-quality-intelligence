
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
)

from backend.app.database import Base


class AirQualityMeasurement(Base):
    __tablename__ = "air_quality_measurements"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    station_id = Column(String(100), nullable=True)
    parameter = Column(String(30), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(100), nullable=False, default="manual")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_air_quality_city_parameter_time",
            "city",
            "parameter",
            "measured_at",
        ),
    )
