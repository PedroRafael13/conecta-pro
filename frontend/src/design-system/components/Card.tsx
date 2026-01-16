'use client';

import { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/shared/utils/cn';

const cardVariants = cva(
  'rounded-xl border transition-all duration-300',
  {
    variants: {
      variant: {
        default: 'bg-bg-secondary border-border-subtle shadow-card',
        elevated: 'bg-bg-tertiary border-border-default shadow-card-hover',
        glass: 'bg-bg-secondary/80 backdrop-blur-xl border-border-subtle/50 shadow-card',
        outline: 'bg-transparent border-border-default',
        ghost: 'bg-transparent border-transparent',
      },
      hover: {
        true: 'hover:border-border-default hover:shadow-card-hover hover:-translate-y-0.5 cursor-pointer',
        glow: 'hover:border-accent-primary/30 hover:shadow-glow cursor-pointer',
      },
      padding: {
        none: 'p-0',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      padding: 'none',
    },
  }
);

export interface CardProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, hover, padding, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(cardVariants({ variant, hover, padding }), className)}
        {...props}
      />
    );
  }
);

Card.displayName = 'Card';

// Card Header
export interface CardHeaderProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  title?: ReactNode;
  subtitle?: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, title, subtitle, description, action, children, ...props }, ref) => {
    const subtitleText = subtitle || description;
    return (
      <div
        ref={ref}
        className={cn('px-6 py-4 border-b border-border-subtle', className)}
        {...props}
      >
        {children || (
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1">
              {title && (
                <h3 className="text-lg font-semibold text-text-primary">
                  {title}
                </h3>
              )}
              {subtitleText && (
                <p className="text-sm text-text-secondary">{subtitleText}</p>
              )}
            </div>
            {action && <div className="flex-shrink-0">{action}</div>}
          </div>
        )}
      </div>
    );
  }
);

CardHeader.displayName = 'CardHeader';

// Card Body
export const CardBody = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('p-6', className)}
        {...props}
      />
    );
  }
);

CardBody.displayName = 'CardBody';

// Card Footer
export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'px-6 py-4 border-t border-border-subtle bg-bg-primary/50 rounded-b-xl',
          className
        )}
        {...props}
      />
    );
  }
);

CardFooter.displayName = 'CardFooter';

export { cardVariants };
