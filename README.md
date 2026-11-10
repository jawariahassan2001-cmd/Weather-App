# Weather Intelligence Platform

A backend application for retrieving, storing, managing, and exporting weather information for different locations.

**Developer:** Jawaria Hassan  
**Project:** Weather Intelligence Platform  
**Version:** 1.0.0

## About the Project

The idea behind this project is simple: provide a single API where users can search for a location, retrieve its weather information, save weather records for a selected date range, manage those records, and export the stored data in different formats.

The application uses external weather and geocoding services to retrieve information and stores the results in a local SQLite database. FastAPI provides the API endpoints, while Swagger UI makes it easy to explore and test the application without needing a separate frontend.

## Features

- Search locations using city names, towns, landmarks, postal codes, or GPS coordinates.
- Retrieve current weather information.
- Retrieve historical weather data for past dates.
- Retrieve forecast data for current and upcoming dates.
- Save weather information for a selected date range.
- View all saved weather records or retrieve an individual record.
- Update and delete existing records.
- Export saved database records as JSON, CSV, XML, PDF, and Markdown.
- Validate locations, date ranges, and record IDs.
- Handle errors from external services and invalid requests.
- Provide API health-check and documentation endpoints.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API development |
| Uvicorn | ASGI server |
| SQLAlchemy | Database operations and ORM |
| SQLite | Local database |
| Pydantic | Request validation and response schemas |
| HTTPX | Communication with external APIs |
| ReportLab | PDF generation |
| Open-Meteo | Weather data and city geocoding |
| OpenStreetMap Nominatim | Postal-code and landmark geocoding |
| Pytest | Automated testing |
| Ruff | Code linting and quality checks |

## How It Works

The application follows a service-based structure:

1. A user sends a request through an API endpoint.
2. The location service identifies the requested location using the appropriate geocoding provider.
3. The weather service retrieves the required weather information from Open-Meteo.
4. For saved records, the repository layer handles database operations through SQLAlchemy.
5. The export endpoints retrieve existing database records and generate the requested file format.

Weather information is retrieved from external APIs, but exports are generated from records already stored in the database. Exporting does not make a fresh weather API request.

## Project Structure

```text
Weather-App/
│
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── weather.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── weather.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── weather.py
│   │   ├── export.py
│   │   └── locations.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── geocoding.py
│   │   ├── nominatim_service.py
│   │   ├── location_service.py
│   │   ├── weather_service.py
│   │   └── weather_repository.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_date_range.py
│   ├── test_location_weather.py
│   ├── test_nominatim.py
│   ├── test_schemas.py
│   └── test_weather_service.py
│
├── .gitignore
├── pytest.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

The `weather.db` file is created locally when the application initializes its database. It is intentionally excluded from Git.

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.13 or a compatible Python version.
- pip
- Git
- An active internet connection for external weather and geocoding requests.

### 1. Clone the Repository

```powershell
git clone https://github.com/jawariahassan2001-cmd/Weather-App.git
cd Weather-App
```

If you already have the project on your computer, simply open its root folder in VS Code.

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 5. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 6. Start the Application

```powershell
python -m uvicorn app.main:app --reload
```

Once the server starts, the API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically generates interactive API documentation.

Open the following URL in your browser:

```text
http://127.0.0.1:8000/docs
```

You can use Swagger UI to send requests, provide JSON request bodies, inspect responses, and test the available endpoints.

## API Endpoints

### Weather

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/weather/current` | Retrieve current weather |
| POST | `/api/weather/` | Retrieve and save weather for a date range |
| GET | `/api/weather/` | Retrieve all saved records |
| GET | `/api/weather/{record_id}` | Retrieve one saved record |
| PUT | `/api/weather/{record_id}` | Update an existing record |
| DELETE | `/api/weather/{record_id}` | Delete a saved record |

