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
        return {
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
            "heading": self.heading,
            "satellites": self.satellites,
            "protocol": self.protocol,
            "message_type": self.message_type,
            "io_elements": self.io_elements,
        }
