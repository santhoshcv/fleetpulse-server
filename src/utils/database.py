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
            import json

            # Convert io_elements dict to JSON string to prevent Supabase client from unnesting it
            data = telemetry_data.copy()
            if data.get('io_elements') and isinstance(data['io_elements'], dict):
                data['io_elements'] = json.dumps(data['io_elements'])

            logger.info(f"DEBUG AFTER JSON CONVERSION: io_elements type={type(data.get('io_elements'))}, value={data.get('io_elements')[:100] if data.get('io_elements') else None}")
            self.client.table("telemetry_data").insert(data).execute()
        except Exception as e:
            logger.error(f"Error inserting telemetry: {e}")
            raise

    async def insert_telemetry_batch(self, telemetry_list: List[Dict]):
        """Batch insert telemetry records."""
        try:
            import json

            # Convert io_elements dict to JSON string for each record
            data_list = []
            for telemetry_data in telemetry_list:
                data = telemetry_data.copy()
                if data.get('io_elements') and isinstance(data['io_elements'], dict):
                    data['io_elements'] = json.dumps(data['io_elements'])
                data_list.append(data)

            self.client.table("telemetry_data").insert(data_list).execute()
            logger.info(f"Inserted {len(data_list)} telemetry records")
        except Exception as e:
            logger.error(f"Error batch inserting telemetry: {e}")
            raise

    async def get_device_by_imei(self, imei: str) -> Optional[Dict]:
        """Get device by IMEI."""
        try:
            response = self.client.table("devices").select("*").eq("imei", imei).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching device by IMEI {imei}: {e}")
            return None

    async def get_next_short_device_id(self, protocol: str) -> int:
        """Get next available short_device_id for TFMS90 protocol."""
        try:
            # Get all devices with short_device_id for this protocol
            response = self.client.table("devices").select("short_device_id").eq("protocol", protocol).not_.is_("short_device_id", "null").execute()

            if not response.data:
                # First device, start from 100
                return 100

            # Find max short_device_id and add 1
            max_id = max([int(d['short_device_id']) for d in response.data if d.get('short_device_id')])
            return max_id + 1

        except Exception as e:
            logger.error(f"Error getting next short_device_id: {e}")
            # Fallback to a random ID
            import random
            return random.randint(100, 999)

    async def assign_short_device_id(self, imei: str, protocol: str) -> int:
        """Assign a new short_device_id for a device."""
        try:
            # Check if device with this IMEI already exists
            existing = await self.get_device_by_imei(imei)

            if existing and existing.get('short_device_id'):
                # Device exists, return existing short_device_id
                logger.info(f"Device {imei} already has short_device_id: {existing['short_device_id']}")
                return int(existing['short_device_id'])

            # Assign new short_device_id
            short_id = await self.get_next_short_device_id(protocol)
            logger.info(f"Assigned new short_device_id {short_id} to IMEI {imei}")
            return short_id

        except Exception as e:
            logger.error(f"Error assigning short_device_id: {e}")
            raise


# Global database client instance
db_client = DatabaseClient()
