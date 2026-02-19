# FleetPulse TFMS90 Fix - Deployment Guide

## What Was Wrong

The backend was receiving TFMS90 packets correctly with fuel=80L, BUT the database insert was failing with error: "column trip_number does not exist"

**Root Cause:** The Supabase Python client automatically unnests JSONB fields when inserting data. When we tried to insert:
```python
{
  "device_id": "TFMS90_100",
  "fuel_level": 80.0,
  "io_elements": {
    "trip_number": "123",
    "short_device_id": "100",
    "hdop": 1.2
  }
}
```

The Supabase client would try to insert `trip_number` and `short_device_id` as top-level columns in the database, which don't exist.

## The Fix

**Replaced Supabase Python client with raw psycopg2** which gives us direct control over SQL and properly handles JSONB without auto-unnesting.

## What Changed

### 1. Database Connection (`src/utils/database.py`)
- **Before:** Used `supabase-py` client library
- **After:** Uses `psycopg2` with direct SQL queries
- **Why:** psycopg2 properly handles JSONB fields without unnesting them

### 2. Dependencies (`requirements.txt`)
- **Added:** `psycopg2-binary` package

### 3. TFMS90 Parser (`src/adapters/tfms90/tfms90.py`)
- Already fixed TD packet field mapping (parts[12]=fuel)

### 4. Telemetry Model (`src/models/telemetry.py`)
- Already extracts fuel_level from io_elements for database trigger

## Deployment Steps

### Step 1: Push to GitHub (Local Machine)

```bash
cd /Users/santhoshvargheese/Projects/fleetpulse

# Add all changes
git add src/utils/database.py requirements.txt

# Commit
git commit -m "Fix TFMS90 fuel/telemetry insertion - replace Supabase client with psycopg2

- Replaced supabase-py with psycopg2 for direct database control
- Fixes JSONB unnesting issue causing 'trip_number column does not exist' error
- Added proper JSONB handling using psycopg2.extras.Json
- Fuel level and trips should now work correctly"

# Push to remote
git push origin main
```

### Step 2: Deploy to Server (SSH to 164.90.223.18)

```bash
# SSH to server
ssh root@164.90.223.18

# Navigate to project directory
cd /root/fleetpulse

# Pull latest changes
git pull origin main

# Install new dependency
pip3 install psycopg2-binary

# Clear Python cache to ensure new code loads
rm -rf src/**/__pycache__ src/__pycache__

# Kill existing backend process
pkill -f "python3 -m src.main"

# Start backend with logging
cd /root/fleetpulse
nohup python3 -m src.main > backend.log 2>&1 &

# Verify it's running
ps aux | grep python3

# Monitor logs in real-time
tail -f backend.log
```

### Step 3: Test with Simulator

1. **Start the simulator** with:
   - Server: `164.90.223.18`
   - Port: `23000`
   - IMEI: `867762040399040`
   - Device ID: `100`

2. **Send TD packet** (tracking data with fuel=80L)

3. **Check logs** for successful insert:
   ```
   ✓ Telemetry inserted successfully
   ```

4. **Verify in database** (run in Supabase SQL Editor):
   ```sql
   SELECT device_id, timestamp, fuel_level, latitude, longitude, message_type
   FROM telemetry_data
   WHERE device_id = 'TFMS90_100'
   ORDER BY timestamp DESC
   LIMIT 5;
   ```

5. **Check frontend** at `http://localhost:5174/live/6b6d7c1c-891a-45bf-ae53-154d663277d3`
   - Fuel should show 80L
   - Location should update

### Step 4: Test Trip Creation

1. **Send TS packet** (trip start) from simulator
2. **Send TE packet** (trip end) from simulator
3. **Check trips table**:
   ```sql
   SELECT * FROM trips
   WHERE device_id IN (
     SELECT id FROM devices WHERE short_device_id = '100'
   )
   ORDER BY start_time DESC
   LIMIT 5;
   ```

4. **Check frontend** at `http://localhost:5174/trips`
   - New trip should appear

## What This Fixes

1. ✓ Fuel level updates (80L will show correctly)
2. ✓ Telemetry data insertion (no more "column does not exist" errors)
3. ✓ Trip creation (TS/TE packets will create trip records via database trigger)
4. ✓ Engine status (will sync from telemetry via trigger)
5. ✓ All other TFMS90 message types (FLF, FLD, HA2, HB2, etc.)

## Technical Details

### How JSONB is Now Handled

**Before (Supabase client):**
```python
# This would fail
data = {"io_elements": {"trip_number": "123"}}
supabase.table("telemetry_data").insert(data).execute()
# Error: column "trip_number" does not exist
```

**After (psycopg2):**
```python
# This works correctly
from psycopg2.extras import Json
data = {"io_elements": Json({"trip_number": "123"})}
cursor.execute("INSERT INTO telemetry_data (io_elements) VALUES (%s)", (data['io_elements'],))
# Success: io_elements stored as proper JSONB
```

### Database Triggers (Already in Place)

1. **`fn_sync_telemetry_to_gps()`** - Syncs telemetry_data → gps_locations
   - Maps varchar device_id to UUID
   - Copies fuel_level, lat/lon, speed, etc.
   - Frontend reads from gps_locations

2. **`fn_sync_trip_end()`** - Creates trip records from TE packets
   - Triggers on telemetry_data INSERT where message_type='TE'
   - Extracts start/end times, distance, fuel from io_elements

## Rollback Plan (If Needed)

If something goes wrong, revert to old code:

```bash
# On server
cd /root/fleetpulse
git log --oneline  # Find commit hash before changes
git checkout <previous_commit_hash> src/utils/database.py
pkill -f "python3 -m src.main"
nohup python3 -m src.main > backend.log 2>&1 &
```

## Expected Outcome

After deployment:
- Backend logs show: `✓ Telemetry inserted successfully`
- Database has new rows in `telemetry_data` with correct fuel_level
- Frontend displays correct fuel (80L)
- Trips appear when TS/TE packets are sent
- No more 400 errors or "column does not exist" errors
