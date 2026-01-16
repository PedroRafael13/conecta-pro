'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  RefreshCw,
  Shield,
  Server,
  Wifi,
  WifiOff,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Activity,
  Settings,
  Eye,
  Play,
  Pause,
  MoreHorizontal,
  Download,
  Upload,
  Database,
  Zap,
  TrendingUp,
  Calendar,
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
interface SyncConnection {
  id: string;
  name: string;
  systemType: 'intelbras' | 'hikvision' | 'controlid' | 'custom';
  host: string;
  port: number;
  status: 'connected' | 'disconnected' | 'error' | 'syncing';
  lastSync: string | null;
  syncInterval: number;
  recordsSynced: number;
  pendingRecords: number;
  errorCount: number;
  createdAt: string;
}

interface SyncLog {
  id: string;
  connectionName: string;
  action: 'sync_started' | 'sync_completed' | 'sync_failed' | 'connection_lost' | 'records_imported';
  status: 'success' | 'warning' | 'error';
  message: string;
  recordsAffected: number;
  timestamp: string;
}

// Mock Data
const connections: SyncConnection[] = [
  {
    id: '1',
    name: 'Intelbras - Matriz',
    systemType: 'intelbras',
    host: '192.168.1.100',
    port: 8080,
    status: 'connected',
    lastSync: '2026-01-16 10:15',
    syncInterval: 5,
    recordsSynced: 45678,
    pendingRecords: 12,
    errorCount: 0,
    createdAt: '2025-03-15',
  },
  {
    id: '2',
    name: 'Hikvision - Filial SP',
    systemType: 'hikvision',
    host: '192.168.2.50',
    port: 8000,
    status: 'syncing',
    lastSync: '2026-01-16 10:10',
    syncInterval: 10,
    recordsSynced: 32145,
    pendingRecords: 145,
    errorCount: 2,
    createdAt: '2025-06-20',
  },
  {
    id: '3',
    name: 'Control iD - Portaria',
    systemType: 'controlid',
    host: '192.168.1.200',
    port: 3000,
    status: 'connected',
    lastSync: '2026-01-16 10:12',
    syncInterval: 5,
    recordsSynced: 18934,
    pendingRecords: 0,
    errorCount: 0,
    createdAt: '2025-08-10',
  },
  {
    id: '4',
    name: 'Sistema Legado',
    systemType: 'custom',
    host: '10.0.0.50',
    port: 5432,
    status: 'error',
    lastSync: '2026-01-15 18:30',
    syncInterval: 30,
    recordsSynced: 8756,
    pendingRecords: 523,
    errorCount: 15,
    createdAt: '2025-01-05',
  },
];

const syncLogs: SyncLog[] = [
  { id: '1', connectionName: 'Intelbras - Matriz', action: 'sync_completed', status: 'success', message: 'Sincronização concluída com sucesso', recordsAffected: 45, timestamp: '2026-01-16 10:15' },
  { id: '2', connectionName: 'Hikvision - Filial SP', action: 'sync_started', status: 'success', message: 'Iniciando sincronização', recordsAffected: 0, timestamp: '2026-01-16 10:10' },
  { id: '3', connectionName: 'Sistema Legado', action: 'sync_failed', status: 'error', message: 'Falha de conexão: timeout após 30s', recordsAffected: 0, timestamp: '2026-01-15 18:35' },
  { id: '4', connectionName: 'Control iD - Portaria', action: 'records_imported', status: 'success', message: 'Registros de acesso importados', recordsAffected: 128, timestamp: '2026-01-16 10:12' },
  { id: '5', connectionName: 'Hikvision - Filial SP', action: 'connection_lost', status: 'warning', message: 'Conexão perdida temporariamente', recordsAffected: 0, timestamp: '2026-01-16 08:45' },
];

const syncVolume = [
  { hour: '06h', records: 120 },
  { hour: '08h', records: 450 },
  { hour: '10h', records: 680 },
  { hour: '12h', records: 320 },
  { hour: '14h', records: 540 },
  { hour: '16h', records: 720 },
  { hour: '18h', records: 890 },
  { hour: '20h', records: 340 },
];

const syncHealth = [
  { day: 'Seg', success: 98, error: 2 },
  { day: 'Ter', success: 99, error: 1 },
  { day: 'Qua', success: 97, error: 3 },
  { day: 'Qui', success: 100, error: 0 },
  { day: 'Sex', success: 96, error: 4 },
  { day: 'Sáb', success: 99, error: 1 },
  { day: 'Dom', success: 100, error: 0 },
];

