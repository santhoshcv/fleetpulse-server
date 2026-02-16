# TFMS90 Protocol Specification v2.0

## Overview
Text-based TCP protocol. All messages are ASCII strings terminated with `#?` or `#`.  
Default port: **23000**

## Common Header
All messages follow this structure:
```
$,<token>,<msg_type>,<device_id>,<trip_number>,<timestamp_hex>,<payload>,#?
```

| Field | Type | Description |
|-------|------|-------------|
| `$` | char | Start delimiter |
| token | int | Message sequence number (0 for device-initiated) |
| msg_type | string | Message type identifier |
| device_id | int | Short device ID (e.g., 171) |
| trip_number | int | Current trip number (0 if not in trip) |
| timestamp_hex | hex | UTC timestamp as 8-char hex (seconds since 2000-01-01 00:00:00) |

### Timestamp Encoding
```
Hex timestamp → Seconds since 2000-01-01 00:00:00 UTC
Example: 698ED6C4 → 1774421700 seconds → 2026-02-14 10:15:00 UTC
```

### Device Identification
The device sends its full IMEI **only once** during the LG (Login) message when establishing a TCP connection. The server maps the IMEI to the device's `short_id` (e.g., 171) and internal UUID. All subsequent messages use only the `short_id` to minimize data usage. If the TCP connection drops and reconnects, the device sends LG again.

```
Connection flow:
1. TCP connect → LG with IMEI (one time)
2. Server maps: IMEI 867762040399039 → short_id 171 → UUID 5a516372-...
3. All messages use short_id 171 (saves ~11 bytes per message)
4. TCP disconnect → reconnect → LG again
```

### Coordinate Format
All coordinates are **decimal degrees, signed**:
- Positive latitude = North, Negative = South
- Positive longitude = East, Negative = West
- Example: `25.180430,51.414085` (Doha, Qatar)

---

## 1. Device Login (LG)
Sent on TCP connection establishment.

```
$,0,LG,<device_id>,<imei>,<firmware_version>,<iccid>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | imei | string | 867762040399039 |
| 2 | firmware_version | string | 2.0.1 |
| 3 | iccid | string | 8997103024032XXXXX |

**Server Response:**
```
$AK,LG,<device_id>,<server_timestamp_hex>,#
```

---

## 2. GPS Tracking (TD / TDA)
Sent at regular intervals during active trip.  
**TD** = standard tracking, **TDA** = tracking with additional data.

```
$,0,TD,<device_id>,<trip_number>,<timestamp>,<lat>,<lon>,<speed>,<heading>,<satellites>,<hdop>,<fuel_level>,<odometer>,<digital_inputs>,<digital_outputs>,<analog1>,<voltage>,<gsm_signal>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | trip_number | int | - | 795 |
| 2 | timestamp | hex | - | 698ED6C4 |
| 3 | latitude | float | degrees | 25.180430 |
| 4 | longitude | float | degrees | 51.414085 |
| 5 | speed | int | km/h | 87 |
| 6 | heading | int | degrees (0-360) | 180 |
| 7 | satellites | int | count | 12 |
| 8 | hdop | float | - | 1.2 |
| 9 | fuel_level | float | liters | 52.0 |
| 10 | odometer | int | meters | 1523456 |
| 11 | digital_inputs | hex | bitmask | 0F |
| 12 | digital_outputs | hex | bitmask | 03 |
| 13 | analog1 | float | volts | 0.0 |
| 14 | voltage | float | volts | 12.8 |
| 15 | gsm_signal | int | 0-31 | 22 |

**ACC status**: Inferred from message type. TD = ignition ON.

---

## 3. Trip Start (TS)
Sent when ignition turns ON.

