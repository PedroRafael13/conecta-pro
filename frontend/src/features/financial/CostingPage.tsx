'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Calculator,
  DollarSign,
  TrendingUp,
  TrendingDown,
  PieChart,
  BarChart3,
  Settings,
  Download,
  RefreshCw,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  Building2,
  Users,
  Package,
  Clock,
  Target,
  Layers,
  ArrowRight,
  Sparkles,
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
  Legend,
  Sankey,
} from 'recharts';

// Types
interface CostCenter {
  id: string;
  name: string;
  type: 'department' | 'project' | 'client' | 'service';
  totalCost: number;
  directCost: number;
  indirectCost: number;
  allocation: number;
  margin: number;
  trend: 'up' | 'down' | 'stable';
}

interface CostDriver {
  id: string;
  name: string;
  category: string;
  value: number;
  unit: string;
  costPerUnit: number;
  totalCost: number;
}

interface Activity {
  id: string;
  name: string;
  costDriver: string;
  totalCost: number;
  allocation: CostAllocation[];
}

interface CostAllocation {
  costCenter: string;
  percentage: number;
  value: number;
}

// Mock Data
const mockCostCenters: CostCenter[] = [
  {
    id: '1',
    name: 'Operações - Vigilância',
    type: 'service',
    totalCost: 456000,
    directCost: 380000,
    indirectCost: 76000,
    allocation: 92,
    margin: 24.5,
    trend: 'up',
  },
  {
    id: '2',
    name: 'Operações - Portaria',
    type: 'service',
    totalCost: 312000,
    directCost: 265000,
    indirectCost: 47000,
    allocation: 88,
    margin: 28.2,
    trend: 'stable',
  },
  {
    id: '3',
    name: 'Operações - Limpeza',
    type: 'service',
    totalCost: 198000,
    directCost: 170000,
    indirectCost: 28000,
    allocation: 95,
    margin: 31.5,
    trend: 'up',
  },
  {
    id: '4',
    name: 'Administrativo',
    type: 'department',
    totalCost: 145000,
    directCost: 98000,
    indirectCost: 47000,
    allocation: 100,
    margin: 0,
    trend: 'down',
  },
  {
    id: '5',
    name: 'Comercial',
    type: 'department',
    totalCost: 87000,
    directCost: 65000,
    indirectCost: 22000,
    allocation: 100,
    margin: 0,
    trend: 'stable',
  },
];

const mockCostDrivers: CostDriver[] = [
  { id: '1', name: 'Horas Trabalhadas', category: 'Mão de Obra', value: 45600, unit: 'horas', costPerUnit: 18.5, totalCost: 843600 },
  { id: '2', name: 'Funcionários', category: 'Mão de Obra', value: 285, unit: 'pessoas', costPerUnit: 3200, totalCost: 912000 },
  { id: '3', name: 'Postos de Serviço', category: 'Operacional', value: 45, unit: 'postos', costPerUnit: 8500, totalCost: 382500 },
  { id: '4', name: 'Área Atendida', category: 'Operacional', value: 125000, unit: 'm²', costPerUnit: 0.85, totalCost: 106250 },
  { id: '5', name: 'Equipamentos', category: 'Infraestrutura', value: 380, unit: 'unidades', costPerUnit: 250, totalCost: 95000 },
];

const costBreakdown = [
  { name: 'Mão de Obra Direta', value: 720000, color: '#6366f1' },
  { name: 'Encargos', value: 324000, color: '#10b981' },
  { name: 'Materiais', value: 98000, color: '#f59e0b' },
  { name: 'Equipamentos', value: 65000, color: '#ef4444' },
  { name: 'Administrativo', value: 87000, color: '#8b5cf6' },
  { name: 'Outros', value: 45000, color: '#3b82f6' },
];

