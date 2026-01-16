'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Briefcase,
  Users,
  Route,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Filter,
  Search,
  RefreshCw,
  Plus,
  Grid,
  List,
  X,
} from 'lucide-react';
import { Card } from '@/core/components/ui';
import { Button } from '@/core/components/ui';
import { Badge } from '@/core/components/ui';
import { Input } from '@/core/components/ui';
import { Spinner } from '@/core/components/ui';

import { useFieldService } from './hooks';
import { ServiceOrderCard } from './orders/components';
import { TechnicianCard, TechnicianMap, RouteOptimizer } from './technicians/components';
import type { StatusOrdem, TipoServico, PrioridadeServico, StatusTecnico } from './types';
import { STATUS_ORDEM_CONFIG, TIPO_SERVICO_CONFIG, PRIORIDADE_CONFIG, STATUS_TECNICO_CONFIG } from './types';

type TabType = 'ordens' | 'tecnicos' | 'rotas';
type ViewMode = 'grid' | 'list';

export function FieldServiceDashboard() {
  // States
  const [activeTab, setActiveTab] = useState<TabType>('ordens');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTechnician, setSelectedTechnician] = useState<string | undefined>();

  // Filtros de ordens
  const [statusFilter, setStatusFilter] = useState<StatusOrdem[]>([]);
  const [tipoFilter, setTipoFilter] = useState<TipoServico[]>([]);
  const [prioridadeFilter, setPrioridadeFilter] = useState<PrioridadeServico[]>([]);

  // Filtros de técnicos
  const [statusTecnicoFilter, setStatusTecnicoFilter] = useState<StatusTecnico[]>([]);

  // Hook principal
  const {
    kpis,
    kpisLoading,
    orders,
    technicians,
    routes,
    isLoading,
    refetchAll,
  } = useFieldService();

  // Aplicar filtros nas ordens
  const filteredOrders = useMemo(() => {
    let filtered = orders.orders;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(o =>
        o.numero.toLowerCase().includes(query) ||
        o.cliente.toLowerCase().includes(query) ||
        o.descricao.toLowerCase().includes(query)
      );
    }

    if (statusFilter.length > 0) {
      filtered = filtered.filter(o => statusFilter.includes(o.status));
    }

    if (tipoFilter.length > 0) {
      filtered = filtered.filter(o => tipoFilter.includes(o.tipo));
    }

    if (prioridadeFilter.length > 0) {
      filtered = filtered.filter(o => prioridadeFilter.includes(o.prioridade));
    }

    return filtered;
  }, [orders.orders, searchQuery, statusFilter, tipoFilter, prioridadeFilter]);

  // Aplicar filtros nos técnicos
  const filteredTechnicians = useMemo(() => {
    let filtered = technicians.technicians;

    if (searchQuery && activeTab === 'tecnicos') {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.nome.toLowerCase().includes(query) ||
        t.especialidades.some(e => e.toLowerCase().includes(query))
      );
    }

    if (statusTecnicoFilter.length > 0) {
      filtered = filtered.filter(t => statusTecnicoFilter.includes(t.status));
    }

    return filtered;
  }, [technicians.technicians, searchQuery, activeTab, statusTecnicoFilter]);

  // Toggle de filtros
  const toggleStatusFilter = (status: StatusOrdem) => {
    setStatusFilter(prev =>
      prev.includes(status) ? prev.filter(s => s !== status) : [...prev, status]
    );
  };

  const toggleTipoFilter = (tipo: TipoServico) => {
    setTipoFilter(prev =>
      prev.includes(tipo) ? prev.filter(t => t !== tipo) : [...prev, tipo]
    );
  };

  const togglePrioridadeFilter = (prioridade: PrioridadeServico) => {
    setPrioridadeFilter(prev =>
      prev.includes(prioridade) ? prev.filter(p => p !== prioridade) : [...prev, prioridade]
    );
  };

  const toggleStatusTecnicoFilter = (status: StatusTecnico) => {
    setStatusTecnicoFilter(prev =>
      prev.includes(status) ? prev.filter(s => s !== status) : [...prev, status]
    );
  };

  const clearAllFilters = () => {
    setStatusFilter([]);
    setTipoFilter([]);
    setPrioridadeFilter([]);
    setStatusTecnicoFilter([]);
    setSearchQuery('');
  };

  const hasActiveFilters = statusFilter.length > 0 || tipoFilter.length > 0 ||
    prioridadeFilter.length > 0 || statusTecnicoFilter.length > 0 || searchQuery.length > 0;

  // Tabs
  const tabs: { id: TabType; label: string; icon: React.ReactNode; count?: number }[] = [
    { id: 'ordens', label: 'Ordens de Servico', icon: <Briefcase className="w-4 h-4" />, count: orders.stats.total },
    { id: 'tecnicos', label: 'Tecnicos', icon: <Users className="w-4 h-4" />, count: technicians.stats.total },
    { id: 'rotas', label: 'Rotas', icon: <Route className="w-4 h-4" />, count: routes.routes.length },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Field Service</h1>
          <p className="text-gray-500 mt-1">
            Gerenciamento de ordens de servico e tecnicos em campo
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            onClick={() => refetchAll()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button variant="primary">
            <Plus className="w-4 h-4 mr-2" />
            Nova Ordem
          </Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {kpisLoading ? <Spinner size="sm" /> : kpis?.ordens_abertas || 0}
              </div>
              <div className="text-xs text-gray-500">Abertas</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Briefcase className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {kpisLoading ? <Spinner size="sm" /> : kpis?.ordens_em_atendimento || 0}
              </div>
              <div className="text-xs text-gray-500">Em Atendimento</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {kpisLoading ? <Spinner size="sm" /> : kpis?.ordens_concluidas_hoje || 0}
              </div>
              <div className="text-xs text-gray-500">Concluidas Hoje</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {kpisLoading ? <Spinner size="sm" /> : `${kpis?.sla_compliance || 0}%`}
              </div>
              <div className="text-xs text-gray-500">SLA Compliance</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-teal-100 rounded-lg">
              <Users className="w-5 h-5 text-teal-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {kpisLoading ? <Spinner size="sm" /> : (
                  `${kpis?.tecnicos_disponiveis || 0}/${kpis?.tecnicos_total || 0}`
                )}
              </div>
              <div className="text-xs text-gray-500">Tecnicos Disp.</div>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {orders.isLoading ? <Spinner size="sm" /> : orders.stats.urgentes}
              </div>
              <div className="text-xs text-gray-500">Urgentes</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex items-center justify-between">
          <nav className="flex gap-4">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.icon}
                <span className="font-medium">{tab.label}</span>
                {tab.count !== undefined && (
                  <Badge variant="default" size="sm">{tab.count}</Badge>
                )}
              </button>
            ))}
          </nav>

          {/* Controles de view */}
          <div className="flex items-center gap-2 pb-2">
            <Button
              variant={showFilters ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="w-4 h-4 mr-1" />
              Filtros
              {hasActiveFilters && (
                <span className="ml-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </Button>
            <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-gray-100 text-gray-900' : 'text-gray-500'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-gray-100 text-gray-900' : 'text-gray-500'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <Card className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-gray-900">Filtros</h3>
                {hasActiveFilters && (
                  <Button variant="ghost" size="sm" onClick={clearAllFilters}>
                    <X className="w-4 h-4 mr-1" />
                    Limpar filtros
                  </Button>
                )}
              </div>

              {/* Busca */}
              <div className="mb-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    placeholder={activeTab === 'ordens' ? 'Buscar ordens...' : 'Buscar tecnicos...'}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Filtros de Ordens */}
              {activeTab === 'ordens' && (
                <div className="space-y-4">
                  {/* Status */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">Status</label>
                    <div className="flex flex-wrap gap-2">
                      {(Object.keys(STATUS_ORDEM_CONFIG) as StatusOrdem[]).map((status) => (
                        <button
                          key={status}
                          onClick={() => toggleStatusFilter(status)}
                          className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                            statusFilter.includes(status)
                              ? 'bg-blue-100 border-blue-300 text-blue-700'
                              : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                          }`}
                        >
                          {STATUS_ORDEM_CONFIG[status].label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Tipo */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">Tipo</label>
                    <div className="flex flex-wrap gap-2">
                      {(Object.keys(TIPO_SERVICO_CONFIG) as TipoServico[]).map((tipo) => (
                        <button
                          key={tipo}
                          onClick={() => toggleTipoFilter(tipo)}
                          className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                            tipoFilter.includes(tipo)
                              ? 'bg-blue-100 border-blue-300 text-blue-700'
                              : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                          }`}
                        >
                          {TIPO_SERVICO_CONFIG[tipo].label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Prioridade */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">Prioridade</label>
                    <div className="flex flex-wrap gap-2">
                      {(Object.keys(PRIORIDADE_CONFIG) as PrioridadeServico[]).map((prioridade) => (
                        <button
                          key={prioridade}
                          onClick={() => togglePrioridadeFilter(prioridade)}
                          className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                            prioridadeFilter.includes(prioridade)
                              ? 'bg-blue-100 border-blue-300 text-blue-700'
                              : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                          }`}
                        >
                          {PRIORIDADE_CONFIG[prioridade].label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Filtros de Técnicos */}
              {activeTab === 'tecnicos' && (
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">Status</label>
                  <div className="flex flex-wrap gap-2">
                    {(Object.keys(STATUS_TECNICO_CONFIG) as StatusTecnico[]).map((status) => (
                      <button
                        key={status}
                        onClick={() => toggleStatusTecnicoFilter(status)}
                        className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                          statusTecnicoFilter.includes(status)
                            ? 'bg-blue-100 border-blue-300 text-blue-700'
                            : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                        }`}
                      >
                        {STATUS_TECNICO_CONFIG[status].label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Conteúdo */}
      <AnimatePresence mode="wait">
        {/* Tab Ordens */}
        {activeTab === 'ordens' && (
          <motion.div
            key="ordens"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {orders.isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Spinner size="lg" />
              </div>
            ) : filteredOrders.length === 0 ? (
              <Card className="p-12 text-center">
                <Briefcase className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhuma ordem encontrada
                </h3>
                <p className="text-gray-500">
                  {hasActiveFilters
                    ? 'Tente ajustar os filtros para ver mais resultados'
                    : 'Crie uma nova ordem de servico para comecar'
                  }
                </p>
              </Card>
            ) : (
              <div className={viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
                : 'space-y-3'
              }>
                {filteredOrders.map((order) => (
                  <ServiceOrderCard
                    key={order.id}
                    order={order}
                    onClick={() => console.log('Ordem selecionada:', order.id)}
                    showDetails={viewMode === 'grid'}
                  />
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Tab Técnicos */}
        {activeTab === 'tecnicos' && (
          <motion.div
            key="tecnicos"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-6"
          >
            {/* Mapa de técnicos */}
            <TechnicianMap
              technicians={filteredTechnicians}
              selectedTechnician={selectedTechnician}
              onSelectTechnician={setSelectedTechnician}
              onRefresh={() => technicians.refetch()}
              isLoading={technicians.isLoading}
            />

            {/* Lista de técnicos */}
            {technicians.isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Spinner size="lg" />
              </div>
            ) : filteredTechnicians.length === 0 ? (
              <Card className="p-12 text-center">
                <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhum tecnico encontrado
                </h3>
                <p className="text-gray-500">
                  Ajuste os filtros para ver mais resultados
                </p>
              </Card>
            ) : (
              <div className={viewMode === 'grid'
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
                : 'space-y-3'
              }>
                {filteredTechnicians.map((tech) => (
                  <TechnicianCard
                    key={tech.id}
                    technician={tech}
                    onClick={() => setSelectedTechnician(
                      selectedTechnician === tech.id ? undefined : tech.id
                    )}
                    compact={viewMode === 'list'}
                  />
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Tab Rotas */}
        {activeTab === 'rotas' && (
          <motion.div
            key="rotas"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-4"
          >
            {routes.isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Spinner size="lg" />
              </div>
            ) : routes.routes.length === 0 ? (
              <Card className="p-12 text-center">
                <Route className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhuma rota ativa
                </h3>
                <p className="text-gray-500">
                  As rotas serao criadas automaticamente ao atribuir ordens aos tecnicos
                </p>
              </Card>
            ) : (
              routes.routes.map((route) => (
                <RouteOptimizer
                  key={route.id}
                  route={route}
                  orders={orders.orders}
                  onOptimize={routes.optimizeRoute}
                  onReorder={routes.reorderRoute}
                  isOptimizing={routes.isOptimizing}
                />
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default FieldServiceDashboard;
