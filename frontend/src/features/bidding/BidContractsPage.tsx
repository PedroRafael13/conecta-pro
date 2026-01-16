'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  FileText,
  Calendar,
  Clock,
  DollarSign,
  Building2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit2,
  Download,
  MoreHorizontal,
  TrendingUp,
  Users,
  Briefcase,
  FileSignature,
  RefreshCw,
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
  Textarea,
} from '@/design-system/components';
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
} from 'recharts';

// Types
interface BidContract {
  id: string;
  contractNumber: string;
  bidNumber: string;
  client: string;
  description: string;
  value: number;
  startDate: string;
  endDate: string;
  status: 'draft' | 'pending_signature' | 'active' | 'completed' | 'cancelled' | 'expired';
  renewalOption: boolean;
  renewalCount: number;
  category: 'vigilancia' | 'portaria' | 'limpeza' | 'facilities' | 'outros';
  signedAt: string | null;
  documents: number;
  createdAt: string;
}

// Mock Data
const contracts: BidContract[] = [
  {
    id: '1',
    contractNumber: 'CT-2026-001',
    bidNumber: 'PE-001/2025',
    client: 'Prefeitura Municipal de São Paulo',
    description: 'Serviços de vigilância patrimonial para prédios públicos',
    value: 2500000,
    startDate: '2026-01-01',
    endDate: '2026-12-31',
    status: 'active',
    renewalOption: true,
    renewalCount: 0,
    category: 'vigilancia',
    signedAt: '2025-12-20',
    documents: 8,
    createdAt: '2025-12-15',
  },
  {
    id: '2',
    contractNumber: 'CT-2026-002',
    bidNumber: 'PP-012/2025',
    client: 'Hospital Municipal',
    description: 'Serviços de portaria e controle de acesso',
    value: 850000,
    startDate: '2026-02-01',
    endDate: '2027-01-31',
    status: 'pending_signature',
    renewalOption: true,
    renewalCount: 0,
    category: 'portaria',
    signedAt: null,
    documents: 5,
    createdAt: '2026-01-10',
  },
  {
    id: '3',
    contractNumber: 'CT-2025-045',
    bidNumber: 'PE-089/2024',
    client: 'Secretaria de Educação',
    description: 'Vigilância em escolas municipais - Região Sul',
    value: 1800000,
    startDate: '2025-03-01',
    endDate: '2026-02-28',
    status: 'active',
    renewalOption: true,
    renewalCount: 1,
    category: 'vigilancia',
    signedAt: '2025-02-20',
    documents: 12,
    createdAt: '2025-02-10',
  },
  {
    id: '4',
    contractNumber: 'CT-2024-089',
    bidNumber: 'PE-045/2023',
    client: 'Câmara Municipal',
    description: 'Serviços de facilities completo',
    value: 650000,
    startDate: '2024-01-01',
    endDate: '2025-12-31',
    status: 'completed',
    renewalOption: false,
    renewalCount: 0,
    category: 'facilities',
    signedAt: '2023-12-15',
    documents: 15,
    createdAt: '2023-12-01',
  },
];

const contractsByCategory = [
  { name: 'Vigilância', value: 45, color: '#3B82F6' },
  { name: 'Portaria', value: 25, color: '#10B981' },
  { name: 'Limpeza', value: 15, color: '#F59E0B' },
  { name: 'Facilities', value: 10, color: '#8B5CF6' },
  { name: 'Outros', value: 5, color: '#6B7280' },
];

const contractsTimeline = [
  { month: 'Set', value: 1500000 },
  { month: 'Out', value: 2100000 },
  { month: 'Nov', value: 1800000 },
  { month: 'Dez', value: 2500000 },
  { month: 'Jan', value: 3200000 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'active', label: 'Ativos' },
  { id: 'pending_signature', label: 'Aguardando Assinatura' },
  { id: 'completed', label: 'Finalizados' },
];

const statusLabels = {
  draft: 'Rascunho',
  pending_signature: 'Ag. Assinatura',
  active: 'Ativo',
  completed: 'Finalizado',
  cancelled: 'Cancelado',
  expired: 'Expirado',
};

const statusColors = {
  draft: 'secondary',
  pending_signature: 'warning',
  active: 'success',
  completed: 'info',
  cancelled: 'danger',
  expired: 'neutral',
} as const;

