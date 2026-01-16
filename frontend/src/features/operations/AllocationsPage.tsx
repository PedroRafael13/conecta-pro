'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Search,
  Plus,
  Download,
  Calendar,
  Building2,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  MapPin,
  UserPlus,
  UserMinus,
  ArrowRightLeft,
  Eye,
  Edit,
  MoreVertical,
  Filter,
  RefreshCw,
  UserCheck,
  FileText,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
  Avatar,
} from '@/design-system/components';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

// Types
interface Allocation {
  id: string;
  employeeId: string;
  employeeName: string;
  employeeRole: string;
  postId: string;
  postName: string;
  clientName: string;
  shiftId: string;
  shiftName: string;
  startDate: string;
  endDate: string | null;
  status: 'active' | 'pending' | 'ended' | 'suspended';
  allocationType: 'permanent' | 'temporary' | 'replacement';
}

interface Substitution {
  id: string;
  originalEmployee: string;
  substituteEmployee: string;
  postName: string;
  clientName: string;
  reason: 'vacation' | 'sick_leave' | 'absence' | 'training' | 'other';
  startDate: string;
  endDate: string;
  status: 'scheduled' | 'active' | 'completed' | 'cancelled';
}

interface Vacancy {
  id: string;
  postName: string;
  clientName: string;
  shiftName: string;
  requiredDate: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  reason: string;
  status: 'open' | 'in_progress' | 'filled';
}

// Mock Data
const allocationDistribution = [
  { name: 'Vigilantes', value: 245, color: '#6366f1' },
  { name: 'Porteiros', value: 68, color: '#8b5cf6' },
  { name: 'Supervisores', value: 22, color: '#3b82f6' },
  { name: 'Rondistas', value: 12, color: '#10b981' },
];

const allocations: Allocation[] = [
  {
    id: '1',
    employeeId: 'EMP001',
    employeeName: 'Roberto Silva',
    employeeRole: 'Vigilante',
    postId: 'POST001',
    postName: 'Portaria Principal',
    clientName: 'Shopping Center Norte',
    shiftId: 'SHIFT001',
    shiftName: '12x36 Diurno',
    startDate: '2025-06-15',
    endDate: null,
    status: 'active',
    allocationType: 'permanent',
  },
  {
    id: '2',
    employeeId: 'EMP002',
    employeeName: 'Maria Santos',
    employeeRole: 'Vigilante',
    postId: 'POST002',
    postName: 'CFTV',
    clientName: 'Hospital São Lucas',
    shiftId: 'SHIFT002',
    shiftName: '12x36 Noturno',
    startDate: '2025-08-01',
    endDate: null,
    status: 'active',
    allocationType: 'permanent',
  },
  {
    id: '3',
    employeeId: 'EMP003',
    employeeName: 'Carlos Eduardo',
    employeeRole: 'Supervisor',
    postId: 'POST003',
    postName: 'Supervisão Geral',
    clientName: 'Tech Park Empresarial',
    shiftId: 'SHIFT003',
    shiftName: 'Comercial',
    startDate: '2026-01-10',
    endDate: null,
    status: 'pending',
    allocationType: 'permanent',
  },
  {
    id: '4',
    employeeId: 'EMP004',
    employeeName: 'Ana Paula',
    employeeRole: 'Vigilante',
    postId: 'POST001',
    postName: 'Portaria Principal',
    clientName: 'Shopping Center Norte',
    shiftId: 'SHIFT002',
    shiftName: '12x36 Noturno',
    startDate: '2026-01-05',
    endDate: '2026-01-20',
    status: 'active',
    allocationType: 'replacement',
  },
  {
    id: '5',
    employeeId: 'EMP005',
    employeeName: 'João Pereira',
    employeeRole: 'Porteiro',
    postId: 'POST004',
    postName: 'Recepção',
    clientName: 'Condomínio Residencial',
    shiftId: 'SHIFT001',
    shiftName: '12x36 Diurno',
    startDate: '2025-09-01',
    endDate: '2025-12-31',
    status: 'ended',
    allocationType: 'temporary',
  },
];

