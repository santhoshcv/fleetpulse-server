"""Telemetry data model."""

from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime


@dataclass
class TelemetryData:
    """Telemetry data from GPS device."""

    device_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    satellites: Optional[int] = None
    protocol: str = "unknown"
    message_type: Optional[str] = None
    io_elements: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage."""
        # Promote fuel_level from io_elements to top-level column so the
        # fn_sync_telemetry_to_gps trigger can map it into gps_locations.fuel_level
        fuel_level = None
        if self.io_elements:
            raw = self.io_elements.get("fuel_level")
            if raw is not None:
                try:
                    fuel_level = float(raw)
                except (TypeError, ValueError):
                    fuel_level = None

        return {
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
            "heading": self.heading,
            "satellites": self.satellites,
            "fuel_level": fuel_level,  # promoted from io_elements for DB trigger
            "protocol": self.protocol,
            "message_type": self.message_type,
            "io_elements": self.io_elements,
        }
