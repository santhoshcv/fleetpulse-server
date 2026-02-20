# TFMS90 System - Quick Reference Guide

## 🚀 Quick Start

### Start Backend Server
```bash
cd /Users/santhoshvargheese/Projects/fleetpulse
python main.py
# Listening on ports 5010 (Teltonika) and 5011 (TFMS90)
```

### Start Frontend Portal
```bash
cd /Users/santhoshvargheese/webprojects/tracking-platform
npm run dev
# Opens at http://localhost:5173
```

### Start TFMS90 Simulator
```bash
cd /Users/santhoshvargheese/Projects/tfms90_simulator
flutter run
# Or open in Android Studio/VS Code
```

---

## 📋 Common Tasks

### Add New TFMS90 Device
1. Portal → Devices → Add Device
2. Enter IMEI: `867762040399039`
3. Protocol: TFMS90
4. Port: 5011
5. Hardware Config: ✓ Fuel Sensor (if applicable)
6. Submit
7. Start device/simulator → connects automatically

### Check Device Status
```bash
# Database query
psql postgresql://postgres.ypxlpqylmxddrvhasmst:Sm%40rtfleet123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres -c "
SELECT device_id, imei, short_device_id, protocol, connection_status, last_seen
FROM devices
WHERE protocol = 'tfms90'
ORDER BY last_seen DESC;
"
```

### View Recent Telemetry
```bash
psql $DB_URL -c "
SELECT device_id, timestamp, latitude, longitude, speed, fuel_level, ignition
FROM telemetry_data
WHERE device_id LIKE 'TFMS90_%'
ORDER BY timestamp DESC
LIMIT 10;
"
```

### Check Ignition Status
```bash
psql $DB_URL -c "
SELECT d.device_id, g.device_timestamp, g.acc_status, g.engine_status
FROM gps_locations g
JOIN devices d ON d.id = g.device_id
WHERE d.protocol = 'tfms90'
ORDER BY g.device_timestamp DESC
LIMIT 5;
"
```

---

## 🔧 Critical File Locations

### Backend (Python)
```
/Users/santhoshvargheese/Projects/fleetpulse/
├── main.py                                    # Entry point
├── src/adapters/tfms90/tfms90.py             # Protocol parser (ignition parsing at line 144)
├── src/models/telemetry.py                   # Data model (ignition field at line 20)
├── src/handlers/connection_handler.py        # Device registration (line 200-229)
└── src/utils/database.py                     # Supabase client
```

### Frontend (React)
```
/Users/santhoshvargheese/webprojects/tracking-platform/
├── src/pages/Devices.tsx                     # Device management (fuel sensor config at line 509)
├── src/pages/LiveTracking.tsx                # Real-time map
└── src/components/device-detail/            # Device detail views
```

### Simulator (Flutter)
```
/Users/santhoshvargheese/Projects/tfms90_simulator/
├── lib/utils/tfms90_protocol.dart           # Protocol formatter (ignition at line 71-81)
└── lib/services/app_state.dart              # State management (trip handling)
```

---

## 🐛 Common Issues & Fixes

### Issue: Device Not Connecting
```bash
# Check server running
ps aux | grep "python.*main.py"

# Check port listening
lsof -i :5011

# Restart server
cd /Users/santhoshvargheese/Projects/fleetpulse
python main.py
```

### Issue: "Device not found in database"
**Cause**: Device not pre-registered in portal
**Fix**: Add device in portal BEFORE connecting

### Issue: Ignition Always Null
**Cause**: Database trigger not mapping ignition field
**Fix**: Run this SQL in Supabase SQL Editor:
```sql
-- Add columns if missing
ALTER TABLE telemetry_data ADD COLUMN IF NOT EXISTS ignition BOOLEAN;
ALTER TABLE gps_locations ADD COLUMN IF NOT EXISTS acc_status BOOLEAN;
ALTER TABLE gps_locations ADD COLUMN IF NOT EXISTS engine_status BOOLEAN;

-- Recreate trigger (see TFMS90_IMPLEMENTATION_GUIDE.md)
```

