import { motion } from 'framer-motion';

interface ProgressRingProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  strokeWidth?: number;
  color?: string;
  backgroundColor?: string;
  label?: string;
  sublabel?: string;
  showValue?: boolean;
  valueFormat?: 'percent' | 'number' | 'custom';
  customValueRender?: (value: number) => string;
  animated?: boolean;
  className?: string;
}

const sizeConfig = {
  sm: { size: 60, strokeWidth: 4, fontSize: 'text-sm', sublabelSize: 'text-xs' },
  md: { size: 80, strokeWidth: 6, fontSize: 'text-lg', sublabelSize: 'text-xs' },
  lg: { size: 120, strokeWidth: 8, fontSize: 'text-2xl', sublabelSize: 'text-sm' },
  xl: { size: 160, strokeWidth: 10, fontSize: 'text-3xl', sublabelSize: 'text-base' },
};

const defaultColors: Record<string, string> = {
  primary: '#0A2540',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6',
};

function getColorByValue(value: number): string {
  if (value >= 80) return defaultColors.success;
  if (value >= 60) return defaultColors.info;
  if (value >= 40) return defaultColors.warning;
  return defaultColors.danger;
}

export function ProgressRing({
  value,
  max = 100,
  size = 'md',
  strokeWidth,
  color,
  backgroundColor = '#e5e7eb',
  label,
  sublabel,
  showValue = true,
  valueFormat = 'percent',
  customValueRender,
  animated = true,
  className = '',
}: ProgressRingProps) {
  const config = sizeConfig[size];
  const actualStrokeWidth = strokeWidth || config.strokeWidth;
  const ringSize = config.size;
  const radius = (ringSize - actualStrokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const offset = circumference - (percentage / 100) * circumference;
  const actualColor = color || getColorByValue(percentage);

  const formatValue = (): string => {
    if (customValueRender) return customValueRender(value);
    switch (valueFormat) {
      case 'percent':
        return `${Math.round(percentage)}%`;
      case 'number':
        return value.toLocaleString('pt-BR');
      default:
        return `${value}`;
    }
  };

  return (
    <div className={`inline-flex flex-col items-center ${className}`}>
      <div className="relative" style={{ width: ringSize, height: ringSize }}>
        <svg
          width={ringSize}
          height={ringSize}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={ringSize / 2}
            cy={ringSize / 2}
            r={radius}
            fill="none"
            stroke={backgroundColor}
            strokeWidth={actualStrokeWidth}
          />
          {/* Progress circle */}
          <motion.circle
            cx={ringSize / 2}
            cy={ringSize / 2}
            r={radius}
            fill="none"
            stroke={actualColor}
            strokeWidth={actualStrokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={animated ? { strokeDashoffset: circumference } : { strokeDashoffset: offset }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>

        {/* Center content */}
        {showValue && (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`${config.fontSize} font-bold text-gray-900`}>
              {formatValue()}
            </span>
            {sublabel && (
              <span className={`${config.sublabelSize} text-gray-500`}>
                {sublabel}
              </span>
            )}
          </div>
        )}
      </div>

      {label && (
        <p className="mt-2 text-sm font-medium text-gray-700 text-center">
          {label}
        </p>
      )}
    </div>
  );
}

// Preset variants
export function SuccessRing(props: Omit<ProgressRingProps, 'color'>) {
  return <ProgressRing {...props} color={defaultColors.success} />;
}

export function WarningRing(props: Omit<ProgressRingProps, 'color'>) {
  return <ProgressRing {...props} color={defaultColors.warning} />;
}

export function DangerRing(props: Omit<ProgressRingProps, 'color'>) {
  return <ProgressRing {...props} color={defaultColors.danger} />;
}

export default ProgressRing;
