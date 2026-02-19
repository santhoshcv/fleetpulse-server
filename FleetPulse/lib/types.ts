// FleetPulse Database Types
// Matches existing production Supabase schema

export interface Device {
  device_id: string;           // e.g. "TFMS90_100", "860000000000001"
  protocol: 'tfms90' | 'teltonika' | string;
  imei: string | null;         // 15-digit IMEI
  short_device_id: number | null; // 100-999, TFMS90 only
  firmware_version: string | null;
  sim_iccid: string | null;
  is_active: boolean;
  last_seen: string | null;    // ISO timestamptz
  created_at: string | null;
  name: string | null;
  vehicle_id: string | null;
}

export interface TelemetryData {
  id: string;
  device_id: string;
  message_type: MessageType;
  timestamp: string;           // ISO timestamptz
  latitude: number | null;
  longitude: number | null;
  speed: number | null;        // km/h
  heading: number | null;      // degrees
  fuel_level: number | null;
  battery_voltage: number | null;
  odometer: number | null;
  gsm_signal: number | null;
  io_elements: Record<string, unknown> | null;
  raw_data: string | null;
}

export type MessageType =
  | 'TS'        // Trip Start
  | 'TD'        // Tracking Data
  | 'TE'        // Trip End
  | 'HB'        // Heartbeat
  | 'FLF'       // Fuel Fill
  | 'FLD'       // Fuel Drain
  | 'HA2'       // Harsh Acceleration
  | 'HB2'       // Harsh Braking
  | 'HC2'       // Harsh Cornering
  | 'OS3'       // Overspeed
  | 'STAT'      // Status
  | 'codec_0x8' // Teltonika Codec 8
  | string;

export interface Trip {
  device_id: string;
  trip_number: number;
  start_time: string;
  end_time: string | null;
  start_lat: number;
  start_lon: number;
  end_lat: number | null;
  end_lon: number | null;
  max_speed: number;
  avg_speed: number;
  duration_minutes: number | null;
  record_count: number;
}

// Device status helper
export function getDeviceStatus(last_seen: string | null): 'online' | 'idle' | 'offline' {
  if (!last_seen) return 'offline';
  const diff = Date.now() - new Date(last_seen).getTime();
  if (diff < 5 * 60 * 1000) return 'online';      // < 5 minutes
  if (diff < 30 * 60 * 1000) return 'idle';        // < 30 minutes
  return 'offline';
}
