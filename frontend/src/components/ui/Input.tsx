import { type InputHTMLAttributes, type ReactNode } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  icon?: ReactNode;
}

export function Input({ icon, className = '', ...props }: InputProps) {
  if (icon) {
    return (
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 pointer-events-none">
          {icon}
        </div>
        <input
          className={`w-full pl-10 pr-3 py-2 text-sm bg-white border border-zinc-300 rounded-md placeholder:text-zinc-400 focus:border-zinc-900 focus:ring-1 focus:ring-zinc-900 transition-colors disabled:bg-zinc-50 disabled:text-zinc-400 ${className}`}
          {...props}
        />
      </div>
    );
  }

  return (
    <input
      className={`w-full px-3 py-2 text-sm bg-white border border-zinc-300 rounded-md placeholder:text-zinc-400 focus:border-zinc-900 focus:ring-1 focus:ring-zinc-900 transition-colors disabled:bg-zinc-50 disabled:text-zinc-400 ${className}`}
      {...props}
    />
  );
}
