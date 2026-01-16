'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  User,
  Users,
  Palmtree,
  Briefcase,
  Heart,
  Baby,
  GraduationCap,
  Home,
  Download,
  Eye,
  MoreHorizontal,
  CalendarDays,
  TrendingUp,
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
  Textarea,
} from '@/design-system/components';
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
} from 'recharts';

// Types
interface LeaveRequest {
  id: string;
  employeeName: string;
  department: string;
  type: 'vacation' | 'sick' | 'maternity' | 'paternity' | 'study' | 'personal' | 'bereavement';
  startDate: string;
  endDate: string;
  totalDays: number;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  approver: string | null;
  reason: string;
  createdAt: string;
}

// Mock Data
const leaveRequests: LeaveRequest[] = [
  { id: '1', employeeName: 'Ana Costa', department: 'Comercial', type: 'vacation', startDate: '2026-02-01', endDate: '2026-02-15', totalDays: 15, status: 'approved', approver: 'Carlos Lima', reason: 'Férias anuais', createdAt: '2026-01-10' },
  { id: '2', employeeName: 'Roberto Silva', department: 'TI', type: 'sick', startDate: '2026-01-14', endDate: '2026-01-16', totalDays: 3, status: 'approved', approver: 'Maria Oliveira', reason: 'Atestado médico', createdAt: '2026-01-14' },
  { id: '3', employeeName: 'Pedro Santos', department: 'Operacional', type: 'personal', startDate: '2026-01-20', endDate: '2026-01-20', totalDays: 1, status: 'pending', approver: null, reason: 'Assuntos pessoais', createdAt: '2026-01-15' },
  { id: '4', employeeName: 'Maria Oliveira', department: 'RH', type: 'study', startDate: '2026-01-25', endDate: '2026-01-25', totalDays: 1, status: 'pending', approver: null, reason: 'Prova de pós-graduação', createdAt: '2026-01-15' },
  { id: '5', employeeName: 'Carlos Lima', department: 'Financeiro', type: 'bereavement', startDate: '2026-01-12', endDate: '2026-01-14', totalDays: 3, status: 'approved', approver: 'Ana Costa', reason: 'Falecimento familiar', createdAt: '2026-01-12' },
  { id: '6', employeeName: 'Julia Ferreira', department: 'Marketing', type: 'maternity', startDate: '2026-02-01', endDate: '2026-05-31', totalDays: 120, status: 'approved', approver: 'Roberto Silva', reason: 'Licença maternidade', createdAt: '2025-12-15' },
];

const leaveTypeDistribution = [
  { name: 'Férias', value: 45, color: '#3B82F6' },
  { name: 'Médico', value: 25, color: '#EF4444' },
  { name: 'Pessoal', value: 15, color: '#F59E0B' },
  { name: 'Estudo', value: 10, color: '#10B981' },
  { name: 'Outros', value: 5, color: '#6B7280' },
];

const monthlyLeaves = [
  { month: 'Set', days: 45 },
  { month: 'Out', days: 52 },
  { month: 'Nov', days: 38 },
  { month: 'Dez', days: 85 },
  { month: 'Jan', days: 62 },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'pending', label: 'Pendentes' },
  { id: 'approved', label: 'Aprovadas' },
  { id: 'rejected', label: 'Rejeitadas' },
];

const typeConfig = {
  vacation: { label: 'Férias', icon: Palmtree, color: 'primary' },
  sick: { label: 'Médico', icon: Heart, color: 'danger' },
  maternity: { label: 'Maternidade', icon: Baby, color: 'success' },
  paternity: { label: 'Paternidade', icon: Baby, color: 'info' },
  study: { label: 'Estudo', icon: GraduationCap, color: 'warning' },
  personal: { label: 'Pessoal', icon: Home, color: 'secondary' },
  bereavement: { label: 'Luto', icon: Heart, color: 'neutral' },
};

const statusColors = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  cancelled: 'secondary',
} as const;

const statusLabels = {
  pending: 'Pendente',
  approved: 'Aprovada',
  rejected: 'Rejeitada',
  cancelled: 'Cancelada',
};

