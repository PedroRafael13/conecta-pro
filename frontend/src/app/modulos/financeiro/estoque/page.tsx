'use client';

import { Package, Search, RefreshCw, Plus, AlertCircle, Warehouse, ArrowLeft, TrendingDown } from 'lucide-react';
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { customInstance } from '@/lib/api-client';
import { cn } from '@/lib/utils';

type TabType = 'items' | 'warehouses' | 'movements';

interface StockItem {
  id: string;
  product_id: string;
  warehouse_id: string;
  name?: string | null;
  code?: string | null;
  batch_number?: string | null;
  status?: string;
  quantity_on_hand?: number;
  quantity_available?: number;
  unit_cost?: number;
  total_cost?: number;
  expiry_date?: string | null;
  full_location?: string;
  is_low_stock?: boolean;
  is_expired?: boolean;
}

interface WarehouseItem {
  id: string;
  name?: string;
  code?: string;
  status?: string;
  capacity?: number;
  current_occupancy?: number;
  address?: string;
}

interface MovementItem {
  id: string;
  movement_type?: string;
  quantity?: number;
  created_at?: string;
  reference_document?: string;
  notes?: string;
}

const formatCurrency = (v?: number | null) =>
  (v ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

const getItemDisplayName = (item: StockItem) =>
  item.name ?? item.code ?? `${item.product_id?.slice(0, 8)}...`;

const getStatusBadge = (status?: string, isLow?: boolean, isExpired?: boolean) => {
  if (isExpired) return <Badge variant="destructive">Vencido</Badge>;
  if (isLow) return <Badge className="bg-orange-100 text-orange-800">Baixo</Badge>;
  const s = (status || '').toLowerCase();
  if (s === 'ativo' || s === 'active') return <Badge className="bg-green-100 text-green-800">Ativo</Badge>;
  if (s === 'inativo' || s === 'inactive') return <Badge variant="secondary">Inativo</Badge>;
  return <Badge variant="outline">{status || 'N/D'}</Badge>;
};

export default function EstoquePage() {
  const [activeTab, setActiveTab] = useState<TabType>('items');
  const [search, setSearch] = useState('');

  const {
    data: itemsRaw,
    isLoading: loadingItems,
    isError: errorItems,
    refetch: refetchItems,
  } = useQuery<StockItem[]>({
    queryKey: ['inventory-items'],
    queryFn: () =>
      customInstance<StockItem[]>({
        url: '/api/v1/financial/inventory/items',
        params: { limit: 200 },
      }),
  });

  const {
    data: warehousesRaw,
    isLoading: loadingWarehouses,
    refetch: refetchWarehouses,
  } = useQuery<WarehouseItem[]>({
    queryKey: ['inventory-warehouses'],
    queryFn: () =>
      customInstance<WarehouseItem[]>({ url: '/api/v1/financial/inventory/warehouses', params: { limit: 100 } }),
    retry: 1,
  });

  const {
    data: movementsRaw,
    isLoading: loadingMovements,
    refetch: refetchMovements,
  } = useQuery<MovementItem[]>({
    queryKey: ['inventory-movements'],
    queryFn: () =>
      customInstance<MovementItem[]>({
        url: '/api/v1/financial/inventory/stock-movements',
        params: { limit: 100 },
      }),
    enabled: activeTab === 'movements',
    retry: 1,
  });

  const items = Array.isArray(itemsRaw) ? itemsRaw : (itemsRaw as { items?: StockItem[] })?.items ?? [];
  const warehouses = Array.isArray(warehousesRaw) ? warehousesRaw : [];
  const movements = Array.isArray(movementsRaw) ? movementsRaw : [];

  const filteredItems = useMemo(() => {
    if (!search) return items;
    const q = search.toLowerCase();
    return items.filter(
      (i) =>
        getItemDisplayName(i).toLowerCase().includes(q) ||
        (i.code ?? '').toLowerCase().includes(q) ||
        (i.batch_number ?? '').toLowerCase().includes(q),
    );
  }, [items, search]);

  const kpis = useMemo(
    () => ({
      total: items.length,
      totalValue: items.reduce((acc, i) => acc + (i.total_cost ?? 0), 0),
      lowStock: items.filter((i) => i.is_low_stock).length,
      armazens: warehouses.length,
    }),
    [items, warehouses],
  );

  const isLoading =
    activeTab === 'items' ? loadingItems : activeTab === 'warehouses' ? loadingWarehouses : loadingMovements;

  const handleRefresh = () => {
    if (activeTab === 'items') refetchItems();
    else if (activeTab === 'warehouses') refetchWarehouses();
    else refetchMovements();
  };

  const tabs: { key: TabType; label: string }[] = [
    { key: 'items', label: 'Itens' },
    { key: 'warehouses', label: 'Armazéns' },
    { key: 'movements', label: 'Movimentações' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/modulos/financeiro">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Package className="h-6 w-6 text-green-600" />
              Estoque
            </h1>
            <p className="text-sm text-muted-foreground">Controle de inventário e movimentações</p>
          </div>
        </div>
        <Button variant="outline">
          <Plus className="h-4 w-4 mr-2" />
          Nova Entrada
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total de Itens</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">{kpis.total}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Valor Total</p>
            <p className="text-2xl font-bold text-green-600 mt-1">{formatCurrency(kpis.totalValue)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Abaixo do Mínimo</p>
              {kpis.lowStock > 0 && <TrendingDown className="h-4 w-4 text-orange-500" />}
            </div>
            <p className={cn('text-2xl font-bold mt-1', kpis.lowStock > 0 ? 'text-orange-600' : 'text-gray-600')}>
              {kpis.lowStock}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Armazéns</p>
              <Warehouse className="h-4 w-4 text-purple-500" />
            </div>
            <p className="text-2xl font-bold text-purple-600 mt-1">{kpis.armazens}</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs + Search */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex gap-2">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={cn(
                'px-4 py-1.5 rounded-full text-sm font-medium transition-colors',
                activeTab === t.key
                  ? 'bg-green-600 text-white'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80',
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          {activeTab === 'items' && (
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nome, código..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
          )}
          <Button variant="outline" size="icon" onClick={handleRefresh}>
            <RefreshCw className={cn('h-4 w-4', isLoading && 'animate-spin')} />
          </Button>
        </div>
      </div>

      {/* Conteúdo das Tabs */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-40 text-muted-foreground">
              <RefreshCw className="h-5 w-5 animate-spin mr-2" />
              Carregando...
            </div>
          ) : errorItems && activeTab === 'items' ? (
            <div className="flex items-center justify-center h-40 text-destructive gap-2">
              <AlertCircle className="h-5 w-5" />
              Erro ao carregar itens de estoque
            </div>
          ) : activeTab === 'items' ? (
            filteredItems.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                <Package className="h-8 w-8 mb-2 opacity-30" />
                <p>Nenhum item encontrado</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/30">
                      <th className="text-left px-4 py-3 font-medium">Item</th>
                      <th className="text-left px-4 py-3 font-medium hidden md:table-cell">Código</th>
                      <th className="text-left px-4 py-3 font-medium">Qtd. Disponível</th>
                      <th className="text-left px-4 py-3 font-medium hidden md:table-cell">Custo Unit.</th>
                      <th className="text-left px-4 py-3 font-medium hidden lg:table-cell">Valor Total</th>
                      <th className="text-left px-4 py-3 font-medium">Status</th>
                      <th className="text-left px-4 py-3 font-medium hidden lg:table-cell">Localização</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredItems.map((item) => (
                      <tr key={item.id} className="border-b hover:bg-muted/20 transition-colors">
                        <td className="px-4 py-3 font-medium">
                          {getItemDisplayName(item)}
                          {item.batch_number && (
                            <div className="text-xs text-muted-foreground">Lote: {item.batch_number}</div>
                          )}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground font-mono text-xs hidden md:table-cell">
                          {item.code ?? '-'}
                        </td>
                        <td className="px-4 py-3">
                          <span className={cn('font-medium', (item.quantity_available ?? 0) === 0 && 'text-red-600')}>
                            {item.quantity_available ?? 0}
                          </span>
                          {item.quantity_on_hand !== item.quantity_available && (
                            <span className="text-xs text-muted-foreground ml-1">
                              / {item.quantity_on_hand ?? 0} total
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 hidden md:table-cell">{formatCurrency(item.unit_cost)}</td>
                        <td className="px-4 py-3 font-medium hidden lg:table-cell">
                          {formatCurrency(item.total_cost)}
                        </td>
                        <td className="px-4 py-3">
                          {getStatusBadge(item.status, item.is_low_stock, item.is_expired)}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground text-xs hidden lg:table-cell">
                          {item.full_location || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : activeTab === 'warehouses' ? (
            warehouses.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                <Warehouse className="h-8 w-8 mb-2 opacity-30" />
                <p>Nenhum armazém cadastrado</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/30">
                      <th className="text-left px-4 py-3 font-medium">Armazém</th>
                      <th className="text-left px-4 py-3 font-medium">Código</th>
                      <th className="text-left px-4 py-3 font-medium">Status</th>
                      <th className="text-left px-4 py-3 font-medium hidden md:table-cell">Endereço</th>
                    </tr>
                  </thead>
                  <tbody>
                    {warehouses.map((wh) => (
                      <tr key={wh.id} className="border-b hover:bg-muted/20 transition-colors">
                        <td className="px-4 py-3 font-medium">{wh.name ?? wh.id.slice(0, 8)}</td>
                        <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{wh.code ?? '-'}</td>
                        <td className="px-4 py-3">
                          <Badge variant={wh.status === 'ativo' ? 'default' : 'secondary'}>
                            {wh.status ?? 'N/D'}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">
                          {wh.address ?? '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : movements.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
              <Package className="h-8 w-8 mb-2 opacity-30" />
              <p>Nenhuma movimentação registrada</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/30">
                    <th className="text-left px-4 py-3 font-medium">Tipo</th>
                    <th className="text-left px-4 py-3 font-medium">Quantidade</th>
                    <th className="text-left px-4 py-3 font-medium hidden md:table-cell">Documento</th>
                    <th className="text-left px-4 py-3 font-medium hidden md:table-cell">Data</th>
                    <th className="text-left px-4 py-3 font-medium hidden lg:table-cell">Notas</th>
                  </tr>
                </thead>
                <tbody>
                  {movements.map((mv) => (
                    <tr key={mv.id} className="border-b hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3">
                        <Badge variant="outline">{mv.movement_type ?? 'N/D'}</Badge>
                      </td>
                      <td className="px-4 py-3 font-medium">{mv.quantity ?? 0}</td>
                      <td className="px-4 py-3 font-mono text-xs text-muted-foreground hidden md:table-cell">
                        {mv.reference_document ?? '-'}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">
                        {mv.created_at ? new Date(mv.created_at).toLocaleDateString('pt-BR') : '-'}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground hidden lg:table-cell">
                        {mv.notes ?? '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
