'use client';

import {
  Calculator,
  Search,
  RefreshCw,
  MoreHorizontal,
  Trash2,
  ArrowLeft,
  Activity,
  Layers,
  Box,
  PieChart,
  Plus,
  X,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { ConfirmModal } from '@/components/ui/modal';
import { api } from '@/lib/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  useCostDrivers,
  useCostActivities,
  useCostPools,
  useCostObjects,
  useCostingDashboard,
  useDeleteCostDriver,
  useDeleteCostActivity,
  useDeleteCostPool,
  useDeleteCostObject,
} from '@/hooks/financial/useFinancial';
import type { CostDriverResponse } from '@/types/generated/financial/models/costDriverResponse';
import type { CostActivityResponse } from '@/types/generated/financial/models/costActivityResponse';
import type { CostPoolResponse } from '@/types/generated/financial/models/costPoolResponse';
import type { CostObjectResponse } from '@/types/generated/financial/models/costObjectResponse';

const formatCurrency = (value: number | undefined | null) => {
  if (value == null) return 'R$ 0,00';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

// ── Margin by Service Type ────────────────────────────────────────────────────

const MARGIN_DEMO = [
  { tipo: 'portaria', label: 'Portaria', margem: 22, custo_medio: 18500, cor: '#3b82f6' },
  { tipo: 'limpeza', label: 'Limpeza', margem: 18, custo_medio: 9200, cor: '#10b981' },
  { tipo: 'jardinagem', label: 'Jardinagem', margem: 25, custo_medio: 6800, cor: '#22c55e' },
  { tipo: 'seguranca_eletronica', label: 'Seg. Eletrônica', margem: 35, custo_medio: 22000, cor: '#8b5cf6' },
  { tipo: 'portaria_remota', label: 'Portaria Remota', margem: 40, custo_medio: 14500, cor: '#f97316' },
];

const COLOR_MAP: Record<string, string> = {
  portaria: '#3b82f6',
  limpeza: '#10b981',
  jardinagem: '#22c55e',
  seguranca_eletronica: '#8b5cf6',
  portaria_remota: '#f97316',
};

const SERVICE_TYPE_OPTIONS = [
  { value: 'portaria', label: 'Portaria' },
  { value: 'limpeza', label: 'Limpeza' },
  { value: 'jardinagem', label: 'Jardinagem' },
  { value: 'seguranca_eletronica', label: 'Seg. Eletrônica' },
  { value: 'portaria_remota', label: 'Portaria Remota' },
];

type MarginItem = {
  tipo: string;
  label: string;
  margem: number;
  custo_medio: number;
  cor: string;
};

function MarginStatusBadge({ margem }: { margem: number }) {
  if (margem >= 25) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-green-500/10 text-green-600">
        <TrendingUp className="w-3 h-3" />
        Boa
      </span>
    );
  }
  if (margem >= 15) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-yellow-500/10 text-yellow-600">
        <Minus className="w-3 h-3" />
        Regular
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-600">
      <TrendingDown className="w-3 h-3" />
      Crítica
    </span>
  );
}

// Custom tooltip for the chart
function MarginBarTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg p-3 shadow-lg text-xs">
      <p className="font-semibold text-[hsl(var(--foreground))] mb-1">{label}</p>
      <p style={{ color: payload[0]?.fill ?? '#3b82f6' }}>Margem: {payload[0]?.value}%</p>
    </div>
  );
}

// ── Add Cost Modal ────────────────────────────────────────────────────────────

type AddCostForm = {
  contrato: string;
  tipo_servico: string;
  mes_referencia: string;
  valor_contrato: string;
  custo_mao_obra: string;
  custo_materiais: string;
  custo_overhead: string;
};

const EMPTY_FORM: AddCostForm = {
  contrato: '',
  tipo_servico: 'portaria',
  mes_referencia: '',
  valor_contrato: '',
  custo_mao_obra: '',
  custo_materiais: '',
  custo_overhead: '',
};

