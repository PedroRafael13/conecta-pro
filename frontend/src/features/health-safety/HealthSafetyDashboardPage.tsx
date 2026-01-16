'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Heart,
  Shield,
  HardHat,
  Users,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  FileText,
  TrendingUp,
  Activity,
  Stethoscope,
  ClipboardCheck,
  AlertCircle,
  ChevronRight,
  Download,
  Plus,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  StatCard,
  StatGrid,
} from '@/design-system/components';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Mock Data
const complianceData = [
  { month: 'Ago', pcmso: 95, ppra: 88, epi: 92 },
  { month: 'Set', pcmso: 96, ppra: 90, epi: 94 },
  { month: 'Out', pcmso: 94, ppra: 92, epi: 93 },
  { month: 'Nov', pcmso: 97, ppra: 94, epi: 96 },
  { month: 'Dez', pcmso: 98, ppra: 95, epi: 97 },
  { month: 'Jan', pcmso: 96, ppra: 93, epi: 95 },
];

const examDistribution = [
  { name: 'Admissional', value: 45, color: '#10b981' },
  { name: 'Periódico', value: 120, color: '#6366f1' },
  { name: 'Retorno', value: 15, color: '#3b82f6' },
  { name: 'Mudança Função', value: 8, color: '#f59e0b' },
  { name: 'Demissional', value: 22, color: '#ef4444' },
];

const pendingExams = [
  { id: 1, employee: 'Roberto Silva', type: 'Periódico', dueDate: '2026-01-20', days: 5, risk: 'medium' },
  { id: 2, employee: 'Maria Santos', type: 'Retorno ao Trabalho', dueDate: '2026-01-18', days: 3, risk: 'high' },
  { id: 3, employee: 'Carlos Eduardo', type: 'Periódico', dueDate: '2026-01-25', days: 10, risk: 'low' },
  { id: 4, employee: 'Ana Paula', type: 'Mudança de Função', dueDate: '2026-01-22', days: 7, risk: 'medium' },
];

const epiAlerts = [
  { id: 1, item: 'Colete Balístico', employee: 'João Pereira', expiry: '2026-01-25', status: 'expiring' },
  { id: 2, item: 'Capacete Tático', employee: 'Pedro Almeida', expiry: '2026-01-18', status: 'critical' },
  { id: 3, item: 'Bota de Segurança', employee: 'Marcos Lima', expiry: '2026-02-01', status: 'expiring' },
];

const riskLabels = {
  low: { label: 'Baixo', color: 'success' as const },
  medium: { label: 'Médio', color: 'warning' as const },
  high: { label: 'Alto', color: 'danger' as const },
};

