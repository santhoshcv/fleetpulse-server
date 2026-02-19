"""Database client for PostgreSQL operations."""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Optional, List, Dict
import os

logger = logging.getLogger(__name__)

# Database connection parameters
DB_HOST = "db.ypxlpqylmxddrvhasmst.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "tHinkpad#123A"


class DatabaseClient:
    """PostgreSQL database client using psycopg2."""

    def __init__(self):
        """Initialize PostgreSQL connection pool."""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            self.conn.autocommit = False
            logger.info("✓ Database client initialized with psycopg2")
        except Exception as e:
            logger.error(f"Failed to initialize database client: {e}")
            raise

    def _get_cursor(self):
        """Get a cursor, reconnecting if needed."""
        try:
            # Test connection
            self.conn.isolation_level
        except:
            # Reconnect if connection is dead
            logger.warning("Reconnecting to database...")
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            self.conn.autocommit = False
        return self.conn.cursor()

    async def get_device(self, device_id: str) -> Optional[Dict]:
        """Get device by ID."""
        try:
            cursor = self._get_cursor()
            cursor.execute(
                "SELECT * FROM devices WHERE device_id = %s LIMIT 1",
                (device_id,)
            )
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching device {device_id}: {e}")
            return None

    async def upsert_device(self, device_data: Dict):
        """Insert or update device."""
        try:
            cursor = self._get_cursor()

            # Build column names and placeholders
            columns = list(device_data.keys())
            values = [device_data[col] for col in columns]

            # Create INSERT with ON CONFLICT DO UPDATE
            cols_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'device_id'])

            query = f"""
                INSERT INTO devices ({cols_str})
                VALUES ({placeholders})
                ON CONFLICT (device_id)
                DO UPDATE SET {update_set}
            """

            cursor.execute(query, values)
            self.conn.commit()
            cursor.close()
            logger.info(f"Device {device_data['device_id']} upserted")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error upserting device: {e}")
            raise

    async def update_device_last_seen(self, device_id: str):
        """Update device last_seen timestamp."""
        from datetime import datetime
        try:
            cursor = self._get_cursor()
            cursor.execute(
                "UPDATE devices SET last_seen = %s WHERE device_id = %s",
                (datetime.utcnow(), device_id)
            )
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error updating last_seen for {device_id}: {e}")

    async def insert_telemetry(self, telemetry_data: Dict):
        """Insert single telemetry record with proper JSONB handling."""
        try:
            cursor = self._get_cursor()

            # Prepare data - convert io_elements dict to JSON for psycopg2
            data = telemetry_data.copy()
            io_elements = data.get('io_elements')
            if io_elements and isinstance(io_elements, dict):
                data['io_elements'] = Json(io_elements)

            # Build INSERT query dynamically based on available columns
            columns = [
                'device_id', 'timestamp', 'latitude', 'longitude',
                'altitude', 'speed', 'heading', 'satellites',
                'fuel_level', 'protocol', 'message_type', 'io_elements'
            ]

            # Only include columns that have non-None values
            insert_cols = []
            insert_vals = []
            for col in columns:
                if col in data:
                    insert_cols.append(col)
                    insert_vals.append(data[col])

            cols_str = ", ".join(insert_cols)
            placeholders = ", ".join(["%s"] * len(insert_cols))

            query = f"INSERT INTO telemetry_data ({cols_str}) VALUES ({placeholders})"

            logger.info(f"Inserting telemetry: device={data.get('device_id')}, fuel={data.get('fuel_level')}, msg_type={data.get('message_type')}")
            cursor.execute(query, insert_vals)
            self.conn.commit()
            cursor.close()
            logger.info("✓ Telemetry inserted successfully")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting telemetry: {e}")
            logger.error(f"Data was: {telemetry_data}")
            raise

    async def insert_telemetry_batch(self, telemetry_list: List[Dict]):
        """Batch insert telemetry records."""
        try:
            cursor = self._get_cursor()

            for telemetry_data in telemetry_list:
                # Prepare data
                data = telemetry_data.copy()
                io_elements = data.get('io_elements')
                if io_elements and isinstance(io_elements, dict):
                    data['io_elements'] = Json(io_elements)

                # Build INSERT
                columns = [
                    'device_id', 'timestamp', 'latitude', 'longitude',
                    'altitude', 'speed', 'heading', 'satellites',
                    'fuel_level', 'protocol', 'message_type', 'io_elements'
                ]

                insert_cols = []
                insert_vals = []
                for col in columns:
                    if col in data:
                        insert_cols.append(col)
                        insert_vals.append(data[col])

                cols_str = ", ".join(insert_cols)
                placeholders = ", ".join(["%s"] * len(insert_cols))
                query = f"INSERT INTO telemetry_data ({cols_str}) VALUES ({placeholders})"

                cursor.execute(query, insert_vals)

            self.conn.commit()
            cursor.close()
            logger.info(f"✓ Inserted {len(telemetry_list)} telemetry records")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error batch inserting telemetry: {e}")
            raise

    async def get_device_by_imei(self, imei: str) -> Optional[Dict]:
        """Get device by IMEI."""
        try:
            cursor = self._get_cursor()
            cursor.execute(
                "SELECT * FROM devices WHERE imei = %s LIMIT 1",
                (imei,)
            )
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching device by IMEI {imei}: {e}")
            return None

    async def get_next_short_device_id(self, protocol: str) -> int:
        """Get next available short_device_id for TFMS90 protocol."""
        try:
            cursor = self._get_cursor()
            cursor.execute(
                """
                SELECT short_device_id FROM devices
                WHERE protocol = %s AND short_device_id IS NOT NULL
                ORDER BY CAST(short_device_id AS INTEGER) DESC
                LIMIT 1
                """,
                (protocol,)
            )
            result = cursor.fetchone()
            cursor.close()

            if not result:
                # First device, start from 100
                return 100

            # Return max + 1
            max_id = int(result['short_device_id'])
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

    def __del__(self):
        """Close connection on cleanup."""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except:
            pass


# Global database client instance
db_client = DatabaseClient()
