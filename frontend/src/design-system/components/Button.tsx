'use client';

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/shared/utils/cn';
import { Loader2 } from 'lucide-react';

const buttonVariants = cva(
  `inline-flex items-center justify-center gap-2 rounded-lg font-medium text-sm
   transition-all duration-200 ease-out
   focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary
   disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none
   active:scale-[0.98]`,
  {
    variants: {
      variant: {
        primary: `bg-gradient-to-r from-accent-primary to-accent-secondary text-white
                  hover:shadow-glow hover:brightness-110`,
        secondary: `bg-bg-tertiary text-text-primary border border-border-default
                    hover:bg-bg-elevated hover:border-border-strong`,
        outline: `bg-transparent border-2 border-accent-primary text-accent-primary
                  hover:bg-accent-primary hover:text-white`,
        ghost: `bg-transparent text-text-secondary
                hover:bg-bg-tertiary hover:text-text-primary`,
        danger: `bg-danger text-white
                 hover:bg-danger-dark hover:shadow-glow-danger`,
        success: `bg-success text-white
                  hover:bg-success-dark hover:shadow-glow-success`,
        link: `bg-transparent text-accent-primary underline-offset-4
               hover:underline`,
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
        xl: 'h-14 px-8 text-lg',
        icon: 'h-10 w-10 p-0',
        'icon-sm': 'h-8 w-8 p-0',
        'icon-lg': 'h-12 w-12 p-0',
      },
      fullWidth: {
        true: 'w-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      isLoading = false,
      leftIcon,
      rightIcon,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size, fullWidth }), className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          leftIcon
        )}
        {children}
        {!isLoading && rightIcon}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { buttonVariants };
