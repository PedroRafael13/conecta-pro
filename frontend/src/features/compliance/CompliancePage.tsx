'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  Search,
  Filter,
  Download,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  FileText,
  Eye,
  Lock,
  UserCheck,
  Scale,
  ClipboardCheck,
  Calendar,
  TrendingUp,
  AlertCircle,
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
} from '@/design-system/components';
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts';

// Types
interface ComplianceItem {
  id: string;
  name: string;
  category: 'lgpd' | 'trabalhista' | 'fiscal' | 'contratual' | 'seguranca';
  status: 'compliant' | 'pending' | 'non_compliant' | 'in_progress';
  dueDate: string | null;
  lastAudit: string;
  responsible: string;
  score: number;
  actions: number;
}

interface AuditLog {
  id: string;
  action: string;
  user: string;
  resource: string;
  timestamp: string;
  ip: string;
  result: 'success' | 'warning' | 'error';
}

// Mock Data
const complianceItems: ComplianceItem[] = [
  {
    id: '1',
    name: 'Política de Privacidade',
    category: 'lgpd',
    status: 'compliant',
    dueDate: null,
    lastAudit: '2026-01-10',
    responsible: 'Ana Costa',
    score: 100,
    actions: 0,
  },
  {
    id: '2',
    name: 'Consentimento de Dados',
    category: 'lgpd',
    status: 'compliant',
    dueDate: null,
    lastAudit: '2026-01-10',
    responsible: 'Ana Costa',
    score: 95,
    actions: 1,
  },
  {
    id: '3',
    name: 'eSocial - Eventos S-1200',
    category: 'trabalhista',
    status: 'compliant',
    dueDate: '2026-01-20',
    lastAudit: '2026-01-15',
    responsible: 'Carlos Lima',
    score: 100,
    actions: 0,
  },
  {
    id: '4',
    name: 'Certificados de Segurança',
    category: 'seguranca',
    status: 'pending',
    dueDate: '2026-01-30',
    lastAudit: '2025-12-15',
    responsible: 'Roberto Silva',
    score: 75,
    actions: 3,
  },
  {
    id: '5',
    name: 'SPED Fiscal Dezembro',
    category: 'fiscal',
    status: 'non_compliant',
    dueDate: '2026-01-25',
    lastAudit: '2026-01-14',
    responsible: 'Maria Santos',
    score: 45,
    actions: 5,
  },
  {
    id: '6',
    name: 'Renovação Contratos',
    category: 'contratual',
    status: 'in_progress',
    dueDate: '2026-02-01',
    lastAudit: '2026-01-12',
    responsible: 'Pedro Oliveira',
    score: 80,
    actions: 2,
  },
];

const auditLogs: AuditLog[] = [
  {
    id: '1',
    action: 'Login',
    user: 'admin@conectapro.com',
    resource: 'Sistema',
    timestamp: '2026-01-15T14:30:00',
    ip: '192.168.1.100',
    result: 'success',
  },
  {
    id: '2',
    action: 'Exportação de Dados',
    user: 'carlos@conectapro.com',
    resource: 'Relatório Financeiro',
    timestamp: '2026-01-15T14:15:00',
    ip: '192.168.1.105',
    result: 'success',
  },
  {
    id: '3',
    action: 'Alteração de Permissão',
    user: 'admin@conectapro.com',
    resource: 'Usuário: maria@conectapro.com',
    timestamp: '2026-01-15T13:45:00',
    ip: '192.168.1.100',
    result: 'warning',
  },
  {
    id: '4',
    action: 'Tentativa de Acesso',
    user: 'desconhecido',
    resource: 'API Financeiro',
    timestamp: '2026-01-15T13:30:00',
    ip: '45.33.32.156',
    result: 'error',
  },
  {
    id: '5',
    action: 'Backup Automático',
    user: 'sistema',
    resource: 'Database',
    timestamp: '2026-01-15T12:00:00',
    ip: 'localhost',
    result: 'success',
  },
];

const complianceScore = [
  { name: 'Score', value: 87, fill: '#6366f1' },
];

