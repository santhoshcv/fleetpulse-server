# FleetPulse Quick Start Guide

Get FleetPulse up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- Supabase account (free tier works)
- Git (optional)

## Step 1: Clone or Download

```bash
cd /Users/santhoshvargheese/Projects/fleetpulse
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Setup Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the database to be ready
3. Go to **SQL Editor** in your Supabase dashboard
4. Copy and paste the contents of `database/schema.sql`
5. Click **Run** to create all tables

## Step 5: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

To find these values in Supabase:
- Go to **Settings** → **API**
- **URL**: Project URL
- **anon public**: Use for SUPABASE_KEY
- **service_role**: Use for SUPABASE_SERVICE_KEY (⚠️ Keep secret!)

## Step 6: Start the TCP Server

```bash
python src/main.py
```

You should see:
```
============================================================
FleetPulse Multi-Protocol GPS Tracking Server
============================================================
TCP Server: 0.0.0.0:8888
Supported Protocols: Teltonika Codec 8E, TFMS90
Database: https://your-project.supabase.co
============================================================
Server started on ('0.0.0.0', 8888)
Waiting for connections...
```

## Step 7: Start the API Server (Optional)

In a new terminal:

```bash
source venv/bin/activate
python src/api/server.py
```

Or using uvicorn:

```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: http://localhost:8000

## Step 8: Test with Simulator

In a new terminal:

```bash
source venv/bin/activate
python simulators/tfms90_simulator.py
```

You should see the simulator connect and send data to the server.

## Verify Everything Works

1. **Check Server Logs**: You should see device connection and telemetry messages

2. **Check API**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/devices/TFMS90_SIM_001/telemetry/latest
   ```

3. **Check Supabase Dashboard**:
   - Go to **Table Editor**
   - View `devices` table - should have 1 device
   - View `telemetry_data` table - should have multiple records

## Connect Real Devices

### Teltonika (FMB920/FMA120)

1. Configure device to send data to your server IP and port 8888
2. Use Codec 8 or 8E protocol
3. Device will automatically register on first connection

### TFMS90 Devices

1. Configure device server IP: `your-server-ip`
2. Configure port: `8888`
3. Device will send text-based messages

## API Endpoints

Once running, visit http://localhost:8000/docs for interactive API documentation.

Key endpoints:
- `GET /api/devices/{device_id}` - Get device info
- `GET /api/devices/{device_id}/telemetry` - Get telemetry history
- `GET /api/devices/{device_id}/telemetry/latest` - Get latest position
- `GET /api/devices/{device_id}/location` - Get current location
- `GET /api/devices/{device_id}/trips/active` - Get active trip

## Troubleshooting

### Server won't start
- Check if port 8888 is already in use: `lsof -i :8888`
- Check `.env` file has correct Supabase credentials
- Verify Python version: `python --version` (should be 3.8+)

### Device not connecting
- Check firewall allows incoming connections on port 8888
- Verify device configuration (IP, port, protocol)
- Check server logs for connection attempts

### Database errors
- Verify Supabase credentials in `.env`
- Check if schema.sql was run successfully
- Verify RLS policies allow service_role access

### Simulator fails
- Make sure TCP server is running first
- Check SERVER_HOST and SERVER_PORT in simulator code
- Verify network connectivity

## Production Deployment

For production:

1. **Security**:
   - Use environment variables for secrets
   - Enable HTTPS/TLS for API
   - Configure proper CORS origins
   - Use firewall rules

2. **Performance**:
   - Adjust `MAX_CONNECTIONS` in .env
   - Consider load balancing for multiple servers
   - Setup database connection pooling
   - Enable database indexes (already in schema.sql)

3. **Monitoring**:
   - Setup logging to files
   - Monitor server health
   - Setup alerts for downtime
   - Track database performance

## Next Steps

- Connect your Flutter app to the API
- Customize protocol adapters for your needs
- Add geofencing and alerts
- Setup webhooks for real-time notifications
- Create dashboards and reports

## Support

For issues and questions:
- Check the documentation
- Review server logs
- Test with the simulator first
- Verify database schema is correct

Happy tracking! 🚗📍
