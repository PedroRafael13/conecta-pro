/**
 * ECharts Bundle - Carregado sob demanda
 * Mais pesado que recharts, usar apenas quando necessário
 */
'use client';

// @ts-ignore - echarts-for-react não tem tipos definidos
import ReactECharts from 'echarts-for-react';

interface EChartsBundleProps {
  option: any;
  style?: React.CSSProperties;
}

export default function EChartsBundle({ option, style }: EChartsBundleProps) {
  return (
    <ReactECharts
      option={option}
      style={{ height: 300, ...style }}
      opts={{ renderer: 'svg' }}
    />
  );
}
