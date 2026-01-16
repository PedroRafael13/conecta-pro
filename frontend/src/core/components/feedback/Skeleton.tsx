import { clsx } from 'clsx';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
}

const roundedClasses = {
  none: 'rounded-none',
  sm: 'rounded',
  md: 'rounded-md',
  lg: 'rounded-lg',
  full: 'rounded-full',
};

export function Skeleton({
  className,
  width,
  height,
  rounded = 'md',
}: SkeletonProps) {
  return (
    <div
      className={clsx(
        'animate-pulse bg-gray-200',
        roundedClasses[rounded],
        className
      )}
      style={{ width, height }}
    />
  );
}

export function SkeletonText({
  lines = 3,
  className,
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={clsx('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height={16}
          className={i === lines - 1 ? 'w-3/4' : 'w-full'}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={clsx('bg-white rounded-lg p-6 shadow-card', className)}>
      <div className="flex items-center gap-4 mb-4">
        <Skeleton width={48} height={48} rounded="full" />
        <div className="flex-1 space-y-2">
          <Skeleton height={16} className="w-1/3" />
          <Skeleton height={12} className="w-1/2" />
        </div>
      </div>
      <SkeletonText lines={3} />
    </div>
  );
}

export function SkeletonTable({
  rows = 5,
  cols = 4,
}: {
  rows?: number;
  cols?: number;
}) {
  return (
    <div className="bg-white rounded-lg shadow-card overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 px-6 py-3 border-b flex gap-4">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} height={16} className="flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={rowIndex}
          className="px-6 py-4 border-b last:border-b-0 flex gap-4"
        >
          {Array.from({ length: cols }).map((_, colIndex) => (
            <Skeleton key={colIndex} height={16} className="flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

export default Skeleton;
