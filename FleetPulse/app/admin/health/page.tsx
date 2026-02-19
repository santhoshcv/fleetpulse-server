'use client';

import { Header } from '@/components/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatCard } from '@/components/stat-card';
import { Server, Database, Activity, Wifi } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const statsData = [
  { icon: Server, title: 'Active Servers', value: '4/4', description: 'All systems operational' },
  { icon: Database, title: 'Database', value: 'Healthy', description: '2.3ms avg response' },
  { icon: Wifi, title: 'Active Connections', value: '1,834', description: 'Devices connected' },
  { icon: Activity, title: 'Uptime', value: '99.98%', description: 'Last 30 days' },
];

const serverStatus = [
  { name: 'API Server 1', status: 'Healthy', cpu: 45, memory: 62, location: 'US-East-1' },
  { name: 'API Server 2', status: 'Healthy', cpu: 38, memory: 58, location: 'US-West-2' },
  { name: 'Database Primary', status: 'Healthy', cpu: 28, memory: 71, location: 'US-East-1' },
  { name: 'Database Replica', status: 'Healthy', cpu: 22, memory: 68, location: 'EU-West-1' },
];

export default function SystemHealthPage() {
  return (
    <>
      <Header title="System Health Monitor" />

      <main className="p-6 space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statsData.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Server Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {serverStatus.map((server, index) => (
                <div key={index} className="space-y-3 border-b pb-4 last:border-0">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">{server.name}</h3>
                      <p className="text-sm text-muted-foreground">{server.location}</p>
                    </div>
                    <Badge className="bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20">
                      {server.status}
                    </Badge>
                  </div>

                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">CPU Usage</span>
                        <span className="font-medium">{server.cpu}%</span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                        <div
                          className="h-full bg-brand-primary transition-all"
                          style={{ width: `${server.cpu}%` }}
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Memory Usage</span>
                        <span className="font-medium">{server.memory}%</span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                        <div
                          className="h-full bg-brand-primary transition-all"
                          style={{ width: `${server.memory}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="font-heading">Recent Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { event: 'System backup completed', time: '5 mins ago', type: 'success' },
                  { event: 'Database optimization finished', time: '23 mins ago', type: 'success' },
                  { event: 'API Server 2 restarted', time: '1 hour ago', type: 'info' },
                  { event: 'SSL certificate renewed', time: '3 hours ago', type: 'success' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between border-b pb-2 last:border-0">
                    <div className="flex items-center gap-2">
                      <div
                        className={`h-2 w-2 rounded-full ${
                          item.type === 'success' ? 'bg-green-500' : 'bg-brand-primary'
                        }`}
                      ></div>
                      <span className="text-sm">{item.event}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">{item.time}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="font-heading">Connection Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Active Devices</span>
                  <span className="text-2xl font-bold font-heading">1,834</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Messages/sec</span>
                  <span className="text-2xl font-bold font-heading">342</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Avg Latency</span>
                  <span className="text-2xl font-bold font-heading">23ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Data Processed</span>
                  <span className="text-2xl font-bold font-heading">45.2 GB</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  );
}
