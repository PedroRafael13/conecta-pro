import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendingUp } from 'lucide-react';

interface TrendData {
  date: string;
  score: number;
}

interface ComplianceTrendProps {
  data: TrendData[];
  isLoading?: boolean;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg border p-3">
      <p className="text-sm font-medium text-gray-900">{label}</p>
      <p className="text-lg font-bold text-conecta-escuro">{payload[0].value}%</p>
    </div>
  );
}

export function ComplianceTrend({ data, isLoading }: ComplianceTrendProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-40 mb-4" />
        <div className="h-64 bg-gray-200 rounded" />
      </div>
    );
  }

  const minScore = Math.min(...data.map(d => d.score)) - 5;
  const maxScore = Math.max(...data.map(d => d.score)) + 5;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-conecta-escuro" />
          <h3 className="text-lg font-semibold text-gray-900">Tendencia Compliance</h3>
        </div>
        <span className="text-sm text-gray-500">Ultimos 6 meses</span>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0A2540" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#0A2540" stopOpacity={0} />
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
              domain={[minScore, maxScore]}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              y={90}
              stroke="#22c55e"
              strokeDasharray="3 3"
              label={{ value: 'Meta', position: 'right', fill: '#22c55e', fontSize: 10 }}
            />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#0A2540"
              strokeWidth={2}
              dot={{ fill: '#0A2540', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: '#FF6B35' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export default ComplianceTrend;
