'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Download,
  Calendar,
  Filter,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  BarChart3,
  PieChart,
  TrendingUp,
  Users,
  DollarSign,
  Shield,
  Building2,
  Wrench,
  Eye,
  Printer,
  Mail,
  Plus,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
} from '@/design-system/components';

// Types
interface Report {
  id: string;
  name: string;
  description: string;
  category: 'financial' | 'operations' | 'hr' | 'security' | 'commercial' | 'executive';
  type: 'pdf' | 'excel' | 'dashboard';
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'on_demand';
  lastGenerated: string | null;
  nextGeneration: string | null;
  status: 'ready' | 'generating' | 'scheduled' | 'error';
  createdBy: string;
}

interface ReportExecution {
  id: string;
  reportName: string;
  generatedAt: string;
  generatedBy: string;
  format: 'pdf' | 'excel' | 'csv';
  fileSize: string;
  status: 'completed' | 'failed' | 'processing';
}

// Mock Data
const reports: Report[] = [
  {
    id: '1',
    name: 'Relatório Financeiro Mensal',
    description: 'Consolidado de receitas, despesas e fluxo de caixa',
    category: 'financial',
    type: 'pdf',
    frequency: 'monthly',
    lastGenerated: '2026-01-01 08:00',
    nextGeneration: '2026-02-01 08:00',
    status: 'ready',
    createdBy: 'Sistema',
  },
  {
    id: '2',
    name: 'Dashboard Executivo',
    description: 'KPIs principais da empresa em tempo real',
    category: 'executive',
    type: 'dashboard',
    frequency: 'daily',
    lastGenerated: '2026-01-15 06:00',
    nextGeneration: '2026-01-16 06:00',
    status: 'ready',
    createdBy: 'Sistema',
  },
  {
    id: '3',
    name: 'Escala de Funcionários',
    description: 'Escalas de trabalho por posto e turno',
    category: 'operations',
    type: 'excel',
    frequency: 'weekly',
    lastGenerated: '2026-01-13 00:00',
    nextGeneration: '2026-01-20 00:00',
    status: 'scheduled',
    createdBy: 'Ana Paula',
  },
  {
    id: '4',
    name: 'Ocorrências de Segurança',
    description: 'Registro de todas as ocorrências por cliente',
    category: 'security',
    type: 'pdf',
    frequency: 'monthly',
    lastGenerated: '2026-01-01 08:00',
    nextGeneration: '2026-02-01 08:00',
    status: 'ready',
    createdBy: 'Sistema',
  },
  {
    id: '5',
    name: 'Folha de Pagamento',
    description: 'Relatório analítico de folha de pagamento',
    category: 'hr',
    type: 'excel',
    frequency: 'monthly',
    lastGenerated: '2026-01-05 10:00',
    nextGeneration: '2026-02-05 10:00',
    status: 'ready',
    createdBy: 'Sistema',
  },
  {
    id: '6',
    name: 'Performance Comercial',
    description: 'Pipeline de vendas e taxa de conversão',
    category: 'commercial',
    type: 'pdf',
    frequency: 'weekly',
    lastGenerated: null,
    nextGeneration: null,
    status: 'generating',
    createdBy: 'Carlos Eduardo',
  },
];

const executions: ReportExecution[] = [
  { id: '1', reportName: 'Dashboard Executivo', generatedAt: '2026-01-15 06:00', generatedBy: 'Sistema', format: 'pdf', fileSize: '2.4 MB', status: 'completed' },
  { id: '2', reportName: 'Relatório Financeiro Mensal', generatedAt: '2026-01-15 05:30', generatedBy: 'Ana Paula', format: 'excel', fileSize: '1.8 MB', status: 'completed' },
  { id: '3', reportName: 'Performance Comercial', generatedAt: '2026-01-15 04:00', generatedBy: 'Sistema', format: 'pdf', fileSize: '', status: 'processing' },
  { id: '4', reportName: 'Ocorrências de Segurança', generatedAt: '2026-01-14 18:00', generatedBy: 'Roberto Silva', format: 'pdf', fileSize: '890 KB', status: 'completed' },
  { id: '5', reportName: 'Escala de Funcionários', generatedAt: '2026-01-13 08:00', generatedBy: 'Sistema', format: 'excel', fileSize: '456 KB', status: 'completed' },
];

const categoryConfig = {
  financial: { label: 'Financeiro', color: 'success' as const, icon: DollarSign },
  operations: { label: 'Operações', color: 'primary' as const, icon: Wrench },
  hr: { label: 'RH', color: 'info' as const, icon: Users },
  security: { label: 'Segurança', color: 'danger' as const, icon: Shield },
  commercial: { label: 'Comercial', color: 'warning' as const, icon: TrendingUp },
  executive: { label: 'Executivo', color: 'primary' as const, icon: BarChart3 },
};

const frequencyLabels = {
  daily: 'Diário',
  weekly: 'Semanal',
  monthly: 'Mensal',
  quarterly: 'Trimestral',
  on_demand: 'Sob Demanda',
};

