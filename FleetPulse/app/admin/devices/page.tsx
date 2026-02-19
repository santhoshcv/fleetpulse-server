'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/header';
import { StatusBadge } from '@/components/status-badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { supabase } from '@/lib/supabase';
import { Device, getDeviceStatus } from '@/lib/types';
import { Cpu, Search, RefreshCw } from 'lucide-react';

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchDevices = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from('devices')
      .select('*')
      .order('last_seen', { ascending: false });

    if (!error && data) setDevices(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchDevices();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDevices, 30000);
    return () => clearInterval(interval);
  }, []);

  const filtered = devices.filter(d =>
    d.device_id.toLowerCase().includes(search.toLowerCase()) ||
    (d.imei && d.imei.includes(search)) ||
    (d.protocol && d.protocol.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <>
      <Header title="Device Inventory" />
      <main className="p-6">
        <Card>
          <CardContent className="pt-6">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-heading font-semibold">GPS Devices</h2>
                <p className="text-sm text-muted-foreground">
                  {devices.length} total devices · {devices.filter(d => d.is_active).length} active
                </p>
              </div>
              <Button
                variant="outline"
                onClick={fetchDevices}
                disabled={loading}
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>

            <div className="mb-4 flex items-center gap-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by device ID, IMEI, or protocol..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="max-w-sm"
              />
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="h-6 w-6 animate-spin text-brand-primary" />
                <span className="ml-2 text-muted-foreground">Loading devices...</span>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left">
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Device ID</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Protocol</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">IMEI</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Short ID</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Status</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Last Seen</th>
                      <th className="pb-3 font-medium text-muted-foreground">Firmware</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map(device => {
                      const status = getDeviceStatus(device.last_seen);
                      const lastSeen = device.last_seen
                        ? new Date(device.last_seen).toLocaleString()
                        : 'Never';
                      return (
                        <tr key={device.device_id} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="py-3 pr-4 font-mono font-medium text-brand-primary">
                            <div className="flex items-center gap-2">
                              <Cpu className="h-4 w-4" />
                              {device.device_id}
                            </div>
                          </td>
                          <td className="py-3 pr-4">
                            <Badge
                              variant="outline"
                              className={device.protocol === 'tfms90'
                                ? 'border-brand-primary text-brand-primary'
                                : 'border-green-500 text-green-600'}
                            >
                              {device.protocol?.toUpperCase()}
                            </Badge>
                          </td>
                          <td className="py-3 pr-4 font-mono text-xs text-muted-foreground">
                            {device.imei || '—'}
                          </td>
                          <td className="py-3 pr-4 text-center">
                            {device.short_device_id
                              ? <span className="font-bold text-brand-primary">{device.short_device_id}</span>
                              : <span className="text-muted-foreground">—</span>}
                          </td>
                          <td className="py-3 pr-4">
                            <StatusBadge status={status as any} />
                          </td>
                          <td className="py-3 pr-4 text-xs text-muted-foreground">{lastSeen}</td>
                          <td className="py-3 text-xs text-muted-foreground">
                            {device.firmware_version || '—'}
                          </td>
                        </tr>
                      );
                    })}
                    {filtered.length === 0 && !loading && (
                      <tr>
                        <td colSpan={7} className="py-8 text-center text-muted-foreground">
                          No devices found
                        </td>
                      </tr>
                    )}
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
