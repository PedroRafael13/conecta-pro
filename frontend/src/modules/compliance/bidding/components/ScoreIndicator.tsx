'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';

type ScoreSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface ScoreIndicatorProps {
  score: number; // 0-100
  size?: ScoreSize;
  showLabel?: boolean;
  label?: string;
  animate?: boolean;
  showPercentage?: boolean;
  className?: string;
}

const sizeConfig: Record<
  ScoreSize,
  {
    container: string;
    circle: number;
    stroke: number;
    fontSize: string;
    labelSize: string;
  }
> = {
  xs: { container: 'w-8 h-8', circle: 28, stroke: 3, fontSize: 'text-xs', labelSize: 'text-[8px]' },
  sm: { container: 'w-12 h-12', circle: 44, stroke: 4, fontSize: 'text-sm', labelSize: 'text-[10px]' },
  md: { container: 'w-16 h-16', circle: 60, stroke: 5, fontSize: 'text-lg', labelSize: 'text-xs' },
  lg: { container: 'w-24 h-24', circle: 88, stroke: 6, fontSize: 'text-2xl', labelSize: 'text-sm' },
  xl: { container: 'w-32 h-32', circle: 120, stroke: 8, fontSize: 'text-3xl', labelSize: 'text-base' },
};

function getScoreColor(score: number): { main: string; bg: string; text: string } {
  if (score >= 80) {
    return { main: '#22c55e', bg: 'bg-green-50', text: 'text-green-600' }; // green
  }
  if (score >= 60) {
    return { main: '#FF6B35', bg: 'bg-orange-50', text: 'text-[#FF6B35]' }; // conecta-laranja
  }
  if (score >= 40) {
    return { main: '#eab308', bg: 'bg-yellow-50', text: 'text-yellow-600' }; // yellow
  }
  return { main: '#ef4444', bg: 'bg-red-50', text: 'text-red-600' }; // red
}

function getScoreLabel(score: number): string {
  if (score >= 80) return 'Excelente';
  if (score >= 60) return 'Bom';
  if (score >= 40) return 'Regular';
  return 'Baixo';
}

export function ScoreIndicator({
  score,
  size = 'md',
  showLabel = false,
  label,
  animate = true,
  showPercentage = true,
  className,
}: ScoreIndicatorProps) {
  const config = sizeConfig[size];
  const colors = getScoreColor(score);
  const displayLabel = label || getScoreLabel(score);

  // SVG circle calculations
  const radius = (config.circle - config.stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className={clsx('flex flex-col items-center', className)}>
      <div className={clsx('relative', config.container)}>
        {/* Background circle */}
        <svg className="w-full h-full -rotate-90" viewBox={`0 0 ${config.circle} ${config.circle}`}>
          <circle
            cx={config.circle / 2}
            cy={config.circle / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={config.stroke}
          />

          {/* Progress circle */}
          <motion.circle
            cx={config.circle / 2}
            cy={config.circle / 2}
            r={radius}
            fill="none"
            stroke={colors.main}
            strokeWidth={config.stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={animate ? { strokeDashoffset: circumference } : { strokeDashoffset: offset }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>

        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            initial={animate ? { opacity: 0, scale: 0.5 } : false}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.3 }}
            className={clsx('font-bold leading-none', config.fontSize, colors.text)}
          >
            {Math.round(score)}
          </motion.span>
          {showPercentage && size !== 'xs' && (
            <span className={clsx('text-gray-400', config.labelSize)}>%</span>
          )}
        </div>
      </div>

      {/* Label */}
      {showLabel && (
        <motion.span
          initial={animate ? { opacity: 0, y: 5 } : false}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.3 }}
          className={clsx(
            'mt-1 font-medium text-center',
            config.labelSize,
            colors.text
          )}
        >
          {displayLabel}
        </motion.span>
      )}
    </div>
  );
}

// Additional component for score comparison
interface ScoreComparisonProps {
  scores: Array<{
    label: string;
    score: number;
  }>;
  className?: string;
}

export function ScoreComparison({ scores, className }: ScoreComparisonProps) {
  return (
    <div className={clsx('space-y-3', className)}>
      {scores.map((item, index) => {
        const colors = getScoreColor(item.score);

        return (
          <div key={index} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">{item.label}</span>
              <span className={clsx('font-semibold', colors.text)}>
                {Math.round(item.score)}%
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${item.score}%` }}
                transition={{ duration: 0.8, delay: index * 0.1, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ backgroundColor: colors.main }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Score badge variant
interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function ScoreBadge({ score, size = 'md', className }: ScoreBadgeProps) {
  const colors = getScoreColor(score);
  const label = getScoreLabel(score);

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 font-semibold rounded-full',
        colors.bg,
        colors.text,
        sizeStyles[size],
        className
      )}
    >
      <span className="font-bold">{Math.round(score)}</span>
      <span className="opacity-80">- {label}</span>
    </span>
  );
}
