# FleetPulse Deployment Guide

## Server Details

- **Server IP**: 164.90.223.18
- **TCP Port**: 23000
- **API Port**: 8000 (not yet implemented)
- **Platform**: Digital Ocean Droplet (Ubuntu)

## Supabase Database

- **URL**: https://ypxlpqylmxddrvhasmst.supabase.co
- **Anon Key**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlweGxwcXlsbXhkZHJ2aGFzbXN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyMzM3MjAsImV4cCI6MjA4NjgwOTcyMH0.6UYQzZSMFne8CdugAwqJhjBTIe-8YP8fL1jQeM4YJTw

Credentials are hardcoded in `src/utils/database.py`.

## Service Management

FleetPulse runs as a systemd service that:
- Starts automatically on boot
- Restarts automatically if it crashes
- Logs to `/var/log/fleetpulse.log`

### Common Commands

```bash
# View live logs
sudo tail -f /var/log/fleetpulse.log

# Stop the server
sudo systemctl stop fleetpulse

# Start the server
sudo systemctl start fleetpulse

# Restart the server (after code updates)
sudo systemctl restart fleetpulse

# Check status
sudo systemctl status fleetpulse

# View recent logs
sudo journalctl -u fleetpulse -n 100

# Follow logs in real-time
sudo journalctl -u fleetpulse -f
```

### Disable auto-start

```bash
sudo systemctl disable fleetpulse
```

### Re-enable auto-start

```bash
sudo systemctl enable fleetpulse
```

## Deploying Code Updates

When you update code on your Mac:

1. **On Mac:**
   ```bash
   cd ~/Projects/fleetpulse
   git add -A
   git commit -m "Your update message"
   git push
   ```

2. **On Server (SSH):**
   ```bash
   cd /root/fleetpulse
   git pull
   sudo systemctl restart fleetpulse
   ```

3. **Verify:**
   ```bash
   sudo systemctl status fleetpulse
   sudo tail -f /var/log/fleetpulse.log
   ```

## Firewall Configuration

```bash
# TCP port for GPS devices
sudo ufw allow 23000/tcp

# API port (future)
sudo ufw allow 8000/tcp

# SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

## Database Schema Updates

If you need to modify database schema:

1. Go to Supabase Dashboard → SQL Editor
2. Run your SQL commands
3. No server restart needed

Example:
```sql
ALTER TABLE telemetry_data
ALTER COLUMN heading TYPE DOUBLE PRECISION;
```

## Troubleshooting

### Server not starting

```bash
# Check logs for errors
sudo journalctl -u fleetpulse -n 50

# Check if port is already in use
sudo netstat -tulpn | grep 23000

# Manually test the server
cd /root/fleetpulse
python3 -m src.main
```

### Database connection issues

Check Supabase credentials in `src/utils/database.py` are correct.

### Clear Python cache after updates

```bash
cd /root/fleetpulse
find . -type d -name __pycache__ -exec rm -rf {} +
sudo systemctl restart fleetpulse
```

## Mobile App Configuration

Point your Flutter TFMS90 simulator to:
- **Host**: 164.90.223.18
- **Port**: 23000

## Monitoring

Check Supabase dashboard:
- **Table Editor** → `devices` - See registered devices
- **Table Editor** → `telemetry_data` - See GPS tracking records
- **Table Editor** → `trips` - See trip history (future feature)

## Service File Location

`/etc/systemd/system/fleetpulse.service`

If you need to edit it:
```bash
sudo nano /etc/systemd/system/fleetpulse.service
sudo systemctl daemon-reload
sudo systemctl restart fleetpulse
```
