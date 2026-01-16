'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Shield,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Plus,
  Eye,
  Edit2,
  Download,
  MoreHorizontal,
  ClipboardList,
  Target,
  Scale,
  Users,
  Database,
  Lock,
  AlertCircle,
  TrendingUp,
  BarChart2,
  Calendar,
  User,
  Settings,
  Send,
  History,
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
  Textarea,
} from '@/design-system/components';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts';

// Types
interface PIA {
  id: string;
  title: string;
  project: string;
  status: 'draft' | 'in_review' | 'approved' | 'rejected' | 'archived';
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  updatedAt: string;
  dueDate: string;
  owner: string;
  reviewer: string | null;
  dataProcessingPurposes: string[];
  dataCategories: string[];
  riskScore: number;
  mitigationStatus: number;
}

interface RiskAssessment {
  category: string;
  score: number;
  maxScore: number;
}

// Mock Data
const piaList: PIA[] = [
  {
    id: '1',
    title: 'PIA - Sistema de Reconhecimento Facial',
    project: 'Controle de Acesso v3',
    status: 'in_review',
    riskLevel: 'high',
    createdAt: '2026-01-10',
    updatedAt: '2026-01-15',
    dueDate: '2026-01-25',
    owner: 'Ana Costa',
    reviewer: 'Carlos Lima',
    dataProcessingPurposes: ['Controle de Acesso', 'Segurança'],
    dataCategories: ['Dados Biométricos', 'Dados de Localização'],
    riskScore: 78,
    mitigationStatus: 45,
  },
  {
    id: '2',
    title: 'PIA - Integração com CRM Externo',
    project: 'Projeto Unificação',
    status: 'approved',
    riskLevel: 'medium',
    createdAt: '2025-12-15',
    updatedAt: '2026-01-08',
    dueDate: '2026-01-10',
    owner: 'Roberto Silva',
    reviewer: 'Maria Oliveira',
    dataProcessingPurposes: ['Marketing', 'Vendas', 'Análise'],
    dataCategories: ['Dados Pessoais', 'Histórico de Compras'],
    riskScore: 52,
    mitigationStatus: 90,
  },
  {
    id: '3',
    title: 'PIA - App Mobile para Moradores',
    project: 'Conecta Mobile',
    status: 'draft',
    riskLevel: 'medium',
    createdAt: '2026-01-12',
    updatedAt: '2026-01-14',
    dueDate: '2026-02-01',
    owner: 'Pedro Santos',
    reviewer: null,
    dataProcessingPurposes: ['Comunicação', 'Serviços'],
    dataCategories: ['Dados Pessoais', 'Dados de Uso'],
    riskScore: 45,
    mitigationStatus: 0,
  },
  {
    id: '4',
    title: 'PIA - Sistema de Cobrança Automatizado',
    project: 'FinTech Integration',
    status: 'approved',
    riskLevel: 'low',
    createdAt: '2025-11-20',
    updatedAt: '2025-12-10',
    dueDate: '2025-12-15',
    owner: 'Maria Oliveira',
    reviewer: 'Ana Costa',
    dataProcessingPurposes: ['Cobrança', 'Financeiro'],
    dataCategories: ['Dados Financeiros'],
    riskScore: 28,
    mitigationStatus: 100,
  },
  {
    id: '5',
    title: 'PIA - Analytics de Comportamento',
    project: 'Business Intelligence',
    status: 'rejected',
    riskLevel: 'critical',
    createdAt: '2025-10-01',
    updatedAt: '2025-10-20',
    dueDate: '2025-10-30',
    owner: 'Carlos Lima',
    reviewer: 'Roberto Silva',
    dataProcessingPurposes: ['Análise Comportamental', 'Profiling'],
    dataCategories: ['Dados Sensíveis', 'Dados de Comportamento'],
    riskScore: 92,
    mitigationStatus: 15,
  },
];

const riskDistribution = [
  { name: 'Baixo', value: 3, color: '#10B981' },
  { name: 'Médio', value: 5, color: '#F59E0B' },
  { name: 'Alto', value: 4, color: '#EF4444' },
  { name: 'Crítico', value: 1, color: '#7C3AED' },
];

