import { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Download, RefreshCw } from 'lucide-react';
import { formatCurrency } from '@core/utils/formatters';
import { Skeleton } from '@core/components/feedback';
import type { RevenueChartData } from '../types/dashboard.types';

interface RevenueChartProps {
  data: RevenueChartData[];
  isLoading?: boolean;
  onRefresh?: () => void;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg border p-3">
      <p className="font-medium text-gray-900 mb-2">{label}</p>
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center gap-2 text-sm">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-gray-600">{entry.name}:</span>
          <span className="font-medium text-gray-900">
            {formatCurrency(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

export function RevenueChart({ data, isLoading, onRefresh }: RevenueChartProps) {
  const [activeLines, setActiveLines] = useState({
    revenue: true,
    forecast: true,
  });

  const handleLegendClick = (dataKey: string) => {
    setActiveLines((prev) => ({
      ...prev,
      [dataKey]: !prev[dataKey as keyof typeof prev],
    }));
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6">
        <div className="flex items-center justify-between mb-6">
          <Skeleton height={24} className="w-48" />
          <Skeleton height={32} className="w-24" />
        </div>
        <Skeleton height={300} />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Receita vs Previsao
          </h3>
          <p className="text-sm text-gray-500">Ultimos 12 meses</p>
        </div>
        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0A2540" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#0A2540" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FF6B35" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#FF6B35" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
            <XAxis
              dataKey="label"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#6b7280' }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              onClick={(e) => handleLegendClick(e.dataKey as string)}
              wrapperStyle={{ paddingTop: 20 }}
              formatter={(value, entry) => (
                <span
                  className={`cursor-pointer ${
                    !activeLines[entry.dataKey as keyof typeof activeLines]
                      ? 'opacity-40'
                      : ''
                  }`}
                >
                  {value}
                </span>
              )}
            />
            {activeLines.revenue && (
              <Area
                type="monotone"
                dataKey="revenue"
                name="Receita Real"
                stroke="#0A2540"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorRevenue)"
                animationDuration={1000}
              />
            )}
            {activeLines.forecast && (
              <Area
                type="monotone"
                dataKey="forecast"
                name="Previsao"
                stroke="#FF6B35"
                strokeWidth={2}
                strokeDasharray="5 5"
                fillOpacity={1}
                fill="url(#colorForecast)"
                animationDuration={1000}
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default RevenueChart;
