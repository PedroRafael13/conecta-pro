'use client';

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, Clock } from 'lucide-react';

interface IoTChartProps {
  data: Array<{
    time: string;
    valor: number;
    min?: number;
    max?: number;
  }>;
  sensorName?: string;
  unit?: string;
  limitMin?: number;
  limitMax?: number;
  type?: 'line' | 'area';
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  color?: string;
  period?: 'hora' | 'dia' | 'semana';
}

interface TooltipPayloadEntry {
  name: string;
  value: number;
  color: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
  unit?: string;
}

function CustomTooltip({ active, payload, label, unit = '' }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      {payload.map((entry, index) => (
        <p key={index} className="text-sm font-medium" style={{ color: entry.color }}>
          {entry.name}: {entry.value}{unit}
        </p>
      ))}
    </div>
  );
}

export function IoTChart({
  data,
  sensorName,
  unit = '',
  limitMin,
  limitMax,
  type = 'area',
  height = 300,
  showLegend = false,
  showGrid = true,
  color = '#3B82F6',
  period = 'hora'
}: IoTChartProps) {
  // Calcular estatisticas
  const stats = useMemo(() => {
    if (data.length === 0) return null;

    const valores = data.map(d => d.valor);
    const atual = valores[valores.length - 1];
    const anterior = valores.length > 1 ? valores[valores.length - 2] : atual;
    const media = valores.reduce((a, b) => a + b, 0) / valores.length;
    const minimo = Math.min(...valores);
    const maximo = Math.max(...valores);
    const variacao = atual - anterior;
    const variacaoPercent = anterior !== 0 ? ((atual - anterior) / anterior) * 100 : 0;

    return {
      atual,
      media: Number(media.toFixed(2)),
      minimo: Number(minimo.toFixed(2)),
      maximo: Number(maximo.toFixed(2)),
      variacao: Number(variacao.toFixed(2)),
      variacaoPercent: Number(variacaoPercent.toFixed(1)),
      tendencia: variacao > 0 ? 'up' : variacao < 0 ? 'down' : 'stable'
    };
  }, [data]);

  const getTrendIcon = () => {
    if (!stats) return null;
    switch (stats.tendencia) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPeriodLabel = () => {
    switch (period) {
      case 'hora': return 'Ultimas 24 horas';
      case 'dia': return 'Ultimos 7 dias';
      case 'semana': return 'Ultimas 4 semanas';
      default: return '';
    }
  };

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-lg">
        <Clock className="w-12 h-12 text-gray-300 mb-2" />
        <p className="text-gray-500">Sem dados para exibir</p>
      </div>
    );
  }

  const ChartComponent = type === 'line' ? LineChart : AreaChart;

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      {(sensorName || stats) && (
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              {sensorName && (
                <h3 className="font-semibold text-gray-900">{sensorName}</h3>
              )}
              <p className="text-xs text-gray-500 mt-0.5">{getPeriodLabel()}</p>
            </div>

            {stats && (
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-xs text-gray-500">Atual</p>
                  <div className="flex items-center space-x-1">
                    <span className="text-lg font-bold text-gray-900">
                      {stats.atual}{unit}
                    </span>
                    {getTrendIcon()}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="p-4">
        <ResponsiveContainer width="100%" height={height}>
          <ChartComponent data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            {showGrid && (
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            )}

            <XAxis
              dataKey="time"
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb' }}
            />

            <YAxis
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${value}${unit}`}
              domain={['auto', 'auto']}
            />

            <Tooltip content={<CustomTooltip unit={unit} />} />

            {showLegend && <Legend />}

            {/* Limit lines */}
            {limitMin !== undefined && (
              <ReferenceLine
                y={limitMin}
                stroke="#FCD34D"
                strokeDasharray="5 5"
                label={{
                  value: `Min: ${limitMin}`,
                  fill: '#FCD34D',
                  fontSize: 10,
                  position: 'left'
                }}
              />
            )}

            {limitMax !== undefined && (
              <ReferenceLine
                y={limitMax}
                stroke="#EF4444"
                strokeDasharray="5 5"
                label={{
                  value: `Max: ${limitMax}`,
                  fill: '#EF4444',
                  fontSize: 10,
                  position: 'left'
                }}
              />
            )}

            {type === 'area' ? (
              <Area
                type="monotone"
                dataKey="valor"
                name="Valor"
                stroke={color}
                fill={`${color}20`}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: color }}
              />
            ) : (
              <Line
                type="monotone"
                dataKey="valor"
                name="Valor"
                stroke={color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: color }}
              />
            )}

            {/* Min/Max bands if available */}
            {data[0]?.min !== undefined && data[0]?.max !== undefined && (
              <>
                <Area
                  type="monotone"
                  dataKey="max"
                  name="Maximo"
                  stroke="transparent"
                  fill={`${color}10`}
                />
                <Area
                  type="monotone"
                  dataKey="min"
                  name="Minimo"
                  stroke="transparent"
                  fill="white"
                />
              </>
            )}
          </ChartComponent>
        </ResponsiveContainer>
      </div>

      {/* Stats Footer */}
      {stats && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-500">Media</p>
              <p className="text-sm font-semibold text-gray-900">{stats.media}{unit}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Minimo</p>
              <p className="text-sm font-semibold text-gray-900">{stats.minimo}{unit}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Maximo</p>
              <p className="text-sm font-semibold text-gray-900">{stats.maximo}{unit}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Variacao</p>
              <p className={`text-sm font-semibold ${
                stats.variacao > 0 ? 'text-green-600' :
                stats.variacao < 0 ? 'text-red-600' :
                'text-gray-600'
              }`}>
                {stats.variacao > 0 ? '+' : ''}{stats.variacao}{unit} ({stats.variacaoPercent}%)
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Componente de mini chart para cards
interface MiniIoTChartProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  showTrend?: boolean;
}

export function MiniIoTChart({
  data,
  width = 80,
  height = 32,
  color = '#3B82F6',
  showTrend = true
}: MiniIoTChartProps) {
  if (data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  const trend = data[data.length - 1] - data[0];
  const strokeColor = showTrend
    ? trend > 0 ? '#10B981' : trend < 0 ? '#EF4444' : color
    : color;

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points}
        fill="none"
        stroke={strokeColor}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* End dot */}
      <circle
        cx={width}
        cy={height - ((data[data.length - 1] - min) / range) * height}
        r={2}
        fill={strokeColor}
      />
    </svg>
  );
}

export default IoTChart;