const categoryBreakdown = [
  { name: 'LGPD', value: 95, color: '#10b981' },
  { name: 'Trabalhista', value: 100, color: '#6366f1' },
  { name: 'Fiscal', value: 65, color: '#ef4444' },
  { name: 'Contratual', value: 80, color: '#f59e0b' },
  { name: 'Segurança', value: 75, color: '#8b5cf6' },
];

const categoryConfig = {
  lgpd: { label: 'LGPD', color: 'success' as const, icon: Lock },
  trabalhista: { label: 'Trabalhista', color: 'primary' as const, icon: UserCheck },
  fiscal: { label: 'Fiscal', color: 'warning' as const, icon: Scale },
  contratual: { label: 'Contratual', color: 'info' as const, icon: FileText },
  seguranca: { label: 'Segurança', color: 'secondary' as const, icon: Shield },
};

const statusConfig = {
  compliant: { label: 'Conforme', color: 'success' as const, icon: CheckCircle2 },
  pending: { label: 'Pendente', color: 'warning' as const, icon: Clock },
  non_compliant: { label: 'Não Conforme', color: 'danger' as const, icon: XCircle },
  in_progress: { label: 'Em Andamento', color: 'info' as const, icon: AlertCircle },
};

const complianceColumns: Column<ComplianceItem>[] = [
  {
    key: 'name',
    header: 'Item',
    render: (row) => {
      const category = categoryConfig[row.category];
      const CategoryIcon = category.icon;
      return (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-${category.color}/10`}>
            <CategoryIcon className={`w-4 h-4 text-${category.color}`} />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <Badge variant={category.color} size="sm">{category.label}</Badge>
          </div>
        </div>
      );
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const status = statusConfig[row.status];
      const StatusIcon = status.icon;
      return (
        <Badge variant={status.color} leftIcon={<StatusIcon className="w-3 h-3" />}>
          {status.label}
        </Badge>
      );
    },
  },
  {
    key: 'score',
    header: 'Score',
    render: (row) => (
      <div className="flex items-center gap-2">
        <div className="w-16 h-2 bg-bg-tertiary rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${
              row.score >= 90 ? 'bg-success' : row.score >= 70 ? 'bg-warning' : 'bg-danger'
            }`}
            style={{ width: `${row.score}%` }}
          />
        </div>
        <span className={`text-sm font-medium ${
          row.score >= 90 ? 'text-success' : row.score >= 70 ? 'text-warning' : 'text-danger'
        }`}>
          {row.score}%
        </span>
      </div>
    ),
  },
  {
    key: 'dueDate',
    header: 'Prazo',
    render: (row) => (
      row.dueDate ? (
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-text-muted" />
          <span className="text-sm text-text-secondary">
            {new Date(row.dueDate).toLocaleDateString('pt-BR')}
          </span>
        </div>
      ) : (
        <span className="text-text-muted">-</span>
      )
    ),
  },
  {
    key: 'responsible',
    header: 'Responsável',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.responsible} size="xs" />
        <span className="text-sm text-text-secondary">{row.responsible}</span>
      </div>
    ),
  },
  {
    key: 'actions',
    header: 'Ações',
    render: (row) => (
      row.actions > 0 ? (
        <Badge variant="warning" size="sm">{row.actions} pendente(s)</Badge>
      ) : (
        <Badge variant="success" size="sm">OK</Badge>
      )
    ),
  },
  {
    key: 'view',
    header: '',
    render: () => (
      <Button variant="ghost" size="sm" leftIcon={<Eye className="w-4 h-4" />}>
        Detalhes
      </Button>
    ),
  },
];

const auditColumns: Column<AuditLog>[] = [
  {
    key: 'timestamp',
    header: 'Data/Hora',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {new Date(row.timestamp).toLocaleString('pt-BR')}
      </span>
    ),
  },
  {
    key: 'action',
    header: 'Ação',
    render: (row) => <span className="font-medium text-text-primary">{row.action}</span>,
  },
  {
    key: 'user',
    header: 'Usuário',
    render: (row) => <span className="text-sm text-text-secondary">{row.user}</span>,
  },
  {
    key: 'resource',
    header: 'Recurso',
    render: (row) => <span className="text-sm text-text-secondary">{row.resource}</span>,
  },
  {
    key: 'ip',
    header: 'IP',
    render: (row) => <span className="font-mono text-xs text-text-muted">{row.ip}</span>,
  },
  {
    key: 'result',
    header: 'Resultado',
    render: (row) => {
      const config = {
        success: { label: 'Sucesso', color: 'success' as const },
        warning: { label: 'Alerta', color: 'warning' as const },
        error: { label: 'Erro', color: 'danger' as const },
      };
      const status = config[row.result];
      return <Badge variant={status.color} size="sm">{status.label}</Badge>;
    },
  },
];

