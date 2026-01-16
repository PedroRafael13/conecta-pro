'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Download,
  Calendar,
  Clock,
  Users,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  TrendingUp,
  BarChart2,
  PieChart as PieIcon,
  FileText,
  Printer,
  Mail,
  Eye,
  User,
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
  LineChart,
  Line,
} from 'recharts';

// Types
interface AttendanceReport {
  id: string;
  employeeName: string;
  department: string;
  month: string;
  workDays: number;
  presentDays: number;
  absences: number;
  lateArrivals: number;
  earlyDepartures: number;
  overtimeHours: number;
  attendanceRate: number;
}

// Mock Data
const reports: AttendanceReport[] = [
  { id: '1', employeeName: 'Ana Costa', department: 'Comercial', month: 'Janeiro 2026', workDays: 22, presentDays: 21, absences: 1, lateArrivals: 2, earlyDepartures: 0, overtimeHours: 12, attendanceRate: 95.5 },
  { id: '2', employeeName: 'Roberto Silva', department: 'TI', month: 'Janeiro 2026', workDays: 22, presentDays: 22, absences: 0, lateArrivals: 1, earlyDepartures: 0, overtimeHours: 18, attendanceRate: 100 },
  { id: '3', employeeName: 'Pedro Santos', department: 'Operacional', month: 'Janeiro 2026', workDays: 22, presentDays: 20, absences: 2, lateArrivals: 3, earlyDepartures: 1, overtimeHours: 8, attendanceRate: 90.9 },
  { id: '4', employeeName: 'Maria Oliveira', department: 'RH', month: 'Janeiro 2026', workDays: 22, presentDays: 21, absences: 1, lateArrivals: 0, earlyDepartures: 0, overtimeHours: 4, attendanceRate: 95.5 },
  { id: '5', employeeName: 'Carlos Lima', department: 'Financeiro', month: 'Janeiro 2026', workDays: 22, presentDays: 22, absences: 0, lateArrivals: 0, earlyDepartures: 0, overtimeHours: 6, attendanceRate: 100 },
];

const attendanceTrend = [
  { month: 'Set', rate: 94.5 },
  { month: 'Out', rate: 95.2 },
  { month: 'Nov', rate: 93.8 },
  { month: 'Dez', rate: 91.5 },
  { month: 'Jan', rate: 96.3 },
];

const absenceTypes = [
  { name: 'Férias', value: 45, color: '#3B82F6' },
  { name: 'Médico', value: 25, color: '#EF4444' },
  { name: 'Pessoal', value: 15, color: '#F59E0B' },
  { name: 'Falta', value: 10, color: '#6B7280' },
  { name: 'Outros', value: 5, color: '#10B981' },
];

const departmentAttendance = [
  { dept: 'TI', rate: 98.5 },
  { dept: 'Financeiro', rate: 97.2 },
  { dept: 'RH', rate: 96.8 },
  { dept: 'Comercial', rate: 95.5 },
  { dept: 'Operacional', rate: 93.2 },
];

const tabs = [
  { id: 'individual', label: 'Individual' },
  { id: 'department', label: 'Por Departamento' },
  { id: 'trends', label: 'Tendências' },
];

