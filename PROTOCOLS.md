# Supported GPS Protocols

## Currently Supported

### ✅ TFMS90 (Text-based Protocol)

**Status**: Fully implemented and tested

**Message Types Supported:**
- ✅ LG - Login/Device Registration
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

**Protocol Format:**
```
$,<token>,<message_type>,<device_id>,<trip_number>,<data...>,#?
```

**Tested With:**
- Flutter TFMS90 Simulator (Android)
- Real GPS coordinates from mobile phone

**Code Location:**
- Adapter: `src/adapters/tfms90/tfms90.py`
- Protocol Router: `src/handlers/protocol_router.py`

---

## Planned Support

### 🔜 Teltonika Codec 8E (Binary Protocol)

**Status**: Not yet implemented

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
