'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Terminal,
  Server,
  Wifi,
  WifiOff,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Shield,
  Key,
  Settings,
  Eye,
  Play,
  Pause,
  MoreHorizontal,
  RefreshCw,
  Lock,
  Unlock,
  Activity,
  Download,
  Upload,
  Monitor,
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
interface SSHConnection {
  id: string;
  name: string;
  host: string;
  port: number;
  username: string;
  deviceType: 'dvr' | 'nvr' | 'camera' | 'controller' | 'server' | 'other';
  location: string;
  status: 'connected' | 'disconnected' | 'error' | 'busy';
  lastConnection: string | null;
  uptime: string | null;
  commandsExecuted: number;
  authMethod: 'password' | 'key';
  createdAt: string;
}

interface CommandLog {
  id: string;
  connectionName: string;
  command: string;
  user: string;
  status: 'success' | 'error' | 'timeout';
  executionTime: number;
  timestamp: string;
}

// Mock Data
const connections: SSHConnection[] = [
  {
    id: '1',
    name: 'DVR Principal - Matriz',
    host: '192.168.1.101',
    port: 22,
    username: 'admin',
    deviceType: 'dvr',
    location: 'São Paulo - Matriz',
    status: 'connected',
    lastConnection: '2026-01-16 10:00',
    uptime: '45 dias',
    commandsExecuted: 1245,
    authMethod: 'key',
    createdAt: '2025-03-15',
  },
  {
    id: '2',
    name: 'NVR Filial - SP Sul',
    host: '192.168.2.50',
    port: 22,
    username: 'operator',
    deviceType: 'nvr',
    location: 'São Paulo - Zona Sul',
    status: 'connected',
    lastConnection: '2026-01-16 09:45',
    uptime: '30 dias',
    commandsExecuted: 856,
    authMethod: 'password',
    createdAt: '2025-06-20',
  },
  {
    id: '3',
    name: 'Controlador de Acesso',
    host: '192.168.1.200',
    port: 2222,
    username: 'root',
    deviceType: 'controller',
    location: 'Guarulhos - Portaria',
    status: 'busy',
    lastConnection: '2026-01-16 10:05',
    uptime: '60 dias',
    commandsExecuted: 2341,
    authMethod: 'key',
    createdAt: '2025-08-10',
  },
  {
    id: '4',
    name: 'Servidor de Backup',
    host: '10.0.0.100',
    port: 22,
    username: 'backup',
    deviceType: 'server',
    location: 'Data Center',
    status: 'disconnected',
    lastConnection: '2026-01-15 18:30',
    uptime: null,
    commandsExecuted: 456,
    authMethod: 'key',
    createdAt: '2025-01-05',
  },
];

const commandLogs: CommandLog[] = [
  { id: '1', connectionName: 'DVR Principal', command: 'systemctl status recording', user: 'admin', status: 'success', executionTime: 120, timestamp: '2026-01-16 10:05' },
  { id: '2', connectionName: 'NVR Filial', command: 'df -h', user: 'operator', status: 'success', executionTime: 85, timestamp: '2026-01-16 09:50' },
  { id: '3', connectionName: 'Controlador de Acesso', command: 'tail -f /var/log/access.log', user: 'root', status: 'success', executionTime: 5000, timestamp: '2026-01-16 10:05' },
  { id: '4', connectionName: 'Servidor de Backup', command: 'rsync -avz /data /backup', user: 'backup', status: 'error', executionTime: 30000, timestamp: '2026-01-15 18:30' },
];

const connectionStats = [
  { hour: '06h', active: 8, commands: 45 },
  { hour: '08h', active: 12, commands: 125 },
  { hour: '10h', active: 15, commands: 210 },
  { hour: '12h', active: 14, commands: 180 },
  { hour: '14h', active: 16, commands: 245 },
  { hour: '16h', active: 15, commands: 198 },
  { hour: '18h', active: 10, commands: 120 },
];

const tabs = [
  { id: 'connections', label: 'Conexões' },
  { id: 'commands', label: 'Comandos' },
  { id: 'terminal', label: 'Terminal' },
];

