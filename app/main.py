
from fastapi import FastAPI

from app.database.connection import Base, engine
from app.models.weather import WeatherRecord  # noqa: F401
from app.routes.export import router as export_router
from app.routes.locations import router as locations_router
from app.routes.weather import router as weather_router

app = FastAPI(
    title="Weather Intelligence Platform",
    description="A backend API for weather data retrieval and management.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(weather_router)
app.include_router(locations_router)
app.include_router(export_router)


@app.get("/")
def root():
    return {
        "message": "Weather Intelligence Platform API is running."
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
