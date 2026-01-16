'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  MapPin,
  Navigation,
  Route,
  Clock,
  Calendar,
  User,
  Building2,
  Play,
  Pause,
  CheckCircle2,
  AlertTriangle,
  Car,
  Truck,
  Bike,
  TrendingUp,
  Timer,
  Target,
  Eye,
  Edit,
  Copy,
  Map,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
} from '@/design-system/components';

// Types
interface RoutePoint {
  id: string;
  order: number;
  client: string;
  address: string;
  type: 'start' | 'visit' | 'service' | 'end';
  estimatedArrival: string;
  actualArrival: string | null;
  estimatedDuration: number;
  actualDuration: number | null;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
}

interface PlannedRoute {
  id: string;
  name: string;
  date: string;
  vehicle: 'car' | 'motorcycle' | 'van' | 'truck';
  responsible: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  points: RoutePoint[];
  totalDistance: number;
  estimatedDuration: number;
  actualDuration: number | null;
  startTime: string | null;
  endTime: string | null;
  efficiency: number | null;
}

// Mock Data
const routes: PlannedRoute[] = [
  {
    id: '1',
    name: 'Rota Norte - Manutenção',
    date: '2026-01-15',
    vehicle: 'van',
    responsible: 'Carlos Eduardo',
    status: 'in_progress',
    points: [
      { id: '1a', order: 1, client: 'Base', address: 'Av. Paulista, 1000', type: 'start', estimatedArrival: '08:00', actualArrival: '08:05', estimatedDuration: 0, actualDuration: 0, status: 'completed' },
      { id: '1b', order: 2, client: 'Shopping Center Norte', address: 'Av. Cruzeiro do Sul, 1100', type: 'service', estimatedArrival: '08:45', actualArrival: '08:50', estimatedDuration: 120, actualDuration: 110, status: 'completed' },
      { id: '1c', order: 3, client: 'Hospital São Lucas', address: 'Rua Dr. Arnaldo, 500', type: 'service', estimatedArrival: '11:30', actualArrival: '11:25', estimatedDuration: 90, actualDuration: null, status: 'in_progress' },
      { id: '1d', order: 4, client: 'Condomínio Aurora', address: 'Rua das Flores, 200', type: 'visit', estimatedArrival: '14:00', actualArrival: null, estimatedDuration: 60, actualDuration: null, status: 'pending' },
      { id: '1e', order: 5, client: 'Base', address: 'Av. Paulista, 1000', type: 'end', estimatedArrival: '16:00', actualArrival: null, estimatedDuration: 0, actualDuration: null, status: 'pending' },
    ],
    totalDistance: 45.5,
    estimatedDuration: 480,
    actualDuration: null,
    startTime: '08:05',
    endTime: null,
    efficiency: null,
  },
  {
    id: '2',
    name: 'Rota Sul - Instalações',
    date: '2026-01-15',
    vehicle: 'car',
    responsible: 'Ana Paula',
    status: 'planned',
    points: [
      { id: '2a', order: 1, client: 'Base', address: 'Av. Paulista, 1000', type: 'start', estimatedArrival: '09:00', actualArrival: null, estimatedDuration: 0, actualDuration: null, status: 'pending' },
      { id: '2b', order: 2, client: 'Tech Park Empresarial', address: 'Av. Paulista, 1000', type: 'service', estimatedArrival: '09:30', actualArrival: null, estimatedDuration: 180, actualDuration: null, status: 'pending' },
      { id: '2c', order: 3, client: 'Banco Regional', address: 'Av. Brigadeiro, 800', type: 'service', estimatedArrival: '13:30', actualArrival: null, estimatedDuration: 120, actualDuration: null, status: 'pending' },
      { id: '2d', order: 4, client: 'Base', address: 'Av. Paulista, 1000', type: 'end', estimatedArrival: '16:30', actualArrival: null, estimatedDuration: 0, actualDuration: null, status: 'pending' },
    ],
    totalDistance: 28.3,
    estimatedDuration: 450,
    actualDuration: null,
    startTime: null,
    endTime: null,
    efficiency: null,
  },
  {
    id: '3',
    name: 'Rota Express - Emergências',
    date: '2026-01-15',
    vehicle: 'motorcycle',
    responsible: 'Pedro Santos',
    status: 'completed',
    points: [
      { id: '3a', order: 1, client: 'Base', address: 'Av. Paulista, 1000', type: 'start', estimatedArrival: '07:00', actualArrival: '07:00', estimatedDuration: 0, actualDuration: 0, status: 'completed' },
      { id: '3b', order: 2, client: 'Edifício Corporate', address: 'Rua Augusta, 500', type: 'service', estimatedArrival: '07:30', actualArrival: '07:25', estimatedDuration: 45, actualDuration: 40, status: 'completed' },
      { id: '3c', order: 3, client: 'Clínica Vida', address: 'Al. Santos, 300', type: 'service', estimatedArrival: '08:45', actualArrival: '08:40', estimatedDuration: 60, actualDuration: 55, status: 'completed' },
      { id: '3d', order: 4, client: 'Base', address: 'Av. Paulista, 1000', type: 'end', estimatedArrival: '10:30', actualArrival: '10:15', estimatedDuration: 0, actualDuration: 0, status: 'completed' },
    ],
    totalDistance: 15.2,
    estimatedDuration: 210,
    actualDuration: 195,
    startTime: '07:00',
    endTime: '10:15',
    efficiency: 107,
  },
  {
    id: '4',
    name: 'Rota Oeste - Vistorias',
    date: '2026-01-14',
    vehicle: 'car',
    responsible: 'Roberto Silva',
    status: 'completed',
    points: [
      { id: '4a', order: 1, client: 'Base', address: 'Av. Paulista, 1000', type: 'start', estimatedArrival: '08:00', actualArrival: '08:10', estimatedDuration: 0, actualDuration: 0, status: 'completed' },
      { id: '4b', order: 2, client: 'Shopping Oeste', address: 'Av. Rebouças, 1500', type: 'visit', estimatedArrival: '09:00', actualArrival: '09:15', estimatedDuration: 90, actualDuration: 100, status: 'completed' },
      { id: '4c', order: 3, client: 'Centro Comercial', address: 'Av. Faria Lima, 2000', type: 'visit', estimatedArrival: '11:30', actualArrival: '11:45', estimatedDuration: 60, actualDuration: 70, status: 'completed' },
      { id: '4d', order: 4, client: 'Base', address: 'Av. Paulista, 1000', type: 'end', estimatedArrival: '14:00', actualArrival: '14:30', estimatedDuration: 0, actualDuration: 0, status: 'completed' },
    ],
    totalDistance: 32.8,
    estimatedDuration: 360,
    actualDuration: 390,
    startTime: '08:10',
    endTime: '14:30',
    efficiency: 92,
  },
];

