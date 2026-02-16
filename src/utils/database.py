"""Database client for Supabase operations."""

import logging
from supabase import create_client, Client
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Hardcoded Supabase credentials
SUPABASE_URL = "https://ypxlpqylmxddrvhasmst.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlweGxwcXlsbXhkZHJ2aGFzbXN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyMzM3MjAsImV4cCI6MjA4NjgwOTcyMH0.6UYQzZSMFne8CdugAwqJhjBTIe-8YP8fL1jQeM4YJTw"


class DatabaseClient:
    """Supabase database client."""

    def __init__(self):
        """Initialize Supabase client."""
        try:
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✓ Database client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database client: {e}")
            raise

    async def get_device(self, device_id: str) -> Optional[Dict]:
        """Get device by ID."""
        try:
            response = self.client.table("devices").select("*").eq("device_id", device_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching device {device_id}: {e}")
            return None

    async def upsert_device(self, device_data: Dict):
        """Insert or update device."""
        try:
            self.client.table("devices").upsert(device_data).execute()
            logger.info(f"Device {device_data['device_id']} upserted")
        except Exception as e:
            logger.error(f"Error upserting device: {e}")
            raise

    async def update_device_last_seen(self, device_id: str):
        """Update device last_seen timestamp."""
        from datetime import datetime
        try:
            self.client.table("devices").update({
                "last_seen": datetime.utcnow().isoformat()
            }).eq("device_id", device_id).execute()
        except Exception as e:
            logger.error(f"Error updating last_seen for {device_id}: {e}")

    async def insert_telemetry(self, telemetry_data: Dict):
        """Insert single telemetry record."""
        try:
            self.client.table("telemetry_data").insert(telemetry_data).execute()
        except Exception as e:
            logger.error(f"Error inserting telemetry: {e}")
            raise

    async def insert_telemetry_batch(self, telemetry_list: List[Dict]):
        """Batch insert telemetry records."""
        try:
            self.client.table("telemetry_data").insert(telemetry_list).execute()
            logger.info(f"Inserted {len(telemetry_list)} telemetry records")
        except Exception as e:
            logger.error(f"Error batch inserting telemetry: {e}")
            raise


# Global database client instance
db_client = DatabaseClient()
