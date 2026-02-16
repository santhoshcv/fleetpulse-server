"""Device model for GPS tracking devices."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Device:
    """Represents a GPS tracking device."""

    device_id: str  # IMEI or unique identifier
    protocol: str  # 'teltonika' or 'tfms90'
    name: Optional[str] = None
    vehicle_id: Optional[str] = None
    is_active: bool = True
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Connection state (not persisted)
    is_connected: bool = False
    connection_ip: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "device_id": self.device_id,
            "protocol": self.protocol,
            "name": self.name,
            "vehicle_id": self.vehicle_id,
            "is_active": self.is_active,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "Device":
        """Create Device from dictionary."""
        return Device(
            device_id=data["device_id"],
            protocol=data["protocol"],
            name=data.get("name"),
            vehicle_id=data.get("vehicle_id"),
            is_active=data.get("is_active", True),
            last_seen=datetime.fromisoformat(data["last_seen"]) if data.get("last_seen") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
