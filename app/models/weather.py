
from datetime import UTC, date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    location_name: Mapped[str] = mapped_column(String(150))
    region: Mapped[str | None] = mapped_column(String(150), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)

    weather_data: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
