'use client';

import { Header } from '@/components/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Check } from 'lucide-react';

const subscriptionPlans = [
  {
    name: 'Starter',
    price: '$49.99',
    current: false,
    features: ['Up to 10 vehicles', '2 user accounts', 'Live tracking', 'Basic reports', 'Email alerts'],
  },
  {
    name: 'Professional',
    price: '$149.99',
    current: true,
    features: [
      'Up to 50 vehicles',
      '10 user accounts',
      'Live tracking',
      'Advanced reports',
      'SMS & Email alerts',
      'Geofencing',
      'Driver behavior analysis',
    ],
  },
  {
    name: 'Enterprise',
    price: '$499.99',
    current: false,
    features: [
      'Unlimited vehicles',
      'Unlimited users',
      'Live tracking',
      'Advanced reports',
      'SMS & Email alerts',
      'Geofencing',
      'Driver behavior analysis',
      'Custom integrations',
      'API access',
      '24/7 support',
    ],
  },
];

export default function AccountPage() {
  return (
    <>
      <Header title="Account & Subscription" />

      <main className="p-6 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Company Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="company">Company Name</Label>
                <Input id="company" defaultValue="Acme Logistics" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="contact">Contact Name</Label>
                <Input id="contact" defaultValue="John Smith" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" type="email" defaultValue="john@acmelogistics.com" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input id="phone" type="tel" defaultValue="+1 (555) 123-4567" />
              </div>
            </div>
            <Button className="bg-brand-primary hover:bg-brand-primary/90">Save Changes</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="font-heading">Subscription Plan</CardTitle>
              <Badge className="bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20">
                Active
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="mb-6 rounded-lg bg-muted p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Current Plan</p>
                  <p className="text-2xl font-bold font-heading">Professional</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Billing</p>
                  <p className="text-2xl font-bold font-heading">$149.99/mo</p>
                </div>
              </div>
              <div className="mt-4 text-sm text-muted-foreground">
                Next billing date: March 17, 2024
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {subscriptionPlans.map((plan, index) => (
                <Card
                  key={index}
                  className={plan.current ? 'border-2 border-brand-primary' : ''}
                >
                  <CardHeader>
                    <CardTitle className="font-heading text-lg">{plan.name}</CardTitle>
                    <div className="text-3xl font-bold font-heading">{plan.price}</div>
                    <p className="text-xs text-muted-foreground">per month</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <ul className="space-y-2">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <Check className="h-4 w-4 text-brand-primary mt-0.5 flex-shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button
                      className="w-full"
                      variant={plan.current ? 'secondary' : 'default'}
                      disabled={plan.current}
                    >
                      {plan.current ? 'Current Plan' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Billing History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { date: 'Feb 17, 2024', amount: '$149.99', status: 'Paid', invoice: 'INV-2024-0234' },
                { date: 'Jan 17, 2024', amount: '$149.99', status: 'Paid', invoice: 'INV-2024-0156' },
                { date: 'Dec 17, 2023', amount: '$149.99', status: 'Paid', invoice: 'INV-2023-0987' },
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between border-b pb-3 last:border-0">
                  <div>
                    <p className="font-medium text-sm">{item.invoice}</p>
                    <p className="text-sm text-muted-foreground">{item.date}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold">{item.amount}</span>
                    <Badge className="bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20">
                      {item.status}
                    </Badge>
                    <Button size="sm" variant="ghost">
                      Download
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </>
  );
}
