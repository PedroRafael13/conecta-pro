'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Database,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  RefreshCw,
  Download,
  Settings,
  Search,
  Filter,
  BarChart3,
  PieChart,
  TrendingUp,
  Shield,
  Zap,
  Clock,
  Target,
  FileText,
  Users,
  Building2,
  Calendar,
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
  Progress,
  Tabs,
  Tab,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/design-system/components';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

// Types
interface DataQualityMetric {
  id: string;
  name: string;
  category: string;
  score: number;
  issues: number;
  lastCheck: string;
  trend: 'up' | 'down' | 'stable';
}

interface DataIssue {
  id: string;
  table: string;
  field: string;
  type: 'missing' | 'invalid' | 'duplicate' | 'inconsistent';
  count: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  suggestion?: string;
}

// Mock Data
const mockMetrics: DataQualityMetric[] = [
  { id: '1', name: 'Completude', category: 'Integridade', score: 94.5, issues: 156, lastCheck: '2026-01-16T10:00:00', trend: 'up' },
  { id: '2', name: 'Consistência', category: 'Integridade', score: 89.2, issues: 234, lastCheck: '2026-01-16T10:00:00', trend: 'stable' },
  { id: '3', name: 'Unicidade', category: 'Integridade', score: 97.8, issues: 45, lastCheck: '2026-01-16T10:00:00', trend: 'up' },
  { id: '4', name: 'Validade', category: 'Precisão', score: 91.3, issues: 189, lastCheck: '2026-01-16T10:00:00', trend: 'down' },
  { id: '5', name: 'Atualidade', category: 'Precisão', score: 86.7, issues: 312, lastCheck: '2026-01-16T10:00:00', trend: 'stable' },
  { id: '6', name: 'Conformidade', category: 'Compliance', score: 98.1, issues: 28, lastCheck: '2026-01-16T10:00:00', trend: 'up' },
];

const mockIssues: DataIssue[] = [
  {
    id: '1',
    table: 'clientes',
    field: 'email',
    type: 'invalid',
    count: 45,
    severity: 'high',
    description: 'Emails com formato inválido detectados',
    suggestion: 'Validar e corrigir formato de emails',
  },
  {
    id: '2',
    table: 'funcionarios',
    field: 'cpf',
    type: 'duplicate',
    count: 12,
    severity: 'critical',
    description: 'CPFs duplicados encontrados',
    suggestion: 'Verificar registros duplicados e unificar',
  },
  {
    id: '3',
    table: 'contratos',
    field: 'data_fim',
    type: 'missing',
    count: 89,
    severity: 'medium',
    description: 'Data de fim não preenchida',
    suggestion: 'Preencher datas de fim dos contratos',
  },
  {
    id: '4',
    table: 'pagamentos',
    field: 'valor',
    type: 'inconsistent',
    count: 23,
    severity: 'high',
    description: 'Valores inconsistentes com contratos',
    suggestion: 'Revisar valores de pagamentos',
  },
  {
    id: '5',
    table: 'enderecos',
    field: 'cep',
    type: 'invalid',
    count: 156,
    severity: 'low',
    description: 'CEPs com formato incorreto',
    suggestion: 'Aplicar correção automática de CEPs',
  },
];

const qualityByCategory = [
  { name: 'Integridade', value: 93.8, color: '#6366f1' },
  { name: 'Precisão', value: 89.0, color: '#10b981' },
  { name: 'Compliance', value: 98.1, color: '#f59e0b' },
];

const qualityTrend = [
  { date: '09/01', score: 88 },
  { date: '10/01', score: 89 },
  { date: '11/01', score: 90 },
  { date: '12/01', score: 91 },
  { date: '13/01', score: 92 },
  { date: '14/01', score: 91 },
  { date: '15/01', score: 93 },
];

const issuesByType = [
  { type: 'Ausentes', count: 312, color: '#f59e0b' },
  { type: 'Inválidos', count: 234, color: '#ef4444' },
  { type: 'Duplicados', count: 89, color: '#8b5cf6' },
  { type: 'Inconsistentes', count: 156, color: '#3b82f6' },
];

const severityConfig = {
  low: { label: 'Baixo', color: 'success' as const },
  medium: { label: 'Médio', color: 'warning' as const },
  high: { label: 'Alto', color: 'danger' as const },
  critical: { label: 'Crítico', color: 'danger' as const },
};

const typeConfig = {
  missing: { label: 'Ausente', icon: AlertCircle },
  invalid: { label: 'Inválido', icon: AlertTriangle },
  duplicate: { label: 'Duplicado', icon: Users },
  inconsistent: { label: 'Inconsistente', icon: RefreshCw },
};

