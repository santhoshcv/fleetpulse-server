"""Database utilities for Supabase integration."""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client

from config.settings import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase database client wrapper."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Optional[Client] = None
        self._connect()

    def _connect(self):
        """Establish connection to Supabase."""
        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    # Device operations
    async def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device by ID."""
        try:
            response = self.client.table("devices").select("*").eq("device_id", device_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching device {device_id}: {e}")
            return None

    async def upsert_device(self, device_data: Dict[str, Any]) -> bool:
        """Insert or update device."""
        try:
            device_data["updated_at"] = datetime.utcnow().isoformat()
            self.client.table("devices").upsert(device_data, on_conflict="device_id").execute()
            logger.info(f"Upserted device {device_data['device_id']}")
            return True
        except Exception as e:
            logger.error(f"Error upserting device: {e}")
            return False

    async def update_device_last_seen(self, device_id: str) -> bool:
        """Update device last_seen timestamp."""
        try:
            self.client.table("devices").update({
                "last_seen": datetime.utcnow().isoformat()
            }).eq("device_id", device_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating device last_seen: {e}")
            return False

    # Telemetry operations
    async def insert_telemetry(self, telemetry_data: Dict[str, Any]) -> bool:
        """Insert telemetry data."""
        try:
            telemetry_data["created_at"] = datetime.utcnow().isoformat()
            self.client.table("telemetry_data").insert(telemetry_data).execute()
            return True
        except Exception as e:
            logger.error(f"Error inserting telemetry: {e}")
            return False

    async def insert_telemetry_batch(self, telemetry_batch: List[Dict[str, Any]]) -> bool:
        """Insert multiple telemetry records."""
        try:
            for record in telemetry_batch:
                record["created_at"] = datetime.utcnow().isoformat()
            self.client.table("telemetry_data").insert(telemetry_batch).execute()
            logger.info(f"Inserted {len(telemetry_batch)} telemetry records")
            return True
        except Exception as e:
            logger.error(f"Error inserting telemetry batch: {e}")
            return False

    async def get_latest_telemetry(self, device_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get latest telemetry for a device."""
        try:
            response = self.client.table("telemetry_data")\
                .select("*")\
                .eq("device_id", device_id)\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching telemetry: {e}")
            return []

    # Trip operations
    async def create_trip(self, trip_data: Dict[str, Any]) -> Optional[str]:
        """Create a new trip."""
        try:
            trip_data["created_at"] = datetime.utcnow().isoformat()
            response = self.client.table("trips").insert(trip_data).execute()
            trip_id = response.data[0]["trip_id"] if response.data else None
            logger.info(f"Created trip {trip_id}")
            return trip_id
        except Exception as e:
            logger.error(f"Error creating trip: {e}")
            return None

    async def update_trip(self, trip_id: str, trip_data: Dict[str, Any]) -> bool:
        """Update an existing trip."""
        try:
            self.client.table("trips").update(trip_data).eq("trip_id", trip_id).execute()
            logger.info(f"Updated trip {trip_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating trip: {e}")
            return False

    async def get_active_trip(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get active trip for a device."""
        try:
            response = self.client.table("trips")\
                .select("*")\
                .eq("device_id", device_id)\
                .eq("is_active", True)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching active trip: {e}")
            return None


# Global instance
db_client = SupabaseClient()
