'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Building2,
  MapPin,
  Phone,
  Mail,
  User,
  Calendar,
  Eye,
  Edit,
  MoreVertical,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  FileText,
  DollarSign,
  Users,
  Shield,
  Download,
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
interface Client {
  id: string;
  type: 'pj' | 'pf';
  name: string;
  tradeName: string | null;
  document: string; // CNPJ or CPF
  status: 'active' | 'inactive' | 'prospect' | 'suspended';
  segment: 'condominio' | 'comercial' | 'industrial' | 'governo' | 'residencial' | 'eventos';
  address: {
    street: string;
    number: string;
    city: string;
    state: string;
    zipCode: string;
  };
  contacts: {
    name: string;
    email: string;
    phone: string;
    role: string;
  }[];
  contractValue: number;
  contractStart: string;
  contractEnd: string;
  servicesCount: number;
  lastInteraction: string;
  healthScore: number; // 0-100
  createdAt: string;
}

// Mock Data
const clients: Client[] = [
  {
    id: '1',
    type: 'pj',
    name: 'Shopping Center Norte',
    tradeName: 'Shopping Center Norte',
    document: '12.345.678/0001-90',
    status: 'active',
    segment: 'comercial',
    address: {
      street: 'Av. Cruzeiro do Sul',
      number: '1100',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '02031-000',
    },
    contacts: [
      { name: 'João Silva', email: 'joao@scn.com.br', phone: '(11) 99999-1234', role: 'Gerente Operacional' },
      { name: 'Maria Santos', email: 'maria@scn.com.br', phone: '(11) 99888-5678', role: 'Coord. Segurança' },
    ],
    contractValue: 150000,
    contractStart: '2024-01-01',
    contractEnd: '2026-12-31',
    servicesCount: 5,
    lastInteraction: '2026-01-15',
    healthScore: 92,
    createdAt: '2023-06-15',
  },
  {
    id: '2',
    type: 'pj',
    name: 'Hospital São Lucas',
    tradeName: 'Hospital São Lucas',
    document: '23.456.789/0001-01',
    status: 'active',
    segment: 'comercial',
    address: {
      street: 'Rua Dr. Arnaldo',
      number: '500',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '01246-000',
    },
    contacts: [
      { name: 'Roberto Costa', email: 'roberto@hsl.com.br', phone: '(11) 97777-9012', role: 'Diretor Administrativo' },
    ],
    contractValue: 85000,
    contractStart: '2024-06-01',
    contractEnd: '2027-05-31',
    servicesCount: 3,
    lastInteraction: '2026-01-14',
    healthScore: 88,
    createdAt: '2024-05-10',
  },
  {
    id: '3',
    type: 'pj',
    name: 'Tech Park Empresarial',
    tradeName: 'Tech Park',
    document: '34.567.890/0001-12',
    status: 'active',
    segment: 'comercial',
    address: {
      street: 'Av. Paulista',
      number: '1000',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '01310-100',
    },
    contacts: [
      { name: 'Pedro Costa', email: 'pedro@techpark.com.br', phone: '(11) 96666-3456', role: 'Gerente de Facilities' },
    ],
    contractValue: 65000,
    contractStart: '2025-01-01',
    contractEnd: '2027-12-31',
    servicesCount: 4,
    lastInteraction: '2026-01-13',
    healthScore: 95,
    createdAt: '2024-11-20',
  },
  {
    id: '4',
    type: 'pj',
    name: 'Condomínio Aurora',
    tradeName: null,
    document: '45.678.901/0001-23',
    status: 'active',
    segment: 'condominio',
    address: {
      street: 'Rua das Flores',
      number: '200',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '04543-000',
    },
    contacts: [
      { name: 'Ana Oliveira', email: 'ana@condaurora.com.br', phone: '(11) 95555-7890', role: 'Síndica' },
    ],
    contractValue: 28000,
    contractStart: '2025-03-01',
    contractEnd: '2027-02-28',
    servicesCount: 2,
    lastInteraction: '2026-01-10',
    healthScore: 78,
    createdAt: '2025-02-15',
  },
  {
    id: '5',
    type: 'pj',
    name: 'Banco Regional S.A.',
    tradeName: 'Banco Regional',
    document: '56.789.012/0001-34',
    status: 'suspended',
    segment: 'comercial',
    address: {
      street: 'Av. Brigadeiro',
      number: '800',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '01451-000',
    },
    contacts: [
      { name: 'Carlos Mendes', email: 'carlos@bancoregional.com.br', phone: '(11) 94444-1234', role: 'Gerente de Segurança' },
    ],
    contractValue: 95000,
    contractStart: '2023-01-01',
    contractEnd: '2025-12-31',
    servicesCount: 3,
    lastInteraction: '2025-12-20',
    healthScore: 45,
    createdAt: '2022-10-05',
  },
  {
    id: '6',
    type: 'pj',
    name: 'Prefeitura Municipal',
    tradeName: null,
    document: '67.890.123/0001-45',
    status: 'prospect',
    segment: 'governo',
    address: {
      street: 'Praça da Sé',
      number: '100',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '01001-000',
    },
    contacts: [
      { name: 'Fernando Almeida', email: 'fernando@prefeitura.sp.gov.br', phone: '(11) 93333-5678', role: 'Secretário' },
    ],
    contractValue: 0,
    contractStart: '',
    contractEnd: '',
    servicesCount: 0,
    lastInteraction: '2026-01-08',
    healthScore: 0,
    createdAt: '2026-01-05',
  },
];

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const, icon: CheckCircle2 },
  inactive: { label: 'Inativo', color: 'neutral' as const, icon: XCircle },
  prospect: { label: 'Prospect', color: 'info' as const, icon: Clock },
  suspended: { label: 'Suspenso', color: 'danger' as const, icon: AlertTriangle },
};

