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

        Format: $,<token>,<msg_type>,<device_id>,<trip_number>,<timestamp>,<payload>,#?
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
            # parts[3] = device_id
            device_id = parts[3]

            if device_id:
                self.logger.info(f"Identified TFMS90 device: {device_id}")
                return f"TFMS90_{device_id}"

            return None

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
            if msg_type == 'TD' or msg_type == 'TDA':
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

        Format after split: ['', token, 'TD', dev_id, trip_num, timestamp_hex, lat, lon, speed, heading, sats, fuel, odo, ...]
        Indices:             0    1      2      3        4           5            6    7     8       9       10    11    12
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
            fuel = float(parts[11]) if len(parts) > 11 and parts[11] else None
            odometer = float(parts[12]) if len(parts) > 12 and parts[12] else None

            io_elements = {
                "trip_number": parts[4],
                "short_device_id": parts[3],
                "fuel_level": fuel,
                "odometer": odometer,
            }

            telemetry = TelemetryData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading,
                satellites=satellites,
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
        """Parse TS (Trip Start) or TE (Trip End) message."""
        try:
            if len(parts) < 11:
                return []

            timestamp = self._parse_timestamp(parts[5])
            latitude = float(parts[6])
            longitude = float(parts[7])

            io_elements = {
                "trip_number": parts[4],
                "short_device_id": parts[3],
                "event_type": "trip_start" if msg_type == "TS" else "trip_end",
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
                "trip_number": parts[4],
                "short_device_id": parts[3],
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
        """Parse FLF (Fuel Fill) or FLD (Fuel Drain) message."""
        try:
            if len(parts) < 12:
                return []

            timestamp = self._parse_timestamp(parts[5])
            latitude = float(parts[6])
            longitude = float(parts[7])
            fuel_level = float(parts[11]) if parts[11] else None

            io_elements = {
                "trip_number": parts[4],
                "short_device_id": parts[3],
                "event_type": "fuel_fill" if msg_type == "FLF" else "fuel_drain",
                "fuel_level": fuel_level,
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
                "short_device_id": parts[3],
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

        Format: $,<token>,ACK,<device_id>,<num_records>,#?
        """
        try:
            msg_type = kwargs.get('msg_type', 'TD')
            device_id = kwargs.get('device_id', '000')
            token = kwargs.get('token', '0')

            ack = f"$,{token},ACK,{device_id},{num_records},#?\n"
            self.logger.debug(f"Created TFMS90 ACK: {ack.strip()}")
            return ack.encode('ascii')

        except Exception as e:
            self.logger.error(f"Error creating TFMS90 response: {e}")
            return b"$,0,ACK,000,0,#?\n"
