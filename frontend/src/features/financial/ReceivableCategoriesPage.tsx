'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Tags,
  Plus,
  Edit,
  Trash2,
  MoreVertical,
  Search,
  Filter,
  DollarSign,
  TrendingUp,
  PieChart,
  Settings,
  Download,
  Eye,
  Layers,
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
  StatCard,
  StatGrid,
  Dropdown,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/design-system/components';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

// Types
interface Category {
  id: string;
  name: string;
  description: string;
  parentId?: string;
  color: string;
  icon: string;
  status: 'active' | 'inactive';
  totalReceivables: number;
  receivedAmount: number;
  pendingAmount: number;
  count: number;
}

// Mock Data
const mockCategories: Category[] = [
  {
    id: '1',
    name: 'Serviços de Vigilância',
    description: 'Receitas de contratos de vigilância patrimonial',
    color: '#6366f1',
    icon: '🛡️',
    status: 'active',
    totalReceivables: 580000,
    receivedAmount: 520000,
    pendingAmount: 60000,
    count: 45,
  },
  {
    id: '2',
    name: 'Serviços de Portaria',
    description: 'Receitas de contratos de portaria',
    color: '#10b981',
    icon: '🚪',
    status: 'active',
    totalReceivables: 420000,
    receivedAmount: 400000,
    pendingAmount: 20000,
    count: 38,
  },
  {
    id: '3',
    name: 'Serviços de Limpeza',
    description: 'Receitas de contratos de limpeza',
    color: '#f59e0b',
    icon: '🧹',
    status: 'active',
    totalReceivables: 280000,
    receivedAmount: 265000,
    pendingAmount: 15000,
    count: 32,
  },
  {
    id: '4',
    name: 'Facilities',
    description: 'Receitas de serviços de facilities',
    color: '#8b5cf6',
    icon: '🏢',
    status: 'active',
    totalReceivables: 185000,
    receivedAmount: 175000,
    pendingAmount: 10000,
    count: 15,
  },
  {
    id: '5',
    name: 'Serviços Eventuais',
    description: 'Receitas de serviços esporádicos',
    color: '#3b82f6',
    icon: '📋',
    status: 'active',
    totalReceivables: 95000,
    receivedAmount: 85000,
    pendingAmount: 10000,
    count: 28,
  },
  {
    id: '6',
    name: 'Multas e Juros',
    description: 'Receitas de multas por atraso',
    color: '#ef4444',
    icon: '⚠️',
    status: 'active',
    totalReceivables: 12000,
    receivedAmount: 10000,
    pendingAmount: 2000,
    count: 12,
  },
];

const chartData = mockCategories.map((c) => ({
  name: c.name,
  value: c.totalReceivables,
  color: c.color,
}));

const statusConfig = {
  active: { label: 'Ativa', color: 'success' as const },
  inactive: { label: 'Inativa', color: 'secondary' as const },
};

