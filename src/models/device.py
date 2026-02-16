"""Device model."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Device:
    """GPS device model."""

    device_id: str
    protocol: str
    is_active: bool = True
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
