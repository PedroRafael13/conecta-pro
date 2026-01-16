'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  type Column,
  Modal,
  Select
} from '@/design-system/components';
import {
  UserPlus,
  Plus,
  Search,
  Filter,
  Download,
  Clock,
  User,
  Users,
  Calendar,
  MapPin,
  Phone,
  FileText,
  CheckCircle,
  XCircle,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  Eye
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

// Types
interface DailyWorker {
  id: string;
  name: string;
  cpf: string;
  phone: string;
  skills: string[];
  dailyRate: number;
  status: 'available' | 'allocated' | 'absent' | 'inactive';
  rating: number;
  totalDays: number;
  lastWork: string;
}

interface DailyAllocation {
  id: string;
  workerId: string;
  workerName: string;
  date: string;
  shift: string;
  post: string;
  client: string;
  status: 'scheduled' | 'in-progress' | 'completed' | 'no-show';
  checkIn?: string;
  checkOut?: string;
  value: number;
}

// Mock data
const mockWorkers: DailyWorker[] = [
  {
    id: '1',
    name: 'José Oliveira',
    cpf: '123.456.789-00',
    phone: '(11) 98765-4321',
    skills: ['Limpeza', 'Conservação', 'Manutenção básica'],
    dailyRate: 150,
    status: 'available',
    rating: 4.7,
    totalDays: 45,
    lastWork: '2026-01-15'
  },
  {
    id: '2',
    name: 'Mariana Costa',
    cpf: '234.567.890-11',
    phone: '(11) 97654-3210',
    skills: ['Recepção', 'Atendimento', 'Organização'],
    dailyRate: 180,
    status: 'allocated',
    rating: 4.9,
    totalDays: 78,
    lastWork: '2026-01-16'
  },
  {
    id: '3',
    name: 'Roberto Santos',
    cpf: '345.678.901-22',
    phone: '(11) 96543-2109',
    skills: ['Segurança', 'Vigilância', 'Controle de acesso'],
    dailyRate: 200,
    status: 'allocated',
    rating: 4.5,
    totalDays: 120,
    lastWork: '2026-01-16'
  },
  {
    id: '4',
    name: 'Ana Paula Lima',
    cpf: '456.789.012-33',
    phone: '(11) 95432-1098',
    skills: ['Cozinha', 'Copa', 'Serviços gerais'],
    dailyRate: 160,
    status: 'absent',
    rating: 4.3,
    totalDays: 32,
    lastWork: '2026-01-10'
  }
];

const mockAllocations: DailyAllocation[] = [
  {
    id: '1',
    workerId: '2',
    workerName: 'Mariana Costa',
    date: '2026-01-16',
    shift: 'Matutino',
    post: 'Recepção Principal',
    client: 'Condomínio Verde',
    status: 'in-progress',
    checkIn: '08:00',
    value: 180
  },
  {
    id: '2',
    workerId: '3',
    workerName: 'Roberto Santos',
    date: '2026-01-16',
    shift: 'Matutino',
    post: 'Portaria',
    client: 'Edifício Comercial ABC',
    status: 'in-progress',
    checkIn: '06:00',
    value: 200
  },
  {
    id: '3',
    workerId: '1',
    workerName: 'José Oliveira',
    date: '2026-01-15',
    shift: 'Vespertino',
    post: 'Limpeza Geral',
    client: 'Shopping Center',
    status: 'completed',
    checkIn: '14:00',
    checkOut: '22:00',
    value: 150
  },
  {
    id: '4',
    workerId: '4',
    workerName: 'Ana Paula Lima',
    date: '2026-01-16',
    shift: 'Matutino',
    post: 'Copa/Cozinha',
    client: 'Empresa XYZ',
    status: 'no-show',
    value: 160
  }
];

// Chart data
const workersByStatus = [
  { name: 'Disponíveis', value: 234, color: '#10b981' },
  { name: 'Alocados', value: 156, color: '#6366f1' },
  { name: 'Ausentes', value: 12, color: '#f59e0b' },
  { name: 'Inativos', value: 45, color: '#64748b' }
];

const weeklyAllocations = [
  { day: 'Seg', allocated: 145, completed: 140, noShow: 5 },
  { day: 'Ter', allocated: 152, completed: 148, noShow: 4 },
  { day: 'Qua', allocated: 160, completed: 155, noShow: 5 },
  { day: 'Qui', allocated: 158, completed: 153, noShow: 5 },
  { day: 'Sex', allocated: 165, completed: 160, noShow: 5 },
  { day: 'Sáb', allocated: 80, completed: 78, noShow: 2 },
  { day: 'Dom', allocated: 60, completed: 58, noShow: 2 }
];

export function DailyWorkersPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showNewWorkerModal, setShowNewWorkerModal] = useState(false);
  const [showAllocateModal, setShowAllocateModal] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState<DailyWorker | null>(null);
  const [filterAllocationStatus, setFilterAllocationStatus] = useState('');
  const [newShift, setNewShift] = useState('');
  const [newClient, setNewClient] = useState('');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <UserPlus className="h-4 w-4" /> },
    { value: 'workers', label: 'Diaristas', icon: <Users className="h-4 w-4" /> },
    { value: 'allocations', label: 'Alocações', icon: <Calendar className="h-4 w-4" /> }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'available': return <Badge variant="success">Disponível</Badge>;
      case 'allocated': return <Badge variant="primary">Alocado</Badge>;
      case 'absent': return <Badge variant="warning">Ausente</Badge>;
      case 'inactive': return <Badge variant="neutral">Inativo</Badge>;
      case 'scheduled': return <Badge variant="info">Agendado</Badge>;
      case 'in-progress': return <Badge variant="warning">Em Serviço</Badge>;
      case 'completed': return <Badge variant="success">Concluído</Badge>;
      case 'no-show': return <Badge variant="danger">Não Compareceu</Badge>;
      default: return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const workerColumns: Column<DailyWorker>[] = [
    {
      key: 'name',
      header: 'Diarista',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.cpf}</p>
          </div>
        </div>
      )
    },
    {
      key: 'phone',
      header: 'Contato',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Phone className="h-4 w-4 text-text-muted" />
          <span className="text-text-secondary">{row.phone}</span>
        </div>
      )
    },
    {
      key: 'skills',
      header: 'Habilidades',
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          {row.skills.slice(0, 2).map((skill) => (
            <Badge key={skill} variant="outline" size="sm">{skill}</Badge>
          ))}
          {row.skills.length > 2 && (
            <Badge variant="outline" size="sm">+{row.skills.length - 2}</Badge>
          )}
        </div>
      )
    },
    {
      key: 'dailyRate',
      header: 'Diária',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.dailyRate.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'rating',
      header: 'Avaliação',
      render: (row) => (
        <div className="flex items-center gap-1">
          <span className="text-warning">★</span>
          <span className="text-text-primary">{row.rating.toFixed(1)}</span>
          <span className="text-text-muted text-sm">({row.totalDays} dias)</span>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedWorker(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'available' && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSelectedWorker(row);
                setShowAllocateModal(true);
              }}
            >
              <UserPlus className="h-4 w-4 mr-1" />
              Alocar
            </Button>
          )}
        </div>
      )
    }
  ];

  const allocationColumns: Column<DailyAllocation>[] = [
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <span className="text-text-primary">
          {new Date(row.date).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      key: 'workerName',
      header: 'Diarista',
      render: (row) => (
        <span className="font-medium text-text-primary">{row.workerName}</span>
      )
    },
    {
      key: 'post',
      header: 'Posto',
      render: (row) => (
        <div>
          <p className="text-text-primary">{row.post}</p>
          <p className="text-sm text-text-secondary">{row.client}</p>
        </div>
      )
    },
    {
      key: 'shift',
      header: 'Turno',
      render: (row) => (
        <span className="text-text-secondary">{row.shift}</span>
      )
    },
    {
      key: 'checkIn',
      header: 'Entrada/Saída',
      render: (row) => (
        <div className="text-text-secondary">
          {row.checkIn ? (
            <>
              <span className="text-success">{row.checkIn}</span>
              {row.checkOut && <span> - <span className="text-danger">{row.checkOut}</span></span>}
            </>
          ) : (
            <span className="text-text-muted">-</span>
          )}
        </div>
      )
    },
    {
      key: 'value',
      header: 'Valor',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    }
  ];

  const filteredWorkers = mockWorkers.filter(worker => {
    const matchesSearch = worker.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      worker.cpf.includes(searchTerm);
    const matchesStatus = filterStatus === 'all' || worker.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const availableCount = mockWorkers.filter(w => w.status === 'available').length;
  const allocatedCount = mockWorkers.filter(w => w.status === 'allocated').length;
  const absentCount = mockWorkers.filter(w => w.status === 'absent').length;
  const todayTotal = mockAllocations.filter(a => a.date === '2026-01-16').reduce((sum, a) => sum + a.value, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Diaristas
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de trabalhadores diaristas
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewWorkerModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Diarista
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Diaristas Hoje"
            value={allocatedCount.toString()}
            icon={<UserPlus className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Disponíveis"
            value={availableCount.toString()}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Ausentes"
            value={absentCount.toString()}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Custo Hoje"
            value={todayTotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="info"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Workers by Status */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Diaristas por Status
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={workersByStatus}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {workersByStatus.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Weekly Allocations */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Alocações Semanais
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyAllocations}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Bar dataKey="allocated" name="Alocados" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="completed" name="Concluídos" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="noShow" name="Não Compareceu" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* In Service Now */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Em Serviço Agora
                </h3>
                <Badge variant="success">{allocatedCount} ativos</Badge>
              </div>
              <div className="space-y-4">
                {mockAllocations.filter(a => a.status === 'in-progress').map((allocation) => (
                  <div key={allocation.id} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-success/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-success" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{allocation.workerName}</p>
                        <p className="text-sm text-text-secondary">{allocation.post}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-success">Entrada: {allocation.checkIn}</p>
                      <p className="text-sm text-text-muted">{allocation.client}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Available Workers */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Disponíveis para Alocação
                </h3>
                <Badge variant="info">{availableCount}</Badge>
              </div>
              <div className="space-y-4">
                {mockWorkers.filter(w => w.status === 'available').slice(0, 4).map((worker) => (
                  <div key={worker.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{worker.name}</p>
                        <div className="flex items-center gap-1">
                          <span className="text-warning text-sm">★</span>
                          <span className="text-sm text-text-secondary">{worker.rating}</span>
                        </div>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      <UserPlus className="h-4 w-4 mr-1" />
                      Alocar
                    </Button>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Workers Tab */}
        {activeTab === 'workers' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar diarista..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={[
                  { value: 'all', label: 'Todos os status' },
                  { value: 'available', label: 'Disponíveis' },
                  { value: 'allocated', label: 'Alocados' },
                  { value: 'absent', label: 'Ausentes' },
                  { value: 'inactive', label: 'Inativos' }
                ]}
                className="w-40"
              />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={workerColumns}
              data={filteredWorkers}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Allocations Tab */}
        {activeTab === 'allocations' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar alocação..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Input type="date" className="w-40" />
              <Select
                value={filterAllocationStatus}
                onChange={(value) => setFilterAllocationStatus(value)}
                options={[
                  { value: '', label: 'Todos os status' },
                  { value: 'scheduled', label: 'Agendados' },
                  { value: 'in-progress', label: 'Em Serviço' },
                  { value: 'completed', label: 'Concluídos' },
                  { value: 'no-show', label: 'Não Compareceu' }
                ]}
                className="w-48"
              />
            </div>
            <DataTable
              columns={allocationColumns}
              data={mockAllocations}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Worker Detail Modal */}
        {selectedWorker && !showAllocateModal && (
          <Modal
            isOpen={!!selectedWorker && !showAllocateModal}
            onClose={() => setSelectedWorker(null)}
            title="Detalhes do Diarista"
            size="md"
          >
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">
                    {selectedWorker.name}
                  </h3>
                  <p className="text-text-secondary">{selectedWorker.cpf}</p>
                  <div className="mt-1">{getStatusBadge(selectedWorker.status)}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Contato</p>
                  <p className="font-medium text-text-primary">{selectedWorker.phone}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Diária</p>
                  <p className="font-medium text-text-primary">
                    {selectedWorker.dailyRate.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-text-secondary mb-2">Habilidades</p>
                <div className="flex flex-wrap gap-2">
                  {selectedWorker.skills.map((skill) => (
                    <Badge key={skill} variant="outline">{skill}</Badge>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border-subtle">
                <div className="text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedWorker.totalDays}</p>
                  <p className="text-sm text-text-secondary">Dias trabalhados</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    <span className="text-2xl font-bold text-warning">★</span>
                    <span className="text-2xl font-bold text-text-primary">{selectedWorker.rating}</span>
                  </div>
                  <p className="text-sm text-text-secondary">Avaliação</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-text-primary">
                    {new Date(selectedWorker.lastWork).toLocaleDateString('pt-BR')}
                  </p>
                  <p className="text-sm text-text-secondary">Último trabalho</p>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedWorker(null)}>
                  Fechar
                </Button>
                {selectedWorker.status === 'available' && (
                  <Button onClick={() => setShowAllocateModal(true)}>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Alocar
                  </Button>
                )}
              </div>
            </div>
          </Modal>
        )}

        {/* Allocate Modal */}
        <Modal
          isOpen={showAllocateModal}
          onClose={() => {
            setShowAllocateModal(false);
            setSelectedWorker(null);
          }}
          title="Alocar Diarista"
          size="md"
        >
          <div className="space-y-4">
            {selectedWorker && (
              <div className="p-4 bg-bg-tertiary rounded-lg flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-medium text-text-primary">{selectedWorker.name}</p>
                  <p className="text-sm text-text-secondary">
                    Diária: {selectedWorker.dailyRate.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                </div>
              </div>
            )}
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data" type="date" />
              <Select
                value={newShift}
                onChange={(value) => setNewShift(value)}
                options={[
                  { value: '', label: 'Selecione o turno' },
                  { value: 'morning', label: 'Matutino' },
                  { value: 'afternoon', label: 'Vespertino' },
                  { value: 'night', label: 'Noturno' }
                ]}
                className="w-full"
              />
            </div>
            <Select
              value={newClient}
              onChange={(value) => setNewClient(value)}
              options={[
                { value: '', label: 'Selecione o cliente' },
                { value: '1', label: 'Condomínio Verde' },
                { value: '2', label: 'Edifício Comercial ABC' },
                { value: '3', label: 'Shopping Center' }
              ]}
              className="w-full"
            />
            <Input label="Posto/Função" placeholder="Ex: Portaria Principal" />
            <Input label="Observações" placeholder="Informações adicionais (opcional)" />
            <div className="flex justify-end gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAllocateModal(false);
                  setSelectedWorker(null);
                }}
              >
                Cancelar
              </Button>
              <Button>
                <CheckCircle className="h-4 w-4 mr-2" />
                Confirmar Alocação
              </Button>
            </div>
          </div>
        </Modal>

        {/* New Worker Modal */}
        <Modal
          isOpen={showNewWorkerModal}
          onClose={() => setShowNewWorkerModal(false)}
          title="Novo Diarista"
          size="md"
        >
          <div className="space-y-4">
            <Input label="Nome Completo" placeholder="Nome do diarista" />
            <div className="grid grid-cols-2 gap-4">
              <Input label="CPF" placeholder="000.000.000-00" />
              <Input label="Telefone" placeholder="(00) 00000-0000" />
            </div>
            <Input label="Valor da Diária" type="number" placeholder="0,00" />
            <div>
              <p className="text-sm font-medium text-text-primary mb-2">Habilidades</p>
              <div className="flex flex-wrap gap-2">
                {['Limpeza', 'Segurança', 'Recepção', 'Manutenção', 'Cozinha'].map((skill) => (
                  <Badge key={skill} variant="outline" className="cursor-pointer hover:bg-bg-tertiary">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewWorkerModal(false)}>
                Cancelar
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Cadastrar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
