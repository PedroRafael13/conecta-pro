'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  Search,
  Download,
  Eye,
  Edit,
  Trash2,
  UserX,
  FileText,
  Lock,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Users,
  Database,
  FileCheck,
  Settings,
  Plus,
  XCircle,
  RefreshCw,
  Mail,
  Calendar,
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
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

// Types
interface DataSubject {
  id: string;
  name: string;
  email: string;
  type: 'employee' | 'client' | 'supplier' | 'visitor';
  consentDate: string;
  consentStatus: 'active' | 'revoked' | 'pending';
  dataCategories: string[];
  lastAccess: string | null;
  requestsCount: number;
}

interface DataRequest {
  id: string;
  protocol: string;
  requester: string;
  requesterEmail: string;
  type: 'access' | 'rectification' | 'deletion' | 'portability' | 'objection';
  status: 'pending' | 'in_progress' | 'completed' | 'rejected';
  createdAt: string;
  deadline: string;
  completedAt: string | null;
  description: string;
}

interface DataMapping {
  id: string;
  category: string;
  purpose: string;
  legalBasis: string;
  retentionPeriod: string;
  sharingParties: string[];
  securityMeasures: string[];
  riskLevel: 'low' | 'medium' | 'high';
}

// Mock Data
const consentDistribution = [
  { name: 'Ativos', value: 85, color: '#10b981' },
  { name: 'Revogados', value: 10, color: '#ef4444' },
  { name: 'Pendentes', value: 5, color: '#f59e0b' },
];

const dataSubjects: DataSubject[] = [
  {
    id: '1',
    name: 'Roberto Silva',
    email: 'roberto.silva@email.com',
    type: 'employee',
    consentDate: '2025-06-15',
    consentStatus: 'active',
    dataCategories: ['Dados Pessoais', 'Dados Trabalhistas', 'Dados Bancários'],
    lastAccess: '2026-01-14',
    requestsCount: 1,
  },
  {
    id: '2',
    name: 'Shopping Center Norte',
    email: 'contato@shoppingnorte.com',
    type: 'client',
    consentDate: '2024-03-10',
    consentStatus: 'active',
    dataCategories: ['Dados Cadastrais', 'Dados Contratuais', 'Dados Financeiros'],
    lastAccess: '2026-01-15',
    requestsCount: 0,
  },
  {
    id: '3',
    name: 'Uniformes Brasil LTDA',
    email: 'contato@uniformesbrasil.com',
    type: 'supplier',
    consentDate: '2025-01-20',
    consentStatus: 'active',
    dataCategories: ['Dados Cadastrais', 'Dados Bancários'],
    lastAccess: '2026-01-10',
    requestsCount: 0,
  },
  {
    id: '4',
    name: 'Maria Santos',
    email: 'maria.santos@email.com',
    type: 'employee',
    consentDate: '2025-08-01',
    consentStatus: 'revoked',
    dataCategories: ['Dados Pessoais', 'Dados Trabalhistas'],
    lastAccess: null,
    requestsCount: 2,
  },
  {
    id: '5',
    name: 'Visitante Exemplo',
    email: 'visitante@email.com',
    type: 'visitor',
    consentDate: '2026-01-15',
    consentStatus: 'pending',
    dataCategories: ['Dados de Acesso'],
    lastAccess: null,
    requestsCount: 0,
  },
];

const dataRequests: DataRequest[] = [
  {
    id: '1',
    protocol: 'LGPD-2026-001',
    requester: 'Maria Santos',
    requesterEmail: 'maria.santos@email.com',
    type: 'deletion',
    status: 'in_progress',
    createdAt: '2026-01-10',
    deadline: '2026-01-25',
    completedAt: null,
    description: 'Solicitação de exclusão de todos os dados pessoais',
  },
  {
    id: '2',
    protocol: 'LGPD-2026-002',
    requester: 'Carlos Eduardo',
    requesterEmail: 'carlos.eduardo@email.com',
    type: 'access',
    status: 'completed',
    createdAt: '2026-01-05',
    deadline: '2026-01-20',
    completedAt: '2026-01-12',
    description: 'Solicitação de acesso aos dados armazenados',
  },
  {
    id: '3',
    protocol: 'LGPD-2026-003',
    requester: 'Roberto Silva',
    requesterEmail: 'roberto.silva@email.com',
    type: 'rectification',
    status: 'pending',
    createdAt: '2026-01-14',
    deadline: '2026-01-29',
    completedAt: null,
    description: 'Solicitação de correção de endereço residencial',
  },
  {
    id: '4',
    protocol: 'LGPD-2025-089',
    requester: 'Ana Paula',
    requesterEmail: 'ana.paula@email.com',
    type: 'portability',
    status: 'completed',
    createdAt: '2025-12-20',
    deadline: '2026-01-04',
    completedAt: '2026-01-02',
    description: 'Solicitação de portabilidade de dados',
  },
];

