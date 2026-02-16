"""
TFMS90 GPS device simulator.

Simulates a TFMS90 device sending various message types to the FleetPulse server.
Supports: TD, TS, TE, HA2, HB2, HC2, OS3, FLF, FLD messages.
"""

import socket
import time
import random
import math
from datetime import datetime
from typing import Tuple


class TFMS90Simulator:
    """Simulates a TFMS90 GPS tracking device."""

    def __init__(
        self,
        device_id: str,
        server_host: str = "localhost",
        server_port: int = 8888,
        start_lat: float = 12.9716,
        start_lon: float = 77.5946
    ):
        """
        Initialize TFMS90 simulator.

        Args:
            device_id: Device identifier (IMEI or custom ID)
            server_host: FleetPulse server hostname
            server_port: FleetPulse server port
            start_lat: Starting latitude (default: Bangalore, India)
            start_lon: Starting longitude
        """
        self.device_id = device_id
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None

        # Vehicle state
        self.latitude = start_lat
        self.longitude = start_lon
        self.speed = 0.0  # km/h
        self.heading = 0  # degrees
        self.altitude = 920.0  # meters
        self.satellites = 8
        self.odometer = 0.0  # km
        self.fuel_level = 75.0  # liters
        self.battery_voltage = 12.6  # volts
        self.engine_hours = 1234.5  # hours
        self.ignition = False
        self.in_trip = False

        print(f"[TFMS90] Initialized device {device_id}")
        print(f"[TFMS90] Starting position: {start_lat:.6f}, {start_lon:.6f}")

    def connect(self):
        """Connect to FleetPulse server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            print(f"[TFMS90] Connected to {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"[TFMS90] Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from server."""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("[TFMS90] Disconnected")

    def send_message(self, message: str) -> bool:
        """
        Send message to server.

        Args:
            message: TFMS90 protocol message

        Returns:
            True if successful
        """
        try:
            if not self.sock:
                print("[TFMS90] Not connected")
                return False

            # Send message
            self.sock.send(message.encode('ascii'))
            print(f"[TFMS90] Sent: {message}")

            # Wait for acknowledgment
            response = self.sock.recv(1024)
            print(f"[TFMS90] Received: {response.decode('ascii').strip()}")

            return True

        except Exception as e:
            print(f"[TFMS90] Error sending message: {e}")
            return False

    def send_tracking_data(self):
        """
        Send TD (Tracking Data) message.

        Format: <DEVICE_ID>,TD,<TIMESTAMP>,<LAT>,<LON>,<SPEED>,<HEADING>,<ALT>,<SATS>,<ODO>,<IGN>,<FUEL>
        """
        timestamp = datetime.utcnow().isoformat()

        message = (
            f"{self.device_id},TD,"
            f"{timestamp},"
            f"{self.latitude:.6f},"
            f"{self.longitude:.6f},"
            f"{self.speed:.1f},"
            f"{self.heading},"
            f"{self.altitude:.1f},"
            f"{self.satellites},"
            f"{self.odometer:.2f},"
            f"{1 if self.ignition else 0},"
            f"{self.fuel_level:.1f}"
        )

        return self.send_message(message)

    def send_trip_start(self):
        """
        Send TS (Trip Start) message.

        Format: <DEVICE_ID>,TS,<TIMESTAMP>,<LAT>,<LON>,<ODOMETER>
        """
        timestamp = datetime.utcnow().isoformat()

        message = (
            f"{self.device_id},TS,"
            f"{timestamp},"
            f"{self.latitude:.6f},"
            f"{self.longitude:.6f},"
            f"{self.odometer:.2f}"
        )

        self.in_trip = True
        self.ignition = True
        return self.send_message(message)

    def send_trip_end(self, trip_distance: float = 0.0, trip_duration: int = 0):
        """
        Send TE (Trip End) message.

        Format: <DEVICE_ID>,TE,<TIMESTAMP>,<LAT>,<LON>,<ODOMETER>,<DISTANCE>,<DURATION>
        """
        timestamp = datetime.utcnow().isoformat()

        message = (
            f"{self.device_id},TE,"
            f"{timestamp},"
            f"{self.latitude:.6f},"
            f"{self.longitude:.6f},"
            f"{self.odometer:.2f},"
            f"{trip_distance:.2f},"
            f"{trip_duration}"
        )

        self.in_trip = False
        self.ignition = False
        self.speed = 0.0
        return self.send_message(message)

    def send_heartbeat_a2(self):
        """Send HA2 (Heartbeat A2) message."""
        timestamp = datetime.utcnow().isoformat()

        message = (
            f"{self.device_id},HA2,"
            f"{timestamp},"
            f"{self.latitude:.6f},"
            f"{self.longitude:.6f},"
            f"OK"
        )

        return self.send_message(message)

    def send_heartbeat_b2(self):
        """Send HB2 (Heartbeat B2) message."""
        timestamp = datetime.utcnow().isoformat()

        message = (
            f"{self.device_id},HB2,"
            f"{timestamp},"
            f"{self.latitude:.6f},"
            f"{self.longitude:.6f},"
            f"ALIVE"
        )

        return self.send_message(message)

    def send_heartbeat_c2(self):
        """Send HC2 (Heartbeat C2) message."""
        timestamp = datetime.utcnow().isoformat()

        message = f"{self.device_id},HC2,{timestamp},RUNNING"

        return self.send_message(message)

    def send_operating_status(self):
        """
        Send OS3 (Operating Status) message.

        Format: <DEVICE_ID>,OS3,<TIMESTAMP>,<BATTERY_V>,<IGNITION>,<FUEL>,<ENGINE_HRS>
        """
        timestamp = datetime.utcnow().isoformat()

        message = (
            f"{self.device_id},OS3,"
            f"{timestamp},"
            f"{self.battery_voltage:.1f},"
            f"{1 if self.ignition else 0},"
            f"{self.fuel_level:.1f},"
            f"{self.engine_hours:.1f}"
        )

        return self.send_message(message)

    def send_fuel_fill(self, amount: float):
        """
        Send FLF (Fuel Fill) event.

        Format: <DEVICE_ID>,FLF,<TIMESTAMP>,<LAT>,<LON>,<FUEL_BEFORE>,<FUEL_AFTER>,<FUEL_ADDED>
        """
        timestamp = datetime.utcnow().isoformat()
        fuel_before = self.fuel_level
        self.fuel_level += amount
        fuel_after = self.fuel_level

        message = (
            f"{self.device_id},FLF,"
            f"{timestamp},"
            f"{self.latitude:.6f},"
            f"{self.longitude:.6f},"
            f"{fuel_before:.1f},"
            f"{fuel_after:.1f},"
            f"{amount:.1f}"
        )

        return self.send_message(message)

    def send_fuel_drain(self, amount: float):
        """
        Send FLD (Fuel Drain) event.

        Format: <DEVICE_ID>,FLD,<TIMESTAMP>,<LAT>,<LON>,<FUEL_BEFORE>,<FUEL_AFTER>,<FUEL_DRAINED>
        """
        timestamp = datetime.utcnow().isoformat()
        fuel_before = self.fuel_level
        self.fuel_level -= amount
        fuel_after = self.fuel_level

        message = (
            f"{self.device_id},FLD,"
            f"{timestamp},"
            f"{self.latitude:.6f},"
            f"{self.longitude:.6f},"
            f"{fuel_before:.1f},"
            f"{fuel_after:.1f},"
            f"{amount:.1f}"
        )

        return self.send_message(message)

    def simulate_movement(self, duration_seconds: float = 1.0):
        """
        Simulate vehicle movement.

        Args:
            duration_seconds: Time delta for movement calculation
        """
        if self.speed > 0:
            # Update position based on speed and heading
            # Approximate: 1 degree latitude = 111 km
            # 1 degree longitude = 111 * cos(latitude) km

            distance_km = (self.speed * duration_seconds) / 3600.0  # km traveled

            # Convert heading to radians
            heading_rad = math.radians(self.heading)

            # Calculate lat/lon deltas
            dlat = (distance_km / 111.0) * math.cos(heading_rad)
            dlon = (distance_km / (111.0 * math.cos(math.radians(self.latitude)))) * math.sin(heading_rad)

            self.latitude += dlat
            self.longitude += dlon
            self.odometer += distance_km

            # Consume fuel (rough estimate: 0.1 L per km)
            self.fuel_level -= distance_km * 0.1

            # Update engine hours
            self.engine_hours += duration_seconds / 3600.0

    def simulate_realistic_trip(self, duration_minutes: int = 30):
        """
        Simulate a realistic trip with varying speed and direction.

        Args:
            duration_minutes: Trip duration in minutes
        """
        print(f"\n[TFMS90] Starting realistic trip simulation ({duration_minutes} minutes)")

        # Start trip
        self.send_trip_start()
        time.sleep(2)

        start_odo = self.odometer
        start_time = time.time()

        # Acceleration phase (0-60 km/h)
        print("[TFMS90] Accelerating...")
        for i in range(6):
            self.speed = 10.0 * (i + 1)
            self.heading = random.randint(0, 360)
            self.simulate_movement(1.0)
            self.send_tracking_data()
            time.sleep(5)

        # Cruising phase
        print("[TFMS90] Cruising...")
        cruise_duration = duration_minutes - 2  # Reserve 2 minutes for accel/decel

        for i in range(cruise_duration):
            # Vary speed slightly
            self.speed = random.uniform(50.0, 70.0)

            # Occasionally change direction
            if random.random() > 0.8:
                self.heading = (self.heading + random.randint(-45, 45)) % 360

            self.simulate_movement(60.0)  # 1 minute
            self.send_tracking_data()

            # Random events
            if random.random() > 0.95:
                print("[TFMS90] Sending heartbeat...")
                self.send_heartbeat_a2()

            if random.random() > 0.98:
                print("[TFMS90] Sending operating status...")
                self.send_operating_status()

            time.sleep(3)

        # Deceleration phase
        print("[TFMS90] Decelerating...")
        for i in range(6):
            self.speed = 60.0 - (10.0 * i)
            self.simulate_movement(1.0)
            self.send_tracking_data()
            time.sleep(5)

        # End trip
        end_time = time.time()
        trip_distance = self.odometer - start_odo
        trip_duration = int(end_time - start_time)

        print(f"[TFMS90] Trip complete: {trip_distance:.2f} km, {trip_duration} seconds")
        self.send_trip_end(trip_distance, trip_duration)


