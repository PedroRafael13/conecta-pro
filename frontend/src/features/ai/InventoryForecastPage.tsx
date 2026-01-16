'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Clock,
  BarChart3,
  RefreshCw,
  Download,
  Settings,
  Search,
  Filter,
  Sparkles,
  Target,
  ShoppingCart,
  Truck,
  Calendar,
  DollarSign,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Progress,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
} from 'recharts';

// Types
interface InventoryItem {
  id: string;
  name: string;
  category: string;
  currentStock: number;
  minStock: number;
  maxStock: number;
  avgConsumption: number;
  forecastDemand: number;
  daysUntilEmpty: number;
  reorderPoint: number;
  status: 'ok' | 'low' | 'critical' | 'overstock';
  trend: 'up' | 'down' | 'stable';
}

interface ForecastData {
  month: string;
  actual: number;
  forecast: number;
  confidence: number;
}

// Mock Data
const mockInventory: InventoryItem[] = [
  {
    id: '1',
    name: 'Uniformes - Camisa Polo',
    category: 'Vestuário',
    currentStock: 45,
    minStock: 20,
    maxStock: 100,
    avgConsumption: 8,
    forecastDemand: 35,
    daysUntilEmpty: 5,
    reorderPoint: 30,
    status: 'low',
    trend: 'up',
  },
  {
    id: '2',
    name: 'Materiais de Limpeza - Kit',
    category: 'Limpeza',
    currentStock: 120,
    minStock: 50,
    maxStock: 200,
    avgConsumption: 15,
    forecastDemand: 60,
    daysUntilEmpty: 8,
    reorderPoint: 75,
    status: 'ok',
    trend: 'stable',
  },
  {
    id: '3',
    name: 'EPIs - Luvas',
    category: 'Segurança',
    currentStock: 15,
    minStock: 30,
    maxStock: 150,
    avgConsumption: 10,
    forecastDemand: 40,
    daysUntilEmpty: 1,
    reorderPoint: 45,
    status: 'critical',
    trend: 'up',
  },
  {
    id: '4',
    name: 'Rádios Comunicação',
    category: 'Equipamentos',
    currentStock: 85,
    minStock: 20,
    maxStock: 50,
    avgConsumption: 2,
    forecastDemand: 8,
    daysUntilEmpty: 42,
    reorderPoint: 25,
    status: 'overstock',
    trend: 'down',
  },
  {
    id: '5',
    name: 'Lanternas Táticas',
    category: 'Equipamentos',
    currentStock: 32,
    minStock: 15,
    maxStock: 60,
    avgConsumption: 3,
    forecastDemand: 12,
    daysUntilEmpty: 10,
    reorderPoint: 20,
    status: 'ok',
    trend: 'stable',
  },
];

const forecastData: ForecastData[] = [
  { month: 'Jul', actual: 450, forecast: 440, confidence: 95 },
  { month: 'Ago', actual: 520, forecast: 510, confidence: 93 },
  { month: 'Set', actual: 480, forecast: 495, confidence: 91 },
  { month: 'Out', actual: 550, forecast: 540, confidence: 89 },
  { month: 'Nov', actual: 620, forecast: 600, confidence: 87 },
  { month: 'Dez', actual: 580, forecast: 590, confidence: 85 },
  { month: 'Jan', actual: 540, forecast: 555, confidence: 92 },
  { month: 'Fev', actual: null, forecast: 580, confidence: 88 },
  { month: 'Mar', actual: null, forecast: 610, confidence: 84 },
  { month: 'Abr', actual: null, forecast: 590, confidence: 80 },
];

const demandByCategory = [
  { category: 'Vestuário', atual: 180, previsto: 210 },
  { category: 'Limpeza', atual: 320, previsto: 350 },
  { category: 'Segurança', atual: 150, previsto: 180 },
  { category: 'Equipamentos', atual: 80, previsto: 75 },
  { category: 'Outros', atual: 120, previsto: 130 },
];

const statusConfig = {
  ok: { label: 'Normal', color: 'success' as const },
  low: { label: 'Baixo', color: 'warning' as const },
  critical: { label: 'Crítico', color: 'danger' as const },
  overstock: { label: 'Excesso', color: 'info' as const },
};

