'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Zap,
  Play,
  Pause,
  Settings,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Edit2,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  ArrowRight,
  GitBranch,
  Activity,
  Calendar,
  BarChart3,
  TrendingUp,
  ChevronRight,
  Copy,
  Workflow
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { MainLayout } from '../../layouts/MainLayout';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';

// Types
interface Workflow {
  id: string;
  name: string;
  description: string;
  category: 'crm' | 'financial' | 'hr' | 'operations' | 'notifications' | 'integrations';
  trigger: {
    type: 'event' | 'schedule' | 'webhook' | 'manual';
    config: string;
  };
  status: 'active' | 'paused' | 'draft' | 'error';
  lastRun: string | null;
  nextRun: string | null;
  runsToday: number;
  runsTotal: number;
  successRate: number;
  createdAt: string;
  updatedAt: string;
}

// Mock Data
const mockWorkflows: Workflow[] = [
  {
    id: '1',
    name: 'Notificação de Lead Qualificado',
    description: 'Envia notificação ao vendedor quando lead é qualificado',
    category: 'crm',
    trigger: { type: 'event', config: 'lead.qualified' },
    status: 'active',
    lastRun: '2024-02-16T14:30:00',
    nextRun: null,
    runsToday: 12,
    runsTotal: 1250,
    successRate: 99.2,
    createdAt: '2023-06-15',
    updatedAt: '2024-02-10'
  },
  {
    id: '2',
    name: 'Alerta de Contas a Pagar',
    description: 'Alerta sobre contas vencendo nos próximos 5 dias',
    category: 'financial',
    trigger: { type: 'schedule', config: 'Diário às 08:00' },
    status: 'active',
    lastRun: '2024-02-16T08:00:00',
    nextRun: '2024-02-17T08:00:00',
    runsToday: 1,
    runsTotal: 320,
    successRate: 100,
    createdAt: '2023-09-01',
    updatedAt: '2024-01-15'
  },
  {
    id: '3',
    name: 'Integração WhatsApp - Boas-vindas',
    description: 'Envia mensagem de boas-vindas para novos clientes',
    category: 'integrations',
    trigger: { type: 'event', config: 'client.created' },
    status: 'active',
    lastRun: '2024-02-16T11:45:00',
    nextRun: null,
    runsToday: 5,
    runsTotal: 890,
    successRate: 97.5,
    createdAt: '2023-10-20',
    updatedAt: '2024-02-01'
  },
  {
    id: '4',
    name: 'Sincronização de Escalas',
    description: 'Sincroniza escalas de trabalho com sistema externo',
    category: 'operations',
    trigger: { type: 'schedule', config: 'A cada 6 horas' },
    status: 'paused',
    lastRun: '2024-02-15T18:00:00',
    nextRun: null,
    runsToday: 0,
    runsTotal: 456,
    successRate: 95.8,
    createdAt: '2023-07-10',
    updatedAt: '2024-02-15'
  },
  {
    id: '5',
    name: 'Backup de Documentos GED',
    description: 'Backup automático dos documentos para cloud storage',
    category: 'operations',
    trigger: { type: 'schedule', config: 'Diário às 02:00' },
    status: 'active',
    lastRun: '2024-02-16T02:00:00',
    nextRun: '2024-02-17T02:00:00',
    runsToday: 1,
    runsTotal: 365,
    successRate: 100,
    createdAt: '2023-02-15',
    updatedAt: '2023-12-20'
  },
  {
    id: '6',
    name: 'Lembrete de Aniversário',
    description: 'Envia email de felicitações para colaboradores aniversariantes',
    category: 'hr',
    trigger: { type: 'schedule', config: 'Diário às 09:00' },
    status: 'active',
    lastRun: '2024-02-16T09:00:00',
    nextRun: '2024-02-17T09:00:00',
    runsToday: 1,
    runsTotal: 180,
    successRate: 100,
    createdAt: '2023-08-01',
    updatedAt: '2024-01-10'
  }
];