```
$,0,TS,<device_id>,<trip_number>,<timestamp>,<fuel_level>,<lat>,<lon>,<voltage>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | trip_number | int | 795 |
| 2 | timestamp | hex | 698ED6C4 |
| 3 | fuel_level | float | 52.0 |
| 4 | latitude | float | 25.180430 |
| 5 | longitude | float | 51.414085 |
| 6 | voltage | float | 12.8 |

**Server Response:**
```
$AK,TS,<device_id>,<trip_number>,#
```

---

## 4. Trip End (TE)
Sent when ignition turns OFF.

```
$,0,TE,<device_id>,<trip_number>,<start_timestamp>,<end_timestamp>,<duration_sec>,<distance_m>,<start_fuel>,<end_fuel>,<fuel_consumed>,<max_speed>,<avg_speed>,<start_lat>,<start_lon>,<end_lat>,<end_lon>,<voltage>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | trip_number | int | - | 795 |
| 2 | start_timestamp | hex | - | 698ED6C4 |
| 3 | end_timestamp | hex | - | 698EDBD5 |
| 4 | duration_sec | int | seconds | 1297 |
| 5 | distance_m | int | meters | 11830 |
| 6 | start_fuel | float | liters | 52.0 |
| 7 | end_fuel | float | liters | 48.0 |
| 8 | fuel_consumed | float | liters | 4.0 |
| 9 | max_speed | int | km/h | 112 |
| 10 | avg_speed | int | km/h | 67 |
| 11 | start_lat | float | degrees | 25.180430 |
| 12 | start_lon | float | degrees | 51.414085 |
| 13 | end_lat | float | degrees | 25.195200 |
| 14 | end_lon | float | degrees | 51.428300 |
| 15 | voltage | float | volts | 12.6 |

**Server Response:**
```
$AK,TE,<device_id>,<trip_number>,#
```

---

## 5. Trip Statistics (STAT)
Sent after TE with driving behavior summary.

```
$,0,STAT,<device_id>,<trip_number>,<td_count>,<harsh_accel_count>,<harsh_brake_count>,<harsh_corner_count>,<overspeed_count>,<idle_events>,<max_rpm>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | trip_number | int | 795 |
| 2 | td_count | int | 347 |
| 3 | harsh_accel_count | int | 2 |
| 4 | harsh_brake_count | int | 1 |
| 5 | harsh_corner_count | int | 3 |
| 6 | overspeed_count | int | 1 |
| 7 | idle_events | int | 2 |
| 8 | max_rpm | int | 4200 |

---

## 6. Harsh Acceleration (HA2)
Sent when acceleration exceeds threshold.

```
$,<token>,HA2,<device_id>,<trip_number>,<start_timestamp>,<end_timestamp>,<severity>,<initial_speed>,<final_speed>,<rate>,<start_lat>,<start_lon>,<end_lat>,<end_lon>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | trip_number | int | - | 795 |
| 2 | start_timestamp | hex | - | 698ED6C4 |
| 3 | end_timestamp | hex | - | 698ED6C8 |
| 4 | severity | int | 1-3 | 2 |
| 5 | initial_speed | int | km/h | 35 |
| 6 | final_speed | int | km/h | 78 |
| 7 | rate | float | km/h/s | 10.75 |
| 8 | start_lat | float | degrees | 25.180430 |
| 9 | start_lon | float | degrees | 51.414085 |
| 10 | end_lat | float | degrees | 25.180890 |
| 11 | end_lon | float | degrees | 51.414320 |

**Severity levels:** 1 = mild, 2 = moderate, 3 = severe

**Server Response:**
```
$AK,HA2,<device_id>,<token>,#
```

---

## 7. Harsh Braking (HB2)
Same format as HA2.

```
$,<token>,HB2,<device_id>,<trip_number>,<start_timestamp>,<end_timestamp>,<severity>,<initial_speed>,<final_speed>,<rate>,<start_lat>,<start_lon>,<end_lat>,<end_lon>,#?
```

**rate** = deceleration in km/h/s (positive value, e.g., 12.5 means losing 12.5 km/h per second)

---

## 8. Harsh Cornering (HC2)
Sent when lateral g-force exceeds threshold.

