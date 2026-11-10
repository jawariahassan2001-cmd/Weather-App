
import csv
import io
import json
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.weather import WeatherResponse
from app.services.weather_repository import get_all_weather_records


router = APIRouter(
    prefix="/api/export",
    tags=["Export"],
)


# JSON EXPORT
@router.get("/json")
def export_json(db: Session = Depends(get_db)):
    records = get_all_weather_records(db)

    export_data = [
        WeatherResponse.model_validate(record).model_dump(mode="json")
        for record in records
    ]

    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": 'attachment; filename="weather_records.json"'
        },
    )


# CSV EXPORT
@router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    records = get_all_weather_records(db)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Location",
        "Region",
        "Country",
        "Latitude",
        "Longitude",
        "Start Date",
        "End Date",
        "Weather Data",
        "Created At",
        "Updated At",
    ])

    for record in records:
        writer.writerow([
            record.id,
            record.location_name,
            record.region,
            record.country,
            record.latitude,
            record.longitude,
            record.start_date,
            record.end_date,
            record.weather_data,
            record.created_at,
            record.updated_at,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="weather_records.csv"'
        },
    )


# XML EXPORT
@router.get("/xml")
def export_xml(db: Session = Depends(get_db)):
    records = get_all_weather_records(db)

    root = ET.Element("weather_records")

    for record in records:
        record_element = ET.SubElement(root, "record")

        ET.SubElement(record_element, "id").text = str(record.id)
        ET.SubElement(record_element, "location").text = record.location_name
        ET.SubElement(record_element, "region").text = record.region or ""
        ET.SubElement(record_element, "country").text = record.country or ""
        ET.SubElement(record_element, "latitude").text = str(record.latitude)
        ET.SubElement(record_element, "longitude").text = str(record.longitude)
        ET.SubElement(record_element, "start_date").text = record.start_date.isoformat()
        ET.SubElement(record_element, "end_date").text = record.end_date.isoformat()

        ET.SubElement(record_element, "weather_data").text = json.dumps(
            record.weather_data
        )

        ET.SubElement(record_element, "created_at").text = record.created_at.isoformat()
        ET.SubElement(record_element, "updated_at").text = record.updated_at.isoformat()

    xml_content = ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True,
    )

    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": 'attachment; filename="weather_records.xml"'
        },
    )
@router.get("/pdf")
def export_pdf(db: Session = Depends(get_db)):
    records = get_all_weather_records(db)

    # Create an in-memory PDF file.
    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Add the report title.
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Weather Intelligence Report")

    y = height - 90

    pdf.setFont("Helvetica", 10)

    if not records:
        pdf.drawString(50, y, "No weather records found.")
    else:
        for record in records:
            # Start a new page if there isn't enough space.
            if y < 100:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = height - 50

            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(50, y, f"Record ID: {record.id}")
            y -= 20

            pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, f"Location: {record.location_name}")
            y -= 15

            pdf.drawString(50, y, f"Country: {record.country or 'N/A'}")
            y -= 15

            pdf.drawString(
                50, y,
                f"Date Range: {record.start_date} to {record.end_date}"
            )
            y -= 15

            pdf.drawString(50, y, f"Latitude: {record.latitude}")
            y -= 15

            pdf.drawString(50, y, f"Longitude: {record.longitude}")
            y -= 25

    # Finalize the PDF.
    pdf.save()

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="weather_records.pdf"'
        },
    )
@router.get("/markdown")
def export_markdown(db: Session = Depends(get_db)):
    records = get_all_weather_records(db)

    output = io.StringIO()

    output.write("# Weather Intelligence Report\n\n")

    if not records:
        output.write("No weather records found.\n")
    else:
        for record in records:
            output.write(f"## Record ID: {record.id}\n\n")
            output.write(f"- **Location:** {record.location_name}\n")
            output.write(f"- **Region:** {record.region or 'N/A'}\n")
            output.write(f"- **Country:** {record.country or 'N/A'}\n")
            output.write(f"- **Latitude:** {record.latitude}\n")
            output.write(f"- **Longitude:** {record.longitude}\n")
            output.write(f"- **Start Date:** {record.start_date}\n")
            output.write(f"- **End Date:** {record.end_date}\n")
            output.write(f"- **Created At:** {record.created_at}\n")
            output.write(f"- **Updated At:** {record.updated_at}\n\n")

            output.write("### Weather Data\n\n")
            output.write("```json\n")
            output.write(json.dumps(record.weather_data, indent=2))
            output.write("\n```\n\n")

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/markdown",
        headers={
            "Content-Disposition": 'attachment; filename="weather_records.md"'
        },
    )