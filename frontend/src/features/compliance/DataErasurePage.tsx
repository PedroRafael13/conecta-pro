'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Trash2,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  User,
  FileText,
  Database,
  Calendar,
  Mail,
  Plus,
  Eye,
  Download,
  MoreHorizontal,
  RefreshCw,
  XCircle,
  History,
  Lock,
  Unlock,
  AlertCircle,
  Send,
  Filter,
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
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Types
interface ErasureRequest {
  id: string;
  protocol: string;
  requester: string;
  requesterEmail: string;
  requestType: 'full' | 'partial' | 'anonymization';
  status: 'pending' | 'in_progress' | 'completed' | 'rejected' | 'blocked';
  createdAt: string;
  deadline: string;
  completedAt: string | null;
  affectedSystems: string[];
  dataCategories: string[];
  rejectionReason: string | null;
  assignedTo: string | null;
}

// Mock Data
const erasureRequests: ErasureRequest[] = [
  {
    id: '1',
    protocol: 'LGPD-2026-0015',
    requester: 'João Silva',
    requesterEmail: 'joao.silva@email.com',
    requestType: 'full',
    status: 'pending',
    createdAt: '2026-01-15T10:00:00',
    deadline: '2026-01-30',
    completedAt: null,
    affectedSystems: ['CRM', 'ERP', 'GED'],
    dataCategories: ['Dados Pessoais', 'Dados Financeiros', 'Histórico de Compras'],
    rejectionReason: null,
    assignedTo: 'Ana Costa',
  },
  {
    id: '2',
    protocol: 'LGPD-2026-0014',
    requester: 'Maria Santos',
    requesterEmail: 'maria.santos@empresa.com',
    requestType: 'partial',
    status: 'in_progress',
    createdAt: '2026-01-12T14:00:00',
    deadline: '2026-01-27',
    completedAt: null,
    affectedSystems: ['CRM', 'Marketing'],
    dataCategories: ['Dados de Marketing', 'Cookies'],
    rejectionReason: null,
    assignedTo: 'Carlos Lima',
  },
  {
    id: '3',
    protocol: 'LGPD-2026-0013',
    requester: 'Pedro Oliveira',
    requesterEmail: 'pedro@fornecedor.com',
    requestType: 'full',
    status: 'completed',
    createdAt: '2026-01-08T09:00:00',
    deadline: '2026-01-23',
    completedAt: '2026-01-14T16:30:00',
    affectedSystems: ['CRM', 'ERP'],
    dataCategories: ['Dados Pessoais', 'Dados Contratuais'],
    rejectionReason: null,
    assignedTo: 'Roberto Silva',
  },
  {
    id: '4',
    protocol: 'LGPD-2026-0012',
    requester: 'Empresa XYZ',
    requesterEmail: 'juridico@xyz.com',
    requestType: 'anonymization',
    status: 'completed',
    createdAt: '2026-01-05T11:00:00',
    deadline: '2026-01-20',
    completedAt: '2026-01-12T10:00:00',
    affectedSystems: ['ERP', 'BI'],
    dataCategories: ['Dados Estatísticos'],
    rejectionReason: null,
    assignedTo: 'Maria Oliveira',
  },
  {
    id: '5',
    protocol: 'LGPD-2026-0011',
    requester: 'Cliente Antigo',
    requesterEmail: 'cliente@old.com',
    requestType: 'full',
    status: 'blocked',
    createdAt: '2026-01-03T15:00:00',
    deadline: '2026-01-18',
    completedAt: null,
    affectedSystems: ['ERP'],
    dataCategories: ['Dados Financeiros'],
    rejectionReason: 'Retenção legal obrigatória - Dados fiscais (5 anos)',
    assignedTo: null,
  },
  {
    id: '6',
    protocol: 'LGPD-2026-0010',
    requester: 'Ex-Funcionário',
    requesterEmail: 'ex@func.com',
    requestType: 'partial',
    status: 'rejected',
    createdAt: '2026-01-02T08:00:00',
    deadline: '2026-01-17',
    completedAt: null,
    affectedSystems: ['RH'],
    dataCategories: ['Dados Trabalhistas'],
    rejectionReason: 'Dados necessários para cumprimento de obrigação legal trabalhista',
    assignedTo: null,
  },
];

