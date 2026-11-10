
from fastapi import FastAPI

from app.database.connection import Base, engine
from app.models.weather import WeatherRecord
from app.routes.weather import router as weather_router
from app.routes.export import router as export_router
from app.routes.locations import router as locations_router


app = FastAPI(
    title="Weather Intelligence Platform",
    description="A backend application for retrieving, storing, managing and exporting weather information.",
    version="1.0.0",
)

# Create database tables
Base.metadata.create_all(bind=engine)


# Register weather routes
app.include_router(weather_router)
app.include_router(export_router)
app.include_router(locations_router)


@app.get("/")
def home():
    return {
        "message": "Weather Intelligence Platform API is running."
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
