"""Trip model for journey tracking."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Trip:
    """Represents a vehicle trip/journey."""

    trip_id: Optional[str] = None
    device_id: str = ""
    vehicle_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_location: Optional[dict] = None  # {"lat": float, "lng": float, "address": str}
    end_location: Optional[dict] = None
    distance: Optional[float] = None  # km
    duration: Optional[int] = None  # seconds
    max_speed: Optional[float] = None  # km/h
    avg_speed: Optional[float] = None  # km/h
    fuel_consumed: Optional[float] = None  # liters
    is_active: bool = True
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "trip_id": self.trip_id,
            "device_id": self.device_id,
            "vehicle_id": self.vehicle_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "start_location": self.start_location,
            "end_location": self.end_location,
            "distance": self.distance,
            "duration": self.duration,
            "max_speed": self.max_speed,
            "avg_speed": self.avg_speed,
            "fuel_consumed": self.fuel_consumed,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "Trip":
        """Create Trip from dictionary."""
        return Trip(
            trip_id=data.get("trip_id"),
            device_id=data["device_id"],
            vehicle_id=data.get("vehicle_id"),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            start_location=data.get("start_location"),
            end_location=data.get("end_location"),
            distance=data.get("distance"),
            duration=data.get("duration"),
            max_speed=data.get("max_speed"),
            avg_speed=data.get("avg_speed"),
            fuel_consumed=data.get("fuel_consumed"),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )
