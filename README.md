# FleetPulse Server

Multi-protocol GPS tracking platform supporting TFMS90 and other protocols.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python3 -m src.main
```

The server will listen on port 23000 for GPS device connections.

## Supported Protocols

- TFMS90 (text-based)

## Database

Uses Supabase for data storage. Credentials are hardcoded in `src/utils/database.py`.