const columns: Column<LeaveRequest>[] = [
  {
    key: 'employeeName',
    header: 'Colaborador',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.employeeName} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.employeeName}</p>
          <p className="text-xs text-text-muted">{row.department}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const config = typeConfig[row.type];
      const Icon = config.icon;
      return (
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-text-muted" />
          <Badge variant={config.color as any} size="sm">{config.label}</Badge>
        </div>
      );
    },
  },
  {
    key: 'startDate',
    header: 'Período',
    render: (row) => (
      <div>
        <p className="font-medium">{new Date(row.startDate).toLocaleDateString('pt-BR')} - {new Date(row.endDate).toLocaleDateString('pt-BR')}</p>
        <p className="text-xs text-text-muted">{row.totalDays} dia(s)</p>
      </div>
    ),
  },
  {
    key: 'reason',
    header: 'Motivo',
    render: (row) => (
      <p className="text-sm text-text-secondary line-clamp-1 max-w-xs">{row.reason}</p>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={statusColors[row.status]}>
        {statusLabels[row.status]}
      </Badge>
    ),
  },
  {
    key: 'approver',
    header: 'Aprovador',
    render: (row) => row.approver ? (
      <div className="flex items-center gap-2">
        <Avatar name={row.approver} size="xs" />
        <span className="text-sm">{row.approver}</span>
      </div>
    ) : <span className="text-text-muted">-</span>,
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'pending' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Aprovar">
              <CheckCircle2 className="w-4 h-4 text-success" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Rejeitar">
              <XCircle className="w-4 h-4 text-danger" />
            </Button>
          </>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const COLORS = ['#3B82F6', '#EF4444', '#F59E0B', '#10B981', '#6B7280'];

export function LeaveRequestsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const filteredRequests = leaveRequests.filter((request) => {
    const matchesSearch = request.employeeName.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && request.status === activeTab;
  });

  // Stats
  const totalRequests = leaveRequests.length;
  const pendingRequests = leaveRequests.filter(r => r.status === 'pending').length;
  const approvedDays = leaveRequests.filter(r => r.status === 'approved').reduce((acc, r) => acc + r.totalDays, 0);
  const onLeaveNow = leaveRequests.filter(r => {
    const today = new Date();
    const start = new Date(r.startDate);
    const end = new Date(r.endDate);
    return r.status === 'approved' && today >= start && today <= end;
  }).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Solicitações de Ausência
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie férias, licenças e ausências dos colaboradores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<CalendarDays className="w-4 h-4" />}>
              Calendário
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Nova Solicitação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Solicitações" value={totalRequests} icon={<Calendar className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Pendentes" value={pendingRequests} icon={<Clock className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Dias Aprovados" value={approvedDays} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Ausentes Hoje" value={onLeaveNow} icon={<Users className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Distribuição por Tipo</h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={leaveTypeDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {leaveTypeDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {leaveTypeDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-text-muted">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Dias de Ausência por Mês</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyLeaves}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="days" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Dias" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex items-center gap-3">
            <Input placeholder="Buscar colaborador..." leftIcon={<Search className="w-4 h-4" />} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
            <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>Filtros</Button>
          </div>
        </div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable columns={columns} data={filteredRequests} keyExtractor={(row) => row.id} />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Nova Solicitação de Ausência" size="md" footer={<><Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>Cancelar</Button><Button variant="primary">Solicitar</Button></>}>
          <div className="space-y-4">
            <Select label="Colaborador" options={[{ value: '1', label: 'Ana Costa' }, { value: '2', label: 'Roberto Silva' }]} value="" onChange={() => {}} placeholder="Selecione..." />
            <Select label="Tipo de Ausência" options={Object.entries(typeConfig).map(([k, v]) => ({ value: k, label: v.label }))} value="" onChange={() => {}} placeholder="Selecione..." />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data Início" type="date" />
              <Input label="Data Fim" type="date" />
            </div>
            <Textarea label="Motivo" placeholder="Descreva o motivo da ausência..." rows={3} required />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
