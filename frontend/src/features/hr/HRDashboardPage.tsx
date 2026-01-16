'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  UserCheck,
  UserX,
  Clock,
  Calendar,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Building2,
  Briefcase,
  MapPin,
  Award,
  DollarSign,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
} from '@/design-system/components';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Mock Data
const employeesByDepartment = [
  { name: 'Segurança', value: 245, color: '#6366f1' },
  { name: 'Limpeza', value: 180, color: '#8b5cf6' },
  { name: 'Portaria', value: 85, color: '#ec4899' },
  { name: 'Manutenção', value: 45, color: '#14b8a6' },
  { name: 'Administrativo', value: 32, color: '#f59e0b' },
  { name: 'Outros', value: 18, color: '#64748b' },
];

const monthlyMetrics = [
  { month: 'Ago', admissoes: 12, demissoes: 5, turnover: 0.8 },
  { month: 'Set', admissoes: 8, demissoes: 7, turnover: 1.2 },
  { month: 'Out', admissoes: 15, demissoes: 4, turnover: 0.7 },
  { month: 'Nov', admissoes: 10, demissoes: 8, turnover: 1.4 },
  { month: 'Dez', admissoes: 6, demissoes: 12, turnover: 2.0 },
  { month: 'Jan', admissoes: 18, demissoes: 3, turnover: 0.5 },
];

interface RecentEmployee {
  id: string;
  name: string;
  department: string;
  position: string;
  startDate: string;
  status: 'active' | 'vacation' | 'leave' | 'terminated';
  client: string;
}

const recentEmployees: RecentEmployee[] = [
  {
    id: '1',
    name: 'Carlos Eduardo Silva',
    department: 'Segurança',
    position: 'Vigilante',
    startDate: '2026-01-15',
    status: 'active',
    client: 'Shopping Center Norte',
  },
  {
    id: '2',
    name: 'Maria Aparecida Santos',
    department: 'Limpeza',
    position: 'Auxiliar de Limpeza',
    startDate: '2026-01-14',
    status: 'active',
    client: 'Hospital São Lucas',
  },
  {
    id: '3',
    name: 'José Roberto Lima',
    department: 'Portaria',
    position: 'Porteiro',
    startDate: '2026-01-13',
    status: 'active',
    client: 'Condomínio Aurora',
  },
  {
    id: '4',
    name: 'Ana Paula Oliveira',
    department: 'Administrativo',
    position: 'Assistente RH',
    startDate: '2026-01-10',
    status: 'active',
    client: 'Sede Central',
  },
];

const upcomingEvents = [
  { type: 'vacation', employee: 'Ricardo Mendes', date: '2026-01-20', days: 30 },
  { type: 'birthday', employee: 'Fernanda Costa', date: '2026-01-18', days: 0 },
  { type: 'anniversary', employee: 'Paulo Souza', date: '2026-01-22', years: 5 },
  { type: 'return', employee: 'Lucia Ferreira', date: '2026-01-25', days: 0 },
];

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  vacation: { label: 'Férias', color: 'info' as const },
  leave: { label: 'Afastado', color: 'warning' as const },
  terminated: { label: 'Desligado', color: 'danger' as const },
};

const recentColumns: Column<RecentEmployee>[] = [
  {
    key: 'name',
    header: 'Funcionário',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.name} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.position}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'department',
    header: 'Departamento',
    render: (row) => <Badge variant="secondary">{row.department}</Badge>,
  },
  {
    key: 'client',
    header: 'Alocação',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Building2 className="w-4 h-4 text-text-muted" />
        <span className="text-sm text-text-secondary">{row.client}</span>
      </div>
    ),
  },
  {
    key: 'startDate',
    header: 'Admissão',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {new Date(row.startDate).toLocaleDateString('pt-BR')}
      </span>
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
];