const dataMappings: DataMapping[] = [
  {
    id: '1',
    category: 'Dados Pessoais de Funcionários',
    purpose: 'Gestão de RH e Folha de Pagamento',
    legalBasis: 'Execução de Contrato (Art. 7º, V)',
    retentionPeriod: '5 anos após desligamento',
    sharingParties: ['Contador', 'eSocial'],
    securityMeasures: ['Criptografia', 'Controle de Acesso', 'Backup'],
    riskLevel: 'medium',
  },
  {
    id: '2',
    category: 'Dados de Clientes',
    purpose: 'Prestação de Serviços de Segurança',
    legalBasis: 'Execução de Contrato (Art. 7º, V)',
    retentionPeriod: '10 anos após término do contrato',
    sharingParties: [],
    securityMeasures: ['Criptografia', 'Controle de Acesso'],
    riskLevel: 'low',
  },
  {
    id: '3',
    category: 'Dados Biométricos',
    purpose: 'Controle de Acesso e Ponto',
    legalBasis: 'Consentimento (Art. 7º, I)',
    retentionPeriod: '1 ano após desligamento',
    sharingParties: [],
    securityMeasures: ['Criptografia forte', 'Acesso restrito', 'Anonimização'],
    riskLevel: 'high',
  },
  {
    id: '4',
    category: 'Dados de Fornecedores',
    purpose: 'Gestão de Compras e Pagamentos',
    legalBasis: 'Execução de Contrato (Art. 7º, V)',
    retentionPeriod: '5 anos após último pedido',
    sharingParties: ['Contador'],
    securityMeasures: ['Controle de Acesso'],
    riskLevel: 'low',
  },
];

const typeLabels = {
  employee: 'Funcionário',
  client: 'Cliente',
  supplier: 'Fornecedor',
  visitor: 'Visitante',
};

const consentStatusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  revoked: { label: 'Revogado', color: 'danger' as const },
  pending: { label: 'Pendente', color: 'warning' as const },
};

const requestTypeConfig = {
  access: { label: 'Acesso', color: 'info' as const },
  rectification: { label: 'Retificação', color: 'warning' as const },
  deletion: { label: 'Exclusão', color: 'danger' as const },
  portability: { label: 'Portabilidade', color: 'primary' as const },
  objection: { label: 'Oposição', color: 'neutral' as const },
};

const requestStatusConfig = {
  pending: { label: 'Pendente', color: 'warning' as const },
  in_progress: { label: 'Em Andamento', color: 'info' as const },
  completed: { label: 'Concluída', color: 'success' as const },
  rejected: { label: 'Rejeitada', color: 'danger' as const },
};

const riskLevelConfig = {
  low: { label: 'Baixo', color: 'success' as const },
  medium: { label: 'Médio', color: 'warning' as const },
  high: { label: 'Alto', color: 'danger' as const },
};

const subjectColumns: Column<DataSubject>[] = [
  {
    key: 'name',
    header: 'Titular',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.name}</p>
        <p className="text-xs text-text-muted">{row.email}</p>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => <Badge variant="info">{typeLabels[row.type]}</Badge>,
  },
  {
    key: 'dataCategories',
    header: 'Categorias de Dados',
    render: (row) => (
      <div className="flex flex-wrap gap-1">
        {row.dataCategories.slice(0, 2).map((cat, idx) => (
          <Badge key={idx} variant="neutral" size="sm">{cat}</Badge>
        ))}
        {row.dataCategories.length > 2 && (
          <Badge variant="neutral" size="sm">+{row.dataCategories.length - 2}</Badge>
        )}
      </div>
    ),
  },
  {
    key: 'consentStatus',
    header: 'Consentimento',
    render: (row) => {
      const config = consentStatusConfig[row.consentStatus];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'consentDate',
    header: 'Data Consentimento',
    render: (row) => (
      <span className="text-sm">{new Date(row.consentDate).toLocaleDateString('pt-BR')}</span>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver dados">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Histórico">
          <FileText className="w-4 h-4" />
        </Button>
        {row.consentStatus === 'active' && (
          <Button variant="ghost" size="icon-sm" title="Revogar">
            <UserX className="w-4 h-4" />
          </Button>
        )}
      </div>
    ),
  },
];

