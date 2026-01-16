'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Building2,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  Mail,
  Phone,
  MapPin,
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Clock,
  FileText,
  CreditCard,
  Star,
  Download,
  Upload,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Modal,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Progress,
  Dropdown,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  Avatar,
} from '@/design-system/components';

// Types
interface Customer {
  id: string;
  name: string;
  type: 'pj' | 'pf';
  document: string;
  email: string;
  phone: string;
  address: string;
  status: 'active' | 'inactive' | 'blocked';
  creditLimit: number;
  usedCredit: number;
  balance: number;
  totalRevenue: number;
  lastPayment: string;
  riskScore: 'low' | 'medium' | 'high';
  contracts: number;
  rating: number;
}

// Mock Data
const mockCustomers: Customer[] = [
  {
    id: '1',
    name: 'Shopping Center Norte',
    type: 'pj',
    document: '12.345.678/0001-90',
    email: 'financeiro@shoppingnorte.com.br',
    phone: '(11) 3456-7890',
    address: 'Av. das Nações, 1234 - São Paulo/SP',
    status: 'active',
    creditLimit: 500000,
    usedCredit: 128000,
    balance: 0,
    totalRevenue: 1536000,
    lastPayment: '2026-01-15',
    riskScore: 'low',
    contracts: 3,
    rating: 5,
  },
  {
    id: '2',
    name: 'Tech Park Empresarial',
    type: 'pj',
    document: '98.765.432/0001-10',
    email: 'contato@techpark.com.br',
    phone: '(11) 2345-6789',
    address: 'Rua da Tecnologia, 500 - São Paulo/SP',
    status: 'active',
    creditLimit: 300000,
    usedCredit: 89000,
    balance: 15000,
    totalRevenue: 1068000,
    lastPayment: '2026-01-10',
    riskScore: 'medium',
    contracts: 2,
    rating: 4,
  },
  {
    id: '3',
    name: 'Condomínio Aurora',
    type: 'pj',
    document: '45.678.901/0001-23',
    email: 'sindico@condominioaurora.com.br',
    phone: '(11) 9876-5432',
    address: 'Rua das Flores, 100 - São Paulo/SP',
    status: 'active',
    creditLimit: 150000,
    usedCredit: 45000,
    balance: 0,
    totalRevenue: 540000,
    lastPayment: '2026-01-12',
    riskScore: 'low',
    contracts: 1,
    rating: 5,
  },
  {
    id: '4',
    name: 'Hospital Central',
    type: 'pj',
    document: '11.222.333/0001-44',
    email: 'financeiro@hospitalcentral.com.br',
    phone: '(11) 1234-5678',
    address: 'Av. da Saúde, 789 - São Paulo/SP',
    status: 'active',
    creditLimit: 400000,
    usedCredit: 38000,
    balance: 25000,
    totalRevenue: 456000,
    lastPayment: '2026-01-05',
    riskScore: 'medium',
    contracts: 1,
    rating: 4,
  },
  {
    id: '5',
    name: 'Universidade Federal',
    type: 'pj',
    document: '22.333.444/0001-55',
    email: 'contratos@unifederal.edu.br',
    phone: '(11) 5555-4444',
    address: 'Campus Universitário - São Paulo/SP',
    status: 'blocked',
    creditLimit: 250000,
    usedCredit: 67000,
    balance: 67000,
    totalRevenue: 804000,
    lastPayment: '2025-11-15',
    riskScore: 'high',
    contracts: 1,
    rating: 2,
  },
];

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  inactive: { label: 'Inativo', color: 'secondary' as const },
  blocked: { label: 'Bloqueado', color: 'danger' as const },
};

const riskConfig = {
  low: { label: 'Baixo', color: 'success' as const },
  medium: { label: 'Médio', color: 'warning' as const },
  high: { label: 'Alto', color: 'danger' as const },
};

