# FleetPulse Simulators

Device simulators for testing FleetPulse platform.

## TFMS90 Simulator

Python-based simulator for TFMS90 text-based protocol.

### Features

- Sends realistic GPS tracking data
- Simulates complete trips with acceleration/deceleration
- Supports all TFMS90 message types:
  - **TD**: Tracking Data (location, speed, fuel, etc.)
  - **TS**: Trip Start
  - **TE**: Trip End
  - **HA2, HB2, HC2**: Heartbeat messages
  - **OS3**: Operating Status
  - **FLF**: Fuel Fill event
  - **FLD**: Fuel Drain event

### Usage

```bash
# Basic usage
python simulators/tfms90_simulator.py

# Customize device ID and server
python simulators/tfms90_simulator.py --device-id TFMS90_001 --host 192.168.1.100 --port 8888
```

### Simulation Scenarios

The simulator demonstrates:

1. **Heartbeat Messages**: Periodic keep-alive signals
2. **Operating Status**: Battery, fuel, engine hours
3. **Fuel Fill**: Refueling events
4. **Realistic Trip**:
   - Ignition ON → Trip Start
   - Acceleration phase (0-60 km/h)
   - Cruising with varying speed and direction
   - Random heartbeats and status updates
   - Deceleration phase
   - Ignition OFF → Trip End
5. **Fuel Drain**: Theft detection simulation

### Configuration

Edit the `main()` function in `tfms90_simulator.py` to customize:

- `DEVICE_ID`: Device identifier
- `SERVER_HOST`: FleetPulse server IP/hostname
- `SERVER_PORT`: TCP port (default: 8888)
- Starting location (lat/lon)
- Trip duration
- Message intervals

## Teltonika Simulator

For Teltonika Codec 8E testing, use the existing **Flutter simulator** mentioned by the user.

## Testing Tips

1. **Start the FleetPulse server first**:
   ```bash
   python src/main.py
   ```

2. **Run the simulator** in a separate terminal:
   ```bash
   python simulators/tfms90_simulator.py
   ```

3. **Monitor server logs** to see incoming data processing

4. **Check API** for stored data:
   ```bash
   curl http://localhost:8000/api/devices/TFMS90_SIM_001/telemetry/latest
   ```

5. **View in Flutter app** to see real-time tracking
