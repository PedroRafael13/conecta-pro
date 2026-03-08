'use client';

import { Calculator, Search, RefreshCw, Plus, MoreHorizontal, Edit, Trash2, ArrowLeft, DollarSign, Activity, Layers, Box } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { ConfirmModal } from '@/components/ui/modal';
import {
  useCostDrivers,
  useCostActivities,
  useCostPools,
  useCostObjects,
  useCostingDashboard,
  useCreateCostDriver,
  useCreateCostActivity,
  useCreateCostPool,
  useCreateCostObject,
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

type TabType = 'drivers' | 'activities' | 'pools' | 'objects';

const TABS: { key: TabType; label: string; icon: typeof Calculator }[] = [
  { key: 'drivers', label: 'Direcionadores', icon: Calculator },
  { key: 'activities', label: 'Atividades', icon: Activity },
  { key: 'pools', label: 'Pools de Custo', icon: Layers },
  { key: 'objects', label: 'Objetos de Custo', icon: Box },
];

export default function CusteioABCPage() {
  const [activeTab, setActiveTab] = useState<TabType>('drivers');
  const [searchTerm, setSearchTerm] = useState('');

  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{
    title: string;
    message: string;
    action: () => Promise<void>;
    variant: 'danger' | 'warning' | 'info';
  } | null>(null);

  // Hooks de dados
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

  const isLoading = activeTab === 'drivers' ? driversLoading
    : activeTab === 'activities' ? activitiesLoading
    : activeTab === 'pools' ? poolsLoading
    : objectsLoading;

  const handleRefresh = () => {
    if (activeTab === 'drivers') refetchDrivers();
    else if (activeTab === 'activities') refetchActivities();
    else if (activeTab === 'pools') refetchPools();
    else refetchObjects();
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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const filterItems = (items: any[]) => {
    if (!searchTerm) return items;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
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
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
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
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
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
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
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
    }
  };

  const currentItems = activeTab === 'drivers' ? filterItems(drivers)
    : activeTab === 'activities' ? filterItems(activities)
    : activeTab === 'pools' ? filterItems(pools)
    : filterItems(objects);

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
              <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
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
        <div className="flex gap-1 mb-6 p-1 bg-[hsl(var(--muted))] rounded-lg w-fit">
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

        {/* Search */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <Input
              type="search"
              placeholder={`Buscar ${TABS.find(t => t.key === activeTab)?.label.toLowerCase()}...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              icon={<Search className="w-4 h-4" />}
            />
          </div>
        </div>

        {/* Table */}
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
          {isLoading ? (
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
    </div>
  );
}
