'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  Search,
  Filter,
  Plus,
  Download,
  Upload,
  BarChart3,
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  ArrowRightLeft,
  Eye,
  Edit,
  Trash2,
  QrCode,
  Box,
  Warehouse,
  Tag,
  Clock,
  CheckCircle2,
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
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

// Types
interface Product {
  id: string;
  code: string;
  name: string;
  category: string;
  unit: string;
  currentStock: number;
  minStock: number;
  maxStock: number;
  avgCost: number;
  totalValue: number;
  location: string;
  status: 'normal' | 'low' | 'critical' | 'overstock';
  lastMovement: string;
}

interface StockMovement {
  id: string;
  date: string;
  type: 'entry' | 'exit' | 'transfer' | 'adjustment';
  productCode: string;
  productName: string;
  quantity: number;
  unitCost: number;
  totalCost: number;
  origin: string;
  destination: string;
  responsible: string;
  notes: string;
}

// Mock Data
const categoryDistribution = [
  { name: 'Uniformes', value: 35, color: '#6366f1' },
  { name: 'Equipamentos', value: 28, color: '#8b5cf6' },
  { name: 'Material Limpeza', value: 18, color: '#3b82f6' },
  { name: 'EPIs', value: 12, color: '#10b981' },
  { name: 'Outros', value: 7, color: '#f59e0b' },
];

const monthlyMovements = [
  { month: 'Set', entries: 45000, exits: 38000 },
  { month: 'Out', entries: 52000, exits: 41000 },
  { month: 'Nov', entries: 48000, exits: 45000 },
  { month: 'Dez', entries: 65000, exits: 58000 },
  { month: 'Jan', entries: 42000, exits: 35000 },
];

const products: Product[] = [
  {
    id: '1',
    code: 'UNI-001',
    name: 'Camisa Polo Padrão',
    category: 'Uniformes',
    unit: 'UN',
    currentStock: 245,
    minStock: 100,
    maxStock: 400,
    avgCost: 45.00,
    totalValue: 11025.00,
    location: 'A-01-01',
    status: 'normal',
    lastMovement: '2026-01-14',
  },
  {
    id: '2',
    code: 'EQP-015',
    name: 'Rádio Comunicador',
    category: 'Equipamentos',
    unit: 'UN',
    currentStock: 18,
    minStock: 20,
    maxStock: 50,
    avgCost: 350.00,
    totalValue: 6300.00,
    location: 'B-02-03',
    status: 'low',
    lastMovement: '2026-01-12',
  },
  {
    id: '3',
    code: 'EPI-008',
    name: 'Colete Refletivo',
    category: 'EPIs',
    unit: 'UN',
    currentStock: 5,
    minStock: 30,
    maxStock: 100,
    avgCost: 28.00,
    totalValue: 140.00,
    location: 'A-02-05',
    status: 'critical',
    lastMovement: '2026-01-10',
  },
  {
    id: '4',
    code: 'LMP-003',
    name: 'Desinfetante 5L',
    category: 'Material Limpeza',
    unit: 'UN',
    currentStock: 85,
    minStock: 20,
    maxStock: 60,
    avgCost: 18.50,
    totalValue: 1572.50,
    location: 'C-01-02',
    status: 'overstock',
    lastMovement: '2026-01-15',
  },
  {
    id: '5',
    code: 'UNI-003',
    name: 'Calça Tática',
    category: 'Uniformes',
    unit: 'UN',
    currentStock: 180,
    minStock: 80,
    maxStock: 300,
    avgCost: 85.00,
    totalValue: 15300.00,
    location: 'A-01-03',
    status: 'normal',
    lastMovement: '2026-01-13',
  },
];

const movements: StockMovement[] = [
  {
    id: '1',
    date: '2026-01-15 14:30',
    type: 'entry',
    productCode: 'LMP-003',
    productName: 'Desinfetante 5L',
    quantity: 50,
    unitCost: 18.50,
    totalCost: 925.00,
    origin: 'Fornecedor ABC',
    destination: 'Almoxarifado Central',
    responsible: 'Maria Santos',
    notes: 'NF 12345',
  },
  {
    id: '2',
    date: '2026-01-15 10:15',
    type: 'exit',
    productCode: 'UNI-001',
    productName: 'Camisa Polo Padrão',
    quantity: 15,
    unitCost: 45.00,
    totalCost: 675.00,
    origin: 'Almoxarifado Central',
    destination: 'Cliente Shopping Norte',
    responsible: 'João Pereira',
    notes: 'Requisição 789',
  },
  {
    id: '3',
    date: '2026-01-14 16:45',
    type: 'transfer',
    productCode: 'EQP-015',
    productName: 'Rádio Comunicador',
    quantity: 5,
    unitCost: 350.00,
    totalCost: 1750.00,
    origin: 'Almoxarifado Central',
    destination: 'Filial Sul',
    responsible: 'Carlos Eduardo',
    notes: 'Transferência interna',
  },
  {
    id: '4',
    date: '2026-01-14 09:00',
    type: 'adjustment',
    productCode: 'EPI-008',
    productName: 'Colete Refletivo',
    quantity: -3,
    unitCost: 28.00,
    totalCost: -84.00,
    origin: 'Almoxarifado Central',
    destination: '-',
    responsible: 'Ana Paula',
    notes: 'Ajuste inventário - itens danificados',
  },
];

