'use client';

import React, { useState, useEffect } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  StatCard,
  SimpleTabBar
} from '@/design-system/components';
import {
  Activity,
  Server,
  Database,
  Cpu,
  HardDrive,
  Wifi,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Clock,
  TrendingUp,
  Zap,
  Globe,
  Shield,
  BarChart2,
  Settings,
  Bell
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

interface ServiceStatus {
  id: string;
  name: string;
  type: 'api' | 'database' | 'cache' | 'queue' | 'storage' | 'external';
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  responseTime: number;
  lastCheck: string;
  url?: string;
}

const mockServices: ServiceStatus[] = [
  { id: '1', name: 'API Principal', type: 'api', status: 'healthy', uptime: 99.98, responseTime: 45, lastCheck: '2s atrás' },
  { id: '2', name: 'PostgreSQL', type: 'database', status: 'healthy', uptime: 99.99, responseTime: 12, lastCheck: '5s atrás' },
  { id: '3', name: 'Redis Cache', type: 'cache', status: 'healthy', uptime: 99.95, responseTime: 2, lastCheck: '3s atrás' },
  { id: '4', name: 'Celery Workers', type: 'queue', status: 'degraded', uptime: 98.5, responseTime: 150, lastCheck: '10s atrás' },
  { id: '5', name: 'AWS S3', type: 'storage', status: 'healthy', uptime: 99.99, responseTime: 85, lastCheck: '8s atrás' },
  { id: '6', name: 'WhatsApp API', type: 'external', status: 'healthy', uptime: 99.7, responseTime: 320, lastCheck: '15s atrás' },
  { id: '7', name: 'SEFAZ', type: 'external', status: 'down', uptime: 95.2, responseTime: 0, lastCheck: '1m atrás' },
  { id: '8', name: 'Email SMTP', type: 'external', status: 'healthy', uptime: 99.9, responseTime: 125, lastCheck: '12s atrás' }
];

const mockMetricsData = Array.from({ length: 30 }, (_, i) => ({
  time: `${i}:00`,
  cpu: Math.floor(20 + Math.random() * 40),
  memory: Math.floor(40 + Math.random() * 30),
  requests: Math.floor(100 + Math.random() * 200),
  errors: Math.floor(Math.random() * 5)
}));

const mockIncidents = [
  { id: '1', title: 'SEFAZ - Timeout na conexão', service: 'SEFAZ', severity: 'high', status: 'investigating', startedAt: '14:30', duration: '15 min' },
  { id: '2', title: 'Celery Workers - Alta latência', service: 'Celery', severity: 'medium', status: 'monitoring', startedAt: '13:45', duration: '60 min' },
  { id: '3', title: 'Redis - Memória alta', service: 'Redis', severity: 'low', status: 'resolved', startedAt: '10:00', duration: '30 min' }
];

const tabs = [
  { value: 'overview', label: 'Visão Geral', icon: <Activity className="h-4 w-4" /> },
  { value: 'services', label: 'Serviços', icon: <Server className="h-4 w-4" /> },
  { value: 'metrics', label: 'Métricas', icon: <BarChart2 className="h-4 w-4" /> },
  { value: 'incidents', label: 'Incidentes', icon: <AlertTriangle className="h-4 w-4" /> }
];

export function MonitoringPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        setLastUpdate(new Date());
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getServiceIcon = (type: string) => {
    switch (type) {
      case 'api': return <Globe className="h-5 w-5" />;
      case 'database': return <Database className="h-5 w-5" />;
      case 'cache': return <Zap className="h-5 w-5" />;
      case 'queue': return <Clock className="h-5 w-5" />;
      case 'storage': return <HardDrive className="h-5 w-5" />;
      case 'external': return <Wifi className="h-5 w-5" />;
      default: return <Server className="h-5 w-5" />;
    }
  };

  const healthyServices = mockServices.filter(s => s.status === 'healthy').length;
  const degradedServices = mockServices.filter(s => s.status === 'degraded').length;
  const downServices = mockServices.filter(s => s.status === 'down').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Monitoramento</h1>
            <p className="text-text-secondary mt-1">Status em tempo real de todos os serviços</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <Clock className="h-4 w-4" />
              Última atualização: {lastUpdate.toLocaleTimeString('pt-BR')}
            </div>
            <Button
              variant={autoRefresh ? 'primary' : 'outline'}
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
              Auto-refresh
            </Button>
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Configurar
            </Button>
          </div>
        </div>

        {/* Overall Status */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className={`p-4 border-2 ${
            downServices > 0 ? 'border-red-500/50 bg-red-500/5' :
            degradedServices > 0 ? 'border-amber-500/50 bg-amber-500/5' :
            'border-green-500/50 bg-green-500/5'
          }`}>
            <div className="flex items-center gap-3">
              {downServices > 0 ? (
                <XCircle className="h-8 w-8 text-red-400" />
              ) : degradedServices > 0 ? (
                <AlertTriangle className="h-8 w-8 text-amber-400" />
              ) : (
                <CheckCircle className="h-8 w-8 text-green-400" />
              )}
              <div>
                <h3 className={`text-lg font-semibold ${
                  downServices > 0 ? 'text-red-400' :
                  degradedServices > 0 ? 'text-amber-400' :
                  'text-green-400'
                }`}>
                  {downServices > 0 ? 'Sistema com Falhas' :
                   degradedServices > 0 ? 'Parcialmente Operacional' :
                   'Todos Operacionais'}
                </h3>
                <p className="text-sm text-text-secondary">
                  {healthyServices}/{mockServices.length} serviços saudáveis
                </p>
              </div>
            </div>
          </Card>

          <StatCard
            title="Uptime (30d)"
            value="99.85%"
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="success"
            change={0.12}
            changeLabel="vs mês anterior"
          />
          <StatCard
            title="Tempo de Resposta"
            value="48ms"
            icon={<Zap className="h-5 w-5" />}
            iconColor="primary"
            change={-8}
            changeLabel="mais rápido"
          />
          <StatCard
            title="Incidentes Abertos"
            value="2"
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="warning"
            change={-1}
            changeLabel="vs ontem"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Services Status */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Status dos Serviços
              </h3>
              <div className="space-y-3">
                {mockServices.map((service) => (
                  <div key={service.id} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${
                        service.status === 'healthy' ? 'bg-green-500/10 text-green-400' :
                        service.status === 'degraded' ? 'bg-amber-500/10 text-amber-400' :
                        'bg-red-500/10 text-red-400'
                      }`}>
                        {getServiceIcon(service.type)}
                      </div>
                      <div>
                        <span className="text-text-primary font-medium">{service.name}</span>
                        <p className="text-sm text-text-secondary">{service.lastCheck}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-text-secondary text-sm">
                        {service.responseTime > 0 ? `${service.responseTime}ms` : '-'}
                      </span>
                      <Badge variant={
                        service.status === 'healthy' ? 'success' :
                        service.status === 'degraded' ? 'warning' : 'danger'
                      }>
                        {service.status === 'healthy' ? 'OK' :
                         service.status === 'degraded' ? 'Lento' : 'Offline'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Real-time Metrics */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Métricas em Tempo Real
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockMetricsData.slice(-20)}>
                  <defs>
                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis dataKey="time" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="cpu"
                    stroke="#6366f1"
                    fill="url(#colorCpu)"
                    name="CPU %"
                  />
                  <Area
                    type="monotone"
                    dataKey="memory"
                    stroke="#10b981"
                    fill="url(#colorMemory)"
                    name="Memória %"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            {/* Recent Incidents */}
            <Card className="lg:col-span-2 p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Incidentes Recentes
              </h3>
              <div className="space-y-3">
                {mockIncidents.map((incident) => (
                  <div key={incident.id} className={`p-4 rounded-lg border ${
                    incident.status === 'investigating' ? 'bg-red-500/10 border-red-500/20' :
                    incident.status === 'monitoring' ? 'bg-amber-500/10 border-amber-500/20' :
                    'bg-green-500/10 border-green-500/20'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-text-primary">{incident.title}</h4>
                          <Badge variant={
                            incident.severity === 'high' ? 'danger' :
                            incident.severity === 'medium' ? 'warning' : 'info'
                          }>
                            {incident.severity === 'high' ? 'Alta' :
                             incident.severity === 'medium' ? 'Média' : 'Baixa'}
                          </Badge>
                        </div>
                        <p className="text-sm text-text-secondary mt-1">
                          Serviço: {incident.service} • Início: {incident.startedAt} • Duração: {incident.duration}
                        </p>
                      </div>
                      <Badge variant={
                        incident.status === 'investigating' ? 'danger' :
                        incident.status === 'monitoring' ? 'warning' : 'success'
                      }>
                        {incident.status === 'investigating' ? 'Investigando' :
                         incident.status === 'monitoring' ? 'Monitorando' : 'Resolvido'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'services' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {mockServices.map((service) => (
              <Card key={service.id} className={`p-6 border-2 ${
                service.status === 'healthy' ? 'border-green-500/20' :
                service.status === 'degraded' ? 'border-amber-500/20' :
                'border-red-500/20'
              }`}>
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-lg ${
                    service.status === 'healthy' ? 'bg-green-500/10' :
                    service.status === 'degraded' ? 'bg-amber-500/10' :
                    'bg-red-500/10'
                  }`}>
                    <span className={
                      service.status === 'healthy' ? 'text-green-400' :
                      service.status === 'degraded' ? 'text-amber-400' :
                      'text-red-400'
                    }>
                      {getServiceIcon(service.type)}
                    </span>
                  </div>
                  <Badge variant={
                    service.status === 'healthy' ? 'success' :
                    service.status === 'degraded' ? 'warning' : 'danger'
                  }>
                    {service.status === 'healthy' ? 'Saudável' :
                     service.status === 'degraded' ? 'Degradado' : 'Offline'}
                  </Badge>
                </div>

                <h3 className="font-semibold text-text-primary">{service.name}</h3>
                <p className="text-sm text-text-secondary capitalize">{service.type}</p>

                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Uptime</span>
                    <span className="text-text-primary font-medium">{service.uptime}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Latência</span>
                    <span className="text-text-primary font-medium">
                      {service.responseTime > 0 ? `${service.responseTime}ms` : '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Último check</span>
                    <span className="text-text-primary">{service.lastCheck}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                CPU & Memória
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={mockMetricsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis dataKey="time" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="cpu" stroke="#6366f1" strokeWidth={2} name="CPU %" />
                  <Line type="monotone" dataKey="memory" stroke="#10b981" strokeWidth={2} name="Memória %" />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Requisições & Erros
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockMetricsData}>
                  <defs>
                    <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis dataKey="time" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="requests"
                    stroke="#8b5cf6"
                    fill="url(#colorRequests)"
                    name="Requisições"
                  />
                  <Line type="monotone" dataKey="errors" stroke="#ef4444" strokeWidth={2} name="Erros" />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            <Card className="lg:col-span-2 p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Recursos do Sistema
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="h-5 w-5 text-accent-primary" />
                    <span className="text-text-secondary">CPU</span>
                  </div>
                  <p className="text-2xl font-bold text-text-primary">42%</p>
                  <div className="w-full bg-bg-primary rounded-full h-2 mt-2">
                    <div className="bg-accent-primary h-2 rounded-full" style={{ width: '42%' }} />
                  </div>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="h-5 w-5 text-green-400" />
                    <span className="text-text-secondary">Memória</span>
                  </div>
                  <p className="text-2xl font-bold text-text-primary">68%</p>
                  <div className="w-full bg-bg-primary rounded-full h-2 mt-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '68%' }} />
                  </div>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <HardDrive className="h-5 w-5 text-amber-400" />
                    <span className="text-text-secondary">Disco</span>
                  </div>
                  <p className="text-2xl font-bold text-text-primary">54%</p>
                  <div className="w-full bg-bg-primary rounded-full h-2 mt-2">
                    <div className="bg-amber-500 h-2 rounded-full" style={{ width: '54%' }} />
                  </div>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Wifi className="h-5 w-5 text-blue-400" />
                    <span className="text-text-secondary">Rede</span>
                  </div>
                  <p className="text-2xl font-bold text-text-primary">12 MB/s</p>
                  <div className="w-full bg-bg-primary rounded-full h-2 mt-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '24%' }} />
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'incidents' && (
          <Card className="p-6">
            <div className="space-y-4">
              {mockIncidents.concat([
                { id: '4', title: 'API - Pico de latência', service: 'API', severity: 'low', status: 'resolved', startedAt: '09:00', duration: '15 min' },
                { id: '5', title: 'Database - Conexões esgotadas', service: 'PostgreSQL', severity: 'high', status: 'resolved', startedAt: 'Ontem 22:30', duration: '45 min' }
              ]).map((incident) => (
                <Card key={incident.id} className={`p-4 ${
                  incident.status === 'investigating' ? 'border-red-500/30' :
                  incident.status === 'monitoring' ? 'border-amber-500/30' :
                  'border-green-500/30'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-3 rounded-lg ${
                        incident.status === 'investigating' ? 'bg-red-500/10' :
                        incident.status === 'monitoring' ? 'bg-amber-500/10' :
                        'bg-green-500/10'
                      }`}>
                        {incident.status === 'investigating' ? (
                          <XCircle className="h-6 w-6 text-red-400" />
                        ) : incident.status === 'monitoring' ? (
                          <AlertTriangle className="h-6 w-6 text-amber-400" />
                        ) : (
                          <CheckCircle className="h-6 w-6 text-green-400" />
                        )}
                      </div>
                      <div>
                        <h4 className="font-medium text-text-primary">{incident.title}</h4>
                        <p className="text-sm text-text-secondary mt-1">
                          Serviço afetado: {incident.service}
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-sm text-text-secondary">
                          <span>Início: {incident.startedAt}</span>
                          <span>Duração: {incident.duration}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <Badge variant={
                        incident.severity === 'high' ? 'danger' :
                        incident.severity === 'medium' ? 'warning' : 'info'
                      }>
                        {incident.severity === 'high' ? 'Alta' :
                         incident.severity === 'medium' ? 'Média' : 'Baixa'}
                      </Badge>
                      <Badge variant={
                        incident.status === 'investigating' ? 'danger' :
                        incident.status === 'monitoring' ? 'warning' : 'success'
                      }>
                        {incident.status === 'investigating' ? 'Investigando' :
                         incident.status === 'monitoring' ? 'Monitorando' : 'Resolvido'}
                      </Badge>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