const columns: Column<AttendanceReport>[] = [
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
    key: 'presentDays',
    header: 'Presença',
    render: (row) => (
      <div className="flex items-center gap-2">
        <CheckCircle2 className="w-4 h-4 text-success" />
        <span>{row.presentDays}/{row.workDays} dias</span>
      </div>
    ),
  },
  {
    key: 'absences',
    header: 'Faltas',
    render: (row) => (
      <Badge variant={row.absences > 2 ? 'danger' : row.absences > 0 ? 'warning' : 'success'}>
        {row.absences}
      </Badge>
    ),
  },
  {
    key: 'lateArrivals',
    header: 'Atrasos',
    render: (row) => (
      <Badge variant={row.lateArrivals > 3 ? 'danger' : row.lateArrivals > 0 ? 'warning' : 'success'}>
        {row.lateArrivals}
      </Badge>
    ),
  },
  {
    key: 'overtimeHours',
    header: 'Horas Extras',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-text-muted" />
        <span>{row.overtimeHours}h</span>
      </div>
    ),
  },
  {
    key: 'attendanceRate',
    header: 'Taxa de Presença',
    render: (row) => (
      <div className="flex items-center gap-2">
        <div className="w-16 h-2 bg-bg-secondary rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${row.attendanceRate >= 95 ? 'bg-success' : row.attendanceRate >= 90 ? 'bg-warning' : 'bg-danger'}`}
            style={{ width: `${row.attendanceRate}%` }}
          />
        </div>
        <span className={`font-medium ${row.attendanceRate >= 95 ? 'text-success' : row.attendanceRate >= 90 ? 'text-warning' : 'text-danger'}`}>
          {row.attendanceRate.toFixed(1)}%
        </span>
      </div>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Exportar">
          <Download className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const COLORS = ['#3B82F6', '#EF4444', '#F59E0B', '#6B7280', '#10B981'];

export function AttendanceReportsPage() {
  const [activeTab, setActiveTab] = useState('individual');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMonth, setSelectedMonth] = useState('2026-01');

  const filteredReports = reports.filter((report) =>
    report.employeeName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Stats
  const avgAttendance = reports.reduce((acc, r) => acc + r.attendanceRate, 0) / reports.length;
  const totalAbsences = reports.reduce((acc, r) => acc + r.absences, 0);
  const totalLateArrivals = reports.reduce((acc, r) => acc + r.lateArrivals, 0);
  const totalOvertime = reports.reduce((acc, r) => acc + r.overtimeHours, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Relatórios de Frequência
            </h1>
            <p className="text-text-secondary mt-1">
              Análise detalhada de presença e pontualidade
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              options={[
                { value: '2026-01', label: 'Janeiro 2026' },
                { value: '2025-12', label: 'Dezembro 2025' },
                { value: '2025-11', label: 'Novembro 2025' },
              ]}
              value={selectedMonth}
              onChange={(value) => setSelectedMonth(value)}
              className="w-40"
            />
            <Button variant="secondary" leftIcon={<Printer className="w-4 h-4" />}>
              Imprimir
            </Button>
            <Button variant="primary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Taxa Média de Presença" value={`${avgAttendance.toFixed(1)}%`} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Total de Faltas" value={totalAbsences} icon={<XCircle className="w-6 h-6" />} iconColor="danger" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Total de Atrasos" value={totalLateArrivals} icon={<AlertTriangle className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Horas Extras" value={`${totalOvertime}h`} icon={<Clock className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === 'individual' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input placeholder="Buscar colaborador..." leftIcon={<Search className="w-4 h-4" />} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
              <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>Filtros</Button>
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable columns={columns} data={filteredReports} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'department' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold">Taxa de Presença por Departamento</h3>
                </div>
              </CardHeader>
              <CardBody>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={departmentAttendance} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                      <XAxis type="number" domain={[80, 100]} stroke="var(--color-text-muted)" />
                      <YAxis type="category" dataKey="dept" stroke="var(--color-text-muted)" width={80} />
                      <Tooltip formatter={(value: number) => `${value}%`} />
                      <Bar dataKey="rate" fill="#10B981" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <PieIcon className="w-5 h-5 text-warning" />
                  <h3 className="font-semibold">Tipos de Ausência</h3>
                </div>
              </CardHeader>
              <CardBody>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={absenceTypes} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                        {absenceTypes.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap justify-center gap-4 mt-4">
                  {absenceTypes.map((item) => (
                    <div key={item.name} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm text-text-muted">{item.name}</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'trends' && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Evolução da Taxa de Presença</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={attendanceTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis domain={[85, 100]} stroke="var(--color-text-muted)" />
                    <Tooltip formatter={(value: number) => `${value}%`} />
                    <Line type="monotone" dataKey="rate" stroke="#10B981" strokeWidth={3} dot={{ fill: '#10B981', strokeWidth: 2 }} name="Taxa de Presença" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
