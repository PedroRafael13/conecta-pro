'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  type Column,
  Modal,
  Select
} from '@/design-system/components';
import {
  Truck,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Building2,
  Phone,
  Mail,
  MapPin,
  FileText,
  DollarSign,
  Calendar,
  Edit,
  Trash2,
  Eye,
  Star,
  TrendingUp,
  Package,
  Clock,
  CheckCircle,
  AlertCircle,
  ShoppingCart
} from 'lucide-react';
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
  Legend
} from 'recharts';

// Types
interface Supplier {
  id: string;
  code: string;
  name: string;
  tradeName: string;
  cnpj: string;
  category: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  rating: number;
  status: 'active' | 'inactive' | 'blocked';
  totalOrders: number;
  totalSpent: number;
  lastOrderDate: string;
  paymentTerms: string;
}

interface PurchaseOrder {
  id: string;
  orderNumber: string;
  supplierId: string;
  supplierName: string;
  date: string;
  deliveryDate: string;
  status: 'pending' | 'approved' | 'shipped' | 'delivered' | 'cancelled';
  items: number;
  total: number;
}

// Mock data
const mockSuppliers: Supplier[] = [
  {
    id: '1',
    code: 'FOR001',
    name: 'Tech Solutions Ltda',
    tradeName: 'Tech Solutions',
    cnpj: '12.345.678/0001-90',
    category: 'Tecnologia',
    email: 'contato@techsolutions.com.br',
    phone: '(11) 3456-7890',
    address: 'Rua das Empresas, 100',
    city: 'São Paulo',
    state: 'SP',
    rating: 4.8,
    status: 'active',
    totalOrders: 45,
    totalSpent: 125000,
    lastOrderDate: '2026-01-10',
    paymentTerms: '30 dias'
  },
  {
    id: '2',
    code: 'FOR002',
    name: 'Office Supplies Brasil',
    tradeName: 'Office Supplies',
    cnpj: '23.456.789/0001-01',
    category: 'Materiais de Escritório',
    email: 'vendas@officesupplies.com.br',
    phone: '(11) 2345-6789',
    address: 'Av. Comercial, 500',
    city: 'Guarulhos',
    state: 'SP',
    rating: 4.2,
    status: 'active',
    totalOrders: 120,
    totalSpent: 45000,
    lastOrderDate: '2026-01-14',
    paymentTerms: '15 dias'
  },
  {
    id: '3',
    code: 'FOR003',
    name: 'Limpeza Total ME',
    tradeName: 'Limpeza Total',
    cnpj: '34.567.890/0001-12',
    category: 'Limpeza',
    email: 'pedidos@limpezatotal.com.br',
    phone: '(11) 9876-5432',
    address: 'Rua Industrial, 250',
    city: 'Osasco',
    state: 'SP',
    rating: 3.9,
    status: 'active',
    totalOrders: 78,
    totalSpent: 32000,
    lastOrderDate: '2026-01-12',
    paymentTerms: '7 dias'
  },
  {
    id: '4',
    code: 'FOR004',
    name: 'Uniformes Profissionais SA',
    tradeName: 'Uniformes Pro',
    cnpj: '45.678.901/0001-23',
    category: 'Uniformes',
    email: 'comercial@uniformespro.com.br',
    phone: '(11) 4567-8901',
    address: 'Rua da Confecção, 300',
    city: 'São Paulo',
    state: 'SP',
    rating: 4.5,
    status: 'inactive',
    totalOrders: 25,
    totalSpent: 78000,
    lastOrderDate: '2025-11-20',
    paymentTerms: '45 dias'
  }
];

const mockOrders: PurchaseOrder[] = [
  {
    id: '1',
    orderNumber: 'PC-2026-001',
    supplierId: '1',
    supplierName: 'Tech Solutions',
    date: '2026-01-15',
    deliveryDate: '2026-01-20',
    status: 'approved',
    items: 5,
    total: 15000
  },
  {
    id: '2',
    orderNumber: 'PC-2026-002',
    supplierId: '2',
    supplierName: 'Office Supplies',
    date: '2026-01-14',
    deliveryDate: '2026-01-18',
    status: 'shipped',
    items: 12,
    total: 2500
  },
  {
    id: '3',
    orderNumber: 'PC-2026-003',
    supplierId: '3',
    supplierName: 'Limpeza Total',
    date: '2026-01-13',
    deliveryDate: '2026-01-16',
    status: 'delivered',
    items: 8,
    total: 1200
  },
  {
    id: '4',
    orderNumber: 'PC-2026-004',
    supplierId: '1',
    supplierName: 'Tech Solutions',
    date: '2026-01-12',
    deliveryDate: '2026-01-25',
    status: 'pending',
    items: 3,
    total: 8500
  }
];

