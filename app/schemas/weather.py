from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator


class WeatherCreate(BaseModel):
    country: str | None = None
    location: str = Field(min_length=2, max_length=150)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date.")
        return self


class WeatherUpdate(BaseModel):
    country: str | None = None
    location: str = Field(min_length=2, max_length=150)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date.")
        return self


class WeatherResponse(BaseModel):
    id: int
    location_name: str
    region: str | None
    country: str | None
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    weather_data: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}