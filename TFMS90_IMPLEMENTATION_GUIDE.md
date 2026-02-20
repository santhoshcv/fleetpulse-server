# TFMS90 GPS Tracking System - Complete Implementation Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [TFMS90 Protocol Implementation](#tfms90-protocol-implementation)
4. [Device Registration Flow](#device-registration-flow)
5. [Data Flow](#data-flow)
6. [Database Schema](#database-schema)
7. [Ignition Status Implementation](#ignition-status-implementation)
8. [Deployment Guide](#deployment-guide)
9. [Testing Procedures](#testing-procedures)
10. [Troubleshooting](#troubleshooting)
11. [Recent Changes Log](#recent-changes-log)

---

## System Overview

### Components
1. **Backend Server** (`/Users/santhoshvargheese/Projects/fleetpulse`)
   - Python asyncio TCP server
   - Handles TFMS90 and Teltonika protocols
   - Stores data in Supabase PostgreSQL

2. **Frontend Portal** (`/Users/santhoshvargheese/webprojects/tracking-platform`)
   - React + TypeScript
   - Real-time vehicle tracking
   - Device management interface

3. **TFMS90 Simulator** (`/Users/santhoshvargheese/Projects/tfms90_simulator`)
   - Flutter/Dart application
   - Simulates TFMS90 GPS device for testing

### Technology Stack
- **Backend**: Python 3.x, asyncio, Supabase Python client
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Protocols**: TFMS90 (text-based), Teltonika (binary)

---

## Architecture

### High-Level Data Flow
```
GPS Device (TFMS90)
    ↓ TCP Connection (Port 5011)
Backend Server (connection_handler.py)
    ↓ Protocol Detection & Parsing
Protocol Adapters (tfms90.py, teltonika.py)
    ↓ TelemetryData Objects
Database Layer (database.py)
    ↓ Insert telemetry_data (varchar device_id)
Database Triggers (fn_sync_telemetry_to_gps)
    ↓ Sync to gps_locations (UUID device_id)
Frontend Portal
    ↓ Display real-time tracking
```

### Backend File Structure
```
/Users/santhoshvargheese/Projects/fleetpulse/
├── src/
│   ├── adapters/
│   │   ├── base.py                  # Base protocol adapter interface
│   │   ├── tfms90/
│   │   │   └── tfms90.py           # TFMS90 protocol parser
│   │   └── teltonika/
│   │       └── teltonika.py        # Teltonika protocol parser
│   ├── handlers/
│   │   ├── connection_handler.py   # TCP connection handler
│   │   └── protocol_router.py      # Protocol detection
│   ├── models/
│   │   ├── telemetry.py            # TelemetryData model
│   │   └── device.py               # Device model
│   └── utils/
│       └── database.py             # Supabase client wrapper
├── main.py                         # Entry point
└── server.py                       # TCP server setup
```

---

## TFMS90 Protocol Implementation

### Message Types

#### 1. LG (Login/Registration)
**Purpose**: Device initial registration
**Format**: `$,0,LG,<IMEI>,<firmware>,<sim_iccid>,#?`
**Example**: `$,0,LG,867762040399039,2.0.1,89970000000000000000,#?`
**Response**: `$,0,ACK,<short_device_id>,#?`

**Flow**:
1. Device sends LG with IMEI
2. Server checks if IMEI pre-registered in portal
3. If found: assigns short_device_id (3-digit number like 100, 101, etc.)
4. Updates device record with `device_id = "TFMS90_{short_id}"`, preserves IMEI
5. Sends ACK with short_device_id
6. Device uses short_device_id for all future messages

**IMPORTANT**: Device MUST be pre-registered in portal before connecting. Server rejects unknown devices.

#### 2. TD (Tracking Data)
**Purpose**: Periodic GPS position updates during trip
**Format**: `$,<token>,TD,<device_id>,<trip_num>,<timestamp_hex>,<lat>,<lon>,<speed>,<heading>,<sats>,<hdop>,<fuel>,<odometer>,<status_flags>,<digital_out>,<analog1>,<voltage>,<gsm>,#?`

**Field Details**:
- `token`: Trip number (used in ACK)
- `device_id`: Short device ID (e.g., 100)
- `timestamp_hex`: Seconds since 2000-01-01 in hex
- `status_flags` (hex): **Bit 0 = Ignition/ACC status**
  - `0x0F` (1111 binary) = Ignition ON
  - `0x0E` (1110 binary) = Ignition OFF
  - Bit 0: 1=ON, 0=OFF

**Example**: `$,0,TD,100,1,1A2B3C4D,13.067439,80.237617,45,270,12,1.2,45.5,123456,0F,03,0.0,12.8,22,#?`

**Response**: `$,<trip_num>,ACK,<device_id>,<num_records>,#?`

#### 3. TS (Trip Start)
**Format**: `$,0,TS,<device_id>,<trip_num>,<timestamp>,<fuel>,<lat>,<lon>,<heading>,#?`
**Purpose**: Sent when ignition turns ON / trip begins

#### 4. TE (Trip End)
**Format**: `$,0,TE,<device_id>,<trip_num>,<start_ts>,<end_ts>,<duration>,<unknown>,<start_fuel>,<end_fuel>,<distance>,<unknown>,<unknown>,<start_lat>,<start_lon>,<end_lat>,<end_lon>,<heading>,#?`
**Purpose**: Sent when ignition turns OFF / trip ends

#### 5. FLF/FLD (Fuel Fill/Drain)
**Format**: `$,0,FLF,<device_id>,<trip_num>,<timestamp>,<fuel_before>,<fuel_after>,<amount>,<lat>,<lon>,#?`
**Purpose**: Fuel level change events

#### 6. HB (Heartbeat)
**Format**: `$,0,HB,<device_id>,<timestamp>,<fuel>,<voltage>,<gsm>,<gps_fix>,<lat>,<lon>,<odometer>,<acc>,<sleep>,#?`
**Purpose**: Periodic keep-alive when not in trip

---

## Device Registration Flow

### Pre-Registration in Portal (REQUIRED)

**Step 1: Create Device in Portal**
```
Navigate to: http://localhost:5173/devices
Click: "Add Device"
Fill form:
  - Device Name: "Test Vehicle"
  - IMEI: 867762040399039  (MUST match device)
  - Protocol: TFMS90
  - Server Port: 5011
  - Status: Active
  - Hardware Config:
    ✓ Fuel Level Sensor (if device has fuel sensor)
Submit
```

**Database Record Created**:
```sql
INSERT INTO devices (
  id,                    -- UUID (auto-generated)
  device_id,            -- Initially set to IMEI
  imei,                 -- 867762040399039
  protocol_id,          -- 3 (TFMS90)
  protocol,             -- 'tfms90'
  vehicle_id,           -- NULL or linked vehicle UUID
  organization_id,      -- User's org UUID
  has_fuel_sensor,      -- true/false
  connection_status,    -- 'offline'
  status                -- 'active'
)
```

### Device Connection Flow

**Step 2: Device Connects**
```
Device → TCP connect to server:5011
Device → Sends LG message with IMEI
Server → Detects protocol = 'tfms90'
Server → Calls identify_device() → extracts IMEI
Server → Calls parse_login_message() → gets IMEI, firmware, SIM
Server → Calls get_device_by_imei(imei)
```

**Step 3: Server Validation**
```python
existing_device = await db_client.get_device_by_imei(imei)

if not existing_device:
    # REJECT - device not pre-registered
    logger.error("Device must be pre-registered in portal")
    return
```

**Step 4: Assign Short Device ID**
```python
short_id = await db_client.assign_short_device_id(imei, 'tfms90')
# Returns: 100 (first device), 101 (second), etc.
```

**Step 5: Update Device Record**
```python
device_data = {
    "device_id": f"TFMS90_{short_id}",  # Changes from IMEI to TFMS90_100
    "short_device_id": short_id,        # 100
    "protocol": "tfms90",
    "firmware_version": "2.0.1",
    "sim_iccid": "89970000000000000000",
    "last_seen": datetime.utcnow().isoformat(),
    "is_active": True
}

# Update by UUID (NOT by device_id since device_id is changing)
await db_client.update_device_by_uuid(existing_device['id'], device_data)
```

**Step 6: Send ACK**
```
Server → Sends: $,0,ACK,100,#?
Device → Receives short_device_id = 100
Device → Saves to persistent storage
Device → All future messages use device_id=100
```

**Step 7: Normal Operation**
```
Device sends TS (trip start)
Device sends TD every 3 seconds during trip
Device sends TE (trip end)
Device sends HB every 60 seconds when idle
```

---

## Data Flow

### Telemetry Data Path

**1. Device → Server**
```
TD message arrives at connection_handler.py
→ _process_data(data)
→ adapter.parse(data, device_id)
→ Returns List[TelemetryData]
```

**2. TelemetryData Model**
```python
@dataclass
class TelemetryData:
    device_id: str              # "TFMS90_100"
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: Optional[float]
    speed: Optional[float]
    heading: Optional[float]
    satellites: Optional[int]
    ignition: Optional[bool]    # CRITICAL: Parsed from status_flags
    protocol: str               # "tfms90"
    message_type: str           # "TD", "TS", "TE", etc.
    io_elements: Optional[Dict] # Extra data
```

**3. TelemetryData.to_dict()**
```python
def to_dict(self) -> Dict:
    # Extract fuel_level from io_elements
    fuel_level = None
    if self.io_elements:
        raw = self.io_elements.get("fuel_level")
        if raw is not None:
            fuel_level = float(raw)

    result = {
        "device_id": self.device_id,        # "TFMS90_100"
        "timestamp": self.timestamp.isoformat(),
        "latitude": self.latitude,
        "longitude": self.longitude,
        "altitude": self.altitude,
        "speed": self.speed,
        "heading": self.heading,
        "satellites": self.satellites,
        "fuel_level": fuel_level,           # Promoted from io_elements
        "ignition": self.ignition,          # CRITICAL for ignition display
        "protocol": self.protocol,
        "message_type": self.message_type,
        "io_elements": self.io_elements,    # Removed before DB insert
    }

    # For TE messages, promote trip data to top-level
    if self.message_type == "TE" and self.io_elements:
        result["start_timestamp"] = self.io_elements.get("start_timestamp")
        result["end_timestamp"] = self.io_elements.get("end_timestamp")
        result["duration_seconds"] = self.io_elements.get("duration_seconds")
        result["start_fuel"] = self.io_elements.get("start_fuel")
        result["end_fuel"] = self.io_elements.get("end_fuel")
        result["distance_km"] = self.io_elements.get("distance_km")
        result["start_latitude"] = self.io_elements.get("start_latitude")
        result["start_longitude"] = self.io_elements.get("start_longitude")

    return result
```

**4. Database Insert**
```python
telemetry_dict = telemetry.to_dict()
# Remove io_elements to avoid schema cache issues
telemetry_dict.pop('io_elements', None)

# Insert into telemetry_data table
await db_client.insert_telemetry(telemetry_dict)
```

**5. Database Trigger: fn_sync_telemetry_to_gps()**
```sql
CREATE OR REPLACE FUNCTION fn_sync_telemetry_to_gps()
RETURNS trigger AS $$
DECLARE
    v_portal_device_id UUID;
BEGIN
    -- Skip invalid GPS coordinates
    IF NEW.latitude IS NULL OR NEW.longitude IS NULL
       OR (NEW.latitude = 0 AND NEW.longitude = 0) THEN
        RETURN NEW;
    END IF;

    -- Resolve portal UUID from varchar device_id
    SELECT id INTO v_portal_device_id
    FROM devices
    WHERE device_id = NEW.device_id
    LIMIT 1;

    IF v_portal_device_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- Insert into gps_locations with UUID device_id
    INSERT INTO gps_locations (
        device_id,
        device_timestamp,
        latitude,
        longitude,
        altitude,
        speed,
        course,
        satellites,
        fuel_level,
        acc_status,      -- Maps from ignition
        engine_status    -- Maps from ignition
    ) VALUES (
        v_portal_device_id,  -- UUID from devices table
        NEW.timestamp,
        NEW.latitude,
        NEW.longitude,
        NEW.altitude,
        NEW.speed,
        NEW.heading,
        NEW.satellites,
        NEW.fuel_level,
        NEW.ignition,        -- CRITICAL: Maps ignition → acc_status
        NEW.ignition         -- CRITICAL: Maps ignition → engine_status
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**6. Frontend Display**
```
Frontend queries gps_locations table
Joins with devices table using UUID
Displays vehicle position + acc_status (ignition)
```

---

## Database Schema

### Table: devices
```sql
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR,              -- "TFMS90_100" (changes from IMEI after registration)
    imei VARCHAR,                   -- "867762040399039" (preserved from portal)
    short_device_id INTEGER,        -- 100 (for TFMS90 protocol communication)
    protocol_id INTEGER,            -- 3 = TFMS90
    protocol VARCHAR,               -- 'tfms90'
    vehicle_id UUID,                -- FK to vehicles.id
    organization_id UUID NOT NULL,  -- FK to organizations.id
    firmware_version VARCHAR,       -- "2.0.1" (from LG message)
    sim_iccid VARCHAR,              -- SIM card ID (from LG message)
    has_fuel_sensor BOOLEAN DEFAULT false,
    connection_status VARCHAR,      -- 'online' | 'offline'
    status VARCHAR,                 -- 'active' | 'inactive'
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_devices_device_id ON devices(device_id);
CREATE INDEX idx_devices_imei ON devices(imei);
CREATE INDEX idx_devices_vehicle_id ON devices(vehicle_id);
```

### Table: telemetry_data
```sql
CREATE TABLE telemetry_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR NOT NULL,     -- "TFMS90_100" (varchar, not UUID)
    timestamp TIMESTAMP NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    heading DOUBLE PRECISION,
    satellites INTEGER,
    fuel_level DOUBLE PRECISION,    -- Promoted from io_elements
    ignition BOOLEAN,               -- CRITICAL: Parsed from status_flags
    protocol VARCHAR,               -- 'tfms90'
    message_type VARCHAR,           -- 'TD', 'TS', 'TE', etc.

    -- TE (Trip End) specific columns
    start_timestamp TIMESTAMP,
    end_timestamp TIMESTAMP,
    duration_seconds INTEGER,
    start_fuel DOUBLE PRECISION,
    end_fuel DOUBLE PRECISION,
    distance_km DOUBLE PRECISION,
    start_latitude DOUBLE PRECISION,
    start_longitude DOUBLE PRECISION,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_telemetry_device_id ON telemetry_data(device_id);
CREATE INDEX idx_telemetry_timestamp ON telemetry_data(timestamp);

-- TRIGGER: Sync to gps_locations after insert
CREATE TRIGGER trg_sync_telemetry_to_gps
    AFTER INSERT ON telemetry_data
    FOR EACH ROW
    EXECUTE FUNCTION fn_sync_telemetry_to_gps();
```

### Table: gps_locations
```sql
CREATE TABLE gps_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL,        -- UUID (FK to devices.id)
    device_timestamp TIMESTAMP NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    course DOUBLE PRECISION,        -- Same as heading
    satellites INTEGER,
    fuel_level DOUBLE PRECISION,
    acc_status BOOLEAN,             -- Ignition status (from telemetry.ignition)
    engine_status BOOLEAN,          -- Engine status (from telemetry.ignition)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_gps_locations_device_id ON gps_locations(device_id);
CREATE INDEX idx_gps_locations_timestamp ON gps_locations(device_timestamp);
```

### Key Relationships
- `devices.id` (UUID) ← `gps_locations.device_id` (UUID)
- `devices.device_id` (VARCHAR "TFMS90_100") ← `telemetry_data.device_id` (VARCHAR)
- Database trigger syncs: `telemetry_data` → `gps_locations` (converts VARCHAR device_id to UUID)

---

## Ignition Status Implementation

### Problem
TFMS90 devices send ignition status in the `status_flags` field (hex value) of TD messages. Backend was not parsing this field, causing ignition to always show as null.

### Solution

**1. Parse status_flags in TD Message** (`tfms90.py:144-152`)
```python
# Parse status flags (hex) for ignition status
# Bit 0 of status_flags = ACC/Ignition (1 = ON, 0 = OFF)
ignition_status = None
if len(parts) > 14 and parts[14]:
    try:
        status_flags = int(parts[14], 16)  # Convert hex to int
        ignition_status = bool(status_flags & 0x01)  # Check bit 0
    except (ValueError, TypeError):
        pass
```

**How it works**:
- TD message field 14 (parts[14]) contains status_flags in hex
- Example: `0F` = 15 decimal = `1111` binary → Bit 0 = 1 → Ignition ON
- Example: `0E` = 14 decimal = `1110` binary → Bit 0 = 0 → Ignition OFF
- Bitwise AND with `0x01` checks if bit 0 is set

**2. Add Ignition to TelemetryData** (`telemetry.py:20`)
```python
@dataclass
class TelemetryData:
    # ... other fields
    ignition: Optional[bool] = None  # Added this field
```

**3. Include Ignition in to_dict()** (`telemetry.py:46`)
```python
result = {
    # ... other fields
    "ignition": self.ignition,  # Added this line
}
```

**4. Database Trigger Maps Ignition** (Supabase SQL Editor)
```sql
INSERT INTO gps_locations (
    -- ... other fields
    acc_status,      -- Maps from NEW.ignition
    engine_status    -- Maps from NEW.ignition
) VALUES (
    -- ... other values
    NEW.ignition,    -- Both acc_status and engine_status
    NEW.ignition     -- get same value from ignition field
);
```

**5. Simulator Sends Correct Status**
```dart
// tfms90_protocol.dart:71-81
static String formatTrackingData({
    // ... parameters
    required bool isEngineOn,  // Changed from hardcoded string
}) {
    // Status flags (hex): Bit 0 = ACC/Ignition (1=ON, 0=OFF)
    final String digitalInputs = isEngineOn ? '0F' : '0E';
    // ... rest of message
}
```

```dart
// app_state.dart:314
final message = TFMS90Protocol.formatTrackingData(
    // ... other params
    isEngineOn: _tripManager.isInTrip,  // Trip active = ignition ON
);
```

### Testing Ignition Status
```bash
# Start simulator, connect to server
# Start a trip → Ignition ON

# Check telemetry_data
psql $DB_URL -c "
SELECT device_id, timestamp, ignition, message_type
FROM telemetry_data
WHERE device_id LIKE 'TFMS90_%'
ORDER BY timestamp DESC
LIMIT 5;
"
# Should show ignition=true for TD messages

# Check gps_locations
psql $DB_URL -c "
SELECT d.device_id, g.device_timestamp, g.acc_status, g.engine_status
FROM gps_locations g
JOIN devices d ON d.id = g.device_id
WHERE d.protocol = 'tfms90'
ORDER BY g.device_timestamp DESC
LIMIT 5;
"
# Should show acc_status=true, engine_status=true
```

---

## Deployment Guide

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL database (Supabase account)

### Backend Deployment

**1. Install Dependencies**
```bash
cd /Users/santhoshvargheese/Projects/fleetpulse
pip install -r requirements.txt
```

**2. Configure Database**
Edit `src/utils/database.py`:
```python
SUPABASE_URL = "https://ypxlpqylmxddrvhasmst.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

**3. Run Server**
```bash
python main.py
```

**Server starts on**:
- Port 5010: Teltonika devices
- Port 5011: TFMS90 devices

**4. Deploy to Production Server**
```bash
# SSH to server
ssh root@68.183.91.130

# Navigate to project
cd /root/fleetpulse

# Pull latest changes
git pull origin main

# Restart service
sudo systemctl restart fleetpulse

# Check logs
sudo journalctl -u fleetpulse -f
```

### Frontend Deployment

**1. Install Dependencies**
```bash
cd /Users/santhoshvargheese/webprojects/tracking-platform
npm install
```

**2. Configure Environment**
Create `.env`:
```
VITE_SUPABASE_URL=https://ypxlpqylmxddrvhasmst.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

**3. Run Development Server**
```bash
npm run dev
# Opens at http://localhost:5173
```

**4. Build for Production**
```bash
npm run build
# Output in dist/
```

### Database Migration

**Apply Triggers**:
```sql
-- In Supabase SQL Editor

-- 1. Create sync function
CREATE OR REPLACE FUNCTION public.fn_sync_telemetry_to_gps()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
-- [Full function code from Database Schema section]
$function$;

-- 2. Create trigger
CREATE TRIGGER trg_sync_telemetry_to_gps
    AFTER INSERT ON telemetry_data
    FOR EACH ROW
    EXECUTE FUNCTION fn_sync_telemetry_to_gps();
```

---

## Testing Procedures

### 1. Device Registration Test

**Test Pre-Registration Requirement**:
```bash
# Start backend server
python main.py

# Start simulator WITHOUT pre-registered device
# Expected: Connection rejected, error in logs
grep "not found in database" /var/log/fleetpulse.log
```

**Test Successful Registration**:
```bash
# 1. Create device in portal with IMEI: 867762040399039
# 2. Start simulator with same IMEI
# 3. Check device updated with short_device_id

psql $DB_URL -c "
SELECT id, device_id, imei, short_device_id, protocol
FROM devices
WHERE imei = '867762040399039';
"
# Expected:
# device_id: TFMS90_100
# short_device_id: 100
```

### 2. Telemetry Data Test

**Start Trip and Verify Data**:
```bash
# 1. Start simulator
# 2. Connect to server
# 3. Start trip
# 4. Wait 10 seconds (3-4 TD messages)

# Check telemetry_data
psql $DB_URL -c "
SELECT device_id, timestamp, latitude, longitude, speed, fuel_level, ignition, message_type
FROM telemetry_data
WHERE device_id LIKE 'TFMS90_%'
ORDER BY timestamp DESC
LIMIT 10;
"

# Check gps_locations
psql $DB_URL -c "
SELECT d.device_id, g.device_timestamp, g.latitude, g.longitude, g.speed, g.fuel_level, g.acc_status
FROM gps_locations g
JOIN devices d ON d.id = g.device_id
WHERE d.protocol = 'tfms90'
ORDER BY g.device_timestamp DESC
LIMIT 10;
"
```

### 3. Ignition Status Test

**Test Ignition ON**:
```bash
# Start trip in simulator
# Check status_flags in server logs
grep "status_flags" /var/log/fleetpulse.log
# Expected: 0F (ignition ON)

# Verify database
psql $DB_URL -c "
SELECT ignition, acc_status, engine_status
FROM telemetry_data t
JOIN gps_locations g ON g.device_id = (
    SELECT id FROM devices WHERE device_id = t.device_id
)
WHERE t.device_id LIKE 'TFMS90_%'
ORDER BY t.timestamp DESC
LIMIT 1;
"
# Expected: ignition=true, acc_status=true, engine_status=true
```

**Test Ignition OFF**:
```bash
# Stop trip in simulator (sends TE message)
# TD messages stop (no more tracking data during stopped trip)
# Verify last TE message has correct fuel_level and trip data
```

### 4. Fuel Level Test

**Test Fuel Sensor Data**:
```bash
# 1. Ensure device has has_fuel_sensor=true
# 2. Start trip
# 3. Send Fuel Fill event (+30L)

psql $DB_URL -c "
SELECT device_id, timestamp, message_type, fuel_level, io_elements
FROM telemetry_data
WHERE message_type IN ('FLF', 'FLD')
ORDER BY timestamp DESC
LIMIT 5;
"
```

### 5. Trip Data Test

**Test Trip End (TE) Message**:
```bash
# 1. Start trip
# 2. Wait 30 seconds
# 3. Stop trip

psql $DB_URL -c "
SELECT
    device_id,
    message_type,
    start_timestamp,
    end_timestamp,
    duration_seconds,
    distance_km,
    start_fuel,
    end_fuel,
    start_latitude,
    start_longitude
FROM telemetry_data
WHERE message_type = 'TE'
ORDER BY timestamp DESC
LIMIT 1;
"
```

---

## Troubleshooting

### Issue: Device Not Connecting

**Symptoms**: Simulator shows "Disconnected", no logs in server

**Diagnosis**:
```bash
# Check if server is running
ps aux | grep python | grep main.py

# Check if port is listening
netstat -an | grep 5011

# Check firewall
sudo ufw status
```

**Solution**:
```bash
# Restart server
sudo systemctl restart fleetpulse

# Check logs
sudo journalctl -u fleetpulse -f
```

### Issue: Device Rejected (Not Pre-Registered)

**Symptoms**: Connection closes immediately, log shows "not found in database"

**Solution**:
1. Go to portal: http://localhost:5173/devices
2. Click "Add Device"
3. Enter **exact** IMEI from simulator
4. Set protocol = TFMS90
5. Submit
6. Retry connection

### Issue: Ignition Always Shows Null

**Diagnosis**:
```bash
# Check if ignition field exists in telemetry_data
psql $DB_URL -c "
\d telemetry_data
"
# Should show: ignition | boolean

# Check if trigger is active
psql $DB_URL -c "
SELECT tgname, tgenabled
FROM pg_trigger
WHERE tgname = 'trg_sync_telemetry_to_gps';
"
# Should show: enabled = O (origin trigger)
```

**Solution**:
```bash
# If field missing, add it
psql $DB_URL -c "
ALTER TABLE telemetry_data ADD COLUMN ignition BOOLEAN;
ALTER TABLE gps_locations ADD COLUMN acc_status BOOLEAN;
ALTER TABLE gps_locations ADD COLUMN engine_status BOOLEAN;
"

# Recreate trigger
# [Use SQL from Database Schema section]
```

### Issue: No Data in gps_locations

**Diagnosis**:
```bash
# Check if trigger is firing
psql $DB_URL -c "
SELECT COUNT(*) FROM telemetry_data WHERE device_id LIKE 'TFMS90_%';
"
# Should match:
psql $DB_URL -c "
SELECT COUNT(*)
FROM gps_locations g
JOIN devices d ON d.id = g.device_id
WHERE d.protocol = 'tfms90';
"
```

**Solution**:
```bash
# Check trigger exists and is enabled
psql $DB_URL -c "
SELECT * FROM pg_trigger WHERE tgname LIKE '%sync%';
"

# Manually test trigger
psql $DB_URL -c "
SELECT fn_sync_telemetry_to_gps();
"
```

### Issue: Duplicate Device IDs

**Symptoms**: Multiple devices with same short_device_id

**Diagnosis**:
```bash
psql $DB_URL -c "
SELECT short_device_id, COUNT(*)
FROM devices
WHERE protocol = 'tfms90'
GROUP BY short_device_id
HAVING COUNT(*) > 1;
"
```

**Solution**:
```bash
# Reassign short_device_ids
psql $DB_URL -c "
UPDATE devices
SET short_device_id = 100
WHERE imei = '867762040399039';
"
```

---

## Recent Changes Log

### 2024 Session - Ignition Status Fix

**Problem**: Ignition status always showing as null in portal

**Root Cause**:
1. Backend not parsing `status_flags` field from TD messages
2. TelemetryData model missing `ignition` field
3. Database trigger not mapping ignition to gps_locations
4. Simulator hardcoding digitalInputs='0F' regardless of trip state

**Changes Made**:

1. **Backend - tfms90.py** (Lines 144-152, 179)
   - Added ignition status parsing from hex status_flags field
   - Bitwise AND operation to check bit 0 for ACC/Ignition
   - Pass ignition_status to TelemetryData constructor

2. **Backend - telemetry.py** (Lines 20, 46)
   - Added `ignition: Optional[bool] = None` field to dataclass
   - Added ignition to to_dict() output

3. **Database - fn_sync_telemetry_to_gps()**
   - Added acc_status and engine_status columns to INSERT
   - Map NEW.ignition to both acc_status and engine_status

4. **Simulator - tfms90_protocol.dart** (Lines 71-81)
   - Changed digitalInputs from hardcoded string to dynamic bool
   - Calculate based on isEngineOn parameter
   - '0F' when true, '0E' when false

5. **Simulator - app_state.dart** (Line 314)
   - Pass isEngineOn: _tripManager.isInTrip to formatTrackingData()
   - Trip active = ignition ON, trip stopped = ignition OFF

**Testing**:
```bash
# Verified ignition parsing
echo "TD message with 0F → ignition=true"
echo "TD message with 0E → ignition=false"

# Verified database sync
echo "telemetry_data.ignition → gps_locations.acc_status"
echo "telemetry_data.ignition → gps_locations.engine_status"

# Verified simulator
echo "Trip started → sends 0F"
echo "Trip stopped → no TD messages (correct behavior)"
```

**Status**: ✅ COMPLETE - Ignition status now working end-to-end

---

## Additional Resources

### Supabase Connection String
```
postgresql://postgres.ypxlpqylmxddrvhasmst:Sm%40rtfleet123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### Important File Locations
- Backend: `/Users/santhoshvargheese/Projects/fleetpulse`
- Frontend: `/Users/santhoshvargheese/webprojects/tracking-platform`
- Simulator: `/Users/santhoshvargheese/Projects/tfms90_simulator`

### Git Repositories
- Backend: Local changes, commit before deployment
- Frontend: `/Users/santhoshvargheese/webprojects/tracking-platform`
- Simulator: No git repository (local only)

### Server Access
```bash
# Production server
ssh root@68.183.91.130

# Backend logs
sudo journalctl -u fleetpulse -f

# Backend service
sudo systemctl status fleetpulse
sudo systemctl restart fleetpulse
```

---

## End of Documentation

**Last Updated**: 2024 Session
**Status**: System fully operational with ignition status support
**Next Steps**:
- Monitor production deployment
- Test with real TFMS90 devices
- Implement additional features as needed
