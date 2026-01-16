import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { MoreVertical, Download, Maximize2, RefreshCw } from 'lucide-react';

type ChartType = 'line' | 'area' | 'bar';

interface ChartConfig {
  dataKey: string;
  color: string;
  name?: string;
  type?: 'monotone' | 'linear' | 'step';
}

interface ChartWidgetProps {
  title: string;
  subtitle?: string;
  data: Record<string, unknown>[];
  xAxisKey: string;
  charts: ChartConfig[];
  chartType?: ChartType;
  height?: number;
  showGrid?: boolean;
  showLegend?: boolean;
  onRefresh?: () => void;
  onExport?: () => void;
  onExpand?: () => void;
  loading?: boolean;
}

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean;
  payload?: { color: string; name: string; value: number }[];
  label?: string;
}) => {
  if (!active || !payload) return null;

  return (
    <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
      <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center gap-2 text-sm">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-gray-600">{entry.name}:</span>
          <span className="font-medium">{entry.value.toLocaleString('pt-BR')}</span>
        </div>
      ))}
    </div>
  );
};

export function ChartWidget({
  title,
  subtitle,
  data,
  xAxisKey,
  charts,
  chartType = 'line',
  height = 300,
  showGrid = true,
  showLegend = true,
  onRefresh,
  onExport,
  onExpand,
  loading = false,
}: ChartWidgetProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 10, right: 30, left: 0, bottom: 0 },
    };

    const renderLines = () =>
      charts.map((chart) => (
        <Line
          key={chart.dataKey}
          type={chart.type || 'monotone'}
          dataKey={chart.dataKey}
          name={chart.name || chart.dataKey}
          stroke={chart.color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      ));

    const renderAreas = () =>
      charts.map((chart) => (
        <Area
          key={chart.dataKey}
          type={chart.type || 'monotone'}
          dataKey={chart.dataKey}
          name={chart.name || chart.dataKey}
          stroke={chart.color}
          fill={chart.color}
          fillOpacity={0.1}
          strokeWidth={2}
        />
      ));

    const renderBars = () =>
      charts.map((chart) => (
        <Bar
          key={chart.dataKey}
          dataKey={chart.dataKey}
          name={chart.name || chart.dataKey}
          fill={chart.color}
          radius={[4, 4, 0, 0]}
        />
      ));

    switch (chartType) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis dataKey={xAxisKey} tick={{ fontSize: 12 }} stroke="#9ca3af" />
            <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && <Legend />}
            {renderAreas()}
          </AreaChart>
        );
      case 'bar':
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis dataKey={xAxisKey} tick={{ fontSize: 12 }} stroke="#9ca3af" />
            <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && <Legend />}
            {renderBars()}
          </BarChart>
        );
      default:
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis dataKey={xAxisKey} tick={{ fontSize: 12 }} stroke="#9ca3af" />
            <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && <Legend />}
            {renderLines()}
          </LineChart>
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-card p-6"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
        </div>
        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <MoreVertical className="w-5 h-5 text-gray-400" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-10 min-w-[140px]">
              {onRefresh && (
                <button
                  onClick={() => {
                    onRefresh();
                    setMenuOpen(false);
                  }}
                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <RefreshCw className="w-4 h-4" />
                  Atualizar
                </button>
              )}
              {onExport && (
                <button
                  onClick={() => {
                    onExport();
                    setMenuOpen(false);
                  }}
                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Download className="w-4 h-4" />
                  Exportar
                </button>
              )}
              {onExpand && (
                <button
                  onClick={() => {
                    onExpand();
                    setMenuOpen(false);
                  }}
                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Maximize2 className="w-4 h-4" />
                  Expandir
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Chart */}
      <div style={{ height }} className="relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-conecta-escuro" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        )}
      </div>
    </motion.div>
  );
}

export default ChartWidget;
