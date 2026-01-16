'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Download,
  Eye,
  Clock,
  User,
  Activity,
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  Database,
  Settings,
  Lock,
  Unlock,
  LogIn,
  LogOut,
  Edit,
  Trash2,
  Plus,
  MoreHorizontal,
  Calendar,
  ChevronDown,
  RefreshCw,
  Terminal,
  Server,
  Globe,
  Smartphone,
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
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

// Types
interface AuditLog {
  id: string;
  timestamp: string;
  user: string;
  userEmail: string;
  action: 'login' | 'logout' | 'create' | 'read' | 'update' | 'delete' | 'export' | 'permission_change' | 'config_change';
  module: string;
  resource: string;
  resourceId: string;
  ipAddress: string;
  userAgent: string;
  status: 'success' | 'failure' | 'warning';
  details: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

// Mock Data
const auditLogs: AuditLog[] = [
  {
    id: '1',
    timestamp: '2026-01-16T10:30:45',
    user: 'Ana Costa',
    userEmail: 'ana.costa@empresa.com',
    action: 'login',
    module: 'Autenticação',
    resource: 'Sessão',
    resourceId: 'session_abc123',
    ipAddress: '192.168.1.100',
    userAgent: 'Chrome/120.0 Windows',
    status: 'success',
    details: 'Login bem-sucedido via MFA',
    riskLevel: 'low',
  },
  {
    id: '2',
    timestamp: '2026-01-16T10:25:30',
    user: 'Carlos Lima',
    userEmail: 'carlos.lima@empresa.com',
    action: 'export',
    module: 'Financeiro',
    resource: 'Relatório',
    resourceId: 'report_456',
    ipAddress: '192.168.1.105',
    userAgent: 'Firefox/121.0 MacOS',
    status: 'success',
    details: 'Exportação de relatório financeiro Q4',
    riskLevel: 'medium',
  },
  {
    id: '3',
    timestamp: '2026-01-16T10:20:15',
    user: 'Roberto Silva',
    userEmail: 'roberto.silva@empresa.com',
    action: 'permission_change',
    module: 'Administração',
    resource: 'Usuário',
    resourceId: 'user_789',
    ipAddress: '192.168.1.110',
    userAgent: 'Edge/120.0 Windows',
    status: 'success',
    details: 'Alteração de permissões: adicionado acesso ao módulo Financeiro',
    riskLevel: 'high',
  },
  {
    id: '4',
    timestamp: '2026-01-16T10:15:00',
    user: 'Desconhecido',
    userEmail: 'unknown@external.com',
    action: 'login',
    module: 'Autenticação',
    resource: 'Sessão',
    resourceId: 'session_xyz',
    ipAddress: '45.33.102.15',
    userAgent: 'Unknown Bot',
    status: 'failure',
    details: 'Tentativa de login falhou - credenciais inválidas (5 tentativas)',
    riskLevel: 'critical',
  },
  {
    id: '5',
    timestamp: '2026-01-16T10:10:30',
    user: 'Maria Oliveira',
    userEmail: 'maria.oliveira@empresa.com',
    action: 'delete',
    module: 'LGPD',
    resource: 'Dados Pessoais',
    resourceId: 'data_321',
    ipAddress: '192.168.1.115',
    userAgent: 'Chrome/120.0 Windows',
    status: 'success',
    details: 'Exclusão de dados conforme solicitação LGPD #2026-001',
    riskLevel: 'medium',
  },
  {
    id: '6',
    timestamp: '2026-01-16T10:05:00',
    user: 'Sistema',
    userEmail: 'system@empresa.com',
    action: 'config_change',
    module: 'Segurança',
    resource: 'Configuração',
    resourceId: 'config_ssl',
    ipAddress: '127.0.0.1',
    userAgent: 'System/Automated',
    status: 'success',
    details: 'Renovação automática do certificado SSL',
    riskLevel: 'low',
  },
  {
    id: '7',
    timestamp: '2026-01-16T09:55:45',
    user: 'Pedro Santos',
    userEmail: 'pedro.santos@empresa.com',
    action: 'update',
    module: 'GED',
    resource: 'Documento',
    resourceId: 'doc_654',
    ipAddress: '192.168.1.120',
    userAgent: 'Safari/17.0 iOS',
    status: 'success',
    details: 'Atualização do documento "Contrato ABC"',
    riskLevel: 'low',
  },
];

const activityTrend = [
  { hour: '00h', events: 12 },
  { hour: '04h', events: 5 },
  { hour: '08h', events: 145 },
  { hour: '12h', events: 98 },
  { hour: '16h', events: 234 },
  { hour: '20h', events: 67 },
];

const actionDistribution = [
  { action: 'Login', count: 245 },
  { action: 'Read', count: 890 },
  { action: 'Update', count: 156 },
  { action: 'Create', count: 89 },
  { action: 'Delete', count: 23 },
  { action: 'Export', count: 45 },
];

const tabs = [
  { id: 'all', label: 'Todos os Logs' },
  { id: 'security', label: 'Segurança' },
  { id: 'data', label: 'Dados' },
  { id: 'system', label: 'Sistema' },
];

const actionIcons = {
  login: LogIn,
  logout: LogOut,
  create: Plus,
  read: Eye,
  update: Edit,
  delete: Trash2,
  export: Download,
  permission_change: Shield,
  config_change: Settings,
};

const actionLabels = {
  login: 'Login',
  logout: 'Logout',
  create: 'Criação',
  read: 'Leitura',
  update: 'Atualização',
  delete: 'Exclusão',
  export: 'Exportação',
  permission_change: 'Permissão',
  config_change: 'Configuração',
};

const statusColors = {
  success: 'success',
  failure: 'danger',
  warning: 'warning',
} as const;

const riskColors = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
  critical: 'danger',
} as const;

