import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Skeleton } from '@core/components/feedback';
import type { ComplianceScore } from '../types/dashboard.types';

interface ComplianceChartProps {
  scores: ComplianceScore[];
  isLoading?: boolean;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: ComplianceScore;
  }>;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;

  return (
    <div className="bg-white rounded-lg shadow-lg border p-3">
      <p className="font-medium text-gray-900">{data.label}</p>
      <p className="text-2xl font-bold" style={{ color: data.color }}>
        {data.score}%
      </p>
    </div>
  );
}

export function ComplianceChart({ scores, isLoading }: ComplianceChartProps) {
  const totalScore = scores.length > 0
    ? Math.round(scores.reduce((acc, s) => acc + s.score, 0) / scores.length)
    : 0;

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6 h-full">
        <Skeleton height={24} className="w-40 mb-4" />
        <div className="flex items-center justify-center">
          <Skeleton width={200} height={200} rounded="full" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-card p-6 h-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Compliance Score
      </h3>

      <div className="relative h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={scores}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={85}
              paddingAngle={3}
              dataKey="score"
              animationDuration={1000}
            >
              {scores.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Center score */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <p className="text-4xl font-bold text-gray-900">{totalScore}%</p>
            <p className="text-sm text-gray-500">Score Geral</p>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 space-y-2">
        {scores.map((score) => (
          <div key={score.category} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: score.color }}
              />
              <span className="text-sm text-gray-600">{score.label}</span>
            </div>
            <span className="text-sm font-medium text-gray-900">{score.score}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ComplianceChart;
