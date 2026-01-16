import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

type TrendDirection = 'up' | 'down' | 'neutral';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    direction: TrendDirection;
    label?: string;
  };
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  className?: string;
  children?: ReactNode;
}

const variantStyles = {
  default: {
    bg: 'bg-white',
    iconBg: 'bg-gray-100',
    iconColor: 'text-gray-600',
  },
  primary: {
    bg: 'bg-gradient-to-br from-conecta-escuro to-conecta-medio',
    iconBg: 'bg-white/20',
    iconColor: 'text-white',
  },
  success: {
    bg: 'bg-gradient-to-br from-green-500 to-emerald-600',
    iconBg: 'bg-white/20',
    iconColor: 'text-white',
  },
  warning: {
    bg: 'bg-gradient-to-br from-yellow-500 to-orange-500',
    iconBg: 'bg-white/20',
    iconColor: 'text-white',
  },
  danger: {
    bg: 'bg-gradient-to-br from-red-500 to-rose-600',
    iconBg: 'bg-white/20',
    iconColor: 'text-white',
  },
};

const sizeStyles = {
  sm: {
    padding: 'p-4',
    iconSize: 'w-8 h-8',
    iconWrapper: 'p-2',
    valueSize: 'text-2xl',
    titleSize: 'text-xs',
  },
  md: {
    padding: 'p-5',
    iconSize: 'w-10 h-10',
    iconWrapper: 'p-2.5',
    valueSize: 'text-3xl',
    titleSize: 'text-sm',
  },
  lg: {
    padding: 'p-6',
    iconSize: 'w-12 h-12',
    iconWrapper: 'p-3',
    valueSize: 'text-4xl',
    titleSize: 'text-base',
  },
};

const TrendIcon = ({ direction }: { direction: TrendDirection }) => {
  switch (direction) {
    case 'up':
      return <TrendingUp className="w-4 h-4" />;
    case 'down':
      return <TrendingDown className="w-4 h-4" />;
    default:
      return <Minus className="w-4 h-4" />;
  }
};

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'default',
  size = 'md',
  loading = false,
  className = '',
  children,
}: StatCardProps) {
  const styles = variantStyles[variant];
  const sizes = sizeStyles[size];
  const isColored = variant !== 'default';

  const getTrendColor = (direction: TrendDirection) => {
    if (isColored) return 'text-white/80';
    switch (direction) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`${styles.bg} rounded-xl shadow-card ${sizes.padding} ${className}`}
    >
      {loading ? (
        <div className="animate-pulse">
          <div className="flex items-center gap-4">
            <div className={`${sizes.iconWrapper} rounded-xl bg-gray-200`}>
              <div className={`${sizes.iconSize}`} />
            </div>
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-20 mb-2" />
              <div className="h-8 bg-gray-200 rounded w-32" />
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              {Icon && (
                <div className={`${sizes.iconWrapper} rounded-xl ${styles.iconBg}`}>
                  <Icon className={`${sizes.iconSize} ${styles.iconColor}`} />
                </div>
              )}
              <div>
                <p
                  className={`${sizes.titleSize} ${
                    isColored ? 'text-white/70' : 'text-gray-500'
                  } font-medium`}
                >
                  {title}
                </p>
                <p
                  className={`${sizes.valueSize} font-bold mt-1 ${
                    isColored ? 'text-white' : 'text-gray-900'
                  }`}
                >
                  {value}
                </p>
                {subtitle && (
                  <p
                    className={`text-xs mt-1 ${
                      isColored ? 'text-white/60' : 'text-gray-400'
                    }`}
                  >
                    {subtitle}
                  </p>
                )}
              </div>
            </div>

            {trend && (
              <div
                className={`flex items-center gap-1 ${getTrendColor(trend.direction)}`}
              >
                <TrendIcon direction={trend.direction} />
                <span className="text-sm font-medium">{trend.value}%</span>
              </div>
            )}
          </div>

          {trend?.label && (
            <p
              className={`text-xs mt-3 ${
                isColored ? 'text-white/60' : 'text-gray-400'
              }`}
            >
              {trend.label}
            </p>
          )}

          {children}
        </>
      )}
    </motion.div>
  );
}

export default StatCard;
