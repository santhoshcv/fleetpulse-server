'use client';

import { Header } from '@/components/header';
import { DataTable } from '@/components/data-table';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle2 } from 'lucide-react';

const mockAlerts = [
  {
    id: '1',
    vehicle: 'TRK-1045',
    alert_type: 'Overspeed',
    severity: 'high',
    message: 'Speed exceeded limit: 112 km/h in 80 km/h zone',
    location: 'Highway 101, Mile 45',
    time: '2024-02-17 14:23',
    acknowledged: false,
  },
  {
    id: '2',
    vehicle: 'VAN-2341',
    alert_type: 'Harsh Braking',
    severity: 'medium',
    message: 'Sudden deceleration detected',
    location: 'Market St & 5th Ave',
    time: '2024-02-17 13:45',
    acknowledged: false,
  },
  {
    id: '3',
    vehicle: 'CAR-5678',
    alert_type: 'Geofence Violation',
    severity: 'high',
    message: 'Vehicle left authorized zone',
    location: '37.7749° N, 122.4194° W',
    time: '2024-02-17 12:30',
    acknowledged: true,
  },
  {
    id: '4',
    vehicle: 'TRK-1045',
    alert_type: 'Overspeed',
    severity: 'critical',
    message: 'Speed exceeded limit: 125 km/h in 90 km/h zone',
    location: 'Interstate 5, Mile 120',
    time: '2024-02-17 11:15',
    acknowledged: false,
  },
  {
    id: '5',
    vehicle: 'VAN-3456',
    alert_type: 'Harsh Braking',
    severity: 'low',
    message: 'Moderate deceleration detected',
    location: 'Oak St & Main St',
    time: '2024-02-17 10:05',
    acknowledged: true,
  },
];

const severityColors: Record<string, string> = {
  critical: 'bg-red-500 text-white border-red-500',
  high: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20',
  medium: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20',
  low: 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20',
};

const columns = [
  { key: 'vehicle', label: 'Vehicle', sortable: true },
  { key: 'alert_type', label: 'Alert Type', sortable: true },
  {
    key: 'severity',
    label: 'Severity',
    render: (value: string) => (
      <Badge variant="outline" className={severityColors[value]}>
        {value.toUpperCase()}
      </Badge>
    ),
  },
  { key: 'message', label: 'Message', sortable: false },
  { key: 'location', label: 'Location', sortable: false },
  { key: 'time', label: 'Time', sortable: true },
  {
    key: 'acknowledged',
    label: 'Status',
    render: (value: boolean) =>
      value ? (
        <Badge variant="outline" className="bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20">
          <CheckCircle2 className="mr-1 h-3 w-3" />
          Acknowledged
        </Badge>
      ) : (
        <Button size="sm" variant="outline" className="h-7 text-xs">
          Acknowledge
        </Button>
      ),
  },
];

export default function AlertsPage() {
  return (
    <>
      <Header title="Fleet Alerts" />

      <main className="p-6">
        <Card>
          <CardContent className="pt-6">
            <div className="mb-6">
              <h2 className="text-2xl font-heading font-semibold">Active Alerts</h2>
              <p className="text-sm text-muted-foreground">Monitor overspeed, harsh braking, and geofence violations</p>
            </div>

            <DataTable
              data={mockAlerts}
              columns={columns}
              searchPlaceholder="Search alerts..."
            />
          </CardContent>
        </Card>
      </main>
    </>
  );
}
