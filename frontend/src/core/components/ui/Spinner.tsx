import { clsx } from 'clsx';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
};

const colorClasses = {
  primary: 'border-conecta-escuro',
  secondary: 'border-conecta-laranja',
  white: 'border-white',
};

export function Spinner({ size = 'md', color = 'primary', className }: SpinnerProps) {
  return (
    <div
      className={clsx(
        'animate-spin rounded-full border-2 border-t-transparent',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Carregando...</span>
    </div>
  );
}

export default Spinner;
