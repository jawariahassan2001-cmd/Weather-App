
from sqlalchemy.orm import Session

from app.models.weather import WeatherRecord


def create_weather_record(
    db: Session,
    location: dict,
    start_date,
    end_date,
    weather_data: dict,
):
    record = WeatherRecord(
        location_name=location["name"],
        region=location.get("region"),
        country=location.get("country"),
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=start_date,
        end_date=end_date,
        weather_data=weather_data,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

def get_all_weather_records(db: Session):
    return db.query(WeatherRecord).order_by(
        WeatherRecord.id.desc()
    ).all()


def get_weather_record_by_id(db: Session, record_id: int):
    return db.query(WeatherRecord).filter(
        WeatherRecord.id == record_id
    ).first()

def update_weather_record(
    db: Session,
    record: WeatherRecord,
    location: dict,
    start_date,
    end_date,
    weather_data: dict,
):
    record.location_name = location["name"]
    record.region = location.get("region")
    record.country = location.get("country")
    record.latitude = location["latitude"]
    record.longitude = location["longitude"]
    record.start_date = start_date
    record.end_date = end_date
    record.weather_data = weather_data

    db.commit()
    db.refresh(record)

    return record
def delete_weather_record(db: Session, record: WeatherRecord):
    db.delete(record)
    db.commit()