export function CustomersPage() {
  const [customers, setCustomers] = useState(mockCustomers);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);

  const stats = {
    total: customers.length,
    active: customers.filter((c) => c.status === 'active').length,
    totalRevenue: customers.reduce((sum, c) => sum + c.totalRevenue, 0),
    totalBalance: customers.reduce((sum, c) => sum + c.balance, 0),
    highRisk: customers.filter((c) => c.riskScore === 'high').length,
  };

  const filteredCustomers = customers.filter((customer) => {
    const matchesSearch =
      customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      customer.document.includes(searchQuery);
    const matchesTab =
      activeTab === 'all' ||
      (activeTab === 'active' && customer.status === 'active') ||
      (activeTab === 'risk' && customer.riskScore === 'high') ||
      (activeTab === 'debtors' && customer.balance > 0);
    return matchesSearch && matchesTab;
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Users className="w-8 h-8 text-accent-primary" />
              Clientes Financeiro
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de crédito, histórico e análise de risco
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setCreateOpen(true)}
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
              value={stats.total}
              icon={<Users className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Clientes Ativos"
              value={stats.active}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Receita Total"
              value={formatCurrency(stats.totalRevenue)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Saldo em Aberto"
              value={formatCurrency(stats.totalBalance)}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Alto Risco"
              value={stats.highRisk}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="all" label="Todos" />
          <Tab value="active" label="Ativos" />
          <Tab value="risk" label="Alto Risco" />
          <Tab value="debtors" label="Inadimplentes" />
        </Tabs>

        {/* Search */}
        <Card>
          <CardBody>
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                <Input
                  placeholder="Buscar por nome ou CNPJ..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                Filtros
              </Button>
            </div>
          </CardBody>
        </Card>

        {/* Customers Table */}
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cliente</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Limite de Crédito</TableHead>
                <TableHead>Saldo em Aberto</TableHead>
                <TableHead>Receita Total</TableHead>
                <TableHead>Risco</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredCustomers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar name={customer.name} />
                      <div>
                        <p className="font-medium text-text-primary">{customer.name}</p>
                        <p className="text-xs text-text-muted">{customer.document}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusConfig[customer.status].color}>
                      {statusConfig[customer.status].label}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="text-text-primary">{formatCurrency(customer.creditLimit)}</p>
                      <div className="w-24 mt-1">
                        <Progress
                          value={(customer.usedCredit / customer.creditLimit) * 100}
                          color={customer.usedCredit / customer.creditLimit > 0.8 ? 'danger' : 'primary'}
                        />
                      </div>
                      <p className="text-xs text-text-muted">
                        {((customer.usedCredit / customer.creditLimit) * 100).toFixed(0)}% utilizado
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className={`font-medium ${customer.balance > 0 ? 'text-red-500' : 'text-green-500'}`}>
                      {formatCurrency(customer.balance)}
                    </span>
                  </TableCell>
                  <TableCell>
                    <span className="text-text-primary">{formatCurrency(customer.totalRevenue)}</span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={riskConfig[customer.riskScore].color}>
                      {riskConfig[customer.riskScore].label}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-4 h-4 ${
                            i < customer.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-600'
                          }`}
                        />
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedCustomer(customer);
                          setDetailsOpen(true);
                        }}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Dropdown
                        trigger={
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        }
                        items={[
                          { label: 'Editar', icon: <Edit className="w-4 h-4" /> },
                          { label: 'Extrato', icon: <FileText className="w-4 h-4" /> },
                          { label: 'Ajustar Crédito', icon: <CreditCard className="w-4 h-4" /> },
                          { label: 'Bloquear', icon: <AlertTriangle className="w-4 h-4" /> },
                        ]}
                      />
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>

      {/* Details Modal */}
      <Modal
        isOpen={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        title={selectedCustomer?.name || ''}
        size="lg"
      >
        {selectedCustomer && (
          <div className="space-y-6">
            {/* Customer Info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-text-muted">
                  <Building2 className="w-4 h-4" />
                  <span>{selectedCustomer.document}</span>
                </div>
                <div className="flex items-center gap-2 text-text-muted">
                  <Mail className="w-4 h-4" />
                  <span>{selectedCustomer.email}</span>
                </div>
                <div className="flex items-center gap-2 text-text-muted">
                  <Phone className="w-4 h-4" />
                  <span>{selectedCustomer.phone}</span>
                </div>
                <div className="flex items-center gap-2 text-text-muted">
                  <MapPin className="w-4 h-4" />
                  <span>{selectedCustomer.address}</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Status</span>
                  <Badge variant={statusConfig[selectedCustomer.status].color}>
                    {statusConfig[selectedCustomer.status].label}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Risco</span>
                  <Badge variant={riskConfig[selectedCustomer.riskScore].color}>
                    {riskConfig[selectedCustomer.riskScore].label}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Contratos Ativos</span>
                  <span className="text-text-primary">{selectedCustomer.contracts}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Último Pagamento</span>
                  <span className="text-text-primary">
                    {new Date(selectedCustomer.lastPayment).toLocaleDateString('pt-BR')}
                  </span>
                </div>
              </div>
            </div>

            {/* Financial Info */}
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Limite de Crédito</p>
                <p className="text-xl font-bold text-text-primary">
                  {formatCurrency(selectedCustomer.creditLimit)}
                </p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Crédito Utilizado</p>
                <p className="text-xl font-bold text-accent-primary">
                  {formatCurrency(selectedCustomer.usedCredit)}
                </p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Saldo em Aberto</p>
                <p className={`text-xl font-bold ${selectedCustomer.balance > 0 ? 'text-red-500' : 'text-green-500'}`}>
                  {formatCurrency(selectedCustomer.balance)}
                </p>
              </div>
            </div>

            {/* Credit Progress */}
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-text-muted">Utilização do Crédito</span>
                <span className="text-text-primary">
                  {((selectedCustomer.usedCredit / selectedCustomer.creditLimit) * 100).toFixed(1)}%
                </span>
              </div>
              <Progress
                value={(selectedCustomer.usedCredit / selectedCustomer.creditLimit) * 100}
                color={selectedCustomer.usedCredit / selectedCustomer.creditLimit > 0.8 ? 'danger' : 'primary'}
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<FileText className="w-4 h-4" />}>
                Ver Extrato
              </Button>
              <Button variant="secondary" leftIcon={<CreditCard className="w-4 h-4" />}>
                Ajustar Crédito
              </Button>
              <Button variant="primary" leftIcon={<Edit className="w-4 h-4" />}>
                Editar
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Create Modal */}
      <Modal
        isOpen={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Novo Cliente"
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-text-primary">Razão Social</label>
              <Input placeholder="Nome da empresa" className="mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-text-primary">CNPJ</label>
              <Input placeholder="00.000.000/0000-00" className="mt-1" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-text-primary">Email</label>
              <Input placeholder="email@empresa.com" className="mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-text-primary">Telefone</label>
              <Input placeholder="(00) 0000-0000" className="mt-1" />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Endereço</label>
            <Input placeholder="Endereço completo" className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Limite de Crédito</label>
            <Input placeholder="R$ 0,00" className="mt-1" />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setCreateOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              Criar Cliente
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}

export default CustomersPage;
