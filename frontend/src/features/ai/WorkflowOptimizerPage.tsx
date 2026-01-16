'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Workflow,
  Play,
  Pause,
  Settings,
  Plus,
  Edit,
  Trash2,
  Eye,
  Copy,
  Sparkles,
  Clock,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Zap,
  Target,
  BarChart3,
  RefreshCw,
  Search,
  Filter,
  MoreVertical,
  ArrowRight,
  GitBranch,
  Users,
  Calendar,
  DollarSign,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Modal,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Progress,
  Dropdown,
  EmptyState,
} from '@/design-system/components';

// Types
interface WorkflowProcess {
  id: string;
  name: string;
  description: string;
  category: string;
  status: 'active' | 'optimizing' | 'paused' | 'draft';
  steps: number;
  avgDuration: number;
  optimizedDuration?: number;
  executions: number;
  successRate: number;
  lastOptimized?: string;
  savings?: {
    time: number;
    cost: number;
  };
  bottlenecks: Bottleneck[];
}

interface Bottleneck {
  id: string;
  step: string;
  issue: string;
  impact: 'low' | 'medium' | 'high';
  suggestion: string;
}

interface Optimization {
  id: string;
  processId: string;
  processName: string;
  type: 'automation' | 'parallelization' | 'elimination' | 'simplification';
  description: string;
  status: 'suggested' | 'approved' | 'implemented' | 'rejected';
  impact: {
    timeSaved: number;
    costSaved: number;
  };
  createdAt: string;
}

// Mock Data
const mockProcesses: WorkflowProcess[] = [
  {
    id: '1',
    name: 'Onboarding de Funcionário',
    description: 'Processo completo de admissão de novos funcionários',
    category: 'RH',
    status: 'active',
    steps: 12,
    avgDuration: 480,
    optimizedDuration: 320,
    executions: 45,
    successRate: 94.5,
    lastOptimized: '2026-01-10',
    savings: {
      time: 33,
      cost: 1500,
    },
    bottlenecks: [
      {
        id: '1',
        step: 'Coleta de Documentos',
        issue: 'Tempo excessivo aguardando documentos',
        impact: 'high',
        suggestion: 'Implementar portal de upload com lembretes automáticos',
      },
      {
        id: '2',
        step: 'Aprovação Gerencial',
        issue: 'Gargalo em aprovações múltiplas',
        impact: 'medium',
        suggestion: 'Paralelizar aprovações quando possível',
      },
    ],
  },
  {
    id: '2',
    name: 'Aprovação de Despesas',
    description: 'Fluxo de aprovação de solicitações de despesas',
    category: 'Financeiro',
    status: 'active',
    steps: 6,
    avgDuration: 120,
    optimizedDuration: 45,
    executions: 230,
    successRate: 98.2,
    lastOptimized: '2026-01-15',
    savings: {
      time: 62,
      cost: 3200,
    },
    bottlenecks: [],
  },
  {
    id: '3',
    name: 'Atendimento ao Cliente',
    description: 'Fluxo de atendimento e resolução de chamados',
    category: 'Suporte',
    status: 'optimizing',
    steps: 8,
    avgDuration: 240,
    executions: 156,
    successRate: 89.7,
    bottlenecks: [
      {
        id: '1',
        step: 'Triagem inicial',
        issue: 'Classificação manual demorada',
        impact: 'high',
        suggestion: 'Usar IA para classificação automática de tickets',
      },
    ],
  },
  {
    id: '4',
    name: 'Geração de Relatórios',
    description: 'Processo de coleta e geração de relatórios mensais',
    category: 'Analytics',
    status: 'paused',
    steps: 5,
    avgDuration: 180,
    executions: 12,
    successRate: 100,
    bottlenecks: [],
  },
];

const mockOptimizations: Optimization[] = [
  {
    id: '1',
    processId: '1',
    processName: 'Onboarding de Funcionário',
    type: 'automation',
    description: 'Automatizar envio de emails de boas-vindas e agendamento de treinamentos',
    status: 'suggested',
    impact: {
      timeSaved: 60,
      costSaved: 500,
    },
    createdAt: '2026-01-16',
  },
  {
    id: '2',
    processId: '3',
    processName: 'Atendimento ao Cliente',
    type: 'automation',
    description: 'Implementar chatbot para triagem inicial de tickets',
    status: 'approved',
    impact: {
      timeSaved: 120,
      costSaved: 2000,
    },
    createdAt: '2026-01-15',
  },
  {
    id: '3',
    processId: '2',
    processName: 'Aprovação de Despesas',
    type: 'simplification',
    description: 'Remover etapa de pré-aprovação para valores até R$ 500',
    status: 'implemented',
    impact: {
      timeSaved: 30,
      costSaved: 800,
    },
    createdAt: '2026-01-10',
  },
];

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  optimizing: { label: 'Otimizando', color: 'warning' as const },
  paused: { label: 'Pausado', color: 'secondary' as const },
  draft: { label: 'Rascunho', color: 'info' as const },
};

