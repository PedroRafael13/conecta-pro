'use client';

import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline' | 'destructive' | 'default';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, disabled, children, ...props }, ref) => {
    const baseStyles = `
      inline-flex items-center justify-center gap-2
      font-medium transition-all duration-200
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[hsl(var(--background))]
      disabled:opacity-50 disabled:cursor-not-allowed
      active:scale-[0.98]
    `;

    const variants = {
      primary: `
        bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]
        hover:brightness-110 focus:ring-[hsl(var(--primary))]
        glow-primary
      `,
      default: `
        bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]
        hover:brightness-110 focus:ring-[hsl(var(--primary))]
      `,
      secondary: `
        bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))]
        hover:bg-[hsl(var(--secondary))]/80 focus:ring-[hsl(var(--secondary))]
        border border-[hsl(var(--border))]
      `,
      ghost: `
        bg-transparent text-[hsl(var(--foreground))]
        hover:bg-[hsl(var(--secondary))] focus:ring-[hsl(var(--primary))]
      `,
      danger: `
        bg-[hsl(var(--destructive))] text-white
        hover:brightness-110 focus:ring-[hsl(var(--destructive))]
        glow-destructive
      `,
      destructive: `
        bg-[hsl(var(--destructive))] text-white
        hover:brightness-110 focus:ring-[hsl(var(--destructive))]
      `,
      outline: `
        bg-transparent text-[hsl(var(--primary))]
        border border-[hsl(var(--primary))]
        hover:bg-[hsl(var(--primary))]/10 focus:ring-[hsl(var(--primary))]
      `,
    };

    const sizes = {
      sm: 'h-8 px-3 text-sm rounded-md',
      md: 'h-10 px-4 text-sm rounded-lg',
      lg: 'h-12 px-6 text-base rounded-lg',
      icon: 'h-10 w-10 rounded-lg',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