const substitutions: Substitution[] = [
  {
    id: '1',
    originalEmployee: 'Pedro Almeida',
    substituteEmployee: 'Ana Paula',
    postName: 'Portaria Principal',
    clientName: 'Shopping Center Norte',
    reason: 'vacation',
    startDate: '2026-01-05',
    endDate: '2026-01-20',
    status: 'active',
  },
  {
    id: '2',
    originalEmployee: 'Marcos Lima',
    substituteEmployee: 'Carlos Eduardo',
    postName: 'CFTV',
    clientName: 'Hospital São Lucas',
    reason: 'training',
    startDate: '2026-01-18',
    endDate: '2026-01-22',
    status: 'scheduled',
  },
  {
    id: '3',
    originalEmployee: 'Juliana Costa',
    substituteEmployee: 'Roberto Silva',
    postName: 'Ronda Externa',
    clientName: 'Tech Park Empresarial',
    reason: 'sick_leave',
    startDate: '2026-01-10',
    endDate: '2026-01-14',
    status: 'completed',
  },
];

const vacancies: Vacancy[] = [
  {
    id: '1',
    postName: 'Vigilante Noturno',
    clientName: 'Shopping Center Norte',
    shiftName: '12x36 Noturno',
    requiredDate: '2026-01-20',
    priority: 'high',
    reason: 'Nova demanda do cliente',
    status: 'open',
  },
  {
    id: '2',
    postName: 'Porteiro Diurno',
    clientName: 'Condomínio Residencial',
    shiftName: '12x36 Diurno',
    requiredDate: '2026-02-01',
    priority: 'medium',
    reason: 'Desligamento de colaborador',
    status: 'in_progress',
  },
  {
    id: '3',
    postName: 'Supervisor',
    clientName: 'Hospital São Lucas',
    shiftName: 'Comercial',
    requiredDate: '2026-01-25',
    priority: 'critical',
    reason: 'Expansão do contrato',
    status: 'open',
  },
];

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  pending: { label: 'Pendente', color: 'warning' as const },
  ended: { label: 'Encerrado', color: 'neutral' as const },
  suspended: { label: 'Suspenso', color: 'danger' as const },
};

const allocationTypeConfig = {
  permanent: { label: 'Efetivo', color: 'primary' as const },
  temporary: { label: 'Temporário', color: 'info' as const },
  replacement: { label: 'Substituição', color: 'warning' as const },
};

const substitutionStatusConfig = {
  scheduled: { label: 'Agendada', color: 'info' as const },
  active: { label: 'Em Andamento', color: 'success' as const },
  completed: { label: 'Concluída', color: 'neutral' as const },
  cancelled: { label: 'Cancelada', color: 'danger' as const },
};

const reasonLabels = {
  vacation: 'Férias',
  sick_leave: 'Atestado',
  absence: 'Falta',
  training: 'Treinamento',
  other: 'Outro',
};

const priorityConfig = {
  low: { label: 'Baixa', color: 'neutral' as const },
  medium: { label: 'Média', color: 'info' as const },
  high: { label: 'Alta', color: 'warning' as const },
  critical: { label: 'Crítica', color: 'danger' as const },
};

const vacancyStatusConfig = {
  open: { label: 'Aberta', color: 'danger' as const },
  in_progress: { label: 'Em Andamento', color: 'warning' as const },
  filled: { label: 'Preenchida', color: 'success' as const },
};

