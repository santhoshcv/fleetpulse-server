/*
  # FleetPulse - Fleet Management System Schema
  
  ## Overview
  Complete database schema for a professional fleet management SaaS platform with
  super admin and client portals.
  
  ## New Tables
  
  ### 1. clients
  - `id` (uuid, primary key) - Unique client identifier
  - `company_name` (text) - Client company name
  - `contact_name` (text) - Primary contact person
  - `email` (text, unique) - Client email address
  - `phone` (text) - Contact phone number
  - `status` (text) - Account status: active, suspended, trial
  - `subscription_plan` (text) - Plan: starter, professional, enterprise
  - `subscription_end_date` (timestamptz) - Subscription expiry date
  - `max_vehicles` (integer) - Maximum vehicles allowed
  - `created_at` (timestamptz) - Account creation timestamp
  - `updated_at` (timestamptz) - Last update timestamp
  
  ### 2. devices
  - `id` (uuid, primary key) - Unique device identifier
  - `imei` (text, unique) - Device IMEI number
  - `protocol` (text) - Protocol type: TFMS90, Teltonika
  - `status` (text) - Device status: active, inactive, maintenance
  - `client_id` (uuid, foreign key) - Associated client
  - `assigned_vehicle_id` (uuid, nullable) - Currently assigned vehicle
  - `last_communication` (timestamptz) - Last time device sent data
  - `created_at` (timestamptz) - Device registration date
  
  ### 3. vehicles
  - `id` (uuid, primary key) - Unique vehicle identifier
  - `client_id` (uuid, foreign key) - Owner client
  - `vehicle_number` (text) - Vehicle registration/fleet number
  - `vehicle_type` (text) - Type: truck, van, car, motorcycle
  - `make` (text) - Vehicle manufacturer
  - `model` (text) - Vehicle model
  - `year` (integer) - Manufacturing year
  - `status` (text) - Current status: online, offline, moving, idle, maintenance
  - `last_location_lat` (numeric) - Last known latitude
  - `last_location_lng` (numeric) - Last known longitude
  - `last_seen` (timestamptz) - Last GPS update timestamp
  - `odometer` (numeric) - Total distance traveled (km)
  - `fuel_level` (numeric) - Current fuel level percentage
  - `speed` (numeric) - Current speed (km/h)
  - `created_at` (timestamptz) - Vehicle registration date
  
  ### 4. trips
  - `id` (uuid, primary key) - Unique trip identifier
  - `vehicle_id` (uuid, foreign key) - Associated vehicle
  - `client_id` (uuid, foreign key) - Associated client
  - `start_time` (timestamptz) - Trip start timestamp (TS)
  - `end_time` (timestamptz, nullable) - Trip end timestamp (TE)
  - `start_location_lat` (numeric) - Starting latitude
  - `start_location_lng` (numeric) - Starting longitude
  - `end_location_lat` (numeric, nullable) - Ending latitude
  - `end_location_lng` (numeric, nullable) - Ending longitude
  - `distance` (numeric) - Total distance traveled (km)
  - `duration` (integer) - Trip duration in seconds
  - `max_speed` (numeric) - Maximum speed during trip (km/h)
  - `avg_speed` (numeric) - Average speed (km/h)
  - `fuel_consumed` (numeric) - Fuel consumed during trip (liters)
  - `created_at` (timestamptz) - Record creation timestamp
  
  ### 5. alerts
  - `id` (uuid, primary key) - Unique alert identifier
  - `vehicle_id` (uuid, foreign key) - Associated vehicle
  - `client_id` (uuid, foreign key) - Associated client
  - `alert_type` (text) - Type: overspeed, harsh_braking, geofence_violation, maintenance_due
  - `severity` (text) - Severity: low, medium, high, critical
  - `message` (text) - Alert description
  - `latitude` (numeric) - Location latitude where alert occurred
  - `longitude` (numeric) - Location longitude where alert occurred
  - `value` (numeric, nullable) - Related value (e.g., speed for overspeed)
  - `acknowledged` (boolean) - Whether alert has been acknowledged
  - `acknowledged_at` (timestamptz, nullable) - When alert was acknowledged
  - `created_at` (timestamptz) - Alert timestamp
  
  ### 6. subscription_plans
  - `id` (uuid, primary key) - Unique plan identifier
  - `name` (text) - Plan name: Starter, Professional, Enterprise
  - `price_monthly` (numeric) - Monthly price
  - `max_vehicles` (integer) - Maximum vehicles allowed
  - `max_users` (integer) - Maximum user accounts
  - `features` (jsonb) - Plan features as JSON array
  - `is_active` (boolean) - Whether plan is currently available
  - `created_at` (timestamptz) - Plan creation date
  
  ### 7. billing_records
  - `id` (uuid, primary key) - Unique billing record identifier
  - `client_id` (uuid, foreign key) - Associated client
  - `amount` (numeric) - Billing amount
  - `currency` (text) - Currency code (USD, EUR, etc.)
  - `billing_date` (timestamptz) - Date of billing
  - `payment_status` (text) - Status: pending, paid, failed, refunded
  - `payment_method` (text) - Payment method used
  - `invoice_number` (text) - Invoice reference number
  - `created_at` (timestamptz) - Record creation timestamp
  
  ### 8. system_health
  - `id` (uuid, primary key) - Unique health check identifier
  - `server_name` (text) - Server identifier
  - `status` (text) - Status: healthy, warning, critical
  - `cpu_usage` (numeric) - CPU usage percentage
  - `memory_usage` (numeric) - Memory usage percentage
  - `active_connections` (integer) - Number of active device connections
  - `checked_at` (timestamptz) - Health check timestamp
  
  ## Security
  - Enable RLS on all tables
  - Add policies for authenticated access based on user roles
*/