const reportColumns: Column<Report>[] = [
  {
    key: 'name',
    header: 'Relatório',
    render: (row) => {
      const config = categoryConfig[row.category];
      const CategoryIcon = config.icon;
      return (
        <div className="flex items-center gap-3">
          <div className="p-2 bg-bg-tertiary rounded-lg">
            <CategoryIcon className="w-5 h-5 text-text-muted" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.description}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => {
      const config = categoryConfig[row.category];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'frequency',
    header: 'Frequência',
    render: (row) => <span className="text-sm">{frequencyLabels[row.frequency]}</span>,
  },
  {
    key: 'lastGenerated',
    header: 'Última Geração',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {row.lastGenerated || 'Nunca gerado'}
      </span>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const colors = {
        ready: 'success' as const,
        generating: 'primary' as const,
        scheduled: 'info' as const,
        error: 'danger' as const,
      };
      const labels = {
        ready: 'Pronto',
        generating: 'Gerando...',
        scheduled: 'Agendado',
        error: 'Erro',
      };
      return <Badge variant={colors[row.status]}>{labels[row.status]}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Visualizar">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Download">
          <Download className="w-4 h-4" />
        </Button>
        {row.status === 'ready' && (
          <Button variant="primary" size="sm" leftIcon={<RefreshCw className="w-3 h-3" />}>
            Gerar
          </Button>
        )}
      </div>
    ),
  },
];

const executionColumns: Column<ReportExecution>[] = [
  {
    key: 'reportName',
    header: 'Relatório',
    render: (row) => <span className="font-medium text-text-primary">{row.reportName}</span>,
  },
  {
    key: 'generatedAt',
    header: 'Gerado em',
    render: (row) => <span className="text-sm">{row.generatedAt}</span>,
  },
  {
    key: 'generatedBy',
    header: 'Por',
    render: (row) => <span className="text-sm text-text-secondary">{row.generatedBy}</span>,
  },
  {
    key: 'format',
    header: 'Formato',
    render: (row) => <Badge variant="info">{row.format.toUpperCase()}</Badge>,
  },
  {
    key: 'fileSize',
    header: 'Tamanho',
    render: (row) => <span className="text-sm">{row.fileSize || '-'}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const colors = {
        completed: 'success' as const,
        processing: 'primary' as const,
        failed: 'danger' as const,
      };
      const labels = {
        completed: 'Concluído',
        processing: 'Processando',
        failed: 'Falhou',
      };
      return <Badge variant={colors[row.status]}>{labels[row.status]}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        {row.status === 'completed' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Download">
              <Download className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Imprimir">
              <Printer className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Enviar por e-mail">
              <Mail className="w-4 h-4" />
            </Button>
          </>
        )}
      </div>
    ),
  },
];

export function ReportsPage() {
  const [selectedTab, setSelectedTab] = useState('templates');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Stats
  const totalReports = reports.length;
  const scheduledCount = reports.filter(r => r.status === 'scheduled').length;
  const generatingCount = reports.filter(r => r.status === 'generating').length;
  const todayExecutions = executions.filter(e => e.generatedAt.startsWith('2026-01-15')).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Central de Relatórios
            </h1>
            <p className="text-text-secondary mt-1">
              Gere e gerencie relatórios do sistema
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Calendar className="w-4 h-4" />}>
              Agendamentos
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Novo Relatório
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Templates"
              value={totalReports}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Agendados"
              value={scheduledCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Em Geração"
              value={generatingCount}
              icon={<RefreshCw className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Gerados Hoje"
              value={todayExecutions}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'templates', label: 'Templates de Relatório' },
                { value: 'history', label: 'Histórico de Execuções' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              {selectedTab === 'templates' ? (
                <DataTable
                  columns={reportColumns}
                  data={reports}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <DataTable
                  columns={executionColumns}
                  data={executions}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Report Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Gerar Novo Relatório"
          description="Configure os parâmetros do relatório"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Gerar Relatório
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Template"
              options={reports.map(r => ({ value: r.id, label: r.name }))}
              value=""
              onChange={() => {}}
              placeholder="Selecione o relatório..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data Início" type="date" />
              <Input label="Data Fim" type="date" />
            </div>
            <Select
              label="Formato de Saída"
              options={[
                { value: 'pdf', label: 'PDF' },
                { value: 'excel', label: 'Excel' },
                { value: 'csv', label: 'CSV' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />
            <Select
              label="Cliente (opcional)"
              options={[
                { value: 'all', label: 'Todos os Clientes' },
                { value: '1', label: 'Shopping Center Norte' },
                { value: '2', label: 'Hospital São Lucas' },
                { value: '3', label: 'Tech Park Empresarial' },
              ]}
              value="all"
              onChange={() => {}}
            />
            <div className="flex items-center gap-2">
              <input type="checkbox" id="sendEmail" className="rounded" />
              <label htmlFor="sendEmail" className="text-sm text-text-secondary">
                Enviar por e-mail após geração
              </label>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