const categoryLabels = {
  vigilancia: 'Vigilância',
  portaria: 'Portaria',
  limpeza: 'Limpeza',
  facilities: 'Facilities',
  outros: 'Outros',
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

const columns: Column<BidContract>[] = [
  {
    key: 'contractNumber',
    header: 'Contrato',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <FileSignature className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.contractNumber}</p>
          <p className="text-xs text-text-muted">Edital: {row.bidNumber}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'client',
    header: 'Cliente',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.client}</p>
        <p className="text-xs text-text-muted line-clamp-1">{row.description}</p>
      </div>
    ),
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => <Badge variant="info">{categoryLabels[row.category]}</Badge>,
  },
  {
    key: 'value',
    header: 'Valor',
    render: (row) => <span className="font-bold text-success">{formatCurrency(row.value)}</span>,
  },
  {
    key: 'endDate',
    header: 'Vigência',
    render: (row) => (
      <div className="flex items-center gap-2 text-sm">
        <Calendar className="w-4 h-4 text-text-muted" />
        <span>{new Date(row.startDate).toLocaleDateString('pt-BR')} - {new Date(row.endDate).toLocaleDateString('pt-BR')}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => <Badge variant={statusColors[row.status]}>{statusLabels[row.status]}</Badge>,
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Download">
          <Download className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function BidContractsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newContractClient, setNewContractClient] = useState('');
  const [newContractCategory, setNewContractCategory] = useState('');

  const filteredContracts = contracts.filter((contract) => {
    const matchesSearch =
      contract.contractNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contract.client.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && contract.status === activeTab;
  });

  // Stats
  const totalContracts = contracts.length;
  const activeContracts = contracts.filter((c) => c.status === 'active').length;
  const totalValue = contracts.filter((c) => c.status === 'active').reduce((acc, c) => acc + c.value, 0);
  const pendingSignature = contracts.filter((c) => c.status === 'pending_signature').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Contratos de Licitação</h1>
            <p className="text-text-secondary mt-1">Gestão de contratos originados de processos licitatórios</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Novo Contrato
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Contratos" value={totalContracts} icon={<FileText className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Contratos Ativos" value={activeContracts} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Valor Total Ativo" value={formatCurrency(totalValue)} icon={<DollarSign className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Aguardando Assinatura" value={pendingSignature} icon={<Clock className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Contratos por Categoria</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={contractsByCategory} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {contractsByCategory.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {contractsByCategory.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-text-muted">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Valor de Contratos (Mensal)</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={contractsTimeline}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" tickFormatter={(v) => `R$${(v / 1000000).toFixed(1)}M`} />
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                    <Bar dataKey="value" fill="#10B981" radius={[4, 4, 0, 0]} name="Valor" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex items-center gap-3">
            <Input
              placeholder="Buscar contratos..."
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

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable columns={columns} data={filteredContracts} keyExtractor={(row) => row.id} />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Novo Contrato"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary">Criar Contrato</Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Número do Contrato" placeholder="CT-2026-XXX" required />
              <Input label="Número do Edital" placeholder="PE-XXX/2026" required />
            </div>
            <Select
              label="Cliente"
              options={[
                { value: '1', label: 'Prefeitura Municipal de São Paulo' },
                { value: '2', label: 'Hospital Municipal' },
                { value: '3', label: 'Secretaria de Educação' },
              ]}
              value={newContractClient}
              onChange={(value) => setNewContractClient(value)}
              placeholder="Selecione..."
            />
            <Input label="Descrição do Objeto" placeholder="Descrição detalhada do serviço" />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Categoria"
                options={[
                  { value: 'vigilancia', label: 'Vigilância' },
                  { value: 'portaria', label: 'Portaria' },
                  { value: 'limpeza', label: 'Limpeza' },
                  { value: 'facilities', label: 'Facilities' },
                  { value: 'outros', label: 'Outros' },
                ]}
                value={newContractCategory}
                onChange={(value) => setNewContractCategory(value)}
                placeholder="Selecione..."
              />
              <Input label="Valor do Contrato" type="number" placeholder="0,00" leftIcon={<DollarSign className="w-4 h-4" />} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data de Início" type="date" required />
              <Input label="Data de Término" type="date" required />
            </div>
            <Textarea label="Observações" placeholder="Informações adicionais..." rows={3} />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