const riskAssessment: RiskAssessment[] = [
  { category: 'Coleta', score: 7, maxScore: 10 },
  { category: 'Armazenamento', score: 6, maxScore: 10 },
  { category: 'Compartilhamento', score: 8, maxScore: 10 },
  { category: 'Segurança', score: 5, maxScore: 10 },
  { category: 'Retenção', score: 4, maxScore: 10 },
  { category: 'Direitos', score: 6, maxScore: 10 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'draft', label: 'Rascunhos' },
  { id: 'in_review', label: 'Em Revisão' },
  { id: 'approved', label: 'Aprovados' },
  { id: 'rejected', label: 'Rejeitados' },
];

const statusColors = {
  draft: 'secondary',
  in_review: 'warning',
  approved: 'success',
  rejected: 'danger',
  archived: 'neutral',
} as const;

const statusLabels = {
  draft: 'Rascunho',
  in_review: 'Em Revisão',
  approved: 'Aprovado',
  rejected: 'Rejeitado',
  archived: 'Arquivado',
};

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

const columns: Column<PIA>[] = [
  {
    key: 'title',
    header: 'Avaliação',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${
          row.riskLevel === 'low' ? 'bg-success/10' :
          row.riskLevel === 'medium' ? 'bg-warning/10' :
          'bg-danger/10'
        }`}>
          <Shield className={`w-5 h-5 ${
            row.riskLevel === 'low' ? 'text-success' :
            row.riskLevel === 'medium' ? 'text-warning' :
            'text-danger'
          }`} />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.title}</p>
          <p className="text-xs text-text-muted">{row.project}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={statusColors[row.status]}>
        {statusLabels[row.status]}
      </Badge>
    ),
  },
  {
    key: 'riskLevel',
    header: 'Nível de Risco',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Badge variant={riskColors[row.riskLevel]} size="sm">
          {riskLabels[row.riskLevel]}
        </Badge>
        <span className="text-sm font-medium">{row.riskScore}%</span>
      </div>
    ),
  },
  {
    key: 'mitigationStatus',
    header: 'Mitigação',
    render: (row) => (
      <div className="flex items-center gap-2">
        <div className="w-20 h-2 bg-bg-secondary rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${
              row.mitigationStatus >= 80 ? 'bg-success' :
              row.mitigationStatus >= 50 ? 'bg-warning' :
              'bg-danger'
            }`}
            style={{ width: `${row.mitigationStatus}%` }}
          />
        </div>
        <span className="text-sm text-text-muted">{row.mitigationStatus}%</span>
      </div>
    ),
  },
  {
    key: 'owner',
    header: 'Responsável',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.owner} size="xs" />
        <span className="text-sm">{row.owner}</span>
      </div>
    ),
  },
  {
    key: 'dueDate',
    header: 'Prazo',
    render: (row) => {
      const due = new Date(row.dueDate);
      const isOverdue = due < new Date() && row.status !== 'approved';
      return (
        <span className={`text-sm ${isOverdue ? 'text-danger' : 'text-text-secondary'}`}>
          {due.toLocaleDateString('pt-BR')}
        </span>
      );
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Download">
          <Download className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#7C3AED'];

export function PIAPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedPIA, setSelectedPIA] = useState<PIA | null>(null);
  const [newPIAResponsible, setNewPIAResponsible] = useState('');

  const filteredPIAs = piaList.filter((pia) => {
    const matchesSearch =
      pia.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pia.project.toLowerCase().includes(searchTerm.toLowerCase());

    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && pia.status === activeTab;
  });

  // Stats
  const totalPIAs = piaList.length;
  const pendingPIAs = piaList.filter(p => p.status === 'draft' || p.status === 'in_review').length;
  const approvedPIAs = piaList.filter(p => p.status === 'approved').length;
  const highRiskPIAs = piaList.filter(p => p.riskLevel === 'high' || p.riskLevel === 'critical').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Avaliação de Impacto à Privacidade (PIA)
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie avaliações de impacto para tratamento de dados pessoais
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Nova Avaliação
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
              title="Total de Avaliações"
              value={totalPIAs}
              icon={<ClipboardList className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Pendentes"
              value={pendingPIAs}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Aprovadas"
              value={approvedPIAs}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Alto Risco"
              value={highRiskPIAs}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Análise de Risco por Categoria</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={riskAssessment}>
                    <PolarGrid stroke="var(--color-border)" />
                    <PolarAngleAxis
                      dataKey="category"
                      tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 10]}
                      tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
                    />
                    <Radar
                      name="Score"
                      dataKey="score"
                      stroke="#3B82F6"
                      fill="#3B82F6"
                      fillOpacity={0.3}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Distribuição por Nível de Risco</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {riskDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-4">
                {riskDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-text-muted">{item.name}: {item.value}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* High Risk Alert */}
        {highRiskPIAs > 0 && (
          <Card className="border-l-4 border-l-danger">
            <CardBody className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-danger/10">
                    <AlertTriangle className="w-5 h-5 text-danger" />
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">Avaliações de Alto Risco</p>
                    <p className="text-sm text-text-muted">
                      {highRiskPIAs} projetos requerem atenção especial e medidas de mitigação
                    </p>
                  </div>
                </div>
                <Button variant="danger" size="sm">Ver Detalhes</Button>
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
              placeholder="Buscar avaliações..."
              leftIcon={<Search className="w-4 h-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
          </div>
        </div>

        {/* PIA Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredPIAs}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedPIA(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create PIA Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Nova Avaliação de Impacto"
          description="Inicie uma nova avaliação de impacto à privacidade"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
                Criar Avaliação
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Título da Avaliação"
              placeholder="Ex: PIA - Novo Sistema de..."
              required
            />

            <Input
              label="Projeto/Sistema"
              placeholder="Nome do projeto ou sistema"
              required
            />

            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Responsável"
                options={[
                  { value: 'ana', label: 'Ana Costa' },
                  { value: 'carlos', label: 'Carlos Lima' },
                  { value: 'roberto', label: 'Roberto Silva' },
                ]}
                value={newPIAResponsible}
                onChange={(value) => setNewPIAResponsible(value)}
                placeholder="Selecione..."
              />
              <Input
                label="Prazo"
                type="date"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Finalidades do Tratamento</label>
              <div className="grid grid-cols-2 gap-2">
                {['Controle de Acesso', 'Marketing', 'Análise', 'Cobrança', 'RH', 'Segurança'].map((purpose) => (
                  <label key={purpose} className="flex items-center gap-2 p-2 rounded border border-border hover:bg-bg-secondary cursor-pointer">
                    <input type="checkbox" className="rounded" />
                    <span className="text-sm">{purpose}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Categorias de Dados</label>
              <div className="grid grid-cols-2 gap-2">
                {['Dados Pessoais', 'Dados Sensíveis', 'Dados Biométricos', 'Dados Financeiros', 'Dados de Localização', 'Dados de Saúde'].map((category) => (
                  <label key={category} className="flex items-center gap-2 p-2 rounded border border-border hover:bg-bg-secondary cursor-pointer">
                    <input type="checkbox" className="rounded" />
                    <span className="text-sm">{category}</span>
                  </label>
                ))}
              </div>
            </div>

            <Textarea
              label="Descrição do Tratamento"
              placeholder="Descreva como os dados serão processados..."
              rows={3}
            />

            <div className="p-3 rounded-lg bg-info/10 border border-info/20">
              <div className="flex items-center gap-2 mb-1">
                <Scale className="w-4 h-4 text-info" />
                <span className="text-sm font-medium text-info">Base Legal</span>
              </div>
              <p className="text-sm text-text-secondary">
                O Art. 38 da LGPD exige a elaboração de relatório de impacto quando o tratamento
                pode gerar riscos às liberdades civis e direitos fundamentais.
              </p>
            </div>
          </div>
        </Modal>

        {/* PIA Detail Modal */}
        <Modal
          isOpen={!!selectedPIA}
          onClose={() => setSelectedPIA(null)}
          title="Detalhes da Avaliação"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedPIA(null)}>
                Fechar
              </Button>
              {selectedPIA?.status === 'draft' && (
                <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                  Enviar para Revisão
                </Button>
              )}
            </>
          }
        >
          {selectedPIA && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                <div className={`p-3 rounded-lg ${
                  selectedPIA.riskLevel === 'low' ? 'bg-success/10' :
                  selectedPIA.riskLevel === 'medium' ? 'bg-warning/10' :
                  'bg-danger/10'
                }`}>
                  <Shield className={`w-6 h-6 ${
                    selectedPIA.riskLevel === 'low' ? 'text-success' :
                    selectedPIA.riskLevel === 'medium' ? 'text-warning' :
                    'text-danger'
                  }`} />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-text-primary">{selectedPIA.title}</h4>
                  <p className="text-sm text-text-muted">{selectedPIA.project}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={statusColors[selectedPIA.status]}>
                      {statusLabels[selectedPIA.status]}
                    </Badge>
                    <Badge variant={riskColors[selectedPIA.riskLevel]}>
                      Risco {riskLabels[selectedPIA.riskLevel]}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Risk Score */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg border border-border">
                  <p className="text-sm text-text-muted mb-2">Score de Risco</p>
                  <div className="flex items-center gap-4">
                    <div className="text-3xl font-bold text-text-primary">{selectedPIA.riskScore}%</div>
                    <div className="flex-1">
                      <div className="h-3 bg-bg-secondary rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            selectedPIA.riskScore <= 30 ? 'bg-success' :
                            selectedPIA.riskScore <= 60 ? 'bg-warning' :
                            'bg-danger'
                          }`}
                          style={{ width: `${selectedPIA.riskScore}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-4 rounded-lg border border-border">
                  <p className="text-sm text-text-muted mb-2">Mitigação Aplicada</p>
                  <div className="flex items-center gap-4">
                    <div className="text-3xl font-bold text-text-primary">{selectedPIA.mitigationStatus}%</div>
                    <div className="flex-1">
                      <div className="h-3 bg-bg-secondary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-success rounded-full"
                          style={{ width: `${selectedPIA.mitigationStatus}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Data Categories */}
              <div>
                <h5 className="font-medium text-text-primary mb-3">Categorias de Dados</h5>
                <div className="flex flex-wrap gap-2">
                  {selectedPIA.dataCategories.map((cat) => (
                    <Badge key={cat} variant="secondary">{cat}</Badge>
                  ))}
                </div>
              </div>

              {/* Purposes */}
              <div>
                <h5 className="font-medium text-text-primary mb-3">Finalidades</h5>
                <div className="flex flex-wrap gap-2">
                  {selectedPIA.dataProcessingPurposes.map((purpose) => (
                    <Badge key={purpose} variant="info">{purpose}</Badge>
                  ))}
                </div>
              </div>

              {/* Team */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                  <Avatar name={selectedPIA.owner} size="sm" />
                  <div>
                    <p className="text-sm text-text-muted">Responsável</p>
                    <p className="font-medium">{selectedPIA.owner}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                  {selectedPIA.reviewer ? (
                    <>
                      <Avatar name={selectedPIA.reviewer} size="sm" />
                      <div>
                        <p className="text-sm text-text-muted">Revisor</p>
                        <p className="font-medium">{selectedPIA.reviewer}</p>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="w-8 h-8 rounded-full bg-bg-tertiary flex items-center justify-center">
                        <User className="w-4 h-4 text-text-muted" />
                      </div>
                      <div>
                        <p className="text-sm text-text-muted">Revisor</p>
                        <p className="text-text-muted">Não atribuído</p>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Timeline */}
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Criado em</p>
                  <p className="font-medium">{new Date(selectedPIA.createdAt).toLocaleDateString('pt-BR')}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Atualizado em</p>
                  <p className="font-medium">{new Date(selectedPIA.updatedAt).toLocaleDateString('pt-BR')}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Prazo</p>
                  <p className="font-medium">{new Date(selectedPIA.dueDate).toLocaleDateString('pt-BR')}</p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
