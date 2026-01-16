'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  MapPin,
  Clock,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Building2,
  Briefcase,
  Shield,
  Activity,
  RefreshCw,
  Eye,
  MoreHorizontal,
  ArrowUp,
  ArrowDown,
  UserCheck,
  UserX,
  Timer,
  Target,
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
  SimpleTabBar,
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
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts';

// Mock Data
const dailyPresence = [
  { hour: '06h', present: 45, absent: 5 },
  { hour: '08h', present: 120, absent: 8 },
  { hour: '10h', present: 125, absent: 10 },
  { hour: '12h', present: 118, absent: 12 },
  { hour: '14h', present: 130, absent: 5 },
  { hour: '16h', present: 128, absent: 7 },
  { hour: '18h', present: 95, absent: 4 },
  { hour: '20h', present: 65, absent: 2 },
  { hour: '22h', present: 55, absent: 3 },
];

const weeklyPerformance = [
  { day: 'Seg', kpi: 94, target: 95 },
  { day: 'Ter', kpi: 96, target: 95 },
  { day: 'Qua', kpi: 92, target: 95 },
  { day: 'Qui', kpi: 98, target: 95 },
  { day: 'Sex', kpi: 97, target: 95 },
  { day: 'Sáb', kpi: 95, target: 95 },
  { day: 'Dom', kpi: 93, target: 95 },
];

const allocationsByClient = [
  { name: 'Shopping Center Norte', value: 85, color: '#3B82F6' },
  { name: 'Hospital São Lucas', value: 45, color: '#10B981' },
  { name: 'Condomínio Aurora', value: 32, color: '#F59E0B' },
  { name: 'Corporate Tower', value: 28, color: '#8B5CF6' },
  { name: 'Outros', value: 45, color: '#6B7280' },
];

const recentAlerts = [
  { id: '1', type: 'absence', message: 'Falta não justificada - Carlos Silva', client: 'Shopping Center Norte', time: '08:15', severity: 'high' },
  { id: '2', type: 'late', message: 'Atraso de 25min - Maria Santos', client: 'Hospital São Lucas', time: '07:25', severity: 'medium' },
  { id: '3', type: 'overtime', message: 'Hora extra não autorizada - Roberto Lima', client: 'Condomínio Aurora', time: '22:30', severity: 'low' },
  { id: '4', type: 'coverage', message: 'Posto descoberto - Portaria B', client: 'Corporate Tower', time: '10:00', severity: 'high' },
];

const upcomingShifts = [
  { id: '1', employee: 'Ana Costa', client: 'Shopping Center Norte', post: 'Vigilância - Setor A', start: '14:00', status: 'confirmed' },
  { id: '2', employee: 'Pedro Almeida', client: 'Hospital São Lucas', post: 'Portaria Principal', start: '14:00', status: 'pending' },
  { id: '3', employee: 'Julia Martins', client: 'Condomínio Aurora', post: 'Ronda - Bloco B', start: '18:00', status: 'confirmed' },
  { id: '4', employee: 'Lucas Ferreira', client: 'Corporate Tower', post: 'CFTV', start: '22:00', status: 'confirmed' },
];

const tabs = [
  { id: 'today', label: 'Hoje' },
  { id: 'week', label: 'Semana' },
  { id: 'month', label: 'Mês' },
];

