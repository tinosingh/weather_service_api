#!/bin/bash
set -e

# Function to log messages with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    local max_retries=30
    local retry_count=0
    
    local db_host=${WEATHER_POSTGRES_SERVER:-postgres}
    local db_port=${WEATHER_POSTGRES_PORT:-5432}
    local db_user=${WEATHER_POSTGRES_USER:-aog4_user}
    local db_name=${WEATHER_POSTGRES_DB:-weather_db}
    local db_password=${WEATHER_POSTGRES_PASSWORD:-aog4_dev_password}
    
    log "Waiting for PostgreSQL at ${db_host}:${db_port}..."
    
    until PGPASSWORD="${db_password}" psql -h "${db_host}" -U "${db_user}" -d "${db_name}" -p "${db_port}" -c '\q' 2>/dev/null; do
        retry_count=$((retry_count + 1))
        if [ $retry_count -ge $max_retries ]; then
            log "ERROR: PostgreSQL is not available after $max_retries retries. Exiting." >&2
            exit 1
        fi
        log "PostgreSQL is not ready yet. Retrying in 1 second... (${retry_count}/${max_retries})"
        sleep 1
    done
    log "PostgreSQL is ready!"
}

# Install development dependencies if in development
if [ "$WEATHER_ENVIRONMENT" = "development" ]; then
    log "Running in development mode"
    log "Running database migrations..."
    if ! uv run alembic upgrade head; then
        log "Error: Database migration failed"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    log "Running tests..."
    if ! uv run pytest tests/ -v --cov=app --cov-report=term-missing; then
        log "Error: Tests failed"
        exit 1
    fi
}

# Function to set up development environment
setup_development() {
    log "Setting up development environment..."
    
    # Install development dependencies
    install_dev_deps
    
    # Wait for PostgreSQL
    wait_for_postgres
    
    # Run database migrations
    run_migrations
    
    # Install the package in development mode if not already installed
    if [ ! -e "/app/.installed" ]; then
        log "Installing package in development mode..."
        if uv pip install -e .; then
            touch /app/.installed
        else
            log "Error: Failed to install package in development mode"
            exit 1
        fi
    fi
}

# Main execution
log "Starting container with environment: ${ENVIRONMENT:-production}"

case "${ENVIRONMENT:-production}" in
    development)
        setup_development
        
        # Run tests if requested
        if [ "${RUN_TESTS:-false}" = "true" ]; then
            run_tests
        fi
        ;;
    production)
        # In production, just wait for the database
        wait_for_postgres
        run_migrations
        ;;
    *)
        log "Error: Unknown environment '$ENVIRONMENT'"
        exit 1
        ;;
esac

# Execute the command passed to the container
log "Executing: $@"
exec "$@"
