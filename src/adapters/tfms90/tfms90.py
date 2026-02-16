"""TFMS90 Protocol v2.0 Parser - Text-based TCP protocol."""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from src.adapters.base import ProtocolAdapter
from src.models.telemetry import TelemetryData

logger = logging.getLogger(__name__)


class TFMS90Adapter(ProtocolAdapter):
    """
    TFMS90 Protocol v2.0 Adapter.

    Message format: $,<token>,<msg_type>,<device_id>,<trip_number>,<timestamp_hex>,<payload>,#?
    Port: 23000
    Timestamp: Hex format (seconds since 2000-01-01 00:00:00 UTC)
    """

    # Epoch for TFMS90 timestamps (2000-01-01 00:00:00 UTC)
    EPOCH_2000 = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    MESSAGE_HANDLERS = {
        'LG': '_parse_login',
        'TD': '_parse_tracking_data',
        'TDA': '_parse_tracking_data',  # Same as TD with additional data
        'TS': '_parse_trip_start',
        'TE': '_parse_trip_end',
        'STAT': '_parse_trip_stats',
        'HA2': '_parse_harsh_accel',
        'HB2': '_parse_harsh_brake',
        'HC2': '_parse_harsh_corner',
        'OS3': '_parse_overspeed',
        'FLF': '_parse_fuel_fill',
        'FLD': '_parse_fuel_drain',
        'FCR': '_parse_fuel_consumption',
        'HB': '_parse_heartbeat',
        'DHR': '_parse_device_health',
        'ERR': '_parse_error',
        'GEO': '_parse_geofence',
        'DID': '_parse_driver_id',
        'TMP': '_parse_tamper',
    }

    def __init__(self):
        """Initialize TFMS90 adapter."""
        self.logger = logger
        self.device_imei_map = {}  # Maps device_id -> IMEI

    async def parse(self, data: bytes, device_id: str) -> List[TelemetryData]:
        """
        Parse TFMS90 v2.0 message.

        Format: $,<token>,<msg_type>,<device_id>,<trip_number>,<timestamp_hex>,<payload>,#?
        """
        try:
            message = data.decode('ascii').strip()
            self.logger.info(f"TFMS90 message: {message}")

            # Remove delimiters
            if message.startswith('$'):
                message = message[1:]
            if message.endswith('#?'):
                message = message[:-2]
            elif message.endswith('#'):
                message = message[:-1]

            parts = message.split(',')

            if len(parts) < 3:
                self.logger.warning(f"Invalid message format: {message}")
                return []

            token = parts[0]
            msg_type = parts[1]

            # Route to handler
            handler_name = self.MESSAGE_HANDLERS.get(msg_type)
            if handler_name:
                handler = getattr(self, handler_name, None)
                if handler:
                    telemetry = handler(parts, device_id)
                    if telemetry:
                        return [telemetry]
            else:
                self.logger.warning(f"Unknown message type: {msg_type}")

            return []

        except Exception as e:
            self.logger.error(f"Error parsing TFMS90 message: {e}")
            return []

    def _hex_to_timestamp(self, hex_str: str) -> datetime:
        """Convert hex timestamp to datetime (seconds since 2000-01-01)."""
        try:
            seconds = int(hex_str, 16)
            return self.EPOCH_2000 + timezone.timedelta(seconds=seconds)
        except:
            return datetime.now(timezone.utc)

    def _timestamp_to_hex(self, dt: datetime) -> str:
        """Convert datetime to hex timestamp."""
        seconds = int((dt - self.EPOCH_2000).total_seconds())
        return format(seconds, '08X')

    def _parse_login(self, parts: List[str], device_id: str) -> Optional[TelemetryData]:
        """
        Parse LG (Login) message.
        Format: $,0,LG,<device_id>,<imei>,<firmware_version>,<iccid>,#?
        """
        try:
            if len(parts) < 6:
                return None

            dev_id = parts[2]
            imei = parts[3]
            firmware = parts[4]
            iccid = parts[5]

            # Store IMEI mapping
            self.device_imei_map[dev_id] = imei

            self.logger.info(f"Device login: ID={dev_id}, IMEI={imei}, FW={firmware}")

            # Create a telemetry record for login event
            return TelemetryData(
                device_id=imei,  # Use IMEI as primary device_id
                timestamp=datetime.now(timezone.utc),
                latitude=0.0,
                longitude=0.0,
                protocol="tfms90",
                message_type="LG",
                io_elements={
                    "short_device_id": dev_id,
                    "firmware_version": firmware,
                    "iccid": iccid
                },
                raw_data=','.join(parts)
            )

        except Exception as e:
            self.logger.error(f"Error parsing LG: {e}")
            return None

    def _parse_tracking_data(self, parts: List[str], device_id: str) -> Optional[TelemetryData]:
        """
        Parse TD/TDA (Tracking Data) message.
        Format: $,0,TD,<device_id>,<trip_number>,<timestamp>,<lat>,<lon>,<speed>,<heading>,
                <satellites>,<hdop>,<fuel_level>,<odometer>,<digital_inputs>,<digital_outputs>,
                <analog1>,<voltage>,<gsm_signal>,#?
        """
        try:
            if len(parts) < 18:
                return None

            dev_id = parts[2]
            trip_number = int(parts[3])
            timestamp = self._hex_to_timestamp(parts[4])
            latitude = float(parts[5])
            longitude = float(parts[6])
            speed = int(parts[7]) if parts[7] else 0
            heading = int(parts[8]) if parts[8] else 0
            satellites = int(parts[9]) if parts[9] else 0
            hdop = float(parts[10]) if parts[10] else 0.0
            fuel_level = float(parts[11]) if parts[11] else 0.0
            odometer = int(parts[12]) if parts[12] else 0
            digital_inputs = parts[13]
            digital_outputs = parts[14]
            analog1 = float(parts[15]) if parts[15] else 0.0
            voltage = float(parts[16]) if parts[16] else 0.0
            gsm_signal = int(parts[17]) if parts[17] else 0

            # Get IMEI if available
            imei = self.device_imei_map.get(dev_id, dev_id)

            return TelemetryData(
                device_id=imei,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                speed=float(speed),
                heading=heading,
                satellites=satellites,
                hdop=hdop,
                fuel_level=fuel_level,
                odometer=odometer / 1000.0,  # meters to km
                battery_voltage=voltage,
                ignition=True,  # TD means ignition is ON
                moving=speed > 5,
                protocol="tfms90",
                message_type="TD",
                io_elements={
                    "short_device_id": dev_id,
                    "trip_number": trip_number,
                    "digital_inputs": digital_inputs,
                    "digital_outputs": digital_outputs,
                    "analog1": analog1,
                    "gsm_signal": gsm_signal
                },
                raw_data=','.join(parts)
            )

        except Exception as e:
            self.logger.error(f"Error parsing TD: {e}")
            return None

    def _parse_trip_start(self, parts: List[str], device_id: str) -> Optional[TelemetryData]:
        """
        Parse TS (Trip Start) message.
        Format: $,0,TS,<device_id>,<trip_number>,<timestamp>,<fuel_level>,<lat>,<lon>,<voltage>,#?
        """
        try:
            if len(parts) < 10:
                return None

            dev_id = parts[2]
            trip_number = int(parts[3])
            timestamp = self._hex_to_timestamp(parts[4])
            fuel_level = float(parts[5])
            latitude = float(parts[6])
            longitude = float(parts[7])
            voltage = float(parts[8])

            imei = self.device_imei_map.get(dev_id, dev_id)

            return TelemetryData(
                device_id=imei,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                fuel_level=fuel_level,
                battery_voltage=voltage,
                ignition=True,
                moving=True,
                protocol="tfms90",
                message_type="TS",
                io_elements={
                    "short_device_id": dev_id,
                    "trip_number": trip_number,
                    "event": "trip_start"
                },
                raw_data=','.join(parts)
            )

        except Exception as e:
            self.logger.error(f"Error parsing TS: {e}")
            return None

    def _parse_trip_end(self, parts: List[str], device_id: str) -> Optional[TelemetryData]:
        """
        Parse TE (Trip End) message.
        Format: $,0,TE,<device_id>,<trip_number>,<start_timestamp>,<end_timestamp>,<duration_sec>,
                <distance_m>,<start_fuel>,<end_fuel>,<fuel_consumed>,<max_speed>,<avg_speed>,
                <start_lat>,<start_lon>,<end_lat>,<end_lon>,<voltage>,#?
        """
        try:
            if len(parts) < 18:
                return None

            dev_id = parts[2]
            trip_number = int(parts[3])
            start_time = self._hex_to_timestamp(parts[4])
            end_time = self._hex_to_timestamp(parts[5])
            duration = int(parts[6])
            distance = int(parts[7])
            start_fuel = float(parts[8])
            end_fuel = float(parts[9])
            fuel_consumed = float(parts[10])
            max_speed = int(parts[11])
            avg_speed = int(parts[12])
            start_lat = float(parts[13])
            start_lon = float(parts[14])
            end_lat = float(parts[15])
            end_lon = float(parts[16])
            voltage = float(parts[17])

            imei = self.device_imei_map.get(dev_id, dev_id)

            return TelemetryData(
                device_id=imei,
                timestamp=end_time,
                latitude=end_lat,
                longitude=end_lon,
                fuel_level=end_fuel,
                battery_voltage=voltage,
                ignition=False,
                moving=False,
                protocol="tfms90",
                message_type="TE",
                io_elements={
                    "short_device_id": dev_id,
                    "trip_number": trip_number,
                    "event": "trip_end",
                    "start_time": start_time.isoformat(),
                    "duration_sec": duration,
                    "distance_m": distance,
                    "start_fuel": start_fuel,
                    "fuel_consumed": fuel_consumed,
                    "max_speed": max_speed,
                    "avg_speed": avg_speed,
                    "start_lat": start_lat,
                    "start_lon": start_lon
                },
                raw_data=','.join(parts)
            )

        except Exception as e:
            self.logger.error(f"Error parsing TE: {e}")
            return None

    def _parse_heartbeat(self, parts: List[str], device_id: str) -> Optional[TelemetryData]:
        """
        Parse HB (Heartbeat) message.
        Format: $,0,HB,<device_id>,<timestamp>,<fuel_level>,<voltage>,<gsm_signal>,
                <gps_fix>,<lat>,<lon>,<odometer>,<acc_status>,<sleep_mode>,#?
        """
        try:
            if len(parts) < 13:
                return None

            dev_id = parts[2]
            timestamp = self._hex_to_timestamp(parts[3])
            fuel_level = float(parts[4])
            voltage = float(parts[5])
            gsm_signal = int(parts[6])
            gps_fix = int(parts[7])
            latitude = float(parts[8])
            longitude = float(parts[9])
            odometer = int(parts[10])
            acc_status = int(parts[11])
            sleep_mode = int(parts[12])

            imei = self.device_imei_map.get(dev_id, dev_id)

            return TelemetryData(
                device_id=imei,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                fuel_level=fuel_level,
                battery_voltage=voltage,
                odometer=odometer / 1000.0,
                ignition=bool(acc_status),
                moving=False,
                protocol="tfms90",
                message_type="HB",
                io_elements={
                    "short_device_id": dev_id,
                    "gsm_signal": gsm_signal,
                    "gps_fix": gps_fix,
                    "sleep_mode": sleep_mode
                },
                raw_data=','.join(parts)
            )

        except Exception as e:
            self.logger.error(f"Error parsing HB: {e}")
            return None

    def _parse_fuel_fill(self, parts: List[str], device_id: str) -> Optional[TelemetryData]:
        """
        Parse FLF (Fuel Fill) message.
        Format: $,0,FLF,<device_id>,<trip_number>,<timestamp>,<volume>,
                <fuel_before>,<fuel_after>,<lat>,<lon>,#?
        """
        try:
            if len(parts) < 11:
                return None

            dev_id = parts[2]
            trip_number = int(parts[3])
            timestamp = self._hex_to_timestamp(parts[4])
            volume = float(parts[5])
            fuel_before = float(parts[6])
            fuel_after = float(parts[7])
            latitude = float(parts[8])
            longitude = float(parts[9])

            imei = self.device_imei_map.get(dev_id, dev_id)

            return TelemetryData(
                device_id=imei,
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                fuel_level=fuel_after,
                protocol="tfms90",
                message_type="FLF",
                io_elements={
                    "short_device_id": dev_id,
                    "trip_number": trip_number,
                    "event": "fuel_fill",
                    "volume": volume,
                    "fuel_before": fuel_before,
                    "fuel_after": fuel_after
                },
                raw_data=','.join(parts)
            )

        except Exception as e:
            self.logger.error(f"Error parsing FLF: {e}")
            return None

    def _parse_fuel_drain(self, parts: List[str], device_id: str) -> Optional[TelemetryData]:
        """Parse FLD (Fuel Drain) - same format as FLF."""
        telemetry = self._parse_fuel_fill(parts, device_id)
        if telemetry:
            telemetry.message_type = "FLD"
            if telemetry.io_elements:
                telemetry.io_elements["event"] = "fuel_drain"
        return telemetry

    # Stub handlers for other message types
    def _parse_trip_stats(self, parts, device_id): return None
    def _parse_harsh_accel(self, parts, device_id): return None
    def _parse_harsh_brake(self, parts, device_id): return None
    def _parse_harsh_corner(self, parts, device_id): return None
    def _parse_overspeed(self, parts, device_id): return None
    def _parse_fuel_consumption(self, parts, device_id): return None
    def _parse_device_health(self, parts, device_id): return None
    def _parse_error(self, parts, device_id): return None
    def _parse_geofence(self, parts, device_id): return None
    def _parse_driver_id(self, parts, device_id): return None
    def _parse_tamper(self, parts, device_id): return None

    def create_response(self, record_count: int, msg_type: str = "TD",
                       device_id: str = "", token: str = "0") -> bytes:
        """
        Create server ACK response for TFMS90 device.
        Format: $AK,<msg_type>,<device_id>,<token_or_trip>,#
        """
        # Messages that need ACK: LG, TS, TE, FLF, FLD, HA2, HB2, HC2, OS3, GEO, TMP, ERR
        ack_messages = ['LG', 'TS', 'TE', 'FLF', 'FLD', 'HA2', 'HB2', 'HC2', 'OS3', 'GEO', 'TMP', 'ERR']

        if msg_type in ack_messages:
            if msg_type == 'LG':
                # LG response includes server timestamp
                server_time = self._timestamp_to_hex(datetime.now(timezone.utc))
                response = f"$AK,LG,{device_id},{server_time},#"
            else:
                response = f"$AK,{msg_type},{device_id},{token},#"

            self.logger.info(f"Sending ACK: {response}")
            return response.encode('ascii')

        return b""  # No ACK for other messages

    def identify_device(self, data: bytes) -> Optional[str]:
        """
        Extract device ID from TFMS90 LG (Login) message.
        Format: $,0,LG,<device_id>,<imei>,<firmware_version>,<iccid>,#?
        """
        try:
            message = data.decode('ascii').strip()

            if ',LG,' in message:
                parts = message.split(',')
                if len(parts) >= 4:
                    # Return IMEI as the primary device identifier
                    imei = parts[4]
                    dev_id = parts[3]
                    self.device_imei_map[dev_id] = imei
                    self.logger.info(f"Identified TFMS90 device: short_id={dev_id}, IMEI={imei}")
                    return imei

        except Exception as e:
            self.logger.error(f"Error identifying TFMS90 device: {e}")

        return None
