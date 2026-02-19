import Link from 'next/link';
import { Logo } from '@/components/logo';
import { Button } from '@/components/ui/button';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, Users, BarChart3 } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-brand-primary/5">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,174,239,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,174,239,0.03)_1px,transparent_1px)] bg-[size:20px_20px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,black_40%,transparent_100%)]"></div>

      <div className="relative">
        <div className="container mx-auto px-6 py-16">
          <div className="flex flex-col items-center justify-center text-center space-y-8">
            <Logo className="scale-150 mb-4" showText={true} />

            <div className="max-w-3xl space-y-4">
              <h1 className="font-heading text-5xl font-bold tracking-tight sm:text-6xl">
                Professional Fleet Management
              </h1>
              <p className="text-xl text-muted-foreground">
                Enterprise-grade telematics platform for real-time vehicle tracking, analytics, and fleet optimization
              </p>
            </div>

            <div className="flex gap-4 mt-8">
              <Link href="/admin">
                <Button size="lg" className="bg-brand-primary hover:bg-brand-primary/90 text-white">
                  <Shield className="mr-2 h-5 w-5" />
                  Super Admin Portal
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="lg" variant="outline">
                  <Users className="mr-2 h-5 w-5" />
                  Client Portal
                </Button>
              </Link>
            </div>

            <div className="grid gap-6 md:grid-cols-3 mt-16 w-full max-w-5xl">
              <Card>
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-primary/10 mb-2">
                    <Shield className="h-6 w-6 text-brand-primary" />
                  </div>
                  <CardTitle className="font-heading">Real-Time Tracking</CardTitle>
                  <CardDescription>
                    Monitor your entire fleet with live GPS tracking and instant location updates
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-primary/10 mb-2">
                    <BarChart3 className="h-6 w-6 text-brand-primary" />
                  </div>
                  <CardTitle className="font-heading">Advanced Analytics</CardTitle>
                  <CardDescription>
                    Comprehensive reports on fuel consumption, driver behavior, and trip history
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-primary/10 mb-2">
                    <Users className="h-6 w-6 text-brand-primary" />
                  </div>
                  <CardTitle className="font-heading">Multi-Client Management</CardTitle>
                  <CardDescription>
                    Scalable platform supporting multiple clients with isolated data and permissions
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
