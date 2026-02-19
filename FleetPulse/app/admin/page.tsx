'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { supabase } from '@/lib/supabase';
import { getDeviceStatus } from '@/lib/types';
import { Cpu, Activity, Radio, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface AdminStats {
  totalDevices: number;
  activeDevices: number;
  onlineNow: number;
  recordsToday: number;
  tfms90Count: number;
  teltonikaCount: number;
  tripsToday: number;
  recentActivity: { device_id: string; message_type: string; timestamp: string; speed: number | null }[];
  hourlyData: { hour: string; records: number }[];
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);

    // Fetch all devices
    const { data: devices } = await supabase
      .from('devices')
      .select('device_id, protocol, is_active, last_seen');

    const totalDevices = devices?.length || 0;
    const activeDevices = devices?.filter(d => d.is_active).length || 0;
    const onlineNow = devices?.filter(d => getDeviceStatus(d.last_seen) === 'online').length || 0;
    const tfms90Count = devices?.filter(d => d.protocol === 'tfms90').length || 0;
    const teltonikaCount = devices?.filter(d => d.protocol === 'teltonika').length || 0;

    // Records today
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    const { count: recordsToday } = await supabase
      .from('telemetry_data')
      .select('id', { count: 'exact', head: true })
      .gte('timestamp', todayStart.toISOString());

    // Trips today (TS records)
    const { count: tripsToday } = await supabase
      .from('telemetry_data')
      .select('id', { count: 'exact', head: true })
      .eq('message_type', 'TS')
      .gte('timestamp', todayStart.toISOString());

    // Recent activity (last 8 records)
    const { data: recentActivity } = await supabase
      .from('telemetry_data')
      .select('device_id, message_type, timestamp, speed')
      .order('timestamp', { ascending: false })
      .limit(8);

    // Hourly data for the last 12 hours
    const hourlyData: { hour: string; records: number }[] = [];
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
      const hourStart = new Date(now);
      hourStart.setHours(now.getHours() - i, 0, 0, 0);
      const hourEnd = new Date(hourStart);
      hourEnd.setHours(hourStart.getHours() + 1);

      const { count } = await supabase
        .from('telemetry_data')
        .select('id', { count: 'exact', head: true })
        .gte('timestamp', hourStart.toISOString())
        .lt('timestamp', hourEnd.toISOString());

      hourlyData.push({
        hour: `${hourStart.getHours()}:00`,
        records: count || 0,
      });
    }

    setStats({
      totalDevices,
      activeDevices,
      onlineNow,
      recordsToday: recordsToday || 0,
      tfms90Count,
      teltonikaCount,
      tripsToday: tripsToday || 0,
      recentActivity: recentActivity || [],
      hourlyData,
    });
    setLoading(false);
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (ts: string) => {
    const diff = Math.round((Date.now() - new Date(ts).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  };

  const msgTypeColor: Record<string, string> = {
    TS: 'text-green-600',
    TE: 'text-red-500',
    TD: 'text-brand-primary',
    HB: 'text-amber-500',
    codec_0x8: 'text-purple-500',
  };

  return (
    <>
      <Header title="Super Admin Dashboard" />

      <main className="p-6 space-y-6">
        {loading && !stats ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="h-6 w-6 animate-spin text-brand-primary mr-2" />
            <span className="text-muted-foreground">Loading dashboard...</span>
          </div>
        ) : stats ? (
          <>
            {/* Stats row */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Devices</p>
                      <p className="text-3xl font-heading font-bold text-brand-primary">{stats.totalDevices}</p>
                      <p className="text-xs text-muted-foreground mt-1">{stats.activeDevices} active</p>
                    </div>
                    <Cpu className="h-8 w-8 text-brand-primary/30" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Online Now</p>
                      <p className="text-3xl font-heading font-bold text-green-600">{stats.onlineNow}</p>
                      <p className="text-xs text-muted-foreground mt-1">last 5 minutes</p>
                    </div>
                    <Radio className="h-8 w-8 text-green-600/30" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Trips Today</p>
                      <p className="text-3xl font-heading font-bold text-amber-500">{stats.tripsToday}</p>
                      <p className="text-xs text-muted-foreground mt-1">TS events</p>
                    </div>
                    <Activity className="h-8 w-8 text-amber-500/30" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Records Today</p>
                      <p className="text-3xl font-heading font-bold text-blue-600">{stats.recordsToday.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground mt-1">telemetry points</p>
                    </div>
                    <Activity className="h-8 w-8 text-blue-600/30" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Protocol split + Hourly chart */}
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="font-heading text-base">Protocol Split</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">TFMS90</p>
                      <p className="text-xs text-muted-foreground">Text protocol</p>
                    </div>
                    <span className="text-2xl font-bold text-brand-primary">{stats.tfms90Count}</span>
                  </div>
                  <div className="h-px bg-border" />
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Teltonika</p>
                      <p className="text-xs text-muted-foreground">Binary Codec 8E</p>
                    </div>
                    <span className="text-2xl font-bold text-green-600">{stats.teltonikaCount}</span>
                  </div>
                  <div className="h-px bg-border" />
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Total</p>
                    </div>
                    <span className="text-2xl font-bold">{stats.totalDevices}</span>
                  </div>
                </CardContent>
              </Card>

              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="font-heading text-base">Telemetry Volume (last 12h)</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={stats.hourlyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="hour" className="text-xs" tick={{ fontSize: 10 }} />
                      <YAxis className="text-xs" tick={{ fontSize: 10 }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="records" fill="#00AEEF" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <CardTitle className="font-heading">Live Event Feed</CardTitle>
                <button
                  onClick={fetchStats}
                  disabled={loading}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats.recentActivity.map((event, idx) => (
                    <div key={idx} className="flex items-center justify-between border-b pb-2 last:border-0">
                      <div className="flex items-center gap-3">
                        <span className={`text-xs font-mono font-bold w-16 ${msgTypeColor[event.message_type] || 'text-muted-foreground'}`}>
                          {event.message_type}
                        </span>
                        <span className="font-mono text-sm">{event.device_id}</span>
                        {event.speed != null && (
                          <span className="text-xs text-muted-foreground">{Math.round(event.speed)} km/h</span>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">{formatTime(event.timestamp)}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </>
        ) : null}
      </main>
    </>
  );
}
