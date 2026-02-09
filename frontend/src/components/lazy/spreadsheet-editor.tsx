/**
 * Lazy-loaded Spreadsheet Editor
 * Carregado apenas quando necessário
 */

import { Suspense, lazy } from 'react';
import { Skeleton } from '@/components/ui/skeleton';

const SpreadsheetComponent = lazy(() => import('./spreadsheet-bundle'));

const SpreadsheetSkeleton = () => (
  <div className="w-full h-[400px]">
    <Skeleton className="w-full h-full" />
  </div>
);

interface LazySpreadsheetProps {
  data: any[][];
  onChange?: (data: any[][]) => void;
  readOnly?: boolean;
}

export function LazySpreadsheet({ data, onChange, readOnly }: LazySpreadsheetProps) {
  return (
    <Suspense fallback={<SpreadsheetSkeleton />}>
      <SpreadsheetComponent data={data} onChange={onChange} readOnly={readOnly} />
    </Suspense>
  );
}
