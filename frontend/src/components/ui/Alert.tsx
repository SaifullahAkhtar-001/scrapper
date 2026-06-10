import { AlertCircle, CheckCircle2, type LucideIcon } from 'lucide-react';
import { type ReactNode } from 'react';

type AlertVariant = 'error' | 'success' | 'info';

interface AlertProps {
  variant: AlertVariant;
  children: ReactNode;
}

const config: Record<AlertVariant, { icon: LucideIcon; classes: string }> = {
  error: {
    icon: AlertCircle,
    classes: 'bg-red-50 border-red-200 text-red-800',
  },
  success: {
    icon: CheckCircle2,
    classes: 'bg-emerald-50 border-emerald-200 text-emerald-800',
  },
  info: {
    icon: AlertCircle,
    classes: 'bg-blue-50 border-blue-200 text-blue-800',
  },
};

export function Alert({ variant, children }: AlertProps) {
  const { icon: Icon, classes } = config[variant];

  return (
    <div className={`flex items-start gap-3 px-4 py-3 border rounded-md text-sm ${classes}`}>
      <Icon className="w-4 h-4 mt-0.5 shrink-0" />
      <p>{children}</p>
    </div>
  );
}