```
$,<token>,HC2,<device_id>,<trip_number>,<start_timestamp>,<end_timestamp>,<severity>,<speed>,<angle>,<rate>,<start_lat>,<start_lon>,<end_lat>,<end_lon>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | trip_number | int | - | 795 |
| 2 | start_timestamp | hex | - | 698ED6C4 |
| 3 | end_timestamp | hex | - | 698ED6C6 |
| 4 | severity | int | 1-3 | 2 |
| 5 | speed | int | km/h | 65 |
| 6 | angle | int | degrees | 45 |
| 7 | rate | float | deg/s | 22.5 |
| 8 | start_lat | float | degrees | 25.180430 |
| 9 | start_lon | float | degrees | 51.414085 |
| 10 | end_lat | float | degrees | 25.180890 |
| 11 | end_lon | float | degrees | 51.414320 |

---

## 9. Overspeed (OS3)
Sent when vehicle exceeds configured speed limit.

```
$,<token>,OS3,<device_id>,<trip_number>,<start_timestamp>,<end_timestamp>,<speed_limit>,<top_speed>,<avg_speed>,<duration_sec>,<start_lat>,<start_lon>,<end_lat>,<end_lon>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | trip_number | int | - | 795 |
| 2 | start_timestamp | hex | - | 698ED6C4 |
| 3 | end_timestamp | hex | - | 698ED6F0 |
| 4 | speed_limit | int | km/h | 120 |
| 5 | top_speed | int | km/h | 145 |
| 6 | avg_speed | int | km/h | 132 |
| 7 | duration_sec | int | seconds | 44 |
| 8 | start_lat | float | degrees | 25.180430 |
| 9 | start_lon | float | degrees | 51.414085 |
| 10 | end_lat | float | degrees | 25.195200 |
| 11 | end_lon | float | degrees | 51.428300 |

**Server Response:**
```
$AK,OS3,<device_id>,<token>,#
```

---

## 10. Fuel Fill (FLF)
Sent when a refueling event is confirmed.

```
$,0,FLF,<device_id>,<trip_number>,<timestamp>,<volume>,<fuel_before>,<fuel_after>,<lat>,<lon>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | trip_number | int | - | 795 (0 if parked) |
| 2 | timestamp | hex | - | 698ED6C4 |
| 3 | volume | float | liters | 63.0 |
| 4 | fuel_before | float | liters | 31.0 |
| 5 | fuel_after | float | liters | 94.0 |
| 6 | latitude | float | degrees | 25.180430 |
| 7 | longitude | float | degrees | 51.414085 |

**Server Response:**
```
$AK,FLF,<device_id>,<token>,#
```

---

## 11. Fuel Drain (FLD)
Sent when fuel theft/drain is confirmed.

```
$,0,FLD,<device_id>,<trip_number>,<timestamp>,<volume>,<fuel_before>,<fuel_after>,<lat>,<lon>,#?
```

Same format as FLF. **volume** is the amount lost.

**Server Response:**
```
$AK,FLD,<device_id>,<token>,#
```

---

## 12. Fuel Consumption Report (FCR)
Sent with TE at end of every trip.

```
$,0,FCR,<device_id>,<trip_number>,<start_fuel>,<end_fuel>,<consumed>,<consumption_per_km>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | trip_number | int | - | 795 |
| 2 | start_fuel | float | liters | 52.0 |
| 3 | end_fuel | float | liters | 48.0 |
| 4 | consumed | float | liters | 4.0 |
| 5 | consumption_per_km | float | L/km | 0.338 |

---

## 13. Heartbeat (HB)
Sent every 60 seconds while parked (engine off). Provides fuel and device health while vehicle is stationary.

```
$,0,HB,<device_id>,<timestamp>,<fuel_level>,<voltage>,<gsm_signal>,<gps_fix>,<lat>,<lon>,<odometer>,<acc_status>,<sleep_mode>,#?
```

| Index | Field | Type | Unit | Example |
|-------|-------|------|------|---------|
| 0 | device_id | int | - | 171 |
| 1 | timestamp | hex | - | 698ED6C4 |
| 2 | fuel_level | float | liters | 48.0 |
| 3 | voltage | float | volts | 12.4 |
| 4 | gsm_signal | int | 0-31 | 18 |
| 5 | gps_fix | int | 0/1 | 1 |
| 6 | latitude | float | degrees | 25.180430 |
| 7 | longitude | float | degrees | 51.414085 |
| 8 | odometer | int | meters | 1523456 |
| 9 | acc_status | int | 0/1 | 0 |
| 10 | sleep_mode | int | 0-3 | 1 |

**Sleep modes:** 0 = active, 1 = parked_monitoring, 2 = light_sleep, 3 = deep_sleep

---

## 14. Device Health Report (DHR)
Sent once per day or on device boot.