const requestTrend = [
  { month: 'Set', requests: 5, completed: 4 },
  { month: 'Out', requests: 8, completed: 7 },
  { month: 'Nov', requests: 12, completed: 10 },
  { month: 'Dez', requests: 15, completed: 13 },
  { month: 'Jan', requests: 10, completed: 6 },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'pending', label: 'Pendentes' },
  { id: 'in_progress', label: 'Em Andamento' },
  { id: 'completed', label: 'Concluídas' },
  { id: 'blocked', label: 'Bloqueadas' },
];

const statusColors = {
  pending: 'warning',
  in_progress: 'info',
  completed: 'success',
  rejected: 'danger',
  blocked: 'secondary',
} as const;

const statusLabels = {
  pending: 'Pendente',
  in_progress: 'Em Andamento',
  completed: 'Concluída',
  rejected: 'Rejeitada',
  blocked: 'Bloqueada',
};

const statusIcons = {
  pending: Clock,
  in_progress: RefreshCw,
  completed: CheckCircle2,
  rejected: XCircle,
  blocked: Lock,
};

const requestTypeLabels = {
  full: 'Exclusão Total',
  partial: 'Exclusão Parcial',
  anonymization: 'Anonimização',
};

const columns: Column<ErasureRequest>[] = [
  {
    key: 'protocol',
    header: 'Protocolo',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${
          row.status === 'completed' ? 'bg-success/10' :
          row.status === 'blocked' || row.status === 'rejected' ? 'bg-danger/10' :
          'bg-warning/10'
        }`}>
          <Trash2 className={`w-5 h-5 ${
            row.status === 'completed' ? 'text-success' :
            row.status === 'blocked' || row.status === 'rejected' ? 'text-danger' :
            'text-warning'
          }`} />
        </div>
        <div>
          <p className="font-medium text-text-primary font-mono">{row.protocol}</p>
          <p className="text-xs text-text-muted">{requestTypeLabels[row.requestType]}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'requester',
    header: 'Solicitante',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.requester} size="xs" />
        <div>
          <p className="text-sm font-medium">{row.requester}</p>
          <p className="text-xs text-text-muted">{row.requesterEmail}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const Icon = statusIcons[row.status];
      return (
        <Badge variant={statusColors[row.status]}>
          <Icon className="w-3 h-3 mr-1" />
          {statusLabels[row.status]}
        </Badge>
      );
    },
  },
  {
    key: 'affectedSystems',
    header: 'Sistemas',
    render: (row) => (
      <div className="flex flex-wrap gap-1">
        {row.affectedSystems.slice(0, 2).map((sys) => (
          <Badge key={sys} variant="neutral" size="sm">{sys}</Badge>
        ))}
        {row.affectedSystems.length > 2 && (
          <Badge variant="neutral" size="sm">+{row.affectedSystems.length - 2}</Badge>
        )}
      </div>
    ),
  },
  {
    key: 'deadline',
    header: 'Prazo',
    render: (row) => {
      const deadline = new Date(row.deadline);
      const isOverdue = deadline < new Date() && row.status !== 'completed';
      return (
        <div className={`flex items-center gap-2 ${isOverdue ? 'text-danger' : 'text-text-secondary'}`}>
          <Calendar className="w-4 h-4" />
          <span className="text-sm">{deadline.toLocaleDateString('pt-BR')}</span>
        </div>
      );
    },
  },
  {
    key: 'assignedTo',
    header: 'Responsável',
    render: (row) => (
      row.assignedTo ? (
        <div className="flex items-center gap-2">
          <Avatar name={row.assignedTo} size="xs" />
          <span className="text-sm">{row.assignedTo}</span>
        </div>
      ) : (
        <span className="text-sm text-text-muted">-</span>
      )
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'pending' && (
          <Button variant="ghost" size="icon-sm" title="Iniciar">
            <RefreshCw className="w-4 h-4" />
          </Button>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function DataErasurePage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isNewRequestModalOpen, setIsNewRequestModalOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<ErasureRequest | null>(null);

  const filteredRequests = erasureRequests.filter((request) => {
    const matchesSearch =
      request.protocol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.requester.toLowerCase().includes(searchTerm.toLowerCase());

    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && request.status === activeTab;
  });

  // Stats
  const totalRequests = erasureRequests.length;
  const pendingRequests = erasureRequests.filter(r => r.status === 'pending' || r.status === 'in_progress').length;
  const completedRequests = erasureRequests.filter(r => r.status === 'completed').length;
  const overdueRequests = erasureRequests.filter(r => {
    const deadline = new Date(r.deadline);
    return deadline < new Date() && r.status !== 'completed';
  }).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Exclusão de Dados (LGPD)
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie solicitações de exclusão e direito ao esquecimento
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar Relatório
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsNewRequestModalOpen(true)}
            >
              Nova Solicitação
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
              title="Total de Solicitações"
              value={totalRequests}
              icon={<Trash2 className="w-6 h-6" />}
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
              value={pendingRequests}
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
              title="Concluídas"
              value={completedRequests}
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
              title="Atrasadas"
              value={overdueRequests}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Trend Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">Tendência de Solicitações</h3>
            </div>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={requestTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                  <YAxis stroke="var(--color-text-muted)" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--color-bg-secondary)',
                      border: '1px solid var(--color-border)',
                      borderRadius: '8px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="requests"
                    stroke="#F59E0B"
                    strokeWidth={2}
                    name="Solicitações"
                  />
                  <Line
                    type="monotone"
                    dataKey="completed"
                    stroke="#10B981"
                    strokeWidth={2}
                    name="Concluídas"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Overdue Alert */}
        {overdueRequests > 0 && (
          <Card className="border-l-4 border-l-danger">
            <CardBody className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-danger/10">
                    <AlertTriangle className="w-5 h-5 text-danger" />
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">Solicitações Atrasadas</p>
                    <p className="text-sm text-text-muted">
                      {overdueRequests} solicitações ultrapassaram o prazo legal de 15 dias
                    </p>
                  </div>
                </div>
                <Button variant="danger" size="sm">Ver Atrasadas</Button>
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
              placeholder="Buscar solicitações..."
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

        {/* Requests Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredRequests}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedRequest(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Request Modal */}
        <Modal
          isOpen={isNewRequestModalOpen}
          onClose={() => setIsNewRequestModalOpen(false)}
          title="Nova Solicitação de Exclusão"
          description="Registre uma nova solicitação de exclusão de dados"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsNewRequestModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
                Registrar Solicitação
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Nome do Solicitante" placeholder="Nome completo" required />
              <Input label="E-mail" type="email" placeholder="email@exemplo.com" required />
            </div>

            <Select
              label="Tipo de Solicitação"
              options={[
                { value: 'full', label: 'Exclusão Total - Todos os dados pessoais' },
                { value: 'partial', label: 'Exclusão Parcial - Dados específicos' },
                { value: 'anonymization', label: 'Anonimização - Manter dados estatísticos' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Categorias de Dados</label>
              <div className="grid grid-cols-2 gap-2">
                {['Dados Pessoais', 'Dados Financeiros', 'Dados de Marketing', 'Histórico de Compras', 'Dados Contratuais', 'Cookies e Tracking'].map((category) => (
                  <label key={category} className="flex items-center gap-2 p-2 rounded border border-border hover:bg-bg-secondary cursor-pointer">
                    <input type="checkbox" className="rounded" />
                    <span className="text-sm">{category}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Sistemas Afetados</label>
              <div className="grid grid-cols-3 gap-2">
                {['CRM', 'ERP', 'GED', 'RH', 'Marketing', 'BI'].map((system) => (
                  <label key={system} className="flex items-center gap-2 p-2 rounded border border-border hover:bg-bg-secondary cursor-pointer">
                    <input type="checkbox" className="rounded" />
                    <span className="text-sm">{system}</span>
                  </label>
                ))}
              </div>
            </div>

            <Textarea
              label="Justificativa/Observações"
              placeholder="Motivo da solicitação ou observações relevantes"
              rows={3}
            />

            <div className="p-3 rounded-lg bg-warning/10 border border-warning/20">
              <div className="flex items-center gap-2 mb-1">
                <AlertCircle className="w-4 h-4 text-warning" />
                <span className="text-sm font-medium text-warning">Prazo Legal</span>
              </div>
              <p className="text-sm text-text-secondary">
                A LGPD estabelece prazo máximo de 15 dias para resposta às solicitações de exclusão.
              </p>
            </div>
          </div>
        </Modal>

        {/* Request Detail Modal */}
        <Modal
          isOpen={!!selectedRequest}
          onClose={() => setSelectedRequest(null)}
          title="Detalhes da Solicitação"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedRequest(null)}>
                Fechar
              </Button>
              {selectedRequest?.status === 'pending' && (
                <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />}>
                  Iniciar Processamento
                </Button>
              )}
              {selectedRequest?.status === 'in_progress' && (
                <Button variant="success" leftIcon={<CheckCircle2 className="w-4 h-4" />}>
                  Marcar como Concluída
                </Button>
              )}
            </>
          }
        >
          {selectedRequest && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center gap-4 p-4 rounded-lg bg-bg-secondary">
                <div className={`p-3 rounded-lg ${
                  selectedRequest.status === 'completed' ? 'bg-success/10' :
                  selectedRequest.status === 'blocked' || selectedRequest.status === 'rejected' ? 'bg-danger/10' :
                  'bg-warning/10'
                }`}>
                  <Trash2 className={`w-6 h-6 ${
                    selectedRequest.status === 'completed' ? 'text-success' :
                    selectedRequest.status === 'blocked' || selectedRequest.status === 'rejected' ? 'text-danger' :
                    'text-warning'
                  }`} />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-text-primary font-mono">{selectedRequest.protocol}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant={statusColors[selectedRequest.status]}>
                      {statusLabels[selectedRequest.status]}
                    </Badge>
                    <Badge variant="neutral">{requestTypeLabels[selectedRequest.requestType]}</Badge>
                  </div>
                </div>
              </div>

              {/* Rejection Reason */}
              {selectedRequest.rejectionReason && (
                <div className="p-4 rounded-lg bg-danger/10 border border-danger/20">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-5 h-5 text-danger" />
                    <span className="font-medium text-danger">Motivo da Rejeição/Bloqueio</span>
                  </div>
                  <p className="text-text-secondary">{selectedRequest.rejectionReason}</p>
                </div>
              )}

              {/* Requester Info */}
              <div className="flex items-center gap-4 p-4 rounded-lg border border-border">
                <Avatar name={selectedRequest.requester} size="lg" />
                <div>
                  <p className="font-medium text-text-primary">{selectedRequest.requester}</p>
                  <p className="text-sm text-text-muted">{selectedRequest.requesterEmail}</p>
                </div>
              </div>

              {/* Data Categories */}
              <div>
                <h5 className="font-medium text-text-primary mb-3">Categorias de Dados</h5>
                <div className="flex flex-wrap gap-2">
                  {selectedRequest.dataCategories.map((cat) => (
                    <Badge key={cat} variant="secondary">{cat}</Badge>
                  ))}
                </div>
              </div>

              {/* Affected Systems */}
              <div>
                <h5 className="font-medium text-text-primary mb-3">Sistemas Afetados</h5>
                <div className="flex flex-wrap gap-2">
                  {selectedRequest.affectedSystems.map((sys) => (
                    <Badge key={sys} variant="info">{sys}</Badge>
                  ))}
                </div>
              </div>

              {/* Timeline */}
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Data da Solicitação</p>
                  <p className="font-medium">{new Date(selectedRequest.createdAt).toLocaleString('pt-BR')}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Prazo</p>
                  <p className="font-medium">{new Date(selectedRequest.deadline).toLocaleDateString('pt-BR')}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Conclusão</p>
                  <p className="font-medium">
                    {selectedRequest.completedAt
                      ? new Date(selectedRequest.completedAt).toLocaleString('pt-BR')
                      : '-'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