const executionTrendData = [
  { date: '10/02', success: 145, failure: 3 },
  { date: '11/02', success: 167, failure: 5 },
  { date: '12/02', success: 132, failure: 2 },
  { date: '13/02', success: 189, failure: 4 },
  { date: '14/02', success: 156, failure: 1 },
  { date: '15/02', success: 178, failure: 3 },
  { date: '16/02', success: 124, failure: 2 }
];

const categoryDistribution = [
  { name: 'CRM', value: 35, color: '#6366f1' },
  { name: 'Financeiro', value: 25, color: '#10b981' },
  { name: 'Operações', value: 20, color: '#f59e0b' },
  { name: 'RH', value: 10, color: '#8b5cf6' },
  { name: 'Integrações', value: 10, color: '#3b82f6' }
];

const recentExecutions = [
  { id: '1', workflow: 'Notificação de Lead Qualificado', status: 'success', timestamp: '2024-02-16T14:30:00', duration: '1.2s' },
  { id: '2', workflow: 'Integração WhatsApp - Boas-vindas', status: 'success', timestamp: '2024-02-16T14:25:00', duration: '2.8s' },
  { id: '3', workflow: 'Alerta de Contas a Pagar', status: 'success', timestamp: '2024-02-16T08:00:15', duration: '5.4s' },
  { id: '4', workflow: 'Sincronização de Escalas', status: 'failure', timestamp: '2024-02-15T18:00:00', duration: '15.2s' },
  { id: '5', workflow: 'Backup de Documentos GED', status: 'success', timestamp: '2024-02-16T02:05:00', duration: '45.6s' }
];

