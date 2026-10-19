
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Find the project root folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Create a local SQLite database file
DATABASE_PATH = PROJECT_ROOT / "air_quality.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Connect to SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for database models
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
