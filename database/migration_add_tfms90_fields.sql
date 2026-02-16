-- Migration: Add TFMS90-specific fields to devices table
-- Date: 2026-02-16
-- Purpose: Support TFMS90 LG message handling with IMEI and short_device_id

-- Add new columns to devices table
ALTER TABLE devices
ADD COLUMN IF NOT EXISTS imei VARCHAR(20),
ADD COLUMN IF NOT EXISTS short_device_id INTEGER,
ADD COLUMN IF NOT EXISTS firmware_version VARCHAR(50),
ADD COLUMN IF NOT EXISTS sim_iccid VARCHAR(30);

-- Create index on IMEI for faster lookups
CREATE INDEX IF NOT EXISTS idx_devices_imei ON devices(imei);

-- Create index on short_device_id for TFMS90 devices
CREATE INDEX IF NOT EXISTS idx_devices_short_id ON devices(short_device_id);

-- Add comment
COMMENT ON COLUMN devices.imei IS 'Device IMEI (15 digits) for TFMS90 and Teltonika devices';
COMMENT ON COLUMN devices.short_device_id IS 'Short device ID (3 digits) assigned by server for TFMS90 protocol';
COMMENT ON COLUMN devices.firmware_version IS 'Device firmware version';
COMMENT ON COLUMN devices.sim_iccid IS 'SIM card ICCID number';