const tabs = [
  { id: 'connections', label: 'Conexões' },
  { id: 'logs', label: 'Logs de Sincronização' },
  { id: 'settings', label: 'Configurações' },
];

const systemTypeLabels = {
  intelbras: 'Intelbras',
  hikvision: 'Hikvision',
  controlid: 'Control iD',
  custom: 'Personalizado',
};

const systemTypeColors = {
  intelbras: '#00A651',
  hikvision: '#E4002B',
  controlid: '#1E3A5F',
  custom: '#6B7280',
};

const statusConfig = {
  connected: { label: 'Conectado', color: 'success', icon: Wifi },
  disconnected: { label: 'Desconectado', color: 'secondary', icon: WifiOff },
  error: { label: 'Erro', color: 'danger', icon: XCircle },
  syncing: { label: 'Sincronizando', color: 'info', icon: RefreshCw },
} as const;

const connectionColumns: Column<SyncConnection>[] = [
  {
    key: 'name',
    header: 'Conexão',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg" style={{ backgroundColor: `${systemTypeColors[row.systemType]}20` }}>
          <Server className="w-5 h-5" style={{ color: systemTypeColors[row.systemType] }} />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.host}:{row.port}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'systemType',
    header: 'Sistema',
    render: (row) => <Badge variant="info">{systemTypeLabels[row.systemType]}</Badge>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      const Icon = config.icon;
      return (
        <Badge variant={config.color as any}>
          <Icon className={`w-3 h-3 mr-1 ${row.status === 'syncing' ? 'animate-spin' : ''}`} />
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'lastSync',
    header: 'Última Sincronização',
    render: (row) => (
      <div className="flex items-center gap-2 text-sm">
        <Clock className="w-4 h-4 text-text-muted" />
        <span>{row.lastSync || 'Nunca'}</span>
      </div>
    ),
  },
  {
    key: 'recordsSynced',
    header: 'Registros',
    render: (row) => (
      <div>
        <p className="font-medium">{row.recordsSynced.toLocaleString('pt-BR')}</p>
        {row.pendingRecords > 0 && (
          <p className="text-xs text-warning">{row.pendingRecords} pendentes</p>
        )}
      </div>
    ),
  },
  {
    key: 'errorCount',
    header: 'Erros',
    render: (row) => (
      <Badge variant={row.errorCount > 0 ? 'danger' : 'success'}>
        {row.errorCount}
      </Badge>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Sincronizar Agora">
          <RefreshCw className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title={row.status === 'connected' ? 'Pausar' : 'Conectar'}>
          {row.status === 'connected' || row.status === 'syncing' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </Button>
        <Button variant="ghost" size="icon-sm" title="Configurar">
          <Settings className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const logColumns: Column<SyncLog>[] = [
  {
    key: 'timestamp',
    header: 'Data/Hora',
    render: (row) => (
      <div className="flex items-center gap-2 text-sm">
        <Calendar className="w-4 h-4 text-text-muted" />
        <span>{row.timestamp}</span>
      </div>
    ),
  },
  {
    key: 'connectionName',
    header: 'Conexão',
    render: (row) => <span className="font-medium">{row.connectionName}</span>,
  },
  {
    key: 'action',
    header: 'Ação',
    render: (row) => {
      const actionLabels = {
        sync_started: 'Sincronização Iniciada',
        sync_completed: 'Sincronização Concluída',
        sync_failed: 'Falha na Sincronização',
        connection_lost: 'Conexão Perdida',
        records_imported: 'Registros Importados',
      };
      return <span className="text-sm">{actionLabels[row.action]}</span>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={row.status === 'success' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'}>
        {row.status === 'success' ? 'Sucesso' : row.status === 'warning' ? 'Aviso' : 'Erro'}
      </Badge>
    ),
  },
  {
    key: 'message',
    header: 'Mensagem',
    render: (row) => <span className="text-sm text-text-secondary">{row.message}</span>,
  },
  {
    key: 'recordsAffected',
    header: 'Registros',
    render: (row) => (
      row.recordsAffected > 0 ? (
        <Badge variant="info">{row.recordsAffected}</Badge>
      ) : (
        <span className="text-text-muted">-</span>
      )
    ),
  },
];

export function GuardianSyncPage() {
  const [activeTab, setActiveTab] = useState('connections');
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newSystemType, setNewSystemType] = useState('');

  // Stats
  const activeConnections = connections.filter((c) => c.status === 'connected' || c.status === 'syncing').length;
  const totalRecords = connections.reduce((acc, c) => acc + c.recordsSynced, 0);
  const pendingRecords = connections.reduce((acc, c) => acc + c.pendingRecords, 0);
  const errorConnections = connections.filter((c) => c.status === 'error').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Sincronização de Sistemas</h1>
            <p className="text-text-secondary mt-1">Integração com sistemas de vigilância e controle de acesso</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Sincronizar Todos
            </Button>
            <Button variant="primary" leftIcon={<Server className="w-4 h-4" />} onClick={() => setIsAddModalOpen(true)}>
              Nova Conexão
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Conexões Ativas" value={activeConnections} icon={<Wifi className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Total Sincronizado" value={totalRecords.toLocaleString('pt-BR')} icon={<Database className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Pendentes" value={pendingRecords} icon={<Clock className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Com Erro" value={errorConnections} icon={<AlertTriangle className="w-6 h-6" />} iconColor="danger" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Volume de Sincronização (Hoje)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={syncVolume}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="records" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Registros" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Saúde das Sincronizações (Semana)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={syncHealth}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="day" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="success" fill="#10B981" stackId="a" name="Sucesso %" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="error" fill="#EF4444" stackId="a" name="Erro %" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Content */}
        {activeTab === 'connections' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input
                placeholder="Buscar conexões..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                Filtros
              </Button>
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable columns={connectionColumns} data={connections} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'logs' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input
                placeholder="Buscar logs..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
                Exportar
              </Button>
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable columns={logColumns} data={syncLogs} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'settings' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <h3 className="font-semibold">Configurações Globais</h3>
              </CardHeader>
              <CardBody className="space-y-4">
                <Input label="Intervalo Padrão de Sincronização (minutos)" type="number" defaultValue="5" />
                <Input label="Timeout de Conexão (segundos)" type="number" defaultValue="30" />
                <Input label="Máximo de Tentativas de Reconexão" type="number" defaultValue="3" />
                <div className="flex items-center justify-between p-4 rounded-lg bg-bg-secondary">
                  <div>
                    <p className="font-medium text-text-primary">Sincronização Automática</p>
                    <p className="text-sm text-text-muted">Sincronizar todos os sistemas automaticamente</p>
                  </div>
                  <Button variant="primary" size="sm">Ativado</Button>
                </div>
                <Button variant="primary" className="w-full">Salvar Configurações</Button>
              </CardBody>
            </Card>

            <Card>
              <CardHeader>
                <h3 className="font-semibold">Notificações</h3>
              </CardHeader>
              <CardBody className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg border border-border">
                  <div>
                    <p className="font-medium text-text-primary">Alertas de Erro</p>
                    <p className="text-sm text-text-muted">Notificar quando ocorrer erro de sincronização</p>
                  </div>
                  <Badge variant="success">Ativo</Badge>
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg border border-border">
                  <div>
                    <p className="font-medium text-text-primary">Conexão Perdida</p>
                    <p className="text-sm text-text-muted">Notificar quando uma conexão for perdida</p>
                  </div>
                  <Badge variant="success">Ativo</Badge>
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg border border-border">
                  <div>
                    <p className="font-medium text-text-primary">Relatório Diário</p>
                    <p className="text-sm text-text-muted">Enviar resumo diário de sincronizações</p>
                  </div>
                  <Badge variant="secondary">Inativo</Badge>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Add Connection Modal */}
        <Modal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          title="Nova Conexão"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsAddModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="secondary" leftIcon={<Zap className="w-4 h-4" />}>
                Testar Conexão
              </Button>
              <Button variant="primary">Salvar Conexão</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome da Conexão" placeholder="Ex: Intelbras - Matriz" required />
            <Select
              label="Tipo de Sistema"
              options={[
                { value: 'intelbras', label: 'Intelbras' },
                { value: 'hikvision', label: 'Hikvision' },
                { value: 'controlid', label: 'Control iD' },
                { value: 'custom', label: 'Personalizado' },
              ]}
              value={newSystemType}
              onChange={(value) => setNewSystemType(value)}
              placeholder="Selecione..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Host / IP" placeholder="192.168.1.100" required />
              <Input label="Porta" type="number" placeholder="8080" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Usuário" placeholder="admin" />
              <Input label="Senha" type="password" placeholder="********" />
            </div>
            <Input label="Intervalo de Sincronização (minutos)" type="number" placeholder="5" />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
