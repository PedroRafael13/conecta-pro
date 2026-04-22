'use client';
import { useTaxasVigentes } from '@/hooks/crm/useEnrichment';

function formatTaxa(v: number | null | undefined): string {
  if (v == null) return '—';
  return `${Number(v).toFixed(2)}%`;
}

export function TaxasWidget() {
  const { data, isLoading, isError } = useTaxasVigentes();

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border p-4 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-28 mb-3" />
        <div className="flex gap-6">
          <div className="h-8 bg-gray-200 rounded w-20" />
          <div className="h-8 bg-gray-200 rounded w-20" />
          <div className="h-8 bg-gray-200 rounded w-20" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="bg-white rounded-lg border p-4 text-sm text-gray-400">
        Taxas indisponíveis no momento
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Taxas do dia</h3>
        {data.cache_hit && (
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded" title="Dados em cache Redis">
            cached
          </span>
        )}
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="text-xs text-gray-500 mb-0.5">Selic</div>
          <div className="text-xl font-bold text-[#1E3A5F]">{formatTaxa(data.selic)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500 mb-0.5">CDI</div>
          <div className="text-xl font-bold text-[#1E3A5F]">{formatTaxa(data.cdi)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500 mb-0.5">IPCA</div>
          <div className="text-xl font-bold text-[#1E3A5F]">{formatTaxa(data.ipca)}</div>
        </div>
      </div>
    </div>
  );
}