// Chart data
const spendingByCategory = [
  { name: 'Tecnologia', value: 125000, color: '#6366f1' },
  { name: 'Materiais', value: 45000, color: '#8b5cf6' },
  { name: 'Limpeza', value: 32000, color: '#10b981' },
  { name: 'Uniformes', value: 78000, color: '#f59e0b' }
];

const monthlySpending = [
  { month: 'Set', value: 45000 },
  { month: 'Out', value: 52000 },
  { month: 'Nov', value: 48000 },
  { month: 'Dez', value: 65000 },
  { month: 'Jan', value: 70000 }
];

export function SuppliersPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showNewSupplierModal, setShowNewSupplierModal] = useState(false);
  const [showNewOrderModal, setShowNewOrderModal] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Truck className="h-4 w-4" /> },
    { value: 'suppliers', label: 'Fornecedores', icon: <Building2 className="h-4 w-4" /> },
    { value: 'orders', label: 'Pedidos', icon: <ShoppingCart className="h-4 w-4" /> }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="success">Ativo</Badge>;
      case 'inactive':
        return <Badge variant="neutral">Inativo</Badge>;
      case 'blocked':
        return <Badge variant="danger">Bloqueado</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getOrderStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="warning">Pendente</Badge>;
      case 'approved':
        return <Badge variant="info">Aprovado</Badge>;
      case 'shipped':
        return <Badge variant="primary">Em Trânsito</Badge>;
      case 'delivered':
        return <Badge variant="success">Entregue</Badge>;
      case 'cancelled':
        return <Badge variant="danger">Cancelado</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        <Star
          key={i}
          className={`h-4 w-4 ${i < Math.floor(rating) ? 'text-warning fill-warning' : 'text-text-muted'}`}
        />
      );
    }
    return <div className="flex items-center gap-0.5">{stars}</div>;
  };

  const supplierColumns: Column<Supplier>[] = [
    {
      key: 'code',
      header: 'Código',
      render: (row) => (
        <span className="font-mono text-sm text-text-secondary">{row.code}</span>
      )
    },
    {
      key: 'name',
      header: 'Fornecedor',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.tradeName}</p>
          <p className="text-sm text-text-secondary">{row.category}</p>
        </div>
      )
    },
    {
      key: 'cnpj',
      header: 'CNPJ',
      render: (row) => (
        <span className="text-text-secondary">{row.cnpj}</span>
      )
    },
    {
      key: 'rating',
      header: 'Avaliação',
      render: (row) => (
        <div className="flex items-center gap-2">
          {renderStars(row.rating)}
          <span className="text-sm text-text-secondary">{row.rating.toFixed(1)}</span>
        </div>
      )
    },
    {
      key: 'totalSpent',
      header: 'Total Comprado',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.totalSpent.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedSupplier(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const orderColumns: Column<PurchaseOrder>[] = [
    {
      key: 'orderNumber',
      header: 'Nº Pedido',
      render: (row) => (
        <span className="font-mono font-medium text-text-primary">{row.orderNumber}</span>
      )
    },
    {
      key: 'supplierName',
      header: 'Fornecedor',
      render: (row) => (
        <span className="text-text-secondary">{row.supplierName}</span>
      )
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.date).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      key: 'deliveryDate',
      header: 'Previsão',
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.deliveryDate).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      key: 'items',
      header: 'Itens',
      render: (row) => (
        <span className="text-text-secondary">{row.items}</span>
      )
    },
    {
      key: 'total',
      header: 'Total',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getOrderStatusBadge(row.status)
    }
  ];

  const filteredSuppliers = mockSuppliers.filter(supplier => {
    const matchesSearch = supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.tradeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.cnpj.includes(searchTerm);
    const matchesCategory = filterCategory === 'all' || supplier.category === filterCategory;
    const matchesStatus = filterStatus === 'all' || supplier.status === filterStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Fornecedores
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de fornecedores e pedidos de compra
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewOrderModal(true)} variant="outline">
              <ShoppingCart className="h-4 w-4 mr-2" />
              Novo Pedido
            </Button>
            <Button onClick={() => setShowNewSupplierModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Fornecedor
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Fornecedores Ativos"
            value="156"
            icon={<Building2 className="h-5 w-5" />}
            iconColor="primary"
            change={8}
            changeLabel="novos este mês"
          />
          <StatCard
            title="Pedidos em Aberto"
            value="34"
            icon={<ShoppingCart className="h-5 w-5" />}
            iconColor="info"
            change={12}
            changeLabel="esta semana"
          />
          <StatCard
            title="Total a Pagar"
            value="R$ 280K"
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Avaliação Média"
            value="4.3"
            icon={<Star className="h-5 w-5" />}
            iconColor="success"
            change={0.2}
            changeLabel="vs. mês anterior"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Spending by Category */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Gastos por Categoria
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={spendingByCategory}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {spendingByCategory.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Monthly Spending */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Evolução de Compras
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlySpending}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" tickFormatter={(value) => `${value / 1000}K`} />
                    <Tooltip
                      formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="value" name="Total" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Top Suppliers */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Principais Fornecedores
              </h3>
              <div className="space-y-4">
                {mockSuppliers
                  .sort((a, b) => b.totalSpent - a.totalSpent)
                  .slice(0, 5)
                  .map((supplier) => (
                    <div key={supplier.id} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                          <Building2 className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{supplier.tradeName}</p>
                          <p className="text-sm text-text-secondary">{supplier.category}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-text-primary">
                          {supplier.totalSpent.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </p>
                        <p className="text-sm text-text-secondary">{supplier.totalOrders} pedidos</p>
                      </div>
                    </div>
                  ))}
              </div>
            </Card>

            {/* Recent Orders */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Pedidos Recentes
              </h3>
              <div className="space-y-4">
                {mockOrders.slice(0, 5).map((order) => (
                  <div key={order.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-info/10 flex items-center justify-center">
                        <Package className="h-5 w-5 text-info" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{order.orderNumber}</p>
                        <p className="text-sm text-text-secondary">{order.supplierName}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-medium text-text-primary">
                        {order.total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                      {getOrderStatusBadge(order.status)}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Suppliers Tab */}
        {activeTab === 'suppliers' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar fornecedor..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterCategory}
                onChange={setFilterCategory}
                options={[
                  { value: 'all', label: 'Todas categorias' },
                  { value: 'Tecnologia', label: 'Tecnologia' },
                  { value: 'Materiais de Escritório', label: 'Materiais de Escritório' },
                  { value: 'Limpeza', label: 'Limpeza' },
                  { value: 'Uniformes', label: 'Uniformes' }
                ]}
                className="w-48"
              />
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={[
                  { value: 'all', label: 'Todos status' },
                  { value: 'active', label: 'Ativos' },
                  { value: 'inactive', label: 'Inativos' },
                  { value: 'blocked', label: 'Bloqueados' }
                ]}
                className="w-40"
              />
            </div>
            <DataTable
              columns={supplierColumns}
              data={filteredSuppliers}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Orders Tab */}
        {activeTab === 'orders' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar pedido..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={[
                  { value: 'all', label: 'Todos status' },
                  { value: 'pending', label: 'Pendentes' },
                  { value: 'approved', label: 'Aprovados' },
                  { value: 'shipped', label: 'Em Trânsito' },
                  { value: 'delivered', label: 'Entregues' }
                ]}
                className="w-40"
              />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={orderColumns}
              data={mockOrders}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Supplier Detail Modal */}
        {selectedSupplier && (
          <Modal
            isOpen={!!selectedSupplier}
            onClose={() => setSelectedSupplier(null)}
            title="Detalhes do Fornecedor"
            size="lg"
          >
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Building2 className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">
                    {selectedSupplier.tradeName}
                  </h3>
                  <p className="text-text-secondary">{selectedSupplier.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {renderStars(selectedSupplier.rating)}
                    <span className="text-sm text-text-secondary">
                      ({selectedSupplier.rating.toFixed(1)})
                    </span>
                    {getStatusBadge(selectedSupplier.status)}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-text-secondary">
                    <FileText className="h-4 w-4" />
                    <span>CNPJ: {selectedSupplier.cnpj}</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Mail className="h-4 w-4" />
                    <span>{selectedSupplier.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Phone className="h-4 w-4" />
                    <span>{selectedSupplier.phone}</span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-text-secondary">
                    <MapPin className="h-4 w-4" />
                    <span>{selectedSupplier.address}</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Building2 className="h-4 w-4" />
                    <span>{selectedSupplier.city} - {selectedSupplier.state}</span>
                  </div>
                  <div className="flex items-center gap-2 text-text-secondary">
                    <Clock className="h-4 w-4" />
                    <span>Prazo: {selectedSupplier.paymentTerms}</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border-subtle">
                <div className="text-center p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-2xl font-bold text-text-primary">{selectedSupplier.totalOrders}</p>
                  <p className="text-sm text-text-secondary">Pedidos</p>
                </div>
                <div className="text-center p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-2xl font-bold text-text-primary">
                    {selectedSupplier.totalSpent.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                  <p className="text-sm text-text-secondary">Total Comprado</p>
                </div>
                <div className="text-center p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-2xl font-bold text-text-primary">
                    {new Date(selectedSupplier.lastOrderDate).toLocaleDateString('pt-BR')}
                  </p>
                  <p className="text-sm text-text-secondary">Último Pedido</p>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedSupplier(null)}>
                  Fechar
                </Button>
                <Button>
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
              </div>
            </div>
          </Modal>
        )}

        {/* New Supplier Modal */}
        <Modal
          isOpen={showNewSupplierModal}
          onClose={() => setShowNewSupplierModal(false)}
          title="Novo Fornecedor"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Razão Social" placeholder="Nome completo da empresa" />
              <Input label="Nome Fantasia" placeholder="Nome comercial" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="CNPJ" placeholder="00.000.000/0000-00" />
              <Select
                value=""
                onChange={() => {}}
                options={[
                  { value: '', label: 'Selecione uma categoria' },
                  { value: 'Tecnologia', label: 'Tecnologia' },
                  { value: 'Materiais de Escritório', label: 'Materiais de Escritório' },
                  { value: 'Limpeza', label: 'Limpeza' },
                  { value: 'Uniformes', label: 'Uniformes' }
                ]}
                className="w-full"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Email" type="email" placeholder="contato@empresa.com.br" />
              <Input label="Telefone" placeholder="(11) 0000-0000" />
            </div>
            <Input label="Endereço" placeholder="Rua, número" />
            <div className="grid grid-cols-3 gap-4">
              <Input label="Cidade" placeholder="Cidade" />
              <Input label="Estado" placeholder="UF" />
              <Input label="CEP" placeholder="00000-000" />
            </div>
            <Select
              value=""
              onChange={() => {}}
              options={[
                { value: '', label: 'Selecione o prazo de pagamento' },
                { value: '7', label: '7 dias' },
                { value: '15', label: '15 dias' },
                { value: '30', label: '30 dias' },
                { value: '45', label: '45 dias' },
                { value: '60', label: '60 dias' }
              ]}
              className="w-full"
            />
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewSupplierModal(false)}>
                Cancelar
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Cadastrar
              </Button>
            </div>
          </div>
        </Modal>

        {/* New Order Modal */}
        <Modal
          isOpen={showNewOrderModal}
          onClose={() => setShowNewOrderModal(false)}
          title="Novo Pedido de Compra"
          size="lg"
        >
          <div className="space-y-4">
            <Select
              value=""
              onChange={() => {}}
              options={[
                { value: '', label: 'Selecione o fornecedor' },
                ...mockSuppliers.map(s => ({ value: s.id, label: s.tradeName }))
              ]}
              className="w-full"
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data do Pedido" type="date" />
              <Input label="Previsão de Entrega" type="date" />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-text-primary">Itens do Pedido</h4>
                <Button variant="outline" size="sm">
                  <Plus className="h-4 w-4 mr-1" />
                  Adicionar Item
                </Button>
              </div>
              <div className="text-center py-8 text-text-secondary">
                Nenhum item adicionado ainda.
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewOrderModal(false)}>
                Cancelar
              </Button>
              <Button>
                <ShoppingCart className="h-4 w-4 mr-2" />
                Criar Pedido
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
