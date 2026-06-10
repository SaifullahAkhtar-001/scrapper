import { type SelectHTMLAttributes } from 'react';

export function Select({ className = '', children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={`w-full px-3 py-2 text-sm bg-white border border-zinc-300 rounded-md focus:border-zinc-900 focus:ring-1 focus:ring-zinc-900 transition-colors disabled:bg-zinc-50 disabled:text-zinc-400 ${className}`}
      {...props}
    >
      {children}
    </select>
  );
}
