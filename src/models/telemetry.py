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
        # Promote fuel_level from io_elements to top-level column
        fuel_level = None
        if self.io_elements:
            raw = self.io_elements.get("fuel_level")
            if raw is not None:
                try:
                    fuel_level = float(raw)
                except (TypeError, ValueError):
                    fuel_level = None

        result = {
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
            "heading": self.heading,
            "satellites": self.satellites,
            "fuel_level": fuel_level,
            "protocol": self.protocol,
            "message_type": self.message_type,
            "io_elements": self.io_elements,
        }

        # For TE messages, promote all trip data to top-level columns
        # This avoids Supabase schema cache issues
        if self.message_type == "TE" and self.io_elements:
            result["start_timestamp"] = self.io_elements.get("start_timestamp")
            result["end_timestamp"] = self.io_elements.get("end_timestamp")
            result["duration_seconds"] = self.io_elements.get("duration_seconds")
            result["start_fuel"] = self.io_elements.get("start_fuel")
            result["end_fuel"] = self.io_elements.get("end_fuel")
            result["distance_km"] = self.io_elements.get("distance_km")
            result["start_latitude"] = self.io_elements.get("start_latitude")
            result["start_longitude"] = self.io_elements.get("start_longitude")

        return result