### Issue: No Data in gps_locations
**Cause**: Trigger not syncing telemetry_data → gps_locations
**Fix**: Check trigger exists:
```bash
psql $DB_URL -c "SELECT tgname FROM pg_trigger WHERE tgname = 'trg_sync_telemetry_to_gps';"
```
If missing, recreate using SQL in TFMS90_IMPLEMENTATION_GUIDE.md

---

## 📊 Database Quick Reference

### Connection String
```
postgresql://postgres.ypxlpqylmxddrvhasmst:Sm%40rtfleet123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### Key Tables
- `devices` - Device registry (UUID id, VARCHAR device_id, VARCHAR imei)
- `telemetry_data` - Raw telemetry (VARCHAR device_id, matches devices.device_id)
- `gps_locations` - Frontend data (UUID device_id, FK to devices.id)

### Critical Trigger
```sql
trg_sync_telemetry_to_gps
→ Fires AFTER INSERT on telemetry_data
→ Syncs to gps_locations
→ Converts VARCHAR device_id → UUID device_id
→ Maps ignition → acc_status, engine_status
```

---

## 🔐 TFMS90 Protocol Cheat Sheet

### Message Types
- **LG** - Login (IMEI → short_device_id assignment)
- **TS** - Trip Start (ignition ON)
- **TD** - Tracking Data (every 3 sec during trip)
- **TE** - Trip End (ignition OFF)
- **HB** - Heartbeat (every 60 sec when idle)
- **FLF/FLD** - Fuel Fill/Drain

### TD Message Format
```
$,<trip_num>,TD,<device_id>,<trip_num>,<timestamp>,<lat>,<lon>,<speed>,<heading>,<sats>,<hdop>,<fuel>,<odometer>,<status_flags>,<digital_out>,<analog1>,<voltage>,<gsm>,#?
                                                                                                                               ^^^^^^^^^^^^
                                                                                                                               Ignition here!
```

### Status Flags (Hex)
- `0F` = Ignition ON (bit 0 = 1)
- `0E` = Ignition OFF (bit 0 = 0)

### ACK Response
```
$,<trip_num>,ACK,<device_id>,<num_records>,#?
```

---

## 🚀 Deployment Commands

### Backend to Production
```bash
# SSH to server
ssh root@68.183.91.130

# Pull latest code
cd /root/fleetpulse
git pull origin main

# Restart service
sudo systemctl restart fleetpulse

# Check status
sudo systemctl status fleetpulse

# View logs
sudo journalctl -u fleetpulse -f
```

### Frontend Build
```bash
cd /Users/santhoshvargheese/webprojects/tracking-platform
npm run build
# Output in dist/
```

---

## 📈 Testing Checklist

### Device Registration
- [ ] Create device in portal with IMEI
- [ ] Set protocol = TFMS90, port = 5011
- [ ] Configure fuel sensor if applicable
- [ ] Start simulator/device
- [ ] Verify connection (check logs)
- [ ] Verify device_id updated to TFMS90_XXX
- [ ] Verify short_device_id assigned

### Telemetry Flow
- [ ] Start trip in simulator
- [ ] Wait 10 seconds (3-4 TD messages)
- [ ] Check telemetry_data table (should have 3-4 rows)
- [ ] Check gps_locations table (should have 3-4 rows)
- [ ] Verify ignition=true in both tables
- [ ] Verify fuel_level present if sensor enabled
- [ ] Verify portal shows vehicle on map

### Ignition Status
- [ ] Start trip → Check ignition=true
- [ ] Verify server logs show status_flags=0F
- [ ] Verify telemetry_data.ignition = true
- [ ] Verify gps_locations.acc_status = true
- [ ] Verify portal displays "Engine ON" or similar

### Trip Data
- [ ] Start trip
- [ ] Drive for 30+ seconds
- [ ] Stop trip
- [ ] Verify TE message in telemetry_data
- [ ] Check start_timestamp, end_timestamp, duration_seconds
- [ ] Check distance_km, start_fuel, end_fuel

---

## 🔍 Debug Commands

### Check Server Logs
```bash
# Local
tail -f /var/log/fleetpulse.log

