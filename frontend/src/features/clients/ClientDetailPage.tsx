'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Phone,
  Mail,
  User,
  Calendar,
  FileText,
  DollarSign,
  Shield,
  Clock,
  Edit,
  Trash2,
  Plus,
  Eye,
  Download,
  CheckCircle2,
  AlertTriangle,
  MessageSquare,
  Wrench,
  TrendingUp,
  Activity,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Types
interface Contract {
  id: string;
  name: string;
  type: 'vigilancia' | 'cftv' | 'controle_acesso' | 'portaria' | 'monitoramento';
  value: number;
  startDate: string;
  endDate: string;
  status: 'active' | 'expiring' | 'expired' | 'cancelled';
}

interface ServiceOrder {
  id: string;
  number: string;
  type: string;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  createdAt: string;
  scheduledFor: string | null;
}

interface Interaction {
  id: string;
  type: 'call' | 'email' | 'meeting' | 'visit' | 'support';
  subject: string;
  description: string;
  createdAt: string;
  createdBy: string;
}

// Mock Data
const client = {
  id: '1',
  name: 'Shopping Center Norte',
  tradeName: 'Shopping Center Norte',
  document: '12.345.678/0001-90',
  status: 'active' as const,
  segment: 'comercial',
  address: {
    street: 'Av. Cruzeiro do Sul',
    number: '1100',
    complement: '',
    neighborhood: 'Santana',
    city: 'São Paulo',
    state: 'SP',
    zipCode: '02031-000',
  },
  contacts: [
    { id: '1', name: 'João Silva', email: 'joao@scn.com.br', phone: '(11) 99999-1234', role: 'Gerente Operacional', isPrimary: true },
    { id: '2', name: 'Maria Santos', email: 'maria@scn.com.br', phone: '(11) 99888-5678', role: 'Coord. Segurança', isPrimary: false },
  ],
  healthScore: 92,
  createdAt: '2023-06-15',
  mrr: 150000,
  totalRevenue: 2700000,
};

const contracts: Contract[] = [
  { id: '1', name: 'Vigilância Patrimonial 24h', type: 'vigilancia', value: 85000, startDate: '2024-01-01', endDate: '2026-12-31', status: 'active' },
  { id: '2', name: 'Monitoramento CFTV', type: 'cftv', value: 35000, startDate: '2024-01-01', endDate: '2026-12-31', status: 'active' },
  { id: '3', name: 'Controle de Acesso', type: 'controle_acesso', value: 20000, startDate: '2024-06-01', endDate: '2025-05-31', status: 'expiring' },
  { id: '4', name: 'Portaria Eletrônica', type: 'portaria', value: 10000, startDate: '2025-01-01', endDate: '2027-12-31', status: 'active' },
];

const serviceOrders: ServiceOrder[] = [
  { id: '1', number: 'OS-2026-0142', type: 'Manutenção Preventiva', status: 'completed', createdAt: '2026-01-10', scheduledFor: '2026-01-15' },
  { id: '2', number: 'OS-2026-0128', type: 'Instalação Câmera', status: 'in_progress', createdAt: '2026-01-08', scheduledFor: '2026-01-16' },
  { id: '3', number: 'OS-2026-0115', type: 'Chamado Técnico', status: 'completed', createdAt: '2026-01-05', scheduledFor: '2026-01-06' },
];

const interactions: Interaction[] = [
  { id: '1', type: 'meeting', subject: 'Reunião de acompanhamento mensal', description: 'Discutido ampliação do contrato de CFTV', createdAt: '2026-01-15', createdBy: 'Ana Paula' },
  { id: '2', type: 'email', subject: 'Envio de relatório mensal', description: 'Relatório de ocorrências de dezembro/2025', createdAt: '2026-01-10', createdBy: 'Sistema' },
  { id: '3', type: 'call', subject: 'Solicitação de visita técnica', description: 'Cliente solicitou verificação de câmeras do bloco B', createdAt: '2026-01-08', createdBy: 'Carlos Eduardo' },
];

