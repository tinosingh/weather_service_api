# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    WEATHER_HOST=0.0.0.0 \
    WEATHER_PORT=8101

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY pyproject.toml README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Create necessary directories and set permissions
RUN mkdir -p /app/logs && \
    useradd -m appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Command to run the application (using shell form to allow env var expansion)
CMD uvicorn app.main:app --host ${WEATHER_HOST:-0.0.0.0} --port ${WEATHER_PORT:-8101} --reload --workers ${WEATHER_WORKERS:-4}
