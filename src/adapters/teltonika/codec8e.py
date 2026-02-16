"""Teltonika Codec 8E protocol parser for FMB920/FMA120 devices."""

import struct
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from src.adapters.base import ProtocolAdapter
from src.models.telemetry import TelemetryData

logger = logging.getLogger(__name__)


class TeltonikaCodec8EAdapter(ProtocolAdapter):
    """
    Teltonika Codec 8E protocol adapter.

    Supports FMB920, FMA120 and other Teltonika devices using Codec 8/8E.

    Protocol structure:
    - Preamble: 4 bytes (0x00000000)
    - Data field length: 4 bytes
    - Codec ID: 1 byte (0x08 or 0x8E)
    - Number of records: 1 byte
    - AVL data records
    - Number of records: 1 byte (same as before)
    - CRC-16: 4 bytes
    """

    CODEC_8 = 0x08
    CODEC_8E = 0x8E

    def __init__(self):
        """Initialize Teltonika adapter."""
        self.logger = logger

    async def parse(self, data: bytes, device_id: str) -> List[TelemetryData]:
        """
        Parse Teltonika Codec 8E data packet.

        Args:
            data: Raw bytes from device
            device_id: IMEI of the device

        Returns:
            List of parsed telemetry records
        """
        try:
            # Skip preamble (4 bytes of 0x00)
            offset = 0
            preamble = struct.unpack(">I", data[offset:offset + 4])[0]
            offset += 4

            if preamble != 0:
                self.logger.warning(f"Invalid preamble: {preamble:08x}")

            # Data field length
            data_length = struct.unpack(">I", data[offset:offset + 4])[0]
            offset += 4

            # Codec ID
            codec_id = data[offset]
            offset += 1

            if codec_id not in [self.CODEC_8, self.CODEC_8E]:
                raise ValueError(f"Unsupported codec ID: {codec_id:02x}")

            # Number of records
            num_records = data[offset]
            offset += 1

            self.logger.info(f"Parsing {num_records} records from device {device_id} (Codec {codec_id:02x})")

            # Parse AVL records
            telemetry_records = []
            for i in range(num_records):
                record, offset = self._parse_avl_record(data, offset, device_id, codec_id)
                if record:
                    telemetry_records.append(record)

            # Verify number of records matches
            num_records_end = data[offset]
            offset += 1

            if num_records != num_records_end:
                self.logger.warning(f"Record count mismatch: {num_records} vs {num_records_end}")

            # CRC-16 (skip validation for now)
            crc = struct.unpack(">I", data[offset:offset + 4])[0]
            offset += 4

            self.logger.info(f"Successfully parsed {len(telemetry_records)} telemetry records")
            return telemetry_records

        except Exception as e:
            self.logger.error(f"Error parsing Teltonika data: {e}")
            return []

    def _parse_avl_record(
        self,
        data: bytes,
        offset: int,
        device_id: str,
        codec_id: int
    ) -> Tuple[Optional[TelemetryData], int]:
        """
        Parse a single AVL data record.

        Args:
            data: Full data packet
            offset: Current offset in packet
            device_id: Device IMEI
            codec_id: Codec identifier

        Returns:
            Tuple of (TelemetryData, new_offset)
        """
        try:
            # Timestamp (8 bytes, milliseconds since 2000-01-01 00:00:00 UTC)
            timestamp_ms = struct.unpack(">Q", data[offset:offset + 8])[0]
            offset += 8
            timestamp = datetime.utcfromtimestamp(946684800 + timestamp_ms / 1000.0)

            # Priority (1 byte)
            priority = data[offset]
            offset += 1

            # GPS Element (15 bytes)
            longitude = struct.unpack(">i", data[offset:offset + 4])[0] / 10000000.0
            offset += 4

            latitude = struct.unpack(">i", data[offset:offset + 4])[0] / 10000000.0
            offset += 4

            altitude = struct.unpack(">h", data[offset:offset + 2])[0]
            offset += 2

            angle = struct.unpack(">H", data[offset:offset + 2])[0]
            offset += 2

            satellites = data[offset]
            offset += 1

            speed = struct.unpack(">H", data[offset:offset + 2])[0]
            offset += 2

            # IO Element
            io_elements, offset = self._parse_io_element(data, offset, codec_id)

            # Create telemetry record
            telemetry = TelemetryData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                altitude=float(altitude) if altitude != 0 else None,
                speed=float(speed) if speed > 0 else None,
                heading=angle if angle <= 360 else None,
                satellites=satellites if satellites > 0 else None,
                io_elements=io_elements,
                protocol="teltonika",
                message_type=f"codec_{codec_id:02x}",
            )

            # Extract common IO elements
            self._extract_io_data(telemetry, io_elements)

            return telemetry, offset

        except Exception as e:
            self.logger.error(f"Error parsing AVL record: {e}")
            return None, offset

    def _parse_io_element(
        self,
        data: bytes,
        offset: int,
        codec_id: int
    ) -> Tuple[dict, int]:
        """
        Parse IO element section.

        Args:
            data: Full data packet
            offset: Current offset
            codec_id: Codec identifier

        Returns:
            Tuple of (io_dict, new_offset)
        """
        io_dict = {}

        try:
            # Event IO ID (Codec 8E only)
            if codec_id == self.CODEC_8E:
                event_io_id = struct.unpack(">H", data[offset:offset + 2])[0]
                offset += 2
                io_dict["event_io_id"] = event_io_id
            else:
                event_io_id = data[offset]
                offset += 1
                io_dict["event_io_id"] = event_io_id

            # Total IO count (Codec 8E uses 2 bytes)
            if codec_id == self.CODEC_8E:
                total_io = struct.unpack(">H", data[offset:offset + 2])[0]
                offset += 2
            else:
                total_io = data[offset]
                offset += 1

            # Parse different IO element sizes
            # 1-byte IO elements
            offset = self._parse_io_group(data, offset, io_dict, 1, codec_id)

            # 2-byte IO elements
            offset = self._parse_io_group(data, offset, io_dict, 2, codec_id)

            # 4-byte IO elements
            offset = self._parse_io_group(data, offset, io_dict, 4, codec_id)

            # 8-byte IO elements
            offset = self._parse_io_group(data, offset, io_dict, 8, codec_id)

            # Variable length IO elements (Codec 8E only)
            if codec_id == self.CODEC_8E:
                offset = self._parse_io_group_variable(data, offset, io_dict)

        except Exception as e:
            self.logger.error(f"Error parsing IO elements: {e}")

        return io_dict, offset

    def _parse_io_group(
        self,
        data: bytes,
        offset: int,
        io_dict: dict,
        value_size: int,
        codec_id: int
    ) -> int:
        """Parse a group of IO elements of fixed size."""
        try:
            # Number of elements (2 bytes for Codec 8E, 1 byte for Codec 8)
            if codec_id == self.CODEC_8E:
                count = struct.unpack(">H", data[offset:offset + 2])[0]
                offset += 2
            else:
                count = data[offset]
                offset += 1

            for _ in range(count):
                # IO ID (2 bytes for Codec 8E, 1 byte for Codec 8)
                if codec_id == self.CODEC_8E:
                    io_id = struct.unpack(">H", data[offset:offset + 2])[0]
                    offset += 2
                else:
                    io_id = data[offset]
                    offset += 1

                # IO Value
                if value_size == 1:
                    value = data[offset]
                elif value_size == 2:
                    value = struct.unpack(">H", data[offset:offset + 2])[0]
                elif value_size == 4:
                    value = struct.unpack(">I", data[offset:offset + 4])[0]
                elif value_size == 8:
                    value = struct.unpack(">Q", data[offset:offset + 8])[0]
                else:
                    value = 0

                offset += value_size
                io_dict[f"io_{io_id}"] = value

        except Exception as e:
            self.logger.error(f"Error parsing IO group: {e}")

        return offset

    def _parse_io_group_variable(self, data: bytes, offset: int, io_dict: dict) -> int:
        """Parse variable-length IO elements (Codec 8E only)."""
        try:
            # Number of variable-length elements
            count = struct.unpack(">H", data[offset:offset + 2])[0]
            offset += 2

            for _ in range(count):
                # IO ID
                io_id = struct.unpack(">H", data[offset:offset + 2])[0]
                offset += 2

                # Value length
                value_length = struct.unpack(">H", data[offset:offset + 2])[0]
                offset += 2

                # Value
                value = data[offset:offset + value_length]
                offset += value_length

                io_dict[f"io_{io_id}_var"] = value.hex()

        except Exception as e:
            self.logger.error(f"Error parsing variable IO group: {e}")

        return offset

    def _extract_io_data(self, telemetry: TelemetryData, io_elements: dict):
        """Extract common IO elements into telemetry fields."""
        # Common Teltonika IO IDs
        IO_IGNITION = "io_239"  # Digital Input 1 (often ignition)
        IO_MOVEMENT = "io_240"  # Movement sensor
        IO_ODOMETER = "io_16"  # Total odometer
        IO_BATTERY_VOLTAGE = "io_67"  # Battery voltage
        IO_EXTERNAL_VOLTAGE = "io_66"  # External voltage
        IO_FUEL_LEVEL = "io_70"  # Fuel level (if connected)
        IO_ENGINE_HOURS = "io_15"  # Engine hours

        # Ignition status
        if IO_IGNITION in io_elements:
            telemetry.ignition = bool(io_elements[IO_IGNITION])

        # Movement status
        if IO_MOVEMENT in io_elements:
            telemetry.moving = bool(io_elements[IO_MOVEMENT])

        # Battery voltage (mV to V)
        if IO_BATTERY_VOLTAGE in io_elements:
            telemetry.battery_voltage = io_elements[IO_BATTERY_VOLTAGE] / 1000.0

        # Odometer (meters to km)
        if IO_ODOMETER in io_elements:
            telemetry.odometer = io_elements[IO_ODOMETER] / 1000.0

        # Fuel level
        if IO_FUEL_LEVEL in io_elements:
            telemetry.fuel_level = float(io_elements[IO_FUEL_LEVEL])

        # Engine hours (seconds to hours)
        if IO_ENGINE_HOURS in io_elements:
            telemetry.engine_hours = io_elements[IO_ENGINE_HOURS] / 3600.0

    def create_response(self, record_count: int) -> bytes:
        """
        Create ACK response for Teltonika device.

        Args:
            record_count: Number of records received

        Returns:
            4-byte acknowledgment
        """
        return struct.pack(">I", record_count)

    def identify_device(self, data: bytes) -> Optional[str]:
        """
        Extract IMEI from initial connection packet.

        Teltonika devices send IMEI in first packet:
        - 2 bytes: IMEI length
        - N bytes: IMEI (ASCII string)

        Args:
            data: Initial connection bytes

        Returns:
            IMEI string or None
        """
        try:
            if len(data) < 2:
                return None

            imei_length = struct.unpack(">H", data[0:2])[0]

            if imei_length > 0 and len(data) >= 2 + imei_length:
                imei = data[2:2 + imei_length].decode('ascii')
                self.logger.info(f"Identified Teltonika device: {imei}")
                return imei

        except Exception as e:
            self.logger.error(f"Error identifying device: {e}")

        return None