const revenueData = [
  { month: 'Ago', value: 145000 },
  { month: 'Set', value: 148000 },
  { month: 'Out', value: 150000 },
  { month: 'Nov', value: 150000 },
  { month: 'Dez', value: 150000 },
  { month: 'Jan', value: 150000 },
];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const contractColumns: Column<Contract>[] = [
  {
    key: 'name',
    header: 'Contrato',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.name}</p>
        <p className="text-xs text-text-muted capitalize">{row.type.replace('_', ' ')}</p>
      </div>
    ),
  },
  {
    key: 'value',
    header: 'Valor Mensal',
    render: (row) => <span className="font-medium">{formatCurrency(row.value)}</span>,
  },
  {
    key: 'period',
    header: 'Vigência',
    render: (row) => (
      <div>
        <p className="text-sm">{row.startDate} a {row.endDate}</p>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const colors = {
        active: 'success' as const,
        expiring: 'warning' as const,
        expired: 'danger' as const,
        cancelled: 'danger' as const,
      };
      const labels = {
        active: 'Ativo',
        expiring: 'Vencendo',
        expired: 'Vencido',
        cancelled: 'Cancelado',
      };
      return <Badge variant={colors[row.status]}>{labels[row.status]}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <Button variant="ghost" size="icon-sm">
        <Eye className="w-4 h-4" />
      </Button>
    ),
  },
];

const osColumns: Column<ServiceOrder>[] = [
  {
    key: 'number',
    header: 'Número',
    render: (row) => <span className="font-mono text-sm font-medium text-accent-primary">{row.number}</span>,
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => <span className="text-sm">{row.type}</span>,
  },
  {
    key: 'scheduledFor',
    header: 'Agendamento',
    render: (row) => <span className="text-sm">{row.scheduledFor || '-'}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const colors = {
        pending: 'warning' as const,
        scheduled: 'info' as const,
        in_progress: 'primary' as const,
        completed: 'success' as const,
        cancelled: 'danger' as const,
      };
      const labels = {
        pending: 'Pendente',
        scheduled: 'Agendada',
        in_progress: 'Em Andamento',
        completed: 'Concluída',
        cancelled: 'Cancelada',
      };
      return <Badge variant={colors[row.status]}>{labels[row.status]}</Badge>;
    },
  },
];

