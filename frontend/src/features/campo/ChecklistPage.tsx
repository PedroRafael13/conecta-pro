'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  ClipboardList,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Copy,
  MoreVertical,
  FileText,
  Clock,
  User,
  Building2,
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
} from '@/design-system/components';

// Types
interface ChecklistTemplate {
  id: string;
  name: string;
  description: string;
  category: 'installation' | 'maintenance' | 'inspection' | 'security' | 'cleaning';
  itemsCount: number;
  isActive: boolean;
  createdBy: string;
  createdAt: string;
  usageCount: number;
}

interface ChecklistExecution {
  id: string;
  templateId: string;
  templateName: string;
  serviceOrderId: string;
  client: string;
  executor: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  completedItems: number;
  totalItems: number;
  score: number | null;
  startedAt: string | null;
  completedAt: string | null;
  notes: string;
}

// Mock Data - Templates
const templates: ChecklistTemplate[] = [
  {
    id: '1',
    name: 'Instalação CFTV Completa',
    description: 'Checklist para instalação de sistema de CFTV',
    category: 'installation',
    itemsCount: 25,
    isActive: true,
    createdBy: 'Admin',
    createdAt: '2025-12-01',
    usageCount: 156,
  },
  {
    id: '2',
    name: 'Manutenção Preventiva Câmeras',
    description: 'Verificação periódica de câmeras e DVR',
    category: 'maintenance',
    itemsCount: 18,
    isActive: true,
    createdBy: 'Admin',
    createdAt: '2025-11-15',
    usageCount: 89,
  },
  {
    id: '3',
    name: 'Vistoria de Segurança',
    description: 'Inspeção geral de equipamentos de segurança',
    category: 'inspection',
    itemsCount: 32,
    isActive: true,
    createdBy: 'Carlos Eduardo',
    createdAt: '2025-10-20',
    usageCount: 234,
  },
  {
    id: '4',
    name: 'Limpeza Técnica Equipamentos',
    description: 'Procedimentos de limpeza e higienização',
    category: 'cleaning',
    itemsCount: 12,
    isActive: true,
    createdBy: 'Admin',
    createdAt: '2025-09-10',
    usageCount: 67,
  },
  {
    id: '5',
    name: 'Checklist Ronda Noturna',
    description: 'Verificações durante rondas noturnas',
    category: 'security',
    itemsCount: 20,
    isActive: false,
    createdBy: 'Roberto Silva',
    createdAt: '2025-08-05',
    usageCount: 412,
  },
];

// Mock Data - Executions
const executions: ChecklistExecution[] = [
  {
    id: '1',
    templateId: '1',
    templateName: 'Instalação CFTV Completa',
    serviceOrderId: 'OS-2026-0142',
    client: 'Shopping Center Norte',
    executor: 'Carlos Eduardo',
    status: 'completed',
    completedItems: 25,
    totalItems: 25,
    score: 100,
    startedAt: '2026-01-15 09:00',
    completedAt: '2026-01-15 11:30',
    notes: 'Instalação concluída sem pendências',
  },
  {
    id: '2',
    templateId: '2',
    templateName: 'Manutenção Preventiva Câmeras',
    serviceOrderId: 'OS-2026-0141',
    client: 'Hospital São Lucas',
    executor: 'Ana Paula',
    status: 'in_progress',
    completedItems: 12,
    totalItems: 18,
    score: null,
    startedAt: '2026-01-15 14:00',
    completedAt: null,
    notes: '',
  },
  {
    id: '3',
    templateId: '3',
    templateName: 'Vistoria de Segurança',
    serviceOrderId: 'OS-2026-0140',
    client: 'Tech Park Empresarial',
    executor: 'Roberto Silva',
    status: 'failed',
    completedItems: 28,
    totalItems: 32,
    score: 75,
    startedAt: '2026-01-14 10:00',
    completedAt: '2026-01-14 14:00',
    notes: '4 itens com não conformidade - câmeras 5, 8, 12 e sensor bloco B',
  },
  {
    id: '4',
    templateId: '1',
    templateName: 'Instalação CFTV Completa',
    serviceOrderId: 'OS-2026-0139',
    client: 'Condomínio Aurora',
    executor: 'Pedro Santos',
    status: 'pending',
    completedItems: 0,
    totalItems: 25,
    score: null,
    startedAt: null,
    completedAt: null,
    notes: 'Aguardando liberação do cliente',
  },
];

const categoryConfig = {
  installation: { label: 'Instalação', color: 'primary' as const },
  maintenance: { label: 'Manutenção', color: 'info' as const },
  inspection: { label: 'Inspeção', color: 'warning' as const },
  security: { label: 'Segurança', color: 'danger' as const },
  cleaning: { label: 'Limpeza', color: 'success' as const },
};

