'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Download,
  Plus,
  Eye,
  Edit2,
  CheckCircle2,
  XCircle,
  Clock,
  User,
  Users,
  FileText,
  Shield,
  AlertTriangle,
  Mail,
  Calendar,
  RefreshCw,
  Settings,
  MoreHorizontal,
  History,
  Bell,
  Send,
  Trash2,
  Check,
  X,
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
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

// Types
interface Consent {
  id: string;
  subject: string;
  email: string;
  type: 'employee' | 'client' | 'supplier' | 'visitor';
  purposes: Purpose[];
  consentDate: string;
  expirationDate: string | null;
  status: 'active' | 'expired' | 'revoked' | 'pending';
  source: 'web' | 'app' | 'paper' | 'email';
  version: string;
  ipAddress: string;
}

interface Purpose {
  id: string;
  name: string;
  description: string;
  status: 'granted' | 'denied' | 'pending';
  legalBasis: string;
}

// Mock Data
const consents: Consent[] = [
  {
    id: '1',
    subject: 'Roberto Silva',
    email: 'roberto.silva@email.com',
    type: 'employee',
    purposes: [
      { id: 'p1', name: 'Dados Pessoais', description: 'Processamento de dados básicos', status: 'granted', legalBasis: 'Contrato' },
      { id: 'p2', name: 'Marketing', description: 'Envio de comunicações', status: 'granted', legalBasis: 'Consentimento' },
      { id: 'p3', name: 'Analytics', description: 'Análise de comportamento', status: 'denied', legalBasis: 'Consentimento' },
    ],
    consentDate: '2025-06-15T10:30:00',
    expirationDate: '2026-06-15',
    status: 'active',
    source: 'web',
    version: '2.0',
    ipAddress: '192.168.1.100',
  },
  {
    id: '2',
    subject: 'Ana Costa',
    email: 'ana.costa@empresa.com',
    type: 'client',
    purposes: [
      { id: 'p1', name: 'Dados Pessoais', description: 'Processamento de dados básicos', status: 'granted', legalBasis: 'Contrato' },
      { id: 'p2', name: 'Marketing', description: 'Envio de comunicações', status: 'granted', legalBasis: 'Consentimento' },
    ],
    consentDate: '2025-08-20T14:00:00',
    expirationDate: '2026-08-20',
    status: 'active',
    source: 'app',
    version: '2.0',
    ipAddress: '10.0.0.50',
  },
  {
    id: '3',
    subject: 'Carlos Lima',
    email: 'carlos.lima@fornecedor.com',
    type: 'supplier',
    purposes: [
      { id: 'p1', name: 'Dados Pessoais', description: 'Processamento de dados básicos', status: 'granted', legalBasis: 'Contrato' },
    ],
    consentDate: '2024-12-01T09:00:00',
    expirationDate: '2025-12-01',
    status: 'expired',
    source: 'paper',
    version: '1.5',
    ipAddress: '-',
  },
  {
    id: '4',
    subject: 'Maria Oliveira',
    email: 'maria@cliente.com',
    type: 'client',
    purposes: [
      { id: 'p1', name: 'Dados Pessoais', description: 'Processamento de dados básicos', status: 'pending', legalBasis: 'Consentimento' },
    ],
    consentDate: '',
    expirationDate: null,
    status: 'pending',
    source: 'email',
    version: '2.0',
    ipAddress: '-',
  },
  {
    id: '5',
    subject: 'Pedro Santos',
    email: 'pedro@empresa.com',
    type: 'employee',
    purposes: [
      { id: 'p1', name: 'Dados Pessoais', description: 'Processamento de dados básicos', status: 'granted', legalBasis: 'Contrato' },
      { id: 'p2', name: 'Marketing', description: 'Envio de comunicações', status: 'denied', legalBasis: 'Consentimento' },
    ],
    consentDate: '2025-03-10T11:00:00',
    expirationDate: null,
    status: 'revoked',
    source: 'web',
    version: '1.8',
    ipAddress: '192.168.1.105',
  },
];

const consentDistribution = [
  { name: 'Ativos', value: 156, color: '#10B981' },
  { name: 'Expirados', value: 23, color: '#6B7280' },
  { name: 'Revogados', value: 12, color: '#EF4444' },
  { name: 'Pendentes', value: 8, color: '#F59E0B' },
];

const consentTrend = [
  { month: 'Set', granted: 45, revoked: 3 },
  { month: 'Out', granted: 52, revoked: 5 },
  { month: 'Nov', granted: 68, revoked: 4 },
  { month: 'Dez', granted: 72, revoked: 2 },
  { month: 'Jan', granted: 58, revoked: 3 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'active', label: 'Ativos' },
  { id: 'pending', label: 'Pendentes' },
  { id: 'expired', label: 'Expirados' },
  { id: 'revoked', label: 'Revogados' },
];

