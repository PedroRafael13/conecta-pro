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
  Clock,
  Plus,
  Search,
  Filter,
  Download,
  Edit,
  Trash2,
  Eye,
  Users,
  Calendar,
  Sun,
  Moon,
  Sunrise,
  Sunset,
  Copy,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import {
  BarChart,
  Bar,
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
interface Shift {
  id: string;
  name: string;
  code: string;
  type: 'morning' | 'afternoon' | 'night' | 'custom';
  startTime: string;
  endTime: string;
  breakStart: string;
  breakEnd: string;
  totalHours: number;
  employees: number;
  status: 'active' | 'inactive';
  description: string;
}

interface ShiftAllocation {
  id: string;
  shiftId: string;
  shiftName: string;
  employeeName: string;
  date: string;
  status: 'scheduled' | 'in-progress' | 'completed' | 'absent';
}

// Mock data
const mockShifts: Shift[] = [
  {
    id: '1',
    name: 'Turno Matutino',
    code: 'TM-01',
    type: 'morning',
    startTime: '06:00',
    endTime: '14:00',
    breakStart: '10:00',
    breakEnd: '11:00',
    totalHours: 7,
    employees: 156,
    status: 'active',
    description: 'Turno principal da manhã'
  },
  {
    id: '2',
    name: 'Turno Vespertino',
    code: 'TV-01',
    type: 'afternoon',
    startTime: '14:00',
    endTime: '22:00',
    breakStart: '18:00',
    breakEnd: '19:00',
    totalHours: 7,
    employees: 134,
    status: 'active',
    description: 'Turno da tarde'
  },
  {
    id: '3',
    name: 'Turno Noturno',
    code: 'TN-01',
    type: 'night',
    startTime: '22:00',
    endTime: '06:00',
    breakStart: '02:00',
    breakEnd: '03:00',
    totalHours: 7,
    employees: 89,
    status: 'active',
    description: 'Turno noturno com adicional'
  },
  {
    id: '4',
    name: 'Administrativo',
    code: 'ADM-01',
    type: 'custom',
    startTime: '08:00',
    endTime: '17:00',
    breakStart: '12:00',
    breakEnd: '13:00',
    totalHours: 8,
    employees: 77,
    status: 'active',
    description: 'Turno administrativo padrão'
  }
];

const mockAllocations: ShiftAllocation[] = [
  { id: '1', shiftId: '1', shiftName: 'Turno Matutino', employeeName: 'João Silva', date: '2026-01-16', status: 'in-progress' },
  { id: '2', shiftId: '1', shiftName: 'Turno Matutino', employeeName: 'Maria Santos', date: '2026-01-16', status: 'in-progress' },
  { id: '3', shiftId: '2', shiftName: 'Turno Vespertino', employeeName: 'Pedro Lima', date: '2026-01-16', status: 'scheduled' },
  { id: '4', shiftId: '3', shiftName: 'Turno Noturno', employeeName: 'Ana Costa', date: '2026-01-16', status: 'scheduled' },
  { id: '5', shiftId: '1', shiftName: 'Turno Matutino', employeeName: 'Carlos Souza', date: '2026-01-15', status: 'completed' }
];

// Chart data
const employeesByShift = [
  { name: 'Matutino', value: 156, color: '#f59e0b' },
  { name: 'Vespertino', value: 134, color: '#6366f1' },
  { name: 'Noturno', value: 89, color: '#8b5cf6' },
  { name: 'Admin', value: 77, color: '#10b981' }
];

const weeklyDistribution = [
  { day: 'Seg', morning: 150, afternoon: 130, night: 85 },
  { day: 'Ter', morning: 155, afternoon: 132, night: 88 },
  { day: 'Qua', morning: 152, afternoon: 135, night: 87 },
  { day: 'Qui', morning: 158, afternoon: 128, night: 89 },
  { day: 'Sex', morning: 148, afternoon: 138, night: 82 },
  { day: 'Sáb', morning: 80, afternoon: 75, night: 45 },
  { day: 'Dom', morning: 60, afternoon: 55, night: 40 }
];

export function ShiftsPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [showNewShiftModal, setShowNewShiftModal] = useState(false);
  const [selectedShift, setSelectedShift] = useState<Shift | null>(null);

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Clock className="h-4 w-4" /> },
    { value: 'shifts', label: 'Turnos', icon: <Calendar className="h-4 w-4" /> },
    { value: 'allocations', label: 'Alocações', icon: <Users className="h-4 w-4" /> }
  ];

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'morning': return <Sunrise className="h-4 w-4 text-warning" />;
      case 'afternoon': return <Sun className="h-4 w-4 text-primary" />;
      case 'night': return <Moon className="h-4 w-4 text-info" />;
      default: return <Clock className="h-4 w-4 text-text-secondary" />;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'morning': return <Badge variant="warning">Matutino</Badge>;
      case 'afternoon': return <Badge variant="primary">Vespertino</Badge>;
      case 'night': return <Badge variant="info">Noturno</Badge>;
      default: return <Badge variant="neutral">Customizado</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <Badge variant="success">Ativo</Badge>;
      case 'inactive': return <Badge variant="neutral">Inativo</Badge>;
      case 'scheduled': return <Badge variant="info">Agendado</Badge>;
      case 'in-progress': return <Badge variant="warning">Em Andamento</Badge>;
      case 'completed': return <Badge variant="success">Concluído</Badge>;
      case 'absent': return <Badge variant="danger">Ausente</Badge>;
      default: return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const shiftColumns: Column<Shift>[] = [
    {
      key: 'name',
      header: 'Turno',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-bg-tertiary flex items-center justify-center">
            {getTypeIcon(row.type)}
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary font-mono">{row.code}</p>
          </div>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => getTypeBadge(row.type)
    },
    {
      key: 'time',
      header: 'Horário',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.startTime} - {row.endTime}</p>
          <p className="text-sm text-text-secondary">Intervalo: {row.breakStart} - {row.breakEnd}</p>
        </div>
      )
    },
    {
      key: 'totalHours',
      header: 'Carga Horária',
      render: (row) => (
        <span className="text-text-secondary">{row.totalHours}h/dia</span>
      )
    },
    {
      key: 'employees',
      header: 'Colaboradores',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-text-muted" />
          <span className="text-text-primary">{row.employees}</span>
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
          <Button variant="ghost" size="sm" onClick={() => setSelectedShift(row)}>
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Copy className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const allocationColumns: Column<ShiftAllocation>[] = [
    {
      key: 'employeeName',
      header: 'Colaborador',
      render: (row) => (
        <span className="font-medium text-text-primary">{row.employeeName}</span>
      )
    },
    {
      key: 'shiftName',
      header: 'Turno',
      render: (row) => (
        <span className="text-text-secondary">{row.shiftName}</span>
      )
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.date).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    }
  ];

  const filteredShifts = mockShifts.filter(shift => {
    const matchesSearch = shift.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      shift.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || shift.type === filterType;
    return matchesSearch && matchesType;
  });

  const totalEmployees = mockShifts.reduce((sum, s) => sum + s.employees, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Turnos
            </h1>
            <p className="text-text-secondary mt-1">
              Configuração e gestão de turnos de trabalho
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewShiftModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Turno
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Turnos Ativos"
            value={mockShifts.filter(s => s.status === 'active').length.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Colaboradores Alocados"
            value={totalEmployees.toString()}
            icon={<Users className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Em Serviço Agora"
            value="324"
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Cobertura"
            value="98%"
            icon={<Calendar className="h-5 w-5" />}
            iconColor="success"
            change={2}
            changeLabel="vs. semana anterior"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Employees by Shift */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Distribuição por Turno
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={employeesByShift}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {employeesByShift.map((entry, index) => (
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

            {/* Weekly Distribution */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Distribuição Semanal
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weeklyDistribution}>
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
                    <Bar dataKey="morning" name="Matutino" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="afternoon" name="Vespertino" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="night" name="Noturno" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Active Shifts */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Turnos em Andamento
              </h3>
              <div className="space-y-4">
                {mockShifts.filter(s => s.status === 'active').slice(0, 3).map((shift) => (
                  <div key={shift.id} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                        {getTypeIcon(shift.type)}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{shift.name}</p>
                        <p className="text-sm text-text-secondary">{shift.startTime} - {shift.endTime}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-text-primary">{shift.employees}</p>
                      <p className="text-sm text-text-secondary">colaboradores</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Recent Allocations */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Alocações Recentes
              </h3>
              <div className="space-y-4">
                {mockAllocations.slice(0, 4).map((allocation) => (
                  <div key={allocation.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-bg-tertiary flex items-center justify-center">
                        <Users className="h-5 w-5 text-text-muted" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{allocation.employeeName}</p>
                        <p className="text-sm text-text-secondary">{allocation.shiftName}</p>
                      </div>
                    </div>
                    {getStatusBadge(allocation.status)}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Shifts Tab */}
        {activeTab === 'shifts' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar turno..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterType}
                onChange={setFilterType}
                options={[
                  { value: 'all', label: 'Todos os tipos' },
                  { value: 'morning', label: 'Matutino' },
                  { value: 'afternoon', label: 'Vespertino' },
                  { value: 'night', label: 'Noturno' },
                  { value: 'custom', label: 'Customizado' }
                ]}
                className="w-40"
              />
            </div>
            <DataTable
              columns={shiftColumns}
              data={filteredShifts}
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
                  placeholder="Buscar colaborador..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Input type="date" className="w-40" />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={allocationColumns}
              data={mockAllocations}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Shift Detail Modal */}
        {selectedShift && (
          <Modal
            isOpen={!!selectedShift}
            onClose={() => setSelectedShift(null)}
            title="Detalhes do Turno"
            size="md"
          >
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-xl bg-primary/10 flex items-center justify-center">
                  {getTypeIcon(selectedShift.type)}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">
                    {selectedShift.name}
                  </h3>
                  <p className="text-text-secondary font-mono">{selectedShift.code}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {getTypeBadge(selectedShift.type)}
                    {getStatusBadge(selectedShift.status)}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Horário</p>
                  <p className="text-lg font-bold text-text-primary">
                    {selectedShift.startTime} - {selectedShift.endTime}
                  </p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Intervalo</p>
                  <p className="text-lg font-bold text-text-primary">
                    {selectedShift.breakStart} - {selectedShift.breakEnd}
                  </p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Carga Horária</p>
                  <p className="text-lg font-bold text-text-primary">{selectedShift.totalHours}h/dia</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary mb-1">Colaboradores</p>
                  <p className="text-lg font-bold text-text-primary">{selectedShift.employees}</p>
                </div>
              </div>

              <div>
                <p className="text-sm text-text-secondary mb-1">Descrição</p>
                <p className="text-text-primary">{selectedShift.description}</p>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedShift(null)}>
                  Fechar
                </Button>
                <Button>
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
              </div>
            </div>
          </Modal>
        )}

        {/* New Shift Modal */}
        <Modal
          isOpen={showNewShiftModal}
          onClose={() => setShowNewShiftModal(false)}
          title="Novo Turno"
          size="md"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Nome do Turno" placeholder="Ex: Turno Matutino" />
              <Input label="Código" placeholder="Ex: TM-01" />
            </div>
            <Select
              value=""
              onChange={() => {}}
              options={[
                { value: '', label: 'Selecione o tipo' },
                { value: 'morning', label: 'Matutino' },
                { value: 'afternoon', label: 'Vespertino' },
                { value: 'night', label: 'Noturno' },
                { value: 'custom', label: 'Customizado' }
              ]}
              className="w-full"
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Hora Início" type="time" />
              <Input label="Hora Fim" type="time" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Início Intervalo" type="time" />
              <Input label="Fim Intervalo" type="time" />
            </div>
            <Input label="Descrição" placeholder="Descrição do turno" />
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewShiftModal(false)}>
                Cancelar
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Criar Turno
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
