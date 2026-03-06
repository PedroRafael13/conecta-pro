'use client';

import { HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'interactive' | 'highlighted' | 'glass';
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    const variants = {
      default: `
        bg-[hsl(var(--card))] border border-[hsl(var(--border))]
      `,
      interactive: `
        bg-[hsl(var(--card))] border border-[hsl(var(--border))]
        cursor-pointer transition-all duration-300
        hover:border-transparent hover:bg-[hsl(var(--card))]/80
        hover:shadow-xl hover:shadow-[hsl(var(--primary))]/8
        hover:translate-y-[-2px]
        active:scale-[0.99]
        relative overflow-hidden
        before:absolute before:inset-0 before:rounded-2xl before:p-[1px]
        before:bg-gradient-to-br before:from-transparent before:via-transparent before:to-transparent
        before:transition-all before:duration-300 before:pointer-events-none
        hover:before:from-[hsl(var(--primary)/0.4)] hover:before:via-[hsl(var(--accent)/0.2)] hover:before:to-[hsl(var(--primary)/0.1)]
      `,
      highlighted: `
        bg-[hsl(var(--card))] border border-[hsl(var(--primary))]/30
        shadow-lg shadow-[hsl(var(--primary))]/10
      `,
      glass: `
        backdrop-blur-xl border border-white/10
        bg-white/70 dark:bg-white/5
        shadow-lg shadow-black/5
      `,
    };

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-2xl p-4',
          variants[variant],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex flex-col space-y-1.5 pb-4', className)} {...props} />
  )
);
CardHeader.displayName = 'CardHeader';

const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn('text-lg font-semibold leading-none tracking-tight', className)} {...props} />
  )
);
CardTitle.displayName = 'CardTitle';

const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn('text-sm text-[hsl(var(--muted-foreground))]', className)} {...props} />
  )
);
CardDescription.displayName = 'CardDescription';

const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('', className)} {...props} />
  )
);
CardContent.displayName = 'CardContent';

export { Card, CardHeader, CardTitle, CardDescription, CardContent };