-- Create clients table
CREATE TABLE IF NOT EXISTS clients (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name text NOT NULL,
  contact_name text NOT NULL,
  email text UNIQUE NOT NULL,
  phone text,
  status text DEFAULT 'active' NOT NULL,
  subscription_plan text DEFAULT 'starter' NOT NULL,
  subscription_end_date timestamptz,
  max_vehicles integer DEFAULT 10,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  imei text UNIQUE NOT NULL,
  protocol text NOT NULL,
  status text DEFAULT 'active' NOT NULL,
  client_id uuid REFERENCES clients(id) ON DELETE SET NULL,
  assigned_vehicle_id uuid,
  last_communication timestamptz,
  created_at timestamptz DEFAULT now()
);

-- Create vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  vehicle_number text NOT NULL,
  vehicle_type text DEFAULT 'car' NOT NULL,
  make text,
  model text,
  year integer,
  status text DEFAULT 'offline' NOT NULL,
  last_location_lat numeric,
  last_location_lng numeric,
  last_seen timestamptz,
  odometer numeric DEFAULT 0,
  fuel_level numeric DEFAULT 0,
  speed numeric DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  UNIQUE(client_id, vehicle_number)
);

-- Add foreign key constraint for assigned_vehicle_id after vehicles table exists
ALTER TABLE devices ADD CONSTRAINT devices_vehicle_fk 
  FOREIGN KEY (assigned_vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL;

-- Create trips table
CREATE TABLE IF NOT EXISTS trips (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  vehicle_id uuid NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  start_time timestamptz NOT NULL,
  end_time timestamptz,
  start_location_lat numeric NOT NULL,
  start_location_lng numeric NOT NULL,
  end_location_lat numeric,
  end_location_lng numeric,
  distance numeric DEFAULT 0,
  duration integer DEFAULT 0,
  max_speed numeric DEFAULT 0,
  avg_speed numeric DEFAULT 0,
  fuel_consumed numeric DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  vehicle_id uuid NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  alert_type text NOT NULL,
  severity text DEFAULT 'medium' NOT NULL,
  message text NOT NULL,
  latitude numeric,
  longitude numeric,
  value numeric,
  acknowledged boolean DEFAULT false,
  acknowledged_at timestamptz,
  created_at timestamptz DEFAULT now()
);

-- Create subscription_plans table
CREATE TABLE IF NOT EXISTS subscription_plans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  price_monthly numeric NOT NULL,
  max_vehicles integer NOT NULL,
  max_users integer NOT NULL,
  features jsonb DEFAULT '[]'::jsonb,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

-- Create billing_records table
CREATE TABLE IF NOT EXISTS billing_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  amount numeric NOT NULL,
  currency text DEFAULT 'USD',
  billing_date timestamptz NOT NULL,
  payment_status text DEFAULT 'pending' NOT NULL,
  payment_method text,
  invoice_number text UNIQUE,
  created_at timestamptz DEFAULT now()
);

-- Create system_health table
CREATE TABLE IF NOT EXISTS system_health (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  server_name text NOT NULL,
  status text NOT NULL,
  cpu_usage numeric DEFAULT 0,
  memory_usage numeric DEFAULT 0,
  active_connections integer DEFAULT 0,
  checked_at timestamptz DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_vehicles_client_id ON vehicles(client_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON vehicles(status);
CREATE INDEX IF NOT EXISTS idx_trips_vehicle_id ON trips(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_trips_client_id ON trips(client_id);
CREATE INDEX IF NOT EXISTS idx_trips_start_time ON trips(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_client_id ON alerts(client_id);
CREATE INDEX IF NOT EXISTS idx_alerts_vehicle_id ON alerts(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_devices_client_id ON devices(client_id);

-- Enable Row Level Security
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_health ENABLE ROW LEVEL SECURITY;

-- RLS Policies for authenticated users
-- For now, allow authenticated users to read all data (will be refined based on user roles)
CREATE POLICY "Authenticated users can view clients"
  ON clients FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can view devices"
  ON devices FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can view vehicles"
  ON vehicles FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can view trips"
  ON trips FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can view alerts"
  ON alerts FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can view subscription plans"
  ON subscription_plans FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can view billing records"
  ON billing_records FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can view system health"
  ON system_health FOR SELECT
  TO authenticated
  USING (true);

-- Insert default subscription plans
INSERT INTO subscription_plans (name, price_monthly, max_vehicles, max_users, features) VALUES
  ('Starter', 49.99, 10, 2, '["Live tracking", "Basic reports", "Email alerts"]'::jsonb),
  ('Professional', 149.99, 50, 10, '["Live tracking", "Advanced reports", "SMS & Email alerts", "Geofencing", "Driver behavior analysis"]'::jsonb),
  ('Enterprise', 499.99, 999, 999, '["Live tracking", "Advanced reports", "SMS & Email alerts", "Geofencing", "Driver behavior analysis", "Custom integrations", "API access", "24/7 support"]'::jsonb)
ON CONFLICT (name) DO NOTHING;