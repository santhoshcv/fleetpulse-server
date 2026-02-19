import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: 'online' | 'offline' | 'moving' | 'idle' | 'active' | 'inactive' | 'suspended' | 'trial' | 'maintenance';
  className?: string;
}

const statusConfig = {
  online: { label: 'Online', className: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20' },
  offline: { label: 'Offline', className: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20' },
  moving: { label: 'Moving', className: 'bg-brand-primary/10 text-brand-primary border-brand-primary/20' },
  idle: { label: 'Idle', className: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20' },
  active: { label: 'Active', className: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20' },
  inactive: { label: 'Inactive', className: 'bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20' },
  suspended: { label: 'Suspended', className: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20' },
  trial: { label: 'Trial', className: 'bg-brand-accent/10 text-amber-700 dark:text-amber-400 border-brand-accent/20' },
  maintenance: { label: 'Maintenance', className: 'bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20' },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <Badge variant="outline" className={cn('font-medium', config.className, className)}>
      <span className={cn('mr-1.5 h-1.5 w-1.5 rounded-full', config.className.includes('green') ? 'bg-green-500' : config.className.includes('red') ? 'bg-red-500' : config.className.includes('brand-primary') ? 'bg-brand-primary' : config.className.includes('amber') ? 'bg-amber-500' : config.className.includes('gray') ? 'bg-gray-500' : 'bg-orange-500')}></span>
      {config.label}
    </Badge>
  );
}
