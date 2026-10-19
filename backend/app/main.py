
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select, text, func
from sqlalchemy.orm import Session

from backend.app.database import Base, engine, get_db
from backend.app.models import AirQualityMeasurement
from backend.app.schemas import MeasurementCreate, MeasurementResponse

from backend.app.database import SessionLocal
from backend.app.models import AirQualityMeasurement


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Air Quality Intelligence API",
    description="API for storing and exploring air-quality measurements.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "message": "Air Quality Intelligence API is running!",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}


@app.post(
    "/api/measurements",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement(
    measurement: MeasurementCreate,
    db: Session = Depends(get_db),
):
    record = AirQualityMeasurement(**measurement.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/api/measurements", response_model=list[MeasurementResponse])
def list_measurements(
    city: str | None = None,
    parameter: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    statement = select(AirQualityMeasurement)

    if city:
        statement = statement.where(
            AirQualityMeasurement.city.ilike(city)
        )

    if parameter:
        statement = statement.where(
            AirQualityMeasurement.parameter.ilike(parameter)
        )

    statement = (
        statement
        .order_by(AirQualityMeasurement.measured_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(statement).all()


@app.get(
    "/api/measurements/{measurement_id}",
    response_model=MeasurementResponse,
)
def get_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(AirQualityMeasurement, measurement_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Measurement not found",
        )

    return record


@app.get("/api/summary")

@app.get("/api/summary")
def get_summary(
    city: str | None = None,
    parameter: str | None = None,
    db: Session = Depends(get_db),
):
    filters = []

    if city:
        filters.append(
            AirQualityMeasurement.city.ilike(f"%{city}%")
        )

    if parameter:
        filters.append(
            AirQualityMeasurement.parameter.ilike(f"%{parameter}%")
        )

    total = db.scalar(
        select(func.count(AirQualityMeasurement.id)).where(*filters)
    ) or 0

    statement = (
        select(
            AirQualityMeasurement.city,
            AirQualityMeasurement.parameter,
            AirQualityMeasurement.unit,
            func.count(AirQualityMeasurement.id).label("count"),
            func.avg(AirQualityMeasurement.value).label("average"),
            func.min(AirQualityMeasurement.value).label("minimum"),
            func.max(AirQualityMeasurement.value).label("maximum"),
        )
        .where(*filters)
        .group_by(
            AirQualityMeasurement.city,
            AirQualityMeasurement.parameter,
            AirQualityMeasurement.unit,
        )
        .order_by(
            AirQualityMeasurement.city,
            AirQualityMeasurement.parameter,
        )
    )

    rows = db.execute(statement).all()

    summaries = []

    for row in rows:
        summaries.append({
            "city": row.city,
            "parameter": row.parameter,
            "unit": row.unit,
            "measurement_count": row.count,
            "average_value": round(float(row.average), 2),
            "minimum_value": float(row.minimum),
            "maximum_value": float(row.maximum),
        })

    return {
        "total_measurements": total,
        "filters": {
            "city": city,
            "parameter": parameter,
        },
        "summaries": summaries,
    }

@app.get("/api/trends")
def get_trends(
    city: str = "Hyderabad",
    parameter: str = "PM2.5",
    db: Session = Depends(get_db),
):
    statement = (
        select(
            AirQualityMeasurement.measured_at,
            AirQualityMeasurement.value,
            AirQualityMeasurement.unit,
        )
        .where(
            AirQualityMeasurement.city.ilike(city),
            AirQualityMeasurement.parameter.ilike(parameter),
        )
        .order_by(AirQualityMeasurement.measured_at.asc())
    )

    rows = db.execute(statement).all()

    return {
        "city": city,
        "parameter": parameter,
        "total_records": len(rows),
        "data": [
            {
                "measured_at": row.measured_at.isoformat(),
                "value": row.value,
                "unit": row.unit,
            }
            for row in rows
        ],
    }



@app.get("/api/latest")
def get_latest_readings(city: str = "Hyderabad"):
    db = SessionLocal()
    try:
        # Get all saved WAQI readings for the requested city.
        rows = (
            db.query(AirQualityMeasurement)
            .filter(
                AirQualityMeasurement.city.ilike(city),
                AirQualityMeasurement.source == "WAQI",
            )
            .order_by(AirQualityMeasurement.measured_at.desc())
            .all()
        )

        # Keep only the newest reading for each parameter.
        latest = {}
        for row in rows:
            if row.parameter not in latest:
                latest[row.parameter] = {
                    "parameter": row.parameter,
                    "value": row.value,
                    "unit": row.unit,
                    "measured_at": row.measured_at.isoformat(),
                    "station_id": row.station_id,
                    "source": row.source,
                }

        return {
            "city": city,
            "count": len(latest),
            "readings": list(latest.values()),
        }
    finally:
        db.close()