export function OperationsDashboardPage() {
  const [activeTab, setActiveTab] = useState('today');

  // Stats
  const totalEmployees = 235;
  const presentToday = 218;
  const absencesRate = ((totalEmployees - presentToday) / totalEmployees * 100).toFixed(1);
  const avgKpi = 95.3;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Dashboard Operacional</h1>
            <p className="text-text-secondary mt-1">Visão geral das operações em tempo real</p>
          </div>
          <div className="flex items-center gap-3">
            <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Atualizar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Colaboradores Presentes"
              value={`${presentToday}/${totalEmployees}`}
              icon={<Users className="w-6 h-6" />}
              iconColor="success"
              trend="up"
              trendValue="+2.5%"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Taxa de Ausência"
              value={`${absencesRate}%`}
              icon={<UserX className="w-6 h-6" />}
              iconColor="danger"
              trend="down"
              trendValue="-0.5%"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="KPI Médio"
              value={`${avgKpi}%`}
              icon={<Target className="w-6 h-6" />}
              iconColor="info"
              trend="up"
              trendValue="+1.2%"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Clientes Atendidos"
              value="42"
              icon={<Building2 className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
        </StatGrid>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-3 gap-6">
          {/* Presence Chart */}
          <Card className="col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold">Presença ao Longo do Dia</h3>
                </div>
                <Badge variant="success">Ao vivo</Badge>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={dailyPresence}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Area type="monotone" dataKey="present" fill="#10B98150" stroke="#10B981" name="Presentes" />
                    <Area type="monotone" dataKey="absent" fill="#EF444450" stroke="#EF4444" name="Ausentes" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Allocation by Client */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Alocação por Cliente</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={allocationsByClient} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                      {allocationsByClient.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">
                {allocationsByClient.slice(0, 4).map((item) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-xs text-text-muted">{item.name}</span>
                    </div>
                    <span className="text-xs font-medium">{item.value}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-2 gap-6">
          {/* KPI Performance */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-info" />
                <h3 className="font-semibold">Performance KPI (Semana)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weeklyPerformance}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="day" stroke="var(--color-text-muted)" />
                    <YAxis domain={[85, 100]} stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Line type="monotone" dataKey="kpi" stroke="#3B82F6" strokeWidth={3} dot={{ fill: '#3B82F6', strokeWidth: 2 }} name="KPI %" />
                    <Line type="monotone" dataKey="target" stroke="#EF4444" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Meta" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Alerts */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-warning" />
                  <h3 className="font-semibold">Alertas Recentes</h3>
                </div>
                <Badge variant="warning">{recentAlerts.length} ativos</Badge>
              </div>
            </CardHeader>
            <CardBody className="p-0">
              <div className="divide-y divide-border">
                {recentAlerts.map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between p-4 hover:bg-bg-secondary transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${alert.severity === 'high' ? 'bg-danger/10' : alert.severity === 'medium' ? 'bg-warning/10' : 'bg-info/10'}`}>
                        <AlertTriangle className={`w-4 h-4 ${alert.severity === 'high' ? 'text-danger' : alert.severity === 'medium' ? 'text-warning' : 'text-info'}`} />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-text-primary">{alert.message}</p>
                        <p className="text-xs text-text-muted">{alert.client}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-text-muted">{alert.time}</span>
                      <Button variant="ghost" size="icon-sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Upcoming Shifts */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Próximos Turnos</h3>
              </div>
              <Button variant="secondary" size="sm">Ver Todos</Button>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <div className="grid grid-cols-4 divide-x divide-border">
              {upcomingShifts.map((shift) => (
                <div key={shift.id} className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <Badge variant={shift.status === 'confirmed' ? 'success' : 'warning'}>
                      {shift.status === 'confirmed' ? 'Confirmado' : 'Pendente'}
                    </Badge>
                    <span className="text-sm font-medium text-primary">{shift.start}</span>
                  </div>
                  <div className="flex items-center gap-3 mb-2">
                    <Avatar name={shift.employee} size="sm" />
                    <div>
                      <p className="text-sm font-medium text-text-primary">{shift.employee}</p>
                      <p className="text-xs text-text-muted">{shift.post}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <Building2 className="w-3 h-3" />
                    <span>{shift.client}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-6 gap-4">
          <Card>
            <CardBody className="text-center">
              <div className="p-3 rounded-xl bg-success/10 w-fit mx-auto mb-2">
                <UserCheck className="w-6 h-6 text-success" />
              </div>
              <p className="text-2xl font-bold text-text-primary">156</p>
              <p className="text-xs text-text-muted">Pontos OK</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="text-center">
              <div className="p-3 rounded-xl bg-warning/10 w-fit mx-auto mb-2">
                <Timer className="w-6 h-6 text-warning" />
              </div>
              <p className="text-2xl font-bold text-text-primary">12</p>
              <p className="text-xs text-text-muted">Atrasos</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="text-center">
              <div className="p-3 rounded-xl bg-danger/10 w-fit mx-auto mb-2">
                <UserX className="w-6 h-6 text-danger" />
              </div>
              <p className="text-2xl font-bold text-text-primary">17</p>
              <p className="text-xs text-text-muted">Faltas</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="text-center">
              <div className="p-3 rounded-xl bg-info/10 w-fit mx-auto mb-2">
                <Clock className="w-6 h-6 text-info" />
              </div>
              <p className="text-2xl font-bold text-text-primary">45h</p>
              <p className="text-xs text-text-muted">Horas Extras</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="text-center">
              <div className="p-3 rounded-xl bg-primary/10 w-fit mx-auto mb-2">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <p className="text-2xl font-bold text-text-primary">8</p>
              <p className="text-xs text-text-muted">Ocorrências</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="text-center">
              <div className="p-3 rounded-xl bg-secondary/10 w-fit mx-auto mb-2">
                <Briefcase className="w-6 h-6 text-secondary" />
              </div>
              <p className="text-2xl font-bold text-text-primary">24</p>
              <p className="text-xs text-text-muted">Substituições</p>
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
