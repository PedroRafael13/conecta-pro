import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from 'recharts';

type ChartType = 'line' | 'area' | 'bar' | 'sparkline';

interface MiniChartProps {
  data: number[] | { value: number; label?: string }[];
  type?: ChartType;
  color?: string;
  height?: number;
  width?: number | string;
  showTooltip?: boolean;
  animated?: boolean;
  className?: string;
  trend?: 'up' | 'down' | 'neutral';
}

const defaultColors = {
  up: '#22c55e',
  down: '#ef4444',
  neutral: '#6b7280',
  primary: '#0A2540',
};

export function MiniChart({
  data,
  type = 'sparkline',
  color,
  height = 40,
  width = '100%',
  animated = true,
  className = '',
  trend,
}: MiniChartProps) {
  const chartData = useMemo(() => {
    return data.map((item, index) => ({
      index,
      value: typeof item === 'number' ? item : item.value,
      label: typeof item === 'number' ? `${index}` : item.label,
    }));
  }, [data]);

  const calculatedTrend = useMemo(() => {
    if (trend) return trend;
    if (chartData.length < 2) return 'neutral';
    const firstValue = chartData[0].value;
    const lastValue = chartData[chartData.length - 1].value;
    if (lastValue > firstValue) return 'up';
    if (lastValue < firstValue) return 'down';
    return 'neutral';
  }, [chartData, trend]);

  const chartColor = color || defaultColors[calculatedTrend];

  const renderChart = () => {
    switch (type) {
      case 'area':
        return (
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id={`miniGradient-${chartColor}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={chartColor} stopOpacity={0.3} />
                <stop offset="100%" stopColor={chartColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="value"
              stroke={chartColor}
              fill={`url(#miniGradient-${chartColor})`}
              strokeWidth={2}
              isAnimationActive={animated}
            />
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart data={chartData}>
            <Bar
              dataKey="value"
              fill={chartColor}
              radius={[2, 2, 0, 0]}
              isAnimationActive={animated}
            />
          </BarChart>
        );

      case 'line':
      case 'sparkline':
      default:
        return (
          <LineChart data={chartData}>
            <Line
              type="monotone"
              dataKey="value"
              stroke={chartColor}
              strokeWidth={2}
              dot={false}
              isAnimationActive={animated}
            />
          </LineChart>
        );
    }
  };

  return (
    <motion.div
      initial={animated ? { opacity: 0 } : undefined}
      animate={{ opacity: 1 }}
      className={className}
      style={{ height, width }}
    >
      <ResponsiveContainer width="100%" height="100%">
        {renderChart()}
      </ResponsiveContainer>
    </motion.div>
  );
}

// Compact stat with mini chart
interface MiniStatProps {
  label: string;
  value: string | number;
  data: number[];
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  chartType?: ChartType;
  className?: string;
}

export function MiniStat({
  label,
  value,
  data,
  trend,
  trendValue,
  chartType = 'sparkline',
  className = '',
}: MiniStatProps) {
  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500';

  return (
    <div className={`flex items-center justify-between ${className}`}>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <div className="flex items-baseline gap-2">
          <span className="text-lg font-semibold text-gray-900">{value}</span>
          {trendValue && (
            <span className={`text-xs font-medium ${trendColor}`}>
              {trendValue}
            </span>
          )}
        </div>
      </div>
      <MiniChart data={data} type={chartType} trend={trend} height={32} width={80} />
    </div>
  );
}

export default MiniChart;
