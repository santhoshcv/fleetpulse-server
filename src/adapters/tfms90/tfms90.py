"""TFMS90 Protocol Adapter."""

import logging
from typing import List, Optional
from datetime import datetime
from src.adapters.base import ProtocolAdapter
from src.models.telemetry import TelemetryData

logger = logging.getLogger(__name__)


class TFMS90Adapter(ProtocolAdapter):
    """Adapter for TFMS90 text-based protocol."""

    def __init__(self):
        """Initialize TFMS90 adapter."""
        self.logger = logger

    def identify_device(self, data: bytes) -> Optional[str]:
        """
        Extract device ID from TFMS90 message.

        LG Format: $,0,LG,<IMEI>,<firmware>,<sim>,#?
        Other Format: $,<token>,<msg_type>,<short_device_id>,<trip_number>,<timestamp>,<payload>,#?
        After splitting by '$,': ['', '<token>', '<msg_type>', '<device_id>', ...]
        """
        try:
            text = data.decode('ascii').strip()
            if not text.startswith('$'):
                return None

            parts = text.split(',')
            if len(parts) < 4:
                return None

            # parts[0] = '' (before $)
            # parts[1] = token
            # parts[2] = message type
            # parts[3] = IMEI (for LG) or short_device_id (for others)
            msg_type = parts[2].upper()
            device_id = parts[3]

            if msg_type == 'LG':
                # LG message contains full IMEI
                self.logger.info(f"Identified TFMS90 device (LG): IMEI={device_id}")
                return f"TFMS90_IMEI_{device_id}"
            else:
                # Other messages use short_device_id
                self.logger.info(f"Identified TFMS90 device: short_id={device_id}")
                return f"TFMS90_{device_id}"

        except Exception as e:
            self.logger.error(f"Error identifying TFMS90 device: {e}")
            return None

    async def parse(self, data: bytes, device_id: str) -> List[TelemetryData]:
        """
        Parse TFMS90 data into telemetry records.

        Format: $,<token>,<msg_type>,<device_id>,<trip_number>,<timestamp_hex>,<lat>,<lon>,<speed>,<heading>,<satellites>,<fuel>,<odometer>,#?
        """
        try:
            text = data.decode('ascii').strip()
            self.logger.info(f"Parsing TFMS90 message: {text[:100]}")

            if not text.startswith('$'):
                self.logger.warning("Message doesn't start with $")
                return []

            # Remove $ and split
            parts = text.split(',')

            if len(parts) < 4:
                self.logger.warning(f"Insufficient parts: {len(parts)}")
                return []

            # parts[0] = '' (empty string before $)
            # parts[1] = token
            # parts[2] = message type
            # parts[3] = device_id
            token = parts[1]
            msg_type = parts[2].upper()
            dev_id = parts[3]

            self.logger.info(f"Message type: {msg_type}, Device: {dev_id}, Token: {token}")

            # Parse based on message type
            if msg_type == 'LG':
                # LG is handled separately for device registration
                # It doesn't produce telemetry records
                self.logger.info(f"LG message - device registration handled separately")
                return []
            elif msg_type == 'TD' or msg_type == 'TDA':
                return await self._parse_tracking_data(parts, device_id)
            elif msg_type in ['TS', 'TE']:
                return await self._parse_trip_event(parts, device_id, msg_type)
            elif msg_type in ['HA2', 'HB2', 'HC2']:
                return await self._parse_harsh_event(parts, device_id, msg_type)
            elif msg_type in ['FLF', 'FLD']:
                return await self._parse_fuel_event(parts, device_id, msg_type)
            elif msg_type in ['HB', 'OS3', 'STAT']:
                return await self._parse_status(parts, device_id, msg_type)
            else:
                self.logger.warning(f"Unknown message type: {msg_type}")
                return []

        except Exception as e:
            self.logger.error(f"Error parsing TFMS90 data: {e}")
            return []

    async def _parse_tracking_data(self, parts: List[str], device_id: str) -> List[TelemetryData]:
        """
        Parse TD (Tracking Data) message.

        Format after split: ['', token, 'TD', dev_id, trip_num, timestamp_hex, lat, lon, speed, heading, sats, hdop, fuel_level, odometer, ...]
        Indices:             0    1      2      3        4           5            6    7     8       9       10    11    12          13
        """
        try:
            if len(parts) < 13:
                self.logger.warning(f"TD message too short: {len(parts)} parts")
                return []

            # Parse timestamp (hex seconds since 2000-01-01)
            timestamp_hex = parts[5]
            timestamp = self._parse_timestamp(timestamp_hex)

            # Parse GPS data
            latitude = float(parts[6])
            longitude = float(parts[7])
            speed = float(parts[8]) if parts[8] else 0.0
            heading = float(parts[9]) if parts[9] else 0.0
            satellites = int(parts[10]) if parts[10] else 0

            # Parse IO elements
            # parts[11] = hdop
            # parts[12] = fuel_level (liters)
            # parts[13] = odometer (meters)
            # parts[14] = status_flags (hex) - contains ignition/ACC status
            # parts[17] = battery_voltage
            hdop = float(parts[11]) if len(parts) > 11 and parts[11] else None
            fuel = float(parts[12]) if len(parts) > 12 and parts[12] else None
            odometer = float(parts[13]) if len(parts) > 13 and parts[13] else None

            # Parse status flags (hex) for ignition status
            # Bit 0 of status_flags = ACC/Ignition (1 = ON, 0 = OFF)
            ignition_status = None
            if len(parts) > 14 and parts[14]:
                try:
                    status_flags = int(parts[14], 16)  # Convert hex to int
                    ignition_status = bool(status_flags & 0x01)  # Check bit 0
                except (ValueError, TypeError):
                    pass

            # Battery voltage
            battery_voltage = float(parts[17]) if len(parts) > 17 and parts[17] else None

            io_elements = {
                "hdop": hdop,
                "fuel_level": fuel,
                "odometer": odometer,
                "battery_voltage": battery_voltage,
            }

            telemetry = TelemetryData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading,
                satellites=satellites,
                ignition=ignition_status,
                protocol="tfms90",
                message_type="TD",
                io_elements=io_elements,
            )

            self.logger.info(f"Parsed TD: lat={latitude}, lon={longitude}, speed={speed}")
            return [telemetry]

        except Exception as e:
            self.logger.error(f"Error parsing TD message: {e}")
            return []

    async def _parse_trip_event(self, parts: List[str], device_id: str, msg_type: str) -> List[TelemetryData]:
        """
        Parse TS (Trip Start) or TE (Trip End) message.

        TS Format: $,0,TS,dev,trip,timestamp,fuel,lat,lon,heading,#?
        TE Format: $,0,TE,dev,trip,start_ts,end_ts,duration,?,start_fuel,end_fuel,distance,?,?,start_lat,start_lon,end_lat,end_lon,heading,#
        """
        try:
            if msg_type == "TS":
                # Trip Start: simpler format
                if len(parts) < 10:
                    return []

                timestamp = self._parse_timestamp(parts[5])
                fuel = float(parts[6]) if parts[6] else None
                latitude = float(parts[7])
                longitude = float(parts[8])
                heading = float(parts[9]) if len(parts) > 9 and parts[9] else 0.0

                io_elements = {
                    "event_type": "trip_start",
                    "fuel_level": fuel,
                }

                return [TelemetryData(
                    device_id=device_id,
                    timestamp=timestamp,
                    latitude=latitude,
                    longitude=longitude,
                    heading=heading,
                    protocol="tfms90",
                    message_type=msg_type,
                    io_elements=io_elements,
                )]

            else:  # TE - Trip End
                # Trip End: complex format with start/end data
                if len(parts) < 18:
                    return []

                start_timestamp = self._parse_timestamp(parts[5])
                end_timestamp = self._parse_timestamp(parts[6])
                duration = int(parts[7]) if parts[7] else 0
                start_fuel = float(parts[9]) if parts[9] else None
                end_fuel = float(parts[10]) if parts[10] else None
                distance = float(parts[11]) if parts[11] else 0.0

                # Use end location as the primary location
                latitude = float(parts[16])
                longitude = float(parts[17])
                heading = float(parts[18]) if len(parts) > 18 and parts[18] and parts[18] != '#' else 0.0

                io_elements = {
                    "trip_number": parts[4],  # needed by trip creation trigger
                    "event_type": "trip_end",
                    "start_timestamp": start_timestamp.isoformat(),
                    "end_timestamp": end_timestamp.isoformat(),
                    "duration_seconds": duration,
                    "start_fuel": start_fuel,
                    "end_fuel": end_fuel,
                    "fuel_level": end_fuel,  # current fuel level at trip end (used by gps_locations trigger)
                    "distance_km": distance,
                    "start_latitude": float(parts[14]),
                    "start_longitude": float(parts[15]),
                }

                return [TelemetryData(
                    device_id=device_id,
                    timestamp=end_timestamp,
                    latitude=latitude,
                    longitude=longitude,
                    heading=heading,
                    protocol="tfms90",
                    message_type=msg_type,
                    io_elements=io_elements,
                )]

        except Exception as e:
            self.logger.error(f"Error parsing {msg_type} message: {e}")
            return []

    async def _parse_harsh_event(self, parts: List[str], device_id: str, msg_type: str) -> List[TelemetryData]:
        """Parse harsh acceleration/braking/cornering events."""
        try:
            if len(parts) < 11:
                return []

            timestamp = self._parse_timestamp(parts[5])
            latitude = float(parts[6])
            longitude = float(parts[7])

            event_map = {"HA2": "harsh_acceleration", "HB2": "harsh_braking", "HC2": "harsh_cornering"}

            io_elements = {
                "event_type": event_map.get(msg_type, "harsh_event"),
            }

            return [TelemetryData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                protocol="tfms90",
                message_type=msg_type,
                io_elements=io_elements,
            )]

        except Exception as e:
            self.logger.error(f"Error parsing {msg_type} message: {e}")
            return []

    async def _parse_fuel_event(self, parts: List[str], device_id: str, msg_type: str) -> List[TelemetryData]:
        """
        Parse FLF (Fuel Fill) or FLD (Fuel Drain) message.

        Format: $,token,FLF/FLD,dev,trip,timestamp,before_fuel,after_fuel,amount,lat,lon,#?
        """
        try:
            if len(parts) < 11:
                return []

            timestamp = self._parse_timestamp(parts[5])
            fuel_before = float(parts[6]) if parts[6] else None
            fuel_after = float(parts[7]) if parts[7] else None
            fuel_amount = float(parts[8]) if parts[8] else None
            latitude = float(parts[9])
            longitude = float(parts[10])

            io_elements = {
                "event_type": "fuel_fill" if msg_type == "FLF" else "fuel_drain",
                "fuel_before": fuel_before,
                "fuel_after": fuel_after,
                "fuel_amount": fuel_amount,
                # fuel_level = current level after the event (used by gps_locations trigger)
                "fuel_level": fuel_after,
            }

            return [TelemetryData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                protocol="tfms90",
                message_type=msg_type,
                io_elements=io_elements,
            )]

        except Exception as e:
            self.logger.error(f"Error parsing {msg_type} message: {e}")
            return []

    async def _parse_status(self, parts: List[str], device_id: str, msg_type: str) -> List[TelemetryData]:
        """Parse HB (Heartbeat), OS3 (Overspeed), or STAT (Status) message."""
        try:
            if len(parts) < 8:
                return []

            timestamp = self._parse_timestamp(parts[5]) if len(parts) > 5 else datetime.utcnow()

            io_elements = {
                "status_type": msg_type.lower(),
            }

            return [TelemetryData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=0.0,
                longitude=0.0,
                protocol="tfms90",
                message_type=msg_type,
                io_elements=io_elements,
            )]

        except Exception as e:
            self.logger.error(f"Error parsing {msg_type} message: {e}")
            return []

    def parse_login_message(self, data: bytes) -> Optional[dict]:
        """
        Parse LG (Login) message and extract device information.

        Format: $,0,LG,<IMEI>,<firmware_version>,<sim_iccid>,#?
        Example: $,0,LG,867762040399039,2.0.1,89970000000000000000,#?

        Returns dict with: imei, firmware_version, sim_iccid
        """
        try:
            text = data.decode('ascii').strip()
            if not text.startswith('$'):
                return None

            parts = text.split(',')
            if len(parts) < 6:
                return None

            msg_type = parts[2].upper()
            if msg_type != 'LG':
                return None

            login_data = {
                'imei': parts[3],
                'firmware_version': parts[4] if len(parts) > 4 else None,
                'sim_iccid': parts[5] if len(parts) > 5 else None,
            }

            self.logger.info(f"Parsed LG message: IMEI={login_data['imei']}, FW={login_data['firmware_version']}")
            return login_data

        except Exception as e:
            self.logger.error(f"Error parsing LG message: {e}")
            return None

    def _parse_timestamp(self, timestamp_hex: str) -> datetime:
        """Convert hex timestamp to datetime (seconds since 2000-01-01)."""
        try:
            seconds_since_2000 = int(timestamp_hex, 16)
            epoch_2000 = datetime(2000, 1, 1)
            from datetime import timedelta
            return epoch_2000 + timedelta(seconds=seconds_since_2000)
        except:
            return datetime.utcnow()

    def create_response(self, num_records: int, **kwargs) -> bytes:
        """
        Create TFMS90 acknowledgment.

        For LG (Login): $,0,ACK,<short_device_id>,#?
        For data messages: $,<token>,ACK,<device_id>,<num_records>,#?
        """
        try:
            msg_type = kwargs.get('msg_type', 'TD')
            device_id = kwargs.get('device_id', '000')
            token = kwargs.get('token', '0')

            if msg_type == 'LG':
                # Login ACK: just send back the assigned short_device_id
                ack = f"$,0,ACK,{device_id},#?\n"
                self.logger.info(f"Created LG ACK with short_device_id: {device_id}")
            else:
                # Data ACK: include number of records
                ack = f"$,{token},ACK,{device_id},{num_records},#?\n"
                self.logger.debug(f"Created TFMS90 ACK: {ack.strip()}")

            return ack.encode('ascii')

        except Exception as e:
            self.logger.error(f"Error creating TFMS90 response: {e}")
            return b"$,0,ACK,000,0,#?\n"