const optimizationStatusConfig = {
  suggested: { label: 'Sugerido', color: 'info' as const },
  approved: { label: 'Aprovado', color: 'success' as const },
  implemented: { label: 'Implementado', color: 'success' as const },
  rejected: { label: 'Rejeitado', color: 'danger' as const },
};

const optimizationTypeConfig = {
  automation: { label: 'Automação', icon: Zap },
  parallelization: { label: 'Paralelização', icon: GitBranch },
  elimination: { label: 'Eliminação', icon: Trash2 },
  simplification: { label: 'Simplificação', icon: Target },
};

const impactConfig = {
  low: { label: 'Baixo', color: 'success' as const },
  medium: { label: 'Médio', color: 'warning' as const },
  high: { label: 'Alto', color: 'danger' as const },
};

export function WorkflowOptimizerPage() {
  const [processes, setProcesses] = useState(mockProcesses);
  const [optimizations, setOptimizations] = useState(mockOptimizations);
  const [selectedProcess, setSelectedProcess] = useState<WorkflowProcess | null>(null);
  const [activeTab, setActiveTab] = useState('processes');
  const [searchQuery, setSearchQuery] = useState('');
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const stats = {
    totalProcesses: processes.length,
    activeProcesses: processes.filter((p) => p.status === 'active').length,
    totalTimeSaved: processes.reduce((sum, p) => sum + (p.savings?.time || 0), 0),
    totalCostSaved: processes.reduce((sum, p) => sum + (p.savings?.cost || 0), 0),
    avgSuccessRate: Math.round(
      processes.reduce((sum, p) => sum + p.successRate, 0) / processes.length
    ),
  };

  const filteredProcesses = processes.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAnalyzeProcess = async (id: string) => {
    setIsAnalyzing(true);
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setProcesses((prev) =>
      prev.map((p) =>
        p.id === id ? { ...p, status: 'optimizing' as const } : p
      )
    );
    setIsAnalyzing(false);
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h${mins > 0 ? ` ${mins}min` : ''}`;
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Workflow className="w-8 h-8 text-accent-primary" />
              Otimizador de Processos
            </h1>
            <p className="text-text-secondary mt-1">
              Análise e otimização automática de workflows com IA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
              Novo Processo
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Processos"
              value={stats.totalProcesses}
              icon={<Workflow className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Ativos"
              value={stats.activeProcesses}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Tempo Economizado"
              value={`${stats.totalTimeSaved}%`}
              icon={<Clock className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Economia"
              value={`R$ ${(stats.totalCostSaved / 1000).toFixed(1)}K`}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Taxa de Sucesso"
              value={`${stats.avgSuccessRate}%`}
              icon={<Target className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="processes" label="Processos" />
          <Tab value="optimizations" label="Otimizações" />
          <Tab value="bottlenecks" label="Gargalos" />
          <Tab value="analytics" label="Analytics" />
        </Tabs>

        {activeTab === 'processes' && (
          <>
            {/* Search */}
            <Card>
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                    <Input
                      placeholder="Buscar processos..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                    Filtros
                  </Button>
                </div>
              </CardBody>
            </Card>

            {/* Processes List */}
            <div className="grid gap-4">
              {filteredProcesses.map((process) => (
                <Card key={process.id} className="hover:border-accent-primary/50 transition-colors">
                  <CardBody>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          process.status === 'active' ? 'bg-green-500/10' :
                          process.status === 'optimizing' ? 'bg-yellow-500/10' : 'bg-gray-500/10'
                        }`}>
                          <Workflow className={`w-6 h-6 ${
                            process.status === 'active' ? 'text-green-500' :
                            process.status === 'optimizing' ? 'text-yellow-500' : 'text-gray-500'
                          }`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium text-text-primary">{process.name}</h3>
                            <Badge variant={statusConfig[process.status].color}>
                              {statusConfig[process.status].label}
                            </Badge>
                            <Badge variant="secondary">{process.category}</Badge>
                          </div>
                          <p className="text-sm text-text-muted mb-2">{process.description}</p>
                          <div className="flex items-center gap-4 text-sm text-text-muted">
                            <span className="flex items-center gap-1">
                              <GitBranch className="w-4 h-4" />
                              {process.steps} etapas
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {formatDuration(process.avgDuration)}
                              {process.optimizedDuration && (
                                <span className="text-green-500">
                                  → {formatDuration(process.optimizedDuration)}
                                </span>
                              )}
                            </span>
                            <span className="flex items-center gap-1">
                              <RefreshCw className="w-4 h-4" />
                              {process.executions} execuções
                            </span>
                            <span className="flex items-center gap-1">
                              <Target className="w-4 h-4" />
                              {process.successRate}% sucesso
                            </span>
                          </div>
                          {process.bottlenecks.length > 0 && (
                            <div className="flex items-center gap-2 mt-2">
                              <AlertTriangle className="w-4 h-4 text-yellow-500" />
                              <span className="text-sm text-yellow-500">
                                {process.bottlenecks.length} gargalo(s) identificado(s)
                              </span>
                            </div>
                          )}
                          {process.savings && (
                            <div className="flex items-center gap-4 mt-2">
                              <Badge variant="success" size="sm">
                                <TrendingUp className="w-3 h-3 mr-1" />
                                {process.savings.time}% mais rápido
                              </Badge>
                              <Badge variant="success" size="sm">
                                <DollarSign className="w-3 h-3 mr-1" />
                                R$ {process.savings.cost} economizados
                              </Badge>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="primary"
                          size="sm"
                          leftIcon={<Sparkles className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />}
                          onClick={() => handleAnalyzeProcess(process.id)}
                          disabled={isAnalyzing || process.status === 'optimizing'}
                        >
                          {process.status === 'optimizing' ? 'Analisando...' : 'Analisar'}
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          leftIcon={<Eye className="w-4 h-4" />}
                          onClick={() => {
                            setSelectedProcess(process);
                            setDetailsOpen(true);
                          }}
                        >
                          Detalhes
                        </Button>
                        <Dropdown
                          trigger={
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          }
                          items={[
                            { label: 'Editar', icon: <Edit className="w-4 h-4" /> },
                            { label: 'Duplicar', icon: <Copy className="w-4 h-4" /> },
                            { label: 'Pausar', icon: <Pause className="w-4 h-4" /> },
                            { label: 'Excluir', icon: <Trash2 className="w-4 h-4" /> },
                          ]}
                        />
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          </>
        )}

        {activeTab === 'optimizations' && (
          <Card>
            <CardHeader
              title="Otimizações Sugeridas"
              subtitle="Melhorias identificadas pela IA"
            />
            <CardBody>
              <div className="space-y-4">
                {optimizations.map((opt) => {
                  const TypeIcon = optimizationTypeConfig[opt.type].icon;
                  return (
                    <div
                      key={opt.id}
                      className="flex items-start justify-between p-4 bg-bg-tertiary rounded-lg"
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                          <TypeIcon className="w-5 h-5 text-accent-primary" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium text-text-primary">{opt.description}</p>
                            <Badge variant={optimizationStatusConfig[opt.status].color}>
                              {optimizationStatusConfig[opt.status].label}
                            </Badge>
                          </div>
                          <p className="text-sm text-text-muted">{opt.processName}</p>
                          <div className="flex items-center gap-4 mt-2">
                            <Badge variant="success" size="sm">
                              <Clock className="w-3 h-3 mr-1" />
                              {opt.impact.timeSaved}min economizados
                            </Badge>
                            <Badge variant="success" size="sm">
                              <DollarSign className="w-3 h-3 mr-1" />
                              R$ {opt.impact.costSaved}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      {opt.status === 'suggested' && (
                        <div className="flex items-center gap-2">
                          <Button variant="primary" size="sm">
                            Aprovar
                          </Button>
                          <Button variant="ghost" size="sm">
                            Rejeitar
                          </Button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'bottlenecks' && (
          <Card>
            <CardHeader title="Gargalos Identificados" />
            <CardBody>
              <div className="space-y-4">
                {processes
                  .flatMap((p) =>
                    p.bottlenecks.map((b) => ({
                      ...b,
                      processName: p.name,
                    }))
                  )
                  .map((bottleneck) => (
                    <div
                      key={bottleneck.id}
                      className="flex items-start justify-between p-4 bg-bg-tertiary rounded-lg"
                    >
                      <div className="flex items-start gap-4">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          bottleneck.impact === 'high' ? 'bg-red-500/10' :
                          bottleneck.impact === 'medium' ? 'bg-yellow-500/10' : 'bg-green-500/10'
                        }`}>
                          <AlertTriangle className={`w-5 h-5 ${
                            bottleneck.impact === 'high' ? 'text-red-500' :
                            bottleneck.impact === 'medium' ? 'text-yellow-500' : 'text-green-500'
                          }`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium text-text-primary">{bottleneck.step}</p>
                            <Badge variant={impactConfig[bottleneck.impact].color}>
                              Impacto {impactConfig[bottleneck.impact].label}
                            </Badge>
                          </div>
                          <p className="text-sm text-text-muted">{bottleneck.processName}</p>
                          <p className="text-sm text-text-secondary mt-2">{bottleneck.issue}</p>
                          <div className="mt-2 p-2 bg-accent-primary/10 rounded flex items-start gap-2">
                            <Sparkles className="w-4 h-4 text-accent-primary mt-0.5" />
                            <p className="text-sm text-accent-primary">{bottleneck.suggestion}</p>
                          </div>
                        </div>
                      </div>
                      <Button variant="primary" size="sm">
                        Resolver
                      </Button>
                    </div>
                  ))}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Processos por Status" />
              <CardBody>
                <div className="space-y-4">
                  {[
                    { status: 'Ativos', count: stats.activeProcesses, color: 'bg-green-500' },
                    { status: 'Em otimização', count: 1, color: 'bg-yellow-500' },
                    { status: 'Pausados', count: 1, color: 'bg-gray-500' },
                  ].map((item) => (
                    <div key={item.status} className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${item.color}`} />
                      <span className="flex-1 text-text-primary">{item.status}</span>
                      <span className="font-medium text-text-primary">{item.count}</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Economia Total" />
              <CardBody>
                <div className="text-center">
                  <p className="text-4xl font-bold text-green-500">
                    R$ {stats.totalCostSaved.toLocaleString()}
                  </p>
                  <p className="text-text-muted">economia mensal estimada</p>
                </div>
                <div className="mt-6 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-text-muted">Tempo economizado</span>
                    <span className="font-medium text-text-primary">{stats.totalTimeSaved}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-text-muted">Processos otimizados</span>
                    <span className="font-medium text-text-primary">2 de 4</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-text-muted">Gargalos resolvidos</span>
                    <span className="font-medium text-text-primary">5</span>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        )}
      </div>

      {/* Process Details Modal */}
      <Modal
        isOpen={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        title={selectedProcess?.name || ''}
        size="lg"
      >
        {selectedProcess && (
          <div className="space-y-6">
            <p className="text-text-secondary">{selectedProcess.description}</p>

            <div className="grid grid-cols-4 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-text-primary">{selectedProcess.steps}</p>
                <p className="text-sm text-text-muted">Etapas</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-text-primary">
                  {formatDuration(selectedProcess.avgDuration)}
                </p>
                <p className="text-sm text-text-muted">Duração Média</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-text-primary">{selectedProcess.executions}</p>
                <p className="text-sm text-text-muted">Execuções</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-2xl font-bold text-green-500">{selectedProcess.successRate}%</p>
                <p className="text-sm text-text-muted">Taxa de Sucesso</p>
              </div>
            </div>

            {selectedProcess.bottlenecks.length > 0 && (
              <div>
                <h4 className="font-medium text-text-primary mb-3">Gargalos Identificados</h4>
                <div className="space-y-3">
                  {selectedProcess.bottlenecks.map((bottleneck) => (
                    <div key={bottleneck.id} className="p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-text-primary">{bottleneck.step}</span>
                        <Badge variant={impactConfig[bottleneck.impact].color}>
                          {impactConfig[bottleneck.impact].label}
                        </Badge>
                      </div>
                      <p className="text-sm text-text-muted mb-2">{bottleneck.issue}</p>
                      <div className="p-2 bg-accent-primary/10 rounded">
                        <p className="text-sm text-accent-primary">
                          💡 {bottleneck.suggestion}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<Edit className="w-4 h-4" />}>
                Editar Processo
              </Button>
              <Button variant="primary" leftIcon={<Sparkles className="w-4 h-4" />}>
                Otimizar com IA
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}

export default WorkflowOptimizerPage;
