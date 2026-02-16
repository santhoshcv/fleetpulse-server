-- FleetPulse Database Schema for Supabase (PostgreSQL)
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Devices table
CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(50) PRIMARY KEY,
    protocol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    vehicle_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on last_seen for performance
CREATE INDEX idx_devices_last_seen ON devices(last_seen DESC);
CREATE INDEX idx_devices_protocol ON devices(protocol);
CREATE INDEX idx_devices_vehicle_id ON devices(vehicle_id);

-- Telemetry data table
CREATE TABLE IF NOT EXISTS telemetry_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    altitude DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    heading INTEGER,
    satellites INTEGER,
    hdop DOUBLE PRECISION,
    odometer DOUBLE PRECISION,
    engine_hours DOUBLE PRECISION,
    fuel_level DOUBLE PRECISION,
    battery_voltage DOUBLE PRECISION,
    ignition BOOLEAN,
    moving BOOLEAN,
    io_elements JSONB,
    raw_data TEXT,
    protocol VARCHAR(20) NOT NULL,
    message_type VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_telemetry_device_timestamp ON telemetry_data(device_id, timestamp DESC);
CREATE INDEX idx_telemetry_timestamp ON telemetry_data(timestamp DESC);
CREATE INDEX idx_telemetry_device_id ON telemetry_data(device_id);

-- GiST index for location queries (optional, for geospatial queries)
-- CREATE INDEX idx_telemetry_location ON telemetry_data USING GIST(
--     ll_to_earth(latitude, longitude)
-- );

-- Trips table
CREATE TABLE IF NOT EXISTS trips (
    trip_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    vehicle_id VARCHAR(50),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    start_location JSONB,
    end_location JSONB,
    distance DOUBLE PRECISION,
    duration INTEGER,
    max_speed DOUBLE PRECISION,
    avg_speed DOUBLE PRECISION,
    fuel_consumed DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for trips
CREATE INDEX idx_trips_device_id ON trips(device_id);
CREATE INDEX idx_trips_is_active ON trips(is_active);
CREATE INDEX idx_trips_start_time ON trips(start_time DESC);
CREATE INDEX idx_trips_device_active ON trips(device_id, is_active);

-- Events table (for alerts, geofence violations, etc.)
CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(50) NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    description TEXT,
    location JSONB,
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for events
CREATE INDEX idx_events_device_id ON events(device_id);
CREATE INDEX idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_acknowledged ON events(acknowledged);

-- Vehicles table (optional, for managing vehicle information)
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    registration_number VARCHAR(50),
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    vin VARCHAR(17),
    fuel_capacity DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on vehicle registration
CREATE INDEX idx_vehicles_registration ON vehicles(registration_number);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for devices table
CREATE TRIGGER update_devices_updated_at
    BEFORE UPDATE ON devices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for vehicles table
CREATE TRIGGER update_vehicles_updated_at
    BEFORE UPDATE ON vehicles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
-- Enable RLS on all tables
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE telemetry_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your auth requirements)
-- Allow all operations for service role (used by backend)
CREATE POLICY "Allow service role full access to devices"
    ON devices
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow service role full access to telemetry_data"
    ON telemetry_data
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow service role full access to trips"
    ON trips
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow service role full access to events"
    ON events
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow service role full access to vehicles"
    ON vehicles
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Sample data (optional)
-- INSERT INTO devices (device_id, protocol, name) VALUES
-- ('123456789012345', 'teltonika', 'FMB920 Test Device'),
-- ('TFMS90_001', 'tfms90', 'TFMS90 Test Device');

-- Comments for documentation
COMMENT ON TABLE devices IS 'GPS tracking devices registered in the system';
COMMENT ON TABLE telemetry_data IS 'Raw telemetry data from GPS devices';
COMMENT ON TABLE trips IS 'Vehicle trips/journeys';
COMMENT ON TABLE events IS 'System events, alerts, and notifications';
COMMENT ON TABLE vehicles IS 'Vehicle information and metadata';

-- Grant permissions (if needed)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