export function CompliancePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('items');

  const filteredItems = complianceItems.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Stats
  const compliantCount = complianceItems.filter((i) => i.status === 'compliant').length;
  const pendingCount = complianceItems.filter((i) => i.status === 'pending' || i.status === 'in_progress').length;
  const nonCompliantCount = complianceItems.filter((i) => i.status === 'non_compliant').length;
  const overallScore = Math.round(complianceItems.reduce((acc, i) => acc + i.score, 0) / complianceItems.length);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Shield className="w-8 h-8 text-accent-primary" />
              Compliance & Auditoria
            </h1>
            <p className="text-text-secondary mt-1">
              Conformidade regulatória e trilha de auditoria
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar Relatório
            </Button>
            <Button variant="primary" leftIcon={<ClipboardCheck className="w-4 h-4" />}>
              Nova Auditoria
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-5 gap-4">
          {/* Score Gauge */}
          <Card className="col-span-1">
            <CardBody className="flex flex-col items-center justify-center py-4">
              <div className="w-32 h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart
                    cx="50%"
                    cy="50%"
                    innerRadius="70%"
                    outerRadius="100%"
                    data={complianceScore}
                    startAngle={180}
                    endAngle={0}
                  >
                    <RadialBar
                      background={{ fill: '#1a1a2e' }}
                      dataKey="value"
                      cornerRadius={10}
                    />
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-3xl font-bold text-accent-primary -mt-8">{overallScore}%</p>
              <p className="text-xs text-text-muted mt-2">Score Geral</p>
            </CardBody>
          </Card>

          {/* Other Stats */}
          <StatCard
            title="Conformes"
            value={compliantCount}
            icon={<CheckCircle2 className="w-6 h-6" />}
            iconColor="success"
          />
          <StatCard
            title="Pendentes"
            value={pendingCount}
            icon={<Clock className="w-6 h-6" />}
            iconColor="warning"
          />
          <StatCard
            title="Não Conformes"
            value={nonCompliantCount}
            icon={<XCircle className="w-6 h-6" />}
            iconColor="danger"
          />
          <StatCard
            title="Auditorias no Mês"
            value={12}
            change={8}
            icon={<ClipboardCheck className="w-6 h-6" />}
            iconColor="info"
          />
        </div>

        {/* Category Breakdown */}
        <div className="grid grid-cols-5 gap-4">
          {categoryBreakdown.map((cat) => (
            <Card key={cat.name}>
              <CardBody className="py-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-text-secondary">{cat.name}</span>
                  <span className={`font-bold ${
                    cat.value >= 90 ? 'text-success' : cat.value >= 70 ? 'text-warning' : 'text-danger'
                  }`}>
                    {cat.value}%
                  </span>
                </div>
                <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${cat.value}%`, backgroundColor: cat.color }}
                  />
                </div>
              </CardBody>
            </Card>
          ))}
        </div>

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'items', label: 'Itens de Compliance' },
                  { value: 'audit', label: 'Trilha de Auditoria' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <Input
                placeholder="Buscar..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
            </div>
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              {selectedTab === 'items' ? (
                <DataTable
                  columns={complianceColumns}
                  data={filteredItems}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <DataTable
                  columns={auditColumns}
                  data={auditLogs}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* Alerts */}
        {nonCompliantCount > 0 && (
          <Card className="border-danger/30 bg-danger/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-danger/10">
                  <AlertTriangle className="w-6 h-6 text-danger" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    {nonCompliantCount} item(ns) não conforme(s)
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Ações corretivas são necessárias para garantir a conformidade
                  </p>
                </div>
                <Button variant="danger" size="sm">
                  Ver Ações Pendentes
                </Button>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
