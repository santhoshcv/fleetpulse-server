"""Main TCP server for FleetPulse."""

import asyncio
import logging
import sys

from config.settings import settings
from src.utils.logger import setup_logger
from src.handlers.connection_handler import ConnectionHandler


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Handle new client connection.

    Args:
        reader: Asyncio stream reader
        writer: Asyncio stream writer
    """
    handler = ConnectionHandler(reader, writer)
    await handler.handle()


async def main():
    """Start the TCP server."""
    # Setup logging
    logger = setup_logger("fleetpulse", settings.LOG_LEVEL)

    # Validate settings
    if not settings.validate():
        logger.error("Invalid configuration. Please check your .env file.")
        logger.error("Required: SUPABASE_URL, SUPABASE_KEY")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("FleetPulse Multi-Protocol GPS Tracking Server")
    logger.info("=" * 60)
    logger.info(f"TCP Server: {settings.TCP_HOST}:{settings.TCP_PORT}")
    logger.info(f"Supported Protocols: Teltonika Codec 8E, TFMS90")
    logger.info(f"Database: {settings.SUPABASE_URL}")
    logger.info("=" * 60)

    # Start TCP server
    server = await asyncio.start_server(
        handle_client,
        settings.TCP_HOST,
        settings.TCP_PORT
    )

    addr = server.sockets[0].getsockname()
    logger.info(f"Server started on {addr}")
    logger.info("Waiting for connections...")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