export function InventoryForecastPage() {
  const [inventory, setInventory] = useState(mockInventory);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [isForecasting, setIsForecasting] = useState(false);

  const stats = {
    totalItems: inventory.length,
    criticalItems: inventory.filter((i) => i.status === 'critical').length,
    lowItems: inventory.filter((i) => i.status === 'low').length,
    overstock: inventory.filter((i) => i.status === 'overstock').length,
    forecastAccuracy: 92,
  };

  const filteredInventory = inventory.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRunForecast = async () => {
    setIsForecasting(true);
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setIsForecasting(false);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Package className="w-8 h-8 text-accent-primary" />
              Previsão de Estoque
            </h1>
            <p className="text-text-secondary mt-1">
              Análise preditiva de demanda e otimização de estoque com IA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Sparkles className={`w-4 h-4 ${isForecasting ? 'animate-spin' : ''}`} />}
              onClick={handleRunForecast}
              disabled={isForecasting}
            >
              {isForecasting ? 'Processando...' : 'Gerar Previsão'}
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Itens"
              value={stats.totalItems}
              icon={<Package className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Itens Críticos"
              value={stats.criticalItems}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Estoque Baixo"
              value={stats.lowItems}
              icon={<TrendingDown className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Excesso de Estoque"
              value={stats.overstock}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Precisão IA"
              value={`${stats.forecastAccuracy}%`}
              icon={<Target className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="overview" label="Visão Geral" />
          <Tab value="items" label="Itens" />
          <Tab value="forecast" label="Previsões" />
          <Tab value="recommendations" label="Recomendações" />
        </Tabs>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-3 gap-6">
            {/* Forecast Chart */}
            <Card className="col-span-2">
              <CardHeader title="Previsão de Demanda" subtitle="Histórico vs Previsão IA" />
              <CardBody>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={forecastData}>
                      <defs>
                        <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="actual"
                        name="Real"
                        stroke="#6366f1"
                        fillOpacity={1}
                        fill="url(#colorActual)"
                      />
                      <Area
                        type="monotone"
                        dataKey="forecast"
                        name="Previsão"
                        stroke="#10b981"
                        strokeDasharray="5 5"
                        fillOpacity={1}
                        fill="url(#colorForecast)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>

            {/* Status Summary */}
            <Card>
              <CardHeader title="Status do Estoque" />
              <CardBody>
                <div className="space-y-4">
                  {[
                    { status: 'Normal', count: inventory.filter((i) => i.status === 'ok').length, color: 'bg-green-500' },
                    { status: 'Baixo', count: stats.lowItems, color: 'bg-yellow-500' },
                    { status: 'Crítico', count: stats.criticalItems, color: 'bg-red-500' },
                    { status: 'Excesso', count: stats.overstock, color: 'bg-blue-500' },
                  ].map((item) => (
                    <div key={item.status} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${item.color}`} />
                        <span className="text-text-primary">{item.status}</span>
                      </div>
                      <span className="font-bold text-text-primary">{item.count}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-accent-primary/10 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-5 h-5 text-accent-primary" />
                    <span className="font-medium text-accent-primary">Insight IA</span>
                  </div>
                  <p className="text-sm text-text-secondary">
                    Baseado nas tendências, recomendamos aumentar o estoque de EPIs em 30% para o próximo mês.
                  </p>
                </div>
              </CardBody>
            </Card>

            {/* Demand by Category */}
            <Card className="col-span-3">
              <CardHeader title="Demanda por Categoria" />
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={demandByCategory}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                      <XAxis dataKey="category" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="atual" name="Atual" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="previsto" name="Previsto" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'items' && (
          <>
            <Card>
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                    <Input
                      placeholder="Buscar itens..."
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

            <div className="space-y-4">
              {filteredInventory.map((item) => (
                <Card key={item.id} className="hover:border-accent-primary/50 transition-colors">
                  <CardBody>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          item.status === 'critical' ? 'bg-red-500/10' :
                          item.status === 'low' ? 'bg-yellow-500/10' :
                          item.status === 'overstock' ? 'bg-blue-500/10' : 'bg-green-500/10'
                        }`}>
                          <Package className={`w-6 h-6 ${
                            item.status === 'critical' ? 'text-red-500' :
                            item.status === 'low' ? 'text-yellow-500' :
                            item.status === 'overstock' ? 'text-blue-500' : 'text-green-500'
                          }`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium text-text-primary">{item.name}</h3>
                            <Badge variant={statusConfig[item.status].color}>
                              {statusConfig[item.status].label}
                            </Badge>
                            <Badge variant="secondary">{item.category}</Badge>
                          </div>
                          <div className="flex items-center gap-4 mt-1 text-sm text-text-muted">
                            <span>Estoque: {item.currentStock} unid.</span>
                            <span>Mín: {item.minStock}</span>
                            <span>Máx: {item.maxStock}</span>
                            <span>Consumo médio: {item.avgConsumption}/dia</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <div className="flex items-center gap-1">
                            {item.trend === 'up' ? (
                              <ArrowUp className="w-4 h-4 text-red-500" />
                            ) : item.trend === 'down' ? (
                              <ArrowDown className="w-4 h-4 text-green-500" />
                            ) : null}
                            <span className="font-medium text-text-primary">
                              {item.forecastDemand} unid.
                            </span>
                          </div>
                          <span className="text-xs text-text-muted">Demanda prevista</span>
                        </div>
                        <div className="text-right">
                          <span className={`font-medium ${
                            item.daysUntilEmpty <= 3 ? 'text-red-500' :
                            item.daysUntilEmpty <= 7 ? 'text-yellow-500' : 'text-green-500'
                          }`}>
                            {item.daysUntilEmpty} dias
                          </span>
                          <p className="text-xs text-text-muted">Até acabar</p>
                        </div>
                        <div className="w-24">
                          <Progress
                            value={(item.currentStock / item.maxStock) * 100}
                            color={
                              item.status === 'critical' ? 'danger' :
                              item.status === 'low' ? 'warning' :
                              item.status === 'overstock' ? 'info' : 'success'
                            }
                          />
                          <span className="text-xs text-text-muted">
                            {Math.round((item.currentStock / item.maxStock) * 100)}%
                          </span>
                        </div>
                        <Button variant="secondary" size="sm">
                          <ShoppingCart className="w-4 h-4 mr-1" />
                          Repor
                        </Button>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          </>
        )}

        {activeTab === 'forecast' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Previsão por Período" />
              <CardBody>
                <div className="space-y-4">
                  {forecastData.slice(-4).map((data) => (
                    <div key={data.month} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                      <div>
                        <p className="font-medium text-text-primary">{data.month} 2026</p>
                        <p className="text-sm text-text-muted">Confiança: {data.confidence}%</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-accent-primary">{data.forecast}</p>
                        <p className="text-xs text-text-muted">unidades</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Configurações de Previsão" />
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-text-primary">Horizonte de previsão</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>1 mês</option>
                      <option>3 meses</option>
                      <option>6 meses</option>
                      <option>12 meses</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-text-primary">Modelo de previsão</label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>ARIMA + IA</option>
                      <option>Machine Learning</option>
                      <option>Média móvel</option>
                    </select>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Considerar sazonalidade</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Alertas automáticos</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <Button variant="primary" className="w-full" leftIcon={<RefreshCw className="w-4 h-4" />}>
                    Recalcular Previsões
                  </Button>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <Card>
            <CardHeader title="Recomendações de IA" />
            <CardBody>
              <div className="space-y-4">
                {[
                  {
                    type: 'critical',
                    title: 'Reposição Urgente: EPIs - Luvas',
                    description: 'Estoque crítico detectado. Recomendamos pedido imediato de 50 unidades.',
                    action: 'Criar pedido',
                    icon: AlertTriangle,
                    color: 'red',
                  },
                  {
                    type: 'warning',
                    title: 'Estoque Baixo: Uniformes',
                    description: 'Estoque abaixo do ponto de reposição. Agendar pedido para próxima semana.',
                    action: 'Agendar',
                    icon: Clock,
                    color: 'yellow',
                  },
                  {
                    type: 'info',
                    title: 'Otimização: Rádios Comunicação',
                    description: 'Estoque acima do necessário. Considere redistribuição ou redução de pedidos.',
                    action: 'Ver análise',
                    icon: TrendingUp,
                    color: 'blue',
                  },
                  {
                    type: 'success',
                    title: 'Previsão de Aumento: Limpeza',
                    description: 'Demanda deve aumentar 15% no próximo mês. Recomendamos aumento do estoque mínimo.',
                    action: 'Ajustar',
                    icon: Sparkles,
                    color: 'green',
                  },
                ].map((rec, idx) => (
                  <div key={idx} className={`flex items-start gap-4 p-4 bg-${rec.color}-500/10 rounded-lg border border-${rec.color}-500/30`}>
                    <div className={`w-10 h-10 rounded-lg bg-${rec.color}-500/20 flex items-center justify-center`}>
                      <rec.icon className={`w-5 h-5 text-${rec.color}-500`} />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-text-primary">{rec.title}</p>
                      <p className="text-sm text-text-muted mt-1">{rec.description}</p>
                    </div>
                    <Button variant="secondary" size="sm">
                      {rec.action}
                    </Button>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}

export default InventoryForecastPage;