export function HealthSafetyDashboardPage() {
  // Stats
  const totalEmployees = 342;
  const examCompliance = 96;
  const pendingExamsCount = pendingExams.length;
  const epiCompliance = 95;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Saúde e Segurança Ocupacional
            </h1>
            <p className="text-text-secondary mt-1">
              PCMSO, PPRA/PGR e Gestão de EPIs
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Relatórios
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
              Novo Exame
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Funcionários Ativos"
              value={totalEmployees}
              icon={<Users className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Conformidade PCMSO"
              value={`${examCompliance}%`}
              icon={<Stethoscope className="w-6 h-6" />}
              iconColor="success"
              trend="up"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Exames Pendentes"
              value={pendingExamsCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Conformidade EPI"
              value={`${epiCompliance}%`}
              icon={<HardHat className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Quick Access Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card className="hover:border-accent-primary/50 transition-colors cursor-pointer h-full">
              <CardBody className="flex flex-col items-center text-center py-8">
                <div className="p-4 bg-accent-success/20 rounded-xl mb-4">
                  <Heart className="w-8 h-8 text-accent-success" />
                </div>
                <h3 className="text-lg font-semibold text-text-primary">PCMSO</h3>
                <p className="text-sm text-text-secondary mt-1">NR-7 - Programa de Controle Médico</p>
                <p className="text-2xl font-bold text-accent-success mt-4">96%</p>
                <p className="text-xs text-text-muted">Conformidade</p>
                <Button variant="secondary" size="sm" className="mt-4" rightIcon={<ChevronRight className="w-4 h-4" />}>
                  Acessar
                </Button>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card className="hover:border-accent-primary/50 transition-colors cursor-pointer h-full">
              <CardBody className="flex flex-col items-center text-center py-8">
                <div className="p-4 bg-accent-warning/20 rounded-xl mb-4">
                  <Shield className="w-8 h-8 text-accent-warning" />
                </div>
                <h3 className="text-lg font-semibold text-text-primary">PPRA/PGR</h3>
                <p className="text-sm text-text-secondary mt-1">NR-9 - Programa de Riscos</p>
                <p className="text-2xl font-bold text-accent-warning mt-4">93%</p>
                <p className="text-xs text-text-muted">Conformidade</p>
                <Button variant="secondary" size="sm" className="mt-4" rightIcon={<ChevronRight className="w-4 h-4" />}>
                  Acessar
                </Button>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card className="hover:border-accent-primary/50 transition-colors cursor-pointer h-full">
              <CardBody className="flex flex-col items-center text-center py-8">
                <div className="p-4 bg-accent-info/20 rounded-xl mb-4">
                  <HardHat className="w-8 h-8 text-accent-info" />
                </div>
                <h3 className="text-lg font-semibold text-text-primary">Gestão de EPIs</h3>
                <p className="text-sm text-text-secondary mt-1">NR-6 - Equipamentos de Proteção</p>
                <p className="text-2xl font-bold text-accent-info mt-4">95%</p>
                <p className="text-xs text-text-muted">Conformidade</p>
                <Button variant="secondary" size="sm" className="mt-4" rightIcon={<ChevronRight className="w-4 h-4" />}>
                  Acessar
                </Button>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Evolução de Conformidade</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={complianceData}>
                      <defs>
                        <linearGradient id="colorPcmso" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorPpra" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorEpi" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                      <XAxis dataKey="month" stroke="#64748b" />
                      <YAxis stroke="#64748b" domain={[80, 100]} />
                      <Tooltip contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }} />
                      <Area type="monotone" dataKey="pcmso" name="PCMSO" stroke="#10b981" fill="url(#colorPcmso)" />
                      <Area type="monotone" dataKey="ppra" name="PPRA" stroke="#f59e0b" fill="url(#colorPpra)" />
                      <Area type="monotone" dataKey="epi" name="EPI" stroke="#3b82f6" fill="url(#colorEpi)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Exames por Tipo</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64 flex items-center">
                  <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie
                        data={examDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={70}
                        dataKey="value"
                        stroke="none"
                      >
                        {examDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex-1 space-y-2">
                    {examDistribution.map((item) => (
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
        </div>

        {/* Alerts and Pending */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pending Exams */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-text-primary">Exames Pendentes</h3>
                  <Badge variant="warning">{pendingExams.length}</Badge>
                </div>
              </CardHeader>
              <CardBody className="p-0">
                <div className="divide-y divide-border-subtle">
                  {pendingExams.map((exam) => {
                    const riskConfig = riskLabels[exam.risk as keyof typeof riskLabels];
                    return (
                      <div key={exam.id} className="p-4 hover:bg-bg-tertiary transition-colors">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-text-primary">{exam.employee}</p>
                            <p className="text-sm text-text-muted">{exam.type}</p>
                          </div>
                          <div className="text-right">
                            <Badge variant={riskConfig.color}>{exam.days} dias</Badge>
                            <p className="text-xs text-text-muted mt-1">
                              {new Date(exam.dueDate).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </motion.div>

          {/* EPI Alerts */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.1 }}>
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-text-primary">Alertas de EPI</h3>
                  <Badge variant="danger">{epiAlerts.length}</Badge>
                </div>
              </CardHeader>
              <CardBody className="p-0">
                <div className="divide-y divide-border-subtle">
                  {epiAlerts.map((alert) => (
                    <div key={alert.id} className="p-4 hover:bg-bg-tertiary transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {alert.status === 'critical' ? (
                            <AlertCircle className="w-5 h-5 text-accent-danger" />
                          ) : (
                            <AlertTriangle className="w-5 h-5 text-accent-warning" />
                          )}
                          <div>
                            <p className="font-medium text-text-primary">{alert.item}</p>
                            <p className="text-sm text-text-muted">{alert.employee}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={alert.status === 'critical' ? 'danger' : 'warning'}>
                            {alert.status === 'critical' ? 'Vencido' : 'Vencendo'}
                          </Badge>
                          <p className="text-xs text-text-muted mt-1">
                            {new Date(alert.expiry).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>
      </div>
    </MainLayout>
  );
}