const requestColumns: Column<DataRequest>[] = [
  {
    key: 'protocol',
    header: 'Protocolo',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.protocol}</p>
        <p className="text-xs text-text-muted">{new Date(row.createdAt).toLocaleDateString('pt-BR')}</p>
      </div>
    ),
  },
  {
    key: 'requester',
    header: 'Solicitante',
    render: (row) => (
      <div>
        <p className="text-text-primary">{row.requester}</p>
        <p className="text-xs text-text-muted">{row.requesterEmail}</p>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const config = requestTypeConfig[row.type];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'deadline',
    header: 'Prazo',
    render: (row) => {
      const isOverdue = new Date(row.deadline) < new Date() && row.status !== 'completed';
      return (
        <span className={`text-sm ${isOverdue ? 'text-accent-danger font-medium' : ''}`}>
          {new Date(row.deadline).toLocaleDateString('pt-BR')}
        </span>
      );
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = requestStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
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
          <Button variant="primary" size="sm">
            Atender
          </Button>
        )}
      </div>
    ),
  },
];

const mappingColumns: Column<DataMapping>[] = [
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => <span className="font-medium text-text-primary">{row.category}</span>,
  },
  {
    key: 'purpose',
    header: 'Finalidade',
    render: (row) => <span className="text-sm text-text-secondary">{row.purpose}</span>,
  },
  {
    key: 'legalBasis',
    header: 'Base Legal',
    render: (row) => <span className="text-sm">{row.legalBasis}</span>,
  },
  {
    key: 'retentionPeriod',
    header: 'Retenção',
    render: (row) => <span className="text-sm text-text-muted">{row.retentionPeriod}</span>,
  },
  {
    key: 'riskLevel',
    header: 'Risco',
    render: (row) => {
      const config = riskLevelConfig[row.riskLevel];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
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
      </div>
    ),
  },
];

