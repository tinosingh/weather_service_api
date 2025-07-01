-- Database initialization script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schema
CREATE SCHEMA IF NOT EXISTS weather;

-- Set search path
SET search_path TO weather, public;

-- Create tables
CREATE TABLE IF NOT EXISTS weather.locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    elevation DECIMAL(10, 2),
    timezone VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_location_coords UNIQUE (latitude, longitude)
);

-- Create index for faster location lookups
CREATE INDEX IF NOT EXISTS idx_locations_coords ON weather.locations (latitude, longitude);

-- Create weather data table
CREATE TABLE IF NOT EXISTS weather.weather_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id UUID NOT NULL REFERENCES weather.locations(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature DECIMAL(5, 2),
    temperature_unit VARCHAR(10) DEFAULT 'celsius',
    humidity DECIMAL(5, 2),
    pressure DECIMAL(8, 2),
    wind_speed DECIMAL(6, 2),
    wind_direction INT,
    wind_gust DECIMAL(6, 2),
    precipitation_amount DECIMAL(8, 2),
    precipitation_type VARCHAR(50),
    cloud_cover INT,
    visibility DECIMAL(8, 2),
    weather_code VARCHAR(50),
    weather_description TEXT,
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_weather_data UNIQUE (location_id, timestamp, source)
);

-- Create index for faster time-based queries
CREATE INDEX IF NOT EXISTS idx_weather_data_timestamp ON weather.weather_data (timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_data_location ON weather.weather_data (location_id);

-- Create weather forecasts table
CREATE TABLE IF NOT EXISTS weather.weather_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id UUID NOT NULL REFERENCES weather.locations(id) ON DELETE CASCADE,
    forecast_time TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_to TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature_avg DECIMAL(5, 2),
    temperature_min DECIMAL(5, 2),
    temperature_max DECIMAL(5, 2),
    temperature_unit VARCHAR(10) DEFAULT 'celsius',
    precipitation_probability DECIMAL(5, 2),
    precipitation_amount DECIMAL(8, 2),
    weather_code VARCHAR(50),
    weather_description TEXT,
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_forecast UNIQUE (location_id, forecast_time, valid_from, valid_to, source)
);

-- Create index for faster forecast queries
CREATE INDEX IF NOT EXISTS idx_forecasts_valid_from ON weather.weather_forecasts (valid_from);
CREATE INDEX IF NOT EXISTS idx_forecasts_valid_to ON weather.weather_forecasts (valid_to);
CREATE INDEX IF NOT EXISTS idx_forecasts_location ON weather.weather_forecasts (location_id);

-- Create function for updating timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updating timestamps
CREATE TRIGGER update_locations_modtime
BEFORE UPDATE ON weather.locations
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_weather_data_modtime
BEFORE UPDATE ON weather.weather_data
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_weather_forecasts_modtime
BEFORE UPDATE ON weather.weather_forecasts
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Create function for partitioning weather data by time
CREATE OR REPLACE FUNCTION create_weather_data_partition()
RETURNS TRIGGER AS $$
DECLARE
    partition_name TEXT;
    partition_start TIMESTAMP;
    partition_end TIMESTAMP;
    partition_interval INTERVAL := INTERVAL '1 month';
BEGIN
    -- Calculate partition bounds
    partition_start := DATE_TRUNC('month', NEW.timestamp);
    partition_end := partition_start + partition_interval;
    partition_name := 'weather_data_' || TO_CHAR(partition_start, 'YYYY_MM');
    
    -- Create the partition if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'weather' 
        AND tablename = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE weather.%I (LIKE weather.weather_data INCLUDING INDEXES) '
            'INHERITS (weather.weather_data)',
            partition_name
        );
        
        -- Add check constraint for the partition
        EXECUTE format(
            'ALTER TABLE weather.%I '
            'ADD CONSTRAINT %I CHECK (timestamp >= %L AND timestamp < %L)',
            partition_name,
            partition_name || '_timestamp_check',
            partition_start,
            partition_end
        );
        
        -- Create indexes on the partition
        EXECUTE format(
            'CREATE INDEX %I ON weather.%I (location_id, timestamp)',
            partition_name || '_idx',
            partition_name
        );
    END IF;
    
    -- Insert into the appropriate partition
    EXECUTE format(
        'INSERT INTO weather.%I VALUES ($1.*)',
        partition_name
    ) USING NEW;
    
    RETURN NULL; -- Skip the insert into the parent table
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'Error creating partition: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for partitioning
CREATE TRIGGER weather_data_partition_trigger
BEFORE INSERT ON weather.weather_data
FOR EACH ROW EXECUTE FUNCTION create_weather_data_partition();

-- Create a default location (Helsinki)
INSERT INTO weather.locations (name, latitude, longitude, elevation, timezone)
VALUES (
    'Helsinki',
    60.1699, 
    24.9384,
    17.0,
    'Europe/Helsinki'
)
ON CONFLICT (latitude, longitude) DO NOTHING;

-- Create a read-only user for the application
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'weather_ro') THEN
        CREATE ROLE weather_ro WITH LOGIN PASSWORD 'readonly_password';
    END IF;
    
    -- Grant connect to database
    GRANT CONNECT ON DATABASE weather_db TO weather_ro;
    
    -- Grant usage on schema
    GRANT USAGE ON SCHEMA weather TO weather_ro;
    
    -- Grant select on all tables
    GRANT SELECT ON ALL TABLES IN SCHEMA weather TO weather_ro;
    
    -- Set default privileges for future tables
    ALTER DEFAULT PRIVILEGES IN SCHEMA weather GRANT SELECT ON TABLES TO weather_ro;
END
$$;