const riskLabels = {
  low: 'Baixo',
  medium: 'Médio',
  high: 'Alto',
  critical: 'Crítico',
};

const columns: Column<AuditLog>[] = [
  {
    key: 'timestamp',
    header: 'Data/Hora',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-text-muted" />
        <div>
          <p className="text-sm font-medium">{new Date(row.timestamp).toLocaleTimeString('pt-BR')}</p>
          <p className="text-xs text-text-muted">{new Date(row.timestamp).toLocaleDateString('pt-BR')}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'user',
    header: 'Usuário',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.user} size="xs" />
        <div>
          <p className="text-sm font-medium">{row.user}</p>
          <p className="text-xs text-text-muted">{row.userEmail}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'action',
    header: 'Ação',
    render: (row) => {
      const Icon = actionIcons[row.action];
      return (
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg ${
            row.status === 'success' ? 'bg-success/10' :
            row.status === 'failure' ? 'bg-danger/10' : 'bg-warning/10'
          }`}>
            <Icon className={`w-4 h-4 ${
              row.status === 'success' ? 'text-success' :
              row.status === 'failure' ? 'text-danger' : 'text-warning'
            }`} />
          </div>
          <span className="text-sm">{actionLabels[row.action]}</span>
        </div>
      );
    },
  },
  {
    key: 'module',
    header: 'Módulo',
    render: (row) => <Badge variant="neutral">{row.module}</Badge>,
  },
  {
    key: 'details',
    header: 'Detalhes',
    render: (row) => (
      <p className="text-sm text-text-secondary line-clamp-1 max-w-xs">{row.details}</p>
    ),
  },
  {
    key: 'riskLevel',
    header: 'Risco',
    render: (row) => (
      <Badge variant={riskColors[row.riskLevel]} size="sm">
        {riskLabels[row.riskLevel]}
      </Badge>
    ),
  },
  {
    key: 'ipAddress',
    header: 'IP',
    render: (row) => (
      <span className="font-mono text-xs text-text-muted">{row.ipAddress}</span>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
        <Eye className="w-4 h-4" />
      </Button>
    ),
  },
];

export function AuditLogsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [dateFilter, setDateFilter] = useState('today');

  const filteredLogs = auditLogs.filter((log) => {
    const matchesSearch =
      log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.module.toLowerCase().includes(searchTerm.toLowerCase());

    if (activeTab === 'security') {
      return matchesSearch && ['login', 'logout', 'permission_change'].includes(log.action);
    }
    if (activeTab === 'data') {
      return matchesSearch && ['create', 'read', 'update', 'delete', 'export'].includes(log.action);
    }
    if (activeTab === 'system') {
      return matchesSearch && log.user === 'Sistema';
    }
    return matchesSearch;
  });

  // Stats
  const totalEvents = auditLogs.length;
  const securityEvents = auditLogs.filter(l => l.riskLevel === 'high' || l.riskLevel === 'critical').length;
  const failedEvents = auditLogs.filter(l => l.status === 'failure').length;
  const uniqueUsers = new Set(auditLogs.map(l => l.user)).size;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Logs de Auditoria
            </h1>
            <p className="text-text-secondary mt-1">
              Monitoramento e rastreabilidade de todas as atividades do sistema
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              options={[
                { value: 'today', label: 'Hoje' },
                { value: 'week', label: 'Última Semana' },
                { value: 'month', label: 'Último Mês' },
                { value: 'custom', label: 'Personalizado' },
              ]}
              value={dateFilter}
              onChange={(value) => setDateFilter(value)}
              className="w-40"
            />
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Atualizar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total de Eventos"
              value={totalEvents.toLocaleString('pt-BR')}
              icon={<Activity className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Eventos de Risco"
              value={securityEvents}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Falhas"
              value={failedEvents}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Usuários Ativos"
              value={uniqueUsers}
              icon={<User className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Atividade por Hora</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={activityTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-bg-secondary)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '8px',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="events"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      dot={{ fill: '#3B82F6' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Distribuição por Ação</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={actionDistribution} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis type="number" stroke="var(--color-text-muted)" />
                    <YAxis type="category" dataKey="action" stroke="var(--color-text-muted)" width={60} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-bg-secondary)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar dataKey="count" fill="#10B981" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Real-time Alerts */}
        {securityEvents > 0 && (
          <Card className="border-l-4 border-l-danger">
            <CardBody className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-danger/10">
                    <AlertTriangle className="w-5 h-5 text-danger" />
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">Alertas de Segurança Ativos</p>
                    <p className="text-sm text-text-muted">
                      {securityEvents} eventos de risco detectados nas últimas 24 horas
                    </p>
                  </div>
                </div>
                <Button variant="danger" size="sm">Ver Alertas</Button>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
          <div className="flex items-center gap-3">
            <Input
              placeholder="Buscar nos logs..."
              leftIcon={<Search className="w-4 h-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
            <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
              Filtros
            </Button>
          </div>
        </div>

        {/* Logs Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredLogs}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedLog(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Log Detail Modal */}
        <Modal
          isOpen={!!selectedLog}
          onClose={() => setSelectedLog(null)}
          title="Detalhes do Log"
          size="lg"
          footer={
            <Button variant="secondary" onClick={() => setSelectedLog(null)}>
              Fechar
            </Button>
          }
        >
          {selectedLog && (
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center gap-4 p-4 rounded-lg bg-bg-secondary">
                <div className={`p-3 rounded-lg ${
                  selectedLog.status === 'success' ? 'bg-success/10' :
                  selectedLog.status === 'failure' ? 'bg-danger/10' : 'bg-warning/10'
                }`}>
                  {(() => {
                    const Icon = actionIcons[selectedLog.action];
                    return <Icon className={`w-6 h-6 ${
                      selectedLog.status === 'success' ? 'text-success' :
                      selectedLog.status === 'failure' ? 'text-danger' : 'text-warning'
                    }`} />;
                  })()}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-text-primary">{actionLabels[selectedLog.action]}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant={statusColors[selectedLog.status]}>
                      {selectedLog.status === 'success' ? 'Sucesso' : selectedLog.status === 'failure' ? 'Falha' : 'Alerta'}
                    </Badge>
                    <Badge variant={riskColors[selectedLog.riskLevel]} size="sm">
                      Risco {riskLabels[selectedLog.riskLevel]}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <div className="flex items-center gap-2 mb-1">
                    <User className="w-4 h-4 text-text-muted" />
                    <span className="text-sm text-text-muted">Usuário</span>
                  </div>
                  <p className="font-medium">{selectedLog.user}</p>
                  <p className="text-sm text-text-muted">{selectedLog.userEmail}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="w-4 h-4 text-text-muted" />
                    <span className="text-sm text-text-muted">Data/Hora</span>
                  </div>
                  <p className="font-medium">{new Date(selectedLog.timestamp).toLocaleString('pt-BR')}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <div className="flex items-center gap-2 mb-1">
                    <Database className="w-4 h-4 text-text-muted" />
                    <span className="text-sm text-text-muted">Recurso</span>
                  </div>
                  <p className="font-medium">{selectedLog.resource}</p>
                  <p className="text-sm text-text-muted font-mono">{selectedLog.resourceId}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <div className="flex items-center gap-2 mb-1">
                    <Server className="w-4 h-4 text-text-muted" />
                    <span className="text-sm text-text-muted">Módulo</span>
                  </div>
                  <p className="font-medium">{selectedLog.module}</p>
                </div>
              </div>

              {/* Description */}
              <div className="p-4 rounded-lg border border-border">
                <h5 className="font-medium text-text-primary mb-2">Descrição</h5>
                <p className="text-text-secondary">{selectedLog.details}</p>
              </div>

              {/* Technical Details */}
              <div className="p-4 rounded-lg bg-bg-secondary">
                <h5 className="font-medium text-text-primary mb-3">Informações Técnicas</h5>
                <div className="space-y-2 font-mono text-sm">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-text-muted" />
                    <span className="text-text-muted">IP:</span>
                    <span>{selectedLog.ipAddress}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Smartphone className="w-4 h-4 text-text-muted" />
                    <span className="text-text-muted">User Agent:</span>
                    <span>{selectedLog.userAgent}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
