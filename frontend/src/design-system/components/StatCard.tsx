'use client';

import { type ReactNode } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/shared/utils/cn';
import { Card } from './Card';

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  changePeriod?: string;
  icon?: ReactNode;
  iconColor?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  trend?: 'up' | 'down' | 'neutral';
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

const iconColorClasses = {
  primary: 'bg-accent-primary/10 text-accent-primary',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
  danger: 'bg-danger/10 text-danger',
  info: 'bg-info/10 text-info',
};

export function StatCard({
  title,
  value,
  change,
  changeLabel,
  changePeriod = 'vs. mês anterior',
  icon,
  iconColor = 'primary',
  trend,
  loading,
  className,
  onClick,
}: StatCardProps) {
  // Determine trend from change if not provided
  const actualTrend = trend || (change !== undefined ? (change > 0 ? 'up' : change < 0 ? 'down' : 'neutral') : undefined);

  const TrendIcon = actualTrend === 'up' ? TrendingUp : actualTrend === 'down' ? TrendingDown : Minus;

  const trendColorClass = actualTrend === 'up'
    ? 'text-success'
    : actualTrend === 'down'
    ? 'text-danger'
    : 'text-text-muted';

  if (loading) {
    return (
      <Card className={cn('p-5', className)}>
        <div className="space-y-3">
          <div className="h-4 w-24 bg-bg-tertiary rounded animate-pulse" />
          <div className="h-8 w-32 bg-bg-tertiary rounded animate-pulse" />
          <div className="h-4 w-20 bg-bg-tertiary rounded animate-pulse" />
        </div>
      </Card>
    );
  }

  return (
    <Card
      className={cn('p-5', onClick && 'cursor-pointer', className)}
      hover={onClick ? true : undefined}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-text-secondary">{title}</p>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-display font-bold text-text-primary"
          >
            {value}
          </motion.p>
          {change !== undefined && (
            <div className="flex items-center gap-1.5 mt-2">
              <span className={cn('flex items-center gap-0.5 text-sm font-medium', trendColorClass)}>
                <TrendIcon className="w-4 h-4" />
                {Math.abs(change)}%
              </span>
              <span className="text-xs text-text-muted">
                {changeLabel || changePeriod}
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className={cn('p-3 rounded-xl', iconColorClasses[iconColor])}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}

// Mini Stat Card (compact version)
export interface MiniStatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  className?: string;
}

export function MiniStatCard({ label, value, icon, className }: MiniStatCardProps) {
  return (
    <div className={cn('flex items-center gap-3 p-3 rounded-lg bg-bg-tertiary', className)}>
      {icon && (
        <div className="p-2 rounded-lg bg-bg-elevated text-text-secondary">
          {icon}
        </div>
      )}
      <div>
        <p className="text-2xs text-text-muted uppercase tracking-wide">{label}</p>
        <p className="text-lg font-semibold text-text-primary">{value}</p>
      </div>
    </div>
  );
}

// Stat Grid
export interface StatGridProps {
  children: ReactNode;
  columns?: 2 | 3 | 4 | 5;
  className?: string;
}

export function StatGrid({ children, columns = 4, className }: StatGridProps) {
  const gridClasses = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-5',
  };

  return (
    <div className={cn('grid gap-4', gridClasses[columns], className)}>
      {children}
    </div>
  );
}
