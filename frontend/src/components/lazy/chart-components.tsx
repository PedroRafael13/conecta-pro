/**
 * Lazy-loaded Chart Components
 *
 * Estes componentes são carregados sob demanda para reduzir o bundle inicial.
 * Use quando os gráficos não são críticos para o primeiro paint.
 */

import { Suspense, lazy } from 'react';
import { Skeleton } from '@/components/ui/skeleton';

// Lazy load recharts components
const RechartsComponents = lazy(() => import('./recharts-bundle'));

// Loading fallback
const ChartSkeleton = () => (
  <div className="w-full h-[300px] flex items-center justify-center">
    <Skeleton className="w-full h-full" />
  </div>
);

interface LazyChartProps {
  type: 'line' | 'bar' | 'pie' | 'area';
  data: any[];
  config: any;
}

export function LazyChart({ type, data, config }: LazyChartProps) {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <RechartsComponents type={type} data={data} config={config} />
    </Suspense>
  );
}

// ECharts lazy loader (mais pesado)
const EChartsComponent = lazy(() => import('./echarts-bundle'));

interface LazyEChartsProps {
  option: any;
  style?: React.CSSProperties;
}

export function LazyECharts({ option, style }: LazyEChartsProps) {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <EChartsComponent option={option} style={style} />
    </Suspense>
  );
}