export function DataQualityPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const overallScore = Math.round(
    mockMetrics.reduce((sum, m) => sum + m.score, 0) / mockMetrics.length
  );

  const totalIssues = mockMetrics.reduce((sum, m) => sum + m.issues, 0);

  const handleRunAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => setIsAnalyzing(false), 3000);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Database className="w-8 h-8 text-accent-primary" />
              Qualidade de Dados
            </h1>
            <p className="text-text-secondary mt-1">
              Monitoramento e correção automática de qualidade de dados
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar Relatório
            </Button>
            <Button
              variant="primary"
              leftIcon={<RefreshCw className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />}
              onClick={handleRunAnalysis}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? 'Analisando...' : 'Executar Análise'}
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Score Geral"
              value={`${overallScore}%`}
              change={2.3}
              icon={<Target className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Total de Issues"
              value={totalIssues}
              change={-15}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Tabelas Analisadas"
              value={24}
              icon={<FileText className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Última Análise"
              value="10:00"
              icon={<Clock className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="overview" label="Visão Geral" />
          <Tab value="issues" label="Problemas" />
          <Tab value="metrics" label="Métricas" />
          <Tab value="automation" label="Automação" />
        </Tabs>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-3 gap-6">
            {/* Score by Category */}
            <Card className="col-span-2">
              <CardHeader title="Qualidade por Categoria" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={qualityByCategory}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            {/* Issues by Type */}
            <Card>
              <CardHeader title="Issues por Tipo" />
              <CardBody>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={issuesByType}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={70}
                        dataKey="count"
                        nameKey="type"
                      >
                        {issuesByType.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-2 gap-2 mt-4">
                  {issuesByType.map((item) => (
                    <div key={item.type} className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-xs text-text-muted">{item.type}</span>
                      <span className="text-xs text-text-primary ml-auto">{item.count}</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Quality Trend */}
            <Card className="col-span-3">
              <CardHeader title="Tendência de Qualidade" subtitle="Últimos 7 dias" />
              <CardBody>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={qualityTrend}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[80, 100]} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="score" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'issues' && (
          <Card>
            <CardHeader
              title="Problemas Detectados"
              subtitle={`${mockIssues.length} issues encontradas`}
              action={
                <Button variant="primary" size="sm">
                  Corrigir Selecionados
                </Button>
              }
            />
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tabela/Campo</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Registros</TableHead>
                  <TableHead>Severidade</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Ação</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockIssues.map((issue) => {
                  const TypeIcon = typeConfig[issue.type].icon;
                  return (
                    <TableRow key={issue.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium text-text-primary">{issue.table}</p>
                          <p className="text-xs text-text-muted">{issue.field}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" leftIcon={<TypeIcon className="w-3 h-3" />}>
                          {typeConfig[issue.type].label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium text-text-primary">{issue.count}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={severityConfig[issue.severity].color}>
                          {severityConfig[issue.severity].label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <p className="text-sm text-text-primary">{issue.description}</p>
                          {issue.suggestion && (
                            <p className="text-xs text-accent-primary mt-1">
                              💡 {issue.suggestion}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button variant="secondary" size="sm">
                          Corrigir
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </Card>
        )}

        {activeTab === 'metrics' && (
          <div className="grid grid-cols-2 gap-6">
            {mockMetrics.map((metric) => (
              <Card key={metric.id}>
                <CardBody>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="font-medium text-text-primary">{metric.name}</p>
                      <p className="text-xs text-text-muted">{metric.category}</p>
                    </div>
                    <Badge
                      variant={metric.trend === 'up' ? 'success' : metric.trend === 'down' ? 'danger' : 'secondary'}
                    >
                      {metric.trend === 'up' ? '↑' : metric.trend === 'down' ? '↓' : '→'}
                    </Badge>
                  </div>
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-3xl font-bold text-text-primary">{metric.score}%</p>
                      <p className="text-sm text-text-muted">{metric.issues} issues</p>
                    </div>
                    <div className="w-32">
                      <Progress
                        value={metric.score}
                        color={metric.score >= 90 ? 'success' : metric.score >= 70 ? 'warning' : 'danger'}
                      />
                    </div>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'automation' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Regras de Correção Automática" />
              <CardBody>
                <div className="space-y-4">
                  {[
                    { name: 'Correção de CEPs', enabled: true, lastRun: '10:00' },
                    { name: 'Formatação de telefones', enabled: true, lastRun: '10:00' },
                    { name: 'Validação de emails', enabled: true, lastRun: '10:00' },
                    { name: 'Remoção de duplicados', enabled: false, lastRun: 'Nunca' },
                    { name: 'Preenchimento de campos vazios', enabled: false, lastRun: 'Nunca' },
                  ].map((rule, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${rule.enabled ? 'bg-green-500' : 'bg-gray-500'}`} />
                        <span className="text-sm text-text-primary">{rule.name}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-xs text-text-muted">Última: {rule.lastRun}</span>
                        <input type="checkbox" defaultChecked={rule.enabled} className="toggle" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Agendamento de Análise" />
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-text-primary">Frequência</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>A cada hora</option>
                      <option>A cada 6 horas</option>
                      <option>Diariamente</option>
                      <option>Semanalmente</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-text-primary">Horário preferido</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>Qualquer horário</option>
                      <option>Horário comercial</option>
                      <option>Fora do horário comercial</option>
                      <option>Madrugada</option>
                    </select>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Notificar por email</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Correção automática</span>
                    <input type="checkbox" className="toggle" />
                  </div>
                  <Button variant="primary" className="w-full">
                    Salvar Configurações
                  </Button>
                </div>
              </CardBody>
            </Card>
          </div>
        )}
      </div>
    </MainLayout>
  );
}

export default DataQualityPage;
