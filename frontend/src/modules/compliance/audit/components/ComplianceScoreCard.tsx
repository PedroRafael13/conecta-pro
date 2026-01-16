import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Shield, TrendingUp, TrendingDown } from 'lucide-react';
import type { ComplianceScore } from '../types/audit.types';

interface ComplianceScoreCardProps {
  score: ComplianceScore;
  isLoading?: boolean;
}

export function ComplianceScoreCard({ score, isLoading }: ComplianceScoreCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6 animate-pulse">
        <div className="h-48 bg-gray-200 rounded-lg" />
      </div>
    );
  }

  const chartData = [
    { name: 'Score', value: score.overall },
    { name: 'Remaining', value: 100 - score.overall },
  ];

  const getScoreColor = (value: number) => {
    if (value >= 90) return '#22c55e';
    if (value >= 70) return '#f97316';
    return '#ef4444';
  };

  const lastTrend = score.trend.length >= 2
    ? score.trend[score.trend.length - 1].score - score.trend[score.trend.length - 2].score
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-card p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-conecta-escuro" />
          <h3 className="text-lg font-semibold text-gray-900">Compliance Score</h3>
        </div>
        <div className={`flex items-center gap-1 text-sm ${lastTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {lastTrend >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          {lastTrend >= 0 ? '+' : ''}{lastTrend}%
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* Donut Chart */}
        <div className="relative w-32 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={55}
                startAngle={90}
                endAngle={-270}
                dataKey="value"
                strokeWidth={0}
              >
                <Cell fill={getScoreColor(score.overall)} />
                <Cell fill="#e5e7eb" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold text-gray-900">{score.overall}%</span>
          </div>
        </div>

        {/* Breakdown */}
        <div className="flex-1 space-y-3">
          {score.breakdown.map((item) => (
            <div key={item.category}>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600">{item.category}</span>
                <span className="font-medium text-gray-900">{item.score}%</span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.score}%` }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: item.color }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

export default ComplianceScoreCard;
