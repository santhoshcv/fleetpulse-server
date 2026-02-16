"""Pydantic models for API requests/responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DeviceResponse(BaseModel):
    """Device information response."""
    device_id: str
    protocol: str
    name: Optional[str] = None
    vehicle_id: Optional[str] = None
    is_active: bool = True
    last_seen: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DeviceListResponse(BaseModel):
    """List of devices response."""
    count: int
    devices: List[DeviceResponse]


class TelemetryResponse(BaseModel):
    """Telemetry data response."""
    device_id: str
    timestamp: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[int] = None
    satellites: Optional[int] = None
    odometer: Optional[float] = None
    fuel_level: Optional[float] = None
    battery_voltage: Optional[float] = None
    ignition: Optional[bool] = None
    moving: Optional[bool] = None
    io_elements: Optional[Dict[str, Any]] = None
    protocol: str
    message_type: Optional[str] = None


class TelemetryListResponse(BaseModel):
    """List of telemetry records response."""
    device_id: str
    count: int
    telemetry: List[Dict[str, Any]]


class TripResponse(BaseModel):
    """Trip information response."""
    trip_id: Optional[str] = None
    device_id: str
    vehicle_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    start_location: Optional[Dict[str, Any]] = None
    end_location: Optional[Dict[str, Any]] = None
    distance: Optional[float] = None
    duration: Optional[int] = None
    max_speed: Optional[float] = None
    avg_speed: Optional[float] = None
    is_active: bool = True


class LocationResponse(BaseModel):
    """Current location response."""
    device_id: str
    location: Dict[str, Any]
    speed: Optional[float] = None
    heading: Optional[int] = None
    timestamp: str