def main():
    """Main simulator entry point."""
    print("=" * 60)
    print("TFMS90 Device Simulator")
    print("=" * 60)

    # Configuration
    DEVICE_ID = "TFMS90_SIM_001"
    SERVER_HOST = "localhost"
    SERVER_PORT = 8888

    # Create simulator
    simulator = TFMS90Simulator(
        device_id=DEVICE_ID,
        server_host=SERVER_HOST,
        server_port=SERVER_PORT,
        start_lat=12.9716,  # Bangalore
        start_lon=77.5946
    )

    # Connect to server
    if not simulator.connect():
        print("[TFMS90] Failed to connect. Make sure the server is running.")
        return

    try:
        # Demo: Send various message types
        print("\n[TFMS90] Demo: Sending various message types...")

        # Heartbeat
        print("\n1. Sending heartbeat messages...")
        simulator.send_heartbeat_a2()
        time.sleep(2)

        # Operating status
        print("\n2. Sending operating status...")
        simulator.send_operating_status()
        time.sleep(2)

        # Fuel fill event
        print("\n3. Simulating fuel fill...")
        simulator.send_fuel_fill(30.0)
        time.sleep(2)

        # Realistic trip
        print("\n4. Starting realistic trip...")
        simulator.simulate_realistic_trip(duration_minutes=5)

        # Fuel drain event (theft simulation)
        print("\n5. Simulating fuel drain (theft)...")
        simulator.send_fuel_drain(10.0)
        time.sleep(2)

        print("\n[TFMS90] Simulation complete!")

    except KeyboardInterrupt:
        print("\n[TFMS90] Interrupted by user")

    finally:
        simulator.disconnect()


if __name__ == "__main__":
    main()
