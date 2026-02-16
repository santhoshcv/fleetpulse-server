# FleetPulse Architecture

## Overview

FleetPulse is a multi-protocol GPS tracking platform built with a clean layered architecture designed for scalability and maintainability.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GPS Devices                               │
│  ┌──────────────┐              ┌──────────────┐             │
│  │ Teltonika    │              │   TFMS90     │             │
│  │ FMB920/FMA120│              │   Devices    │             │
│  └──────┬───────┘              └──────┬───────┘             │
└─────────┼──────────────────────────────┼───────────────────┘
          │                              │
          │ Binary (Codec 8E)            │ Text-based
          │ TCP                          │ TCP
          │                              │
┌─────────▼──────────────────────────────▼───────────────────┐
│              FleetPulse TCP Server (:8888)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Protocol Router (Auto-detection)            │    │
│  └───────┬─────────────────────────────────┬──────────┘    │
│          │                                 │                │
│  ┌───────▼──────────┐            ┌────────▼─────────┐      │
│  │   Teltonika      │            │   TFMS90         │      │
│  │   Codec 8E       │            │   Adapter        │      │
│  │   Adapter        │            │                  │      │
│  └───────┬──────────┘            └────────┬─────────┘      │
│          │                                │                │
│  ┌───────▼────────────────────────────────▼──────────┐     │
│  │         Connection Handler                        │     │
│  │  • Device authentication                          │     │
│  │  • Message parsing                                │     │
│  │  • Acknowledgment                                 │     │
│  └───────┬───────────────────────────────────────────┘     │
│          │                                                  │
│  ┌───────▼───────────────────────────────────────────┐     │
│  │         Business Logic Managers                   │     │
│  │  • Device Manager                                 │     │
│  │  • Trip Manager (Auto-detection)                  │     │
│  └───────┬───────────────────────────────────────────┘     │
└──────────┼──────────────────────────────────────────────────┘
           │
           │
┌──────────▼──────────────────────────────────────────────────┐
│                    Supabase (PostgreSQL)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ devices  │  │telemetry │  │  trips   │  │  events  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────┬──────────────────────────────────────────────────┘
           │
           │
┌──────────▼──────────────────────────────────────────────────┐
│              REST API Server (:8000)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │              FastAPI Endpoints                     │     │
│  │  • GET /api/devices/{id}                           │     │
│  │  • GET /api/devices/{id}/telemetry                 │     │
│  │  • GET /api/devices/{id}/location                  │     │
│  │  • GET /api/devices/{id}/trips/active              │     │
│  └────────────────────────────────────────────────────┘     │
└──────────┬──────────────────────────────────────────────────┘
           │
           │ HTTP/REST
           │
