'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Logo } from '@/components/logo';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Users,
  Cpu,
  CreditCard,
  Activity,
  Map,
  Car,
  Route,
  AlertTriangle,
  FileText,
  User
} from 'lucide-react';

interface SidebarProps {
  type: 'admin' | 'client';
}

const adminNavItems = [
  { href: '/admin', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/admin/clients', icon: Users, label: 'Clients' },
  { href: '/admin/devices', icon: Cpu, label: 'Devices' },
  { href: '/admin/billing', icon: CreditCard, label: 'Billing' },
  { href: '/admin/health', icon: Activity, label: 'System Health' },
];

const clientNavItems = [
  { href: '/dashboard', icon: Map, label: 'Live Map' },
  { href: '/dashboard/vehicles', icon: Car, label: 'Vehicles' },
  { href: '/dashboard/trips', icon: Route, label: 'Trip History' },
  { href: '/dashboard/alerts', icon: AlertTriangle, label: 'Alerts' },
  { href: '/dashboard/reports', icon: FileText, label: 'Reports' },
  { href: '/dashboard/account', icon: User, label: 'Account' },
];

export function Sidebar({ type }: SidebarProps) {
  const pathname = usePathname();
  const navItems = type === 'admin' ? adminNavItems : clientNavItems;

  return (
    <div className="flex h-full w-64 flex-col bg-gradient-to-b from-brand-primary to-brand-primary/90 text-white">
      <div className="flex h-16 items-center border-b border-white/10 px-6">
        <Logo className="text-white" showText={true} />
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
                isActive
                  ? 'bg-white/20 text-white shadow-lg'
                  : 'text-white/80 hover:bg-white/10 hover:text-white'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 p-4">
        <div className="text-xs text-white/60">
          {type === 'admin' ? 'Super Admin Portal' : 'Client Portal'}
        </div>
      </div>
    </div>
  );
}