```
$,0,DHR,<device_id>,<timestamp>,<firmware_version>,<uptime_hours>,<total_trips>,<total_km>,<flash_usage_pct>,<reboot_count>,<last_reboot_reason>,<iccid>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | timestamp | hex | 698ED6C4 |
| 2 | firmware_version | string | 2.0.1 |
| 3 | uptime_hours | int | 720 |
| 4 | total_trips | int | 1245 |
| 5 | total_km | int | 45230 |
| 6 | flash_usage_pct | int | 23 |
| 7 | reboot_count | int | 3 |
| 8 | last_reboot_reason | string | WATCHDOG |
| 9 | iccid | string | 8997103024032XXXXX |

**Reboot reasons:** POWER_ON, WATCHDOG, LOW_VOLTAGE, OTA_UPDATE, MANUAL, EXCEPTION

---

## 15. Error Report (ERR)
Sent when device detects a fault condition.

```
$,0,ERR,<device_id>,<timestamp>,<error_code>,<error_desc>,<severity>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | timestamp | hex | 698ED6C4 |
| 2 | error_code | string | GPS_LOST |
| 3 | error_desc | string | No GPS fix for 300s |
| 4 | severity | int | 1-3 |

**Error codes:**
- GPS_LOST — No GPS fix for extended period
- FUEL_SENSOR_FAIL — ADC stuck at 0V or 5V
- LOW_BATTERY — Vehicle voltage below 11.0V
- CRITICAL_BATTERY — Vehicle voltage below 10.5V
- SIM_ERROR — SIM card not detected or registration failed
- FLASH_FULL — Flash storage above 90%
- MODEM_FAIL — Cellular modem not responding
- SENSOR_DISCONNECT — External sensor disconnected

---

## 16. Geofence Event (GEO)
Sent when vehicle enters or exits a geofence.

```
$,0,GEO,<device_id>,<trip_number>,<timestamp>,<event_type>,<geofence_id>,<geofence_name>,<speed>,<lat>,<lon>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | trip_number | int | 795 |
| 2 | timestamp | hex | 698ED6C4 |
| 3 | event_type | string | ENTER or EXIT |
| 4 | geofence_id | int | 12 |
| 5 | geofence_name | string | Office_Area |
| 6 | speed | int | 45 |
| 7 | latitude | float | 25.180430 |
| 8 | longitude | float | 51.414085 |

**Server Response:**
```
$AK,GEO,<device_id>,<token>,#
```

---

## 17. Driver ID (DID)
Sent when RFID/iButton is detected.

```
$,0,DID,<device_id>,<trip_number>,<timestamp>,<driver_id>,<driver_name>,<event>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | trip_number | int | 795 |
| 2 | timestamp | hex | 698ED6C4 |
| 3 | driver_id | string | 0A1B2C3D4E |
| 4 | driver_name | string | Ahmed_Ali |
| 5 | event | string | LOGIN or LOGOUT |

---

## 18. Tamper Alert (TMP)
Sent when device detects disconnection or tampering.

```
$,0,TMP,<device_id>,<timestamp>,<tamper_type>,<voltage_before>,<lat>,<lon>,#?
```

| Index | Field | Type | Example |
|-------|-------|------|---------|
| 0 | device_id | int | 171 |
| 1 | timestamp | hex | 698ED6C4 |
| 2 | tamper_type | string | POWER_CUT |
| 3 | voltage_before | float | 12.6 |
| 4 | latitude | float | 25.180430 |
| 5 | longitude | float | 51.414085 |

**Tamper types:** POWER_CUT, CASE_OPEN, ANTENNA_CUT, LOW_VOLTAGE

*Sent using supercapacitor last-gasp power. Device has ~3 seconds to transmit.*

---

## 19. OTA Configuration (Server → Device)

### Set Configuration
```
$CFG,<device_id>,<config_key>,<config_value>,#
```

**Config keys:**
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| SPEED_LIMIT | int | 120 | Overspeed threshold (km/h) |
| FUEL_DAMP | int | 300 | Fuel sensor damping samples |
| TD_INTERVAL | int | 2 | Tracking interval (seconds) |
| IDLE_TIMEOUT | int | 180 | Idle detection timeout (seconds) |
| HB_INTERVAL | int | 60 | Heartbeat interval in sleep (seconds) |
| SLEEP_TIMEOUT | int | 1800 | Seconds after ignition off to enter light sleep |
| DEEP_SLEEP_TIMEOUT | int | 14400 | Seconds to enter deep sleep |
| HA_THRESHOLD | float | 0.4 | Harsh acceleration g-force threshold |
| HB_THRESHOLD | float | 0.35 | Harsh braking g-force threshold |
| HC_THRESHOLD | float | 0.3 | Harsh cornering g-force threshold |

