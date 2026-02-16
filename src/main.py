"""FleetPulse TCP Server - Main entry point."""

import asyncio
import logging
from src.handlers.connection_handler import ConnectionHandler

# Settings
TCP_HOST = "0.0.0.0"
TCP_PORT = 23000
LOG_LEVEL = "INFO"

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle incoming client connection."""
    handler = ConnectionHandler(reader, writer)
    await handler.handle()


async def main():
    """Start the TCP server."""
    server = await asyncio.start_server(
        handle_client,
        TCP_HOST,
        TCP_PORT
    )

    addr = server.sockets[0].getsockname()
    logger.info(f"FleetPulse TCP Server started on {addr[0]}:{addr[1]}")
    logger.info("Waiting for GPS device connections...")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
