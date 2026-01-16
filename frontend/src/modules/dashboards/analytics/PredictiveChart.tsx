import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Brain, TrendingUp } from 'lucide-react';
import { formatCurrency } from '@core/utils/formatters';
import { Skeleton } from '@core/components/feedback';
import type { PredictiveData } from '../types/dashboard.types';

interface PredictiveChartProps {
  data: PredictiveData[];
  isLoading?: boolean;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    dataKey: string;
    value: number;
    color: string;
  }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg border p-4">
      <p className="font-medium text-gray-900 mb-2">{label}</p>
      {payload.map((entry, index) => {
        if (entry.dataKey === 'lowerBound' || entry.dataKey === 'upperBound') return null;
        const labels: Record<string, string> = {
          actual: 'Valor Real',
          predicted: 'Previsao IA',
        };
        return (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600">{labels[entry.dataKey]}:</span>
            <span className="font-medium text-gray-900">
              {formatCurrency(entry.value)}
            </span>
          </div>
        );
      })}
      {payload.find((p) => p.dataKey === 'lowerBound') && (
        <div className="mt-2 pt-2 border-t text-xs text-gray-500">
          Intervalo de confianca: {formatCurrency(payload.find((p) => p.dataKey === 'lowerBound')?.value || 0)} -{' '}
          {formatCurrency(payload.find((p) => p.dataKey === 'upperBound')?.value || 0)}
        </div>
      )}
    </div>
  );
}

export function PredictiveChart({ data, isLoading }: PredictiveChartProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6">
        <Skeleton height={24} className="w-48 mb-4" />
        <Skeleton height={300} />
      </div>
    );
  }

  // Find where prediction starts (no actual value)
  const predictionStartIndex = data.findIndex((d) => d.actual === undefined);

  return (
    <div className="bg-white rounded-xl shadow-card p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-conecta-laranja" />
            <h3 className="text-lg font-semibold text-gray-900">
              Analise Preditiva
            </h3>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Previsao de receita para os proximos 3 meses
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
          <TrendingUp className="w-4 h-4" />
          95% precisao
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0A2540" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#0A2540" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FF6B35" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#FF6B35" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FF6B35" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#FF6B35" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
            <XAxis
              dataKey="date"
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

            {/* Confidence interval */}
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="none"
              fill="url(#colorConfidence)"
              fillOpacity={1}
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="none"
              fill="#ffffff"
              fillOpacity={1}
            />

            {/* Actual line */}
            <Area
              type="monotone"
              dataKey="actual"
              stroke="#0A2540"
              strokeWidth={2}
              fill="url(#colorActual)"
              connectNulls={false}
            />

            {/* Predicted line */}
            <Area
              type="monotone"
              dataKey="predicted"
              stroke="#FF6B35"
              strokeWidth={2}
              strokeDasharray="5 5"
              fill="url(#colorPredicted)"
            />

            {/* Vertical line at prediction start */}
            {predictionStartIndex > 0 && (
              <ReferenceLine
                x={data[predictionStartIndex]?.date}
                stroke="#9ca3af"
                strokeDasharray="3 3"
                label={{
                  value: 'Previsao',
                  position: 'top',
                  fill: '#6b7280',
                  fontSize: 12,
                }}
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-conecta-escuro" />
          <span className="text-sm text-gray-600">Valor Real</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-conecta-laranja" />
          <span className="text-sm text-gray-600">Previsao IA</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-3 rounded bg-conecta-laranja/20" />
          <span className="text-sm text-gray-600">Intervalo Confianca</span>
        </div>
      </div>
    </div>
  );
}

export default PredictiveChart;
