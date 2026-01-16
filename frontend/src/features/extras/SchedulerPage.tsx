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
  Modal,
  Select
} from '@/design-system/components';
import {
  Calendar,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Play,
  Pause,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Settings,
  Zap,
  Database,
  Mail,
  FileText,
  Bell,
  RotateCw,
  History,
  Eye,
  Edit,
  Trash2,
  Timer,
  Activity,
  Terminal,
  Code,
  Server,
  Webhook,
  CalendarClock,
  PlayCircle,
  StopCircle,
  SkipForward,
  Copy
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  AreaChart,
  Area
} from 'recharts';

// ==================== TYPES ====================

interface ScheduledTask {
  id: string;
  name: string;
  description: string;
  category: 'report' | 'integration' | 'backup' | 'notification' | 'sync' | 'cleanup' | 'custom';
  status: 'active' | 'paused' | 'disabled' | 'error';
  triggerType: 'cron' | 'interval' | 'once' | 'event';
  cronExpression: string | null;
  intervalMinutes: number | null;
  scheduledAt: string | null;
  eventTrigger: string | null;
  lastRun: string | null;
  lastRunStatus: 'success' | 'failed' | 'running' | null;
  lastRunDuration: number | null;
  nextRun: string | null;
  runCount: number;
  failCount: number;
  successCount: number;
  timeout: number;
  retryOnFailure: boolean;
  maxRetries: number;
  notifyOnFailure: boolean;
  notifyEmails: string[];
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  tags: string[];
}

interface TaskExecution {
  id: string;
  taskId: string;
  taskName: string;
  status: 'running' | 'success' | 'failed' | 'cancelled' | 'timeout';
  startedAt: string;
  finishedAt: string | null;
  duration: number | null;
  trigger: 'scheduled' | 'manual' | 'retry' | 'event';
  output: string | null;
  errorMessage: string | null;
  retryCount: number;
  triggeredBy: string;
}

interface TaskLog {
  id: string;
  executionId: string;
  taskId: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  timestamp: string;
  metadata: Record<string, any> | null;
}

interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
}

// ==================== CONSTANTS ====================

const CATEGORIES: Record<string, { label: string; icon: any; color: string }> = {
  report: { label: 'Relatório', icon: FileText, color: 'info' },
  integration: { label: 'Integração', icon: Webhook, color: 'primary' },
  backup: { label: 'Backup', icon: Database, color: 'success' },
  notification: { label: 'Notificação', icon: Bell, color: 'warning' },
  sync: { label: 'Sincronização', icon: RotateCw, color: 'info' },
  cleanup: { label: 'Limpeza', icon: Trash2, color: 'danger' },
  custom: { label: 'Customizado', icon: Code, color: 'neutral' }
};

const STATUS_CONFIG: Record<string, { label: string; variant: string; icon: any }> = {
  active: { label: 'Ativo', variant: 'success', icon: PlayCircle },
  paused: { label: 'Pausado', variant: 'warning', icon: Pause },
  disabled: { label: 'Desativado', variant: 'neutral', icon: StopCircle },
  error: { label: 'Erro', variant: 'danger', icon: AlertTriangle }
};

const EXECUTION_STATUS: Record<string, { label: string; variant: string }> = {
  running: { label: 'Executando', variant: 'info' },
  success: { label: 'Sucesso', variant: 'success' },
  failed: { label: 'Falhou', variant: 'danger' },
  cancelled: { label: 'Cancelado', variant: 'warning' },
  timeout: { label: 'Timeout', variant: 'danger' }
};

const TRIGGER_TYPES: Record<string, { label: string; description: string }> = {
  cron: { label: 'Cron', description: 'Expressão cron (ex: 0 8 * * *)' },
  interval: { label: 'Intervalo', description: 'Executar a cada X minutos' },
  once: { label: 'Uma vez', description: 'Executar em data/hora específica' },
  event: { label: 'Evento', description: 'Executar quando evento ocorrer' }
};

// ==================== MOCK DATA ====================