export function LGPDPage() {
  const [selectedTab, setSelectedTab] = useState('subjects');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Stats
  const totalSubjects = dataSubjects.length;
  const activeConsents = dataSubjects.filter(s => s.consentStatus === 'active').length;
  const pendingRequests = dataRequests.filter(r => r.status === 'pending' || r.status === 'in_progress').length;
  const highRiskMappings = dataMappings.filter(m => m.riskLevel === 'high').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              LGPD - Proteção de Dados
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de consentimentos, solicitações e mapeamento de dados
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Relatório RIPD
            </Button>
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Solicitação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Titulares Cadastrados"
              value={totalSubjects}
              icon={<Users className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Consentimentos Ativos"
              value={activeConsents}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Solicitações Pendentes"
              value={pendingRequests}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Dados Alto Risco"
              value={highRiskMappings}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Consent Chart and Compliance Status */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Status de Consentimentos</h3>
              </CardHeader>
              <CardBody>
                <div className="h-48 flex items-center">
                  <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie
                        data={consentDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={60}
                        dataKey="value"
                        stroke="none"
                      >
                        {consentDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }}
                        formatter={(value: number) => [`${value}%`, 'Percentual']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex-1 space-y-2">
                    {consentDistribution.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-text-secondary">{item.name}</span>
                        </div>
                        <span className="text-sm font-medium">{item.value}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="lg:col-span-2">
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Checklist de Conformidade</h3>
              </CardHeader>
              <CardBody>
                <div className="space-y-3">
                  {[
                    { item: 'Política de Privacidade Publicada', done: true },
                    { item: 'DPO Nomeado', done: true },
                    { item: 'Mapeamento de Dados Completo', done: true },
                    { item: 'Medidas de Segurança Implementadas', done: true },
                    { item: 'RIPD Atualizado', done: false },
                    { item: 'Treinamento de Funcionários', done: false },
                  ].map((check, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 rounded-lg hover:bg-bg-tertiary">
                      <div className="flex items-center gap-3">
                        {check.done ? (
                          <CheckCircle2 className="w-5 h-5 text-accent-success" />
                        ) : (
                          <XCircle className="w-5 h-5 text-accent-danger" />
                        )}
                        <span className={check.done ? 'text-text-secondary' : 'text-text-primary'}>
                          {check.item}
                        </span>
                      </div>
                      {!check.done && (
                        <Button variant="secondary" size="sm">
                          Completar
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
                <div className="mt-4 pt-4 border-t border-border-subtle">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-text-secondary">Progresso de Conformidade</span>
                    <span className="text-sm font-medium">67%</span>
                  </div>
                  <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
                    <div className="h-full bg-accent-primary rounded-full" style={{ width: '67%' }} />
                  </div>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Pending Requests Alert */}
        {pendingRequests > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card className="border-accent-warning/30 bg-accent-warning/5">
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent-warning/20 rounded-lg">
                      <Clock className="w-5 h-5 text-accent-warning" />
                    </div>
                    <div>
                      <h4 className="font-medium text-text-primary">Solicitações de Titulares</h4>
                      <p className="text-sm text-text-secondary">
                        {pendingRequests} {pendingRequests === 1 ? 'solicitação aguarda' : 'solicitações aguardam'} atendimento (prazo legal: 15 dias)
                      </p>
                    </div>
                  </div>
                  <Button variant="secondary" size="sm" onClick={() => setSelectedTab('requests')}>
                    Ver Solicitações
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'subjects', label: 'Titulares' },
                { value: 'requests', label: 'Solicitações' },
                { value: 'mapping', label: 'Mapeamento de Dados' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Card>
            <CardBody className="border-b border-border-subtle">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Buscar..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                {selectedTab === 'subjects' && (
                  <>
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Tipos' },
                        { value: 'employee', label: 'Funcionários' },
                        { value: 'client', label: 'Clientes' },
                        { value: 'supplier', label: 'Fornecedores' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-44"
                    />
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Status' },
                        { value: 'active', label: 'Ativos' },
                        { value: 'revoked', label: 'Revogados' },
                        { value: 'pending', label: 'Pendentes' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-40"
                    />
                  </>
                )}
                {selectedTab === 'requests' && (
                  <Select
                    options={[
                      { value: 'all', label: 'Todos Status' },
                      { value: 'pending', label: 'Pendentes' },
                      { value: 'in_progress', label: 'Em Andamento' },
                      { value: 'completed', label: 'Concluídas' },
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-44"
                  />
                )}
              </div>
            </CardBody>
            <CardBody className="p-0">
              {selectedTab === 'subjects' ? (
                <DataTable
                  columns={subjectColumns}
                  data={dataSubjects}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'requests' ? (
                <DataTable
                  columns={requestColumns}
                  data={dataRequests}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <DataTable
                  columns={mappingColumns}
                  data={dataMappings}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Request Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Solicitação do Titular"
          description="Registre uma solicitação de direitos LGPD"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Registrar Solicitação
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome do Titular" placeholder="Nome completo" />
            <Input label="E-mail" type="email" placeholder="email@exemplo.com" />
            <Select
              label="Tipo de Solicitação"
              options={[
                { value: 'access', label: 'Acesso aos Dados' },
                { value: 'rectification', label: 'Retificação de Dados' },
                { value: 'deletion', label: 'Exclusão de Dados' },
                { value: 'portability', label: 'Portabilidade' },
                { value: 'objection', label: 'Oposição ao Tratamento' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o tipo..."
            />
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Descrição da Solicitação</label>
              <textarea
                className="w-full h-24 px-3 py-2 bg-bg-tertiary border border-border-default rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent"
                placeholder="Descreva os detalhes da solicitação..."
              />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <p className="text-sm text-text-secondary">
                <strong>Nota:</strong> O prazo legal para atendimento é de 15 dias úteis, conforme Art. 18, §1º da LGPD.
              </p>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
