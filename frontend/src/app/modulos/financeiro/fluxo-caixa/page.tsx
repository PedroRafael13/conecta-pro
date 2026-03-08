'use client';

import { Activity, Search, RefreshCw, Plus, TrendingUp, TrendingDown, DollarSign, AlertCircle, ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useCashflowEntries, useCashflowDashboard, useCreateCashflowEntry } from '@/hooks/financial/useFinancial';
import type { CashFlowEntryResponse } from '@/types/generated/financial/models/cashFlowEntryResponse';
import { CashflowFormModal } from '@/components/financeiro/cashflow-form-modal';
import type { CashFlowEntryCreate } from '@/types/generated/financial/models/cashFlowEntryCreate';
import { cn, formatCurrency, formatDate } from '@/lib/utils';

export default function FluxoCaixaPage() {
  const [search, setSearch] = useState('');
  const [entryType, setEntryType] = useState<string | undefined>(undefined);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [showFormModal, setShowFormModal] = useState(false);

  // Hooks de dados
  const {
    data: entriesData,
    isLoading,
    isError,
    error,
    refetch,
  } = useCashflowEntries({
    condominio_id: '',
    skip: (page - 1) * pageSize,
    limit: pageSize,
  });

  const { data: dashboardRaw, refetch: refetchDashboard } = useCashflowDashboard({ condominio_id: '' });
  const dashboard = dashboardRaw as any;
  const createEntry = useCreateCashflowEntry();

  const entries: any[] = (entriesData as any)?.items ?? [];
  const total = (entriesData as any)?.total ?? entries.length;
  const totalPages = Math.ceil(total / pageSize);

  // Debounce search
  const lastSearchRef = useRef<string | undefined>(undefined);
  useEffect(() => {
    const newSearch = search || undefined;
    if (lastSearchRef.current === newSearch) return;

    const timer = setTimeout(() => {
      lastSearchRef.current = newSearch;
      setPage(1);
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  const handleCreateEntry = async (data: any) => {
    try {
      await createEntry.mutateAsync({ data });
      setShowFormModal(false);
      // refetch() removido - mutation já invalida queries automaticamente
    } catch (err) {
      console.error('Erro ao criar lancamento:', err);
      throw err;
    }
  };

  const getEntryTypeColor = (type: string) => {
    switch (type) {
      case 'income':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'expense':
        return 'bg-red-500/10 text-red-500 border-red-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  const getEntryTypeLabel = (type: string) => {
    switch (type) {
      case 'income':
        return 'Entrada';
      case 'expense':
        return 'Saida';
      default:
        return type;
    }
  };

  // Filtrar localmente por search se necessario
  const filteredEntries = search
    ? entries.filter((entry: any) =>
        entry.description?.toLowerCase().includes(search.toLowerCase()) ||
        entry.memo?.toLowerCase().includes(search.toLowerCase())
      )
    : entries;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link href="/modulos/financeiro">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Financeiro
            </Button>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                Fluxo de Caixa
              </h1>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {total} lancamentos registrados
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => { refetch(); refetchDashboard(); }}
            disabled={isLoading}
          >
            <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          </Button>
          <Button variant="primary" size="sm" onClick={() => setShowFormModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Novo Lancamento
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {isLoading ? '...' : formatCurrency(Number(dashboard?.summary?.total_inflows ?? 0))}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Entradas</p>
            </div>
          </div>
        </div>

        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {isLoading ? '...' : formatCurrency(Number(dashboard?.summary?.total_outflows ?? 0))}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Saidas</p>
            </div>
          </div>
        </div>

        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {isLoading ? '...' : formatCurrency(Number(dashboard?.summary?.closing_balance ?? 0))}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Saldo Atual</p>
            </div>
          </div>
        </div>

        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {isLoading ? '...' : formatCurrency(Number(dashboard?.upcoming_receivables ?? 0) - Number(dashboard?.upcoming_payables ?? 0))}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Projecao 30d</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            type="search"
            placeholder="Buscar por descricao ou categoria..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            icon={<Search className="w-4 h-4" />}
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={entryType === undefined ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => { setEntryType(undefined); setPage(1); }}
          >
            Todos
          </Button>
          <Button
            variant={entryType === 'income' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => { setEntryType('income'); setPage(1); }}
          >
            Entradas
          </Button>
          <Button
            variant={entryType === 'expense' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => { setEntryType('expense'); setPage(1); }}
          >
            Saidas
          </Button>
        </div>
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/30">
          <AlertCircle className="w-5 h-5 text-[hsl(var(--destructive))]" />
          <div>
            <p className="font-medium text-[hsl(var(--destructive))]">Erro ao carregar lancamentos</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {(error as Error)?.message || 'Tente novamente em alguns instantes'}
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => refetch()} className="ml-auto">
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="divide-y divide-[hsl(var(--border))]">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="p-4 flex items-center gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-48 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                    <div className="h-3 w-32 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                  </div>
                  <div className="h-6 w-20 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                  <div className="h-4 w-24 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[hsl(var(--border))]">
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Data
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Descricao
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Tipo
                    </th>
                    <th className="text-right p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Valor
                    </th>
                    <th className="text-right p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Saldo Acumulado
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                      Categoria
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[hsl(var(--border))]">
                  {filteredEntries.map((entry: any) => (
                    <tr
                      key={entry.id}
                      className="hover:bg-[hsl(var(--secondary))]/50 transition-colors"
                    >
                      <td className="p-4">
                        <span className="text-sm text-[hsl(var(--foreground))]">
                          {entry.entry_date ? formatDate(entry.entry_date) : '-'}
                        </span>
                      </td>
                      <td className="p-4">
                        <p className="font-medium text-[hsl(var(--foreground))]">
                          {entry.description || '-'}
                        </p>
                      </td>
                      <td className="p-4">
                        <span
                          className={cn(
                            'inline-flex px-2 py-1 text-xs font-medium rounded-full border',
                            getEntryTypeColor(entry.entry_type)
                          )}
                        >
                          {getEntryTypeLabel(entry.entry_type)}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <span
                          className={cn(
                            'font-mono text-sm font-medium',
                            entry.entry_type === 'income'
                              ? 'text-green-500'
                              : 'text-red-500'
                          )}
                        >
                          {entry.entry_type === 'income' ? '+' : '-'}
                          {formatCurrency(Math.abs(parseFloat(entry.expected_amount || entry.amount || 0)))}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <span className="font-mono text-sm text-[hsl(var(--foreground))]">
                          {formatCurrency(parseFloat(entry.realized_amount ?? entry.balance ?? 0))}
                        </span>
                      </td>
                      <td className="p-4 hidden md:table-cell">
                        <span className="text-sm text-[hsl(var(--muted-foreground))]">
                          {entry.memo || entry.category || '-'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !isError && filteredEntries.length === 0 && (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
              <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                Nenhum lancamento encontrado
              </h3>
              <p className="text-[hsl(var(--muted-foreground))] mt-1">
                {search || entryType
                  ? 'Tente ajustar os filtros de busca'
                  : 'Comece adicionando seu primeiro lancamento'}
              </p>
              {!search && !entryType && (
                <Button className="mt-4" onClick={() => setShowFormModal(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Novo Lancamento
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Mostrando {(page - 1) * pageSize + 1} a{' '}
            {Math.min(page * pageSize, total)} de {total} lancamentos
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page - 1)}
              disabled={page <= 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-sm text-[hsl(var(--foreground))]">
              Pagina {page} de {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Modal */}
      <CashflowFormModal
        isOpen={showFormModal}
        onClose={() => setShowFormModal(false)}
        onSubmit={handleCreateEntry}
        isLoading={createEntry.isPending}
      />
    </div>
  );
}
