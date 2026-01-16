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
  Modal,
  Select
} from '@/design-system/components';
import {
  Settings,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  DollarSign,
  Calendar,
  Edit,
  Trash2,
  Eye,
  Play,
  Pause,
  Copy,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Percent,
  FileText,
  Users,
  Building2,
  Zap
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

// Types
interface BillingRule {
  id: string;
  name: string;
  description: string;
  type: 'recurring' | 'one-time' | 'usage-based' | 'tiered';
  trigger: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'on-demand';
  baseValue: number;
  currency: string;
  status: 'active' | 'inactive' | 'draft';
  appliedTo: number;
  lastExecuted: string;
  nextExecution: string;
  createdAt: string;
}

interface BillingExecution {
  id: string;
  ruleId: string;
  ruleName: string;
  executedAt: string;
  status: 'success' | 'partial' | 'failed';
  processedCount: number;
  totalValue: number;
  errors: number;
}

// Mock data
const mockRules: BillingRule[] = [
  {
    id: '1',
    name: 'Mensalidade Padrão',
    description: 'Cobrança mensal de serviços básicos',
    type: 'recurring',
    trigger: 'Início do mês',
    frequency: 'monthly',
    baseValue: 1500,
    currency: 'BRL',
    status: 'active',
    appliedTo: 234,
    lastExecuted: '2026-01-01',
    nextExecution: '2026-02-01',
    createdAt: '2025-01-15'
  },
  {
    id: '2',
    name: 'Taxa por Hora Extra',
    description: 'Cobrança adicional por horas trabalhadas',
    type: 'usage-based',
    trigger: 'Registro de hora extra',
    frequency: 'monthly',
    baseValue: 45,
    currency: 'BRL',
    status: 'active',
    appliedTo: 89,
    lastExecuted: '2026-01-15',
    nextExecution: '2026-02-01',
    createdAt: '2025-03-20'
  },
  {
    id: '3',
    name: 'Plano Escalonado',
    description: 'Cobrança por faixa de consumo',
    type: 'tiered',
    trigger: 'Fim do período',
    frequency: 'monthly',
    baseValue: 500,
    currency: 'BRL',
    status: 'active',
    appliedTo: 45,
    lastExecuted: '2026-01-01',
    nextExecution: '2026-02-01',
    createdAt: '2025-06-10'
  },
  {
    id: '4',
    name: 'Multa por Atraso',
    description: 'Aplicação automática de multa',
    type: 'one-time',
    trigger: 'Vencimento + 1 dia',
    frequency: 'on-demand',
    baseValue: 0,
    currency: 'BRL',
    status: 'active',
    appliedTo: 23,
    lastExecuted: '2026-01-14',
    nextExecution: '-',
    createdAt: '2025-01-01'
  },
  {
    id: '5',
    name: 'Serviços Adicionais',
    description: 'Regra em desenvolvimento',
    type: 'recurring',
    trigger: 'Manual',
    frequency: 'monthly',
    baseValue: 200,
    currency: 'BRL',
    status: 'draft',
    appliedTo: 0,
    lastExecuted: '-',
    nextExecution: '-',
    createdAt: '2026-01-10'
  }
];

const mockExecutions: BillingExecution[] = [
  {
    id: '1',
    ruleId: '1',
    ruleName: 'Mensalidade Padrão',
    executedAt: '2026-01-15T10:30:00',
    status: 'success',
    processedCount: 234,
    totalValue: 351000,
    errors: 0
  },
  {
    id: '2',
    ruleId: '2',
    ruleName: 'Taxa por Hora Extra',
    executedAt: '2026-01-15T11:00:00',
    status: 'success',
    processedCount: 89,
    totalValue: 12450,
    errors: 0
  },
  {
    id: '3',
    ruleId: '4',
    ruleName: 'Multa por Atraso',
    executedAt: '2026-01-14T08:00:00',
    status: 'partial',
    processedCount: 20,
    totalValue: 4500,
    errors: 3
  },
  {
    id: '4',
    ruleId: '3',
    ruleName: 'Plano Escalonado',
    executedAt: '2026-01-01T00:05:00',
    status: 'success',
    processedCount: 45,
    totalValue: 67500,
    errors: 0
  }
];

// Chart data
const billingByType = [
  { name: 'Recorrente', value: 351000, color: '#6366f1' },
  { name: 'Por Uso', value: 12450, color: '#8b5cf6' },
  { name: 'Escalonado', value: 67500, color: '#10b981' },
  { name: 'Avulso', value: 4500, color: '#f59e0b' }
];

const monthlyBilling = [
  { month: 'Set', value: 380000 },
  { month: 'Out', value: 395000 },
  { month: 'Nov', value: 410000 },
  { month: 'Dez', value: 425000 },
  { month: 'Jan', value: 450000 }
];

export function BillingRulesPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showNewRuleModal, setShowNewRuleModal] = useState(false);
  const [selectedRule, setSelectedRule] = useState<BillingRule | null>(null);
  const [newRuleType, setNewRuleType] = useState('');
  const [newRuleFrequency, setNewRuleFrequency] = useState('');
  const [newRuleApplyTo, setNewRuleApplyTo] = useState('');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Settings className="h-4 w-4" /> },
    { value: 'rules', label: 'Regras', icon: <FileText className="h-4 w-4" /> },
    { value: 'history', label: 'Histórico', icon: <Clock className="h-4 w-4" /> }
  ];

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'recurring':
        return <Badge variant="primary">Recorrente</Badge>;
      case 'one-time':
        return <Badge variant="info">Avulso</Badge>;
      case 'usage-based':
        return <Badge variant="warning">Por Uso</Badge>;
      case 'tiered':
        return <Badge variant="success">Escalonado</Badge>;
      default:
        return <Badge variant="neutral">{type}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="success">Ativa</Badge>;
      case 'inactive':
        return <Badge variant="neutral">Inativa</Badge>;
      case 'draft':
        return <Badge variant="warning">Rascunho</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getExecutionStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="success">Sucesso</Badge>;
      case 'partial':
        return <Badge variant="warning">Parcial</Badge>;
      case 'failed':
        return <Badge variant="danger">Falha</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const ruleColumns: Column<BillingRule>[] = [
    {
      key: 'name',
      header: 'Regra',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-sm text-text-secondary">{row.description}</p>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => getTypeBadge(row.type)
    },
    {
      key: 'trigger',
      header: 'Gatilho',
      render: (row) => (
        <span className="text-text-secondary">{row.trigger}</span>
      )
    },
    {
      key: 'baseValue',
      header: 'Valor Base',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.baseValue > 0
            ? row.baseValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
            : 'Variável'
          }
        </span>
      )
    },
    {
      key: 'appliedTo',
      header: 'Aplicada a',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-text-muted" />
          <span className="text-text-secondary">{row.appliedTo} clientes</span>
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
            onClick={() => setSelectedRule(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
          {row.status === 'active' ? (
            <Button variant="ghost" size="sm">
              <Pause className="h-4 w-4" />
            </Button>
          ) : (
            <Button variant="ghost" size="sm">
              <Play className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const executionColumns: Column<BillingExecution>[] = [
    {
      key: 'ruleName',
      header: 'Regra',
      render: (row) => (
        <span className="font-medium text-text-primary">{row.ruleName}</span>
      )
    },
    {
      key: 'executedAt',
      header: 'Data/Hora',
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.executedAt).toLocaleString('pt-BR')}
        </span>
      )
    },
    {
      key: 'processedCount',
      header: 'Processados',
      render: (row) => (
        <span className="text-text-secondary">{row.processedCount}</span>
      )
    },
    {
      key: 'totalValue',
      header: 'Valor Total',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'errors',
      header: 'Erros',
      render: (row) => (
        <span className={row.errors > 0 ? 'text-danger' : 'text-text-secondary'}>
          {row.errors}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getExecutionStatusBadge(row.status)
    }
  ];

  const filteredRules = mockRules.filter(rule => {
    const matchesSearch = rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || rule.type === filterType;
    const matchesStatus = filterStatus === 'all' || rule.status === filterStatus;
    return matchesSearch && matchesType && matchesStatus;
  });

  const activeRules = mockRules.filter(r => r.status === 'active').length;
  const totalGenerated = mockExecutions.reduce((sum, e) => sum + e.totalValue, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Regras de Cobrança
            </h1>
            <p className="text-text-secondary mt-1">
              Configuração e automação de faturamento
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewRuleModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Regra
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Regras Ativas"
            value={activeRules.toString()}
            icon={<Zap className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Cobranças Hoje"
            value="156"
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="success"
            change={12}
            changeLabel="vs. ontem"
          />
          <StatCard
            title="Valor Gerado"
            value={totalGenerated.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Taxa de Sucesso"
            value="98.5%"
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
            change={0.5}
            changeLabel="vs. mês anterior"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Billing by Type */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Faturamento por Tipo
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={billingByType}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {billingByType.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Monthly Trend */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Evolução Mensal
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={monthlyBilling}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" tickFormatter={(value) => `${value / 1000}K`} />
                    <Tooltip
                      formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      name="Faturamento"
                      stroke="#6366f1"
                      strokeWidth={2}
                      dot={{ fill: '#6366f1', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Active Rules Summary */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Regras Ativas
              </h3>
              <div className="space-y-4">
                {mockRules.filter(r => r.status === 'active').map((rule) => (
                  <div key={rule.id} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Zap className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{rule.name}</p>
                        <p className="text-sm text-text-secondary">{rule.trigger}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-text-secondary">Próxima execução</p>
                      <p className="font-medium text-text-primary">{rule.nextExecution}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Recent Executions */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Execuções Recentes
              </h3>
              <div className="space-y-4">
                {mockExecutions.slice(0, 4).map((execution) => (
                  <div key={execution.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                        execution.status === 'success' ? 'bg-success/10' :
                        execution.status === 'partial' ? 'bg-warning/10' : 'bg-danger/10'
                      }`}>
                        {execution.status === 'success' ? (
                          <CheckCircle className="h-5 w-5 text-success" />
                        ) : execution.status === 'partial' ? (
                          <AlertTriangle className="h-5 w-5 text-warning" />
                        ) : (
                          <AlertTriangle className="h-5 w-5 text-danger" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{execution.ruleName}</p>
                        <p className="text-sm text-text-secondary">
                          {new Date(execution.executedAt).toLocaleString('pt-BR')}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-text-primary">
                        {execution.totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <p className="text-sm text-text-secondary">{execution.processedCount} processados</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Rules Tab */}
        {activeTab === 'rules' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar regra..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterType}
                onChange={setFilterType}
                options={[
                  { value: 'all', label: 'Todos os tipos' },
                  { value: 'recurring', label: 'Recorrente' },
                  { value: 'one-time', label: 'Avulso' },
                  { value: 'usage-based', label: 'Por Uso' },
                  { value: 'tiered', label: 'Escalonado' }
                ]}
                className="w-40"
              />
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={[
                  { value: 'all', label: 'Todos status' },
                  { value: 'active', label: 'Ativas' },
                  { value: 'inactive', label: 'Inativas' },
                  { value: 'draft', label: 'Rascunhos' }
                ]}
                className="w-40"
              />
            </div>
            <DataTable
              columns={ruleColumns}
              data={filteredRules}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar execução..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Input type="date" className="w-40" />
              <Input type="date" className="w-40" />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={executionColumns}
              data={mockExecutions}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Rule Detail Modal */}
        {selectedRule && (
          <Modal
            isOpen={!!selectedRule}
            onClose={() => setSelectedRule(null)}
            title="Detalhes da Regra"
            size="lg"
          >
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Settings className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">
                    {selectedRule.name}
                  </h3>
                  <p className="text-text-secondary">{selectedRule.description}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {getTypeBadge(selectedRule.type)}
                    {getStatusBadge(selectedRule.status)}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Zap className="h-4 w-4" />
                    <span>Gatilho: {selectedRule.trigger}</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Calendar className="h-4 w-4" />
                    <span>Frequência: {selectedRule.frequency}</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <DollarSign className="h-4 w-4" />
                    <span>Valor Base: {selectedRule.baseValue > 0
                      ? selectedRule.baseValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                      : 'Variável'
                    }</span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Users className="h-4 w-4" />
                    <span>Aplicada a: {selectedRule.appliedTo} clientes</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Clock className="h-4 w-4" />
                    <span>Última execução: {selectedRule.lastExecuted}</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Calendar className="h-4 w-4" />
                    <span>Próxima: {selectedRule.nextExecution}</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border-subtle">
                <div className="text-center p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-2xl font-bold text-text-primary">{selectedRule.appliedTo}</p>
                  <p className="text-sm text-text-secondary">Clientes</p>
                </div>
                <div className="text-center p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-2xl font-bold text-text-primary">
                    {(selectedRule.appliedTo * selectedRule.baseValue).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                  <p className="text-sm text-text-secondary">Valor Estimado</p>
                </div>
                <div className="text-center p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-2xl font-bold text-text-primary">
                    {new Date(selectedRule.createdAt).toLocaleDateString('pt-BR')}
                  </p>
                  <p className="text-sm text-text-secondary">Criada em</p>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedRule(null)}>
                  Fechar
                </Button>
                <Button variant="outline">
                  <Copy className="h-4 w-4 mr-2" />
                  Duplicar
                </Button>
                <Button>
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
              </div>
            </div>
          </Modal>
        )}

        {/* New Rule Modal */}
        <Modal
          isOpen={showNewRuleModal}
          onClose={() => setShowNewRuleModal(false)}
          title="Nova Regra de Cobrança"
          size="lg"
        >
          <div className="space-y-4">
            <Input label="Nome da Regra" placeholder="Ex: Mensalidade Premium" />
            <Input label="Descrição" placeholder="Descreva o propósito desta regra" />
            <div className="grid grid-cols-2 gap-4">
              <Select
                value={newRuleType}
                onChange={(value) => setNewRuleType(value)}
                options={[
                  { value: '', label: 'Selecione o tipo' },
                  { value: 'recurring', label: 'Recorrente' },
                  { value: 'one-time', label: 'Avulso' },
                  { value: 'usage-based', label: 'Por Uso' },
                  { value: 'tiered', label: 'Escalonado' }
                ]}
                className="w-full"
              />
              <Select
                value={newRuleFrequency}
                onChange={(value) => setNewRuleFrequency(value)}
                options={[
                  { value: '', label: 'Selecione a frequência' },
                  { value: 'daily', label: 'Diária' },
                  { value: 'weekly', label: 'Semanal' },
                  { value: 'monthly', label: 'Mensal' },
                  { value: 'yearly', label: 'Anual' },
                  { value: 'on-demand', label: 'Sob Demanda' }
                ]}
                className="w-full"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Valor Base" type="number" placeholder="0,00" />
              <Input label="Gatilho" placeholder="Ex: Início do mês" />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="font-medium text-text-primary mb-3">Aplicar a</h4>
              <Select
                value={newRuleApplyTo}
                onChange={(value) => setNewRuleApplyTo(value)}
                options={[
                  { value: '', label: 'Selecione os clientes' },
                  { value: 'all', label: 'Todos os clientes ativos' },
                  { value: 'segment', label: 'Segmento específico' },
                  { value: 'manual', label: 'Seleção manual' }
                ]}
                className="w-full"
              />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewRuleModal(false)}>
                Cancelar
              </Button>
              <Button variant="outline">
                Salvar como Rascunho
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Criar Regra
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