const vehicleConfig = {
  car: { label: 'Carro', icon: Car },
  motorcycle: { label: 'Moto', icon: Bike },
  van: { label: 'Van', icon: Truck },
  truck: { label: 'Caminhão', icon: Truck },
};

const statusConfig = {
  planned: { label: 'Planejada', color: 'info' as const },
  in_progress: { label: 'Em Andamento', color: 'primary' as const },
  completed: { label: 'Concluída', color: 'success' as const },
  cancelled: { label: 'Cancelada', color: 'neutral' as const },
};

const columns: Column<PlannedRoute>[] = [
  {
    key: 'name',
    header: 'Rota',
    render: (row) => {
      const VehicleIcon = vehicleConfig[row.vehicle].icon;
      return (
        <div className="flex items-center gap-3">
          <div className="p-2 bg-bg-tertiary rounded-lg">
            <VehicleIcon className="w-5 h-5 text-text-muted" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{vehicleConfig[row.vehicle].label}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'date',
    header: 'Data',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Calendar className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.date}</span>
      </div>
    ),
  },
  {
    key: 'responsible',
    header: 'Responsável',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.responsible} size="xs" />
        <span className="text-sm">{row.responsible}</span>
      </div>
    ),
  },
  {
    key: 'points',
    header: 'Pontos',
    render: (row) => {
      const servicePoints = row.points.filter(p => p.type !== 'start' && p.type !== 'end').length;
      const completed = row.points.filter(p => p.status === 'completed' && p.type !== 'start').length;
      return (
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-text-muted" />
          <span className="text-sm">{completed}/{servicePoints} pontos</span>
        </div>
      );
    },
  },
  {
    key: 'distance',
    header: 'Distância',
    render: (row) => (
      <span className="text-sm">{row.totalDistance} km</span>
    ),
  },
  {
    key: 'duration',
    header: 'Duração',
    render: (row) => {
      const estimated = Math.floor(row.estimatedDuration / 60);
      const actual = row.actualDuration ? Math.floor(row.actualDuration / 60) : null;
      return (
        <div>
          <p className="text-sm text-text-primary">
            {actual !== null ? `${actual}h` : '-'} / {estimated}h
          </p>
          {row.efficiency !== null && (
            <Badge size="sm" variant={row.efficiency >= 100 ? 'success' : row.efficiency >= 90 ? 'warning' : 'danger'}>
              {row.efficiency}% eficiência
            </Badge>
          )}
        </div>
      );
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver no mapa">
          <Map className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'planned' && (
          <Button variant="primary" size="sm" leftIcon={<Play className="w-3 h-3" />}>
            Iniciar
          </Button>
        )}
      </div>
    ),
  },
];

