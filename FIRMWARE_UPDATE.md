# TFMS90 Firmware Update Guide

## Overview

This document describes the firmware update process for TFMS90 GPS tracking devices. The firmware must be configured to connect to the FleetPulse server and send data using the TFMS90 protocol.

## Server Configuration

### Production Server Details

- **Server IP**: 164.90.223.18
- **TCP Port**: 23000
- **Protocol**: TFMS90 v2.0 (Text-based)

## TFMS90 Device Registration Flow

### First-Time Connection

When a TFMS90 device connects for the first time, it MUST send an LG (Login) message:

```
$,0,LG,<IMEI>,<firmware_version>,<sim_iccid>,#?
```

**Example:**
```
$,0,LG,867762040399039,2.0.1,89970000000000000000,#?
```

**Fields:**
- `0`: Token (always 0 for LG)
- `LG`: Message type (Login)
- `867762040399039`: Device IMEI (15 digits)
- `2.0.1`: Firmware version
- `89970000000000000000`: SIM ICCID
- `#?`: Message terminator

### Server Response

The server will respond with an ACK containing the assigned **short_device_id**:

```
$,0,ACK,<short_device_id>,#?
```

**Example:**
```
$,0,ACK,171,#?
```

The device MUST:
1. **Store this short_device_id** (e.g., 171) in non-volatile memory
2. **Use this short_device_id** in ALL subsequent messages

### Subsequent Messages

After registration, all messages must use the assigned short_device_id:

**Trip Start:**
```
$,0,TS,171,1,31262DE9,80.0,25.235807,51.536522,12.8,#?
        ^^^  (uses assigned short_device_id)
```

**Tracking Data:**
```
$,0,TD,171,1,31262DEC,25.235807,51.536522,0,0,12,1.2,110.0,1500012,0F,03,0.0,12.8,22,#?
        ^^^  (uses assigned short_device_id)
```

## Firmware Configuration Requirements

### Server Settings

Configure the device firmware with:

```
Server IP:   164.90.223.18
Server Port: 23000
Protocol:    TCP
Format:      TFMS90 Text
```

### Initial Boot Sequence

1. **Power On**: Device starts up
2. **Network Connection**: Establish GPRS/4G connection
3. **Server Connection**: Connect to 164.90.223.18:23000 via TCP
4. **Send LG Message**: Immediately send Login message with IMEI
5. **Wait for ACK**: Receive short_device_id from server
6. **Store short_device_id**: Save to EEPROM/Flash
7. **Send Data**: Use short_device_id for all subsequent messages

### Message Sending Logic

```pseudocode
IF (first_boot OR short_device_id == NULL):
    SEND LG message with IMEI
    WAIT for ACK
    STORE short_device_id from ACK

ELSE:
    USE stored short_device_id for all messages
```

### Persistent Storage

The device MUST store in non-volatile memory:
- **short_device_id**: Server-assigned ID (e.g., 171)
- **server_ip**: 164.90.223.18
- **server_port**: 23000

### Re-registration

Device should send LG message again if:
- Factory reset performed
- short_device_id is lost/corrupted
- Explicitly commanded by server (future feature)

## Message Format Specification

### LG - Login Message

**Format:**
```
$,0,LG,<IMEI>,<firmware_version>,<sim_iccid>,#?
```

**Fields:**
- Token: Always `0`
- Message Type: `LG`
- IMEI: 15-digit device IMEI
- Firmware Version: e.g., `2.0.1`
- SIM ICCID: 19-20 digit SIM card ID

**Server ACK:**
```
$,0,ACK,<short_device_id>,#?
```

### TS - Trip Start

**Format:**
```
$,0,TS,<short_id>,<trip_num>,<timestamp_hex>,<fuel>,<lat>,<lon>,<heading>,#?
```

### TD - Tracking Data

**Format:**
```
$,0,TD,<short_id>,<trip_num>,<timestamp_hex>,<lat>,<lon>,<speed>,<heading>,<sats>,<fuel>,<fuel_level>,<odometer>,<status1>,<status2>,<engine_temp>,<battery>,<gsm_signal>,#?
```

### TE - Trip End

**Format:**
```
$,0,TE,<short_id>,<trip_num>,<start_ts>,<end_ts>,<duration_sec>,<reserved>,<start_fuel>,<end_fuel>,<distance_km>,<max_speed>,<avg_speed>,<start_lat>,<start_lon>,<end_lat>,<end_lon>,<heading>,#?
```

### HB - Heartbeat

**Format:**
```
$,0,HB,<short_id>,<timestamp_hex>,<fuel>,<battery>,<gsm_signal>,<ignition>,<lat>,<lon>,<odometer>,<status1>,<status2>,#?
```

### FLF/FLD - Fuel Fill/Drain

**Format:**
```
$,0,FLF,<short_id>,<trip_num>,<timestamp_hex>,<fuel_before>,<fuel_after>,<fuel_amount>,<lat>,<lon>,#?
```