const deviceTypeLabels = {
  dvr: 'DVR',
  nvr: 'NVR',
  camera: 'Câmera IP',
  controller: 'Controlador',
  server: 'Servidor',
  other: 'Outro',
};

const deviceTypeColors = {
  dvr: '#3B82F6',
  nvr: '#10B981',
  camera: '#F59E0B',
  controller: '#8B5CF6',
  server: '#EF4444',
  other: '#6B7280',
};

const statusConfig = {
  connected: { label: 'Conectado', color: 'success', icon: Wifi },
  disconnected: { label: 'Desconectado', color: 'secondary', icon: WifiOff },
  error: { label: 'Erro', color: 'danger', icon: XCircle },
  busy: { label: 'Ocupado', color: 'warning', icon: Activity },
} as const;

const connectionColumns: Column<SSHConnection>[] = [
  {
    key: 'name',
    header: 'Dispositivo',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg" style={{ backgroundColor: `${deviceTypeColors[row.deviceType]}20` }}>
          <Terminal className="w-5 h-5" style={{ color: deviceTypeColors[row.deviceType] }} />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.host}:{row.port}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'deviceType',
    header: 'Tipo',
    render: (row) => <Badge variant="info">{deviceTypeLabels[row.deviceType]}</Badge>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      const Icon = config.icon;
      return (
        <Badge variant={config.color as any}>
          <Icon className="w-3 h-3 mr-1" />
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'authMethod',
    header: 'Autenticação',
    render: (row) => (
      <div className="flex items-center gap-2">
        {row.authMethod === 'key' ? <Key className="w-4 h-4 text-success" /> : <Lock className="w-4 h-4 text-warning" />}
        <span className="text-sm">{row.authMethod === 'key' ? 'Chave SSH' : 'Senha'}</span>
      </div>
    ),
  },
  {
    key: 'uptime',
    header: 'Uptime',
    render: (row) => <span className="text-sm">{row.uptime || '-'}</span>,
  },
  {
    key: 'commandsExecuted',
    header: 'Comandos',
    render: (row) => <span className="font-medium">{row.commandsExecuted.toLocaleString('pt-BR')}</span>,
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Abrir Terminal">
          <Terminal className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title={row.status === 'connected' ? 'Desconectar' : 'Conectar'}>
          {row.status === 'connected' || row.status === 'busy' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
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

const logColumns: Column<CommandLog>[] = [
  {
    key: 'timestamp',
    header: 'Data/Hora',
    render: (row) => <span className="text-sm">{row.timestamp}</span>,
  },
  {
    key: 'connectionName',
    header: 'Conexão',
    render: (row) => <span className="font-medium">{row.connectionName}</span>,
  },
  {
    key: 'command',
    header: 'Comando',
    render: (row) => (
      <code className="px-2 py-1 rounded bg-bg-secondary text-sm font-mono">{row.command}</code>
    ),
  },
  {
    key: 'user',
    header: 'Usuário',
    render: (row) => <span className="text-sm">{row.user}</span>,
  },
  {
    key: 'executionTime',
    header: 'Tempo',
    render: (row) => <span className="text-sm">{row.executionTime}ms</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={row.status === 'success' ? 'success' : row.status === 'error' ? 'danger' : 'warning'}>
        {row.status === 'success' ? 'Sucesso' : row.status === 'error' ? 'Erro' : 'Timeout'}
      </Badge>
    ),
  },
];

export function SSHGatewayPage() {
  const [activeTab, setActiveTab] = useState('connections');
  const [searchTerm, setSearchTerm] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [terminalInput, setTerminalInput] = useState('');

  // Stats
  const activeConnections = connections.filter((c) => c.status === 'connected' || c.status === 'busy').length;
  const totalCommands = connections.reduce((acc, c) => acc + c.commandsExecuted, 0);
  const errorConnections = connections.filter((c) => c.status === 'error').length;
  const keyAuthCount = connections.filter((c) => c.authMethod === 'key').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Gateway SSH</h1>
            <p className="text-text-secondary mt-1">Acesso remoto a equipamentos de segurança</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Reconectar Todos
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsAddModalOpen(true)}>
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
            <StatCard title="Total Comandos" value={totalCommands.toLocaleString('pt-BR')} icon={<Terminal className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Auth. por Chave" value={keyAuthCount} icon={<Key className="w-6 h-6" />} iconColor="info" />
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
                <h3 className="font-semibold">Atividade de Conexões (Hoje)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={connectionStats}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Line type="monotone" dataKey="active" stroke="#10B981" strokeWidth={2} name="Conexões Ativas" />
                    <Line type="monotone" dataKey="commands" stroke="#3B82F6" strokeWidth={2} name="Comandos/10" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Server className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Status das Conexões</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                {connections.map((conn) => {
                  const config = statusConfig[conn.status];
                  const Icon = config.icon;
                  return (
                    <div key={conn.id} className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary">
                      <div className="flex items-center gap-3">
                        <Icon className={`w-5 h-5 ${conn.status === 'connected' ? 'text-success' : conn.status === 'busy' ? 'text-warning' : conn.status === 'error' ? 'text-danger' : 'text-text-muted'}`} />
                        <div>
                          <p className="font-medium text-text-primary">{conn.name}</p>
                          <p className="text-xs text-text-muted">{conn.location}</p>
                        </div>
                      </div>
                      <Badge variant={config.color as any}>{config.label}</Badge>
                    </div>
                  );
                })}
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

        {activeTab === 'commands' && (
          <>
            <div className="flex items-center justify-end gap-3">
              <Input
                placeholder="Buscar comandos..."
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
                <DataTable columns={logColumns} data={commandLogs} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'terminal' && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-success" />
                  <h3 className="font-semibold">Terminal Web</h3>
                </div>
                <Select
                  options={connections.filter((c) => c.status === 'connected').map((c) => ({ value: c.id, label: c.name }))}
                  value=""
                  onChange={() => {}}
                  placeholder="Selecione uma conexão..."
                  className="w-64"
                />
              </div>
            </CardHeader>
            <CardBody>
              <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm min-h-[400px]">
                <div className="text-green-400 mb-2">Last login: Thu Jan 16 10:00:00 2026 from 192.168.1.50</div>
                <div className="text-white mb-1">$ systemctl status recording</div>
                <div className="text-gray-400 mb-1">● recording.service - Video Recording Service</div>
                <div className="text-gray-400 mb-1">   Loaded: loaded (/etc/systemd/system/recording.service; enabled)</div>
                <div className="text-green-400 mb-1">   Active: active (running) since Mon 2026-01-01 00:00:00 UTC</div>
                <div className="text-gray-400 mb-4">   Main PID: 1234 (recording)</div>
                <div className="flex items-center">
                  <span className="text-green-400">admin@dvr-principal:~$</span>
                  <input
                    type="text"
                    className="flex-1 bg-transparent border-none outline-none text-white ml-2"
                    value={terminalInput}
                    onChange={(e) => setTerminalInput(e.target.value)}
                    placeholder="Digite um comando..."
                  />
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Add Connection Modal */}
        <Modal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          title="Nova Conexão SSH"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsAddModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="secondary" leftIcon={<Shield className="w-4 h-4" />}>
                Testar Conexão
              </Button>
              <Button variant="primary">Salvar Conexão</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome da Conexão" placeholder="Ex: DVR Principal - Matriz" required />
            <Select
              label="Tipo de Dispositivo"
              options={[
                { value: 'dvr', label: 'DVR' },
                { value: 'nvr', label: 'NVR' },
                { value: 'camera', label: 'Câmera IP' },
                { value: 'controller', label: 'Controlador de Acesso' },
                { value: 'server', label: 'Servidor' },
                { value: 'other', label: 'Outro' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Host / IP" placeholder="192.168.1.100" required />
              <Input label="Porta" type="number" placeholder="22" defaultValue="22" required />
            </div>
            <Input label="Usuário" placeholder="admin" required />
            <Select
              label="Método de Autenticação"
              options={[
                { value: 'key', label: 'Chave SSH (Recomendado)' },
                { value: 'password', label: 'Senha' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />
            <Textarea label="Chave SSH Privada" placeholder="-----BEGIN RSA PRIVATE KEY-----" rows={4} />
            <Input label="Localização" placeholder="São Paulo - Matriz" />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
