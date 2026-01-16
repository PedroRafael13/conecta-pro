'use client';

import { forwardRef, type ImgHTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/shared/utils/cn';
import { User } from 'lucide-react';

const avatarVariants = cva(
  'relative inline-flex items-center justify-center rounded-full bg-bg-tertiary text-text-secondary font-medium overflow-hidden',
  {
    variants: {
      size: {
        xs: 'w-6 h-6 text-2xs',
        sm: 'w-8 h-8 text-xs',
        md: 'w-10 h-10 text-sm',
        lg: 'w-12 h-12 text-base',
        xl: 'w-16 h-16 text-lg',
        '2xl': 'w-20 h-20 text-xl',
      },
      status: {
        online: '',
        offline: '',
        busy: '',
        away: '',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  }
);

const statusColors = {
  online: 'bg-success',
  offline: 'bg-text-muted',
  busy: 'bg-danger',
  away: 'bg-warning',
};

const statusSizes = {
  xs: 'w-1.5 h-1.5 border',
  sm: 'w-2 h-2 border',
  md: 'w-2.5 h-2.5 border-2',
  lg: 'w-3 h-3 border-2',
  xl: 'w-4 h-4 border-2',
  '2xl': 'w-5 h-5 border-2',
};

export interface AvatarProps
  extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'size'>,
    VariantProps<typeof avatarVariants> {
  name?: string;
  src?: string;
  fallback?: string;
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, size = 'md', status, name, src, fallback, alt, ...props }, ref) => {
    const initials = name ? getInitials(name) : fallback;

    return (
      <div
        ref={ref}
        className={cn(avatarVariants({ size, status }), className)}
      >
        {src ? (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className="w-full h-full object-cover"
            {...props}
          />
        ) : initials ? (
          <span className="select-none">{initials}</span>
        ) : (
          <User className="w-1/2 h-1/2" />
        )}
        {status && (
          <span
            className={cn(
              'absolute bottom-0 right-0 rounded-full border-bg-primary',
              statusColors[status],
              statusSizes[size as keyof typeof statusSizes]
            )}
          />
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';

// Avatar Group
export interface AvatarGroupProps {
  children: React.ReactNode;
  max?: number;
  size?: VariantProps<typeof avatarVariants>['size'];
  className?: string;
}

export function AvatarGroup({ children, max = 4, size = 'md', className }: AvatarGroupProps) {
  const avatars = Array.isArray(children) ? children : [children];
  const visibleAvatars = avatars.slice(0, max);
  const remainingCount = avatars.length - max;

  return (
    <div className={cn('flex -space-x-2', className)}>
      {visibleAvatars.map((avatar, index) => (
        <div key={index} className="ring-2 ring-bg-primary rounded-full">
          {avatar}
        </div>
      ))}
      {remainingCount > 0 && (
        <div
          className={cn(
            avatarVariants({ size }),
            'ring-2 ring-bg-primary bg-bg-elevated text-text-secondary'
          )}
        >
          +{remainingCount}
        </div>
      )}
    </div>
  );
}

export { avatarVariants };
