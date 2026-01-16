'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ShoppingCart,
  Search,
  Plus,
  Download,
  FileText,
  Building2,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  Package,
  Truck,
  Eye,
  Edit,
  Send,
  Calendar,
  Filter,
  MoreVertical,
  Users,
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
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Types
interface PurchaseOrder {
  id: string;
  number: string;
  supplier: string;
  supplierCnpj: string;
  items: number;
  totalValue: number;
  status: 'draft' | 'pending_approval' | 'approved' | 'sent' | 'partial' | 'completed' | 'cancelled';
  createdAt: string;
  expectedDelivery: string | null;
  createdBy: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

interface PurchaseRequest {
  id: string;
  number: string;
  requester: string;
  department: string;
  items: number;
  estimatedValue: number;
  status: 'pending' | 'approved' | 'rejected' | 'processed';
  createdAt: string;
  justification: string;
}

interface Supplier {
  id: string;
  name: string;
  cnpj: string;
  category: string;
  rating: number;
  ordersCount: number;
  totalPurchased: number;
  status: 'active' | 'inactive' | 'blocked';
  lastOrder: string | null;
}

// Mock Data
const purchaseHistory = [
  { month: 'Set', value: 85000 },
  { month: 'Out', value: 92000 },
  { month: 'Nov', value: 78000 },
  { month: 'Dez', value: 145000 },
  { month: 'Jan', value: 68000 },
];

const categorySpending = [
  { name: 'Uniformes', value: 45, color: '#6366f1' },
  { name: 'Equipamentos', value: 28, color: '#8b5cf6' },
  { name: 'Material Escritório', value: 12, color: '#3b82f6' },
  { name: 'Serviços', value: 10, color: '#10b981' },
  { name: 'Outros', value: 5, color: '#f59e0b' },
];

const orders: PurchaseOrder[] = [
  {
    id: '1',
    number: 'OC-2026-001',
    supplier: 'Uniformes Brasil LTDA',
    supplierCnpj: '12.345.678/0001-90',
    items: 5,
    totalValue: 28500.00,
    status: 'sent',
    createdAt: '2026-01-10',
    expectedDelivery: '2026-01-25',
    createdBy: 'Ana Paula',
    priority: 'high',
  },
  {
    id: '2',
    number: 'OC-2026-002',
    supplier: 'Equipatec',
    supplierCnpj: '98.765.432/0001-10',
    items: 3,
    totalValue: 15800.00,
    status: 'pending_approval',
    createdAt: '2026-01-14',
    expectedDelivery: null,
    createdBy: 'Carlos Eduardo',
    priority: 'medium',
  },
  {
    id: '3',
    number: 'OC-2026-003',
    supplier: 'Material Seg',
    supplierCnpj: '45.678.901/0001-23',
    items: 8,
    totalValue: 4200.00,
    status: 'approved',
    createdAt: '2026-01-15',
    expectedDelivery: null,
    createdBy: 'Maria Santos',
    priority: 'urgent',
  },
  {
    id: '4',
    number: 'OC-2025-089',
    supplier: 'Uniformes Brasil LTDA',
    supplierCnpj: '12.345.678/0001-90',
    items: 4,
    totalValue: 18200.00,
    status: 'completed',
    createdAt: '2025-12-20',
    expectedDelivery: '2026-01-05',
    createdBy: 'Ana Paula',
    priority: 'medium',
  },
  {
    id: '5',
    number: 'OC-2025-088',
    supplier: 'Limpeza Total',
    supplierCnpj: '56.789.012/0001-34',
    items: 12,
    totalValue: 3500.00,
    status: 'partial',
    createdAt: '2025-12-18',
    expectedDelivery: '2026-01-10',
    createdBy: 'João Pereira',
    priority: 'low',
  },
];

const requests: PurchaseRequest[] = [
  {
    id: '1',
    number: 'RC-2026-015',
    requester: 'Roberto Silva',
    department: 'Operações',
    items: 3,
    estimatedValue: 2800.00,
    status: 'pending',
    createdAt: '2026-01-15',
    justification: 'Reposição de equipamentos danificados',
  },
  {
    id: '2',
    number: 'RC-2026-014',
    requester: 'Juliana Costa',
    department: 'RH',
    items: 1,
    estimatedValue: 1500.00,
    status: 'approved',
    createdAt: '2026-01-14',
    justification: 'Novo computador para admissão',
  },
  {
    id: '3',
    number: 'RC-2026-013',
    requester: 'Pedro Almeida',
    department: 'Comercial',
    items: 5,
    estimatedValue: 650.00,
    status: 'processed',
    createdAt: '2026-01-12',
    justification: 'Material para apresentações',
  },
];

const suppliers: Supplier[] = [
  {
    id: '1',
    name: 'Uniformes Brasil LTDA',
    cnpj: '12.345.678/0001-90',
    category: 'Uniformes',
    rating: 4.8,
    ordersCount: 45,
    totalPurchased: 285000.00,
    status: 'active',
    lastOrder: '2026-01-10',
  },
  {
    id: '2',
    name: 'Equipatec',
    cnpj: '98.765.432/0001-10',
    category: 'Equipamentos',
    rating: 4.5,
    ordersCount: 28,
    totalPurchased: 158000.00,
    status: 'active',
    lastOrder: '2026-01-14',
  },
  {
    id: '3',
    name: 'Material Seg',
    cnpj: '45.678.901/0001-23',
    category: 'EPIs',
    rating: 4.2,
    ordersCount: 32,
    totalPurchased: 89000.00,
    status: 'active',
    lastOrder: '2026-01-15',
  },
  {
    id: '4',
    name: 'Limpeza Total',
    cnpj: '56.789.012/0001-34',
    category: 'Limpeza',
    rating: 3.8,
    ordersCount: 18,
    totalPurchased: 42000.00,
    status: 'inactive',
    lastOrder: '2025-12-18',
  },
];

const statusConfig = {
  draft: { label: 'Rascunho', color: 'neutral' as const },
  pending_approval: { label: 'Aguardando Aprovação', color: 'warning' as const },
  approved: { label: 'Aprovada', color: 'info' as const },
  sent: { label: 'Enviada', color: 'primary' as const },
  partial: { label: 'Entrega Parcial', color: 'warning' as const },
  completed: { label: 'Concluída', color: 'success' as const },
  cancelled: { label: 'Cancelada', color: 'danger' as const },
};

const requestStatusConfig = {
  pending: { label: 'Pendente', color: 'warning' as const },
  approved: { label: 'Aprovada', color: 'success' as const },
  rejected: { label: 'Rejeitada', color: 'danger' as const },
  processed: { label: 'Processada', color: 'info' as const },
};

const priorityConfig = {
  low: { label: 'Baixa', color: 'neutral' as const },
  medium: { label: 'Média', color: 'info' as const },
  high: { label: 'Alta', color: 'warning' as const },
  urgent: { label: 'Urgente', color: 'danger' as const },
};

const supplierStatusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  inactive: { label: 'Inativo', color: 'neutral' as const },
  blocked: { label: 'Bloqueado', color: 'danger' as const },
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

const orderColumns: Column<PurchaseOrder>[] = [
  {
    key: 'number',
    header: 'Pedido',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.number}</p>
        <p className="text-xs text-text-muted">{row.createdAt}</p>
      </div>
    ),
  },
  {
    key: 'supplier',
    header: 'Fornecedor',
    render: (row) => (
      <div>
        <p className="text-text-primary">{row.supplier}</p>
        <p className="text-xs text-text-muted">{row.supplierCnpj}</p>
      </div>
    ),
  },
  {
    key: 'items',
    header: 'Itens',
    render: (row) => <span className="text-sm">{row.items}</span>,
  },
  {
    key: 'totalValue',
    header: 'Valor Total',
    render: (row) => <span className="font-medium">{formatCurrency(row.totalValue)}</span>,
  },
  {
    key: 'priority',
    header: 'Prioridade',
    render: (row) => {
      const config = priorityConfig[row.priority];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'draft' && (
          <Button variant="ghost" size="icon-sm" title="Editar">
            <Edit className="w-4 h-4" />
          </Button>
        )}
        {row.status === 'approved' && (
          <Button variant="primary" size="sm" leftIcon={<Send className="w-3 h-3" />}>
            Enviar
          </Button>
        )}
        {row.status === 'pending_approval' && (
          <Button variant="success" size="sm" leftIcon={<CheckCircle2 className="w-3 h-3" />}>
            Aprovar
          </Button>
        )}
      </div>
    ),
  },
];

