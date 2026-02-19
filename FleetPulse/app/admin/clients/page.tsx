'use client';

import { Header } from '@/components/header';
import { DataTable } from '@/components/data-table';
import { StatusBadge } from '@/components/status-badge';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const mockClients = [
  {
    id: '1',
    company_name: 'Acme Logistics',
    contact_name: 'John Smith',
    email: 'john@acmelogistics.com',
    status: 'active' as const,
    subscription_plan: 'Enterprise',
    vehicles: 156,
    devices: 178,
  },
  {
    id: '2',
    company_name: 'Swift Transport',
    contact_name: 'Sarah Johnson',
    email: 'sarah@swifttransport.com',
    status: 'active' as const,
    subscription_plan: 'Professional',
    vehicles: 89,
    devices: 95,
  },
  {
    id: '3',
    company_name: 'Metro Fleet Services',
    contact_name: 'Michael Brown',
    email: 'michael@metrofleet.com',
    status: 'trial' as const,
    subscription_plan: 'Starter',
    vehicles: 12,
    devices: 15,
  },
  {
    id: '4',
    company_name: 'Global Shipping Co.',
    contact_name: 'Emily Davis',
    email: 'emily@globalshipping.com',
    status: 'active' as const,
    subscription_plan: 'Enterprise',
    vehicles: 234,
    devices: 267,
  },
  {
    id: '5',
    company_name: 'Express Delivery Inc.',
    contact_name: 'David Wilson',
    email: 'david@expressdelivery.com',
    status: 'suspended' as const,
    subscription_plan: 'Professional',
    vehicles: 45,
    devices: 52,
  },
];

const columns = [
  { key: 'company_name', label: 'Company', sortable: true },
  { key: 'contact_name', label: 'Contact', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  {
    key: 'status',
    label: 'Status',
    render: (value: string) => <StatusBadge status={value as any} />,
  },
  { key: 'subscription_plan', label: 'Plan', sortable: true },
  { key: 'vehicles', label: 'Vehicles', sortable: true },
  { key: 'devices', label: 'Devices', sortable: true },
];

export default function ClientsPage() {
  return (
    <>
      <Header title="Client Management" />

      <main className="p-6">
        <Card>
          <CardContent className="pt-6">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-heading font-semibold">All Clients</h2>
                <p className="text-sm text-muted-foreground">Manage your client accounts and subscriptions</p>
              </div>
              <Button className="bg-brand-primary hover:bg-brand-primary/90">
                <Plus className="mr-2 h-4 w-4" />
                Add Client
              </Button>
            </div>

            <DataTable
              data={mockClients}
              columns={columns}
              searchPlaceholder="Search clients..."
            />
          </CardContent>
        </Card>
      </main>
    </>
  );
}
