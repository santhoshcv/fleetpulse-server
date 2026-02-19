'use client';

import { Header } from '@/components/header';
import { DataTable } from '@/components/data-table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, CreditCard, TrendingUp, Users } from 'lucide-react';
import { StatCard } from '@/components/stat-card';
import { Badge } from '@/components/ui/badge';

const statsData = [
  { icon: DollarSign, title: 'Total Revenue', value: '$48,392', trend: { value: 15, isPositive: true } },
  { icon: CreditCard, title: 'Pending Payments', value: '$3,240', description: '8 invoices' },
  { icon: TrendingUp, title: 'Monthly Growth', value: '+12.5%', trend: { value: 3, isPositive: true } },
  { icon: Users, title: 'Active Subscriptions', value: '234', description: '13 trials ending soon' },
];

const mockBillingRecords = [
  {
    id: '1',
    client: 'Acme Logistics',
    invoice_number: 'INV-2024-0156',
    amount: '$499.99',
    billing_date: '2024-02-15',
    payment_status: 'Paid',
    plan: 'Enterprise',
  },
  {
    id: '2',
    client: 'Swift Transport',
    invoice_number: 'INV-2024-0157',
    amount: '$149.99',
    billing_date: '2024-02-14',
    payment_status: 'Paid',
    plan: 'Professional',
  },
  {
    id: '3',
    client: 'Metro Fleet Services',
    invoice_number: 'INV-2024-0158',
    amount: '$49.99',
    billing_date: '2024-02-13',
    payment_status: 'Pending',
    plan: 'Starter',
  },
  {
    id: '4',
    client: 'Global Shipping Co.',
    invoice_number: 'INV-2024-0159',
    amount: '$499.99',
    billing_date: '2024-02-12',
    payment_status: 'Paid',
    plan: 'Enterprise',
  },
  {
    id: '5',
    client: 'Express Delivery Inc.',
    invoice_number: 'INV-2024-0160',
    amount: '$149.99',
    billing_date: '2024-02-11',
    payment_status: 'Failed',
    plan: 'Professional',
  },
];

const columns = [
  { key: 'invoice_number', label: 'Invoice', sortable: true },
  { key: 'client', label: 'Client', sortable: true },
  { key: 'plan', label: 'Plan', sortable: true },
  { key: 'amount', label: 'Amount', sortable: true },
  { key: 'billing_date', label: 'Date', sortable: true },
  {
    key: 'payment_status',
    label: 'Status',
    render: (value: string) => {
      const colors: Record<string, string> = {
        Paid: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20',
        Pending: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20',
        Failed: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20',
      };
      return (
        <Badge variant="outline" className={colors[value]}>
          {value}
        </Badge>
      );
    },
  },
];

export default function BillingPage() {
  return (
    <>
      <Header title="Billing & Subscriptions" />

      <main className="p-6 space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statsData.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Recent Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable
              data={mockBillingRecords}
              columns={columns}
              searchPlaceholder="Search by invoice or client..."
            />
          </CardContent>
        </Card>
      </main>
    </>
  );
}
