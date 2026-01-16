'use client';

import { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/shared/utils/cn';

const badgeVariants = cva(
  'inline-flex items-center gap-1 font-medium',
  {
    variants: {
      variant: {
        primary: 'bg-accent-primary/20 text-accent-primary',
        secondary: 'bg-accent-secondary/20 text-accent-secondary',
        success: 'bg-success/20 text-success',
        warning: 'bg-warning/20 text-warning',
        danger: 'bg-danger/20 text-danger',
        info: 'bg-info/20 text-info',
        neutral: 'bg-bg-tertiary text-text-secondary',
        outline: 'bg-transparent border border-border-default text-text-secondary',
      },
      size: {
        sm: 'px-2 py-0.5 text-2xs rounded',
        md: 'px-2.5 py-1 text-xs rounded-full',
        lg: 'px-3 py-1.5 text-sm rounded-full',
      },
      dot: {
        true: '',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

const dotColors = {
  primary: 'bg-accent-primary',
  secondary: 'bg-accent-secondary',
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
  info: 'bg-info',
  neutral: 'bg-text-muted',
  outline: 'bg-text-muted',
};

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'primary', size, dot, leftIcon, rightIcon, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(badgeVariants({ variant, size, dot }), className)}
        {...props}
      >
        {dot && (
          <span
            className={cn(
              'w-1.5 h-1.5 rounded-full',
              dotColors[variant as keyof typeof dotColors]
            )}
          />
        )}
        {leftIcon}
        {children}
        {rightIcon}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export { badgeVariants };