### Location Search

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/locations/search` | Search for a location |

Example:

```text
/api/locations/search?query=Islamabad&country=Pakistan
```

### Data Export

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/export/json` | Export records as JSON |
| GET | `/api/export/csv` | Export records as CSV |
| GET | `/api/export/xml` | Export records as XML |
| GET | `/api/export/pdf` | Export records as PDF |
| GET | `/api/export/markdown` | Export records as Markdown |

### General

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Application health check |

## Example Requests

### Get Current Weather

```http
GET /api/weather/current?location=Islamabad&country=Pakistan
```

The endpoint returns the resolved location and its current weather information.

You can also provide a postal code:

```http
GET /api/weather/current?location=44000&country=Pakistan
```

Or GPS coordinates:

```http
GET /api/weather/current?location=33.729985,73.0373
```

### Save Weather Information

Send a POST request to:

```http
POST /api/weather/
```

Request body:

```json
{
  "location": "Islamabad",
  "country": "Pakistan",
  "start_date": "2026-11-09",
  "end_date": "2026-11-10"
}
```

The application resolves the location, retrieves the weather data for the requested period, and saves the result in the SQLite database.

A successful request returns HTTP `201 Created` with the saved record.

## Date Validation

The application checks date ranges before requesting weather information.

- The end date cannot be earlier than the start date.
- A date range cannot cross between historical dates and current/future dates.
- Historical ranges use the Open-Meteo Archive API.
- Current and future ranges use the Open-Meteo Forecast API.
- Forecast requests are limited to the supported 16-day period, including today.

Invalid date ranges return HTTP `422 Unprocessable Content`.

## Location Handling

Different location inputs are handled through a shared location-resolution service.

- City and town names are searched through Open-Meteo geocoding.
- Postal codes are searched through OpenStreetMap Nominatim.
- Landmarks are supported through Nominatim when the primary geocoder cannot resolve them.
- GPS coordinates are validated and used directly.

When a country is provided, the application uses it to narrow down location results where possible.

## Automated Testing

The project uses Pytest to run automated tests. External API calls are mocked in the tests, allowing the test suite to run without depending on live weather or geocoding services.

Run all tests:

```powershell
python -m pytest -v
```

## Code Quality Checks

The project uses Ruff to check code quality and formatting-related lint issues.

If Ruff is not already installed:

```powershell
python -m pip install ruff
```

Run the lint checks:

```powershell
python -m ruff check app tests
```

Compile the application files to check for Python syntax errors:

```powershell
python -m compileall app
```

## Error Handling

The API uses appropriate HTTP status codes to communicate errors.

| Status Code | Meaning |
|---|---|
| 200 | Request completed successfully |
| 201 | Weather record created |
| 404 | Location or record not found |
| 422 | Invalid input or date range |
| 502 | External service error |
| 504 | External service timeout |
| 500 | Internal server error |

## External Services and Attribution

This project uses the following external services:

**Open-Meteo**

Provides weather information, forecasts, historical weather data, and city geocoding.

Website: https://open-meteo.com/

**OpenStreetMap Nominatim**

Provides location search for postal codes, landmarks, and other geographic places.

Website: https://nominatim.org/

Location data is provided by OpenStreetMap contributors.

© OpenStreetMap contributors — https://www.openstreetmap.org/copyright

Nominatim's public service has a usage policy, including a maximum request rate of one request per second. This application includes request spacing for its Nominatim calls and is intended for low-volume use.

## Current Limitations

A few things are worth keeping in mind about the current implementation:

- Weather retrieval depends on the availability of external APIs.
- Forecast availability is limited by the provider's supported forecast range.
- Nominatim's public service is not intended for heavy production traffic.
- SQLite is suitable for this assessment and small-scale use, but a larger deployment may require a server-based database.
- The application currently provides a backend API and Swagger documentation rather than a separate frontend.
- Authentication and user-specific access control are not implemented.

## Author

**Jawaria Hassan**

Developed as a Weather Intelligence Platform backend project.

---

*Built with Python, FastAPI, SQLAlchemy, and external weather and geocoding APIs.*