const costByService = [
  { servico: 'Vigilância', custo: 456000, receita: 580000, margem: 21.4 },
  { servico: 'Portaria', custo: 312000, receita: 420000, margem: 25.7 },
  { servico: 'Limpeza', custo: 198000, receita: 280000, margem: 29.3 },
  { servico: 'Facilities', custo: 145000, receita: 185000, margem: 21.6 },
];

const typeConfig = {
  department: { label: 'Departamento', color: 'info' as const },
  project: { label: 'Projeto', color: 'warning' as const },
  client: { label: 'Cliente', color: 'success' as const },
  service: { label: 'Serviço', color: 'primary' as const },
};

export function CostingPage() {
  const [costCenters, setCostCenters] = useState(mockCostCenters);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCenter, setSelectedCenter] = useState<CostCenter | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);

  const stats = {
    totalCost: costCenters.reduce((sum, c) => sum + c.totalCost, 0),
    directCost: costCenters.reduce((sum, c) => sum + c.directCost, 0),
    indirectCost: costCenters.reduce((sum, c) => sum + c.indirectCost, 0),
    avgMargin: (costCenters.filter((c) => c.margin > 0).reduce((sum, c) => sum + c.margin, 0) /
      costCenters.filter((c) => c.margin > 0).length).toFixed(1),
  };

  const filteredCostCenters = costCenters.filter((center) =>
    center.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const handleRecalculate = async () => {
    setIsCalculating(true);
    await new Promise((resolve) => setTimeout(resolve, 2500));
    setIsCalculating(false);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Calculator className="w-8 h-8 text-accent-primary" />
              Custeio ABC
            </h1>
            <p className="text-text-secondary mt-1">
              Activity-Based Costing - Alocação de custos por atividades
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<RefreshCw className={`w-4 h-4 ${isCalculating ? 'animate-spin' : ''}`} />}
              onClick={handleRecalculate}
              disabled={isCalculating}
            >
              {isCalculating ? 'Calculando...' : 'Recalcular'}
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Custo Total"
              value={formatCurrency(stats.totalCost)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Custos Diretos"
              value={formatCurrency(stats.directCost)}
              icon={<Target className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Custos Indiretos"
              value={formatCurrency(stats.indirectCost)}
              icon={<Layers className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Margem Média"
              value={`${stats.avgMargin}%`}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="overview" label="Visão Geral" />
          <Tab value="centers" label="Centros de Custo" />
          <Tab value="drivers" label="Direcionadores" />
          <Tab value="allocation" label="Alocação" />
          <Tab value="analysis" label="Análise" />
        </Tabs>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-3 gap-6">
            {/* Cost Breakdown */}
            <Card className="col-span-2">
              <CardHeader title="Composição de Custos" />
              <CardBody>
                <div className="flex gap-8">
                  <div className="w-72 h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPieChart>
                        <Pie
                          data={costBreakdown}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          dataKey="value"
                          nameKey="name"
                        >
                          {costBreakdown.map((entry, index) => (
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
                  <div className="flex-1 space-y-3">
                    {costBreakdown.map((item) => (
                      <div key={item.name} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: item.color }}
                          />
                          <span className="text-text-primary">{item.name}</span>
                        </div>
                        <div className="text-right">
                          <p className="font-medium text-text-primary">{formatCurrency(item.value)}</p>
                          <p className="text-xs text-text-muted">
                            {((item.value / costBreakdown.reduce((s, i) => s + i.value, 0)) * 100).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Cost by Service */}
            <Card>
              <CardHeader title="Custo por Serviço" />
              <CardBody>
                <div className="space-y-4">
                  {costByService.map((service) => (
                    <div key={service.servico} className="p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-text-primary">{service.servico}</span>
                        <Badge variant={service.margem >= 25 ? 'success' : 'warning'}>
                          {service.margem.toFixed(1)}% margem
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <p className="text-text-muted">Custo</p>
                          <p className="text-text-primary">{formatCurrency(service.custo)}</p>
                        </div>
                        <div>
                          <p className="text-text-muted">Receita</p>
                          <p className="text-green-500">{formatCurrency(service.receita)}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            {/* Margin Analysis */}
            <Card className="col-span-3">
              <CardHeader title="Análise de Margem por Serviço" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={costByService}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="servico" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v / 1000}k`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Legend />
                      <Bar dataKey="custo" name="Custo" fill="#ef4444" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="receita" name="Receita" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'centers' && (
          <>
            <Card>
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                    <Input
                      placeholder="Buscar centros de custo..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                    Filtros
                  </Button>
                  <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
                    Novo Centro
                  </Button>
                </div>
              </CardBody>
            </Card>

            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Centro de Custo</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Custo Direto</TableHead>
                    <TableHead>Custo Indireto</TableHead>
                    <TableHead>Custo Total</TableHead>
                    <TableHead>Alocação</TableHead>
                    <TableHead>Margem</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredCostCenters.map((center) => (
                    <TableRow key={center.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                            <Building2 className="w-5 h-5 text-accent-primary" />
                          </div>
                          <span className="font-medium text-text-primary">{center.name}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={typeConfig[center.type].color}>
                          {typeConfig[center.type].label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-text-primary">{formatCurrency(center.directCost)}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-text-primary">{formatCurrency(center.indirectCost)}</span>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium text-text-primary">{formatCurrency(center.totalCost)}</span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16">
                            <Progress value={center.allocation} color="primary" />
                          </div>
                          <span className="text-sm text-text-muted">{center.allocation}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {center.margin > 0 ? (
                          <Badge variant={center.margin >= 25 ? 'success' : 'warning'}>
                            {center.margin.toFixed(1)}%
                          </Badge>
                        ) : (
                          <span className="text-text-muted">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedCenter(center);
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
                              { label: 'Duplicar', icon: <Layers className="w-4 h-4" /> },
                              { label: 'Excluir', icon: <Trash2 className="w-4 h-4" /> },
                            ]}
                          />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          </>
        )}

        {activeTab === 'drivers' && (
          <Card>
            <CardHeader
              title="Direcionadores de Custo"
              subtitle="Cost drivers utilizados na alocação"
              action={
                <Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                  Novo Direcionador
                </Button>
              }
            />
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Direcionador</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Volume</TableHead>
                  <TableHead>Unidade</TableHead>
                  <TableHead>Custo/Unidade</TableHead>
                  <TableHead>Custo Total</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockCostDrivers.map((driver) => (
                  <TableRow key={driver.id}>
                    <TableCell>
                      <span className="font-medium text-text-primary">{driver.name}</span>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">{driver.category}</Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-text-primary">{driver.value.toLocaleString()}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-text-muted">{driver.unit}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-text-primary">{formatCurrency(driver.costPerUnit)}</span>
                    </TableCell>
                    <TableCell>
                      <span className="font-medium text-text-primary">{formatCurrency(driver.totalCost)}</span>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        )}

        {activeTab === 'allocation' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Matriz de Alocação" />
              <CardBody>
                <p className="text-text-muted mb-4">
                  Configure como os custos indiretos são alocados para cada centro de custo.
                </p>
                <div className="space-y-4">
                  {costCenters.filter(c => c.type === 'service').map((center) => (
                    <div key={center.id} className="p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-text-primary">{center.name}</span>
                        <span className="text-sm text-text-muted">{center.allocation}% alocado</span>
                      </div>
                      <Progress value={center.allocation} color="primary" />
                      <div className="flex items-center justify-between mt-2 text-sm">
                        <span className="text-text-muted">Indireto: {formatCurrency(center.indirectCost)}</span>
                        <Button variant="ghost" size="sm">
                          Configurar
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Regras de Rateio" />
              <CardBody>
                <div className="space-y-4">
                  {[
                    { name: 'Administrativo', driver: 'Faturamento', percentage: 5 },
                    { name: 'TI', driver: 'Nº de Funcionários', percentage: 3 },
                    { name: 'RH', driver: 'Nº de Funcionários', percentage: 2 },
                    { name: 'Financeiro', driver: 'Faturamento', percentage: 2 },
                  ].map((rule, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                      <div>
                        <p className="font-medium text-text-primary">{rule.name}</p>
                        <p className="text-sm text-text-muted">Base: {rule.driver}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-text-primary">{rule.percentage}%</p>
                        <p className="text-xs text-text-muted">do custo</p>
                      </div>
                    </div>
                  ))}
                  <Button variant="secondary" className="w-full" leftIcon={<Plus className="w-4 h-4" />}>
                    Nova Regra
                  </Button>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'analysis' && (
          <Card>
            <CardHeader
              title="Análise de Rentabilidade"
              action={
                <Badge variant="success" leftIcon={<Sparkles className="w-3 h-3" />}>
                  Insights IA
                </Badge>
              }
            />
            <CardBody>
              <div className="grid grid-cols-3 gap-4 mb-6">
                {[
                  {
                    title: 'Serviço mais rentável',
                    value: 'Limpeza',
                    detail: '29.3% de margem',
                    color: 'green',
                  },
                  {
                    title: 'Oportunidade de melhoria',
                    value: 'Vigilância',
                    detail: 'Margem pode aumentar 3%',
                    color: 'yellow',
                  },
                  {
                    title: 'Custo em alta',
                    value: 'Mão de Obra',
                    detail: '+8% vs mês anterior',
                    color: 'red',
                  },
                ].map((insight, idx) => (
                  <div key={idx} className={`p-4 bg-${insight.color}-500/10 rounded-lg border border-${insight.color}-500/30`}>
                    <p className="text-sm text-text-muted">{insight.title}</p>
                    <p className="text-xl font-bold text-text-primary mt-1">{insight.value}</p>
                    <p className={`text-sm text-${insight.color}-500 mt-1`}>{insight.detail}</p>
                  </div>
                ))}
              </div>

              <div className="p-4 bg-accent-primary/10 rounded-lg border border-accent-primary/30">
                <div className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-accent-primary mt-0.5" />
                  <div>
                    <p className="font-medium text-accent-primary">Recomendação da IA</p>
                    <p className="text-sm text-text-secondary mt-1">
                      Baseado na análise dos últimos 6 meses, recomendamos revisar a alocação de custos indiretos
                      para o serviço de Vigilância. Uma redistribuição pode aumentar a margem em até 3 pontos percentuais.
                    </p>
                    <Button variant="primary" size="sm" className="mt-3">
                      Ver Simulação
                    </Button>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        )}
      </div>

      {/* Details Modal */}
      <Modal
        isOpen={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        title={selectedCenter?.name || ''}
        size="lg"
      >
        {selectedCenter && (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Custo Total</p>
                <p className="text-xl font-bold text-text-primary">{formatCurrency(selectedCenter.totalCost)}</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Custo Direto</p>
                <p className="text-xl font-bold text-green-500">{formatCurrency(selectedCenter.directCost)}</p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                <p className="text-sm text-text-muted">Custo Indireto</p>
                <p className="text-xl font-bold text-yellow-500">{formatCurrency(selectedCenter.indirectCost)}</p>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-text-primary mb-3">Composição do Custo</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-muted">Mão de Obra</span>
                  <span className="text-text-primary">{formatCurrency(selectedCenter.directCost * 0.7)}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-muted">Materiais</span>
                  <span className="text-text-primary">{formatCurrency(selectedCenter.directCost * 0.2)}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-muted">Outros</span>
                  <span className="text-text-primary">{formatCurrency(selectedCenter.directCost * 0.1)}</span>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
                Exportar
              </Button>
              <Button variant="primary" leftIcon={<Edit className="w-4 h-4" />}>
                Editar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}

export default CostingPage;
