'use client';

import { useState, useEffect } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  DataTable,
  type Column,
  StatCard,
  StatGrid,
  Badge,
  Modal,
  SimpleTabBar
} from '@/design-system/components';
import { motion } from 'framer-motion';
import {
  Activity,
  Monitor,
  Server,
  Database,
  Cpu,
  HardDrive,
  Wifi,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Zap,
  Users,
  Clock,
  TrendingUp,
  TrendingDown,
  Bell,
  Pause,
  Play,
  Settings
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

// Types
interface SystemMetric {
  timestamp: string;
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  requests: number;
  errors: number;
}

interface ServiceStatus {
  id: string;
  name: string;
  type: 'api' | 'database' | 'cache' | 'queue' | 'storage';
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  responseTime: number;
  lastCheck: string;
  endpoint: string;
  details: string;
}

interface ActiveConnection {
  id: string;
  userId: string;
  userName: string;
  connectionType: 'web' | 'mobile' | 'api';
  ipAddress: string;
  location: string;
  connectedAt: string;
  lastActivity: string;
  status: 'active' | 'idle';
}

interface RealtimeAlert {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  service: string;
  timestamp: string;
  acknowledged: boolean;
}

// Mock data
const generateMetricHistory = (): SystemMetric[] => {
  const now = new Date();
  return Array.from({ length: 30 }, (_, i) => ({
    timestamp: new Date(now.getTime() - (29 - i) * 60000).toISOString(),
    cpu: 35 + Math.random() * 30,
    memory: 55 + Math.random() * 20,
    disk: 42 + Math.random() * 5,
    network: 100 + Math.random() * 400,
    requests: 150 + Math.floor(Math.random() * 100),
    errors: Math.floor(Math.random() * 5)
  }));
};

const mockServices: ServiceStatus[] = [
  {
    id: '1',
    name: 'API Principal',
    type: 'api',
    status: 'healthy',
    uptime: 99.98,
    responseTime: 45,
    lastCheck: '2024-01-15T10:30:00',
    endpoint: 'https://api.conectaplus.com.br',
    details: 'Todas as rotas funcionando normalmente'
  },
  {
    id: '2',
    name: 'PostgreSQL',
    type: 'database',
    status: 'healthy',
    uptime: 99.99,
    responseTime: 12,
    lastCheck: '2024-01-15T10:30:00',
    endpoint: 'postgresql://db.conectaplus.com.br',
    details: '245 conexões ativas, pool saudável'
  },
  {
    id: '3',
    name: 'Redis Cache',
    type: 'cache',
    status: 'healthy',
    uptime: 99.95,
    responseTime: 2,
    lastCheck: '2024-01-15T10:30:00',
    endpoint: 'redis://cache.conectaplus.com.br',
    details: 'Hit rate: 94.5%, memória: 2.1GB/4GB'
  },
  {
    id: '4',
    name: 'RabbitMQ',
    type: 'queue',
    status: 'degraded',
    uptime: 98.50,
    responseTime: 85,
    lastCheck: '2024-01-15T10:30:00',
    endpoint: 'amqp://queue.conectaplus.com.br',
    details: 'Latência elevada, fila de notificações com backlog'
  },
  {
    id: '5',
    name: 'MinIO Storage',
    type: 'storage',
    status: 'healthy',
    uptime: 99.90,
    responseTime: 120,
    lastCheck: '2024-01-15T10:30:00',
    endpoint: 'https://storage.conectaplus.com.br',
    details: 'Espaço usado: 156GB/500GB'
  }
];

const mockConnections: ActiveConnection[] = [
  {
    id: '1',
    userId: 'user1',
    userName: 'João Silva',
    connectionType: 'web',
    ipAddress: '189.45.123.45',
    location: 'São Paulo, SP',
    connectedAt: '2024-01-15T08:00:00',
    lastActivity: '2024-01-15T10:28:00',
    status: 'active'
  },
  {
    id: '2',
    userId: 'user2',
    userName: 'Maria Santos',
    connectionType: 'mobile',
    ipAddress: '177.32.98.12',
    location: 'Rio de Janeiro, RJ',
    connectedAt: '2024-01-15T09:15:00',
    lastActivity: '2024-01-15T10:30:00',
    status: 'active'
  },
  {
    id: '3',
    userId: 'api_client_1',
    userName: 'Sistema Externo A',
    connectionType: 'api',
    ipAddress: '200.100.50.25',
    location: 'AWS us-east-1',
    connectedAt: '2024-01-15T00:00:00',
    lastActivity: '2024-01-15T10:29:55',
    status: 'active'
  },
  {
    id: '4',
    userId: 'user3',
    userName: 'Pedro Oliveira',
    connectionType: 'web',
    ipAddress: '187.65.43.21',
    location: 'Belo Horizonte, MG',
    connectedAt: '2024-01-15T07:30:00',
    lastActivity: '2024-01-15T10:15:00',
    status: 'idle'
  }
];

const mockAlerts: RealtimeAlert[] = [
  {
    id: '1',
    type: 'warning',
    message: 'Latência elevada na fila de notificações (85ms)',
    service: 'RabbitMQ',
    timestamp: '2024-01-15T10:25:00',
    acknowledged: false
  },
  {
    id: '2',
    type: 'info',
    message: 'Backup automático concluído com sucesso',
    service: 'PostgreSQL',
    timestamp: '2024-01-15T10:00:00',
    acknowledged: true
  },
  {
    id: '3',
    type: 'error',
    message: 'Falha temporária na conexão com gateway de pagamento',
    service: 'API Principal',
    timestamp: '2024-01-15T09:45:00',
    acknowledged: true
  },
  {
    id: '4',
    type: 'info',
    message: 'Cache invalidado para módulo de relatórios',
    service: 'Redis Cache',
    timestamp: '2024-01-15T09:30:00',
    acknowledged: true
  }
];

const tabs = [
  { value: 'overview', label: 'Visão Geral' },
  { value: 'services', label: 'Serviços' },
  { value: 'connections', label: 'Conexões' },
  { value: 'alerts', label: 'Alertas' }
];

export function RealtimeMonitoringPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState<SystemMetric[]>(generateMetricHistory());
  const [services] = useState<ServiceStatus[]>(mockServices);
  const [connections] = useState<ActiveConnection[]>(mockConnections);
  const [alerts, setAlerts] = useState<RealtimeAlert[]>(mockAlerts);
  const [isLive, setIsLive] = useState(true);
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<RealtimeAlert | null>(null);

  // Simulate real-time updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setMetrics(prev => {
        const newMetric: SystemMetric = {
          timestamp: new Date().toISOString(),
          cpu: 35 + Math.random() * 30,
          memory: 55 + Math.random() * 20,
          disk: 42 + Math.random() * 5,
          network: 100 + Math.random() * 400,
          requests: 150 + Math.floor(Math.random() * 100),
          errors: Math.floor(Math.random() * 5)
        };
        return [...prev.slice(1), newMetric];
      });
    }, 5000);

    return () => clearInterval(interval);
  }, [isLive]);

  // Stats
  const currentMetric = metrics[metrics.length - 1];
  const healthyServices = services.filter(s => s.status === 'healthy').length;
  const activeConnections = connections.filter(c => c.status === 'active').length;
  const unacknowledgedAlerts = alerts.filter(a => !a.acknowledged).length;

  const getStatusBadge = (status: string) => {
    const colors: Record<string, 'success' | 'warning' | 'danger'> = {
      healthy: 'success',
      degraded: 'warning',
      down: 'danger'
    };
    const labels: Record<string, string> = {
      healthy: 'Saudável',
      degraded: 'Degradado',
      down: 'Indisponível'
    };
    return <Badge variant={colors[status]}>{labels[status]}</Badge>;
  };

  const getServiceIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      api: <Server className="w-5 h-5" />,
      database: <Database className="w-5 h-5" />,
      cache: <HardDrive className="w-5 h-5" />,
      queue: <Activity className="w-5 h-5" />,
      storage: <HardDrive className="w-5 h-5" />
    };
    return icons[type];
  };

  const getConnectionTypeBadge = (type: string) => {
    const colors: Record<string, 'primary' | 'success' | 'info'> = {
      web: 'primary',
      mobile: 'success',
      api: 'info'
    };
    const labels: Record<string, string> = {
      web: 'Web',
      mobile: 'Mobile',
      api: 'API'
    };
    return <Badge variant={colors[type]}>{labels[type]}</Badge>;
  };

  const getAlertIcon = (type: string) => {
    if (type === 'error') return <XCircle className="text-red-500 w-5 h-5" />;
    if (type === 'warning') return <AlertTriangle className="text-yellow-500 w-5 h-5" />;
    return <CheckCircle className="text-blue-500 w-5 h-5" />;
  };

  const serviceColumns: Column<ServiceStatus>[] = [
    {
      key: 'name',
      header: 'Serviço',
      render: (service) => (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            service.status === 'healthy' ? 'bg-green-100' :
            service.status === 'degraded' ? 'bg-yellow-100' : 'bg-red-100'
          }`}>
            {getServiceIcon(service.type)}
          </div>
          <div>
            <p className="font-medium">{service.name}</p>
            <p className="text-sm text-gray-500 font-mono">{service.endpoint}</p>
          </div>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (service) => getStatusBadge(service.status)
    },
    {
      key: 'uptime',
      header: 'Uptime',
      render: (service) => (
        <span className={`font-medium ${
          service.uptime >= 99.9 ? 'text-green-600' :
          service.uptime >= 99 ? 'text-yellow-600' : 'text-red-600'
        }`}>
          {service.uptime.toFixed(2)}%
        </span>
      )
    },
    {
      key: 'responseTime',
      header: 'Tempo Resposta',
      render: (service) => (
        <span className={`${
          service.responseTime < 50 ? 'text-green-600' :
          service.responseTime < 100 ? 'text-yellow-600' : 'text-red-600'
        }`}>
          {service.responseTime}ms
        </span>
      )
    },
    {
      key: 'details',
      header: 'Detalhes',
      render: (service) => (
        <span className="text-sm text-gray-600">{service.details}</span>
      )
    },
    {
      key: 'lastCheck',
      header: 'Última Verificação',
      render: (service) => new Date(service.lastCheck).toLocaleTimeString('pt-BR')
    }
  ];

  const connectionColumns: Column<ActiveConnection>[] = [
    {
      key: 'userName',
      header: 'Usuário',
      render: (conn) => (
        <div>
          <p className="font-medium">{conn.userName}</p>
          <p className="text-sm text-gray-500">{conn.userId}</p>
        </div>
      )
    },
    {
      key: 'connectionType',
      header: 'Tipo',
      render: (conn) => getConnectionTypeBadge(conn.connectionType)
    },
    {
      key: 'ipAddress',
      header: 'IP',
      render: (conn) => (
        <span className="font-mono text-sm">{conn.ipAddress}</span>
      )
    },
    {
      key: 'location',
      header: 'Localização',
      render: (conn) => conn.location
    },
    {
      key: 'status',
      header: 'Status',
      render: (conn) => (
        <Badge variant={conn.status === 'active' ? 'success' : 'warning'}>
          {conn.status === 'active' ? 'Ativo' : 'Inativo'}
        </Badge>
      )
    },
    {
      key: 'connectedAt',
      header: 'Conectado há',
      render: (conn) => {
        const hours = Math.floor(
          (new Date().getTime() - new Date(conn.connectedAt).getTime()) / 3600000
        );
        return `${hours}h`;
      }
    },
    {
      key: 'lastActivity',
      header: 'Última Atividade',
      render: (conn) => new Date(conn.lastActivity).toLocaleTimeString('pt-BR')
    }
  ];

  const alertColumns: Column<RealtimeAlert>[] = [
    {
      key: 'type',
      header: '',
      render: (alert) => getAlertIcon(alert.type)
    },
    {
      key: 'message',
      header: 'Mensagem',
      render: (alert) => (
        <p className={!alert.acknowledged ? 'font-medium' : ''}>{alert.message}</p>
      )
    },
    {
      key: 'service',
      header: 'Serviço',
      render: (alert) => <Badge variant="info">{alert.service}</Badge>
    },
    {
      key: 'timestamp',
      header: 'Horário',
      render: (alert) => new Date(alert.timestamp).toLocaleTimeString('pt-BR')
    },
    {
      key: 'acknowledged',
      header: 'Status',
      render: (alert) => (
        alert.acknowledged ? (
          <Badge variant="success">Reconhecido</Badge>
        ) : (
          <Badge variant="warning">Pendente</Badge>
        )
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (alert) => (
        !alert.acknowledged && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setAlerts(prev => prev.map(a =>
                a.id === alert.id ? { ...a, acknowledged: true } : a
              ));
            }}
          >
            Reconhecer
          </Button>
        )
      )
    }
  ];

  const formatChartTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Monitoramento em Tempo Real</h1>
            <p className="text-gray-600">Acompanhe métricas e status do sistema em tempo real</p>
          </div>
          <div className="flex gap-2 items-center">
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${
              isLive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
              <span className="text-sm font-medium">{isLive ? 'AO VIVO' : 'PAUSADO'}</span>
            </div>
            <Button
              variant="outline"
              onClick={() => setIsLive(!isLive)}
            >
              {isLive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </Button>
            <Button variant="outline">
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <StatCard
            title="CPU"
            value={`${currentMetric.cpu.toFixed(1)}%`}
            icon={<Cpu className="w-6 h-6" />}
            iconColor={currentMetric.cpu > 70 ? 'danger' : currentMetric.cpu > 50 ? 'warning' : 'success'}
          />
          <StatCard
            title="Memória"
            value={`${currentMetric.memory.toFixed(1)}%`}
            icon={<HardDrive className="w-6 h-6" />}
            iconColor={currentMetric.memory > 80 ? 'danger' : currentMetric.memory > 60 ? 'warning' : 'success'}
          />
          <StatCard
            title="Serviços Saudáveis"
            value={`${healthyServices}/${services.length}`}
            icon={<Server className="w-6 h-6" />}
            iconColor={healthyServices === services.length ? 'success' : 'warning'}
          />
          <StatCard
            title="Conexões Ativas"
            value={activeConnections.toString()}
            icon={<Users className="w-6 h-6" />}
            iconColor="primary"
          />
        </StatGrid>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">CPU & Memória</h3>
                </CardHeader>
                <CardBody>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={metrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={formatChartTime}
                        interval="preserveStartEnd"
                      />
                      <YAxis domain={[0, 100]} />
                      <Tooltip
                        labelFormatter={(value) => formatChartTime(value as string)}
                        formatter={(value: number) => [`${value.toFixed(1)}%`]}
                      />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="cpu"
                        name="CPU"
                        stroke="#ef4444"
                        fill="#fee2e2"
                        strokeWidth={2}
                      />
                      <Area
                        type="monotone"
                        dataKey="memory"
                        name="Memória"
                        stroke="#3b82f6"
                        fill="#dbeafe"
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Requisições & Erros</h3>
                </CardHeader>
                <CardBody>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={metrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={formatChartTime}
                        interval="preserveStartEnd"
                      />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip
                        labelFormatter={(value) => formatChartTime(value as string)}
                      />
                      <Legend />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="requests"
                        name="Requisições"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="errors"
                        name="Erros"
                        stroke="#ef4444"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardBody>
              </Card>

              <Card className="lg:col-span-2">
                <CardHeader>
                  <h3 className="text-lg font-semibold">Tráfego de Rede (KB/s)</h3>
                </CardHeader>
                <CardBody>
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={metrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={formatChartTime}
                        interval="preserveStartEnd"
                      />
                      <YAxis />
                      <Tooltip
                        labelFormatter={(value) => formatChartTime(value as string)}
                        formatter={(value: number) => [`${value.toFixed(0)} KB/s`]}
                      />
                      <Area
                        type="monotone"
                        dataKey="network"
                        name="Tráfego"
                        stroke="#8b5cf6"
                        fill="#ede9fe"
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardBody>
              </Card>
            </div>
          )}

          {activeTab === 'services' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Status dos Serviços</h3>
                  <Button variant="outline" size="sm">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Verificar Todos
                  </Button>
                </div>
              </CardHeader>
              <CardBody>
                <DataTable columns={serviceColumns} data={services} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          )}

          {activeTab === 'connections' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Conexões Ativas</h3>
                  <div className="flex gap-2">
                    <Badge variant="primary">{connections.filter(c => c.connectionType === 'web').length} Web</Badge>
                    <Badge variant="success">{connections.filter(c => c.connectionType === 'mobile').length} Mobile</Badge>
                    <Badge variant="info">{connections.filter(c => c.connectionType === 'api').length} API</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <DataTable columns={connectionColumns} data={connections} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          )}

          {activeTab === 'alerts' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Alertas Recentes</h3>
                  {unacknowledgedAlerts > 0 && (
                    <Badge variant="danger">{unacknowledgedAlerts} pendentes</Badge>
                  )}
                </div>
              </CardHeader>
              <CardBody>
                <DataTable columns={alertColumns} data={alerts} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          )}
        </motion.div>

        {/* Quick Actions */}
        <Card>
          <CardBody>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-gray-500">Ações Rápidas:</span>
                <Button variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reiniciar Cache
                </Button>
                <Button variant="outline" size="sm">
                  <Database className="w-4 h-4 mr-2" />
                  Health Check
                </Button>
                <Button variant="outline" size="sm">
                  <Zap className="w-4 h-4 mr-2" />
                  Limpar Filas
                </Button>
              </div>
              <p className="text-sm text-gray-500">
                Última atualização: {new Date().toLocaleTimeString('pt-BR')}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>
    </MainLayout>
  );
}
