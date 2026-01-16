import { type HTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

const shadowClasses = {
  none: '',
  sm: 'shadow-sm',
  md: 'shadow-card',
  lg: 'shadow-lg',
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, padding = 'md', shadow = 'md', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          'bg-white rounded-lg',
          paddingClasses[padding],
          shadowClasses[shadow],
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

export type CardHeaderProps = HTMLAttributes<HTMLDivElement>;

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('flex flex-col space-y-1.5 pb-4', className)}
      {...props}
    />
  )
);

CardHeader.displayName = 'CardHeader';

export type CardTitleProps = HTMLAttributes<HTMLHeadingElement>;

export const CardTitle = forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={clsx('text-lg font-semibold text-gray-900', className)}
      {...props}
    />
  )
);

CardTitle.displayName = 'CardTitle';

export type CardContentProps = HTMLAttributes<HTMLDivElement>;

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={clsx('', className)} {...props} />
  )
);

CardContent.displayName = 'CardContent';

export default Card;
