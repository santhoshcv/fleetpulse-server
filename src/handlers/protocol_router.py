"""Protocol detection and routing."""

import logging
from typing import Optional
from src.adapters.base import ProtocolAdapter
from src.adapters.teltonika import TeltonikaCodec8EAdapter
from src.adapters.tfms90 import TFMS90Adapter

logger = logging.getLogger(__name__)


class ProtocolRouter:
    """
    Routes incoming data to appropriate protocol adapter.

    Auto-detects protocol based on initial connection data.
    """

    def __init__(self):
        """Initialize protocol router with available adapters."""
        self.adapters = {
            'teltonika': TeltonikaCodec8EAdapter(),
            'tfms90': TFMS90Adapter(),
        }
        self.logger = logger

    def detect_protocol(self, data: bytes) -> Optional[str]:
        """
        Detect protocol from initial data packet.

        Args:
            data: Initial bytes received from device

        Returns:
            Protocol name ('teltonika' or 'tfms90') or None
        """
        if len(data) < 2:
            return None

        # Teltonika detection: starts with 2-byte IMEI length
        # Common pattern: 0x00 0x0F (15 bytes IMEI)
        if len(data) >= 17:
            imei_len = (data[0] << 8) | data[1]
            if 10 <= imei_len <= 20:  # IMEI is typically 15 digits
                try:
                    # Check if next bytes are ASCII digits (IMEI)
                    potential_imei = data[2:2 + imei_len].decode('ascii')
                    if potential_imei.isdigit():
                        self.logger.info("Detected Teltonika protocol")
                        return 'teltonika'
                except:
                    pass

        # TFMS90 detection: text-based, starts with device ID and comma
        try:
            text = data.decode('ascii').strip()
            if ',' in text:
                parts = text.split(',')
                # Check if it looks like TFMS90 format
                if len(parts) >= 2:
                    msg_type = parts[1].upper()
                    known_types = ['TD', 'TS', 'TE', 'HA2', 'HB2', 'HC2', 'OS3', 'FLF', 'FLD']
                    if msg_type in known_types:
                        self.logger.info("Detected TFMS90 protocol")
                        return 'tfms90'
        except:
            pass

        # Default to None if detection fails
        self.logger.warning("Unable to detect protocol from data")
        return None

    def get_adapter(self, protocol: str) -> Optional[ProtocolAdapter]:
        """
        Get adapter for specified protocol.

        Args:
            protocol: Protocol name

        Returns:
            Protocol adapter instance or None
        """
        return self.adapters.get(protocol)