export function HRDashboardPage() {
  const totalEmployees = 605;
  const activeEmployees = 580;
  const onVacation = 15;
  const onLeave = 10;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Recursos Humanos
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de pessoas e indicadores de RH
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary">
              Exportar Relatório
            </Button>
            <Button variant="primary">
              Novo Funcionário
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total Funcionários"
              value={totalEmployees}
              change={2.8}
              icon={<Users className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Ativos"
              value={activeEmployees}
              icon={<UserCheck className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Em Férias"
              value={onVacation}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Afastados"
              value={onLeave}
              icon={<UserX className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <StatCard
              title="Turnover"
              value="0.5%"
              change={-0.3}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-3 gap-6">
          {/* Admissions vs Terminations */}
          <Card className="col-span-2">
            <CardHeader
              title="Admissões e Desligamentos"
              subtitle="Últimos 6 meses"
            />
            <CardBody>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyMetrics}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                    />
                    <Legend />
                    <Bar dataKey="admissoes" name="Admissões" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="demissoes" name="Desligamentos" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Employees by Department */}
          <Card>
            <CardHeader title="Por Departamento" />
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={employeesByDepartment}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={70}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {employeesByDepartment.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 gap-2 mt-4">
                {employeesByDepartment.slice(0, 4).map((item) => (
                  <div key={item.name} className="flex items-center gap-2 text-xs">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-text-secondary">{item.name}</span>
                    <span className="font-medium text-text-primary ml-auto">{item.value}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Recent Hires & Events */}
        <div className="grid grid-cols-3 gap-6">
          {/* Recent Employees */}
          <Card className="col-span-2">
            <CardHeader
              title="Admissões Recentes"
              action={
                <Button variant="ghost" size="sm">
                  Ver Todos
                </Button>
              }
            />
            <CardBody className="p-0">
              <DataTable
                columns={recentColumns}
                data={recentEmployees}
                keyExtractor={(row) => row.id}
              />
            </CardBody>
          </Card>

          {/* Upcoming Events */}
          <Card>
            <CardHeader title="Próximos Eventos" />
            <CardBody>
              <div className="space-y-4">
                {upcomingEvents.map((event, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-3 bg-bg-tertiary rounded-lg"
                  >
                    <div
                      className={`p-2 rounded-lg ${
                        event.type === 'vacation'
                          ? 'bg-info/10'
                          : event.type === 'birthday'
                          ? 'bg-warning/10'
                          : event.type === 'anniversary'
                          ? 'bg-success/10'
                          : 'bg-primary/10'
                      }`}
                    >
                      {event.type === 'vacation' ? (
                        <Calendar className="w-4 h-4 text-info" />
                      ) : event.type === 'birthday' ? (
                        <Award className="w-4 h-4 text-warning" />
                      ) : event.type === 'anniversary' ? (
                        <Award className="w-4 h-4 text-success" />
                      ) : (
                        <UserCheck className="w-4 h-4 text-primary" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-text-primary">
                        {event.employee}
                      </p>
                      <p className="text-xs text-text-muted">
                        {event.type === 'vacation'
                          ? `Férias - ${event.days} dias`
                          : event.type === 'birthday'
                          ? 'Aniversário'
                          : event.type === 'anniversary'
                          ? `${event.years} anos de empresa`
                          : 'Retorno de afastamento'}
                      </p>
                    </div>
                    <span className="text-xs text-text-muted">
                      {new Date(event.date).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Alerts */}
        <div className="grid grid-cols-2 gap-4">
          <Card className="border-warning/30 bg-warning/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-warning/10">
                  <AlertTriangle className="w-6 h-6 text-warning" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    8 funcionários com férias vencidas
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Providencie o agendamento para evitar passivos trabalhistas
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Ver Lista
                </Button>
              </div>
            </CardBody>
          </Card>

          <Card className="border-info/30 bg-info/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-info/10">
                  <Clock className="w-6 h-6 text-info" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    Folha de Janeiro processada
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    605 funcionários - Total: R$ 1.850.000,00
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Ver Folha
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