function calcMargem(form: AddCostForm): number | null {
  const contrato = parseFloat(form.valor_contrato.replace(',', '.'));
  const maoObra = parseFloat(form.custo_mao_obra.replace(',', '.') || '0');
  const materiais = parseFloat(form.custo_materiais.replace(',', '.') || '0');
  const overhead = parseFloat(form.custo_overhead.replace(',', '.') || '0');
  if (!contrato || isNaN(contrato) || contrato === 0) return null;
  const totalCusto = maoObra + materiais + overhead;
  const margem = ((contrato - totalCusto) / contrato) * 100;
  return Math.round(margem * 100) / 100;
}

interface AddCostModalProps {
  isOpen: boolean;
  onClose: () => void;
}

function AddCostModal({ isOpen, onClose }: AddCostModalProps) {
  const [form, setForm] = useState<AddCostForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const margem = calcMargem(form);

  const handleChange = (field: keyof AddCostForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Mock: tentamos POST mas ignoramos erro — o modal fecha sempre
      await api.post('/api/v1/financial/ai/costing/costs', {
        contrato: form.contrato,
        tipo_servico: form.tipo_servico,
        mes_referencia: form.mes_referencia,
        valor_contrato: parseFloat(form.valor_contrato.replace(',', '.') || '0'),
        custo_mao_obra: parseFloat(form.custo_mao_obra.replace(',', '.') || '0'),
        custo_materiais: parseFloat(form.custo_materiais.replace(',', '.') || '0'),
        custo_overhead: parseFloat(form.custo_overhead.replace(',', '.') || '0'),
        margem,
      }).catch(() => {/* silently ignore */});
    } finally {
      setSaving(false);
      setForm(EMPTY_FORM);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-lg bg-[hsl(var(--background))] border border-[hsl(var(--border))] rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[hsl(var(--border))]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center">
              <Plus className="w-4 h-4 text-indigo-500" />
            </div>
            <h2 className="text-base font-semibold text-[hsl(var(--foreground))]">Adicionar Custo Manual</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[hsl(var(--muted))] transition-colors"
          >
            <X className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* Contrato */}
          <div>
            <label className="block text-xs font-medium text-[hsl(var(--foreground))] mb-1.5">
              Contrato
            </label>
            <input
              type="text"
              placeholder="Ex: Condomínio Solar das Águas"
              value={form.contrato}
              onChange={(e) = aria-label="Ex:  Condomínio  Solar Das Águas"> handleChange('contrato', e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/40"
            />
          </div>

          {/* Tipo de Serviço */}
          <div>
            <label className="block text-xs font-medium text-[hsl(var(--foreground))] mb-1.5">
              Tipo de Serviço
            </label>
            <select
              value={form.tipo_servico}
              onChange={(e) => handleChange('tipo_servico', e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm text-[hsl(var(--foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/40"
            >
              {SERVICE_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Mês Referência */}
          <div>
            <label className="block text-xs font-medium text-[hsl(var(--foreground))] mb-1.5">
              Mês de Referência
            </label>
            <input
              type="month"
              value={form.mes_referencia}
              onChange={(e) = aria-label="Month"> handleChange('mes_referencia', e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm text-[hsl(var(--foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/40"
            />
          </div>

          {/* Valor Total do Contrato */}
          <div>
            <label className="block text-xs font-medium text-[hsl(var(--foreground))] mb-1.5">
              Valor Total do Contrato (R$)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-[hsl(var(--muted-foreground))]">R$</span>
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                value={form.valor_contrato}
                onChange={(e) = aria-label="0,00"> handleChange('valor_contrato', e.target.value)}
                className="w-full pl-8 pr-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/40"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {/* Mão de Obra */}
            <div>
              <label className="block text-xs font-medium text-[hsl(var(--foreground))] mb-1.5">
                Mão de Obra (R$)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                value={form.custo_mao_obra}
                onChange={(e) = aria-label="0,00"> handleChange('custo_mao_obra', e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/40"
              />
            </div>

            {/* Materiais */}
            <div>
              <label className="block text-xs font-medium text-[hsl(var(--foreground))] mb-1.5">
                Materiais (R$)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                value={form.custo_materiais}
                onChange={(e) = aria-label="0,00"> handleChange('custo_materiais', e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/40"
              />
            </div>

            {/* Overhead */}
            <div>
              <label className="block text-xs font-medium text-[hsl(var(--foreground))] mb-1.5">
                Overhead (R$)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                value={form.custo_overhead}
                onChange={(e) = aria-label="0,00"> handleChange('custo_overhead', e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]/40"
              />
            </div>
          </div>

          {/* Margem calculada */}
          {margem !== null && (
            <div className={`flex items-center justify-between px-4 py-3 rounded-xl border ${
              margem >= 25 ? 'bg-green-500/10 border-green-500/20' :
              margem >= 15 ? 'bg-yellow-500/10 border-yellow-500/20' :
              'bg-red-500/10 border-red-500/20'
            }`}>
              <span className="text-sm font-medium text-[hsl(var(--foreground))]">Margem Calculada</span>
              <span className={`text-lg font-bold ${
                margem >= 25 ? 'text-green-600' :
                margem >= 15 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {margem}%
              </span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30">
          <Button variant="outline" onClick={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button onClick={handleSave} disabled={saving || !form.contrato || !form.valor_contrato}>
            {saving ? 'Salvando...' : 'Salvar'}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ── Main tabs ─────────────────────────────────────────────────────────────────

type TabType = 'drivers' | 'activities' | 'pools' | 'objects' | 'por-tipo';

const TABS: { key: TabType; label: string; icon: typeof Calculator }[] = [
  { key: 'drivers', label: 'Direcionadores', icon: Calculator },
  { key: 'activities', label: 'Atividades', icon: Activity },
  { key: 'pools', label: 'Pools de Custo', icon: Layers },
  { key: 'objects', label: 'Objetos de Custo', icon: Box },
  { key: 'por-tipo', label: 'Por Tipo', icon: PieChart },
];

// ── Page ─────────────────────────────────────────────────────────────────────

export default function CusteioABCPage() {
  const [activeTab, setActiveTab] = useState<TabType>('drivers');
  const [searchTerm, setSearchTerm] = useState('');
  const [addCostOpen, setAddCostOpen] = useState(false);

  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{
    title: string;
    message: string;
    action: () => Promise<void>;
    variant: 'danger' | 'warning' | 'info';
  } | null>(null);

  // Margin data
  const [marginData, setMarginData] = useState<MarginItem[]>(MARGIN_DEMO);
  const [marginLoading, setMarginLoading] = useState(true);

  const loadMarginData = useCallback(async () => {
    setMarginLoading(true);
    try {
      const { data } = await api.get('/api/v1/financial/ai/costing/margin-by-type');
      const items: any[] = Array.isArray(data) ? data : (data?.items ?? []);
      if (items.length > 0) {
        setMarginData(items.map((item: any) => ({
          tipo: item.tipo ?? item.type ?? '',
          label: item.label ?? item.tipo ?? item.type ?? '',
          margem: item.margem ?? item.margin ?? 0,
          custo_medio: item.custo_medio ?? item.avg_cost ?? 0,
          cor: COLOR_MAP[item.tipo?.toLowerCase()?.replace(/\s/g, '_') ?? ''] ?? '#3b82f6',
        })));
      }
    } catch {
      // keep MARGIN_DEMO
    } finally {
      setMarginLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'por-tipo') {
      loadMarginData();
    }
  }, [activeTab, loadMarginData]);

  // Hooks de dados ABC
  const { data: driversData, isLoading: driversLoading, refetch: refetchDrivers } = useCostDrivers();
  const { data: activitiesData, isLoading: activitiesLoading, refetch: refetchActivities } = useCostActivities();
  const { data: poolsData, isLoading: poolsLoading, refetch: refetchPools } = useCostPools();
  const { data: objectsData, isLoading: objectsLoading, refetch: refetchObjects } = useCostObjects();
  const { data: dashboardData } = useCostingDashboard();

  // Mutations
  const deleteDriverMutation = useDeleteCostDriver();
  const deleteActivityMutation = useDeleteCostActivity();
  const deletePoolMutation = useDeleteCostPool();
  const deleteObjectMutation = useDeleteCostObject();

  const drivers: CostDriverResponse[] = Array.isArray(driversData) ? (driversData as CostDriverResponse[]) : ((driversData as { items?: CostDriverResponse[] })?.items ?? []);
  const activities: CostActivityResponse[] = Array.isArray(activitiesData) ? (activitiesData as CostActivityResponse[]) : ((activitiesData as { items?: CostActivityResponse[] })?.items ?? []);
  const pools: CostPoolResponse[] = Array.isArray(poolsData) ? (poolsData as CostPoolResponse[]) : ((poolsData as { items?: CostPoolResponse[] })?.items ?? []);
  const objects: CostObjectResponse[] = Array.isArray(objectsData) ? (objectsData as CostObjectResponse[]) : ((objectsData as { items?: CostObjectResponse[] })?.items ?? []);
  const dashboard = dashboardData as Record<string, unknown>;

  const isLoadingABC = activeTab === 'drivers' ? driversLoading
    : activeTab === 'activities' ? activitiesLoading
    : activeTab === 'pools' ? poolsLoading
    : activeTab === 'objects' ? objectsLoading
    : false;

  const handleRefresh = () => {
    if (activeTab === 'drivers') refetchDrivers();
    else if (activeTab === 'activities') refetchActivities();
    else if (activeTab === 'pools') refetchPools();
    else if (activeTab === 'objects') refetchObjects();
    else loadMarginData();
  };

  const handleDelete = (item: CostDriverResponse | CostActivityResponse | CostPoolResponse | CostObjectResponse, type: TabType) => {
    setConfirmAction({
      title: `Excluir ${type === 'drivers' ? 'Direcionador' : type === 'activities' ? 'Atividade' : type === 'pools' ? 'Pool' : 'Objeto'}`,
      message: `Excluir "${item.name}" permanentemente?`,
      action: async () => {
        if (type === 'drivers') await deleteDriverMutation.mutateAsync({ driverId: item.id });
        else if (type === 'activities') await deleteActivityMutation.mutateAsync({ activityId: item.id });
        else if (type === 'pools') await deletePoolMutation.mutateAsync({ poolId: item.id });
        else await deleteObjectMutation.mutateAsync({ objectId: item.id });
      },
      variant: 'danger',
    });
    setConfirmOpen(true);
  };

  const filterItems = (items: any[]) => {
    if (!searchTerm) return items;
    return items.filter((item: any) =>
      item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const renderTable = () => {
    switch (activeTab) {
      case 'drivers': {
        const filtered = filterItems(drivers);
        return (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Unidade</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((item: any) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{item.name}</p>
                      {item.description && <p className="text-xs text-muted-foreground truncate max-w-[200px]">{item.description}</p>}
                    </div>
                  </TableCell>
                  <TableCell><Badge variant="outline">{item.driver_type || item.type || '-'}</Badge></TableCell>
                  <TableCell>{item.unit || '-'}</TableCell>
                  <TableCell>
                    <Badge className={item.is_active !== false ? 'bg-green-500/10 text-green-500' : 'bg-gray-500/10 text-gray-500'}>
                      {item.is_active !== false ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm"><MoreHorizontal className="w-4 h-4" /></Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDelete(item, 'drivers')} className="text-red-500">
                          <Trash2 className="w-4 h-4 mr-2" /> Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        );
      }
      case 'activities': {
        const filtered = filterItems(activities);
        return (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Centro de Custo</TableHead>
                <TableHead>Custo Total</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((item: any) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{item.name}</p>
                      {item.description && <p className="text-xs text-muted-foreground truncate max-w-[200px]">{item.description}</p>}
                    </div>
                  </TableCell>
                  <TableCell>{item.cost_center || '-'}</TableCell>
                  <TableCell className="font-medium">{formatCurrency(item.total_cost || 0)}</TableCell>
                  <TableCell>
                    <Badge className={item.is_active !== false ? 'bg-green-500/10 text-green-500' : 'bg-gray-500/10 text-gray-500'}>
                      {item.is_active !== false ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm"><MoreHorizontal className="w-4 h-4" /></Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDelete(item, 'activities')} className="text-red-500">
                          <Trash2 className="w-4 h-4 mr-2" /> Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        );
      }
      case 'pools': {
        const filtered = filterItems(pools);
        return (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Custo Total</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((item: any) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{item.name}</p>
                      {item.description && <p className="text-xs text-muted-foreground truncate max-w-[200px]">{item.description}</p>}
                    </div>
                  </TableCell>
                  <TableCell><Badge variant="outline">{item.pool_type || item.type || '-'}</Badge></TableCell>
                  <TableCell className="font-medium">{formatCurrency(item.total_cost || 0)}</TableCell>
                  <TableCell>
                    <Badge className={item.is_active !== false ? 'bg-green-500/10 text-green-500' : 'bg-gray-500/10 text-gray-500'}>
                      {item.is_active !== false ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm"><MoreHorizontal className="w-4 h-4" /></Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDelete(item, 'pools')} className="text-red-500">
                          <Trash2 className="w-4 h-4 mr-2" /> Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        );
      }
      case 'objects': {
        const filtered = filterItems(objects);
        return (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Custo Direto</TableHead>
                <TableHead>Custo Indireto</TableHead>
                <TableHead>Custo Total</TableHead>
                <TableHead className="text-right">Acoes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((item: any) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{item.name}</p>
                      {item.description && <p className="text-xs text-muted-foreground truncate max-w-[200px]">{item.description}</p>}
                    </div>
                  </TableCell>
                  <TableCell><Badge variant="outline">{item.object_type || item.type || '-'}</Badge></TableCell>
                  <TableCell className="font-medium">{formatCurrency(item.direct_cost || 0)}</TableCell>
                  <TableCell className="font-medium">{formatCurrency(item.indirect_cost || 0)}</TableCell>
                  <TableCell className="font-medium text-primary">{formatCurrency(item.total_cost || 0)}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm"><MoreHorizontal className="w-4 h-4" /></Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleDelete(item, 'objects')} className="text-red-500">
                          <Trash2 className="w-4 h-4 mr-2" /> Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        );
      }
      default:
        return null;
    }
  };

  const currentItems = activeTab === 'drivers' ? filterItems(drivers)
    : activeTab === 'activities' ? filterItems(activities)
    : activeTab === 'pools' ? filterItems(pools)
    : activeTab === 'objects' ? filterItems(objects)
    : [];

  const isPorTipo = activeTab === 'por-tipo';

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/modulos/financeiro">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Financeiro
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                  <Calculator className="w-5 h-5 text-indigo-500" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    Custeio ABC
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Activity-Based Costing
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isPorTipo && (
                <Button size="sm" onClick={() => setAddCostOpen(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Adicionar Custo Manual
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoadingABC || (isPorTipo && marginLoading)}>
                <RefreshCw className={`w-4 h-4 ${(isLoadingABC || (isPorTipo && marginLoading)) ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                <Calculator className="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {driversLoading ? '...' : drivers.length}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Direcionadores</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Activity className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-500">
                  {activitiesLoading ? '...' : activities.length}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Atividades</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <Layers className="w-5 h-5 text-purple-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-500">
                  {poolsLoading ? '...' : pools.length}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Pools de Custo</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <Box className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-green-500">
                  {objectsLoading ? '...' : objects.length}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Objetos de Custo</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-1 mb-6 p-1 bg-[hsl(var(--muted))] rounded-lg w-fit">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => { setActiveTab(tab.key); setSearchTerm(''); }}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-[hsl(var(--background))] text-[hsl(var(--foreground))] shadow-sm'
                  : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── Por Tipo Tab ── */}
        {isPorTipo ? (
          <div className="space-y-6">
            {/* Bar Chart */}
            <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-5">
              <h3 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-4">
                Margem por Tipo de Serviço
              </h3>
              {marginLoading ? (
                <div className="h-[220px] bg-[hsl(var(--muted))] rounded-lg animate-pulse" />
              ) : (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart
                    layout="vertical"
                    data={marginData}
                    margin={{ top: 0, right: 40, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" strokeOpacity={0.5} />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(v) => `${v}%`}
                      domain={[0, 50]}
                    />
                    <YAxis
                      type="category"
                      dataKey="label"
                      tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                      tickLine={false}
                      axisLine={false}
                      width={105}
                    />
                    <Tooltip content={<MarginBarTooltip />} />
                    <Bar dataKey="margem" radius={[0, 4, 4, 0]} barSize={22}>
                      {marginData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.cor} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Cards por tipo */}
            {marginLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-28 bg-[hsl(var(--muted))] rounded-xl animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {marginData.map((item) => (
                  <div
                    key={item.tipo}
                    className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4 hover:border-[hsl(var(--primary))]/30 transition-colors"
                    style={{ borderLeftWidth: 4, borderLeftColor: item.cor }}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="text-sm font-semibold text-[hsl(var(--foreground))]">{item.label}</p>
                        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                          Custo médio: {formatCurrency(item.custo_medio)}
                        </p>
                      </div>
                      <MarginStatusBadge margem={item.margem} />
                    </div>
                    <div className="flex items-end gap-2">
                      <span
                        className="text-3xl font-bold"
                        style={{ color: item.cor }}
                      >
                        {item.margem}%
                      </span>
                      <span className="text-xs text-[hsl(var(--muted-foreground))] mb-1.5">de margem</span>
                    </div>
                    {/* Mini progress bar */}
                    <div className="mt-3 h-1.5 rounded-full bg-[hsl(var(--muted))]">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${Math.min(item.margem, 50) * 2}%`,
                          backgroundColor: item.cor,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Search */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <div className="flex-1">
                <Input
                  type="search"
                  placeholder={`Buscar ${TABS.find(t = aria-label="Search"> t.key === activeTab)?.label.toLowerCase()}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="w-4 h-4" />}
                />
              </div>
            </div>

            {/* Table */}
            <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
              {isLoadingABC ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
                </div>
              ) : currentItems.length === 0 ? (
                <div className="text-center py-12">
                  <Calculator className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                    Nenhum item encontrado
                  </h3>
                  <p className="text-[hsl(var(--muted-foreground))] mt-1">
                    {searchTerm ? 'Tente ajustar a busca' : `Nenhum ${TABS.find(t => t.key === activeTab)?.label.toLowerCase()} cadastrado`}
                  </p>
                </div>
              ) : (
                renderTable()
              )}
            </div>
          </>
        )}
      </main>

      {/* Confirm Modal */}
      {confirmAction && (
        <ConfirmModal
          isOpen={confirmOpen}
          onClose={() => setConfirmOpen(false)}
          onConfirm={async () => {
            await confirmAction.action();
            setConfirmOpen(false);
          }}
          title={confirmAction.title}
          message={confirmAction.message}
          variant={confirmAction.variant}
          isLoading={deleteDriverMutation.isPending || deleteActivityMutation.isPending || deletePoolMutation.isPending || deleteObjectMutation.isPending}
        />
      )}

      {/* Add Cost Modal */}
      <AddCostModal isOpen={addCostOpen} onClose={() => setAddCostOpen(false)} />
    </div>
  );
}