const allocationColumns: Column<Allocation>[] = [
  {
    key: 'employeeName',
    header: 'Funcionário',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.employeeName} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.employeeName}</p>
          <p className="text-xs text-text-muted">{row.employeeId} • {row.employeeRole}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'postName',
    header: 'Posto',
    render: (row) => (
      <div>
        <p className="text-text-primary">{row.postName}</p>
        <p className="text-xs text-text-muted">{row.clientName}</p>
      </div>
    ),
  },
  {
    key: 'shiftName',
    header: 'Turno',
    render: (row) => <span className="text-sm">{row.shiftName}</span>,
  },
  {
    key: 'allocationType',
    header: 'Tipo',
    render: (row) => {
      const config = allocationTypeConfig[row.allocationType];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'startDate',
    header: 'Período',
    render: (row) => (
      <div className="text-sm">
        <p>{new Date(row.startDate).toLocaleDateString('pt-BR')}</p>
        {row.endDate && (
          <p className="text-text-muted">até {new Date(row.endDate).toLocaleDateString('pt-BR')}</p>
        )}
      </div>
    ),
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
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Mais">
          <MoreVertical className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const substitutionColumns: Column<Substitution>[] = [
  {
    key: 'originalEmployee',
    header: 'Titular',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.originalEmployee} size="sm" />
        <span className="font-medium text-text-primary">{row.originalEmployee}</span>
      </div>
    ),
  },
  {
    key: 'substituteEmployee',
    header: 'Substituto',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.substituteEmployee} size="sm" />
        <span className="text-text-primary">{row.substituteEmployee}</span>
      </div>
    ),
  },
  {
    key: 'postName',
    header: 'Posto',
    render: (row) => (
      <div>
        <p className="text-text-primary">{row.postName}</p>
        <p className="text-xs text-text-muted">{row.clientName}</p>
      </div>
    ),
  },
  {
    key: 'reason',
    header: 'Motivo',
    render: (row) => <Badge variant="info">{reasonLabels[row.reason]}</Badge>,
  },
  {
    key: 'startDate',
    header: 'Período',
    render: (row) => (
      <div className="text-sm">
        <p>{new Date(row.startDate).toLocaleDateString('pt-BR')}</p>
        <p className="text-text-muted">até {new Date(row.endDate).toLocaleDateString('pt-BR')}</p>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = substitutionStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
];

const vacancyColumns: Column<Vacancy>[] = [
  {
    key: 'postName',
    header: 'Vaga',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.postName}</p>
        <p className="text-xs text-text-muted">{row.clientName}</p>
      </div>
    ),
  },
  {
    key: 'shiftName',
    header: 'Turno',
    render: (row) => <span className="text-sm">{row.shiftName}</span>,
  },
  {
    key: 'requiredDate',
    header: 'Data Necessária',
    render: (row) => (
      <span className="text-sm">{new Date(row.requiredDate).toLocaleDateString('pt-BR')}</span>
    ),
  },
  {
    key: 'reason',
    header: 'Motivo',
    render: (row) => <span className="text-sm text-text-secondary">{row.reason}</span>,
  },
  {
    key: 'priority',
    header: 'Prioridade',
    render: (row) => {
      const config = priorityConfig[row.priority];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = vacancyStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        {row.status === 'open' && (
          <Button variant="primary" size="sm" leftIcon={<UserPlus className="w-3 h-3" />}>
            Alocar
          </Button>
        )}
      </div>
    ),
  },
];

