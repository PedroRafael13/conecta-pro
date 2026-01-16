import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Skeleton } from '@core/components/feedback';
import type { OperationStatus } from '../types/dashboard.types';

interface OperationsChartProps {
  operations: OperationStatus[];
  isLoading?: boolean;
}

const statusColors = {
  ok: '#22c55e',
  warning: '#f59e0b',
  critical: '#ef4444',
};

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: OperationStatus;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const statusLabel = {
    ok: 'Operacional',
    warning: 'Atencao',
    critical: 'Critico',
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border p-3">
      <p className="font-medium text-gray-900">{data.label}</p>
      <div className="flex items-center gap-2 mt-1">
        <div
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: statusColors[data.status] }}
        />
        <span className="text-sm text-gray-600">{statusLabel[data.status]}</span>
      </div>
      <p className="text-2xl font-bold text-gray-900 mt-1">{data.percentage}%</p>
    </div>
  );
}

export function OperationsChart({ operations, isLoading }: OperationsChartProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6 h-full">
        <Skeleton height={24} className="w-40 mb-4" />
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center gap-4">
              <Skeleton height={16} className="w-24" />
              <Skeleton height={24} className="flex-1" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-card p-6 h-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Status Operacoes
      </h3>

      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={operations}
            layout="vertical"
            margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
          >
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis
              type="category"
              dataKey="label"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              width={100}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f3f4f6' }} />
            <Bar
              dataKey="percentage"
              radius={[0, 4, 4, 0]}
              barSize={20}
              animationDuration={1000}
            >
              {operations.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={statusColors[entry.status]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-6">
        {Object.entries(statusColors).map(([status, color]) => (
          <div key={status} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-gray-600 capitalize">
              {status === 'ok' ? 'Operacional' : status === 'warning' ? 'Atencao' : 'Critico'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default OperationsChart;