const segmentConfig = {
  condominio: { label: 'Condomínio', color: 'primary' as const },
  comercial: { label: 'Comercial', color: 'info' as const },
  industrial: { label: 'Industrial', color: 'warning' as const },
  governo: { label: 'Governo', color: 'success' as const },
  residencial: { label: 'Residencial', color: 'info' as const },
  eventos: { label: 'Eventos', color: 'warning' as const },
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const columns: Column<Client>[] = [
  {
    key: 'name',
    header: 'Cliente',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 bg-bg-tertiary rounded-lg">
          <Building2 className="w-5 h-5 text-text-muted" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.document}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'segment',
    header: 'Segmento',
    render: (row) => {
      const config = segmentConfig[row.segment];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'contact',
    header: 'Contato',
    render: (row) => {
      const mainContact = row.contacts[0];
      if (!mainContact) return <span className="text-text-muted">-</span>;
      return (
        <div>
          <p className="text-sm text-text-primary">{mainContact.name}</p>
          <p className="text-xs text-text-muted">{mainContact.role}</p>
        </div>
      );
    },
  },
  {
    key: 'location',
    header: 'Localização',
    render: (row) => (
      <div className="flex items-center gap-1">
        <MapPin className="w-3 h-3 text-text-muted" />
        <span className="text-sm">{row.address.city}/{row.address.state}</span>
      </div>
    ),
  },
  {
    key: 'contract',
    header: 'Contrato',
    render: (row) => {
      if (!row.contractValue) return <span className="text-text-muted">-</span>;
      return (
        <div>
          <p className="text-sm font-medium text-text-primary">{formatCurrency(row.contractValue)}/mês</p>
          <p className="text-xs text-text-muted">{row.servicesCount} serviços</p>
        </div>
      );
    },
  },
  {
    key: 'health',
    header: 'Saúde',
    render: (row) => {
      if (row.healthScore === 0) return <span className="text-text-muted">-</span>;
      const color = row.healthScore >= 80 ? 'text-accent-success' : row.healthScore >= 60 ? 'text-accent-warning' : 'text-accent-danger';
      return (
        <div className="flex items-center gap-2">
          <div className="w-16 h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                row.healthScore >= 80 ? 'bg-accent-success' : row.healthScore >= 60 ? 'bg-accent-warning' : 'bg-accent-danger'
              }`}
              style={{ width: `${row.healthScore}%` }}
            />
          </div>
          <span className={`text-sm font-medium ${color}`}>{row.healthScore}%</span>
        </div>
      );
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
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function ClientsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Stats
  const activeCount = clients.filter(c => c.status === 'active').length;
  const prospectCount = clients.filter(c => c.status === 'prospect').length;
  const suspendedCount = clients.filter(c => c.status === 'suspended').length;
  const totalMRR = clients.filter(c => c.status === 'active').reduce((acc, c) => acc + c.contractValue, 0);
  const avgHealth = clients.filter(c => c.healthScore > 0).reduce((acc, c) => acc + c.healthScore, 0) / clients.filter(c => c.healthScore > 0).length;

  const filteredClients = clients.filter((client) => {
    const matchesSearch =
      client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      client.document.includes(searchTerm) ||
      client.address.city.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTab =
      selectedTab === 'all' ||
      client.status === selectedTab ||
      client.segment === selectedTab;

    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Clientes
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie todos os clientes e prospects
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Novo Cliente
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Clientes"
              value={clients.length}
              icon={<Building2 className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Ativos"
              value={activeCount}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Prospects"
              value={prospectCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="MRR Total"
              value={formatCurrency(totalMRR)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Saúde Média"
              value={`${Math.round(avgHealth)}%`}
              icon={<Shield className="w-6 h-6" />}
              iconColor={avgHealth >= 80 ? 'success' : 'warning'}
            />
          </motion.div>
        </StatGrid>

        {/* Alert for at-risk clients */}
        {suspendedCount > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-accent-warning/10 border border-accent-warning/30 rounded-xl p-4"
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-accent-warning" />
              <div className="flex-1">
                <p className="font-medium text-text-primary">
                  {suspendedCount} cliente(s) suspenso(s)
                </p>
                <p className="text-sm text-text-secondary">
                  Verifique a situação contratual e financeira
                </p>
              </div>
              <Button variant="secondary" size="sm">
                Ver Clientes
              </Button>
            </div>
          </motion.div>
        )}

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todos (${clients.length})` },
                  { value: 'active', label: `Ativos (${activeCount})` },
                  { value: 'prospect', label: `Prospects (${prospectCount})` },
                  { value: 'suspended', label: `Suspensos (${suspendedCount})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar cliente..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todos os Segmentos' },
                    { value: 'condominio', label: 'Condomínio' },
                    { value: 'comercial', label: 'Comercial' },
                    { value: 'industrial', label: 'Industrial' },
                    { value: 'governo', label: 'Governo' },
                  ]}
                  value="all"
                  onChange={() => {}}
                  className="w-48"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Clients Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredClients}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => console.log('Client clicked:', row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Client Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Novo Cliente"
          description="Cadastre um novo cliente ou prospect"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Cadastrar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="type" value="pj" defaultChecked className="text-accent-primary" />
                <span>Pessoa Jurídica</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="type" value="pf" className="text-accent-primary" />
                <span>Pessoa Física</span>
              </label>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Razão Social / Nome" placeholder="Nome completo" required />
              <Input label="Nome Fantasia" placeholder="Nome fantasia (opcional)" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="CNPJ / CPF" placeholder="00.000.000/0000-00" required />
              <Select
                label="Segmento"
                options={[
                  { value: 'condominio', label: 'Condomínio' },
                  { value: 'comercial', label: 'Comercial' },
                  { value: 'industrial', label: 'Industrial' },
                  { value: 'governo', label: 'Governo' },
                  { value: 'residencial', label: 'Residencial' },
                  { value: 'eventos', label: 'Eventos' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="font-medium text-text-primary mb-3">Endereço</h4>
              <div className="grid grid-cols-3 gap-4">
                <Input label="CEP" placeholder="00000-000" className="col-span-1" />
                <Input label="Logradouro" placeholder="Rua, Avenida..." className="col-span-2" />
              </div>
              <div className="grid grid-cols-4 gap-4 mt-3">
                <Input label="Número" placeholder="Nº" />
                <Input label="Complemento" placeholder="Apto, Sala..." />
                <Input label="Cidade" placeholder="Cidade" />
                <Select
                  label="Estado"
                  options={[
                    { value: 'SP', label: 'São Paulo' },
                    { value: 'RJ', label: 'Rio de Janeiro' },
                    { value: 'MG', label: 'Minas Gerais' },
                  ]}
                  value=""
                  onChange={() => {}}
                  placeholder="UF"
                />
              </div>
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="font-medium text-text-primary mb-3">Contato Principal</h4>
              <div className="grid grid-cols-2 gap-4">
                <Input label="Nome" placeholder="Nome do contato" />
                <Input label="Cargo" placeholder="Cargo/Função" />
              </div>
              <div className="grid grid-cols-2 gap-4 mt-3">
                <Input label="E-mail" type="email" placeholder="email@empresa.com" />
                <Input label="Telefone" placeholder="(00) 00000-0000" />
              </div>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