const statusConfig = {
  normal: { label: 'Normal', color: 'success' as const },
  low: { label: 'Baixo', color: 'warning' as const },
  critical: { label: 'Crítico', color: 'danger' as const },
  overstock: { label: 'Excesso', color: 'info' as const },
};

const typeConfig = {
  entry: { label: 'Entrada', color: 'success' as const, icon: TrendingUp },
  exit: { label: 'Saída', color: 'danger' as const, icon: TrendingDown },
  transfer: { label: 'Transferência', color: 'info' as const, icon: ArrowRightLeft },
  adjustment: { label: 'Ajuste', color: 'warning' as const, icon: Edit },
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

const productColumns: Column<Product>[] = [
  {
    key: 'name',
    header: 'Produto',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 bg-bg-tertiary rounded-lg">
          <Package className="w-5 h-5 text-text-muted" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.code} • {row.category}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'currentStock',
    header: 'Estoque',
    render: (row) => (
      <div>
        <span className="font-medium">{row.currentStock} {row.unit}</span>
        <p className="text-xs text-text-muted">Mín: {row.minStock} | Máx: {row.maxStock}</p>
      </div>
    ),
  },
  {
    key: 'location',
    header: 'Localização',
    render: (row) => (
      <div className="flex items-center gap-1 text-sm">
        <Warehouse className="w-3 h-3 text-text-muted" />
        {row.location}
      </div>
    ),
  },
  {
    key: 'avgCost',
    header: 'Custo Médio',
    render: (row) => <span className="text-sm">{formatCurrency(row.avgCost)}</span>,
  },
  {
    key: 'totalValue',
    header: 'Valor Total',
    render: (row) => <span className="font-medium">{formatCurrency(row.totalValue)}</span>,
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
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Movimentar">
          <ArrowRightLeft className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const movementColumns: Column<StockMovement>[] = [
  {
    key: 'date',
    header: 'Data',
    render: (row) => <span className="text-sm">{row.date}</span>,
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const config = typeConfig[row.type];
      const TypeIcon = config.icon;
      return (
        <div className="flex items-center gap-2">
          <TypeIcon className="w-4 h-4" />
          <Badge variant={config.color}>{config.label}</Badge>
        </div>
      );
    },
  },
  {
    key: 'productName',
    header: 'Produto',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.productName}</p>
        <p className="text-xs text-text-muted">{row.productCode}</p>
      </div>
    ),
  },
  {
    key: 'quantity',
    header: 'Quantidade',
    render: (row) => (
      <span className={`font-medium ${row.quantity > 0 ? 'text-accent-success' : 'text-accent-danger'}`}>
        {row.quantity > 0 ? '+' : ''}{row.quantity}
      </span>
    ),
  },
  {
    key: 'totalCost',
    header: 'Valor',
    render: (row) => <span className="text-sm">{formatCurrency(Math.abs(row.totalCost))}</span>,
  },
  {
    key: 'origin',
    header: 'Origem/Destino',
    render: (row) => (
      <div className="text-sm">
        <p className="text-text-secondary">{row.origin}</p>
        {row.destination !== '-' && (
          <p className="text-text-muted">→ {row.destination}</p>
        )}
      </div>
    ),
  },
  {
    key: 'responsible',
    header: 'Responsável',
    render: (row) => <span className="text-sm text-text-secondary">{row.responsible}</span>,
  },
];

