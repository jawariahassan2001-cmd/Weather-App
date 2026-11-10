
import csv
import io
import json
import xml.etree.ElementTree as ET
from html import escape

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response, StreamingResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
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
            json.dumps(record.weather_data, ensure_ascii=False),
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


# PDF EXPORT
@router.get("/pdf")
def export_pdf(db: Session = Depends(get_db)):
    records = get_all_weather_records(db)

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "RecordHeading",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = styles["BodyText"]

    story = []

    story.append(
        Paragraph("Weather Intelligence Report", title_style)
    )

    story.append(
        Paragraph(
            f"Total Records: {len(records)}",
            body_style,
        )
    )

    story.append(Spacer(1, 15))

    if not records:
        story.append(
            Paragraph("No weather records found.", body_style)
        )

    else:
        for index, record in enumerate(records):

            story.append(
                Paragraph(
                    f"Record ID: {record.id}",
                    heading_style,
                )
            )

            # Record information.
            metadata = [
                ["Field", "Value"],
                ["Location", escape(str(record.location_name or "N/A"))],
                ["Region", escape(str(record.region or "N/A"))],
                ["Country", escape(str(record.country or "N/A"))],
                ["Latitude", str(record.latitude)],
                ["Longitude", str(record.longitude)],
                [
                    "Date Range",
                    f"{record.start_date} to {record.end_date}",
                ],
            ]

            metadata_table = Table(
                metadata,
                colWidths=[40 * mm, 120 * mm],
                repeatRows=1,
            )

            metadata_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263B5A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ])
            )

            story.append(metadata_table)
            story.append(Spacer(1, 12))

            # Actual weather measurements.
            story.append(
                Paragraph("Weather Measurements", heading_style)
            )

            weather_data = record.weather_data or {}

            daily_data = weather_data.get("daily", {})
            daily_units = weather_data.get("daily_units", {})

            if isinstance(daily_data, dict) and daily_data:

                dates = daily_data.get("time", [])

                weather_rows = [
                    ["Date", "Measurement", "Value", "Unit"]
                ]

                for metric, values in daily_data.items():

                    if metric == "time":
                        continue

                    unit = daily_units.get(metric, "N/A")

                    if isinstance(values, list):
                        for position, value in enumerate(values):

                            measurement_date = (
                                dates[position]
                                if position < len(dates)
                                else "N/A"
                            )

                            weather_rows.append([
                                str(measurement_date),
                                escape(metric.replace("_", " ").title()),
                                str(value),
                                escape(str(unit)),
                            ])

                    else:
                        weather_rows.append([
                            "N/A",
                            escape(metric.replace("_", " ").title()),
                            str(values),
                            escape(str(unit)),
                        ])

                weather_table = Table(
                    weather_rows,
                    colWidths=[
                        30 * mm,
                        55 * mm,
                        35 * mm,
                        40 * mm,
                    ],
                    repeatRows=1,
                )

                weather_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263B5A")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                            colors.white,
                            colors.HexColor("#F0F3F7"),
                        ]),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ])
                )

                story.append(weather_table)

            else:
                # Fallback for records without daily weather data.
                weather_json = json.dumps(
                    weather_data,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )

                formatted_json = escape(weather_json).replace(
                    "\n",
                    "<br/>",
                )

                story.append(
                    Paragraph(
                        f"<font name='Courier'>{formatted_json}</font>",
                        body_style,
                    )
                )

            story.append(Spacer(1, 20))

            if index < len(records) - 1:
                story.append(PageBreak())

    document.build(story)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="weather_records.pdf"'
        },
    )


# MARKDOWN EXPORT
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