## Timestamp Format

**Hex Timestamp**: Seconds since 2000-01-01 00:00:00 UTC, encoded as hex

**Example:**
```
Current time: 2026-02-16 20:00:00
Seconds since 2000-01-01: 824947200
Hex: 31262D00
```

**Firmware Implementation:**
```c
uint32_t seconds_since_2000 = (current_time - epoch_2000) / 1000;
sprintf(timestamp_hex, "%X", seconds_since_2000);
```

## Testing Checklist

Before deploying firmware to production devices:

- [ ] Device sends LG message on first boot
- [ ] Device receives and stores short_device_id from server ACK
- [ ] Device uses stored short_device_id in all subsequent messages
- [ ] short_device_id persists across power cycles
- [ ] TS message sent when ignition ON
- [ ] TD messages sent every 3 seconds while moving
- [ ] TE message sent when ignition OFF
- [ ] HB message sent every 60 seconds
- [ ] FLF/FLD messages sent on fuel level changes
- [ ] GPS coordinates are accurate (lat/lon)
- [ ] Timestamp is correct (check server logs)
- [ ] All messages end with `#?\n`

## Troubleshooting

### Device Not Registered

**Symptoms:**
- Device not appearing in Supabase `devices` table
- Server logs show "Failed to identify device"

**Solutions:**
1. Check LG message format is correct
2. Verify IMEI is 15 digits
3. Ensure message ends with `#?\n`

### Wrong short_device_id

**Symptoms:**
- Data appears under wrong device_id in database

**Solutions:**
1. Factory reset device
2. Clear stored short_device_id
3. Reconnect and get new assignment

### Server Not Responding

**Symptoms:**
- No ACK received after LG message

**Solutions:**
1. Check server is running: `sudo systemctl status fleetpulse`
2. Check firewall: `sudo ufw status`
3. Verify server logs: `sudo tail -f /var/log/fleetpulse.log`

### Data Not Appearing in Database

**Symptoms:**
- Device connected but no telemetry data

**Solutions:**
1. Check message format matches specification
2. Verify timestamp is in hex format
3. Check lat/lon values are valid
4. Look for errors in server logs

## Firmware Update Process

### Development Environment

1. **Configure Development Settings:**
   ```
   Server IP: 164.90.223.18
   Server Port: 23000
   Debug Mode: ON
   Log Level: VERBOSE
   ```

2. **Flash Firmware:**
   - Use manufacturer's firmware update tool
   - Flash via USB/UART
   - Or use OTA update if supported

3. **Verify Configuration:**
   - Check server IP and port stored correctly
   - Verify protocol is set to TFMS90
   - Confirm GPS module is enabled

### Production Deployment

1. **Test on Single Device:**
   - Flash one device
   - Test full message flow (LG → TS → TD → TE)
   - Verify data in Supabase
   - Monitor for 24 hours

2. **Gradual Rollout:**
   - Flash 10% of fleet
   - Monitor for issues
   - If successful, flash remaining devices

3. **Monitoring:**
   - Check server logs for errors
   - Verify all devices appear in database
   - Confirm telemetry data is being received

## OTA (Over-The-Air) Updates

*(To be implemented)*

Future support for:
- Remote firmware updates
- Configuration changes
- Command execution

## Support

For firmware issues or questions:
- Check server logs: `sudo tail -f /var/log/fleetpulse.log`
- View device list: Supabase → `devices` table
- View telemetry: Supabase → `telemetry_data` table

## Appendix: Example Messages

### Complete Registration Flow

```
Device → Server: $,0,LG,867762040399039,2.0.1,89970000000000000000,#?
Server → Device: $,0,ACK,171,#?

Device → Server: $,0,TS,171,1,31262DE9,80.0,25.235807,51.536522,12.8,#?
Server → Device: $,0,ACK,171,1,#?

Device → Server: $,0,TD,171,1,31262DEC,25.235807,51.536522,0,0,12,1.2,80.0,1500012,0F,03,0.0,12.8,22,#?
Server → Device: $,0,ACK,171,1,#?
```

### Message Parsing Example

```
Message: $,0,TD,171,1,31262DEC,25.235807,51.536522,0,0,12,1.2,80.0,1500012,0F,03,0.0,12.8,22,#?

Parsed:
  Token: 0
  Type: TD (Tracking Data)
  Short Device ID: 171
  Trip Number: 1
  Timestamp: 31262DEC (2026-02-16 ~20:00)
  Latitude: 25.235807
  Longitude: 51.536522
  Speed: 0 km/h
  Heading: 0 degrees
  Satellites: 12
  Fuel Consumption: 1.2 L/h
  Fuel Level: 80.0 L
  Odometer: 1500012 meters
  Battery: 12.8 V
  GSM Signal: 22 (good)
```
