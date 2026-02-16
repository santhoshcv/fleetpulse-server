"""Trip management business logic."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from src.utils.database import db_client
from src.models.trip import Trip
from src.models.telemetry import TelemetryData

logger = logging.getLogger(__name__)


class TripManager:
    """Manages trip detection and tracking."""

    def __init__(self):
        """Initialize trip manager."""
        self.logger = logger
        self.active_trips: Dict[str, str] = {}  # device_id -> trip_id

    async def process_telemetry(self, telemetry: TelemetryData):
        """
        Process telemetry for trip detection.

        Args:
            telemetry: Telemetry data
        """
        try:
            device_id = telemetry.device_id

            # Check if trip should start
            if self._should_start_trip(telemetry):
                await self._start_trip(telemetry)

            # Check if trip should end
            elif self._should_end_trip(telemetry):
                await self._end_trip(telemetry)

            # Update active trip
            elif device_id in self.active_trips:
                await self._update_trip(telemetry)

        except Exception as e:
            self.logger.error(f"Error processing telemetry for trip detection: {e}")

    def _should_start_trip(self, telemetry: TelemetryData) -> bool:
        """
        Determine if a trip should start.

        Args:
            telemetry: Telemetry data

        Returns:
            True if trip should start
        """
        device_id = telemetry.device_id

        # Don't start if already in a trip
        if device_id in self.active_trips:
            return False

        # Start trip if:
        # - Ignition is ON, or
        # - Message type is TS (Trip Start), or
        # - Moving (speed > threshold)
        if telemetry.ignition or telemetry.message_type == 'TS':
            return True

        if telemetry.moving or (telemetry.speed and telemetry.speed > 5.0):
            return True

        return False

    def _should_end_trip(self, telemetry: TelemetryData) -> bool:
        """
        Determine if a trip should end.

        Args:
            telemetry: Telemetry data

        Returns:
            True if trip should end
        """
        device_id = telemetry.device_id

        # Only end if currently in a trip
        if device_id not in self.active_trips:
            return False

        # End trip if:
        # - Ignition is OFF, or
        # - Message type is TE (Trip End), or
        # - Not moving for a while
        if telemetry.ignition is False or telemetry.message_type == 'TE':
            return True

        if not telemetry.moving and (not telemetry.speed or telemetry.speed < 1.0):
            return True

        return False

    async def _start_trip(self, telemetry: TelemetryData):
        """
        Start a new trip.

        Args:
            telemetry: Telemetry data
        """
        try:
            device_id = telemetry.device_id

            trip_data = {
                "device_id": device_id,
                "start_time": telemetry.timestamp.isoformat(),
                "start_location": {
                    "lat": telemetry.latitude,
                    "lng": telemetry.longitude,
                },
                "is_active": True,
            }

            trip_id = await db_client.create_trip(trip_data)

            if trip_id:
                self.active_trips[device_id] = trip_id
                self.logger.info(f"Started trip {trip_id} for device {device_id}")

        except Exception as e:
            self.logger.error(f"Error starting trip: {e}")

    async def _end_trip(self, telemetry: TelemetryData):
        """
        End an active trip.

        Args:
            telemetry: Telemetry data
        """
        try:
            device_id = telemetry.device_id
            trip_id = self.active_trips.get(device_id)

            if not trip_id:
                return

            trip_data = {
                "end_time": telemetry.timestamp.isoformat(),
                "end_location": {
                    "lat": telemetry.latitude,
                    "lng": telemetry.longitude,
                },
                "is_active": False,
            }

            # Add trip summary if available from message
            if telemetry.message_type == 'TE' and telemetry.io_elements:
                if "trip_distance" in telemetry.io_elements:
                    trip_data["distance"] = telemetry.io_elements["trip_distance"]
                if "trip_duration" in telemetry.io_elements:
                    trip_data["duration"] = telemetry.io_elements["trip_duration"]

            await db_client.update_trip(trip_id, trip_data)
            del self.active_trips[device_id]

            self.logger.info(f"Ended trip {trip_id} for device {device_id}")

        except Exception as e:
            self.logger.error(f"Error ending trip: {e}")

    async def _update_trip(self, telemetry: TelemetryData):
        """
        Update active trip with new telemetry.

        Args:
            telemetry: Telemetry data
        """
        # In a real implementation, you might update distance, max_speed, etc.
        # For now, we just log
        pass


# Global instance
trip_manager = TripManager()