const mockTasks: ScheduledTask[] = [
  {
    id: 'TASK001',
    name: 'Relatório Diário de Vendas',
    description: 'Gera e envia relatório de vendas do dia anterior',
    category: 'report',
    status: 'active',
    triggerType: 'cron',
    cronExpression: '0 8 * * *',
    intervalMinutes: null,
    scheduledAt: null,
    eventTrigger: null,
    lastRun: '2024-01-15T08:00:00',
    lastRunStatus: 'success',
    lastRunDuration: 45,
    nextRun: '2024-01-16T08:00:00',
    runCount: 365,
    failCount: 3,
    successCount: 362,
    timeout: 300,
    retryOnFailure: true,
    maxRetries: 3,
    notifyOnFailure: true,
    notifyEmails: ['admin@empresa.com'],
    createdBy: 'Sistema',
    createdAt: '2023-01-15T10:00:00',
    updatedAt: '2024-01-10T14:00:00',
    tags: ['vendas', 'diário', 'email']
  },
  {
    id: 'TASK002',
    name: 'Sincronização Contábil',
    description: 'Sincroniza lançamentos contábeis com sistema externo',
    category: 'integration',
    status: 'active',
    triggerType: 'interval',
    cronExpression: null,
    intervalMinutes: 60,
    scheduledAt: null,
    eventTrigger: null,
    lastRun: '2024-01-15T11:00:00',
    lastRunStatus: 'success',
    lastRunDuration: 120,
    nextRun: '2024-01-15T12:00:00',
    runCount: 8760,
    failCount: 45,
    successCount: 8715,
    timeout: 600,
    retryOnFailure: true,
    maxRetries: 5,
    notifyOnFailure: true,
    notifyEmails: ['ti@empresa.com', 'financeiro@empresa.com'],
    createdBy: 'João Silva',
    createdAt: '2023-06-01T09:00:00',
    updatedAt: '2024-01-05T16:00:00',
    tags: ['contabilidade', 'integração', 'crítico']
  },
  {
    id: 'TASK003',
    name: 'Backup Diário do Banco',
    description: 'Realiza backup completo do banco de dados',
    category: 'backup',
    status: 'active',
    triggerType: 'cron',
    cronExpression: '0 2 * * *',
    intervalMinutes: null,
    scheduledAt: null,
    eventTrigger: null,
    lastRun: '2024-01-15T02:00:00',
    lastRunStatus: 'success',
    lastRunDuration: 1800,
    nextRun: '2024-01-16T02:00:00',
    runCount: 400,
    failCount: 2,
    successCount: 398,
    timeout: 7200,
    retryOnFailure: true,
    maxRetries: 2,
    notifyOnFailure: true,
    notifyEmails: ['ti@empresa.com'],
    createdBy: 'Sistema',
    createdAt: '2022-08-10T08:00:00',
    updatedAt: '2023-12-01T10:00:00',
    tags: ['backup', 'banco', 'crítico', 'noturno']
  },
  {
    id: 'TASK004',
    name: 'Envio de Lembretes',
    description: 'Envia lembretes de vencimento de faturas',
    category: 'notification',
    status: 'active',
    triggerType: 'cron',
    cronExpression: '0 9 * * 1-5',
    intervalMinutes: null,
    scheduledAt: null,
    eventTrigger: null,
    lastRun: '2024-01-15T09:00:00',
    lastRunStatus: 'success',
    lastRunDuration: 30,
    nextRun: '2024-01-16T09:00:00',
    runCount: 260,
    failCount: 5,
    successCount: 255,
    timeout: 120,
    retryOnFailure: true,
    maxRetries: 3,
    notifyOnFailure: false,
    notifyEmails: [],
    createdBy: 'Maria Santos',
    createdAt: '2023-03-20T14:00:00',
    updatedAt: '2024-01-02T11:00:00',
    tags: ['notificação', 'email', 'cobrança']
  },
  {
    id: 'TASK005',
    name: 'Sincronização eSocial',
    description: 'Envia eventos pendentes para o eSocial',
    category: 'sync',
    status: 'error',
    triggerType: 'cron',
    cronExpression: '0 6,12,18 * * *',
    intervalMinutes: null,
    scheduledAt: null,
    eventTrigger: null,
    lastRun: '2024-01-15T06:00:00',
    lastRunStatus: 'failed',
    lastRunDuration: 15,
    nextRun: '2024-01-15T12:00:00',
    runCount: 1095,
    failCount: 28,
    successCount: 1067,
    timeout: 900,
    retryOnFailure: true,
    maxRetries: 3,
    notifyOnFailure: true,
    notifyEmails: ['rh@empresa.com', 'ti@empresa.com'],
    createdBy: 'Sistema',
    createdAt: '2023-01-01T00:00:00',
    updatedAt: '2024-01-15T06:15:00',
    tags: ['esocial', 'governo', 'compliance', 'crítico']
  },
  {
    id: 'TASK006',
    name: 'Limpeza de Logs Antigos',
    description: 'Remove logs com mais de 90 dias',
    category: 'cleanup',
    status: 'active',
    triggerType: 'cron',
    cronExpression: '0 3 * * 0',
    intervalMinutes: null,
    scheduledAt: null,
    eventTrigger: null,
    lastRun: '2024-01-14T03:00:00',
    lastRunStatus: 'success',
    lastRunDuration: 600,
    nextRun: '2024-01-21T03:00:00',
    runCount: 52,
    failCount: 0,
    successCount: 52,
    timeout: 3600,
    retryOnFailure: false,
    maxRetries: 0,
    notifyOnFailure: false,
    notifyEmails: [],
    createdBy: 'Sistema',
    createdAt: '2023-01-01T00:00:00',
    updatedAt: '2023-06-15T09:00:00',
    tags: ['limpeza', 'logs', 'manutenção']
  },
  {
    id: 'TASK007',
    name: 'Processamento de Folha',
    description: 'Processa folha de pagamento mensal',
    category: 'custom',
    status: 'paused',
    triggerType: 'once',
    cronExpression: null,
    intervalMinutes: null,
    scheduledAt: '2024-01-25T10:00:00',
    eventTrigger: null,
    lastRun: '2023-12-25T10:00:00',
    lastRunStatus: 'success',
    lastRunDuration: 3600,
    nextRun: '2024-01-25T10:00:00',
    runCount: 12,
    failCount: 0,
    successCount: 12,
    timeout: 7200,
    retryOnFailure: true,
    maxRetries: 2,
    notifyOnFailure: true,
    notifyEmails: ['rh@empresa.com', 'financeiro@empresa.com'],
    createdBy: 'Ana Costa',
    createdAt: '2023-01-10T08:00:00',
    updatedAt: '2024-01-10T15:00:00',
    tags: ['folha', 'mensal', 'RH', 'crítico']
  },
  {
    id: 'TASK008',
    name: 'Webhook Novo Pedido',
    description: 'Processa novos pedidos do e-commerce',
    category: 'integration',
    status: 'active',
    triggerType: 'event',
    cronExpression: null,
    intervalMinutes: null,
    scheduledAt: null,
    eventTrigger: 'order.created',
    lastRun: '2024-01-15T10:45:00',
    lastRunStatus: 'success',
    lastRunDuration: 2,
    nextRun: null,
    runCount: 15678,
    failCount: 123,
    successCount: 15555,
    timeout: 30,
    retryOnFailure: true,
    maxRetries: 5,
    notifyOnFailure: true,
    notifyEmails: ['vendas@empresa.com'],
    createdBy: 'Pedro Lima',
    createdAt: '2023-08-15T14:00:00',
    updatedAt: '2024-01-12T09:00:00',
    tags: ['webhook', 'pedidos', 'e-commerce', 'tempo-real']
  }
];

