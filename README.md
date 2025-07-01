# Weather Service API

A FastAPI-based microservice for weather data aggregation and prediction, integrating with the Finnish Meteorological Institute (FMI) Open Data API.

## Features

- Fetch current weather data for locations in Finland
- Historical weather data retrieval
- Weather forecast data
- Built with FastAPI and PostgreSQL
- Containerized with Docker
- Asynchronous API endpoints
- OpenAPI documentation

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- PostgreSQL 13+
- FMI Open Data API key (optional for development)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/tinosingh/weather_service_api.git
   cd weather_service_api
   ```

2. Copy the example environment file and update with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

4. Access the API documentation:
   - Swagger UI: http://localhost:8101/docs
   - ReDoc: http://localhost:8101/redoc

## Environment Variables

Create a `.env` file with the following variables:

```
# Application
APP_NAME="Weather Service"
APP_ENV=development
DEBUG=True

# Database
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=weather
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:5432/${POSTGRES_DB}

# FMI API
FMI_API_KEY=your_api_key_here
FMI_API_BASE_URL=https://opendata.fmi.fi/wfs

# Server
HOST=0.0.0.0
PORT=8101
WORKERS=1
```

## API Endpoints

- `GET /api/v1/health` - Health check endpoint
- `GET /api/v1/weather/current/{location_id}` - Get current weather for a location
- `GET /api/v1/weather/forecast/{location_id}` - Get weather forecast for a location
- `GET /api/v1/weather/history/{location_id}` - Get historical weather data

## Development

### Setup Development Environment

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Run the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8101
   ```

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
# Linting
ruff check .

# Formatting
black .

# Type checking
mypy .
```

## FMI API Integration

This service integrates with the FMI Open Data API. To use this feature:

1. Get an API key from [FMI Open Data](https://ilmatieteenlaitos.fi/avoin-data)
2. Add it to your `.env` file as `FMI_API_KEY=your_api_key_here`

## Deployment

### Docker

Build and run using Docker Compose:

```bash
docker-compose up --build
```

### Kubernetes

Example Kubernetes deployment files are provided in the `k8s/` directory.

## License

MIT
