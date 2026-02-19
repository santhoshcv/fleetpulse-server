'use client';

import { Header } from '@/components/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, FileText, TrendingUp, Fuel, Activity } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const fuelData = [
  { vehicle: 'TRK-1045', consumption: 245 },
  { vehicle: 'VAN-2341', consumption: 156 },
  { vehicle: 'CAR-5678', consumption: 89 },
  { vehicle: 'TRK-9012', consumption: 312 },
  { vehicle: 'VAN-3456', consumption: 178 },
];

const mileageData = [
  { day: 'Mon', distance: 1240 },
  { day: 'Tue', distance: 1456 },
  { day: 'Wed', distance: 1189 },
  { day: 'Thu', distance: 1623 },
  { day: 'Fri', distance: 1501 },
  { day: 'Sat', distance: 892 },
  { day: 'Sun', distance: 654 },
];

const reportTypes = [
  {
    icon: Fuel,
    title: 'Fuel Consumption Report',
    description: 'Detailed fuel usage analysis by vehicle',
    period: 'Last 30 days',
  },
  {
    icon: TrendingUp,
    title: 'Mileage Report',
    description: 'Total distance covered by fleet',
    period: 'Last 7 days',
  },
  {
    icon: Activity,
    title: 'Driver Behaviour Report',
    description: 'Harsh braking, acceleration, and cornering events',
    period: 'Last 30 days',
  },
  {
    icon: FileText,
    title: 'Trip Summary Report',
    description: 'Complete trip history with timings',
    period: 'Custom date range',
  },
];

export default function ReportsPage() {
  return (
    <>
      <Header title="Reports & Analytics" />

      <main className="p-6 space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          {reportTypes.map((report, index) => {
            const Icon = report.icon;
            return (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-primary/10">
                      <Icon className="h-5 w-5 text-brand-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-base font-heading">{report.title}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">{report.description}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">{report.period}</span>
                    <Button size="sm" variant="outline" className="gap-2">
                      <Download className="h-3 w-3" />
                      Export PDF
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="font-heading">Fuel Consumption by Vehicle</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={fuelData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="vehicle" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="consumption" fill="#00AEEF" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="font-heading">Weekly Distance Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={mileageData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="day" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Line type="monotone" dataKey="distance" stroke="#00AEEF" strokeWidth={2} dot={{ fill: '#00AEEF' }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Driver Behaviour Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2 rounded-lg border p-4">
                <div className="text-sm text-muted-foreground">Harsh Braking Events</div>
                <div className="text-3xl font-bold font-heading text-amber-600">34</div>
                <div className="text-xs text-muted-foreground">Last 30 days</div>
              </div>
              <div className="space-y-2 rounded-lg border p-4">
                <div className="text-sm text-muted-foreground">Rapid Acceleration</div>
                <div className="text-3xl font-bold font-heading text-red-600">18</div>
                <div className="text-xs text-muted-foreground">Last 30 days</div>
              </div>
              <div className="space-y-2 rounded-lg border p-4">
                <div className="text-sm text-muted-foreground">Sharp Cornering</div>
                <div className="text-3xl font-bold font-heading text-orange-600">27</div>
                <div className="text-xs text-muted-foreground">Last 30 days</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </>
  );
}
