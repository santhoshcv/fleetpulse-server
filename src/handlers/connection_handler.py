"""TCP connection handler for GPS devices."""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from src.handlers.protocol_router import ProtocolRouter
from src.adapters.base import ProtocolAdapter
from src.utils.database import db_client
from src.models.device import Device

logger = logging.getLogger(__name__)

# Hardcoded settings
BUFFER_SIZE = 4096


class ConnectionHandler:
    """Handles individual device TCP connections."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Initialize connection handler.

        Args:
            reader: Asyncio stream reader
            writer: Asyncio stream writer
        """
        self.reader = reader
        self.writer = writer
        self.device_id: Optional[str] = None
        self.protocol: Optional[str] = None
        self.adapter: Optional[ProtocolAdapter] = None
        self.router = ProtocolRouter()
        self.logger = logger
        self.addr = writer.get_extra_info('peername')
        self.is_authenticated = False

    async def handle(self):
        """Main connection handling loop."""
        try:
            self.logger.info(f"New connection from {self.addr}")

            # Read initial data to detect protocol and authenticate
            data = await self.reader.read(BUFFER_SIZE)

            self.logger.info(f"Received {len(data)} bytes from {self.addr}")
            self.logger.info(f"Raw data (hex): {data[:100].hex()}")
            try:
                self.logger.info(f"Data as text: {data[:200].decode('ascii', errors='ignore')}")
            except:
                pass

            if not data:
                self.logger.warning(f"No data received from {self.addr}")
                return

            # Detect protocol
            self.protocol = self.router.detect_protocol(data)

            if not self.protocol:
                self.logger.error(f"Failed to detect protocol from {self.addr}")
                return

            # Get appropriate adapter
            self.adapter = self.router.get_adapter(self.protocol)

            if not self.adapter:
                self.logger.error(f"No adapter found for protocol: {self.protocol}")
                return

            # Authenticate device (extract device ID)
            self.device_id = self.adapter.identify_device(data)

            if not self.device_id:
                self.logger.error(f"Failed to identify device from {self.addr}")
                return

            self.logger.info(f"Device {self.device_id} connected using {self.protocol} protocol")
            self.is_authenticated = True

            # Handle TFMS90 LG (Login) message specially
            if self.protocol == 'tfms90' and 'IMEI_' in self.device_id:
                # This is an LG message with IMEI
                login_data = self.adapter.parse_login_message(data)

                if login_data:
                    imei = login_data['imei']

                    # Assign or retrieve short_device_id
                    short_id = await db_client.assign_short_device_id(imei, self.protocol)

                    # Register device with both IMEI and short_device_id
                    await self._register_tfms90_device(imei, short_id, login_data)

                    # Send LG ACK with short_device_id
                    ack = self.adapter.create_response(
                        0,
                        msg_type='LG',
                        device_id=str(short_id),
                        token='0'
                    )
                    self.writer.write(ack)
                    await self.writer.drain()
                    self.logger.info(f"Sent LG ACK with short_device_id={short_id} to IMEI {imei}")

                    # Read next message (should be data message with short_device_id)
                    data = await self.reader.read(BUFFER_SIZE)

                    # Re-identify device with short_device_id
                    self.device_id = self.adapter.identify_device(data)

            # Register/update device in database (for non-LG messages or after LG)
            await self._register_device()

            # Send initial acknowledgment based on protocol
            if self.protocol == 'teltonika':
                # Send IMEI ACK: 0x01 (accepted)
                self.writer.write(b'\x01')
                await self.writer.drain()
                self.logger.info(f"Sent IMEI acknowledgment to {self.device_id}")

                # Read actual data packet
                data = await self.reader.read(BUFFER_SIZE)

            # Process the initial data (for TFMS90, this is the first data; for Teltonika, this is after IMEI ACK)
            await self._process_data(data)

            # Main loop for subsequent messages
            while True:
                data = await self.reader.read(BUFFER_SIZE)

                if not data:
                    self.logger.info(f"Connection closed by device {self.device_id}")
                    break

                await self._process_data(data)

        except asyncio.CancelledError:
            self.logger.info(f"Connection cancelled for device {self.device_id}")
        except Exception as e:
            self.logger.error(f"Error handling connection from {self.addr}: {e}")
        finally:
            await self._close_connection()

    async def _process_data(self, data: bytes):
        """
        Process received data packet.

        Args:
            data: Raw bytes from device
        """
        try:
            if not self.adapter or not self.device_id:
                return

            # Parse data using protocol adapter
            telemetry_records = await self.adapter.parse(data, self.device_id)

            if telemetry_records:
                self.logger.info(f"Parsed {len(telemetry_records)} records from {self.device_id}")

                # Store telemetry in database
                await self._store_telemetry(telemetry_records)

                # Update device last_seen
                await db_client.update_device_last_seen(self.device_id)

                # Send acknowledgment based on protocol
                if self.protocol == 'tfms90' and telemetry_records:
                    # Extract message type and token from raw data for TFMS90 ACK
                    msg_type = telemetry_records[0].message_type
                    io_elem = telemetry_records[0].io_elements or {}
                    token = io_elem.get("trip_number", 0)
                    short_id = io_elem.get("short_device_id", "")

                    ack = self.adapter.create_response(
                        len(telemetry_records),
                        msg_type=msg_type,
                        device_id=short_id,
                        token=str(token)
                    )
                    if ack:
                        self.writer.write(ack)
                        await self.writer.drain()
                        self.logger.debug(f"Sent TFMS90 ACK to {self.device_id}")

                elif self.protocol == 'teltonika' and telemetry_records:
                    # Teltonika ACK: 4 bytes with number of records
                    ack = self.adapter.create_response(len(telemetry_records))
                    if ack:
                        self.writer.write(ack)
                        await self.writer.drain()
                        self.logger.debug(f"Sent Teltonika ACK to {self.device_id}: {len(telemetry_records)} records")

        except Exception as e:
            self.logger.error(f"Error processing data from {self.device_id}: {e}")

    async def _register_tfms90_device(self, imei: str, short_id: int, login_data: dict):
        """Register TFMS90 device with IMEI and short_device_id."""
        try:
            # Check if device with this IMEI already exists (pre-registered in portal)
            existing_device = await db_client.get_device_by_imei(imei)

            if not existing_device:
                # Device not pre-registered - reject connection
                self.logger.error(f"TFMS90 device with IMEI={imei} not found in database. Device must be pre-registered in portal before connecting.")
                return

            # Update existing device with short_device_id and login details
            device_data = {
                "device_id": f"TFMS90_{short_id}",
                "short_device_id": short_id,
                "protocol": self.protocol,
                "firmware_version": login_data.get('firmware_version'),
                "sim_iccid": login_data.get('sim_iccid'),
                "last_seen": datetime.utcnow().isoformat(),
                "is_active": True,
            }

            # Update by UUID id (not by device_id, since device_id is changing)
            device_uuid = existing_device['id']
            self.logger.info(f"Updating existing TFMS90 device: IMEI={imei}, UUID={device_uuid}, short_id={short_id}")
            await db_client.update_device_by_uuid(device_uuid, device_data)

        except Exception as e:
            self.logger.error(f"Error registering TFMS90 device {imei}: {e}")

    async def _register_device(self):
        """Register or update device in database."""
        try:
            # Check if device exists
            existing_device = await db_client.get_device(self.device_id)

            device_data = {
                "device_id": self.device_id,
                "protocol": self.protocol,
                "last_seen": datetime.utcnow().isoformat(),
                "is_active": True,
            }

            if not existing_device:
                # New device
                device_data["created_at"] = datetime.utcnow().isoformat()
                self.logger.info(f"Registering new device: {self.device_id}")

            await db_client.upsert_device(device_data)

        except Exception as e:
            self.logger.error(f"Error registering device {self.device_id}: {e}")

    async def _store_telemetry(self, telemetry_records):
        """
        Store telemetry records in database.

        Args:
            telemetry_records: List of TelemetryData objects
        """
        try:
            # Convert to dictionaries
            telemetry_dicts = [record.to_dict() for record in telemetry_records]

            # Batch insert
            if len(telemetry_dicts) == 1:
                await db_client.insert_telemetry(telemetry_dicts[0])
            else:
                await db_client.insert_telemetry_batch(telemetry_dicts)

            self.logger.info(f"Stored {len(telemetry_dicts)} telemetry records for {self.device_id}")

        except Exception as e:
            self.logger.error(f"Error storing telemetry for {self.device_id}: {e}")

    async def _close_connection(self):
        """Close the connection gracefully."""
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
            self.logger.info(f"Connection closed for device {self.device_id or self.addr}")
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")
