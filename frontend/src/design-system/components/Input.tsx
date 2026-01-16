'use client';

import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/shared/utils/cn';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

const inputVariants = cva(
  `w-full bg-bg-tertiary border rounded-lg text-text-primary placeholder:text-text-muted
   transition-all duration-200
   focus:outline-none focus:ring-1
   disabled:opacity-50 disabled:cursor-not-allowed`,
  {
    variants: {
      variant: {
        default: 'border-border-default focus:border-accent-primary focus:ring-accent-primary',
        error: 'border-danger focus:border-danger focus:ring-danger',
        success: 'border-success focus:border-success focus:ring-success',
      },
      inputSize: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-4 text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      inputSize: 'md',
    },
  }
);

export interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string;
  helperText?: string;
  error?: string;
  success?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  required?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      variant,
      inputSize,
      label,
      helperText,
      error,
      success,
      leftIcon,
      rightIcon,
      required,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
    const currentVariant = error ? 'error' : success ? 'success' : variant;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              'block text-sm font-medium text-text-secondary mb-1.5',
              required && "after:content-['*'] after:text-danger after:ml-0.5"
            )}
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              inputVariants({ variant: currentVariant, inputSize }),
              leftIcon && 'pl-10',
              (rightIcon || error || success) && 'pr-10',
              className
            )}
            {...props}
          />
          {(rightIcon || error || success) && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              {error ? (
                <AlertCircle className="h-5 w-5 text-danger" />
              ) : success ? (
                <CheckCircle2 className="h-5 w-5 text-success" />
              ) : (
                rightIcon
              )}
            </div>
          )}
        </div>
        {(helperText || error || success) && (
          <p
            className={cn(
              'text-sm mt-1.5',
              error
                ? 'text-danger'
                : success
                ? 'text-success'
                : 'text-text-muted'
            )}
          >
            {error || success || helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { inputVariants };
