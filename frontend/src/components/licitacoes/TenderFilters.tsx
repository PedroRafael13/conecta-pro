'use client';

/**
 * Componente de Filtros de Editais
 * Formulário avançado de filtros com múltiplas opções
 */

import { Search, Filter, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

interface TenderFiltersProps {
  filters: {
    termo_busca?: string;
    status?: string;
    uf?: string;
    modalidade?: string;
    segmento?: string;
    valor_min?: number;
    valor_max?: number;
  };
  onFilterChange: (filters: any) => void;
  onClearFilters: () => void;
}

const UFS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO'
];

const MODALIDADES = [
  { value: 'pregao_eletronico', label: 'Pregão Eletrônico' },
  { value: 'pregao_presencial', label: 'Pregão Presencial' },
  { value: 'concorrencia', label: 'Concorrência' },
  { value: 'tomada_precos', label: 'Tomada de Preços' },
  { value: 'convite', label: 'Convite' },
  { value: 'concurso', label: 'Concurso' },
  { value: 'leilao', label: 'Leilão' },
  { value: 'credenciamento', label: 'Credenciamento' },
  { value: 'rdc', label: 'RDC' },
  { value: 'dialogo_competitivo', label: 'Diálogo Competitivo' },
  { value: 'dispensa', label: 'Dispensa' },
  { value: 'inexigibilidade', label: 'Inexigibilidade' },
];

const STATUS_OPTIONS = [
  { value: 'aberto', label: 'Aberto' },
  { value: 'em_andamento', label: 'Em Andamento' },
  { value: 'em_analise', label: 'Em Análise' },
  { value: 'participando', label: 'Participando' },
  { value: 'interesse', label: 'Interesse' },
  { value: 'homologado', label: 'Homologado' },
  { value: 'cancelado', label: 'Cancelado' },
  { value: 'deserto', label: 'Deserto' },
  { value: 'fracassado', label: 'Fracassado' },
  { value: 'arquivado', label: 'Arquivado' },
];

const SEGMENTOS = [
  { value: 'limpeza', label: 'Limpeza' },
  { value: 'vigilancia', label: 'Vigilância' },
  { value: 'manutencao', label: 'Manutenção' },
  { value: 'obras', label: 'Obras' },
  { value: 'tecnologia', label: 'Tecnologia' },
  { value: 'consultoria', label: 'Consultoria' },
  { value: 'materiais', label: 'Materiais' },
  { value: 'equipamentos', label: 'Equipamentos' },
  { value: 'servicos_gerais', label: 'Serviços Gerais' },
];

export function TenderFilters({
  filters,
  onFilterChange,
  onClearFilters,
}: TenderFiltersProps) {
  const handleChange = (key: string, value: any) => {
    onFilterChange({ ...filters, [key]: value || undefined });
  };

  const hasActiveFilters = Object.values(filters).some(
    (value) => value !== undefined && value !== ''
  );

  return (
    <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4 space-y-4">
      {/* Busca principal */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <Input
          placeholder="Buscar por número, órgão, objeto..."
          value={filters.termo_busca || ''}
          onChange={(e) => handleChange('termo_busca', e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Filtros em grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Status */}
        <div>
          <Label className="text-xs text-[hsl(var(--muted-foreground))] mb-1.5 block">
            Status
          </Label>
          <select
            value={filters.status || ''}
            onChange={(e) => handleChange('status', e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          >
            <option value="">Todos os Status</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* UF */}
        <div>
          <Label className="text-xs text-[hsl(var(--muted-foreground))] mb-1.5 block">
            UF
          </Label>
          <select
            value={filters.uf || ''}
            onChange={(e) => handleChange('uf', e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          >
            <option value="">Todas UFs</option>
            {UFS.map((uf) => (
              <option key={uf} value={uf}>
                {uf}
              </option>
            ))}
          </select>
        </div>

        {/* Modalidade */}
        <div>
          <Label className="text-xs text-[hsl(var(--muted-foreground))] mb-1.5 block">
            Modalidade
          </Label>
          <select
            value={filters.modalidade || ''}
            onChange={(e) => handleChange('modalidade', e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          >
            <option value="">Todas Modalidades</option>
            {MODALIDADES.map((mod) => (
              <option key={mod.value} value={mod.value}>
                {mod.label}
              </option>
            ))}
          </select>
        </div>

        {/* Segmento */}
        <div>
          <Label className="text-xs text-[hsl(var(--muted-foreground))] mb-1.5 block">
            Segmento
          </Label>
          <select
            value={filters.segmento || ''}
            onChange={(e) => handleChange('segmento', e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          >
            <option value="">Todos Segmentos</option>
            {SEGMENTOS.map((seg) => (
              <option key={seg.value} value={seg.value}>
                {seg.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Filtros de valor */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label className="text-xs text-[hsl(var(--muted-foreground))] mb-1.5 block">
            Valor Mínimo (R$)
          </Label>
          <Input
            type="number"
            placeholder="0,00"
            value={filters.valor_min || ''}
            onChange={(e) =>
              handleChange('valor_min', e.target.value ? parseFloat(e.target.value) : undefined)
            }
            min="0"
            step="0.01"
          />
        </div>
        <div>
          <Label className="text-xs text-[hsl(var(--muted-foreground))] mb-1.5 block">
            Valor Máximo (R$)
          </Label>
          <Input
            type="number"
            placeholder="0,00"
            value={filters.valor_max || ''}
            onChange={(e) =>
              handleChange('valor_max', e.target.value ? parseFloat(e.target.value) : undefined)
            }
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {/* Botão limpar filtros */}
      {hasActiveFilters && (
        <div className="flex justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={onClearFilters}
            className="text-xs"
          >
            <X className="w-3 h-3 mr-1" />
            Limpar Filtros
          </Button>
        </div>
      )}
    </div>
  );
}
