'use client';

import { type ReactNode } from 'react';
import { cn } from '@/shared/utils/cn';
import { Inbox, Search, FileX, AlertCircle, Plus } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    icon?: ReactNode;
  };
  variant?: 'default' | 'search' | 'error' | 'no-data';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  variant = 'default',
  size = 'md',
  className,
}: EmptyStateProps) {
  const defaultIcons = {
    default: <Inbox className="w-full h-full" />,
    search: <Search className="w-full h-full" />,
    error: <AlertCircle className="w-full h-full" />,
    'no-data': <FileX className="w-full h-full" />,
  };

  const sizeClasses = {
    sm: {
      container: 'py-6',
      iconWrapper: 'w-10 h-10 mb-3',
      title: 'text-sm',
      description: 'text-xs',
    },
    md: {
      container: 'py-12',
      iconWrapper: 'w-14 h-14 mb-4',
      title: 'text-base',
      description: 'text-sm',
    },
    lg: {
      container: 'py-16',
      iconWrapper: 'w-20 h-20 mb-6',
      title: 'text-lg',
      description: 'text-base',
    },
  };

  const styles = sizeClasses[size];

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center',
        styles.container,
        className
      )}
    >
      <div
        className={cn(
          'text-text-muted',
          styles.iconWrapper
        )}
      >
        {icon || defaultIcons[variant]}
      </div>
      <h3
        className={cn(
          'font-semibold text-text-primary mb-1',
          styles.title
        )}
      >
        {title}
      </h3>
      {description && (
        <p
          className={cn(
            'text-text-secondary max-w-sm mb-4',
            styles.description
          )}
        >
          {description}
        </p>
      )}
      {action && (
        <Button
          variant="primary"
          size={size === 'lg' ? 'md' : 'sm'}
          onClick={action.onClick}
          leftIcon={action.icon || <Plus className="w-4 h-4" />}
        >
          {action.label}
        </Button>
      )}
    </div>
  );
}
