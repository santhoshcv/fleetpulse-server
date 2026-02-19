'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/header';
import { StatusBadge } from '@/components/status-badge';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { supabase } from '@/lib/supabase';
import { Device, getDeviceStatus } from '@/lib/types';
import { Search, RefreshCw, Cpu, MapPin, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DeviceWithLatest extends Device {
  latest_speed?: number | null;
  latest_lat?: number | null;
  latest_lon?: number | null;
}

export default function VehiclesPage() {
  const [devices, setDevices] = useState<DeviceWithLatest[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchDevices = async () => {
    setLoading(true);

    // Get all devices
    const { data: devicesData, error } = await supabase
      .from('devices')
      .select('*')
      .order('last_seen', { ascending: false });

    if (error || !devicesData) { setLoading(false); return; }

    // For each device, get the latest TD record
    const enriched = await Promise.all(
      devicesData.map(async (device) => {
        const { data: latest } = await supabase
          .from('telemetry_data')
          .select('speed, latitude, longitude')
          .eq('device_id', device.device_id)
          .eq('message_type', 'TD')
          .order('timestamp', { ascending: false })
          .limit(1)
          .maybeSingle();

        return {
          ...device,
          latest_speed: latest?.speed,
          latest_lat: latest?.latitude,
          latest_lon: latest?.longitude,
        };
      })
    );

    setDevices(enriched);
    setLoading(false);
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, []);

  const filtered = devices.filter(d =>
    d.device_id.toLowerCase().includes(search.toLowerCase()) ||
    (d.imei && d.imei.includes(search))
  );

  const online = devices.filter(d => getDeviceStatus(d.last_seen) === 'online').length;
  const moving = devices.filter(d => (d.latest_speed ?? 0) > 2).length;

  return (
    <>
      <Header title="Vehicle Fleet" />
      <main className="p-6 space-y-4">

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-4 pb-4">
              <p className="text-sm text-muted-foreground">Total Devices</p>
              <p className="text-3xl font-heading font-bold text-brand-primary">{devices.length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 pb-4">
              <p className="text-sm text-muted-foreground">Online Now</p>
              <p className="text-3xl font-heading font-bold text-green-600">{online}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 pb-4">
              <p className="text-sm text-muted-foreground">Moving</p>
              <p className="text-3xl font-heading font-bold text-blue-600">{moving}</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardContent className="pt-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-heading font-semibold">All Devices</h2>
              <div className="flex items-center gap-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search device or IMEI..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="w-56"
                />
                <Button variant="outline" size="icon" onClick={fetchDevices} disabled={loading}>
                  <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-10">
                <RefreshCw className="h-5 w-5 animate-spin text-brand-primary mr-2" />
                <span className="text-muted-foreground">Loading fleet data...</span>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Device</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Protocol</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Status</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Speed</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Location</th>
                      <th className="pb-3 font-medium text-muted-foreground">Last Seen</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map(device => {
                      const status = getDeviceStatus(device.last_seen);
                      const isMoving = (device.latest_speed ?? 0) > 2;
                      return (
                        <tr key={device.device_id} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="py-3 pr-4">
                            <div className="flex items-center gap-2">
                              <Cpu className="h-4 w-4 text-brand-primary" />
                              <div>
                                <p className="font-mono font-medium">{device.device_id}</p>
                                {device.imei && (
                                  <p className="text-xs text-muted-foreground">IMEI: {device.imei}</p>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="py-3 pr-4">
                            <Badge variant="outline"
                              className={device.protocol === 'tfms90'
                                ? 'border-brand-primary text-brand-primary'
                                : 'border-green-500 text-green-600'}>
                              {device.protocol?.toUpperCase()}
                            </Badge>
                          </td>
                          <td className="py-3 pr-4">
                            <StatusBadge status={isMoving ? 'moving' : status as any} />
                          </td>
                          <td className="py-3 pr-4 font-medium">
                            {device.latest_speed != null
                              ? `${Math.round(device.latest_speed)} km/h`
                              : '—'}
                          </td>
                          <td className="py-3 pr-4 text-xs text-muted-foreground">
                            {device.latest_lat != null && device.latest_lon != null ? (
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                {device.latest_lat.toFixed(4)}, {device.latest_lon.toFixed(4)}
                              </div>
                            ) : '—'}
                          </td>
                          <td className="py-3 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {device.last_seen
                                ? new Date(device.last_seen).toLocaleString()
                                : 'Never'}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </>
  );
}
