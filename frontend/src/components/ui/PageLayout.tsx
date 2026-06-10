import { type ReactNode } from 'react';

interface PageLayoutProps {
  children: ReactNode;
  wide?: boolean;
}

export function PageLayout({ children, wide = false }: PageLayoutProps) {
  return (
    <main className={`mx-auto px-4 sm:px-6 py-8 ${wide ? 'max-w-7xl' : 'max-w-6xl'}`}>
      {children}
    </main>
  );
}