**Device Response:**
```
$CFGAK,<device_id>,<config_key>,OK,#?
```

### Request Configuration Dump
```
$CFGDUMP,<device_id>,#
```

**Device Response:** Sends all current config values.

---

## 20. Server Acknowledgment Format
For critical messages, the server sends an ACK. Device retries unacknowledged messages.

```
$AK,<msg_type>,<device_id>,<token_or_trip>,#
```

**Messages requiring ACK:** LG, TS, TE, FLF, FLD, HA2, HB2, HC2, OS3, GEO, TMP, ERR

**Retry logic:**
- Device stores unACKed messages in flash
- Retries every 30 seconds, up to 10 attempts
- After 10 failures, stores for next TCP connection
- Flash holds up to 500 unACKed messages

---

## 21. Time Sync (Server → Device)
Server sends current UTC time on connection.

```
$TS,<timestamp_hex>,#
```

Device uses this to calibrate its RTC if drift > 2 seconds.

---

## Example Message Sequences

### Normal Trip
```
→ $,0,LG,171,867762040399039,2.0.1,8997103024032XXXXX,#?
← $AK,LG,171,698ED6C0,#
→ $,0,TS,171,795,698ED6C4,52.0,25.180430,51.414085,12.8,#?
← $AK,TS,171,795,#
→ $,0,TD,171,795,698ED6C6,25.180450,51.414100,35,180,12,1.2,51.8,1523456,0F,03,0.0,12.8,22,#?
→ $,0,TD,171,795,698ED6C8,25.180890,51.414320,67,185,12,1.1,51.5,1523890,0F,03,0.0,12.9,22,#?
→ $,1,HA2,171,795,698ED6CA,698ED6CE,2,35,78,10.75,25.180430,51.414085,25.180890,51.414320,#?
← $AK,HA2,171,1,#
→ $,0,TD,171,795,698ED6D0,25.181200,51.414600,87,190,12,1.0,51.0,1524200,0F,03,0.0,12.9,21,#?
→ $,0,TE,171,795,698ED6C4,698EDBD5,1297,11830,52.0,48.0,4.0,112,67,25.180430,51.414085,25.195200,51.428300,12.6,#?
← $AK,TE,171,795,#
→ $,0,FCR,171,795,52.0,48.0,4.0,0.338,#?
→ $,0,STAT,171,795,347,2,1,3,1,2,4200,#?
```

### Fuel Fill at Petrol Station
```
→ $,0,TD,171,795,698ED700,25.210000,51.430000,0,0,12,1.0,31.0,1530000,0F,03,0.0,12.8,20,#?
→ $,0,FLF,171,795,698ED730,63.0,31.0,94.0,25.210000,51.430000,#?
← $AK,FLF,171,0,#
→ $,0,TD,171,795,698ED740,25.210000,51.430000,0,0,12,1.0,94.0,1530000,0F,03,0.0,12.8,20,#?
```

### Fuel Theft While Parked (Sleep Mode)
```
→ $,0,HB,171,698EE000,48.0,12.4,18,1,25.180430,51.414085,1530000,0,2,#?
→ $,0,HB,171,698EE03C,48.0,12.4,18,1,25.180430,51.414085,1530000,0,2,#?
→ $,0,HB,171,698EE078,35.0,12.3,18,1,25.180430,51.414085,1530000,0,1,#?
→ $,0,FLD,171,0,698EE078,13.0,48.0,35.0,25.180430,51.414085,#?
← $AK,FLD,171,0,#
```

### Device Boot & Health Report
```
→ $,0,LG,171,867762040399039,2.0.1,8997103024032XXXXX,#?
← $AK,LG,171,698ED6C0,#
← $TS,698ED6C0,#
→ $,0,DHR,171,698ED6C4,2.0.1,720,1245,45230,23,3,POWER_ON,8997103024032XXXXX,#?
```

### Tamper Detection (Power Cut)
```
→ $,0,TMP,171,698EF000,POWER_CUT,12.6,25.180430,51.414085,#?
← $AK,TMP,171,0,#
(device loses power)
```

### OTA Configuration
```
← $CFG,171,SPEED_LIMIT,100,#
→ $CFGAK,171,SPEED_LIMIT,OK,#?
← $CFG,171,TD_INTERVAL,5,#
→ $CFGAK,171,TD_INTERVAL,OK,#?
```
