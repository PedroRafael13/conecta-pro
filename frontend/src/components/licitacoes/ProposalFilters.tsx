'use client';

import { Filter, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { statusOptions, type ProposalStatus } from './ProposalStatusBadge';

export interface ProposalFiltersState {
  status?: ProposalStatus;
  tender_id?: string;
  data_inicio?: string;
  data_fim?: string;
  valor_min?: number;
  valor_max?: number;
}

interface ProposalFiltersProps {
  filters: ProposalFiltersState;
  onFiltersChange: (filters: ProposalFiltersState) => void;
  onClearFilters: () => void;
}

export function ProposalFilters({
  filters,
  onFiltersChange,
  onClearFilters,
}: ProposalFiltersProps) {
  const activeFiltersCount = Object.keys(filters).filter(
    (key) => filters[key as keyof ProposalFiltersState] !== undefined
  ).length;

  const handleFilterChange = (key: keyof ProposalFiltersState, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined,
    });
  };

  return (
    <Card className="p-4">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            <h4 className="font-semibold">Filtros</h4>
            {activeFiltersCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {activeFiltersCount} ativo{activeFiltersCount > 1 ? 's' : ''}
              </Badge>
            )}
          </div>
          {activeFiltersCount > 0 && (
            <Button variant="ghost" size="sm" onClick={onClearFilters}>
              <X className="mr-1 h-3 w-3" />
              Limpar
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {/* Status */}
          <div className="space-y-2">
            <Label htmlFor="status-filter">Status</Label>
            <select
              id="status-filter"
              value={filters.status || ''}
              onChange={(e) =>
                handleFilterChange('status', e.target.value as ProposalStatus)
              }
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="">Todos os status</option>
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Data Início */}
          <div className="space-y-2">
            <Label htmlFor="data-inicio-filter">Data Início</Label>
            <Input
              id="data-inicio-filter"
              type="date"
              value={filters.data_inicio || ''}
              onChange={(e) = aria-label="Date"> handleFilterChange('data_inicio', e.target.value)}
            />
          </div>

          {/* Data Fim */}
          <div className="space-y-2">
            <Label htmlFor="data-fim-filter">Data Fim</Label>
            <Input
              id="data-fim-filter"
              type="date"
              value={filters.data_fim || ''}
              onChange={(e) = aria-label="Date"> handleFilterChange('data_fim', e.target.value)}
            />
          </div>

          {/* Valor Mínimo */}
          <div className="space-y-2">
            <Label htmlFor="valor-min-filter">Valor Mínimo (R$)</Label>
            <Input
              id="valor-min-filter"
              type="number"
              step="0.01"
              placeholder="0.00"
              value={filters.valor_min || ''}
              onChange={(e) = aria-label="0.00">
                handleFilterChange(
                  'valor_min',
                  e.target.value ? parseFloat(e.target.value) : undefined
                )
              }
            />
          </div>

          {/* Valor Máximo */}
          <div className="space-y-2">
            <Label htmlFor="valor-max-filter">Valor Máximo (R$)</Label>
            <Input
              id="valor-max-filter"
              type="number"
              step="0.01"
              placeholder="0.00"
              value={filters.valor_max || ''}
              onChange={(e) = aria-label="0.00">
                handleFilterChange(
                  'valor_max',
                  e.target.value ? parseFloat(e.target.value) : undefined
                )
              }
            />
          </div>
        </div>
      </div>
    </Card>
  );
}
