'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  Shield,
  MapPin,
  FileText,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Edit2,
  Trash2,
  AlertOctagon,
  CheckCircle,
  Clock,
  Target,
  Activity,
  BarChart3,
  Calendar,
  Users,
  Building,
  ChevronRight
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { DataTable, Column } from '../../design-system/components/Table';
import { SimpleTabBar } from '../../design-system/components/Tabs';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

// Types
interface RiskAssessment {
  id: string;
  sector: string;
  sectorId: string;
  riskType: 'fisico' | 'quimico' | 'biologico' | 'ergonomico' | 'acidente';
  riskName: string;
  source: string;
  exposedWorkers: number;
  severity: 'trivial' | 'toleravel' | 'moderado' | 'substancial' | 'intoleravel';
  probability: 'improvavel' | 'remota' | 'possivel' | 'provavel' | 'frequente';
  riskLevel: number;
  controlMeasures: string[];
  status: 'identified' | 'controlled' | 'monitoring' | 'eliminated';
  lastAssessment: string;
  nextAssessment: string;
}

interface ActionPlan {
  id: string;
  riskId: string;
  riskName: string;
  sector: string;
  action: string;
  responsible: string;
  deadline: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  priority: 'low' | 'medium' | 'high' | 'critical';
  investmentRequired: number;
  completedAt: string | null;
}

// Mock Data
const mockRisks: RiskAssessment[] = [
  {
    id: '1',
    sector: 'Produção Industrial',
    sectorId: 'PROD-001',
    riskType: 'fisico',
    riskName: 'Ruído Ocupacional',
    source: 'Máquinas e equipamentos industriais',
    exposedWorkers: 45,
    severity: 'substancial',
    probability: 'frequente',
    riskLevel: 20,
    controlMeasures: ['Uso de protetor auricular', 'Enclausuramento de máquinas', 'Rodízio de funções'],
    status: 'controlled',
    lastAssessment: '2024-01-15',
    nextAssessment: '2024-07-15'
  },
  {
    id: '2',
    sector: 'Laboratório Químico',
    sectorId: 'LAB-001',
    riskType: 'quimico',
    riskName: 'Exposição a Solventes',
    source: 'Manipulação de produtos químicos',
    exposedWorkers: 12,
    severity: 'moderado',
    probability: 'possivel',
    riskLevel: 9,
    controlMeasures: ['Uso de EPIs', 'Ventilação local exaustora', 'Procedimentos operacionais'],
    status: 'monitoring',
    lastAssessment: '2024-02-01',
    nextAssessment: '2024-08-01'
  },
  {
    id: '3',
    sector: 'Escritório Administrativo',
    sectorId: 'ADM-001',
    riskType: 'ergonomico',
    riskName: 'Postura Inadequada',
    source: 'Mobiliário e organização do trabalho',
    exposedWorkers: 78,
    severity: 'toleravel',
    probability: 'provavel',
    riskLevel: 8,
    controlMeasures: ['Análise ergonômica', 'Mobiliário ajustável', 'Ginástica laboral'],
    status: 'controlled',
    lastAssessment: '2024-01-20',
    nextAssessment: '2024-07-20'
  },
  {
    id: '4',
    sector: 'Almoxarifado',
    sectorId: 'ALM-001',
    riskType: 'acidente',
    riskName: 'Queda de Materiais',
    source: 'Empilhamento de caixas e paletes',
    exposedWorkers: 15,
    severity: 'substancial',
    probability: 'possivel',
    riskLevel: 12,
    controlMeasures: ['Organização do estoque', 'Sinalização', 'Treinamento'],
    status: 'identified',
    lastAssessment: '2024-02-10',
    nextAssessment: '2024-05-10'
  },
  {
    id: '5',
    sector: 'Enfermaria',
    sectorId: 'ENF-001',
    riskType: 'biologico',
    riskName: 'Contato com Fluidos Biológicos',
    source: 'Atendimento a funcionários',
    exposedWorkers: 4,
    severity: 'moderado',
    probability: 'possivel',
    riskLevel: 9,
    controlMeasures: ['Uso de EPIs', 'Protocolo de descarte', 'Vacinação'],
    status: 'controlled',
    lastAssessment: '2024-01-25',
    nextAssessment: '2024-07-25'
  }
];