export function ClientDetailPage() {
  const [selectedTab, setSelectedTab] = useState('overview');

  const healthColor = client.healthScore >= 80 ? 'text-accent-success' : client.healthScore >= 60 ? 'text-accent-warning' : 'text-accent-danger';

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon-sm">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-bg-tertiary rounded-xl">
                <Building2 className="w-8 h-8 text-accent-primary" />
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-display font-bold text-text-primary">
                    {client.name}
                  </h1>
                  <Badge variant="success">Ativo</Badge>
                </div>
                <p className="text-text-muted">{client.document}</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<MessageSquare className="w-4 h-4" />}>
              Registrar Interação
            </Button>
            <Button variant="primary" leftIcon={<Edit className="w-4 h-4" />}>
              Editar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Receita Mensal"
              value={formatCurrency(client.mrr)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Receita Total"
              value={formatCurrency(client.totalRevenue)}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Contratos Ativos"
              value={contracts.filter(c => c.status === 'active').length}
              icon={<FileText className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Score de Saúde"
              value={`${client.healthScore}%`}
              icon={<Shield className="w-6 h-6" />}
              iconColor={client.healthScore >= 80 ? 'success' : 'warning'}
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <SimpleTabBar
          tabs={[
            { value: 'overview', label: 'Visão Geral' },
            { value: 'contracts', label: 'Contratos' },
            { value: 'services', label: 'Serviços' },
            { value: 'interactions', label: 'Interações' },
            { value: 'documents', label: 'Documentos' },
          ]}
          value={selectedTab}
          onChange={setSelectedTab}
          variant="pills"
        />

        {/* Content */}
        {selectedTab === 'overview' && (
          <div className="grid grid-cols-3 gap-6">
            <div className="col-span-2 space-y-6">
              {/* Revenue Chart */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
                <Card>
                  <CardHeader title="Evolução da Receita" subtitle="Últimos 6 meses" />
                  <CardBody>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={revenueData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                          <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                          <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `R$${v/1000}k`} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#12121a',
                              border: '1px solid #2d2d3d',
                              borderRadius: '8px',
                            }}
                            formatter={(value: number) => formatCurrency(value)}
                          />
                          <Area
                            type="monotone"
                            dataKey="value"
                            stroke="#6366f1"
                            fill="#6366f1"
                            fillOpacity={0.2}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </CardBody>
                </Card>
              </motion.div>

              {/* Recent Service Orders */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
                <Card>
                  <CardHeader
                    title="Ordens de Serviço Recentes"
                    action={<Button variant="outline" size="sm">Ver Todas</Button>}
                  />
                  <CardBody className="p-0">
                    <DataTable
                      columns={osColumns}
                      data={serviceOrders}
                      keyExtractor={(row) => row.id}
                    />
                  </CardBody>
                </Card>
              </motion.div>
            </div>

            <div className="space-y-6">
              {/* Client Info */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
                <Card>
                  <CardHeader title="Informações" />
                  <CardBody className="space-y-4">
                    <div>
                      <p className="text-xs text-text-muted uppercase mb-1">Endereço</p>
                      <div className="flex items-start gap-2">
                        <MapPin className="w-4 h-4 text-text-muted mt-0.5" />
                        <p className="text-sm text-text-primary">
                          {client.address.street}, {client.address.number}
                          <br />
                          {client.address.neighborhood} - {client.address.city}/{client.address.state}
                          <br />
                          CEP: {client.address.zipCode}
                        </p>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-text-muted uppercase mb-1">Segmento</p>
                      <Badge variant="info">Comercial</Badge>
                    </div>
                    <div>
                      <p className="text-xs text-text-muted uppercase mb-1">Cliente desde</p>
                      <p className="text-sm text-text-primary">{client.createdAt}</p>
                    </div>
                  </CardBody>
                </Card>
              </motion.div>

              {/* Contacts */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
                <Card>
                  <CardHeader
                    title="Contatos"
                    action={<Button variant="ghost" size="icon-sm"><Plus className="w-4 h-4" /></Button>}
                  />
                  <CardBody className="space-y-4">
                    {client.contacts.map((contact) => (
                      <div key={contact.id} className="flex items-start gap-3">
                        <Avatar name={contact.name} size="sm" />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-text-primary">{contact.name}</p>
                            {contact.isPrimary && <Badge size="sm" variant="primary">Principal</Badge>}
                          </div>
                          <p className="text-xs text-text-muted">{contact.role}</p>
                          <div className="flex items-center gap-3 mt-1">
                            <a href={`mailto:${contact.email}`} className="text-xs text-accent-primary hover:underline flex items-center gap-1">
                              <Mail className="w-3 h-3" />
                              {contact.email}
                            </a>
                          </div>
                          <div className="flex items-center gap-1 mt-1">
                            <Phone className="w-3 h-3 text-text-muted" />
                            <span className="text-xs text-text-muted">{contact.phone}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </CardBody>
                </Card>
              </motion.div>

              {/* Recent Interactions */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
                <Card>
                  <CardHeader
                    title="Últimas Interações"
                    action={<Button variant="outline" size="sm">Ver Todas</Button>}
                  />
                  <CardBody className="space-y-4">
                    {interactions.slice(0, 3).map((interaction) => (
                      <div key={interaction.id} className="border-b border-border-subtle pb-3 last:border-0 last:pb-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge size="sm" variant="info">{interaction.type}</Badge>
                          <span className="text-xs text-text-muted">{interaction.createdAt}</span>
                        </div>
                        <p className="text-sm font-medium text-text-primary">{interaction.subject}</p>
                        <p className="text-xs text-text-muted">por {interaction.createdBy}</p>
                      </div>
                    ))}
                  </CardBody>
                </Card>
              </motion.div>
            </div>
          </div>
        )}

        {selectedTab === 'contracts' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader
                title="Contratos"
                action={<Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>Novo Contrato</Button>}
              />
              <CardBody className="p-0">
                <DataTable
                  columns={contractColumns}
                  data={contracts}
                  keyExtractor={(row) => row.id}
                />
              </CardBody>
            </Card>
          </motion.div>
        )}

        {selectedTab === 'services' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader
                title="Ordens de Serviço"
                action={<Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>Nova OS</Button>}
              />
              <CardBody className="p-0">
                <DataTable
                  columns={osColumns}
                  data={serviceOrders}
                  keyExtractor={(row) => row.id}
                />
              </CardBody>
            </Card>
          </motion.div>
        )}

        {selectedTab === 'interactions' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader
                title="Histórico de Interações"
                action={<Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>Registrar</Button>}
              />
              <CardBody>
                <div className="space-y-4">
                  {interactions.map((interaction) => (
                    <div key={interaction.id} className="p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="info">{interaction.type}</Badge>
                          <span className="text-sm font-medium text-text-primary">{interaction.subject}</span>
                        </div>
                        <span className="text-xs text-text-muted">{interaction.createdAt}</span>
                      </div>
                      <p className="text-sm text-text-secondary">{interaction.description}</p>
                      <p className="text-xs text-text-muted mt-2">Registrado por {interaction.createdBy}</p>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {selectedTab === 'documents' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader
                title="Documentos"
                action={<Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>Upload</Button>}
              />
              <CardBody>
                <p className="text-text-muted text-center py-8">Nenhum documento anexado</p>
              </CardBody>
            </Card>
          </motion.div>
        )}
      </div>
    </MainLayout>
  );
}
