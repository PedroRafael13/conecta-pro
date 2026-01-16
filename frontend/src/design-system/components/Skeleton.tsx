'use client';

import { cn } from '@/shared/utils/cn';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'shimmer' | 'none';
}

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
  animation = 'pulse',
}: SkeletonProps) {
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: '',
    rounded: 'rounded-lg',
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    shimmer: 'animate-shimmer',
    none: '',
  };

  return (
    <div
      className={cn(
        'bg-bg-tertiary',
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
    />
  );
}

// Skeleton Text Block
interface SkeletonTextProps {
  lines?: number;
  className?: string;
}

export function SkeletonText({ lines = 3, className }: SkeletonTextProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          className={i === lines - 1 ? 'w-3/4' : 'w-full'}
        />
      ))}
    </div>
  );
}

// Skeleton Card
interface SkeletonCardProps {
  className?: string;
  showImage?: boolean;
  showAvatar?: boolean;
}

export function SkeletonCard({
  className,
  showImage = true,
  showAvatar = false,
}: SkeletonCardProps) {
  return (
    <div
      className={cn(
        'bg-bg-secondary rounded-xl border border-border-subtle p-4',
        className
      )}
    >
      {showImage && (
        <Skeleton variant="rounded" className="w-full h-40 mb-4" />
      )}
      <div className="flex items-start gap-3">
        {showAvatar && (
          <Skeleton variant="circular" width={40} height={40} />
        )}
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" className="w-3/4 h-5" />
          <Skeleton variant="text" className="w-full" />
          <Skeleton variant="text" className="w-1/2" />
        </div>
      </div>
    </div>
  );
}

// Skeleton Table
interface SkeletonTableProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export function SkeletonTable({
  rows = 5,
  columns = 4,
  className,
}: SkeletonTableProps) {
  return (
    <div
      className={cn(
        'bg-bg-secondary rounded-xl border border-border-subtle overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <div className="bg-bg-tertiary px-4 py-3 border-b border-border-default">
        <div className="flex gap-4">
          {Array.from({ length: columns }).map((_, i) => (
            <Skeleton key={i} variant="text" className="flex-1 h-4" />
          ))}
        </div>
      </div>
      {/* Rows */}
      <div className="divide-y divide-border-subtle">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="px-4 py-3">
            <div className="flex gap-4">
              {Array.from({ length: columns }).map((_, colIndex) => (
                <Skeleton
                  key={colIndex}
                  variant="text"
                  className="flex-1 h-4"
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Skeleton Stats
export function SkeletonStats({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'bg-bg-secondary rounded-xl border border-border-subtle p-5',
        className
      )}
    >
      <Skeleton variant="text" className="w-1/3 h-3 mb-3" />
      <Skeleton variant="text" className="w-2/3 h-8 mb-2" />
      <Skeleton variant="text" className="w-1/4 h-3" />
    </div>
  );
}