const mockActionPlans: ActionPlan[] = [
  {
    id: '1',
    riskId: '1',
    riskName: 'Ruído Ocupacional',
    sector: 'Produção Industrial',
    action: 'Instalar cabines acústicas nas máquinas principais',
    responsible: 'Eng. Segurança',
    deadline: '2024-04-30',
    status: 'in_progress',
    priority: 'high',
    investmentRequired: 45000,
    completedAt: null
  },
  {
    id: '2',
    riskId: '2',
    riskName: 'Exposição a Solventes',
    sector: 'Laboratório Químico',
    action: 'Substituir solvente por alternativa menos tóxica',
    responsible: 'Químico Responsável',
    deadline: '2024-03-15',
    status: 'completed',
    priority: 'high',
    investmentRequired: 8000,
    completedAt: '2024-03-10'
  },
  {
    id: '3',
    riskId: '4',
    riskName: 'Queda de Materiais',
    sector: 'Almoxarifado',
    action: 'Instalar redes de proteção e delimitar áreas',
    responsible: 'Supervisor Almoxarifado',
    deadline: '2024-02-28',
    status: 'overdue',
    priority: 'critical',
    investmentRequired: 12000,
    completedAt: null
  },
  {
    id: '4',
    riskId: '3',
    riskName: 'Postura Inadequada',
    sector: 'Escritório Administrativo',
    action: 'Adquirir cadeiras ergonômicas para todos os postos',
    responsible: 'RH',
    deadline: '2024-05-30',
    status: 'pending',
    priority: 'medium',
    investmentRequired: 35000,
    completedAt: null
  }
];

const riskDistributionData = [
  { name: 'Físico', value: 35, color: '#f59e0b' },
  { name: 'Químico', value: 20, color: '#ef4444' },
  { name: 'Biológico', value: 10, color: '#10b981' },
  { name: 'Ergonômico', value: 25, color: '#6366f1' },
  { name: 'Acidente', value: 10, color: '#8b5cf6' }
];

const sectorRiskData = [
  { sector: 'Produção', risks: 12, controlled: 8, pending: 4 },
  { sector: 'Laboratório', risks: 6, controlled: 4, pending: 2 },
  { sector: 'Escritório', risks: 4, controlled: 3, pending: 1 },
  { sector: 'Almoxarifado', risks: 5, controlled: 2, pending: 3 },
  { sector: 'Enfermaria', risks: 3, controlled: 3, pending: 0 }
];

const radarData = [
  { category: 'Físico', nivel: 75 },
  { category: 'Químico', nivel: 45 },
  { category: 'Biológico', nivel: 30 },
  { category: 'Ergonômico', nivel: 60 },
  { category: 'Acidente', nivel: 50 }
];

const tabs = [
  { value: 'risks', label: 'Riscos Identificados', icon: <AlertTriangle className="h-4 w-4" /> },
  { value: 'actions', label: 'Plano de Ação', icon: <Target className="h-4 w-4" /> },
  { value: 'sectors', label: 'Mapa de Riscos', icon: <MapPin className="h-4 w-4" /> },
  { value: 'documents', label: 'Documentos', icon: <FileText className="h-4 w-4" /> }
];