export function InventoryPage() {
  const [selectedTab, setSelectedTab] = useState('products');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Filter states
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterProductStatus, setFilterProductStatus] = useState('all');
  const [filterMovementType, setFilterMovementType] = useState('all');

  // Modal form states
  const [newCategory, setNewCategory] = useState('');
  const [newUnit, setNewUnit] = useState('');

  // Stats
  const totalProducts = products.length;
  const totalValue = products.reduce((acc, p) => acc + p.totalValue, 0);
  const lowStockCount = products.filter(p => p.status === 'low' || p.status === 'critical').length;
  const lastMovements = movements.length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Controle de Estoque
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de produtos e movimentações
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<QrCode className="w-4 h-4" />}>
              Leitor QR
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Novo Produto
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Itens"
              value={totalProducts}
              icon={<Package className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Valor em Estoque"
              value={formatCurrency(totalValue)}
              icon={<Box className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Estoque Baixo"
              value={lowStockCount}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Movimentações Hoje"
              value={lastMovements}
              icon={<ArrowRightLeft className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Distribuição por Categoria</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64 flex items-center">
                  <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie
                        data={categoryDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        dataKey="value"
                        stroke="none"
                      >
                        {categoryDistribution.map((entry, index) => (
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
                    {categoryDistribution.map((cat) => (
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

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Movimentações Mensais</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={monthlyMovements}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                      <XAxis dataKey="month" stroke="#64748b" />
                      <YAxis stroke="#64748b" tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }}
                        formatter={(value: number) => [formatCurrency(value), '']}
                      />
                      <Bar dataKey="entries" name="Entradas" fill="#10b981" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="exits" name="Saídas" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Low Stock Alert */}
        {lowStockCount > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card className="border-accent-warning/30 bg-accent-warning/5">
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent-warning/20 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-accent-warning" />
                    </div>
                    <div>
                      <h4 className="font-medium text-text-primary">Alerta de Estoque</h4>
                      <p className="text-sm text-text-secondary">
                        {lowStockCount} {lowStockCount === 1 ? 'item está' : 'itens estão'} com estoque abaixo do mínimo
                      </p>
                    </div>
                  </div>
                  <Button variant="secondary" size="sm">
                    Ver Itens
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
                { value: 'products', label: 'Produtos' },
                { value: 'movements', label: 'Movimentações' },
                { value: 'inventory', label: 'Inventário' },
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
                    placeholder={selectedTab === 'products' ? 'Buscar produto...' : 'Buscar movimentação...'}
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                {selectedTab === 'products' && (
                  <>
                    <Select
                      options={[
                        { value: 'all', label: 'Todas Categorias' },
                        { value: 'uniformes', label: 'Uniformes' },
                        { value: 'equipamentos', label: 'Equipamentos' },
                        { value: 'epis', label: 'EPIs' },
                        { value: 'limpeza', label: 'Mat. Limpeza' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-48"
                    />
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Status' },
                        { value: 'normal', label: 'Normal' },
                        { value: 'low', label: 'Baixo' },
                        { value: 'critical', label: 'Crítico' },
                        { value: 'overstock', label: 'Excesso' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-40"
                    />
                  </>
                )}
                {selectedTab === 'movements' && (
                  <Select
                    options={[
                      { value: 'all', label: 'Todos Tipos' },
                      { value: 'entry', label: 'Entradas' },
                      { value: 'exit', label: 'Saídas' },
                      { value: 'transfer', label: 'Transferências' },
                      { value: 'adjustment', label: 'Ajustes' },
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-48"
                  />
                )}
              </div>
            </CardBody>
            <CardBody className="p-0">
              {selectedTab === 'products' ? (
                <DataTable
                  columns={productColumns}
                  data={products}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'movements' ? (
                <DataTable
                  columns={movementColumns}
                  data={movements}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <div className="p-8 text-center">
                  <Warehouse className="w-12 h-12 text-text-muted mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-text-primary">Inventário</h3>
                  <p className="text-text-secondary mt-1">Inicie um novo inventário ou consulte inventários anteriores</p>
                  <Button variant="primary" className="mt-4" leftIcon={<Plus className="w-4 h-4" />}>
                    Novo Inventário
                  </Button>
                </div>
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Product Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Novo Produto"
          description="Cadastre um novo item no estoque"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Salvar Produto
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <Input label="Código" placeholder="Ex: UNI-001" />
              <div className="col-span-2">
                <Input label="Nome do Produto" placeholder="Ex: Camisa Polo Padrão" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Categoria"
                options={[
                  { value: 'uniformes', label: 'Uniformes' },
                  { value: 'equipamentos', label: 'Equipamentos' },
                  { value: 'epis', label: 'EPIs' },
                  { value: 'limpeza', label: 'Material de Limpeza' },
                  { value: 'outros', label: 'Outros' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Unidade"
                options={[
                  { value: 'un', label: 'Unidade (UN)' },
                  { value: 'cx', label: 'Caixa (CX)' },
                  { value: 'kg', label: 'Quilograma (KG)' },
                  { value: 'lt', label: 'Litro (LT)' },
                  { value: 'mt', label: 'Metro (MT)' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Input label="Estoque Mínimo" type="number" placeholder="0" />
              <Input label="Estoque Máximo" type="number" placeholder="0" />
              <Input label="Localização" placeholder="Ex: A-01-01" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Custo Unitário" type="number" placeholder="R$ 0,00" />
              <Input label="Estoque Inicial" type="number" placeholder="0" />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
