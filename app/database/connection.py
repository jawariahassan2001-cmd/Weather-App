
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Keep the database file in the main project folder.
BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "weather.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


# SQLite needs this setting when used with FastAPI.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# This creates database sessions for our API operations.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# All our database models will inherit from this class.
class Base(DeclarativeBase):
    pass
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()