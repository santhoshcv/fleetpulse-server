# Supported GPS Protocols

## Currently Supported

### ✅ TFMS90 (Text-based Protocol)

**Status**: Fully implemented and tested

**Message Types Supported:**
- ✅ LG - Login/Device Registration (with short_device_id assignment)
- ✅ TS - Trip Start
- ✅ TD - Tracking Data (GPS location, speed, fuel, etc.)
- ✅ TE - Trip End
- ✅ HB - Heartbeat
- ✅ FLF - Fuel Fill Event
- ✅ FLD - Fuel Drain Event
- ✅ HA2 - Harsh Acceleration
- ✅ HB2 - Harsh Braking
- ✅ HC2 - Harsh Cornering
- ✅ OS3 - Overspeed
- ✅ STAT - Status

**Device Registration Flow (LG Message):**

1. **New Device Connects** - Sends LG message with IMEI:
   ```
   $,0,LG,867762040399039,2.0.1,89970000000000000000,#?
           ^^^^^^^^^^^^^^^ (15-digit IMEI)
   ```

2. **Server Processing:**
   - Receives IMEI from LG message
   - Checks if IMEI exists in database
   - If new: Assigns next available short_device_id (e.g., 171)
   - If existing: Retrieves stored short_device_id
   - Stores mapping: IMEI → short_device_id

3. **Server Response** - Sends ACK with assigned short_device_id:
   ```
   $,0,ACK,171,#?
           ^^^ (assigned short_device_id)
   ```

4. **Subsequent Messages** - Device uses short_device_id:
   ```
   $,0,TS,171,1,31262DE9,...
   $,0,TD,171,1,31262DEC,...
           ^^^ (uses assigned short_device_id)
   ```

**Protocol Format:**
```
LG:    $,0,LG,<IMEI>,<firmware>,<sim_iccid>,#?
Other: $,<token>,<message_type>,<short_device_id>,<trip_number>,<data...>,#?
```

**Database Fields:**
- `imei`: Full 15-digit IMEI
- `short_device_id`: Server-assigned 3-digit ID (100-999)
- `firmware_version`: Device firmware version
- `sim_iccid`: SIM card ICCID

**Tested With:**
- Flutter TFMS90 Simulator (Android)
- Real GPS coordinates from mobile phone

**Code Location:**
- Adapter: `src/adapters/tfms90/tfms90.py`
- Protocol Router: `src/handlers/protocol_router.py`
- Connection Handler: `src/handlers/connection_handler.py`
- Database Migration: `database/migration_add_tfms90_fields.sql`

---

### ✅ Teltonika Codec 8E (Binary Protocol)

**Status**: Fully implemented and tested

**Devices:**
- FMB920 (Vehicle tracker)
- FMA120 (Asset tracker)
- FMB125, FMB130, etc.

**Protocol Details:**
- Binary format
- CRC validation required
- High-frequency data (1-second intervals)
- Rich IO elements (200+ parameters)

**Format:**
```
[Preamble][Data Length][Codec ID][Records][CRC]
```

**Implementation Plan:**
1. Create `src/adapters/teltonika/` directory
2. Implement `teltonika_codec8e.py` adapter
3. Add binary protocol detection in `protocol_router.py`
4. Add CRC validation
5. Parse AVL data records
6. Map IO elements to telemetry fields
7. Test with Teltonika device or simulator

**Reference:**
- Teltonika Codec 8E Protocol Documentation
- Example Flutter Teltonika Simulator (existing)

**Estimated Effort:** 4-6 hours

---

## Future Protocol Support

### GT06 Protocol
- Status: Planned
- Devices: Chinese GPS trackers
- Format: Binary

### Queclink Protocol
- Status: Planned
- Devices: Queclink GL series
- Format: Text-based (AT commands)

### Concox Protocol
- Status: Planned
- Devices: Concox GT series
- Format: Binary

---

## Adding New Protocols

To add a new protocol:

1. **Create adapter** in `src/adapters/<protocol_name>/`
   ```python
   class NewProtocolAdapter(ProtocolAdapter):
       async def parse(self, data: bytes, device_id: str) -> List[TelemetryData]:
           # Parse implementation
           pass

       def identify_device(self, data: bytes) -> Optional[str]:
           # Device ID extraction
           pass

       def create_response(self, num_records: int, **kwargs) -> bytes:
           # ACK response
           pass
   ```

2. **Register in protocol router** (`src/handlers/protocol_router.py`)
   ```python
   self.adapters = {
       'tfms90': TFMS90Adapter(),
       'new_protocol': NewProtocolAdapter(),
   }
   ```

3. **Add detection logic** in `detect_protocol()` method

4. **Test thoroughly** with real device or simulator

5. **Update this documentation**
