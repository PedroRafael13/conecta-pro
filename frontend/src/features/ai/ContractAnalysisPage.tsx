'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Upload,
  Search,
  Filter,
  Download,
  Eye,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Calendar,
  DollarSign,
  Users,
  Building2,
  FileCheck,
  Scale,
  Shield,
  Sparkles,
  RefreshCw,
  MoreVertical,
  ChevronRight,
  Tag,
  TrendingUp,
  AlertCircle,
  Info,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
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
interface Contract {
  id: string;
  title: string;
  client: string;
  type: string;
  value: number;
  startDate: string;
  endDate: string;
  status: 'active' | 'expiring' | 'expired' | 'pending';
  riskScore: number;
  analysisStatus: 'analyzed' | 'pending' | 'in_progress';
  clauses: Clause[];
  alerts: Alert[];
}

interface Clause {
  id: string;
  title: string;
  category: string;
  risk: 'low' | 'medium' | 'high';
  description: string;
  recommendation?: string;
}

interface Alert {
  id: string;
  type: 'risk' | 'expiring' | 'missing' | 'conflict';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

// Mock Data
const mockContracts: Contract[] = [
  {
    id: '1',
    title: 'Contrato de Prestação de Serviços - Condomínio Aurora',
    client: 'Condomínio Aurora',
    type: 'Prestação de Serviços',
    value: 45000,
    startDate: '2025-03-01',
    endDate: '2026-02-28',
    status: 'expiring',
    riskScore: 72,
    analysisStatus: 'analyzed',
    clauses: [
      {
        id: '1',
        title: 'Cláusula de Rescisão',
        category: 'Rescisão',
        risk: 'high',
        description: 'Multa de 50% em caso de rescisão antecipada',
        recommendation: 'Negociar redução da multa para 20%',
      },
      {
        id: '2',
        title: 'Reajuste Anual',
        category: 'Financeiro',
        risk: 'medium',
        description: 'Reajuste pelo IGPM sem teto máximo',
        recommendation: 'Incluir teto de reajuste de 10% ao ano',
      },
    ],
    alerts: [
      {
        id: '1',
        type: 'expiring',
        title: 'Contrato vence em 45 dias',
        description: 'Iniciar processo de renovação',
        severity: 'high',
      },
    ],
  },
  {
    id: '2',
    title: 'Contrato de Vigilância - Shopping Center Norte',
    client: 'Shopping Center Norte',
    type: 'Vigilância',
    value: 128000,
    startDate: '2024-06-01',
    endDate: '2026-05-31',
    status: 'active',
    riskScore: 35,
    analysisStatus: 'analyzed',
    clauses: [],
    alerts: [],
  },
  {
    id: '3',
    title: 'Contrato de Portaria - Tech Park',
    client: 'Tech Park Empresarial',
    type: 'Portaria',
    value: 67000,
    startDate: '2025-01-01',
    endDate: '2025-12-31',
    status: 'active',
    riskScore: 48,
    analysisStatus: 'in_progress',
    clauses: [],
    alerts: [
      {
        id: '1',
        type: 'missing',
        title: 'Cláusula de LGPD ausente',
        description: 'Contrato não possui cláusula de proteção de dados',
        severity: 'critical',
      },
    ],
  },
  {
    id: '4',
    title: 'Contrato de Facilities - Universidade Federal',
    client: 'Universidade Federal',
    type: 'Facilities',
    value: 89000,
    startDate: '2024-01-01',
    endDate: '2025-12-31',
    status: 'expired',
    riskScore: 85,
    analysisStatus: 'analyzed',
    clauses: [],
    alerts: [
      {
        id: '1',
        type: 'risk',
        title: 'Contrato expirado sem renovação',
        description: 'Risco legal alto, regularizar urgente',
        severity: 'critical',
      },
    ],
  },
];

const riskCategories = [
  { label: 'Financeiro', count: 12, risk: 'medium' },
  { label: 'Jurídico', count: 8, risk: 'high' },
  { label: 'Operacional', count: 5, risk: 'low' },
  { label: 'Compliance', count: 3, risk: 'high' },
];

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  expiring: { label: 'Vencendo', color: 'warning' as const },
  expired: { label: 'Vencido', color: 'danger' as const },
  pending: { label: 'Pendente', color: 'info' as const },
};

const severityConfig = {
  low: { label: 'Baixo', color: 'success' as const },
  medium: { label: 'Médio', color: 'warning' as const },
  high: { label: 'Alto', color: 'danger' as const },
  critical: { label: 'Crítico', color: 'danger' as const },
};

