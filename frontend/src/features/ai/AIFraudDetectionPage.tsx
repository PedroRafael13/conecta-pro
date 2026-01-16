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
  type Column,
  Modal
} from '@/design-system/components';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Clock,
  TrendingUp,
  DollarSign,
  Users,
  MapPin,
  Fingerprint,
  Activity,
  FileText,
  Lock,
  Unlock,
  RefreshCw,
  Filter,
  Download,
  Search,
  Zap,
  Target
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
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

interface FraudAlert {
  id: string;
  type: 'time_fraud' | 'location_fraud' | 'document_fraud' | 'expense_fraud' | 'identity_fraud';
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'resolved' | 'dismissed';
  employee: string;
  employeeId: string;
  description: string;
  detectedAt: string;
  confidence: number;
  value?: string;
  location?: string;
  evidence: string[];
}

const mockAlerts: FraudAlert[] = [
  {
    id: '1',
    type: 'time_fraud',
    severity: 'critical',
    status: 'open',
    employee: 'José Silva',
    employeeId: 'EMP-1234',
    description: 'Registro de ponto fora da área geográfica permitida em múltiplas ocasiões',
    detectedAt: '2024-01-15 14:30',
    confidence: 94,
    location: '15km do posto de trabalho',
    evidence: ['3 registros suspeitos', 'GPS inconsistente', 'Padrão repetitivo']
  },
  {
    id: '2',
    type: 'expense_fraud',
    severity: 'high',
    status: 'investigating',
    employee: 'Maria Santos',
    employeeId: 'EMP-2345',
    description: 'Reembolso de despesas com valores acima da média para a função',
    detectedAt: '2024-01-15 10:15',
    confidence: 87,
    value: 'R$ 2.450,00',
    evidence: ['Valor 3x acima da média', 'Comprovantes duplicados', 'Fornecedor não cadastrado']
  },
  {
    id: '3',
    type: 'document_fraud',
    severity: 'medium',
    status: 'resolved',
    employee: 'Pedro Oliveira',
    employeeId: 'EMP-3456',
    description: 'Atestado médico com possíveis irregularidades detectadas pelo OCR',
    detectedAt: '2024-01-14 16:45',
    confidence: 72,
    evidence: ['CRM não encontrado', 'Assinatura inconsistente']
  },
  {
    id: '4',
    type: 'identity_fraud',
    severity: 'critical',
    status: 'open',
    employee: 'Carlos Ferreira',
    employeeId: 'EMP-4567',
    description: 'Tentativa de registro biométrico com digital não cadastrada',
    detectedAt: '2024-01-15 06:00',
    confidence: 98,
    evidence: ['Biometria não reconhecida', 'Horário atípico', 'Múltiplas tentativas']
  },
  {
    id: '5',
    type: 'location_fraud',
    severity: 'low',
    status: 'dismissed',
    employee: 'Ana Costa',
    employeeId: 'EMP-5678',
    description: 'Check-in via app fora do raio permitido',
    detectedAt: '2024-01-13 08:30',
    confidence: 45,
    location: '500m do posto',
    evidence: ['GPS impreciso', 'Primeira ocorrência']
  }
];

const mockTrendData = [
  { date: 'Jan', detected: 12, prevented: 10, loss: 2 },
  { date: 'Fev', detected: 15, prevented: 14, loss: 1 },
  { date: 'Mar', detected: 8, prevented: 8, loss: 0 },
  { date: 'Abr', detected: 18, prevented: 16, loss: 2 },
  { date: 'Mai', detected: 10, prevented: 10, loss: 0 },
  { date: 'Jun', detected: 6, prevented: 6, loss: 0 }
];

const mockTypeData = [
  { name: 'Ponto', value: 35 },
  { name: 'Despesas', value: 25 },
  { name: 'Documentos', value: 20 },
  { name: 'Localização', value: 15 },
  { name: 'Identidade', value: 5 }
];

const COLORS = ['#ef4444', '#f59e0b', '#6366f1', '#8b5cf6', '#64748b'];