const mockExecutions: TaskExecution[] = [
  {
    id: 'EXEC001',
    taskId: 'TASK001',
    taskName: 'Relatório Diário de Vendas',
    status: 'success',
    startedAt: '2024-01-15T08:00:00',
    finishedAt: '2024-01-15T08:00:45',
    duration: 45,
    trigger: 'scheduled',
    output: 'Relatório gerado com sucesso. Enviado para 5 destinatários.',
    errorMessage: null,
    retryCount: 0,
    triggeredBy: 'Sistema'
  },
  {
    id: 'EXEC002',
    taskId: 'TASK002',
    taskName: 'Sincronização Contábil',
    status: 'success',
    startedAt: '2024-01-15T11:00:00',
    finishedAt: '2024-01-15T11:02:00',
    duration: 120,
    trigger: 'scheduled',
    output: '234 registros sincronizados com sucesso.',
    errorMessage: null,
    retryCount: 0,
    triggeredBy: 'Sistema'
  },
  {
    id: 'EXEC003',
    taskId: 'TASK005',
    taskName: 'Sincronização eSocial',
    status: 'failed',
    startedAt: '2024-01-15T06:00:00',
    finishedAt: '2024-01-15T06:00:15',
    duration: 15,
    trigger: 'scheduled',
    output: null,
    errorMessage: 'Erro de conexão com servidor eSocial: Connection timeout',
    retryCount: 3,
    triggeredBy: 'Sistema'
  },
  {
    id: 'EXEC004',
    taskId: 'TASK003',
    taskName: 'Backup Diário do Banco',
    status: 'success',
    startedAt: '2024-01-15T02:00:00',
    finishedAt: '2024-01-15T02:30:00',
    duration: 1800,
    trigger: 'scheduled',
    output: 'Backup concluído: 2.5GB compactado. Armazenado em s3://backups/2024-01-15.tar.gz',
    errorMessage: null,
    retryCount: 0,
    triggeredBy: 'Sistema'
  },
  {
    id: 'EXEC005',
    taskId: 'TASK008',
    taskName: 'Webhook Novo Pedido',
    status: 'success',
    startedAt: '2024-01-15T10:45:00',
    finishedAt: '2024-01-15T10:45:02',
    duration: 2,
    trigger: 'event',
    output: 'Pedido #12345 processado com sucesso.',
    errorMessage: null,
    retryCount: 0,
    triggeredBy: 'order.created'
  },
  {
    id: 'EXEC006',
    taskId: 'TASK004',
    taskName: 'Envio de Lembretes',
    status: 'success',
    startedAt: '2024-01-15T09:00:00',
    finishedAt: '2024-01-15T09:00:30',
    duration: 30,
    trigger: 'scheduled',
    output: '45 lembretes enviados com sucesso.',
    errorMessage: null,
    retryCount: 0,
    triggeredBy: 'Sistema'
  },
  {
    id: 'EXEC007',
    taskId: 'TASK002',
    taskName: 'Sincronização Contábil',
    status: 'running',
    startedAt: '2024-01-15T11:30:00',
    finishedAt: null,
    duration: null,
    trigger: 'manual',
    output: null,
    errorMessage: null,
    retryCount: 0,
    triggeredBy: 'João Silva'
  }
];

const mockLogs: TaskLog[] = [
  {
    id: 'LOG001',
    executionId: 'EXEC003',
    taskId: 'TASK005',
    level: 'info',
    message: 'Iniciando sincronização eSocial...',
    timestamp: '2024-01-15T06:00:00',
    metadata: null
  },
  {
    id: 'LOG002',
    executionId: 'EXEC003',
    taskId: 'TASK005',
    level: 'info',
    message: 'Conectando ao servidor eSocial...',
    timestamp: '2024-01-15T06:00:02',
    metadata: { endpoint: 'https://esocial.gov.br/api' }
  },
  {
    id: 'LOG003',
    executionId: 'EXEC003',
    taskId: 'TASK005',
    level: 'warning',
    message: 'Timeout na primeira tentativa. Tentando novamente...',
    timestamp: '2024-01-15T06:00:05',
    metadata: { attempt: 1 }
  },
  {
    id: 'LOG004',
    executionId: 'EXEC003',
    taskId: 'TASK005',
    level: 'warning',
    message: 'Timeout na segunda tentativa. Tentando novamente...',
    timestamp: '2024-01-15T06:00:10',
    metadata: { attempt: 2 }
  },
  {
    id: 'LOG005',
    executionId: 'EXEC003',
    taskId: 'TASK005',
    level: 'error',
    message: 'Falha após 3 tentativas: Connection timeout',
    timestamp: '2024-01-15T06:00:15',
    metadata: { attempt: 3, error: 'ETIMEDOUT' }
  }
];

