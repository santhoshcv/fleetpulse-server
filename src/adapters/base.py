"""Base protocol adapter interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.telemetry import TelemetryData


class ProtocolAdapter(ABC):
    """Base class for protocol adapters."""

    @abstractmethod
    async def parse(self, data: bytes, device_id: str) -> List[TelemetryData]:
        """Parse raw data into telemetry records."""
        pass

    @abstractmethod
    def identify_device(self, data: bytes) -> Optional[str]:
        """Extract device ID from data."""
        pass

    @abstractmethod
    def create_response(self, num_records: int, **kwargs) -> bytes:
        """Create acknowledgment response."""
        pass
