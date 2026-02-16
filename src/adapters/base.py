"""Base protocol adapter interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.telemetry import TelemetryData


class ProtocolAdapter(ABC):
    """Base class for protocol adapters."""

    @abstractmethod
    async def parse(self, data: bytes, device_id: str) -> List[TelemetryData]:
        """
        Parse raw protocol data into telemetry records.

        Args:
            data: Raw bytes from the device
            device_id: Device identifier (IMEI)

        Returns:
            List of parsed telemetry data records
        """
        pass

    @abstractmethod
    def create_response(self, record_count: int) -> bytes:
        """
        Create acknowledgment response for the device.

        Args:
            record_count: Number of records received

        Returns:
            Response bytes to send back to device
        """
        pass

    @abstractmethod
    def identify_device(self, data: bytes) -> Optional[str]:
        """
        Extract device identifier from initial connection data.

        Args:
            data: Initial connection bytes

        Returns:
            Device ID (IMEI) or None if not found
        """
        pass