const statusConfig = {
  pending: { label: 'Pendente', color: 'neutral' as const, icon: Clock },
  in_progress: { label: 'Em Andamento', color: 'primary' as const, icon: ClipboardList },
  completed: { label: 'Concluído', color: 'success' as const, icon: CheckCircle2 },
  failed: { label: 'Com Falhas', color: 'danger' as const, icon: XCircle },
};

const templateColumns: Column<ChecklistTemplate>[] = [
  {
    key: 'name',
    header: 'Template',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.name}</p>
        <p className="text-xs text-text-muted mt-1 truncate max-w-[300px]">{row.description}</p>
      </div>
    ),
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
    key: 'items',
    header: 'Itens',
    render: (row) => (
      <div className="flex items-center gap-2">
        <FileText className="w-4 h-4 text-text-muted" />
        <span>{row.itemsCount} itens</span>
      </div>
    ),
  },
  {
    key: 'usage',
    header: 'Uso',
    render: (row) => (
      <span className="text-sm text-text-secondary">{row.usageCount} execuções</span>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={row.isActive ? 'success' : 'neutral'}>
        {row.isActive ? 'Ativo' : 'Inativo'}
      </Badge>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Duplicar">
          <Copy className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const executionColumns: Column<ChecklistExecution>[] = [
  {
    key: 'template',
    header: 'Checklist',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.templateName}</p>
        <p className="text-xs text-text-muted mt-1">{row.serviceOrderId}</p>
      </div>
    ),
  },
  {
    key: 'client',
    header: 'Cliente',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Building2 className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.client}</span>
      </div>
    ),
  },
  {
    key: 'executor',
    header: 'Executor',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.executor} size="xs" />
        <span className="text-sm">{row.executor}</span>
      </div>
    ),
  },
  {
    key: 'progress',
    header: 'Progresso',
    render: (row) => {
      const percentage = Math.round((row.completedItems / row.totalItems) * 100);
      return (
        <div className="w-32">
          <div className="flex justify-between text-xs mb-1">
            <span>{row.completedItems}/{row.totalItems}</span>
            <span>{percentage}%</span>
          </div>
          <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                percentage === 100 ? 'bg-accent-success' : 'bg-accent-primary'
              }`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      );
    },
  },
  {
    key: 'score',
    header: 'Score',
    render: (row) => {
      if (row.score === null) return <span className="text-text-muted">-</span>;
      const color = row.score >= 90 ? 'text-accent-success' : row.score >= 70 ? 'text-accent-warning' : 'text-accent-danger';
      return <span className={`font-bold ${color}`}>{row.score}%</span>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      const StatusIcon = config.icon;
      return (
        <Badge variant={config.color} leftIcon={<StatusIcon className="w-3 h-3" />}>
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'pending' && (
          <Button variant="primary" size="sm">Iniciar</Button>
        )}
        {row.status === 'in_progress' && (
          <Button variant="success" size="sm">Continuar</Button>
        )}
      </div>
    ),
  },
];

export function ChecklistPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('executions');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<ChecklistExecution | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<ChecklistTemplate | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [newCategory, setNewCategory] = useState('');

  // Stats
  const totalTemplates = templates.filter(t => t.isActive).length;
  const pendingExecutions = executions.filter(e => e.status === 'pending').length;
  const inProgressExecutions = executions.filter(e => e.status === 'in_progress').length;
  const completedToday = executions.filter(e =>
    e.status === 'completed' && e.completedAt?.startsWith('2026-01-15')
  ).length;
  const avgScore = executions
    .filter(e => e.score !== null)
    .reduce((acc, e) => acc + (e.score || 0), 0) /
    executions.filter(e => e.score !== null).length;

  const filteredTemplates = templates.filter(t =>
    t.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredExecutions = executions.filter(e =>
    e.templateName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.client.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Checklists de Serviço
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie templates e execuções de checklists
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Novo Template
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Templates Ativos"
              value={totalTemplates}
              icon={<ClipboardList className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Pendentes"
              value={pendingExecutions}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Em Andamento"
              value={inProgressExecutions}
              icon={<ClipboardList className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Concluídos Hoje"
              value={completedToday}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Score Médio"
              value={`${Math.round(avgScore)}%`}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor={avgScore >= 90 ? 'success' : avgScore >= 70 ? 'warning' : 'danger'}
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'executions', label: 'Execuções' },
                  { value: 'templates', label: 'Templates' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardBody className="p-0">
              {selectedTab === 'executions' ? (
                <DataTable
                  columns={executionColumns}
                  data={filteredExecutions}
                  keyExtractor={(row) => row.id}
                  onRowClick={(row) => { setSelectedExecution(row); setSelectedTemplate(null); setShowDetailModal(true); }}
                />
              ) : (
                <DataTable
                  columns={templateColumns}
                  data={filteredTemplates}
                  keyExtractor={(row) => row.id}
                  onRowClick={(row) => { setSelectedTemplate(row); setSelectedExecution(null); setShowDetailModal(true); }}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Template Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Novo Template de Checklist"
          description="Crie um novo modelo de checklist"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar Template
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome do Template" placeholder="Ex: Instalação CFTV" required />
            <Input label="Descrição" placeholder="Descreva o objetivo do checklist" />
            <Select
              label="Categoria"
              options={[
                { value: 'installation', label: 'Instalação' },
                { value: 'maintenance', label: 'Manutenção' },
                { value: 'inspection', label: 'Inspeção' },
                { value: 'security', label: 'Segurança' },
                { value: 'cleaning', label: 'Limpeza' },
              ]}
              value={newCategory}
              onChange={(value) => setNewCategory(value)}
              placeholder="Selecione..."
            />
            <div className="pt-4 border-t border-border-subtle">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-text-primary">Itens do Checklist</h4>
                <Button variant="outline" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                  Adicionar Item
                </Button>
              </div>
              <p className="text-sm text-text-muted">
                Adicione os itens que serão verificados neste checklist
              </p>
            </div>
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedExecution ? 'Detalhes da Execução' : 'Detalhes do Template'}
          description={selectedExecution ? selectedExecution.templateName : selectedTemplate?.name || ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              {selectedExecution && selectedExecution.status === 'in_progress' && (
                <Button variant="success">Continuar Checklist</Button>
              )}
              {selectedTemplate && (
                <Button variant="primary">Editar Template</Button>
              )}
            </>
          }
        >
          {selectedExecution && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className="p-3 rounded-lg bg-bg-primary">
                  <ClipboardList className="w-6 h-6 text-text-muted" />
                </div>
                <div className="flex-1">
                  <p className="text-lg font-medium text-text-primary">{selectedExecution.templateName}</p>
                  <p className="text-sm text-text-muted">{selectedExecution.serviceOrderId}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={statusConfig[selectedExecution.status].color}>
                      {statusConfig[selectedExecution.status].label}
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Cliente</p>
                  <p className="font-medium text-text-primary">{selectedExecution.client}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Executor</p>
                  <p className="font-medium text-text-primary">{selectedExecution.executor}</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-2">Progresso</p>
                <div className="flex justify-between text-sm mb-2">
                  <span>{selectedExecution.completedItems}/{selectedExecution.totalItems} itens</span>
                  <span>{Math.round((selectedExecution.completedItems / selectedExecution.totalItems) * 100)}%</span>
                </div>
                <div className="h-3 bg-bg-primary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent-primary rounded-full transition-all"
                    style={{ width: `${(selectedExecution.completedItems / selectedExecution.totalItems) * 100}%` }}
                  />
                </div>
              </div>

              {selectedExecution.score !== null && (
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-sm text-text-muted mb-2">Score Final</p>
                  <p className={`text-4xl font-bold ${
                    selectedExecution.score >= 90 ? 'text-accent-success' :
                    selectedExecution.score >= 70 ? 'text-accent-warning' : 'text-accent-danger'
                  }`}>{selectedExecution.score}%</p>
                </div>
              )}

              {selectedExecution.notes && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Observações</p>
                  <p className="text-text-primary">{selectedExecution.notes}</p>
                </div>
              )}
            </div>
          )}

          {selectedTemplate && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className="p-3 rounded-lg bg-bg-primary">
                  <ClipboardList className="w-6 h-6 text-text-muted" />
                </div>
                <div className="flex-1">
                  <p className="text-lg font-medium text-text-primary">{selectedTemplate.name}</p>
                  <p className="text-sm text-text-muted">{selectedTemplate.description}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={categoryConfig[selectedTemplate.category].color}>
                      {categoryConfig[selectedTemplate.category].label}
                    </Badge>
                    <Badge variant={selectedTemplate.isActive ? 'success' : 'neutral'}>
                      {selectedTemplate.isActive ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedTemplate.itemsCount}</p>
                  <p className="text-sm text-text-muted">Itens</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedTemplate.usageCount}</p>
                  <p className="text-sm text-text-muted">Execuções</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedTemplate.createdAt}</p>
                  <p className="text-sm text-text-muted">Criado em</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-1">Criado por</p>
                <p className="font-medium text-text-primary">{selectedTemplate.createdBy}</p>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