const statusColors = {
  active: 'success',
  expired: 'secondary',
  revoked: 'danger',
  pending: 'warning',
} as const;

const statusLabels = {
  active: 'Ativo',
  expired: 'Expirado',
  revoked: 'Revogado',
  pending: 'Pendente',
};

const typeLabels = {
  employee: 'Funcionário',
  client: 'Cliente',
  supplier: 'Fornecedor',
  visitor: 'Visitante',
};

const columns: Column<Consent>[] = [
  {
    key: 'subject',
    header: 'Titular',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.subject} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.subject}</p>
          <p className="text-xs text-text-muted">{row.email}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => <Badge variant="neutral">{typeLabels[row.type]}</Badge>,
  },
  {
    key: 'purposes',
    header: 'Finalidades',
    render: (row) => {
      const granted = row.purposes.filter(p => p.status === 'granted').length;
      const total = row.purposes.length;
      return (
        <div className="flex items-center gap-2">
          <span className="text-sm">{granted}/{total}</span>
          <div className="w-20 h-2 bg-bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-success rounded-full"
              style={{ width: `${(granted / total) * 100}%` }}
            />
          </div>
        </div>
      );
    },
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
    key: 'consentDate',
    header: 'Data do Consentimento',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {row.consentDate ? new Date(row.consentDate).toLocaleDateString('pt-BR') : '-'}
      </span>
    ),
  },
  {
    key: 'expirationDate',
    header: 'Expiração',
    render: (row) => {
      if (!row.expirationDate) return <span className="text-sm text-text-muted">-</span>;
      const isExpiring = new Date(row.expirationDate) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
      return (
        <span className={`text-sm ${isExpiring ? 'text-warning' : 'text-text-secondary'}`}>
          {new Date(row.expirationDate).toLocaleDateString('pt-BR')}
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
        {row.status === 'pending' && (
          <Button variant="ghost" size="icon-sm" title="Reenviar">
            <Send className="w-4 h-4" />
          </Button>
        )}
        <Button variant="ghost" size="icon-sm" title="Histórico">
          <History className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const COLORS = ['#10B981', '#6B7280', '#EF4444', '#F59E0B'];

export function ConsentManagementPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isRequestModalOpen, setIsRequestModalOpen] = useState(false);
  const [selectedConsent, setSelectedConsent] = useState<Consent | null>(null);
  const [newSubjectType, setNewSubjectType] = useState('');

  const filteredConsents = consents.filter((consent) => {
    const matchesSearch =
      consent.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      consent.email.toLowerCase().includes(searchTerm.toLowerCase());

    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && consent.status === activeTab;
  });

  // Stats
  const totalConsents = consents.length;
  const activeConsents = consents.filter(c => c.status === 'active').length;
  const pendingConsents = consents.filter(c => c.status === 'pending').length;
  const expiringConsents = consents.filter(c => {
    if (!c.expirationDate) return false;
    return new Date(c.expirationDate) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
  }).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Consentimentos
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie os consentimentos LGPD dos titulares de dados
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsRequestModalOpen(true)}
            >
              Solicitar Consentimento
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
              title="Total de Registros"
              value={totalConsents}
              icon={<Users className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Consentimentos Ativos"
              value={activeConsents}
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
              title="Aguardando Resposta"
              value={pendingConsents}
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
              title="Expirando em 30 dias"
              value={expiringConsents}
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
                <Shield className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Distribuição de Consentimentos</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={consentDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {consentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-6 mt-4">
                {consentDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-text-muted">{item.name}: {item.value}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Tendência de Consentimentos</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={consentTrend}>
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
                    <Area
                      type="monotone"
                      dataKey="granted"
                      stackId="1"
                      stroke="#10B981"
                      fill="#10B981"
                      fillOpacity={0.3}
                      name="Concedidos"
                    />
                    <Area
                      type="monotone"
                      dataKey="revoked"
                      stackId="2"
                      stroke="#EF4444"
                      fill="#EF4444"
                      fillOpacity={0.3}
                      name="Revogados"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Expiration Alert */}
        {expiringConsents > 0 && (
          <Card className="border-l-4 border-l-warning">
            <CardBody className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-warning/10">
                    <Bell className="w-5 h-5 text-warning" />
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">Consentimentos Expirando</p>
                    <p className="text-sm text-text-muted">
                      {expiringConsents} consentimentos expiram nos próximos 30 dias
                    </p>
                  </div>
                </div>
                <Button variant="warning" size="sm" leftIcon={<RefreshCw className="w-4 h-4" />}>
                  Renovar Todos
                </Button>
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
              placeholder="Buscar titular..."
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

        {/* Consents Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredConsents}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedConsent(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Request Consent Modal */}
        <Modal
          isOpen={isRequestModalOpen}
          onClose={() => setIsRequestModalOpen(false)}
          title="Solicitar Consentimento"
          description="Envie uma solicitação de consentimento para um titular"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsRequestModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                Enviar Solicitação
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Nome do Titular" placeholder="Nome completo" required />
              <Input label="E-mail" type="email" placeholder="email@exemplo.com" required />
            </div>

            <Select
              label="Tipo de Titular"
              options={[
                { value: 'employee', label: 'Funcionário' },
                { value: 'client', label: 'Cliente' },
                { value: 'supplier', label: 'Fornecedor' },
                { value: 'visitor', label: 'Visitante' },
              ]}
              value={newSubjectType}
              onChange={(value) => setNewSubjectType(value)}
              placeholder="Selecione..."
            />

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Finalidades</label>
              <div className="space-y-2">
                {['Dados Pessoais', 'Marketing', 'Analytics', 'Compartilhamento com Terceiros'].map((purpose) => (
                  <label key={purpose} className="flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-bg-secondary cursor-pointer">
                    <input type="checkbox" className="rounded" />
                    <span className="flex-1">{purpose}</span>
                  </label>
                ))}
              </div>
            </div>

            <Textarea
              label="Mensagem Personalizada (opcional)"
              placeholder="Adicione uma mensagem personalizada..."
              rows={3}
            />

            <div className="p-3 rounded-lg bg-info/10 border border-info/20">
              <div className="flex items-center gap-2 mb-1">
                <Mail className="w-4 h-4 text-info" />
                <span className="text-sm font-medium text-info">Notificação</span>
              </div>
              <p className="text-sm text-text-secondary">
                O titular receberá um e-mail com link para aceitar ou recusar os consentimentos solicitados.
              </p>
            </div>
          </div>
        </Modal>

        {/* Consent Detail Modal */}
        <Modal
          isOpen={!!selectedConsent}
          onClose={() => setSelectedConsent(null)}
          title="Detalhes do Consentimento"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedConsent(null)}>
                Fechar
              </Button>
              {selectedConsent?.status === 'active' && (
                <Button variant="danger" leftIcon={<XCircle className="w-4 h-4" />}>
                  Revogar
                </Button>
              )}
            </>
          }
        >
          {selectedConsent && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center gap-4 p-4 rounded-lg bg-bg-secondary">
                <Avatar name={selectedConsent.subject} size="lg" />
                <div className="flex-1">
                  <h4 className="font-medium text-text-primary">{selectedConsent.subject}</h4>
                  <p className="text-sm text-text-muted">{selectedConsent.email}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={statusColors[selectedConsent.status]}>
                      {statusLabels[selectedConsent.status]}
                    </Badge>
                    <Badge variant="neutral">{typeLabels[selectedConsent.type]}</Badge>
                  </div>
                </div>
              </div>

              {/* Purposes */}
              <div>
                <h5 className="font-medium text-text-primary mb-3">Finalidades</h5>
                <div className="space-y-2">
                  {selectedConsent.purposes.map((purpose) => (
                    <div
                      key={purpose.id}
                      className={`flex items-center justify-between p-3 rounded-lg border ${
                        purpose.status === 'granted' ? 'border-success/30 bg-success/5' :
                        purpose.status === 'denied' ? 'border-danger/30 bg-danger/5' :
                        'border-warning/30 bg-warning/5'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        {purpose.status === 'granted' ? (
                          <Check className="w-5 h-5 text-success" />
                        ) : purpose.status === 'denied' ? (
                          <X className="w-5 h-5 text-danger" />
                        ) : (
                          <Clock className="w-5 h-5 text-warning" />
                        )}
                        <div>
                          <p className="font-medium text-text-primary">{purpose.name}</p>
                          <p className="text-sm text-text-muted">{purpose.description}</p>
                        </div>
                      </div>
                      <Badge variant="neutral" size="sm">{purpose.legalBasis}</Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Info */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Data do Consentimento</p>
                  <p className="font-medium">
                    {selectedConsent.consentDate
                      ? new Date(selectedConsent.consentDate).toLocaleString('pt-BR')
                      : '-'}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Data de Expiração</p>
                  <p className="font-medium">
                    {selectedConsent.expirationDate
                      ? new Date(selectedConsent.expirationDate).toLocaleDateString('pt-BR')
                      : 'Sem expiração'}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Origem</p>
                  <p className="font-medium capitalize">{selectedConsent.source}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Versão do Termo</p>
                  <p className="font-medium">v{selectedConsent.version}</p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
