import { type ImgHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

export interface AvatarProps extends ImgHTMLAttributes<HTMLImageElement> {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  name?: string;
}

const sizeClasses = {
  xs: 'w-6 h-6 text-xs',
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
  xl: 'w-16 h-16 text-lg',
};

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function getColorFromName(name: string): string {
  const colors = [
    'bg-red-500',
    'bg-orange-500',
    'bg-amber-500',
    'bg-yellow-500',
    'bg-lime-500',
    'bg-green-500',
    'bg-emerald-500',
    'bg-teal-500',
    'bg-cyan-500',
    'bg-sky-500',
    'bg-blue-500',
    'bg-indigo-500',
    'bg-violet-500',
    'bg-purple-500',
    'bg-fuchsia-500',
    'bg-pink-500',
    'bg-rose-500',
  ];

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  return colors[Math.abs(hash) % colors.length];
}

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, name, size = 'md', ...props }, ref) => {
    const initials = name ? getInitials(name) : '?';
    const bgColor = name ? getColorFromName(name) : 'bg-gray-400';

    if (src) {
      return (
        <img
          ref={ref as React.Ref<HTMLImageElement>}
          src={src}
          alt={alt || name}
          className={clsx(
            'rounded-full object-cover',
            sizeClasses[size],
            className
          )}
          {...props}
        />
      );
    }

    return (
      <div
        ref={ref}
        className={clsx(
          'rounded-full flex items-center justify-center text-white font-medium',
          sizeClasses[size],
          bgColor,
          className
        )}
      >
        {initials}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';

export default Avatar;
