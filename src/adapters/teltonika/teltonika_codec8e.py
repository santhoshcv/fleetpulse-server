"""Teltonika Codec 8E Protocol Adapter."""

import logging
import struct
from typing import List, Optional
from datetime import datetime
from src.adapters.base import ProtocolAdapter
from src.models.telemetry import TelemetryData

logger = logging.getLogger(__name__)


class TeltonikaCodec8EAdapter(ProtocolAdapter):
    """Adapter for Teltonika Codec 8 Extended protocol."""

    def __init__(self):
        """Initialize Teltonika adapter."""
        self.logger = logger

    def identify_device(self, data: bytes) -> Optional[str]:
        """
        Extract IMEI from Teltonika initial packet.

        Initial packet format: [2 bytes IMEI length][IMEI string]
        Example: 0x00 0x0F followed by 15-digit IMEI
        """
        try:
            if len(data) < 2:
                return None

            # First packet is IMEI
            imei_len = struct.unpack('>H', data[0:2])[0]

            if imei_len < 10 or imei_len > 20 or len(data) < 2 + imei_len:
                return None

            imei = data[2:2 + imei_len].decode('ascii')

            if imei.isdigit():
                self.logger.info(f"Identified Teltonika device: {imei}")
                return imei

            return None

        except Exception as e:
            self.logger.error(f"Error identifying Teltonika device: {e}")
            return None

    async def parse(self, data: bytes, device_id: str) -> List[TelemetryData]:
        """
        Parse Teltonika Codec 8E data packet.

        Packet structure:
        [4 bytes: Preamble (0x00000000)]
        [4 bytes: Data length]
        [1 byte: Codec ID (0x8E for Codec 8E)]
        [1 byte: Number of records]
        [AVL Data Records]
        [1 byte: Number of records (repeat)]
        [4 bytes: CRC16]
        """
        try:
            self.logger.info(f"Parsing Teltonika packet: {len(data)} bytes")

            if len(data) < 12:
                self.logger.warning("Packet too short")
                return []

            # Parse header
            offset = 0

            # Skip preamble (4 bytes of zeros)
            preamble = struct.unpack('>I', data[offset:offset + 4])[0]
            offset += 4

            if preamble != 0:
                self.logger.warning(f"Invalid preamble: {preamble}")
                # Sometimes preamble is missing, try without it
                offset = 0

            # Data length
            data_length = struct.unpack('>I', data[offset:offset + 4])[0]
            offset += 4

            self.logger.info(f"Data length: {data_length}")

            # Codec ID
            codec_id = data[offset]
            offset += 1

            if codec_id not in [0x08, 0x8E]:
                self.logger.warning(f"Unsupported codec ID: {codec_id:#x}")
                return []

            self.logger.info(f"Codec ID: {codec_id:#x}")

            # Number of records
            num_records = data[offset]
            offset += 1

            self.logger.info(f"Number of records: {num_records}")

            # Parse AVL records
            telemetry_records = []

            for i in range(num_records):
                try:
                    record, offset = self._parse_avl_record(data, offset, device_id, codec_id)
                    if record:
                        telemetry_records.append(record)
                        self.logger.info(f"Parsed record {i + 1}/{num_records}")
                except Exception as e:
                    self.logger.error(f"Error parsing record {i + 1}: {e}")
                    break

            return telemetry_records

        except Exception as e:
            self.logger.error(f"Error parsing Teltonika data: {e}")
            return []

    def _parse_avl_record(self, data: bytes, offset: int, device_id: str, codec_id: int) -> tuple:
        """
        Parse single AVL data record.

        Record structure:
        [8 bytes: Timestamp (milliseconds since 1970-01-01)]
        [1 byte: Priority]
        [GPS Element]
        [IO Element]
        """
        try:
            # Timestamp (8 bytes)
            timestamp_ms = struct.unpack('>Q', data[offset:offset + 8])[0]
            offset += 8
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0)

            # Priority
            priority = data[offset]
            offset += 1

            # GPS Element
            gps_data, offset = self._parse_gps_element(data, offset)

            # IO Element
            io_data, offset = self._parse_io_element(data, offset, codec_id)

            # Create telemetry record
            telemetry = TelemetryData(
                device_id=device_id,
                timestamp=timestamp,
                latitude=gps_data['latitude'],
                longitude=gps_data['longitude'],
                altitude=gps_data['altitude'],
                speed=gps_data['speed'],
                heading=gps_data['angle'],
                satellites=gps_data['satellites'],
                protocol="teltonika",
                message_type=f"codec_{codec_id:#x}",
                io_elements=io_data,
            )

            return telemetry, offset

        except Exception as e:
            self.logger.error(f"Error parsing AVL record: {e}")
            return None, offset

    def _parse_gps_element(self, data: bytes, offset: int) -> tuple:
        """
        Parse GPS element.

        Structure:
        [4 bytes: Longitude]
        [4 bytes: Latitude]
        [2 bytes: Altitude]
        [2 bytes: Angle]
        [1 byte: Satellites]
        [2 bytes: Speed]
        """
        try:
            longitude = struct.unpack('>i', data[offset:offset + 4])[0] / 10000000.0
            offset += 4

            latitude = struct.unpack('>i', data[offset:offset + 4])[0] / 10000000.0
            offset += 4

            altitude = struct.unpack('>H', data[offset:offset + 2])[0]
            offset += 2

            angle = struct.unpack('>H', data[offset:offset + 2])[0]
            offset += 2

            satellites = data[offset]
            offset += 1

            speed = struct.unpack('>H', data[offset:offset + 2])[0]
            offset += 2

            gps_data = {
                'latitude': latitude,
                'longitude': longitude,
                'altitude': altitude,
                'angle': angle,
                'satellites': satellites,
                'speed': speed,
            }

            return gps_data, offset

        except Exception as e:
            self.logger.error(f"Error parsing GPS element: {e}")
            return {}, offset

    def _parse_io_element(self, data: bytes, offset: int, codec_id: int) -> tuple:
        """
        Parse IO element.

        Structure varies by Codec ID:
        - Codec 8: Event ID (1 byte), Total IO count, then IO elements
        - Codec 8E: Event ID (2 bytes), Total IO count, then IO elements
        """
        try:
            io_data = {}

            # Event IO ID
            if codec_id == 0x8E:
                event_id = struct.unpack('>H', data[offset:offset + 2])[0]
                offset += 2
            else:
                event_id = data[offset]
                offset += 1

            io_data['event_id'] = event_id

            # Total IO elements count
            total_io = data[offset]
            offset += 1

            # Parse IO elements by size (1, 2, 4, 8 bytes)
            for io_size in [1, 2, 4, 8]:
                count = data[offset]
                offset += 1

                for _ in range(count):
                    if codec_id == 0x8E:
                        io_id = struct.unpack('>H', data[offset:offset + 2])[0]
                        offset += 2
                    else:
                        io_id = data[offset]
                        offset += 1

                    # Read value based on size
                    if io_size == 1:
                        value = data[offset]
                    elif io_size == 2:
                        value = struct.unpack('>H', data[offset:offset + 2])[0]
                    elif io_size == 4:
                        value = struct.unpack('>I', data[offset:offset + 4])[0]
                    elif io_size == 8:
                        value = struct.unpack('>Q', data[offset:offset + 8])[0]

                    offset += io_size

                    # Map common IO IDs to readable names
                    io_name = self._get_io_name(io_id)
                    io_data[io_name] = value

            return io_data, offset

        except Exception as e:
            self.logger.error(f"Error parsing IO element: {e}")
            return {}, offset

    def _get_io_name(self, io_id: int) -> str:
        """Map IO ID to readable name."""
        io_map = {
            1: 'digital_input_1',
            9: 'analog_input_1',
            66: 'external_voltage',
            67: 'battery_voltage',
            68: 'battery_current',
            69: 'gnss_status',
            80: 'data_mode',
            181: 'gnss_pdop',
            182: 'gnss_hdop',
            239: 'ignition',
            240: 'movement',
            241: 'gsm_signal',
            # Add more as needed
        }
        return io_map.get(io_id, f'io_{io_id}')

    def create_response(self, num_records: int, **kwargs) -> bytes:
        """
        Create Teltonika acknowledgment.

        Response format: [4 bytes: Number of records received]
        """
        try:
            ack = struct.pack('>I', num_records)
            self.logger.debug(f"Created Teltonika ACK: {num_records} records")
            return ack
        except Exception as e:
            self.logger.error(f"Error creating Teltonika response: {e}")
            return b'\x00\x00\x00\x00'