// ==================== CHART DATA ====================

const executionStatusData = [
  { name: 'Sucesso', value: 156, color: '#10b981' },
  { name: 'Falha', value: 8, color: '#ef4444' },
  { name: 'Timeout', value: 2, color: '#f59e0b' }
];

const executionsByHourData = [
  { hour: '00h', executions: 5 },
  { hour: '02h', executions: 12 },
  { hour: '04h', executions: 3 },
  { hour: '06h', executions: 18 },
  { hour: '08h', executions: 45 },
  { hour: '10h', executions: 32 },
  { hour: '12h', executions: 28 },
  { hour: '14h', executions: 15 },
  { hour: '16h', executions: 22 },
  { hour: '18h', executions: 35 },
  { hour: '20h', executions: 12 },
  { hour: '22h', executions: 8 }
];

const weeklyTrendData = [
  { day: 'Seg', sucesso: 145, falha: 5 },
  { day: 'Ter', sucesso: 156, falha: 8 },
  { day: 'Qua', sucesso: 148, falha: 3 },
  { day: 'Qui', sucesso: 162, falha: 6 },
  { day: 'Sex', sucesso: 158, falha: 4 },
  { day: 'Sáb', sucesso: 45, falha: 1 },
  { day: 'Dom', sucesso: 32, falha: 0 }
];

const categoryExecutionsData = [
  { name: 'Relatório', executions: 365 },
  { name: 'Integração', executions: 8760 },
  { name: 'Backup', executions: 400 },
  { name: 'Notificação', executions: 260 },
  { name: 'Sync', executions: 1095 }
];

// ==================== HELPERS ====================

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR');
};

const formatDateTime = (dateString: string | null) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('pt-BR');
};

const formatDuration = (seconds: number | null) => {
  if (!seconds) return '-';
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
};

const formatCronExpression = (cron: string | null) => {
  if (!cron) return '-';
  // Simple cron explanation
  const parts = cron.split(' ');
  if (parts.length !== 5) return cron;
  const [minute, hour, dayMonth, month, dayWeek] = parts;

  if (hour !== '*' && minute === '0' && dayMonth === '*' && month === '*' && dayWeek === '*') {
    return `Diariamente às ${hour}:00`;
  }
  if (hour !== '*' && minute === '0' && dayMonth === '*' && month === '*' && dayWeek === '0') {
    return `Semanalmente (Dom) às ${hour}:00`;
  }
  if (dayWeek === '1-5') {
    return `Dias úteis às ${hour}:${minute.padStart(2, '0')}`;
  }
  return cron;
};

