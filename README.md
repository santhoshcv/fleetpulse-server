# FleetPulse - Multi-Protocol GPS Tracking Platform

A robust, scalable GPS tracking platform supporting multiple telemetry protocols with real-time data processing.

## Architecture

FleetPulse follows a clean layered architecture:

```
src/
├── adapters/          # Protocol-specific parsers
│   ├── teltonika/     # Teltonika Codec 8E (binary)
│   └── tfms90/        # TFMS90 (text-based TCP)
├── handlers/          # Connection and message handlers
├── managers/          # Business logic and state management
├── api/              # REST API endpoints
├── models/           # Database models
└── utils/            # Shared utilities

simulators/           # Protocol simulators for testing
tests/               # Unit and integration tests
config/              # Configuration files
```

## Supported Protocols

### 1. Teltonika Codec 8E
- **Devices**: FMB920, FMA120
- **Type**: Binary protocol
- **Features**: AVL data packets, I/O elements, extended format

### 2. TFMS90
- **Type**: Text-based TCP protocol
- **Messages**: TD, TS, TE, HA2, HB2, HC2, OS3, FLF, FLD

## Tech Stack

- **Backend**: Python (asyncio TCP server)
- **Database**: Supabase (PostgreSQL)
- **API**: REST API for Flutter frontend
- **Testing**: Python simulators + Flutter simulator (Teltonika)

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the TCP server
python src/main.py

# Run API server
python src/api/server.py
```

## Development

```bash
# Run tests
pytest tests/

# Run TFMS90 simulator
python simulators/tfms90_simulator.py
```

## Project Status

- [x] Project structure
- [ ] Teltonika Codec 8E adapter
- [ ] TFMS90 adapter
- [ ] TCP server
- [ ] REST API
- [ ] TFMS90 simulator
