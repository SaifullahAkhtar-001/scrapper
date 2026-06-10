import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = 'Loading...' }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <Loader2 className="w-6 h-6 text-zinc-400 animate-spin" />
      <p className="text-sm text-zinc-500">{label}</p>
    </div>
  );
}