const getStatusBadge = (status: ScheduledTask['status']) => {
  const config = STATUS_CONFIG[status];
  if (!config) return <Badge variant="neutral">{status}</Badge>;
  const Icon = config.icon;
  return (
    <Badge variant={config.variant as any}>
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
};

const getExecutionStatusBadge = (status: TaskExecution['status']) => {
  const config = EXECUTION_STATUS[status];
  if (!config) return <Badge variant="neutral">{status}</Badge>;
  return <Badge variant={config.variant as any}>{config.label}</Badge>;
};

const getCategoryBadge = (category: string) => {
  const config = CATEGORIES[category];
  if (!config) return <Badge variant="neutral">{category}</Badge>;
  const Icon = config.icon;
  return (
    <Badge variant={config.color as any}>
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
};

const getLogLevelBadge = (level: TaskLog['level']) => {
  const config: Record<string, { variant: any; label: string }> = {
    info: { variant: 'info', label: 'INFO' },
    warning: { variant: 'warning', label: 'WARN' },
    error: { variant: 'danger', label: 'ERROR' },
    debug: { variant: 'neutral', label: 'DEBUG' }
  };
  const { variant, label } = config[level] || { variant: 'neutral', label: level };
  return <Badge variant={variant}>{label}</Badge>;
};

// ==================== COMPONENT ====================

export function SchedulerPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Modals
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [showExecutionModal, setShowExecutionModal] = useState(false);
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [showLogsModal, setShowLogsModal] = useState(false);

  const [selectedTask, setSelectedTask] = useState<ScheduledTask | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<TaskExecution | null>(null);

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Calendar className="h-4 w-4" /> },
    { value: 'tasks', label: 'Tarefas', icon: <Clock className="h-4 w-4" /> },
    { value: 'executions', label: 'Execuções', icon: <Activity className="h-4 w-4" /> },
    { value: 'logs', label: 'Logs', icon: <Terminal className="h-4 w-4" /> }
  ];

  // Stats
  const activeTasks = mockTasks.filter(t => t.status === 'active').length;
  const executedToday = mockExecutions.filter(e => {
    const today = new Date().toDateString();
    return new Date(e.startedAt).toDateString() === today;
  }).length;
  const failedTasks = mockTasks.filter(t => t.status === 'error').length;
  const runningTasks = mockExecutions.filter(e => e.status === 'running').length;

  // Filters
  const filteredTasks = mockTasks.filter(task => {
    const matchesSearch = task.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || task.category === categoryFilter;
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Columns
  const taskColumns: Column<ScheduledTask>[] = [
    {
      key: 'task',
      header: 'Tarefa',
      render: (row) => {
        const CategoryIcon = CATEGORIES[row.category]?.icon || Clock;
        return (
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-bg-tertiary">
              <CategoryIcon className="h-5 w-5 text-accent-primary" />
            </div>
            <div>
              <p className="font-medium text-text-primary">{row.name}</p>
              <p className="text-sm text-text-secondary">{row.description.substring(0, 40)}...</p>
            </div>
          </div>
        );
      }
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => getCategoryBadge(row.category)
    },
    {
      key: 'schedule',
      header: 'Agendamento',
      render: (row) => (
        <div>
          <p className="text-text-primary text-sm">
            {row.triggerType === 'cron' && formatCronExpression(row.cronExpression)}
            {row.triggerType === 'interval' && `A cada ${row.intervalMinutes} min`}
            {row.triggerType === 'once' && formatDateTime(row.scheduledAt)}
            {row.triggerType === 'event' && `Evento: ${row.eventTrigger}`}
          </p>
          <p className="text-xs text-text-secondary">
            Próxima: {row.nextRun ? formatDateTime(row.nextRun) : 'N/A'}
          </p>
        </div>
      )
    },
    {
      key: 'lastRun',
      header: 'Última Execução',
      render: (row) => (
        <div className="flex items-center gap-2">
          {row.lastRunStatus === 'success' && <CheckCircle className="h-4 w-4 text-accent-success" />}
          {row.lastRunStatus === 'failed' && <XCircle className="h-4 w-4 text-accent-danger" />}
          {row.lastRunStatus === 'running' && <RotateCw className="h-4 w-4 text-accent-info animate-spin" />}
          <div>
            <p className="text-text-primary text-sm">{row.lastRun ? formatDateTime(row.lastRun) : 'Nunca'}</p>
            {row.lastRunDuration && (
              <p className="text-xs text-text-secondary">{formatDuration(row.lastRunDuration)}</p>
            )}
          </div>
        </div>
      )
    },
    {
      key: 'stats',
      header: 'Estatísticas',
      render: (row) => (
        <div className="text-sm">
          <span className="text-accent-success">{row.successCount}</span>
          {' / '}
          <span className="text-accent-danger">{row.failCount}</span>
          <span className="text-text-secondary"> ({row.runCount} total)</span>
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
            onClick={() => {
              setSelectedTask(row);
              setShowTaskModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" title="Executar Agora">
            <Play className="h-4 w-4" />
          </Button>
          {row.status === 'active' ? (
            <Button variant="ghost" size="sm" title="Pausar">
              <Pause className="h-4 w-4" />
            </Button>
          ) : (
            <Button variant="ghost" size="sm" title="Ativar">
              <Play className="h-4 w-4" />
            </Button>
          )}
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const executionColumns: Column<TaskExecution>[] = [
    {
      key: 'task',
      header: 'Tarefa',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.taskName}</p>
          <p className="text-sm text-text-secondary">ID: {row.id}</p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <div className="flex items-center gap-2">
          {row.status === 'running' && (
            <RotateCw className="h-4 w-4 text-accent-info animate-spin" />
          )}
          {getExecutionStatusBadge(row.status)}
        </div>
      )
    },
    {
      key: 'trigger',
      header: 'Gatilho',
      render: (row) => (
        <Badge variant={row.trigger === 'manual' ? 'warning' : row.trigger === 'event' ? 'info' : 'neutral'}>
          {row.trigger === 'scheduled' && 'Agendado'}
          {row.trigger === 'manual' && 'Manual'}
          {row.trigger === 'retry' && 'Retry'}
          {row.trigger === 'event' && 'Evento'}
        </Badge>
      )
    },
    {
      key: 'startedAt',
      header: 'Iniciado',
      render: (row) => (
        <span className="text-text-primary">{formatDateTime(row.startedAt)}</span>
      )
    },
    {
      key: 'duration',
      header: 'Duração',
      render: (row) => (
        <span className="text-text-secondary">
          {row.status === 'running' ? (
            <span className="text-accent-info">Em andamento...</span>
          ) : (
            formatDuration(row.duration)
          )}
        </span>
      )
    },
    {
      key: 'triggeredBy',
      header: 'Por',
      render: (row) => (
        <span className="text-text-secondary">{row.triggeredBy}</span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedExecution(row);
              setShowExecutionModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedExecution(row);
              setShowLogsModal(true);
            }}
          >
            <Terminal className="h-4 w-4" />
          </Button>
          {row.status === 'running' && (
            <Button variant="ghost" size="sm" title="Cancelar">
              <StopCircle className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const logColumns: Column<TaskLog>[] = [
    {
      key: 'timestamp',
      header: 'Data/Hora',
      render: (row) => (
        <span className="text-text-secondary font-mono text-sm">
          {formatDateTime(row.timestamp)}
        </span>
      )
    },
    {
      key: 'level',
      header: 'Nível',
      render: (row) => getLogLevelBadge(row.level)
    },
    {
      key: 'message',
      header: 'Mensagem',
      render: (row) => (
        <span className="text-text-primary">{row.message}</span>
      )
    },
    {
      key: 'metadata',
      header: 'Metadata',
      render: (row) => (
        row.metadata ? (
          <code className="text-xs text-text-secondary bg-bg-tertiary px-2 py-1 rounded">
            {JSON.stringify(row.metadata)}
          </code>
        ) : (
          <span className="text-text-muted">-</span>
        )
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Agendador de Tarefas
            </h1>
            <p className="text-text-secondary mt-1">
              Automação e agendamento de processos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <History className="h-4 w-4 mr-2" />
              Histórico
            </Button>
            <Button onClick={() => setShowNewTaskModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Tarefa
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Tarefas Ativas"
            value={activeTasks.toString()}
            icon={<PlayCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Executadas Hoje"
            value={executedToday.toString()}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="primary"
            change="+12"
            changeLabel="vs ontem"
          />
          <StatCard
            title="Com Erro"
            value={failedTasks.toString()}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Executando"
            value={runningTasks.toString()}
            icon={<RotateCw className="h-5 w-5" />}
            iconColor="info"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Execution Status */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Status das Execuções (Hoje)
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={executionStatusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {executionStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>

              {/* Executions by Hour */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Execuções por Horário
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={executionsByHourData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="hour" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="executions"
                      name="Execuções"
                      stroke="#6366f1"
                      fill="#6366f1"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Weekly Trend */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Tendência Semanal
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={weeklyTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Bar dataKey="sucesso" name="Sucesso" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="falha" name="Falha" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              {/* Category Executions */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Execuções por Categoria
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={categoryExecutionsData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Bar dataKey="executions" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Recent Activity & Failed Tasks */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Executions */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Execuções Recentes
                  </h3>
                  <Button variant="ghost" size="sm" onClick={() => setActiveTab('executions')}>
                    Ver Todas
                  </Button>
                </div>
                <div className="space-y-3">
                  {mockExecutions.slice(0, 5).map((exec) => (
                    <div
                      key={exec.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-bg-tertiary"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${
                          exec.status === 'success' ? 'bg-accent-success/20' :
                          exec.status === 'failed' ? 'bg-accent-danger/20' :
                          exec.status === 'running' ? 'bg-accent-info/20' :
                          'bg-bg-tertiary'
                        }`}>
                          {exec.status === 'success' && <CheckCircle className="h-4 w-4 text-accent-success" />}
                          {exec.status === 'failed' && <XCircle className="h-4 w-4 text-accent-danger" />}
                          {exec.status === 'running' && <RotateCw className="h-4 w-4 text-accent-info animate-spin" />}
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{exec.taskName}</p>
                          <p className="text-sm text-text-secondary">
                            {formatDateTime(exec.startedAt)}
                          </p>
                        </div>
                      </div>
                      {getExecutionStatusBadge(exec.status)}
                    </div>
                  ))}
                </div>
              </Card>

              {/* Tasks with Errors */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Tarefas com Problemas
                  </h3>
                </div>
                <div className="space-y-3">
                  {mockTasks.filter(t => t.status === 'error' || t.lastRunStatus === 'failed').map((task) => (
                    <div
                      key={task.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-accent-danger/10 border border-accent-danger/30"
                    >
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="h-5 w-5 text-accent-danger" />
                        <div>
                          <p className="font-medium text-text-primary">{task.name}</p>
                          <p className="text-sm text-text-secondary">
                            Última falha: {task.lastRun ? formatDateTime(task.lastRun) : 'N/A'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline">
                          <RefreshCw className="h-4 w-4 mr-1" />
                          Retry
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  {mockTasks.filter(t => t.status === 'error' || t.lastRunStatus === 'failed').length === 0 && (
                    <div className="text-center py-8 text-text-secondary">
                      <CheckCircle className="h-12 w-12 mx-auto mb-2 text-accent-success" />
                      <p>Todas as tarefas estão funcionando corretamente!</p>
                    </div>
                  )}
                </div>
              </Card>
            </div>

            {/* Upcoming Tasks */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Próximas Execuções
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {mockTasks.filter(t => t.nextRun && t.status === 'active').slice(0, 4).map((task) => {
                  const CategoryIcon = CATEGORIES[task.category]?.icon || Clock;
                  return (
                    <div
                      key={task.id}
                      className="p-4 rounded-lg bg-bg-tertiary border border-border-subtle"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-accent-primary/20">
                          <CategoryIcon className="h-5 w-5 text-accent-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary truncate">{task.name}</p>
                          {getCategoryBadge(task.category)}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <CalendarClock className="h-4 w-4 text-text-secondary" />
                        <span className="text-text-secondary">{formatDateTime(task.nextRun)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'tasks' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar tarefas..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'Todas Categorias' },
                  ...Object.entries(CATEGORIES).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))
                ]}
                value={categoryFilter}
                onChange={setCategoryFilter}
              />
              <Select
                options={[
                  { value: 'all', label: 'Todos Status' },
                  ...Object.entries(STATUS_CONFIG).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))
                ]}
                value={statusFilter}
                onChange={setStatusFilter}
              />
            </div>

            <DataTable
              data={filteredTasks}
              columns={taskColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'executions' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <Input
                  placeholder="Buscar execuções..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todos Status' },
                    { value: 'running', label: 'Executando' },
                    { value: 'success', label: 'Sucesso' },
                    { value: 'failed', label: 'Falhou' }
                  ]}
                  value="all"
                  onChange={() => {}}
                />
              </div>
              <Button variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Atualizar
              </Button>
            </div>

            <DataTable
              data={mockExecutions}
              columns={executionColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'logs' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <Input
                  placeholder="Buscar nos logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todos Níveis' },
                    { value: 'error', label: 'Error' },
                    { value: 'warning', label: 'Warning' },
                    { value: 'info', label: 'Info' },
                    { value: 'debug', label: 'Debug' }
                  ]}
                  value="all"
                  onChange={() => {}}
                />
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Exportar
                </Button>
                <Button variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Atualizar
                </Button>
              </div>
            </div>

            <DataTable
              data={mockLogs}
              columns={logColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Task Detail Modal */}
        <Modal
          isOpen={showTaskModal}
          onClose={() => setShowTaskModal(false)}
          title="Detalhes da Tarefa"
          size="lg"
        >
          {selectedTask && (
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-accent-primary/20">
                    {(() => {
                      const CategoryIcon = CATEGORIES[selectedTask.category]?.icon || Clock;
                      return <CategoryIcon className="h-8 w-8 text-accent-primary" />;
                    })()}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedTask.name}</h3>
                    <p className="text-text-secondary">{selectedTask.description}</p>
                  </div>
                </div>
                {getStatusBadge(selectedTask.status)}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Categoria</p>
                  <div className="mt-1">{getCategoryBadge(selectedTask.category)}</div>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Total Execuções</p>
                  <p className="text-xl font-semibold text-text-primary mt-1">{selectedTask.runCount}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Taxa de Sucesso</p>
                  <p className="text-xl font-semibold text-accent-success mt-1">
                    {selectedTask.runCount > 0 ? ((selectedTask.successCount / selectedTask.runCount) * 100).toFixed(1) : 0}%
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Falhas</p>
                  <p className="text-xl font-semibold text-accent-danger mt-1">{selectedTask.failCount}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <h4 className="font-semibold text-text-primary mb-3">Agendamento</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Tipo</span>
                      <span className="text-text-primary capitalize">{selectedTask.triggerType}</span>
                    </div>
                    {selectedTask.cronExpression && (
                      <div className="flex justify-between">
                        <span className="text-text-secondary">Cron</span>
                        <code className="text-text-primary">{selectedTask.cronExpression}</code>
                      </div>
                    )}
                    {selectedTask.intervalMinutes && (
                      <div className="flex justify-between">
                        <span className="text-text-secondary">Intervalo</span>
                        <span className="text-text-primary">{selectedTask.intervalMinutes} minutos</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Próxima Execução</span>
                      <span className="text-text-primary">{formatDateTime(selectedTask.nextRun)}</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <h4 className="font-semibold text-text-primary mb-3">Última Execução</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Data/Hora</span>
                      <span className="text-text-primary">{formatDateTime(selectedTask.lastRun)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Status</span>
                      {selectedTask.lastRunStatus === 'success' && <Badge variant="success">Sucesso</Badge>}
                      {selectedTask.lastRunStatus === 'failed' && <Badge variant="danger">Falhou</Badge>}
                      {selectedTask.lastRunStatus === 'running' && <Badge variant="info">Executando</Badge>}
                    </div>
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Duração</span>
                      <span className="text-text-primary">{formatDuration(selectedTask.lastRunDuration)}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <h4 className="font-semibold text-text-primary mb-3">Configurações</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Timeout</span>
                    <span className="text-text-primary">{formatDuration(selectedTask.timeout)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Retry em Falha</span>
                    <span className="text-text-primary">{selectedTask.retryOnFailure ? 'Sim' : 'Não'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Máx. Retries</span>
                    <span className="text-text-primary">{selectedTask.maxRetries}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Notificar Falha</span>
                    <span className="text-text-primary">{selectedTask.notifyOnFailure ? 'Sim' : 'Não'}</span>
                  </div>
                </div>
              </div>

              {selectedTask.tags.length > 0 && (
                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedTask.tags.map((tag, index) => (
                      <Badge key={index} variant="outline">{tag}</Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button className="flex-1">
                  <Play className="h-4 w-4 mr-2" />
                  Executar Agora
                </Button>
                {selectedTask.status === 'active' ? (
                  <Button variant="outline">
                    <Pause className="h-4 w-4 mr-2" />
                    Pausar
                  </Button>
                ) : (
                  <Button variant="outline">
                    <Play className="h-4 w-4 mr-2" />
                    Ativar
                  </Button>
                )}
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
                <Button variant="outline">
                  <History className="h-4 w-4 mr-2" />
                  Histórico
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Execution Detail Modal */}
        <Modal
          isOpen={showExecutionModal}
          onClose={() => setShowExecutionModal(false)}
          title="Detalhes da Execução"
          size="md"
        >
          {selectedExecution && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">{selectedExecution.taskName}</h3>
                  <p className="text-text-secondary">ID: {selectedExecution.id}</p>
                </div>
                {getExecutionStatusBadge(selectedExecution.status)}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Iniciado em</p>
                  <p className="text-text-primary">{formatDateTime(selectedExecution.startedAt)}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Finalizado em</p>
                  <p className="text-text-primary">{formatDateTime(selectedExecution.finishedAt)}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Duração</p>
                  <p className="text-text-primary">{formatDuration(selectedExecution.duration)}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Gatilho</p>
                  <p className="text-text-primary capitalize">{selectedExecution.trigger}</p>
                </div>
              </div>

              {selectedExecution.output && (
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm mb-2">Output</p>
                  <p className="text-text-primary">{selectedExecution.output}</p>
                </div>
              )}

              {selectedExecution.errorMessage && (
                <div className="p-4 rounded-lg bg-accent-danger/10 border border-accent-danger/30">
                  <p className="text-accent-danger text-sm mb-2">Erro</p>
                  <p className="text-text-primary">{selectedExecution.errorMessage}</p>
                </div>
              )}

              <div className="text-sm text-text-secondary">
                Executado por: {selectedExecution.triggeredBy}
                {selectedExecution.retryCount > 0 && ` (${selectedExecution.retryCount} retries)`}
              </div>

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button
                  className="flex-1"
                  onClick={() => {
                    setShowExecutionModal(false);
                    setShowLogsModal(true);
                  }}
                >
                  <Terminal className="h-4 w-4 mr-2" />
                  Ver Logs
                </Button>
                {selectedExecution.status === 'failed' && (
                  <Button variant="outline">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retry
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* Logs Modal */}
        <Modal
          isOpen={showLogsModal}
          onClose={() => setShowLogsModal(false)}
          title="Logs de Execução"
          size="lg"
        >
          <div className="space-y-4">
            {selectedExecution && (
              <div className="p-3 rounded-lg bg-bg-tertiary">
                <span className="text-text-secondary">Execução: </span>
                <span className="text-text-primary">{selectedExecution.taskName}</span>
                <span className="text-text-secondary"> - {selectedExecution.id}</span>
              </div>
            )}

            <div className="bg-bg-primary rounded-lg p-4 font-mono text-sm max-h-96 overflow-y-auto">
              {mockLogs.map((log) => (
                <div key={log.id} className="flex gap-3 py-1 hover:bg-bg-tertiary rounded">
                  <span className="text-text-muted whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleTimeString('pt-BR')}
                  </span>
                  <span className={`w-14 ${
                    log.level === 'error' ? 'text-accent-danger' :
                    log.level === 'warning' ? 'text-accent-warning' :
                    log.level === 'info' ? 'text-accent-info' :
                    'text-text-secondary'
                  }`}>
                    [{log.level.toUpperCase()}]
                  </span>
                  <span className="text-text-primary flex-1">{log.message}</span>
                </div>
              ))}
            </div>

            <div className="flex gap-3 pt-4 border-t border-border-subtle">
              <Button variant="outline" className="flex-1">
                <Download className="h-4 w-4 mr-2" />
                Baixar Logs
              </Button>
              <Button variant="outline">
                <Copy className="h-4 w-4 mr-2" />
                Copiar
              </Button>
            </div>
          </div>
        </Modal>

        {/* New Task Modal */}
        <Modal
          isOpen={showNewTaskModal}
          onClose={() => setShowNewTaskModal(false)}
          title="Criar Nova Tarefa"
          size="lg"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Nome da Tarefa
                </label>
                <Input placeholder="Ex: Relatório de Vendas Semanal" />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Descrição
                </label>
                <textarea
                  className="w-full px-4 py-2 rounded-lg bg-bg-tertiary border border-border-default text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-primary"
                  rows={2}
                  placeholder="Descreva o que esta tarefa faz..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Categoria
                </label>
                <Select
                  options={Object.entries(CATEGORIES).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))}
                  value="report"
                  onChange={() => {}}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Tipo de Gatilho
                </label>
                <Select
                  options={Object.entries(TRIGGER_TYPES).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))}
                  value="cron"
                  onChange={() => {}}
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Expressão Cron
                </label>
                <Input placeholder="0 8 * * *" />
                <p className="text-xs text-text-secondary mt-1">
                  Formato: minuto hora dia mês dia_semana
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Timeout (segundos)
                </label>
                <Input type="number" placeholder="300" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Máx. Retries
                </label>
                <Input type="number" placeholder="3" />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <input type="checkbox" id="retryOnFailure" className="rounded" defaultChecked />
                <label htmlFor="retryOnFailure" className="text-sm text-text-primary">
                  Tentar novamente em caso de falha
                </label>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="notifyOnFailure" className="rounded" defaultChecked />
                <label htmlFor="notifyOnFailure" className="text-sm text-text-primary">
                  Notificar por email em caso de falha
                </label>
              </div>
            </div>

            <div className="flex gap-3 pt-4 border-t border-border-subtle">
              <Button className="flex-1">
                <Plus className="h-4 w-4 mr-2" />
                Criar Tarefa
              </Button>
              <Button variant="outline" onClick={() => setShowNewTaskModal(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
