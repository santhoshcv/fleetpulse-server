"""Telemetry data model."""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class TelemetryData:
    """Represents telemetry data from a GPS device."""

    device_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None  # km/h
    heading: Optional[int] = None  # degrees (0-360)
    satellites: Optional[int] = None
    hdop: Optional[float] = None

    # Vehicle metrics
    odometer: Optional[float] = None  # km
    engine_hours: Optional[float] = None  # hours
    fuel_level: Optional[float] = None  # liters or percentage
    battery_voltage: Optional[float] = None  # volts

    # Status flags
    ignition: Optional[bool] = None
    moving: Optional[bool] = None

    # I/O and custom data
    io_elements: Dict[str, Any] = field(default_factory=dict)
    raw_data: Optional[str] = None

    # Metadata
    protocol: str = "unknown"
    message_type: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
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
            "hdop": self.hdop,
            "odometer": self.odometer,
            "engine_hours": self.engine_hours,
            "fuel_level": self.fuel_level,
            "battery_voltage": self.battery_voltage,
            "ignition": self.ignition,
            "moving": self.moving,
            "io_elements": self.io_elements,
            "raw_data": self.raw_data,
            "protocol": self.protocol,
            "message_type": self.message_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "TelemetryData":
        """Create TelemetryData from dictionary."""
        return TelemetryData(
            device_id=data["device_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data.get("altitude"),
            speed=data.get("speed"),
            heading=data.get("heading"),
            satellites=data.get("satellites"),
            hdop=data.get("hdop"),
            odometer=data.get("odometer"),
            engine_hours=data.get("engine_hours"),
            fuel_level=data.get("fuel_level"),
            battery_voltage=data.get("battery_voltage"),
            ignition=data.get("ignition"),
            moving=data.get("moving"),
            io_elements=data.get("io_elements", {}),
            raw_data=data.get("raw_data"),
            protocol=data.get("protocol", "unknown"),
            message_type=data.get("message_type"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )
