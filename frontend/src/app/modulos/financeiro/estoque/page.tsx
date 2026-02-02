'use client';

import { Package, Search, RefreshCw, Plus, MoreHorizontal, Eye, AlertCircle, ArrowUpDown, ArrowLeft, Warehouse, ArrowDownCircle, ArrowUpCircle } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
;
import {
  useInventoryItems,
  useWarehouses,
  useStockBalance,
  useInventoryDashboard,
  useCreateStockMovement,
} from '@/hooks/financial/useFinancial';
import { InventoryFormModal } from '@/components/financeiro/inventory-form-modal';

type TabType = 'items' | 'warehouses' | 'movements';

const formatCurrency = (value: number | undefined | null) => {
  if (value == null) return 'R$ 0,00';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatDate = (date: string | undefined | null) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('pt-BR');
};

export default function EstoquePage() {
  const [activeTab, setActiveTab] = useState<TabType>('items');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFormModal, setShowFormModal] = useState(false);

  const { data: items = [], isLoading: loadingItems, refetch: refetchItems } = useInventoryItems();
  const { data: warehouses = [], isLoading: loadingWarehouses, refetch: refetchWarehouses } = useWarehouses();
  const { data: stockBalance = [], isLoading: loadingBalance, refetch: refetchBalance } = useStockBalance();
  const { data: dashboard, isLoading: loadingDashboard } = useInventoryDashboard();
  const createMovement = useCreateStockMovement();

  const isLoading =
    activeTab === 'items' ? loadingItems :
    activeTab === 'warehouses' ? loadingWarehouses :
    loadingBalance;

  const handleRefresh = () => {
    if (activeTab === 'items') refetchItems();
    else if (activeTab === 'warehouses') refetchWarehouses();
    else refetchBalance();
  };

  const handleFormSubmit = async (data: any) => {
    try {
      await createMovement.mutateAsync({ data });
      setShowFormModal(false);
      // refetch() removido - mutation já invalida queries automaticamente
    } catch (error) {
      console.error('Erro ao registrar movimentacao:', error);
    }
  };

  const filteredItems = (Array.isArray(items) ? items : []).filter((item: any) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      item.name?.toLowerCase().includes(term) ||
      item.code?.toLowerCase().includes(term) ||
      item.category?.toLowerCase().includes(term)
    );
  });

  const filteredWarehouses = (Array.isArray(warehouses) ? warehouses : []).filter((wh: any) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      wh.name?.toLowerCase().includes(term) ||
      wh.location?.toLowerCase().includes(term)
    );
  });

  const filteredMovements = (Array.isArray(stockBalance) ? stockBalance : []).filter((mov: any) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      mov.item_name?.toLowerCase().includes(term) ||
      mov.warehouse_name?.toLowerCase().includes(term)
    );
  });

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
                <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <Package className="w-5 h-5 text-purple-500" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    Estoque
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Controle de materiais e movimentacoes
                  </p>
                </div>
              </div>
            </div>
            <Button variant="primary" size="sm" onClick={() => setShowFormModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Nova Movimentacao
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                <Package className="w-5 h-5 text-purple-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {dashboard?.total_items ?? 0}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Total Itens</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <ArrowUpDown className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <p className="text-xl font-bold text-green-500 truncate">
                  {formatCurrency(dashboard?.total_value)}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Valor Total</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-red-500">
                  {dashboard?.below_minimum ?? 0}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Abaixo do Minimo</p>
              </div>
            </div>
          </div>

          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                <Warehouse className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {dashboard?.total_warehouses ?? 0}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Armazens</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-1 mb-6 bg-[hsl(var(--muted))] rounded-lg p-1 w-fit">
          <button
            onClick={() => setActiveTab('items')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'items'
                ? 'bg-[hsl(var(--card))] text-[hsl(var(--foreground))] shadow-sm'
                : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
            }`}
          >
            Itens
          </button>
          <button
            onClick={() => setActiveTab('warehouses')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'warehouses'
                ? 'bg-[hsl(var(--card))] text-[hsl(var(--foreground))] shadow-sm'
                : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
            }`}
          >
            Armazens
          </button>
          <button
            onClick={() => setActiveTab('movements')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'movements'
                ? 'bg-[hsl(var(--card))] text-[hsl(var(--foreground))] shadow-sm'
                : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
            }`}
          >
            Movimentacoes
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <Input
              type="search"
              placeholder="Buscar..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              icon={<Search className="w-4 h-4" />}
            />
          </div>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-pulse-slow text-[hsl(var(--primary))]">
              <Package className="w-8 h-8" />
            </div>
          </div>
        )}

        {/* Items Table */}
        {!isLoading && activeTab === 'items' && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Codigo</TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Qtd Estoque</TableHead>
                  <TableHead>Qtd Minima</TableHead>
                  <TableHead>Unidade</TableHead>
                  <TableHead className="text-right">Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredItems.map((item: any) => {
                  const belowMinimum = item.stock_quantity != null && item.min_quantity != null && item.stock_quantity < item.min_quantity;
                  return (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.code || item.id?.slice(0, 8)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {item.name || '-'}
                          {belowMinimum && (
                            <AlertCircle className="w-4 h-4 text-red-500" title="Abaixo do minimo" />
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{item.category || '-'}</TableCell>
                      <TableCell>
                        <span className={belowMinimum ? 'text-red-500 font-medium' : ''}>
                          {item.stock_quantity ?? 0}
                        </span>
                      </TableCell>
                      <TableCell>{item.min_quantity ?? 0}</TableCell>
                      <TableCell>{item.unit || '-'}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>
                              <Eye className="w-4 h-4 mr-2" />
                              Visualizar
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>

            {filteredItems.length === 0 && (
              <div className="text-center py-12">
                <Package className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhum item encontrado
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1">
                  {searchTerm ? 'Tente ajustar os filtros de busca' : 'Nenhum item cadastrado no estoque'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Warehouses Table */}
        {!isLoading && activeTab === 'warehouses' && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Localizacao</TableHead>
                  <TableHead>Capacidade</TableHead>
                  <TableHead>Utilizacao</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredWarehouses.map((wh: any) => {
                  const utilization = wh.capacity && wh.used_capacity
                    ? Math.round((wh.used_capacity / wh.capacity) * 100)
                    : 0;
                  return (
                    <TableRow key={wh.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          <Warehouse className="w-4 h-4 text-blue-500" />
                          {wh.name || '-'}
                        </div>
                      </TableCell>
                      <TableCell>{wh.location || '-'}</TableCell>
                      <TableCell>{wh.capacity ?? '-'}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-[hsl(var(--muted))] rounded-full overflow-hidden max-w-[100px]">
                            <div
                              className={`h-full rounded-full ${
                                utilization > 90 ? 'bg-red-500' :
                                utilization > 70 ? 'bg-yellow-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${Math.min(utilization, 100)}%` }}
                            />
                          </div>
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">
                            {utilization}%
                          </span>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>

            {filteredWarehouses.length === 0 && (
              <div className="text-center py-12">
                <Warehouse className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhum armazem encontrado
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1">
                  {searchTerm ? 'Tente ajustar os filtros de busca' : 'Nenhum armazem cadastrado'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Movements Table */}
        {!isLoading && activeTab === 'movements' && (
          <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Data</TableHead>
                  <TableHead>Item</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Quantidade</TableHead>
                  <TableHead>Armazem</TableHead>
                  <TableHead>Responsavel</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMovements.map((mov: any, index: number) => (
                  <TableRow key={mov.id || index}>
                    <TableCell>{formatDate(mov.created_at || mov.date)}</TableCell>
                    <TableCell className="font-medium">{mov.item_name || '-'}</TableCell>
                    <TableCell>
                      {mov.movement_type === 'entry' || mov.type === 'entry' ? (
                        <Badge className="bg-green-500/10 text-green-500 border-green-500/20">
                          <ArrowDownCircle className="w-3 h-3 mr-1" />
                          Entrada
                        </Badge>
                      ) : mov.movement_type === 'exit' || mov.type === 'exit' ? (
                        <Badge className="bg-red-500/10 text-red-500 border-red-500/20">
                          <ArrowUpCircle className="w-3 h-3 mr-1" />
                          Saida
                        </Badge>
                      ) : (
                        <Badge className="bg-blue-500/10 text-blue-500 border-blue-500/20">
                          <ArrowUpDown className="w-3 h-3 mr-1" />
                          Transferencia
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{mov.quantity ?? 0}</TableCell>
                    <TableCell>{mov.warehouse_name || '-'}</TableCell>
                    <TableCell>{mov.responsible || mov.user_name || '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {filteredMovements.length === 0 && (
              <div className="text-center py-12">
                <ArrowUpDown className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhuma movimentacao encontrada
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1 mb-4">
                  {searchTerm ? 'Tente ajustar os filtros de busca' : 'Registre a primeira movimentacao de estoque'}
                </p>
                {!searchTerm && (
                  <Button variant="primary" onClick={() => setShowFormModal(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Nova Movimentacao
                  </Button>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Modals */}
      <InventoryFormModal
        isOpen={showFormModal}
        onClose={() => setShowFormModal(false)}
        onSubmit={handleFormSubmit}
        isLoading={createMovement.isPending}
      />
    </div>
  );
}
