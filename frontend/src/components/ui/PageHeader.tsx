import { type ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  stat?: { value: number | string; label: string };
  actions?: ReactNode;
}

export function PageHeader({ title, description, stat, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-zinc-500">{description}</p>
        )}
      </div>
      <div className="flex items-center gap-4 shrink-0">
        {stat && (
          <div className="text-right">
            <div className="text-2xl font-semibold tabular-nums text-zinc-900">{stat.value}</div>
            <div className="text-xs text-zinc-500 uppercase tracking-wide">{stat.label}</div>
          </div>
        )}
        {actions}
      </div>
    </div>
  );
}
