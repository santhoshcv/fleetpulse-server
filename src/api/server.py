"""FastAPI REST API server for FleetPulse."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.database import db_client
from src.api.models import (
    DeviceResponse,
    TelemetryResponse,
    TripResponse,
    DeviceListResponse,
    TelemetryListResponse
)

# Setup logging
logger = setup_logger("fleetpulse.api", settings.LOG_LEVEL)

# Create FastAPI app
app = FastAPI(
    title="FleetPulse API",
    description="Multi-Protocol GPS Tracking Platform API",
    version="1.0.0"
)

# CORS middleware for Flutter frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "FleetPulse API",
        "version": "1.0.0",
        "status": "running",
        "protocols": ["teltonika", "tfms90"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Device endpoints
@app.get("/api/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str):
    """
    Get device by ID.

    Args:
        device_id: Device identifier (IMEI)

    Returns:
        Device information
    """
    try:
        device_data = await db_client.get_device(device_id)

        if not device_data:
            raise HTTPException(status_code=404, detail="Device not found")

        return device_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching device {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Telemetry endpoints
@app.get("/api/devices/{device_id}/telemetry", response_model=TelemetryListResponse)
async def get_device_telemetry(
    device_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    Get telemetry data for a device.

    Args:
        device_id: Device identifier
        limit: Number of records to return (max 1000)
        offset: Number of records to skip

    Returns:
        List of telemetry records
    """
    try:
        telemetry_data = await db_client.get_latest_telemetry(device_id, limit)

        return {
            "device_id": device_id,
            "count": len(telemetry_data),
            "telemetry": telemetry_data
        }

    except Exception as e:
        logger.error(f"Error fetching telemetry for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/devices/{device_id}/telemetry/latest", response_model=TelemetryResponse)
async def get_latest_telemetry(device_id: str):
    """
    Get latest telemetry record for a device.

    Args:
        device_id: Device identifier

    Returns:
        Latest telemetry record
    """
    try:
        telemetry_data = await db_client.get_latest_telemetry(device_id, limit=1)

        if not telemetry_data:
            raise HTTPException(status_code=404, detail="No telemetry data found")

        return telemetry_data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest telemetry for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/devices/{device_id}/location", response_model=dict)
async def get_device_location(device_id: str):
    """
    Get current location of a device.

    Args:
        device_id: Device identifier

    Returns:
        Current location with lat/lng
    """
    try:
        telemetry_data = await db_client.get_latest_telemetry(device_id, limit=1)

        if not telemetry_data:
            raise HTTPException(status_code=404, detail="No location data found")

        latest = telemetry_data[0]

        return {
            "device_id": device_id,
            "location": {
                "latitude": latest["latitude"],
                "longitude": latest["longitude"],
                "altitude": latest.get("altitude"),
            },
            "speed": latest.get("speed"),
            "heading": latest.get("heading"),
            "timestamp": latest["timestamp"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching location for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Trip endpoints
@app.get("/api/devices/{device_id}/trips/active", response_model=Optional[TripResponse])
async def get_active_trip(device_id: str):
    """
    Get active trip for a device.

    Args:
        device_id: Device identifier

    Returns:
        Active trip or None
    """
    try:
        trip_data = await db_client.get_active_trip(device_id)

        if not trip_data:
            return None

        return trip_data

    except Exception as e:
        logger.error(f"Error fetching active trip for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Statistics endpoints
@app.get("/api/devices/{device_id}/stats")
async def get_device_stats(device_id: str, days: int = Query(default=7, ge=1, le=90)):
    """
    Get device statistics for the last N days.

    Args:
        device_id: Device identifier
        days: Number of days to analyze

    Returns:
        Device statistics
    """
    try:
        # This would require more complex queries
        # For now, return basic stats
        telemetry_data = await db_client.get_latest_telemetry(device_id, limit=1000)

        total_records = len(telemetry_data)

        # Calculate basic stats
        total_distance = 0.0
        max_speed = 0.0

        for record in telemetry_data:
            if record.get("speed"):
                max_speed = max(max_speed, record["speed"])

        return {
            "device_id": device_id,
            "period_days": days,
            "total_records": total_records,
            "max_speed": max_speed,
            "total_distance": total_distance,
        }

    except Exception as e:
        logger.error(f"Error fetching stats for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