export function PPRAPage() {
  const [activeTab, setActiveTab] = useState('risks');
  const [searchTerm, setSearchTerm] = useState('');
  const [showRiskModal, setShowRiskModal] = useState(false);
  const [showActionModal, setShowActionModal] = useState(false);
  const [selectedRiskType, setSelectedRiskType] = useState<string>('all');

  const getRiskTypeInfo = (type: RiskAssessment['riskType']) => {
    const types = {
      fisico: { label: 'Físico', color: 'warning' as const, icon: Activity },
      quimico: { label: 'Químico', color: 'danger' as const, icon: AlertOctagon },
      biologico: { label: 'Biológico', color: 'success' as const, icon: Shield },
      ergonomico: { label: 'Ergonômico', color: 'primary' as const, icon: Users },
      acidente: { label: 'Acidente', color: 'info' as const, icon: AlertTriangle }
    };
    return types[type];
  };

  const getSeverityInfo = (severity: RiskAssessment['severity']) => {
    const severities = {
      trivial: { label: 'Trivial', color: 'success' as const },
      toleravel: { label: 'Tolerável', color: 'info' as const },
      moderado: { label: 'Moderado', color: 'warning' as const },
      substancial: { label: 'Substancial', color: 'danger' as const },
      intoleravel: { label: 'Intolerável', color: 'danger' as const }
    };
    return severities[severity];
  };

  const getStatusInfo = (status: RiskAssessment['status']) => {
    const statuses = {
      identified: { label: 'Identificado', color: 'warning' as const },
      controlled: { label: 'Controlado', color: 'success' as const },
      monitoring: { label: 'Em Monitoramento', color: 'info' as const },
      eliminated: { label: 'Eliminado', color: 'success' as const }
    };
    return statuses[status];
  };

  const getActionStatusInfo = (status: ActionPlan['status']) => {
    const statuses = {
      pending: { label: 'Pendente', color: 'warning' as const },
      in_progress: { label: 'Em Andamento', color: 'info' as const },
      completed: { label: 'Concluída', color: 'success' as const },
      overdue: { label: 'Atrasada', color: 'danger' as const }
    };
    return statuses[status];
  };

  const getPriorityInfo = (priority: ActionPlan['priority']) => {
    const priorities = {
      low: { label: 'Baixa', color: 'success' as const },
      medium: { label: 'Média', color: 'warning' as const },
      high: { label: 'Alta', color: 'danger' as const },
      critical: { label: 'Crítica', color: 'danger' as const }
    };
    return priorities[priority];
  };

  const riskColumns: Column<RiskAssessment>[] = [
    {
      key: 'riskType',
      header: 'Tipo',
      sortable: true,
      render: (row) => {
        const info = getRiskTypeInfo(row.riskType);
        const Icon = info.icon;
        return (
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-lg bg-accent-${info.color}/20`}>
              <Icon className={`h-4 w-4 text-accent-${info.color}`} />
            </div>
            <Badge variant={info.color} size="sm">{info.label}</Badge>
          </div>
        );
      }
    },
    {
      key: 'riskName',
      header: 'Risco',
      sortable: true,
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.riskName}</p>
          <p className="text-xs text-text-secondary">{row.source}</p>
        </div>
      )
    },
    {
      key: 'sector',
      header: 'Setor',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <Building className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary">{row.sector}</span>
        </div>
      )
    },
    {
      key: 'exposedWorkers',
      header: 'Expostos',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary">{row.exposedWorkers}</span>
        </div>
      )
    },
    {
      key: 'severity',
      header: 'Severidade',
      sortable: true,
      render: (row) => {
        const info = getSeverityInfo(row.severity);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'riskLevel',
      header: 'Nível',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <div className={`
            w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
            ${row.riskLevel >= 15 ? 'bg-accent-danger/20 text-accent-danger' :
              row.riskLevel >= 8 ? 'bg-accent-warning/20 text-accent-warning' :
              'bg-accent-success/20 text-accent-success'}
          `}>
            {row.riskLevel}
          </div>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row) => {
        const info = getStatusInfo(row.status);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit2 className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const actionColumns: Column<ActionPlan>[] = [
    {
      key: 'priority',
      header: 'Prioridade',
      sortable: true,
      render: (row) => {
        const info = getPriorityInfo(row.priority);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'riskName',
      header: 'Risco Associado',
      sortable: true,
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.riskName}</p>
          <p className="text-xs text-text-secondary">{row.sector}</p>
        </div>
      )
    },
    {
      key: 'action',
      header: 'Ação',
      render: (row) => (
        <p className="text-text-primary max-w-xs truncate">{row.action}</p>
      )
    },
    {
      key: 'responsible',
      header: 'Responsável',
      sortable: true
    },
    {
      key: 'deadline',
      header: 'Prazo',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary">
            {new Date(row.deadline).toLocaleDateString('pt-BR')}
          </span>
        </div>
      )
    },
    {
      key: 'investmentRequired',
      header: 'Investimento',
      sortable: true,
      render: (row) => (
        <span className="text-text-primary font-medium">
          {row.investmentRequired.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row) => {
        const info = getActionStatusInfo(row.status);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit2 className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const filteredRisks = mockRisks.filter(risk => {
    const matchesSearch = risk.riskName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         risk.sector.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedRiskType === 'all' || risk.riskType === selectedRiskType;
    return matchesSearch && matchesType;
  });

  const filteredActions = mockActionPlans.filter(action =>
    action.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
    action.riskName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-text-primary">
            PGR / PPRA - Riscos Ambientais
          </h1>
          <p className="text-text-secondary mt-1">
            Programa de Gerenciamento de Riscos (NR-1) e Prevenção de Riscos Ambientais (NR-9)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Exportar PGR
          </Button>
          <Button variant="primary" onClick={() => setShowRiskModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Novo Risco
          </Button>
        </div>
      </div>

      {/* Stats */}
      <StatGrid columns={5}>
        <StatCard
          title="Riscos Identificados"
          value="30"
          icon={<AlertTriangle className="h-5 w-5" />}
          change={3}
          changeLabel="novos este mês"
        />
        <StatCard
          title="Controlados"
          value="20"
          changeLabel="67% do total"
          icon={<CheckCircle className="h-5 w-5" />}
          iconColor="success"
        />
        <StatCard
          title="Em Monitoramento"
          value="6"
          icon={<Activity className="h-5 w-5" />}
          iconColor="info"
        />
        <StatCard
          title="Ações Pendentes"
          value="8"
          icon={<Target className="h-5 w-5" />}
          iconColor="warning"
        />
        <StatCard
          title="Trabalhadores Expostos"
          value="154"
          icon={<Users className="h-5 w-5" />}
          iconColor="info"
        />
      </StatGrid>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Distribuição por Tipo
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {riskDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Risks by Sector */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Riscos por Setor
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sectorRiskData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                  <XAxis type="number" stroke="#64748b" />
                  <YAxis dataKey="sector" type="category" stroke="#64748b" width={80} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="controlled" name="Controlados" fill="#10b981" stackId="a" />
                  <Bar dataKey="pending" name="Pendentes" fill="#f59e0b" stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Risk Radar */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Perfil de Risco
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#2d2d3d" />
                  <PolarAngleAxis dataKey="category" stroke="#64748b" />
                  <PolarRadiusAxis stroke="#64748b" />
                  <Radar
                    name="Nível de Risco"
                    dataKey="nivel"
                    stroke="#6366f1"
                    fill="#6366f1"
                    fillOpacity={0.3}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Tabs */}
      <SimpleTabBar
        tabs={tabs}
        value={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Content */}
      {activeTab === 'risks' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Inventário de Riscos
              </h3>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                  <Input
                    placeholder="Buscar riscos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <select
                  className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary text-sm"
                  value={selectedRiskType}
                  onChange={(e) => setSelectedRiskType(e.target.value)}
                >
                  <option value="all">Todos os tipos</option>
                  <option value="fisico">Físico</option>
                  <option value="quimico">Químico</option>
                  <option value="biologico">Biológico</option>
                  <option value="ergonomico">Ergonômico</option>
                  <option value="acidente">Acidente</option>
                </select>
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <DataTable<RiskAssessment>
              data={filteredRisks}
              columns={riskColumns}
              keyExtractor={(row) => row.id}
            />
          </CardBody>
        </Card>
      )}

      {activeTab === 'actions' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Plano de Ação
              </h3>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                  <Input
                    placeholder="Buscar ações..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <Button variant="primary" onClick={() => setShowActionModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Ação
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <DataTable<ActionPlan>
              data={filteredActions}
              columns={actionColumns}
              keyExtractor={(row) => row.id}
            />
          </CardBody>
        </Card>
      )}

      {activeTab === 'sectors' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sector List */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Setores Mapeados
              </h3>
            </CardHeader>
            <CardBody className="space-y-3">
              {sectorRiskData.map((sector, index) => (
                <motion.div
                  key={sector.sector}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-accent-primary/20">
                        <Building className="h-5 w-5 text-accent-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{sector.sector}</p>
                        <p className="text-sm text-text-secondary">
                          {sector.risks} riscos identificados
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-accent-success">{sector.controlled} controlados</span>
                          <span className="text-text-secondary">|</span>
                          <span className="text-accent-warning">{sector.pending} pendentes</span>
                        </div>
                        <div className="h-2 w-32 bg-bg-secondary rounded-full overflow-hidden mt-2">
                          <div
                            className="h-full bg-accent-success rounded-full"
                            style={{ width: `${(sector.controlled / sector.risks) * 100}%` }}
                          />
                        </div>
                      </div>
                      <ChevronRight className="h-5 w-5 text-text-secondary" />
                    </div>
                  </div>
                </motion.div>
              ))}
            </CardBody>
          </Card>

          {/* Risk Matrix */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Matriz de Risco
              </h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-6 gap-1">
                {/* Header */}
                <div className="col-span-1"></div>
                {['Trivial', 'Leve', 'Moderado', 'Severo', 'Catastrófico'].map((label) => (
                  <div key={label} className="text-center text-xs text-text-secondary p-2">
                    {label}
                  </div>
                ))}

                {/* Rows */}
                {['Frequente', 'Provável', 'Possível', 'Remota', 'Improvável'].map((prob, i) => (
                  <>
                    <div key={`label-${prob}`} className="text-xs text-text-secondary p-2 flex items-center">
                      {prob}
                    </div>
                    {[1, 2, 3, 4, 5].map((sev) => {
                      const level = (5 - i) * sev;
                      const bg = level >= 15 ? 'bg-accent-danger' :
                                level >= 8 ? 'bg-accent-warning' :
                                level >= 4 ? 'bg-accent-info' : 'bg-accent-success';
                      return (
                        <div
                          key={`${prob}-${sev}`}
                          className={`${bg}/30 rounded p-2 text-center text-xs font-medium ${bg.replace('bg-', 'text-')}`}
                        >
                          {level}
                        </div>
                      );
                    })}
                  </>
                ))}
              </div>

              <div className="mt-6 flex items-center justify-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-success/30" />
                  <span className="text-text-secondary">Trivial (1-3)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-info/30" />
                  <span className="text-text-secondary">Tolerável (4-7)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-warning/30" />
                  <span className="text-text-secondary">Moderado (8-14)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-accent-danger/30" />
                  <span className="text-text-secondary">Intolerável (15+)</span>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'documents' && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Documentos do PGR/PPRA
            </h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { name: 'PGR Completo 2024', type: 'PDF', size: '2.4 MB', date: '2024-01-15' },
                { name: 'Inventário de Riscos', type: 'XLSX', size: '456 KB', date: '2024-02-01' },
                { name: 'Plano de Ação', type: 'PDF', size: '1.1 MB', date: '2024-02-10' },
                { name: 'Laudos Técnicos', type: 'PDF', size: '3.8 MB', date: '2024-01-20' },
                { name: 'Relatório de Monitoramento', type: 'PDF', size: '890 KB', date: '2024-02-15' },
                { name: 'Matriz de Risco', type: 'XLSX', size: '234 KB', date: '2024-01-25' }
              ].map((doc, index) => (
                <motion.div
                  key={doc.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-accent-primary/20">
                      <FileText className="h-5 w-5 text-accent-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-text-primary truncate">{doc.name}</p>
                      <p className="text-sm text-text-secondary">
                        {doc.type} • {doc.size}
                      </p>
                      <p className="text-xs text-text-secondary mt-1">
                        Atualizado em {new Date(doc.date).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Risk Modal */}
      <Modal
        isOpen={showRiskModal}
        onClose={() => setShowRiskModal(false)}
        title="Novo Risco Ambiental"
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Tipo de Risco *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Selecione...</option>
                <option value="fisico">Físico</option>
                <option value="quimico">Químico</option>
                <option value="biologico">Biológico</option>
                <option value="ergonomico">Ergonômico</option>
                <option value="acidente">Acidente</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Setor *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Selecione...</option>
                <option value="prod">Produção Industrial</option>
                <option value="lab">Laboratório Químico</option>
                <option value="adm">Escritório Administrativo</option>
                <option value="alm">Almoxarifado</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Nome do Risco *
            </label>
            <Input placeholder="Ex: Ruído Ocupacional" />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Fonte Geradora *
            </label>
            <Input placeholder="Ex: Máquinas e equipamentos industriais" />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Trabalhadores Expostos
              </label>
              <Input type="number" placeholder="0" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Severidade
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="trivial">Trivial</option>
                <option value="toleravel">Tolerável</option>
                <option value="moderado">Moderado</option>
                <option value="substancial">Substancial</option>
                <option value="intoleravel">Intolerável</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Probabilidade
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="improvavel">Improvável</option>
                <option value="remota">Remota</option>
                <option value="possivel">Possível</option>
                <option value="provavel">Provável</option>
                <option value="frequente">Frequente</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Medidas de Controle
            </label>
            <textarea
              className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
              rows={3}
              placeholder="Descreva as medidas de controle existentes ou propostas..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="ghost" onClick={() => setShowRiskModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              Cadastrar Risco
            </Button>
          </div>
        </div>
      </Modal>

      {/* Action Modal */}
      <Modal
        isOpen={showActionModal}
        onClose={() => setShowActionModal(false)}
        title="Nova Ação Corretiva"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Risco Associado *
            </label>
            <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
              <option value="">Selecione o risco...</option>
              {mockRisks.map(risk => (
                <option key={risk.id} value={risk.id}>
                  {risk.riskName} - {risk.sector}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Descrição da Ação *
            </label>
            <textarea
              className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
              rows={3}
              placeholder="Descreva a ação corretiva ou preventiva..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Responsável *
              </label>
              <Input placeholder="Nome do responsável" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Prazo *
              </label>
              <Input type="date" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Prioridade
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="low">Baixa</option>
                <option value="medium">Média</option>
                <option value="high">Alta</option>
                <option value="critical">Crítica</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Investimento Necessário
              </label>
              <Input type="number" placeholder="R$ 0,00" />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="ghost" onClick={() => setShowActionModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              Criar Ação
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default PPRAPage;
