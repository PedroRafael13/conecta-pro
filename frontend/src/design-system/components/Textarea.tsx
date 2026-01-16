'use client';

import { forwardRef, type TextareaHTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/shared/utils/cn';

const textareaVariants = cva(
  `w-full rounded-lg border bg-bg-secondary text-text-primary
   placeholder:text-text-muted
   transition-all duration-200
   focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent
   disabled:opacity-50 disabled:cursor-not-allowed
   resize-none`,
  {
    variants: {
      size: {
        sm: 'px-3 py-2 text-sm min-h-[80px]',
        md: 'px-4 py-3 text-sm min-h-[100px]',
        lg: 'px-4 py-3 text-base min-h-[120px]',
      },
      variant: {
        default: 'border-border-default hover:border-border-strong',
        error: 'border-danger focus:ring-danger',
        success: 'border-success focus:ring-success',
      },
    },
    defaultVariants: {
      size: 'md',
      variant: 'default',
    },
  }
);

export interface TextareaProps
  extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'size'>,
    VariantProps<typeof textareaVariants> {
  label?: string;
  helperText?: string;
  error?: string;
  rows?: number;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      className,
      size,
      variant,
      label,
      helperText,
      error,
      disabled,
      rows = 4,
      ...props
    },
    ref
  ) => {
    const finalVariant = error ? 'error' : variant;

    return (
      <div className="space-y-1.5">
        {label && (
          <label className="block text-sm font-medium text-text-primary">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          rows={rows}
          disabled={disabled}
          className={cn(textareaVariants({ size, variant: finalVariant }), className)}
          {...props}
        />
        {(helperText || error) && (
          <p
            className={cn(
              'text-xs',
              error ? 'text-danger' : 'text-text-muted'
            )}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export { textareaVariants };