export function AutomationDashboardPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const getCategoryInfo = (category: Workflow['category']) => {
    const categories = {
      crm: { label: 'CRM', color: 'primary' as const },
      financial: { label: 'Financeiro', color: 'success' as const },
      hr: { label: 'RH', color: 'info' as const },
      operations: { label: 'Operações', color: 'warning' as const },
      notifications: { label: 'Notificações', color: 'info' as const },
      integrations: { label: 'Integrações', color: 'primary' as const }
    };
    return categories[category];
  };

  const getStatusInfo = (status: Workflow['status']) => {
    const statuses = {
      active: { label: 'Ativo', color: 'success' as const, icon: Play },
      paused: { label: 'Pausado', color: 'warning' as const, icon: Pause },
      draft: { label: 'Rascunho', color: 'info' as const, icon: Edit2 },
      error: { label: 'Erro', color: 'danger' as const, icon: AlertTriangle }
    };
    return statuses[status];
  };

  const getTriggerLabel = (type: string) => {
    const triggers: Record<string, string> = {
      event: 'Por Evento',
      schedule: 'Agendado',
      webhook: 'Webhook',
      manual: 'Manual'
    };
    return triggers[type] || type;
  };

  const activeWorkflows = mockWorkflows.filter(w => w.status === 'active').length;
  const totalExecutionsToday = mockWorkflows.reduce((sum, w) => sum + w.runsToday, 0);
  const avgSuccessRate = mockWorkflows.reduce((sum, w) => sum + w.successRate, 0) / mockWorkflows.length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Central de Automações
            </h1>
            <p className="text-text-secondary mt-1">
              Workflows, triggers e automações do sistema
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button variant="primary">
              <Plus className="h-4 w-4 mr-2" />
              Nova Automação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <StatCard
            title="Workflows Ativos"
            value={activeWorkflows.toString()}
            changeLabel={`de ${mockWorkflows.length} total`}
            icon={<Zap className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Execuções Hoje"
            value={totalExecutionsToday.toString()}
            change={15}
            changeLabel="vs ontem"
            icon={<Activity className="h-5 w-5" />}
          />
          <StatCard
            title="Taxa de Sucesso"
            value={`${avgSuccessRate.toFixed(1)}%`}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Falhas (7d)"
            value="12"
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Tempo Médio"
            value="2.3s"
            changeLabel="de execução"
            icon={<Clock className="h-5 w-5" />}
          />
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Execution Trend */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Execuções (Últimos 7 dias)
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={executionTrendData}>
                    <defs>
                      <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="success"
                      name="Sucesso"
                      stroke="#10b981"
                      fillOpacity={1}
                      fill="url(#colorSuccess)"
                    />
                    <Area
                      type="monotone"
                      dataKey="failure"
                      name="Falha"
                      stroke="#ef4444"
                      fill="#ef4444"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Category Distribution */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Por Categoria
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={60}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {categoryDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-2">
                {categoryDistribution.map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-text-secondary">{item.name}</span>
                    </div>
                    <span className="text-text-primary font-medium">{item.value}%</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Workflows List */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Workflows
              </h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                <Input
                  placeholder="Buscar workflows..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </CardHeader>
          <CardBody className="space-y-3">
            {mockWorkflows
              .filter(w => w.name.toLowerCase().includes(searchTerm.toLowerCase()))
              .map((workflow, index) => {
                const statusInfo = getStatusInfo(workflow.status);
                const categoryInfo = getCategoryInfo(workflow.category);
                const StatusIcon = statusInfo.icon;
                return (
                  <motion.div
                    key={workflow.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 bg-bg-tertiary rounded-xl hover:bg-bg-hover transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl bg-accent-${statusInfo.color}/20`}>
                          <Workflow className={`h-6 w-6 text-accent-${statusInfo.color}`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-text-primary">{workflow.name}</h4>
                            <Badge variant={statusInfo.color} size="sm">
                              {statusInfo.label}
                            </Badge>
                            <Badge variant={categoryInfo.color} size="sm">
                              {categoryInfo.label}
                            </Badge>
                          </div>
                          <p className="text-sm text-text-secondary mt-1">{workflow.description}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-text-secondary">
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {getTriggerLabel(workflow.trigger.type)}: {workflow.trigger.config}
                            </span>
                            {workflow.lastRun && (
                              <span>
                                Última exec: {new Date(workflow.lastRun).toLocaleString('pt-BR')}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-sm text-text-secondary">Execuções hoje</p>
                          <p className="text-xl font-bold text-text-primary">{workflow.runsToday}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-text-secondary">Taxa de sucesso</p>
                          <p className={`text-xl font-bold ${
                            workflow.successRate >= 99 ? 'text-accent-success' :
                            workflow.successRate >= 95 ? 'text-accent-warning' :
                            'text-accent-danger'
                          }`}>
                            {workflow.successRate}%
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {workflow.status === 'active' ? (
                            <Button variant="ghost" size="sm">
                              <Pause className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button variant="ghost" size="sm">
                              <Play className="h-4 w-4" />
                            </Button>
                          )}
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
          </CardBody>
        </Card>

        {/* Recent Executions */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Execuções Recentes
              </h3>
              <Button variant="ghost" size="sm">
                Ver todas
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardBody>
            <div className="space-y-2">
              {recentExecutions.map((execution, index) => (
                <motion.div
                  key={execution.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      execution.status === 'success' ? 'bg-accent-success/20' : 'bg-accent-danger/20'
                    }`}>
                      {execution.status === 'success' ? (
                        <CheckCircle className="h-4 w-4 text-accent-success" />
                      ) : (
                        <XCircle className="h-4 w-4 text-accent-danger" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{execution.workflow}</p>
                      <p className="text-xs text-text-secondary">
                        {new Date(execution.timestamp).toLocaleString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-text-secondary">{execution.duration}</span>
                    <Badge variant={execution.status === 'success' ? 'success' : 'danger'} size="sm">
                      {execution.status === 'success' ? 'Sucesso' : 'Falha'}
                    </Badge>
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </MainLayout>
  );
}

export default AutomationDashboardPage;