# Production
ssh root@68.183.91.130 'sudo journalctl -u fleetpulse -f'
```

### Check Database Connection
```bash
psql postgresql://postgres.ypxlpqylmxddrvhasmst:Sm%40rtfleet123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres -c "SELECT NOW();"
```

### Check Device Count
```bash
psql $DB_URL -c "SELECT protocol, COUNT(*) FROM devices GROUP BY protocol;"
```

### Check Recent Messages
```bash
psql $DB_URL -c "
SELECT device_id, timestamp, message_type, ignition, fuel_level
FROM telemetry_data
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 20;
"
```

### Check Trigger Status
```bash
psql $DB_URL -c "
SELECT tgname, tgenabled, tgisinternal
FROM pg_trigger
WHERE tgrelid = 'telemetry_data'::regclass;
"
```

---

## 📚 Documentation Files

1. **TFMS90_IMPLEMENTATION_GUIDE.md** - Complete technical documentation (800+ lines)
   - System architecture
   - Protocol specifications
   - Database schema
   - Deployment procedures
   - Troubleshooting guide

2. **QUICK_REFERENCE.md** - This file - Quick commands and cheat sheet

3. **README.md** - Project overview (if exists)

---

## 🎯 Key Changes Made (Recent Session)

### Ignition Status Fix
1. **tfms90.py** - Parse status_flags hex field → ignition boolean
2. **telemetry.py** - Add ignition field to TelemetryData
3. **Database** - Add ignition column, update trigger to sync
4. **Simulator** - Dynamic status_flags based on trip state

### Files Modified
- `/Users/santhoshvargheese/Projects/fleetpulse/src/adapters/tfms90/tfms90.py`
- `/Users/santhoshvargheese/Projects/fleetpulse/src/models/telemetry.py`
- `/Users/santhoshvargheese/Projects/tfms90_simulator/lib/utils/tfms90_protocol.dart`
- `/Users/santhoshvargheese/Projects/tfms90_simulator/lib/services/app_state.dart`

### Database Changes
- Added `ignition BOOLEAN` to `telemetry_data`
- Added `acc_status BOOLEAN` to `gps_locations`
- Added `engine_status BOOLEAN` to `gps_locations`
- Updated `fn_sync_telemetry_to_gps()` trigger

---

## ⚠️ Important Notes

### Device Registration Rule
**CRITICAL**: TFMS90 devices MUST be pre-registered in portal before connecting.
Server rejects unknown devices with error: "Device must be pre-registered"

### Device ID Mapping
- **Portal creation**: `device_id = IMEI`
- **After LG message**: `device_id = TFMS90_{short_id}`
- **IMEI preserved**: Original IMEI never changes
- **short_device_id**: Used for protocol communication only

### Database Architecture
- **telemetry_data**: VARCHAR device_id (backend writes here)
- **gps_locations**: UUID device_id (frontend reads here)
- **Trigger**: Syncs telemetry_data → gps_locations automatically

### Simulator Behavior
- **Trip Started**: Sends TD every 3 seconds with status_flags=0F (ignition ON)
- **Trip Stopped**: Sends TE, stops TD messages
- **Idle**: Sends HB every 60 seconds

---

## 🔗 Useful Links

- Frontend Portal: http://localhost:5173
- Supabase Dashboard: https://app.supabase.com/project/ypxlpqylmxddrvhasmst
- Production Server: ssh root@68.183.91.130

---

**Last Updated**: 2024 Session
**Status**: ✅ System operational with full ignition status support