┌──────────▼──────────────────────────────────────────────────┐
│                   Flutter Frontend                           │
│  • Real-time tracking                                        │
│  • Trip history                                              │
│  • Reports & analytics                                       │
└──────────────────────────────────────────────────────────────┘
```

## Layer Architecture

### 1. Adapters Layer (`src/adapters/`)

Protocol-specific parsers that convert raw device data into standardized telemetry.

**Teltonika Codec 8E** (`adapters/teltonika/`)
- Binary protocol parser
- Handles AVL data packets
- Parses IO elements
- Extracts GPS, speed, ignition, fuel, etc.

**TFMS90** (`adapters/tfms90/`)
- Text-based protocol parser
- Message types: TD, TS, TE, HA2, HB2, HC2, OS3, FLF, FLD
- CSV-style parsing
- Flexible timestamp handling

### 2. Handlers Layer (`src/handlers/`)

Connection and protocol management.

**Protocol Router**
- Auto-detects protocol from initial data
- Routes to appropriate adapter
- Binary vs text detection

**Connection Handler**
- Manages TCP connections
- Device authentication
- Message acknowledgment
- Error handling

### 3. Managers Layer (`src/managers/`)

Business logic and state management.

**Device Manager**
- Device registration
- Connection state tracking
- Device metadata

**Trip Manager**
- Automatic trip detection
- Trip start/end events
- Distance and duration calculation

### 4. API Layer (`src/api/`)

REST API for frontend integration.

**FastAPI Server**
- RESTful endpoints
- CORS support
- Pydantic models
- Auto-generated docs

### 5. Models Layer (`src/models/`)

Data models and structures.

**Device Model**
- Device information
- Protocol type
- Connection state

**Telemetry Model**
- GPS coordinates
- Speed, heading, altitude
- Fuel, ignition, odometer
- IO elements
- Protocol-agnostic

**Trip Model**
- Start/end times
- Distance, duration
- Start/end locations

### 6. Utils Layer (`src/utils/`)

Shared utilities and helpers.

**Database Client**
- Supabase integration
- CRUD operations
- Batch inserts
- Connection pooling

**Logger**
- Structured logging
- Console and file output
- Configurable levels

## Data Flow

### Device Connection Flow

1. **Device connects** to TCP server (port 8888)
2. **Protocol Router** detects protocol from initial packet
3. **Adapter** extracts device ID (IMEI)
4. **Connection Handler** authenticates device
5. **Device registered/updated** in database
6. **Acknowledgment** sent to device
7. **Connection maintained** for data packets

### Telemetry Processing Flow

1. **Device sends** telemetry packet
2. **Adapter parses** raw data into TelemetryData objects
3. **Trip Manager** checks for trip events
4. **Database Client** stores telemetry records
5. **Device last_seen** updated
6. **Acknowledgment** sent to device
7. **API serves** data to frontend

### API Request Flow

1. **Flutter app** makes HTTP request
2. **FastAPI** routes to endpoint
3. **Database Client** queries Supabase
4. **Data serialized** to JSON
5. **Response** sent to app
6. **Flutter app** updates UI

## Protocol Support

### Teltonika Codec 8E

**Binary Format:**
```
[Preamble][Data Length][Codec ID][Records][CRC]
```

**Features:**
- High-frequency data (1 second intervals)
- Rich IO elements (200+ parameters)
- Efficient binary encoding
- CRC validation

**Supported Devices:**
- FMB920 (vehicle tracker)
- FMA120 (asset tracker)
- FMB125, FMB130, etc.

### TFMS90

**Text Format:**
```
DEVICE_ID,MESSAGE_TYPE,FIELD1,FIELD2,...
```

**Message Types:**
- **TD**: Tracking data (GPS, speed, fuel)
- **TS**: Trip start event
- **TE**: Trip end event
- **HA2/HB2/HC2**: Heartbeat variants
- **OS3**: Operating status
- **FLF**: Fuel fill event
- **FLD**: Fuel drain event

## Database Schema

### Tables

**devices**
- Device registration
- Protocol type
- Connection state
- Last seen timestamp

**telemetry_data**
- GPS coordinates
- Speed, heading, altitude
- Fuel, odometer, ignition
- IO elements (JSONB)
- Protocol and message type

**trips**
- Auto-detected journeys
- Start/end times and locations
- Distance, duration, speeds
- Active trip flag

**events**
- Alerts and notifications
- Geofence violations
- System events

**vehicles**
- Vehicle metadata
- Registration, make, model
- Fuel capacity

## Scalability

### Horizontal Scaling

- **Multiple server instances** with load balancer
- **Database connection pooling**
- **Stateless connection handlers**
- **Independent protocol adapters**

### Performance Optimizations

- **Batch inserts** for telemetry
- **Database indexes** on common queries
- **Async I/O** with asyncio
- **Connection reuse**

### Monitoring

- **Structured logging**
- **Connection metrics**
- **Database performance**
- **API response times**

## Security

### Network Security

- Firewall rules for TCP port
- IP whitelisting (optional)
- TLS/SSL for API (production)

### Database Security

- Row Level Security (RLS)
- Service role for backend
- Anon key for public API
- Encrypted connections

### Authentication

- Device authentication via IMEI
- API authentication (to be added)
- JWT tokens (future)

## Testing

### Simulators

**TFMS90 Simulator** (`simulators/tfms90_simulator.py`)
- Realistic trip simulation
- All message types
- Configurable scenarios
- Fuel events

**Teltonika Simulator**
- Flutter-based (existing)
- Binary protocol
- Codec 8E packets

### Unit Tests

- Protocol adapter tests
- Message parsing validation
- Database operations
- API endpoint tests

## Deployment

### Development

```bash
# TCP Server
python src/main.py

# API Server
python src/api/server.py

# Simulator
python simulators/tfms90_simulator.py
```

### Production

- Docker containers
- Process manager (systemd, supervisor)
- Reverse proxy (nginx)
- SSL certificates
- Monitoring (Prometheus, Grafana)

## Future Enhancements

### Protocol Support

- [ ] Queclink protocol
- [ ] GT06 protocol
- [ ] Concox protocol
- [ ] GPRS-based protocols

### Features

- [ ] Geofencing
- [ ] Real-time alerts
- [ ] Driver behavior analytics
- [ ] Fuel consumption analysis
- [ ] Maintenance scheduling
- [ ] Custom reports

### Performance

- [ ] Redis caching
- [ ] Message queuing (RabbitMQ)
- [ ] Time-series database (TimescaleDB)
- [ ] WebSocket for real-time updates

### Integration

- [ ] Webhooks
- [ ] MQTT support
- [ ] Third-party integrations
- [ ] Mobile SDK

## Technology Stack

**Backend:**
- Python 3.8+
- asyncio (async TCP)
- FastAPI (REST API)
- Supabase (PostgreSQL)

**Frontend:**
- Flutter (mobile/web)
- REST client
- Real-time maps

**Infrastructure:**
- Supabase (managed PostgreSQL)
- Docker (containerization)
- Cloud hosting (AWS, GCP, Azure)

**Testing:**
- pytest
- Python simulators
- Flutter simulator (Teltonika)

## Conclusion

FleetPulse provides a robust, scalable foundation for multi-protocol GPS tracking. The clean architecture allows easy addition of new protocols and features while maintaining code quality and performance.