export function ContractAnalysisPage() {
  const [contracts, setContracts] = useState(mockContracts);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('contracts');

  const handleAnalyzeContract = useCallback(async (contractId: string) => {
    setIsAnalyzing(true);
    // Simulate AI analysis
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setContracts((prev) =>
      prev.map((c) =>
        c.id === contractId ? { ...c, analysisStatus: 'analyzed' as const } : c
      )
    );
    setIsAnalyzing(false);
  }, []);

  const filteredContracts = contracts.filter((contract) => {
    const matchesSearch =
      contract.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      contract.client.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter =
      filterStatus === 'all' || contract.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const stats = {
    total: contracts.length,
    active: contracts.filter((c) => c.status === 'active').length,
    expiring: contracts.filter((c) => c.status === 'expiring').length,
    expired: contracts.filter((c) => c.status === 'expired').length,
    totalValue: contracts.reduce((sum, c) => sum + c.value, 0),
    avgRisk: Math.round(
      contracts.reduce((sum, c) => sum + c.riskScore, 0) / contracts.length
    ),
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'text-red-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Scale className="w-8 h-8 text-accent-primary" />
              Análise de Contratos com IA
            </h1>
            <p className="text-text-secondary mt-1">
              Análise automática de cláusulas, riscos e recomendações
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              Reanalisar Todos
            </Button>
            <Button
              variant="primary"
              leftIcon={<Upload className="w-4 h-4" />}
              onClick={() => setUploadModalOpen(true)}
            >
              Upload Contrato
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total de Contratos"
              value={stats.total}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Contratos Ativos"
              value={stats.active}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Vencendo (30 dias)"
              value={stats.expiring}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Valor Total"
              value={`R$ ${(stats.totalValue / 1000).toFixed(0)}K`}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <StatCard
              title="Risco Médio"
              value={`${stats.avgRisk}%`}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor={stats.avgRisk >= 50 ? 'warning' : 'success'}
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="contracts" label="Contratos" />
          <Tab value="risks" label="Análise de Riscos" />
          <Tab value="alerts" label="Alertas" />
          <Tab value="reports" label="Relatórios" />
        </Tabs>

        {activeTab === 'contracts' && (
          <>
            {/* Filters */}
            <Card>
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                      <Input
                        placeholder="Buscar contratos..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary text-sm"
                    >
                      <option value="all">Todos os status</option>
                      <option value="active">Ativos</option>
                      <option value="expiring">Vencendo</option>
                      <option value="expired">Vencidos</option>
                      <option value="pending">Pendentes</option>
                    </select>
                    <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                      Mais Filtros
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Contracts Table */}
            <Card>
              <CardHeader title="Contratos" subtitle={`${filteredContracts.length} contratos encontrados`} />
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Contrato</TableHead>
                    <TableHead>Cliente</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Valor Mensal</TableHead>
                    <TableHead>Vencimento</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Risco IA</TableHead>
                    <TableHead>Análise</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredContracts.map((contract) => (
                    <TableRow key={contract.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                            <FileText className="w-5 h-5 text-accent-primary" />
                          </div>
                          <div>
                            <p className="font-medium text-text-primary text-sm line-clamp-1 max-w-[200px]">
                              {contract.title}
                            </p>
                            {contract.alerts.length > 0 && (
                              <div className="flex items-center gap-1 mt-1">
                                <AlertCircle className="w-3 h-3 text-red-500" />
                                <span className="text-xs text-red-500">
                                  {contract.alerts.length} alerta(s)
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-text-muted" />
                          <span className="text-sm text-text-primary">{contract.client}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">{contract.type}</Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm font-medium text-text-primary">
                          R$ {contract.value.toLocaleString('pt-BR')}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-text-muted" />
                          <span className="text-sm text-text-primary">
                            {new Date(contract.endDate).toLocaleDateString('pt-BR')}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusConfig[contract.status].color}>
                          {statusConfig[contract.status].label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16">
                            <Progress
                              value={contract.riskScore}
                              color={
                                contract.riskScore >= 70
                                  ? 'danger'
                                  : contract.riskScore >= 40
                                  ? 'warning'
                                  : 'success'
                              }
                            />
                          </div>
                          <span className={`text-sm font-medium ${getRiskColor(contract.riskScore)}`}>
                            {contract.riskScore}%
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {contract.analysisStatus === 'analyzed' ? (
                          <Badge variant="success" leftIcon={<CheckCircle2 className="w-3 h-3" />}>
                            Analisado
                          </Badge>
                        ) : contract.analysisStatus === 'in_progress' ? (
                          <Badge variant="warning" leftIcon={<RefreshCw className="w-3 h-3 animate-spin" />}>
                            Analisando
                          </Badge>
                        ) : (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleAnalyzeContract(contract.id)}
                            disabled={isAnalyzing}
                          >
                            <Sparkles className="w-4 h-4 mr-1" />
                            Analisar
                          </Button>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedContract(contract);
                              setDetailsModalOpen(true);
                            }}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Dropdown
                            trigger={
                              <Button variant="ghost" size="sm">
                                <MoreVertical className="w-4 h-4" />
                              </Button>
                            }
                            items={[
                              { label: 'Editar', icon: <FileText className="w-4 h-4" /> },
                              { label: 'Download PDF', icon: <Download className="w-4 h-4" /> },
                              { label: 'Reanalisar', icon: <RefreshCw className="w-4 h-4" /> },
                            ]}
                          />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          </>
        )}

        {activeTab === 'risks' && (
          <div className="grid grid-cols-3 gap-6">
            {/* Risk Overview */}
            <Card className="col-span-2">
              <CardHeader title="Visão Geral de Riscos" />
              <CardBody>
                <div className="space-y-4">
                  {riskCategories.map((category, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${
                          category.risk === 'high' ? 'bg-red-500' :
                          category.risk === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                        }`} />
                        <span className="font-medium text-text-primary">{category.label}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-text-muted">{category.count} cláusulas</span>
                        <Badge variant={severityConfig[category.risk].color}>
                          {severityConfig[category.risk].label}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Risk Distribution */}
            <Card>
              <CardHeader title="Distribuição de Risco" />
              <CardBody>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-4xl font-bold text-text-primary">{stats.avgRisk}%</p>
                    <p className="text-sm text-text-muted">Risco médio dos contratos</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-text-muted">Baixo (0-40%)</span>
                      <span className="text-green-500">{contracts.filter(c => c.riskScore < 40).length}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-text-muted">Médio (40-70%)</span>
                      <span className="text-yellow-500">{contracts.filter(c => c.riskScore >= 40 && c.riskScore < 70).length}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-text-muted">Alto (70-100%)</span>
                      <span className="text-red-500">{contracts.filter(c => c.riskScore >= 70).length}</span>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'alerts' && (
          <Card>
            <CardHeader title="Alertas de Contratos" />
            <CardBody>
              <div className="space-y-4">
                {contracts.flatMap(contract =>
                  contract.alerts.map(alert => ({
                    ...alert,
                    contractTitle: contract.title,
                    contractId: contract.id,
                  }))
                ).map((alert, idx) => (
                  <div key={idx} className="flex items-start gap-4 p-4 bg-bg-tertiary rounded-lg">
                    <div className={`p-2 rounded-lg ${
                      alert.severity === 'critical' ? 'bg-red-500/10' :
                      alert.severity === 'high' ? 'bg-orange-500/10' :
                      alert.severity === 'medium' ? 'bg-yellow-500/10' : 'bg-green-500/10'
                    }`}>
                      <AlertTriangle className={`w-5 h-5 ${
                        alert.severity === 'critical' ? 'text-red-500' :
                        alert.severity === 'high' ? 'text-orange-500' :
                        alert.severity === 'medium' ? 'text-yellow-500' : 'text-green-500'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-text-primary">{alert.title}</p>
                        <Badge variant={severityConfig[alert.severity].color}>
                          {severityConfig[alert.severity].label}
                        </Badge>
                      </div>
                      <p className="text-sm text-text-muted mt-1">{alert.description}</p>
                      <p className="text-xs text-text-muted mt-2">
                        Contrato: {alert.contractTitle}
                      </p>
                    </div>
                    <Button variant="secondary" size="sm">
                      Ver Contrato
                    </Button>
                  </div>
                ))}
                {contracts.flatMap(c => c.alerts).length === 0 && (
                  <EmptyState
                    icon={<CheckCircle2 className="w-12 h-12" />}
                    title="Nenhum alerta"
                    description="Todos os contratos estão em conformidade"
                  />
                )}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'reports' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Relatórios Disponíveis" />
              <CardBody>
                <div className="space-y-3">
                  {[
                    { title: 'Resumo de Contratos', description: 'Visão geral de todos os contratos', icon: FileText },
                    { title: 'Análise de Riscos', description: 'Detalhamento de riscos identificados', icon: AlertTriangle },
                    { title: 'Vencimentos Próximos', description: 'Contratos próximos do vencimento', icon: Calendar },
                    { title: 'Compliance LGPD', description: 'Verificação de conformidade', icon: Shield },
                  ].map((report, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg hover:bg-bg-tertiary/80 transition-colors cursor-pointer">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-accent-primary/10">
                          <report.icon className="w-5 h-5 text-accent-primary" />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary text-sm">{report.title}</p>
                          <p className="text-xs text-text-muted">{report.description}</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Gerar Novo Relatório" />
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-text-primary">Tipo de Relatório</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>Análise Completa</option>
                      <option>Resumo Executivo</option>
                      <option>Análise de Riscos</option>
                      <option>Comparativo</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-text-primary">Período</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>Último mês</option>
                      <option>Último trimestre</option>
                      <option>Último ano</option>
                      <option>Personalizado</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-text-primary">Formato</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>PDF</option>
                      <option>Excel</option>
                      <option>Word</option>
                    </select>
                  </div>
                  <Button variant="primary" className="w-full" leftIcon={<Sparkles className="w-4 h-4" />}>
                    Gerar com IA
                  </Button>
                </div>
              </CardBody>
            </Card>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Upload de Contrato"
        size="md"
      >
        <div className="space-y-4">
          <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent-primary transition-colors cursor-pointer">
            <Upload className="w-12 h-12 text-text-muted mx-auto mb-4" />
            <p className="text-text-primary font-medium">Arraste arquivos aqui</p>
            <p className="text-sm text-text-muted mt-1">ou clique para selecionar</p>
            <p className="text-xs text-text-muted mt-2">PDF, DOC, DOCX (máx. 10MB)</p>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="auto-analyze" className="rounded" defaultChecked />
            <label htmlFor="auto-analyze" className="text-sm text-text-primary">
              Analisar automaticamente com IA após upload
            </label>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setUploadModalOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              Upload
            </Button>
          </div>
        </div>
      </Modal>

      {/* Contract Details Modal */}
      <Modal
        isOpen={detailsModalOpen}
        onClose={() => setDetailsModalOpen(false)}
        title="Detalhes do Contrato"
        size="lg"
      >
        {selectedContract && (
          <div className="space-y-6">
            {/* Contract Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-text-muted">Cliente</p>
                <p className="text-text-primary font-medium">{selectedContract.client}</p>
              </div>
              <div>
                <p className="text-sm text-text-muted">Tipo</p>
                <p className="text-text-primary font-medium">{selectedContract.type}</p>
              </div>
              <div>
                <p className="text-sm text-text-muted">Valor Mensal</p>
                <p className="text-text-primary font-medium">
                  R$ {selectedContract.value.toLocaleString('pt-BR')}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-muted">Vigência</p>
                <p className="text-text-primary font-medium">
                  {new Date(selectedContract.startDate).toLocaleDateString('pt-BR')} -{' '}
                  {new Date(selectedContract.endDate).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>

            {/* Risk Score */}
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-text-muted">Score de Risco IA</span>
                <span className={`font-bold ${getRiskColor(selectedContract.riskScore)}`}>
                  {selectedContract.riskScore}%
                </span>
              </div>
              <Progress
                value={selectedContract.riskScore}
                color={
                  selectedContract.riskScore >= 70
                    ? 'danger'
                    : selectedContract.riskScore >= 40
                    ? 'warning'
                    : 'success'
                }
              />
            </div>

            {/* Clauses */}
            {selectedContract.clauses.length > 0 && (
              <div>
                <h4 className="font-medium text-text-primary mb-3">Cláusulas Analisadas</h4>
                <div className="space-y-3">
                  {selectedContract.clauses.map((clause) => (
                    <div key={clause.id} className="p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-text-primary">{clause.title}</span>
                        <Badge variant={severityConfig[clause.risk].color}>
                          {severityConfig[clause.risk].label}
                        </Badge>
                      </div>
                      <p className="text-sm text-text-muted">{clause.description}</p>
                      {clause.recommendation && (
                        <div className="mt-2 p-2 bg-accent-primary/10 rounded flex items-start gap-2">
                          <Sparkles className="w-4 h-4 text-accent-primary mt-0.5" />
                          <p className="text-sm text-accent-primary">{clause.recommendation}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Alerts */}
            {selectedContract.alerts.length > 0 && (
              <div>
                <h4 className="font-medium text-text-primary mb-3">Alertas</h4>
                <div className="space-y-2">
                  {selectedContract.alerts.map((alert) => (
                    <div key={alert.id} className="flex items-start gap-3 p-3 bg-red-500/10 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                      <div>
                        <p className="font-medium text-red-500">{alert.title}</p>
                        <p className="text-sm text-text-muted">{alert.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
                Download PDF
              </Button>
              <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />}>
                Reanalisar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}

export default ContractAnalysisPage;