const requestColumns: Column<PurchaseRequest>[] = [
  {
    key: 'number',
    header: 'Requisição',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.number}</p>
        <p className="text-xs text-text-muted">{row.createdAt}</p>
      </div>
    ),
  },
  {
    key: 'requester',
    header: 'Solicitante',
    render: (row) => (
      <div>
        <p className="text-text-primary">{row.requester}</p>
        <p className="text-xs text-text-muted">{row.department}</p>
      </div>
    ),
  },
  {
    key: 'items',
    header: 'Itens',
    render: (row) => <span className="text-sm">{row.items}</span>,
  },
  {
    key: 'estimatedValue',
    header: 'Valor Estimado',
    render: (row) => <span className="font-medium">{formatCurrency(row.estimatedValue)}</span>,
  },
  {
    key: 'justification',
    header: 'Justificativa',
    render: (row) => <span className="text-sm text-text-secondary truncate max-w-[200px] block">{row.justification}</span>,
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
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'pending' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Aprovar">
              <CheckCircle2 className="w-4 h-4 text-accent-success" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Rejeitar">
              <XCircle className="w-4 h-4 text-accent-danger" />
            </Button>
          </>
        )}
      </div>
    ),
  },
];

const supplierColumns: Column<Supplier>[] = [
  {
    key: 'name',
    header: 'Fornecedor',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 bg-bg-tertiary rounded-lg">
          <Building2 className="w-5 h-5 text-text-muted" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.cnpj}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => <Badge variant="info">{row.category}</Badge>,
  },
  {
    key: 'rating',
    header: 'Avaliação',
    render: (row) => (
      <div className="flex items-center gap-1">
        <span className="font-medium">{row.rating.toFixed(1)}</span>
        <span className="text-accent-warning">★</span>
      </div>
    ),
  },
  {
    key: 'ordersCount',
    header: 'Pedidos',
    render: (row) => <span className="text-sm">{row.ordersCount}</span>,
  },
  {
    key: 'totalPurchased',
    header: 'Total Comprado',
    render: (row) => <span className="font-medium">{formatCurrency(row.totalPurchased)}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = supplierStatusConfig[row.status];
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
        <Button variant="ghost" size="icon-sm" title="Mais">
          <MoreVertical className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function ProcurementPage() {
  const [selectedTab, setSelectedTab] = useState('orders');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Stats
  const pendingOrders = orders.filter(o => o.status === 'pending_approval').length;
  const openOrders = orders.filter(o => ['approved', 'sent', 'partial'].includes(o.status)).length;
  const monthlySpend = purchaseHistory[purchaseHistory.length - 1].value;
  const activeSuppliers = suppliers.filter(s => s.status === 'active').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Compras
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de pedidos e fornecedores
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
              Nova Ordem de Compra
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Aguardando Aprovação"
              value={pendingOrders}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Pedidos em Aberto"
              value={openOrders}
              icon={<ShoppingCart className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Compras do Mês"
              value={formatCurrency(monthlySpend)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Fornecedores Ativos"
              value={activeSuppliers}
              icon={<Building2 className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Histórico de Compras</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={purchaseHistory}>
                      <defs>
                        <linearGradient id="colorPurchase" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                      <XAxis dataKey="month" stroke="#64748b" />
                      <YAxis stroke="#64748b" tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }}
                        formatter={(value: number) => [formatCurrency(value), 'Total']}
                      />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#6366f1"
                        fill="url(#colorPurchase)"
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Gastos por Categoria</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64 flex items-center">
                  <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie
                        data={categorySpending}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        dataKey="value"
                        stroke="none"
                      >
                        {categorySpending.map((entry, index) => (
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
                    {categorySpending.map((cat) => (
                      <div key={cat.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                          <span className="text-sm text-text-secondary">{cat.name}</span>
                        </div>
                        <span className="text-sm font-medium">{cat.value}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'orders', label: 'Ordens de Compra' },
                { value: 'requests', label: 'Requisições' },
                { value: 'suppliers', label: 'Fornecedores' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
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
                {selectedTab === 'orders' && (
                  <>
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Status' },
                        { value: 'pending', label: 'Aguardando Aprovação' },
                        { value: 'approved', label: 'Aprovadas' },
                        { value: 'sent', label: 'Enviadas' },
                        { value: 'completed', label: 'Concluídas' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-48"
                    />
                    <Select
                      options={[
                        { value: 'all', label: 'Todas Prioridades' },
                        { value: 'urgent', label: 'Urgente' },
                        { value: 'high', label: 'Alta' },
                        { value: 'medium', label: 'Média' },
                        { value: 'low', label: 'Baixa' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-44"
                    />
                  </>
                )}
                {selectedTab === 'suppliers' && (
                  <Select
                    options={[
                      { value: 'all', label: 'Todas Categorias' },
                      { value: 'uniformes', label: 'Uniformes' },
                      { value: 'equipamentos', label: 'Equipamentos' },
                      { value: 'epis', label: 'EPIs' },
                      { value: 'limpeza', label: 'Limpeza' },
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-48"
                  />
                )}
              </div>
            </CardBody>
            <CardBody className="p-0">
              {selectedTab === 'orders' ? (
                <DataTable
                  columns={orderColumns}
                  data={orders}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'requests' ? (
                <DataTable
                  columns={requestColumns}
                  data={requests}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <DataTable
                  columns={supplierColumns}
                  data={suppliers}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Order Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Ordem de Compra"
          description="Crie um novo pedido de compra"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar Ordem
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Fornecedor"
              options={suppliers.map(s => ({ value: s.id, label: s.name }))}
              value=""
              onChange={() => {}}
              placeholder="Selecione o fornecedor..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Prioridade"
                options={[
                  { value: 'low', label: 'Baixa' },
                  { value: 'medium', label: 'Média' },
                  { value: 'high', label: 'Alta' },
                  { value: 'urgent', label: 'Urgente' },
                ]}
                value="medium"
                onChange={() => {}}
              />
              <Input label="Previsão de Entrega" type="date" />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-text-primary">Itens do Pedido</h4>
                <Button variant="secondary" size="sm" leftIcon={<Plus className="w-3 h-3" />}>
                  Adicionar Item
                </Button>
              </div>
              <div className="text-sm text-text-muted text-center py-4">
                Nenhum item adicionado
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Observações</label>
              <textarea
                className="w-full h-20 px-3 py-2 bg-bg-tertiary border border-border-default rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent"
                placeholder="Observações adicionais..."
              />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
