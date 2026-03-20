'use client';

import { InputHTMLAttributes, forwardRef, useId } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon, type = 'text', id: externalId, ...props }, ref) => {
    const autoId = useId();
    const inputId = externalId || (label ? autoId : undefined);
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-[hsl(var(--muted-foreground))] mb-1.5">
            {label}
          </label>
        )}
        <div className="relative group">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[hsl(var(--muted-foreground))] transition-colors duration-200 group-focus-within:text-[hsl(var(--primary))]">
              {icon}
            </div>
          )}
          <input
            id={inputId}
            type={type}
            className={cn(
              `w-full h-11 px-3 text-sm
              bg-[hsl(var(--input))] text-[hsl(var(--foreground))]
              border border-[hsl(var(--border))] rounded-xl
              placeholder:text-[hsl(var(--muted-foreground))]
              transition-all duration-200
              focus:border-[hsl(var(--primary))]
              focus:bg-[hsl(var(--input)/0.8)]
              disabled:opacity-50 disabled:cursor-not-allowed`,
              icon && 'pl-10',
              error && 'border-[hsl(var(--destructive))]',
              className
            )}
            ref={ref}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1.5 text-xs text-[hsl(var(--destructive))]">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
