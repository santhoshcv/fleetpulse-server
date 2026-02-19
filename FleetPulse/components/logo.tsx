import { Grid3x3 } from 'lucide-react';

interface LogoProps {
  className?: string;
  showText?: boolean;
}

export function Logo({ className = '', showText = true }: LogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="relative">
        <Grid3x3 className="h-8 w-8 text-brand-primary" strokeWidth={1.5} />
        <div className="absolute inset-0 bg-brand-primary opacity-20 blur-sm rounded"></div>
      </div>
      {showText && (
        <div className="flex flex-col">
          <span className="font-heading text-sm font-semibold tracking-wider text-foreground">
            CLOUD TELEMATICS
          </span>
          <span className="font-heading text-xs text-brand-primary font-bold tracking-widest">
            FleetPulse
          </span>
        </div>
      )}
    </div>
  );
}