export function AllocationsPage() {
  const [selectedTab, setSelectedTab] = useState('allocations');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Stats
  const totalAllocations = allocations.filter(a => a.status === 'active').length;
  const activeSubstitutions = substitutions.filter(s => s.status === 'active' || s.status === 'scheduled').length;
  const openVacancies = vacancies.filter(v => v.status === 'open').length;
  const pendingAllocations = allocations.filter(a => a.status === 'pending').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Alocações
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de alocações, substituições e vagas
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Alocação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Alocações Ativas"
              value={totalAllocations}
              icon={<UserCheck className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Substituições"
              value={activeSubstitutions}
              icon={<ArrowRightLeft className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Vagas Abertas"
              value={openVacancies}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Pendentes"
              value={pendingAllocations}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Distribution Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Distribuição por Função</h3>
              </CardHeader>
              <CardBody>
                <div className="h-48 flex items-center">
                  <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie
                        data={allocationDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={60}
                        dataKey="value"
                        stroke="none"
                      >
                        {allocationDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex-1 space-y-2">
                    {allocationDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-text-secondary">{item.name}</span>
                        </div>
                        <span className="text-sm font-medium">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          {/* Quick Actions */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="lg:col-span-2">
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Ações Rápidas</h3>
              </CardHeader>
              <CardBody>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button variant="secondary" className="flex-col h-24 gap-2">
                    <UserPlus className="w-6 h-6" />
                    <span>Nova Alocação</span>
                  </Button>
                  <Button variant="secondary" className="flex-col h-24 gap-2">
                    <ArrowRightLeft className="w-6 h-6" />
                    <span>Substituição</span>
                  </Button>
                  <Button variant="secondary" className="flex-col h-24 gap-2">
                    <UserMinus className="w-6 h-6" />
                    <span>Encerrar</span>
                  </Button>
                  <Button variant="secondary" className="flex-col h-24 gap-2">
                    <FileText className="w-6 h-6" />
                    <span>Relatórios</span>
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Vacancy Alert */}
        {openVacancies > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card className="border-accent-danger/30 bg-accent-danger/5">
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent-danger/20 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-accent-danger" />
                    </div>
                    <div>
                      <h4 className="font-medium text-text-primary">Vagas em Aberto</h4>
                      <p className="text-sm text-text-secondary">
                        {openVacancies} {openVacancies === 1 ? 'vaga precisa' : 'vagas precisam'} ser preenchida(s)
                      </p>
                    </div>
                  </div>
                  <Button variant="danger" size="sm" onClick={() => setSelectedTab('vacancies')}>
                    Ver Vagas
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'allocations', label: 'Alocações' },
                { value: 'substitutions', label: 'Substituições' },
                { value: 'vacancies', label: 'Vagas' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Card>
            <CardBody className="border-b border-border-subtle">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Buscar..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                {selectedTab === 'allocations' && (
                  <>
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Clientes' },
                        { value: '1', label: 'Shopping Center Norte' },
                        { value: '2', label: 'Hospital São Lucas' },
                        { value: '3', label: 'Tech Park Empresarial' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-48"
                    />
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Status' },
                        { value: 'active', label: 'Ativos' },
                        { value: 'pending', label: 'Pendentes' },
                        { value: 'ended', label: 'Encerrados' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-40"
                    />
                  </>
                )}
                {selectedTab === 'vacancies' && (
                  <Select
                    options={[
                      { value: 'all', label: 'Todas Prioridades' },
                      { value: 'critical', label: 'Crítica' },
                      { value: 'high', label: 'Alta' },
                      { value: 'medium', label: 'Média' },
                      { value: 'low', label: 'Baixa' },
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-44"
                  />
                )}
              </div>
            </CardBody>
            <CardBody className="p-0">
              {selectedTab === 'allocations' ? (
                <DataTable
                  columns={allocationColumns}
                  data={allocations}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'substitutions' ? (
                <DataTable
                  columns={substitutionColumns}
                  data={substitutions}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <DataTable
                  columns={vacancyColumns}
                  data={vacancies}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Allocation Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Alocação"
          description="Aloque um funcionário a um posto"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar Alocação
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Funcionário"
              options={[
                { value: '1', label: 'Roberto Silva - Vigilante' },
                { value: '2', label: 'Maria Santos - Vigilante' },
                { value: '3', label: 'Carlos Eduardo - Supervisor' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o funcionário..."
            />
            <Select
              label="Cliente"
              options={[
                { value: '1', label: 'Shopping Center Norte' },
                { value: '2', label: 'Hospital São Lucas' },
                { value: '3', label: 'Tech Park Empresarial' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o cliente..."
            />
            <Select
              label="Posto"
              options={[
                { value: '1', label: 'Portaria Principal' },
                { value: '2', label: 'CFTV' },
                { value: '3', label: 'Ronda Externa' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o posto..."
            />
            <Select
              label="Turno"
              options={[
                { value: '1', label: '12x36 Diurno (06:00-18:00)' },
                { value: '2', label: '12x36 Noturno (18:00-06:00)' },
                { value: '3', label: 'Comercial (08:00-18:00)' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o turno..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data de Início" type="date" />
              <Input label="Data de Término (opcional)" type="date" />
            </div>
            <Select
              label="Tipo de Alocação"
              options={[
                { value: 'permanent', label: 'Efetivo' },
                { value: 'temporary', label: 'Temporário' },
                { value: 'replacement', label: 'Substituição' },
              ]}
              value="permanent"
              onChange={() => {}}
            />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
