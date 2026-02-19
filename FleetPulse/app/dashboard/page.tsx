'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Header } from '@/components/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/status-badge';
import { supabase } from '@/lib/supabase';
import { getDeviceStatus } from '@/lib/types';
import type { DeviceMarker } from '@/components/map';
import { Car, MapPin, Route, RefreshCw, Gauge } from 'lucide-react';

// Dynamic import - map uses Leaflet which cannot run on server
const FleetMap = dynamic(() => import('@/components/map'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[500px] items-center justify-center rounded-lg bg-muted">
      <div className="text-center">
        <MapPin className="mx-auto h-10 w-10 text-brand-primary mb-2 animate-pulse" />
        <p className="text-sm text-muted-foreground">Loading map...</p>
      </div>
    </div>
  ),
});

interface LiveDevice {
  device_id: string;
  protocol: string;
  last_seen: string | null;
  latest_speed: number | null;
  latest_lat: number | null;
  latest_lon: number | null;
  latest_heading: number;
  status: 'online' | 'idle' | 'offline';
}

export default function ClientDashboard() {
  const [devices, setDevices] = useState<LiveDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [tripsToday, setTripsToday] = useState(0);
  const [recordsToday, setRecordsToday] = useState(0);
  const [focusedDeviceId, setFocusedDeviceId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);

    // Get all devices
    const { data: devicesData } = await supabase
      .from('devices')
      .select('device_id, protocol, last_seen, is_active')
      .order('last_seen', { ascending: false });

    if (!devicesData) { setLoading(false); return; }

    // Enrich each device with latest telemetry
    const enriched: LiveDevice[] = await Promise.all(
      devicesData.map(async (device) => {
        // Get latest record with valid GPS (TD for TFMS90, codec_0x8 for Teltonika)
        const { data: latest } = await supabase
          .from('telemetry_data')
          .select('speed, latitude, longitude, heading')
          .eq('device_id', device.device_id)
          .not('latitude', 'is', null)
          .not('longitude', 'is', null)
          .order('timestamp', { ascending: false })
          .limit(1)
          .maybeSingle();

        const status = getDeviceStatus(device.last_seen);
        return {
          device_id: device.device_id,
          protocol: device.protocol,
          last_seen: device.last_seen,
          latest_speed: latest?.speed ?? null,
          latest_lat: latest?.latitude ?? null,
          latest_lon: latest?.longitude ?? null,
          latest_heading: latest?.heading ?? 0,
          status: status as 'online' | 'idle' | 'offline',
        };
      })
    );

    setDevices(enriched);

    // Stats
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);

    const { count: trips } = await supabase
      .from('telemetry_data')
      .select('id', { count: 'exact', head: true })
      .eq('message_type', 'TS')
      .gte('timestamp', todayStart.toISOString());

    const { count: records } = await supabase
      .from('telemetry_data')
      .select('id', { count: 'exact', head: true })
      .gte('timestamp', todayStart.toISOString());

    setTripsToday(trips || 0);
    setRecordsToday(records || 0);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const onlineCount = devices.filter(d => d.status === 'online').length;
  const movingCount = devices.filter(d => (d.latest_speed ?? 0) > 2).length;

  // Build marker list for map (only devices with valid coords)
  const mapMarkers: DeviceMarker[] = devices
    .filter(d => d.latest_lat != null && d.latest_lon != null)
    .map(d => ({
      device_id: d.device_id,
      lat: d.latest_lat!,
      lon: d.latest_lon!,
      speed: d.latest_speed ?? 0,
      heading: d.latest_heading,
      status: d.status,
      last_seen: d.last_seen,
    }));

  const formatRelative = (ts: string | null) => {
    if (!ts) return 'Never';
    const diff = Math.round((Date.now() - new Date(ts).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  };

  return (
    <>
      <Header title="Live Map" />

      <main className="p-6 space-y-6">
        {/* Summary stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Vehicles</p>
                  <p className="text-3xl font-heading font-bold text-brand-primary">{devices.length}</p>
                  <p className="text-xs text-muted-foreground mt-1">{onlineCount} online</p>
                </div>
                <Car className="h-8 w-8 text-brand-primary/30" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Moving Now</p>
                  <p className="text-3xl font-heading font-bold text-green-600">{movingCount}</p>
                  <p className="text-xs text-muted-foreground mt-1">speed &gt; 2 km/h</p>
                </div>
                <Gauge className="h-8 w-8 text-green-600/30" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Trips Today</p>
                  <p className="text-3xl font-heading font-bold text-amber-500">{tripsToday}</p>
                  <p className="text-xs text-muted-foreground mt-1">TS events</p>
                </div>
                <Route className="h-8 w-8 text-amber-500/30" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Records Today</p>
                  <p className="text-3xl font-heading font-bold text-blue-600">{recordsToday.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground mt-1">telemetry points</p>
                </div>
                <MapPin className="h-8 w-8 text-blue-600/30" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Map + Vehicle list */}
        <div className="grid gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="font-heading">Real-Time Vehicle Tracking</CardTitle>
              <button
                onClick={fetchData}
                disabled={loading}
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
              >
                <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
                {loading ? 'Updating...' : 'Refresh'}
              </button>
            </CardHeader>
            <CardContent>
              {mapMarkers.length === 0 && !loading ? (
                <div className="flex h-[500px] items-center justify-center rounded-lg bg-muted">
                  <div className="text-center">
                    <MapPin className="mx-auto h-10 w-10 text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">No GPS positions available</p>
                    <p className="text-xs text-muted-foreground mt-1">Waiting for TD telemetry records</p>
                  </div>
                </div>
              ) : (
                <FleetMap
                devices={mapMarkers}
                height={500}
                focusedDeviceId={focusedDeviceId}
                onFocusCleared={() => setFocusedDeviceId(null)}
              />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="font-heading">Vehicle Status</CardTitle>
            </CardHeader>
            <CardContent>
              {loading && devices.length === 0 ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="h-4 w-4 animate-spin text-brand-primary mr-2" />
                  <span className="text-sm text-muted-foreground">Loading...</span>
                </div>
              ) : (
                <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
                  {devices.map(device => (
                    <div
                      key={device.device_id}
                      className={`space-y-2 border-b pb-3 last:border-0 cursor-pointer rounded px-1 transition-colors
                        ${focusedDeviceId === device.device_id ? 'bg-brand-primary/10' : 'hover:bg-muted/50'}`}
                      onClick={() => {
                        if (device.latest_lat && device.latest_lon) {
                          setFocusedDeviceId(device.device_id);
                        }
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-semibold text-sm">{device.device_id}</span>
                        <StatusBadge status={
                          (device.latest_speed ?? 0) > 2 ? 'moving' as any : device.status as any
                        } />
                      </div>
                      <div className="text-xs text-muted-foreground space-y-0.5">
                        {device.latest_lat != null && device.latest_lon != null ? (
                          <p className="flex items-center gap-1">
                            <MapPin className="h-3 w-3 flex-shrink-0" />
                            {device.latest_lat.toFixed(4)}, {device.latest_lon.toFixed(4)}
                          </p>
                        ) : (
                          <p className="flex items-center gap-1">
                            <MapPin className="h-3 w-3 flex-shrink-0" />
                            No position
                          </p>
                        )}
                        <div className="flex items-center justify-between">
                          <span>
                            {device.latest_speed != null
                              ? `${Math.round(device.latest_speed)} km/h`
                              : '— km/h'}
                          </span>
                          <span>{formatRelative(device.last_seen)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  {devices.length === 0 && (
                    <p className="text-center text-sm text-muted-foreground py-4">No devices found</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  );
}