export function ReceivableCategoriesPage() {
  const [categories, setCategories] = useState(mockCategories);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);

  const stats = {
    total: categories.length,
    active: categories.filter((c) => c.status === 'active').length,
    totalReceivables: categories.reduce((sum, c) => sum + c.totalReceivables, 0),
    totalPending: categories.reduce((sum, c) => sum + c.pendingAmount, 0),
  };

  const filteredCategories = categories.filter((category) =>
    category.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const handleDelete = (id: string) => {
    setCategories((prev) => prev.filter((c) => c.id !== id));
  };

  const handleToggleStatus = (id: string) => {
    setCategories((prev) =>
      prev.map((c) =>
        c.id === id
          ? { ...c, status: c.status === 'active' ? 'inactive' : 'active' }
          : c
      )
    );
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Tags className="w-8 h-8 text-accent-primary" />
              Categorias de Recebíveis
            </h1>
            <p className="text-text-secondary mt-1">
              Organize e categorize suas receitas a receber
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
              Nova Categoria
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Categorias"
              value={stats.total}
              icon={<Tags className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Categorias Ativas"
              value={stats.active}
              icon={<Layers className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Total em Recebíveis"
              value={formatCurrency(stats.totalReceivables)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Pendente"
              value={formatCurrency(stats.totalPending)}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Chart and List */}
        <div className="grid grid-cols-3 gap-6">
          {/* Pie Chart */}
          <Card>
            <CardHeader title="Distribuição por Categoria" />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      dataKey="value"
                      nameKey="name"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">
                {chartData.slice(0, 4).map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-text-muted truncate max-w-[120px]">{item.name}</span>
                    </div>
                    <span className="text-text-primary">{formatCurrency(item.value)}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Categories Table */}
          <Card className="col-span-2">
            <CardHeader
              title="Categorias"
              action={
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                  <Input
                    placeholder="Buscar..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
              }
            />
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Total</TableHead>
                  <TableHead>Recebido</TableHead>
                  <TableHead>Pendente</TableHead>
                  <TableHead>Qtd</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCategories.map((category) => (
                  <TableRow key={category.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center text-lg"
                          style={{ backgroundColor: `${category.color}20` }}
                        >
                          {category.icon}
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{category.name}</p>
                          <p className="text-xs text-text-muted">{category.description}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusConfig[category.status].color}>
                        {statusConfig[category.status].label}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-text-primary">{formatCurrency(category.totalReceivables)}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-green-500">{formatCurrency(category.receivedAmount)}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-yellow-500">{formatCurrency(category.pendingAmount)}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-text-muted">{category.count}</span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedCategory(category);
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
                            {
                              label: 'Editar',
                              icon: <Edit className="w-4 h-4" />,
                              onClick: () => {
                                setSelectedCategory(category);
                                setEditOpen(true);
                              },
                            },
                            {
                              label: category.status === 'active' ? 'Desativar' : 'Ativar',
                              icon: <Settings className="w-4 h-4" />,
                              onClick: () => handleToggleStatus(category.id),
                            },
                            {
                              label: 'Excluir',
                              icon: <Trash2 className="w-4 h-4" />,
                              onClick: () => handleDelete(category.id),
                            },
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

        {/* Bar Chart */}
        <Card>
          <CardHeader title="Recebíveis por Categoria" subtitle="Recebido vs Pendente" />
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockCategories}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={10}
                    tickFormatter={(v) => v.split(' ')[0]}
                  />
                  <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px',
                    }}
                    formatter={(value: number) => formatCurrency(value)}
                  />
                  <Bar dataKey="receivedAmount" name="Recebido" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="pendingAmount" name="Pendente" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Details Modal */}
      <Modal
        isOpen={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        title={selectedCategory?.name || ''}
        size="md"
      >
        {selectedCategory && (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div
                className="w-16 h-16 rounded-xl flex items-center justify-center text-3xl"
                style={{ backgroundColor: `${selectedCategory.color}20` }}
              >
                {selectedCategory.icon}
              </div>
              <div>
                <p className="text-lg font-medium text-text-primary">{selectedCategory.name}</p>
                <p className="text-text-muted">{selectedCategory.description}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Total em Recebíveis</p>
                <p className="text-xl font-bold text-text-primary">
                  {formatCurrency(selectedCategory.totalReceivables)}
                </p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Quantidade</p>
                <p className="text-xl font-bold text-text-primary">{selectedCategory.count}</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Recebido</p>
                <p className="text-xl font-bold text-green-500">
                  {formatCurrency(selectedCategory.receivedAmount)}
                </p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Pendente</p>
                <p className="text-xl font-bold text-yellow-500">
                  {formatCurrency(selectedCategory.pendingAmount)}
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<Edit className="w-4 h-4" />}>
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
        title="Nova Categoria"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-text-primary">Nome</label>
            <Input placeholder="Nome da categoria" className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Descrição</label>
            <Input placeholder="Descrição da categoria" className="mt-1" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-text-primary">Cor</label>
              <div className="flex items-center gap-2 mt-1">
                <input type="color" defaultValue="#6366f1" className="w-10 h-10 rounded" />
                <Input placeholder="#6366f1" className="flex-1" />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-text-primary">Ícone</label>
              <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                <option>🛡️ Vigilância</option>
                <option>🚪 Portaria</option>
                <option>🧹 Limpeza</option>
                <option>🏢 Facilities</option>
                <option>📋 Serviços</option>
                <option>⚠️ Multas</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Categoria Pai (opcional)</label>
            <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
              <option value="">Nenhuma (categoria raiz)</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setCreateOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              Criar Categoria
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}

export default ReceivableCategoriesPage;
