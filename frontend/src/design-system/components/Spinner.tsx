'use client';

import { cn } from '@/shared/utils/cn';

interface SpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses = {
  xs: 'w-3 h-3 border',
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-8 h-8 border-2',
  xl: 'w-12 h-12 border-3',
};

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <div
      className={cn(
        'rounded-full border-border-default border-t-accent-primary animate-spin',
        sizeClasses[size],
        className
      )}
      role="status"
      aria-label="Carregando"
    >
      <span className="sr-only">Carregando...</span>
    </div>
  );
}

// Page Loader
interface PageLoaderProps {
  message?: string;
}

export function PageLoader({ message = 'Carregando...' }: PageLoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <Spinner size="lg" />
      <p className="text-text-secondary text-sm animate-pulse">{message}</p>
    </div>
  );
}

// Inline Loader
interface InlineLoaderProps {
  className?: string;
}

export function InlineLoader({ className }: InlineLoaderProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Spinner size="sm" />
      <span className="text-text-secondary text-sm">Carregando...</span>
    </div>
  );
}

// Button Loader (for inside buttons)
export function ButtonLoader() {
  return <Spinner size="sm" className="border-current" />;
}