const tabs = [
  { value: 'overview', label: 'Visão Geral', icon: <Shield className="h-4 w-4" /> },
  { value: 'alerts', label: 'Alertas', icon: <AlertTriangle className="h-4 w-4" /> },
  { value: 'patterns', label: 'Padrões', icon: <Activity className="h-4 w-4" /> },
  { value: 'rules', label: 'Regras', icon: <Target className="h-4 w-4" /> }
];

export function AIFraudDetectionPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<FraudAlert | null>(null);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'time_fraud': return <Clock className="h-5 w-5 text-red-400" />;
      case 'expense_fraud': return <DollarSign className="h-5 w-5 text-amber-400" />;
      case 'document_fraud': return <FileText className="h-5 w-5 text-blue-400" />;
      case 'location_fraud': return <MapPin className="h-5 w-5 text-purple-400" />;
      case 'identity_fraud': return <Fingerprint className="h-5 w-5 text-red-400" />;
      default: return <Shield className="h-5 w-5" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'time_fraud': return 'Fraude de Ponto';
      case 'expense_fraud': return 'Fraude de Despesas';
      case 'document_fraud': return 'Documento Fraudulento';
      case 'location_fraud': return 'Fraude de Localização';
      case 'identity_fraud': return 'Fraude de Identidade';
      default: return type;
    }
  };

  const columns: Column<FraudAlert>[] = [
    {
      key: 'type',
      header: 'Tipo',
      render: (alert) => (
        <div className="flex items-center gap-2">
          {getTypeIcon(alert.type)}
          <span className="text-text-primary">{getTypeLabel(alert.type)}</span>
        </div>
      )
    },
    {
      key: 'employee',
      header: 'Colaborador',
      render: (alert) => (
        <div>
          <span className="font-medium text-text-primary">{alert.employee}</span>
          <p className="text-sm text-text-secondary">{alert.employeeId}</p>
        </div>
      )
    },
    {
      key: 'description',
      header: 'Descrição',
      render: (alert) => (
        <span className="text-text-secondary truncate max-w-xs block">
          {alert.description}
        </span>
      )
    },
    {
      key: 'severity',
      header: 'Severidade',
      render: (alert) => (
        <Badge variant={
          alert.severity === 'critical' ? 'danger' :
          alert.severity === 'high' ? 'warning' :
          alert.severity === 'medium' ? 'info' : 'success'
        }>
          {alert.severity === 'critical' ? 'Crítico' :
           alert.severity === 'high' ? 'Alto' :
           alert.severity === 'medium' ? 'Médio' : 'Baixo'}
        </Badge>
      )
    },
    {
      key: 'confidence',
      header: 'Confiança',
      render: (alert) => (
        <div className="flex items-center gap-2">
          <div className="w-16 bg-bg-primary rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                alert.confidence >= 80 ? 'bg-red-500' :
                alert.confidence >= 60 ? 'bg-amber-500' : 'bg-green-500'
              }`}
              style={{ width: `${alert.confidence}%` }}
            />
          </div>
          <span className="text-sm text-text-primary">{alert.confidence}%</span>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (alert) => (
        <Badge variant={
          alert.status === 'open' ? 'danger' :
          alert.status === 'investigating' ? 'warning' :
          alert.status === 'resolved' ? 'success' : 'info'
        }>
          {alert.status === 'open' ? 'Aberto' :
           alert.status === 'investigating' ? 'Investigando' :
           alert.status === 'resolved' ? 'Resolvido' : 'Descartado'}
        </Badge>
      )
    },
    {
      key: 'detectedAt',
      header: 'Detectado',
      render: (alert) => (
        <span className="text-text-secondary text-sm">{alert.detectedAt}</span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (alert) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setSelectedAlert(alert);
            setShowDetailModal(true);
          }}
        >
          <Eye className="h-4 w-4" />
        </Button>
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Detecção de Fraudes</h1>
            <p className="text-text-secondary mt-1">Sistema de prevenção e detecção de fraudes com IA</p>
          </div>
          <div className="flex items-center gap-3">
            {
            <div className="flex items-center gap-3">
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtrar
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Button>
                <RefreshCw className="h-4 w-4 mr-2" />
                Executar Análise
              </Button>
            </div>
          }
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Alertas Ativos"
            value="8"
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
            change={-3}
            changeLabel="vs semana passada"
          />
          <StatCard
            title="Taxa de Detecção"
            value="98.5%"
            icon={<Target className="h-5 w-5" />}
            iconColor="success"
            change={2.1}
            changeLabel="vs mês anterior"
          />
          <StatCard
            title="Perdas Evitadas"
            value="R$ 156K"
            icon={<Shield className="h-5 w-5" />}
            iconColor="primary"
            change={45}
            changeLabel="este trimestre"
          />
          <StatCard
            title="Tempo de Resposta"
            value="4.2h"
            icon={<Zap className="h-5 w-5" />}
            iconColor="warning"
            change={-22}
            changeLabel="mais rápido"
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
            {/* Trend Chart */}
            <Card className="lg:col-span-2 p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Tendência de Fraudes
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockTrendData}>
                  <defs>
                    <linearGradient id="colorDetected" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorPrevented" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis dataKey="date" stroke="#64748b" />
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
                    dataKey="detected"
                    stroke="#f59e0b"
                    fill="url(#colorDetected)"
                    name="Detectados"
                  />
                  <Area
                    type="monotone"
                    dataKey="prevented"
                    stroke="#10b981"
                    fill="url(#colorPrevented)"
                    name="Prevenidos"
                  />
                  <Line
                    type="monotone"
                    dataKey="loss"
                    stroke="#ef4444"
                    strokeWidth={2}
                    name="Perdas"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            {/* Fraud Types */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Tipos de Fraude
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={mockTypeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {mockTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            {/* Critical Alerts */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Alertas Críticos
              </h3>
              <div className="space-y-4">
                {mockAlerts.filter(a => a.severity === 'critical' && a.status === 'open').map((alert) => (
                  <div key={alert.id} className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        {getTypeIcon(alert.type)}
                        <div>
                          <h4 className="font-medium text-text-primary">{alert.employee}</h4>
                          <p className="text-sm text-text-secondary mt-1">{alert.description}</p>
                          <p className="text-xs text-text-secondary mt-2">
                            Confiança: {alert.confidence}% | {alert.detectedAt}
                          </p>
                        </div>
                      </div>
                      <Button size="sm" onClick={() => {
                        setSelectedAlert(alert);
                        setShowDetailModal(true);
                      }}>
                        Investigar
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'alerts' && (
          <Card className="p-6">
            <DataTable<FraudAlert>
              data={mockAlerts}
              columns={columns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'patterns' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Padrões Detectados
              </h3>
              <div className="space-y-4">
                {[
                  { pattern: 'Registro de ponto em horários atípicos', occurrences: 23, risk: 'high' },
                  { pattern: 'Múltiplos reembolsos no mesmo dia', occurrences: 12, risk: 'medium' },
                  { pattern: 'Documentos com mesmo fornecedor', occurrences: 8, risk: 'low' },
                  { pattern: 'Login de IPs diferentes', occurrences: 45, risk: 'medium' },
                  { pattern: 'Alterações de banco após pagamento', occurrences: 3, risk: 'high' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                    <div>
                      <span className="text-text-primary">{item.pattern}</span>
                      <p className="text-sm text-text-secondary">{item.occurrences} ocorrências</p>
                    </div>
                    <Badge variant={
                      item.risk === 'high' ? 'danger' :
                      item.risk === 'medium' ? 'warning' : 'success'
                    }>
                      {item.risk === 'high' ? 'Alto Risco' :
                       item.risk === 'medium' ? 'Médio Risco' : 'Baixo Risco'}
                    </Badge>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Funcionários Monitorados
              </h3>
              <div className="space-y-4">
                {mockAlerts.filter(a => a.status === 'open' || a.status === 'investigating').map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-accent-primary/20 rounded-full flex items-center justify-center">
                        <Users className="h-5 w-5 text-accent-primary" />
                      </div>
                      <div>
                        <span className="text-text-primary font-medium">{alert.employee}</span>
                        <p className="text-sm text-text-secondary">{alert.employeeId}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={alert.status === 'open' ? 'danger' : 'warning'}>
                        {alert.status === 'open' ? 'Alerta Ativo' : 'Em Investigação'}
                      </Badge>
                      <p className="text-xs text-text-secondary mt-1">
                        {alert.evidence.length} evidências
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'rules' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { name: 'Distância Máxima', description: 'Alerta se registro de ponto > 500m do posto', active: true, triggers: 45 },
              { name: 'Valor de Despesa', description: 'Alerta se reembolso > 3x média da função', active: true, triggers: 12 },
              { name: 'Horário Atípico', description: 'Alerta se registro fora do turno ± 2h', active: true, triggers: 23 },
              { name: 'Biometria Falha', description: 'Alerta após 3 tentativas falhas', active: true, triggers: 8 },
              { name: 'Documento Duplicado', description: 'Detecta documentos com mesmo hash', active: true, triggers: 5 },
              { name: 'IP Suspeito', description: 'Alerta se login de IP não cadastrado', active: false, triggers: 0 }
            ].map((rule, idx) => (
              <Card key={idx} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-lg ${rule.active ? 'bg-green-500/10' : 'bg-gray-500/10'}`}>
                    {rule.active ? <Lock className="h-6 w-6 text-green-400" /> : <Unlock className="h-6 w-6 text-gray-400" />}
                  </div>
                  <Badge variant={rule.active ? 'success' : 'info'}>
                    {rule.active ? 'Ativa' : 'Inativa'}
                  </Badge>
                </div>
                <h3 className="font-semibold text-text-primary">{rule.name}</h3>
                <p className="text-sm text-text-secondary mt-1">{rule.description}</p>
                <div className="mt-4 pt-4 border-t border-border-subtle">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Disparos (30d)</span>
                    <span className="text-text-primary font-medium">{rule.triggers}</span>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="w-full mt-4">
                  Configurar
                </Button>
              </Card>
            ))}
          </div>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes do Alerta"
        >
          {selectedAlert && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 bg-bg-tertiary rounded-lg">
                {getTypeIcon(selectedAlert.type)}
                <div>
                  <h4 className="font-medium text-text-primary">{getTypeLabel(selectedAlert.type)}</h4>
                  <p className="text-sm text-text-secondary">{selectedAlert.detectedAt}</p>
                </div>
                <Badge variant={
                  selectedAlert.severity === 'critical' ? 'danger' :
                  selectedAlert.severity === 'high' ? 'warning' : 'info'
                } className="ml-auto">
                  {selectedAlert.severity === 'critical' ? 'Crítico' :
                   selectedAlert.severity === 'high' ? 'Alto' : 'Médio'}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-secondary text-sm">Colaborador</span>
                  <p className="font-medium text-text-primary">{selectedAlert.employee}</p>
                  <p className="text-sm text-text-secondary">{selectedAlert.employeeId}</p>
                </div>
                <div className="p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-secondary text-sm">Confiança</span>
                  <p className="text-2xl font-bold text-text-primary">{selectedAlert.confidence}%</p>
                </div>
              </div>

              <div className="p-3 bg-bg-tertiary rounded-lg">
                <span className="text-text-secondary text-sm">Descrição</span>
                <p className="text-text-primary mt-1">{selectedAlert.description}</p>
              </div>

              <div className="p-3 bg-bg-tertiary rounded-lg">
                <span className="text-text-secondary text-sm">Evidências</span>
                <ul className="mt-2 space-y-1">
                  {selectedAlert.evidence.map((ev, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-text-primary">
                      <CheckCircle className="h-4 w-4 text-amber-400" />
                      {ev}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  <XCircle className="h-4 w-4 mr-2" />
                  Descartar
                </Button>
                <Button>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Confirmar Fraude
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
