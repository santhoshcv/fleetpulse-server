# FleetPulse TODO List

## Completed ✅

- [x] TFMS90 Protocol Adapter
- [x] Protocol Auto-detection
- [x] Supabase Database Integration
- [x] Connection Handler
- [x] Device Registration
- [x] Telemetry Storage
- [x] Digital Ocean Deployment
- [x] Systemd Service Setup
- [x] Flutter TFMS90 Simulator (Mobile App)
- [x] All TFMS90 Message Types (TS, TD, TE, HB, FLF, FLD, HA2, HB2, HC2, OS3, STAT)
- [x] Database Schema (devices, telemetry_data)
- [x] Auto-restart on crash
- [x] Auto-start on boot

## Server Implementation

### High Priority 🔴

- [ ] **Teltonika Codec 8E Protocol Support**
  - [ ] Create teltonika adapter (`src/adapters/teltonika/`)
  - [ ] Implement binary protocol parser
  - [ ] Add CRC validation
  - [ ] Parse AVL data records
  - [ ] Map IO elements
  - [ ] Add detection logic in protocol_router
  - [ ] Test with Teltonika device/simulator
  - [ ] Update PROTOCOLS.md documentation

### Medium Priority 🟡

- [ ] REST API Implementation (`src/api/server.py`)
  - [ ] GET /api/devices - List all devices
  - [ ] GET /api/devices/{id} - Get device details
  - [ ] GET /api/devices/{id}/telemetry - Get device telemetry
  - [ ] GET /api/devices/{id}/location - Get latest location
  - [ ] GET /api/devices/{id}/trips - Get trip history
  - [ ] WebSocket support for real-time updates

- [ ] Trip Manager
  - [ ] Auto-detect trip start/end based on ignition/movement
  - [ ] Calculate trip distance
  - [ ] Calculate trip duration
  - [ ] Track fuel consumption per trip
  - [ ] Store in trips table

- [ ] Event Processing
  - [ ] Geofence violations
  - [ ] Speed alerts
  - [ ] Fuel anomaly detection
  - [ ] Harsh driving events
  - [ ] Store in events table

### Low Priority 🟢

- [ ] Enhanced Logging
  - [ ] Structured JSON logs
  - [ ] Log rotation
  - [ ] Separate error logs
  - [ ] Performance metrics

- [ ] Security
  - [ ] Device authentication/whitelisting
  - [ ] API authentication (JWT)
  - [ ] Rate limiting
  - [ ] SSL/TLS for TCP connections

- [ ] Monitoring & Alerts
  - [ ] Prometheus metrics
  - [ ] Grafana dashboards
  - [ ] Email/SMS alerts
  - [ ] Uptime monitoring

- [ ] Performance Optimization
  - [ ] Redis caching for device states
  - [ ] Message queue (RabbitMQ/Redis)
  - [ ] Batch database writes
  - [ ] Connection pooling

- [ ] Additional Protocols
  - [ ] GT06 Protocol
  - [ ] Queclink Protocol
  - [ ] Concox Protocol

## Hardware & Firmware

### TFMS90 Device Firmware Updates

**Status:** To be documented

**Requirements:**
- Document current firmware version
- Firmware update process
- OTA (Over-The-Air) update capability
- Firmware configuration settings
- Device provisioning process

**Action Items:**
- [ ] Document TFMS90 device specifications
- [ ] Document firmware update procedure
- [ ] Create firmware configuration guide
- [ ] Test firmware OTA updates
- [ ] Document device provisioning steps

### Teltonika Device Setup

**When Teltonika protocol is added:**
- [ ] Document device configuration
- [ ] Server settings (IP, Port, APN)
- [ ] Data acquisition settings
- [ ] IO element mapping
- [ ] Firmware requirements

## Frontend (Flutter App)

### Current Status
- ✅ TFMS90 Simulator working
- ✅ Connects to production server
- ✅ Sends real GPS data

### Future Features
- [ ] Production Fleet Management App
  - [ ] Real-time device tracking on map
  - [ ] Trip history and playback
  - [ ] Fuel monitoring dashboard
  - [ ] Alerts and notifications
  - [ ] Reports (daily/weekly/monthly)
  - [ ] Driver behavior analytics
  - [ ] Geofence management
  - [ ] Multi-device support
  - [ ] User authentication
  - [ ] Role-based access control

## Testing

- [ ] Unit tests for protocol adapters
- [ ] Integration tests for database operations
- [ ] Load testing (multiple concurrent devices)
- [ ] Teltonika device testing with real hardware
- [ ] TFMS90 device testing with real hardware
- [ ] API endpoint tests
- [ ] WebSocket connection tests

## Documentation

- [x] README.md
- [x] DEPLOYMENT.md
- [x] PROTOCOLS.md
- [x] TODO.md
- [ ] API_DOCUMENTATION.md
- [ ] HARDWARE_SETUP.md (TFMS90, Teltonika)
- [ ] FIRMWARE_UPDATE.md
- [ ] TROUBLESHOOTING.md
- [ ] ARCHITECTURE.md (detailed)

## DevOps

- [ ] Docker containerization
- [ ] Docker Compose for local development
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated testing
- [ ] Automated deployment
- [ ] Database migrations
- [ ] Backup and recovery procedures
- [ ] Staging environment

---

## Next Immediate Steps

1. **Add Teltonika Codec 8E Support** (4-6 hours)
2. **Document TFMS90 Firmware Update Process** (1-2 hours)
3. **Implement REST API** (6-8 hours)
4. **Test with Real Teltonika Device** (2-3 hours)
5. **Implement Trip Manager** (4-6 hours)
