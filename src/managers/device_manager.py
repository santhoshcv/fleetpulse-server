"""Device management business logic."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.utils.database import db_client
from src.models.device import Device

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages device-related business logic."""

    def __init__(self):
        """Initialize device manager."""
        self.logger = logger
        self.active_connections: Dict[str, bool] = {}

    async def get_device(self, device_id: str) -> Optional[Device]:
        """
        Get device by ID.

        Args:
            device_id: Device identifier

        Returns:
            Device object or None
        """
        try:
            device_data = await db_client.get_device(device_id)
            if device_data:
                return Device.from_dict(device_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting device {device_id}: {e}")
            return None

    async def get_all_devices(self) -> List[Device]:
        """
        Get all registered devices.

        Returns:
            List of Device objects
        """
        # This would require implementing a get_all method in SupabaseClient
        # For now, return empty list
        return []

    async def get_active_devices(self, minutes: int = 5) -> List[Device]:
        """
        Get devices active within the last N minutes.

        Args:
            minutes: Time window in minutes

        Returns:
            List of active Device objects
        """
        # This would require implementing query with time filter
        # For now, return empty list
        return []

    def mark_connected(self, device_id: str):
        """Mark device as connected."""
        self.active_connections[device_id] = True
        self.logger.info(f"Device {device_id} marked as connected")

    def mark_disconnected(self, device_id: str):
        """Mark device as disconnected."""
        self.active_connections[device_id] = False
        self.logger.info(f"Device {device_id} marked as disconnected")

    def is_connected(self, device_id: str) -> bool:
        """Check if device is currently connected."""
        return self.active_connections.get(device_id, False)


# Global instance
device_manager = DeviceManager()