export function RoutesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState<PlannedRoute | null>(null);

  // Stats
  const todayRoutes = routes.filter(r => r.date === '2026-01-15').length;
  const inProgressCount = routes.filter(r => r.status === 'in_progress').length;
  const completedToday = routes.filter(r => r.status === 'completed' && r.date === '2026-01-15').length;
  const avgEfficiency = routes
    .filter(r => r.efficiency !== null)
    .reduce((acc, r) => acc + (r.efficiency || 0), 0) /
    routes.filter(r => r.efficiency !== null).length;
  const totalKm = routes.filter(r => r.date === '2026-01-15').reduce((acc, r) => acc + r.totalDistance, 0);

  const filteredRoutes = routes.filter((route) => {
    const matchesSearch =
      route.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      route.responsible.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || route.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Roteirização
            </h1>
            <p className="text-text-secondary mt-1">
              Planeje e acompanhe rotas de campo
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Map className="w-4 h-4" />}>
              Mapa em Tempo Real
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Rota
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Rotas Hoje"
              value={todayRoutes}
              icon={<Route className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Em Andamento"
              value={inProgressCount}
              icon={<Navigation className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Concluídas"
              value={completedToday}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Eficiência Média"
              value={`${Math.round(avgEfficiency)}%`}
              icon={<Target className="w-6 h-6" />}
              iconColor={avgEfficiency >= 100 ? 'success' : 'warning'}
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="KM Total Hoje"
              value={`${totalKm.toFixed(1)}`}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Active Routes */}
        {inProgressCount > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card>
              <CardHeader
                title="Rotas em Andamento"
                action={
                  <Button variant="outline" size="sm" leftIcon={<Map className="w-4 h-4" />}>
                    Ver Todas no Mapa
                  </Button>
                }
              />
              <CardBody>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {routes.filter(r => r.status === 'in_progress').map((route) => {
                    const VehicleIcon = vehicleConfig[route.vehicle].icon;
                    const currentPoint = route.points.find(p => p.status === 'in_progress');
                    const completedPoints = route.points.filter(p => p.status === 'completed').length;
                    const totalPoints = route.points.length;

                    return (
                      <div key={route.id} className="p-4 bg-bg-tertiary rounded-xl">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-accent-primary/20 rounded-lg">
                              <VehicleIcon className="w-5 h-5 text-accent-primary" />
                            </div>
                            <div>
                              <p className="font-medium text-text-primary">{route.name}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <Avatar name={route.responsible} size="xs" />
                                <span className="text-xs text-text-muted">{route.responsible}</span>
                              </div>
                            </div>
                          </div>
                          <Badge variant="primary">Em Andamento</Badge>
                        </div>

                        {currentPoint && (
                          <div className="p-3 bg-bg-secondary rounded-lg mb-3">
                            <div className="flex items-center gap-2 text-accent-primary mb-1">
                              <Navigation className="w-4 h-4" />
                              <span className="text-sm font-medium">Ponto Atual</span>
                            </div>
                            <p className="text-text-primary">{currentPoint.client}</p>
                            <p className="text-xs text-text-muted">{currentPoint.address}</p>
                          </div>
                        )}

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4 text-text-muted" />
                              <span className="text-sm">{completedPoints}/{totalPoints}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Timer className="w-4 h-4 text-text-muted" />
                              <span className="text-sm">
                                Início: {route.startTime}
                              </span>
                            </div>
                          </div>
                          <Button variant="outline" size="sm">
                            Acompanhar
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: 'Todas' },
                  { value: 'planned', label: 'Planejadas' },
                  { value: 'in_progress', label: 'Em Andamento' },
                  { value: 'completed', label: 'Concluídas' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar rotas..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Input
                  type="date"
                  defaultValue="2026-01-15"
                  className="w-40"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Routes Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredRoutes}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedRoute(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Route Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Rota"
          description="Planeje uma nova rota de campo"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar Rota
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome da Rota" placeholder="Ex: Rota Norte - Manutenção" required />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data" type="date" required />
              <Select
                label="Veículo"
                options={[
                  { value: 'car', label: 'Carro' },
                  { value: 'motorcycle', label: 'Moto' },
                  { value: 'van', label: 'Van' },
                  { value: 'truck', label: 'Caminhão' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <Select
              label="Responsável"
              options={[
                { value: '1', label: 'Ana Paula' },
                { value: '2', label: 'Carlos Eduardo' },
                { value: '3', label: 'Roberto Silva' },
                { value: '4', label: 'Pedro Santos' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />
            <div className="pt-4 border-t border-border-subtle">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-text-primary">Pontos da Rota</h4>
                <Button variant="outline" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                  Adicionar Ponto
                </Button>
              </div>
              <p className="text-sm text-text-muted">
                Adicione os pontos que serão visitados nesta rota. O sistema otimizará automaticamente a ordem.
              </p>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
