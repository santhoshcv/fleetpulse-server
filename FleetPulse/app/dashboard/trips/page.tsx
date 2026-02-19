'use client';

import { useEffect, useState } from 'react';
import { Header } from '@/components/header';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { supabase } from '@/lib/supabase';
import { RefreshCw, Route, Clock, Gauge, MapPin } from 'lucide-react';

interface TripRecord {
  id: string;
  device_id: string;
  start_time: string;
  end_time: string | null;
  start_lat: number | null;
  start_lon: number | null;
  end_lat: number | null;
  end_lon: number | null;
  max_speed: number;
  avg_speed: number;
  duration_min: number | null;
  record_count: number;
}

export default function TripsPage() {
  const [trips, setTrips] = useState<TripRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTrips = async () => {
    setLoading(true);

    // Get all TS (trip start) records
    const { data: starts } = await supabase
      .from('telemetry_data')
      .select('device_id, timestamp, latitude, longitude')
      .eq('message_type', 'TS')
      .order('timestamp', { ascending: false })
      .limit(50);

    if (!starts) { setLoading(false); return; }

    // For each trip start, find the next TE and TD stats
    const tripData = await Promise.all(
      starts.map(async (start, idx) => {
        // Find next TE after this TS for same device
        const { data: end } = await supabase
          .from('telemetry_data')
          .select('timestamp, latitude, longitude')
          .eq('device_id', start.device_id)
          .eq('message_type', 'TE')
          .gt('timestamp', start.timestamp)
          .order('timestamp', { ascending: true })
          .limit(1)
          .maybeSingle();

        // Get TD records between TS and TE for stats
        const endTime = end?.timestamp || new Date().toISOString();
        const { data: tds } = await supabase
          .from('telemetry_data')
          .select('speed, latitude, longitude')
          .eq('device_id', start.device_id)
          .eq('message_type', 'TD')
          .gt('timestamp', start.timestamp)
          .lt('timestamp', endTime)
          .order('timestamp', { ascending: true });

        const speeds = (tds || []).map(t => t.speed || 0).filter(s => s > 0);
        const maxSpeed = speeds.length ? Math.max(...speeds) : 0;
        const avgSpeed = speeds.length ? speeds.reduce((a, b) => a + b, 0) / speeds.length : 0;

        const durationMin = end
          ? Math.round((new Date(end.timestamp).getTime() - new Date(start.timestamp).getTime()) / 60000)
          : null;

        return {
          id: `${start.device_id}-${idx}`,
          device_id: start.device_id,
          start_time: start.timestamp,
          end_time: end?.timestamp || null,
          start_lat: start.latitude,
          start_lon: start.longitude,
          end_lat: end?.latitude || null,
          end_lon: end?.longitude || null,
          max_speed: Math.round(maxSpeed),
          avg_speed: Math.round(avgSpeed),
          duration_min: durationMin,
          record_count: tds?.length || 0,
        };
      })
    );

    setTrips(tripData);
    setLoading(false);
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  const formatDuration = (min: number | null) => {
    if (!min) return '—';
    const h = Math.floor(min / 60);
    const m = min % 60;
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  };

  return (
    <>
      <Header title="Trip History" />
      <main className="p-6 space-y-4">

        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-4 pb-4">
              <p className="text-sm text-muted-foreground">Total Trips</p>
              <p className="text-3xl font-heading font-bold text-brand-primary">{trips.length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 pb-4">
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-3xl font-heading font-bold text-green-600">
                {trips.filter(t => t.end_time).length}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 pb-4">
              <p className="text-sm text-muted-foreground">In Progress</p>
              <p className="text-3xl font-heading font-bold text-amber-500">
                {trips.filter(t => !t.end_time).length}
              </p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardContent className="pt-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-heading font-semibold">Trip Records</h2>
                <p className="text-sm text-muted-foreground">
                  Real trips from TS → TD → TE message sequence
                </p>
              </div>
              <button
                onClick={fetchTrips}
                disabled={loading}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-10">
                <RefreshCw className="h-5 w-5 animate-spin text-brand-primary mr-2" />
                <span className="text-muted-foreground">Loading trips...</span>
              </div>
            ) : (
              <div className="space-y-3">
                {trips.map(trip => (
                  <div
                    key={trip.id}
                    className="rounded-lg border p-4 hover:bg-muted/30 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="rounded-full bg-brand-primary/10 p-2">
                          <Route className="h-4 w-4 text-brand-primary" />
                        </div>
                        <div>
                          <p className="font-mono font-medium">{trip.device_id}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(trip.start_time).toLocaleString()}
                            {trip.end_time && ` → ${new Date(trip.end_time).toLocaleString()}`}
                          </p>
                        </div>
                      </div>
                      <Badge variant={trip.end_time ? 'outline' : 'default'}
                        className={trip.end_time
                          ? 'border-green-500 text-green-600'
                          : 'bg-amber-500 text-white'}>
                        {trip.end_time ? 'Completed' : 'In Progress'}
                      </Badge>
                    </div>

                    <div className="mt-3 grid grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>{formatDuration(trip.duration_min)}</span>
                      </div>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Gauge className="h-3 w-3" />
                        <span>Max: {trip.max_speed} km/h</span>
                      </div>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Gauge className="h-3 w-3" />
                        <span>Avg: {trip.avg_speed} km/h</span>
                      </div>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-3 w-3" />
                        <span>{trip.record_count} points</span>
                      </div>
                    </div>

                    {trip.start_lat && trip.start_lon && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        Start: {trip.start_lat.toFixed(4)}, {trip.start_lon.toFixed(4)}
                        {trip.end_lat && trip.end_lon &&
                          ` → End: ${trip.end_lat.toFixed(4)}, ${trip.end_lon.toFixed(4)}`}
                      </div>
                    )}
                  </div>
                ))}
                {trips.length === 0 && (
                  <div className="py-8 text-center text-muted-foreground">No trip records found</div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </>
  );
}
