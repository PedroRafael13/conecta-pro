'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Calendar,
  User,
  DollarSign,
  TrendingUp,
  Download,
  Eye,
  Edit2,
  MoreHorizontal,
  Sun,
  Moon,
  Sunrise,
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
  LineChart,
  Line,
} from 'recharts';

// Types
interface OvertimeRecord {
  id: string;
  employeeName: string;
  department: string;
  date: string;
  startTime: string;
  endTime: string;
  totalHours: number;
  type: 'normal' | 'night' | 'holiday' | 'sunday';
  multiplier: number;
  calculatedValue: number;
  status: 'pending' | 'approved' | 'rejected';
  approver: string | null;
  justification: string;
}

// Mock Data
const overtimeRecords: OvertimeRecord[] = [
  { id: '1', employeeName: 'Ana Costa', department: 'Comercial', date: '2026-01-15', startTime: '18:00', endTime: '22:00', totalHours: 4, type: 'normal', multiplier: 1.5, calculatedValue: 180, status: 'approved', approver: 'Carlos Lima', justification: 'Fechamento de proposta urgente' },
  { id: '2', employeeName: 'Roberto Silva', department: 'TI', date: '2026-01-14', startTime: '22:00', endTime: '02:00', totalHours: 4, type: 'night', multiplier: 2.0, calculatedValue: 320, status: 'approved', approver: 'Maria Oliveira', justification: 'Deploy de sistema crítico' },
  { id: '3', employeeName: 'Pedro Santos', department: 'Operacional', date: '2026-01-13', startTime: '08:00', endTime: '16:00', totalHours: 8, type: 'sunday', multiplier: 2.0, calculatedValue: 480, status: 'pending', approver: null, justification: 'Plantão de domingo' },
  { id: '4', employeeName: 'Maria Oliveira', department: 'RH', date: '2026-01-12', startTime: '18:00', endTime: '20:00', totalHours: 2, type: 'normal', multiplier: 1.5, calculatedValue: 90, status: 'rejected', approver: 'Carlos Lima', justification: 'Reunião pós-expediente' },
  { id: '5', employeeName: 'Carlos Lima', department: 'Financeiro', date: '2026-01-11', startTime: '18:00', endTime: '23:00', totalHours: 5, type: 'normal', multiplier: 1.5, calculatedValue: 225, status: 'approved', approver: 'Ana Costa', justification: 'Fechamento mensal' },
];

const overtimeTrend = [
  { month: 'Set', hours: 320, value: 14500 },
  { month: 'Out', hours: 380, value: 17200 },
  { month: 'Nov', hours: 410, value: 18600 },
  { month: 'Dez', hours: 520, value: 24800 },
  { month: 'Jan', hours: 280, value: 12600 },
];

const departmentOvertime = [
  { dept: 'TI', hours: 120 },
  { dept: 'Comercial', hours: 95 },
  { dept: 'Operacional', hours: 180 },
  { dept: 'Financeiro', hours: 65 },
  { dept: 'RH', hours: 40 },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'pending', label: 'Pendentes' },
  { id: 'approved', label: 'Aprovadas' },
  { id: 'rejected', label: 'Rejeitadas' },
];

const typeConfig = {
  normal: { label: 'Normal', icon: Sun, color: 'info', multiplier: '50%' },
  night: { label: 'Noturna', icon: Moon, color: 'warning', multiplier: '100%' },
  holiday: { label: 'Feriado', icon: Calendar, color: 'danger', multiplier: '100%' },
  sunday: { label: 'Domingo', icon: Sunrise, color: 'success', multiplier: '100%' },
};

const statusColors = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
} as const;

const statusLabels = {
  pending: 'Pendente',
  approved: 'Aprovada',
  rejected: 'Rejeitada',
};

const columns: Column<OvertimeRecord>[] = [
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
    key: 'date',
    header: 'Data',
    render: (row) => (
      <div>
        <p className="font-medium">{new Date(row.date).toLocaleDateString('pt-BR')}</p>
        <p className="text-xs text-text-muted">{row.startTime} - {row.endTime}</p>
      </div>
    ),
  },
  {
    key: 'totalHours',
    header: 'Horas',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-text-muted" />
        <span className="font-medium">{row.totalHours}h</span>
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
    key: 'calculatedValue',
    header: 'Valor',
    render: (row) => (
      <span className="font-medium text-success">
        {row.calculatedValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
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

export function OvertimePage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const filteredRecords = overtimeRecords.filter((record) => {
    const matchesSearch = record.employeeName.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && record.status === activeTab;
  });

  // Stats
  const totalHours = overtimeRecords.reduce((acc, r) => acc + r.totalHours, 0);
  const totalValue = overtimeRecords.filter(r => r.status === 'approved').reduce((acc, r) => acc + r.calculatedValue, 0);
  const pendingCount = overtimeRecords.filter(r => r.status === 'pending').length;
  const avgHoursPerEmployee = totalHours / new Set(overtimeRecords.map(r => r.employeeName)).size;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Horas Extras
            </h1>
            <p className="text-text-secondary mt-1">
              Controle e aprovação de horas extras dos colaboradores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Registrar Hora Extra
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Horas" value={`${totalHours}h`} icon={<Clock className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Valor Aprovado" value={totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} icon={<DollarSign className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Pendentes Aprovação" value={pendingCount} icon={<AlertTriangle className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Média por Colaborador" value={`${avgHoursPerEmployee.toFixed(1)}h`} icon={<User className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Evolução Mensal</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={overtimeTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis yAxisId="left" stroke="var(--color-text-muted)" />
                    <YAxis yAxisId="right" orientation="right" stroke="var(--color-text-muted)" tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                    <Tooltip />
                    <Line yAxisId="left" type="monotone" dataKey="hours" stroke="#3B82F6" strokeWidth={2} name="Horas" />
                    <Line yAxisId="right" type="monotone" dataKey="value" stroke="#10B981" strokeWidth={2} name="Valor" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="font-semibold">Horas por Departamento</h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={departmentOvertime} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis type="number" stroke="var(--color-text-muted)" />
                    <YAxis type="category" dataKey="dept" stroke="var(--color-text-muted)" width={80} />
                    <Tooltip />
                    <Bar dataKey="hours" fill="#F59E0B" radius={[0, 4, 4, 0]} />
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
              <DataTable columns={columns} data={filteredRecords} keyExtractor={(row) => row.id} />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Registrar Hora Extra" size="md" footer={<><Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>Cancelar</Button><Button variant="primary">Registrar</Button></>}>
          <div className="space-y-4">
            <Select label="Colaborador" options={[{ value: '1', label: 'Ana Costa' }, { value: '2', label: 'Roberto Silva' }]} value="" onChange={() => {}} placeholder="Selecione..." />
            <Input label="Data" type="date" />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Hora Início" type="time" />
              <Input label="Hora Fim" type="time" />
            </div>
            <Select label="Tipo" options={Object.entries(typeConfig).map(([k, v]) => ({ value: k, label: `${v.label} (+${v.multiplier})` }))} value="" onChange={() => {}} placeholder="Selecione..." />
            <Textarea label="Justificativa" placeholder="Descreva o motivo da hora extra..." rows={3} required />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
