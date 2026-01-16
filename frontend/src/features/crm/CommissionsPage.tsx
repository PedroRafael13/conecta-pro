'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  TrendingUp,
  Users,
  Calendar,
  Download,
  Filter,
  Search,
  Eye,
  Calculator,
  Target,
  Award,
  BarChart3,
  PieChart,
  CheckCircle,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { DataTable, Column } from '../../design-system/components/Table';
import { SimpleTabBar } from '../../design-system/components/Tabs';
import { Modal } from '../../design-system/components/Modal';
import { MainLayout } from '../../layouts/MainLayout';
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
  Cell
} from 'recharts';

interface Commission {
  id: string;
  salesperson: string;
  salesPersonId: string;
  period: string;
  totalSales: number;
  commissionRate: number;
  commissionValue: number;
  bonuses: number;
  deductions: number;
  netCommission: number;
  status: 'pending' | 'approved' | 'paid' | 'disputed';
  contractsCount: number;
  avgTicket: number;
}

interface SalespersonRanking {
  id: string;
  name: string;
  totalSales: number;
  totalCommission: number;
  contractsCount: number;
  conversionRate: number;
  avgTicket: number;
  trend: number;
}

const mockCommissions: Commission[] = [
  {
    id: '1',
    salesperson: 'Carlos Silva',
    salesPersonId: 'SP001',
    period: 'Janeiro/2026',
    totalSales: 450000,
    commissionRate: 5,
    commissionValue: 22500,
    bonuses: 3500,
    deductions: 0,
    netCommission: 26000,
    status: 'paid',
    contractsCount: 12,
    avgTicket: 37500
  },
  {
    id: '2',
    salesperson: 'Ana Rodrigues',
    salesPersonId: 'SP002',
    period: 'Janeiro/2026',
    totalSales: 380000,
    commissionRate: 5,
    commissionValue: 19000,
    bonuses: 2000,
    deductions: 500,
    netCommission: 20500,
    status: 'approved',
    contractsCount: 8,
    avgTicket: 47500
  },
  {
    id: '3',
    salesperson: 'Roberto Santos',
    salesPersonId: 'SP003',
    period: 'Janeiro/2026',
    totalSales: 520000,
    commissionRate: 6,
    commissionValue: 31200,
    bonuses: 5000,
    deductions: 0,
    netCommission: 36200,
    status: 'pending',
    contractsCount: 15,
    avgTicket: 34666
  },
  {
    id: '4',
    salesperson: 'Mariana Costa',
    salesPersonId: 'SP004',
    period: 'Janeiro/2026',
    totalSales: 290000,
    commissionRate: 4.5,
    commissionValue: 13050,
    bonuses: 0,
    deductions: 1200,
    netCommission: 11850,
    status: 'disputed',
    contractsCount: 6,
    avgTicket: 48333
  }
];

const rankingData: SalespersonRanking[] = [
  { id: '1', name: 'Roberto Santos', totalSales: 520000, totalCommission: 36200, contractsCount: 15, conversionRate: 45, avgTicket: 34666, trend: 15 },
  { id: '2', name: 'Carlos Silva', totalSales: 450000, totalCommission: 26000, contractsCount: 12, conversionRate: 38, avgTicket: 37500, trend: 8 },
  { id: '3', name: 'Ana Rodrigues', totalSales: 380000, totalCommission: 20500, contractsCount: 8, conversionRate: 42, avgTicket: 47500, trend: -3 },
  { id: '4', name: 'Mariana Costa', totalSales: 290000, totalCommission: 11850, contractsCount: 6, conversionRate: 30, avgTicket: 48333, trend: -10 }
];

const commissionTrendData = [
  { month: 'Ago', total: 85000, meta: 100000 },
  { month: 'Set', total: 92000, meta: 100000 },
  { month: 'Out', total: 78000, meta: 100000 },
  { month: 'Nov', total: 105000, meta: 100000 },
  { month: 'Dez', total: 125000, meta: 120000 },
  { month: 'Jan', total: 94550, meta: 100000 }
];

const tabs = [
  { value: 'commissions', label: 'Comissões', icon: <DollarSign className="h-4 w-4" /> },
  { value: 'ranking', label: 'Ranking', icon: <Award className="h-4 w-4" /> },
  { value: 'simulation', label: 'Simulador', icon: <Calculator className="h-4 w-4" /> }
];

export function CommissionsPage() {
  const [activeTab, setActiveTab] = useState('commissions');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('2026-01');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedCommission, setSelectedCommission] = useState<Commission | null>(null);
  const [simulationValues, setSimulationValues] = useState({
    sales: 100000,
    rate: 5,
    bonus: 0
  });

  const getStatusInfo = (status: Commission['status']) => {
    const statuses = {
      pending: { label: 'Pendente', color: 'warning' as const, icon: Clock },
      approved: { label: 'Aprovada', color: 'info' as const, icon: CheckCircle },
      paid: { label: 'Paga', color: 'success' as const, icon: CheckCircle },
      disputed: { label: 'Contestada', color: 'danger' as const, icon: AlertTriangle }
    };
    return statuses[status];
  };

  const columns: Column<Commission>[] = [
    {
      key: 'salesperson',
      header: 'Vendedor',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-white font-bold">
            {row.salesperson.split(' ').map(n => n[0]).slice(0, 2).join('')}
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.salesperson}</p>
            <p className="text-xs text-text-secondary">{row.salesPersonId}</p>
          </div>
        </div>
      )
    },
    {
      key: 'period',
      header: 'Período',
      sortable: true,
      render: (row) => <span className="text-text-primary">{row.period}</span>
    },
    {
      key: 'totalSales',
      header: 'Vendas',
      sortable: true,
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.totalSales.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'commissionRate',
      header: 'Taxa',
      sortable: true,
      render: (row) => <Badge variant="info">{row.commissionRate}%</Badge>
    },
    {
      key: 'netCommission',
      header: 'Comissão Líquida',
      sortable: true,
      render: (row) => (
        <span className="font-semibold text-accent-success">
          {row.netCommission.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'contractsCount',
      header: 'Contratos',
      sortable: true,
      render: (row) => <span className="text-text-primary">{row.contractsCount}</span>
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row) => {
        const info = getStatusInfo(row.status);
        return <Badge variant={info.color}>{info.label}</Badge>;
      }
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => { setSelectedCommission(row); setShowDetailModal(true); }}
        >
          <Eye className="h-4 w-4" />
        </Button>
      )
    }
  ];

  const totalCommissions = mockCommissions.reduce((sum, c) => sum + c.netCommission, 0);
  const totalSales = mockCommissions.reduce((sum, c) => sum + c.totalSales, 0);
  const avgRate = mockCommissions.reduce((sum, c) => sum + c.commissionRate, 0) / mockCommissions.length;
  const pendingCount = mockCommissions.filter(c => c.status === 'pending').length;

  const simulatedCommission = (simulationValues.sales * simulationValues.rate / 100) + simulationValues.bonus;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Comissões de Vendas
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão e cálculo de comissões dos vendedores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary"
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
            >
              <option value="2026-01">Janeiro/2026</option>
              <option value="2025-12">Dezembro/2025</option>
              <option value="2025-11">Novembro/2025</option>
            </select>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button variant="primary">
              <Calculator className="h-4 w-4 mr-2" />
              Calcular Período
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <StatCard
            title="Total Comissões"
            value={totalCommissions.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Total Vendas"
            value={totalSales.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Taxa Média"
            value={`${avgRate.toFixed(1)}%`}
            icon={<Target className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Vendedores"
            value={mockCommissions.length.toString()}
            icon={<Users className="h-5 w-5" />}
          />
          <StatCard
            title="Pendentes"
            value={pendingCount.toString()}
            changeLabel="aguardando aprovação"
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
        </StatGrid>

        {/* Chart */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Evolução de Comissões vs Meta
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={commissionTrendData}>
                  <defs>
                    <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                  <XAxis dataKey="month" stroke="#64748b" />
                  <YAxis stroke="#64748b" tickFormatter={(v) => `R$ ${(v/1000)}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                    formatter={(value: number) => [value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), '']}
                  />
                  <Area
                    type="monotone"
                    dataKey="total"
                    name="Total Comissões"
                    stroke="#10b981"
                    fillOpacity={1}
                    fill="url(#colorTotal)"
                  />
                  <Area
                    type="monotone"
                    dataKey="meta"
                    name="Meta"
                    stroke="#6366f1"
                    strokeDasharray="5 5"
                    fill="none"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Content */}
        {activeTab === 'commissions' && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-text-primary">
                  Comissões do Período
                </h3>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                  <Input
                    placeholder="Buscar vendedor..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
              </div>
            </CardHeader>
            <CardBody className="p-0">
              <DataTable<Commission>
                data={mockCommissions.filter(c =>
                  c.salesperson.toLowerCase().includes(searchTerm.toLowerCase())
                )}
                columns={columns}
                keyExtractor={(row) => row.id}
              />
            </CardBody>
          </Card>
        )}

        {activeTab === 'ranking' && (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Ranking de Vendedores
              </h3>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                {rankingData.map((seller, index) => (
                  <motion.div
                    key={seller.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg"
                  >
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                      index === 0 ? 'bg-yellow-500/20 text-yellow-500' :
                      index === 1 ? 'bg-gray-400/20 text-gray-400' :
                      index === 2 ? 'bg-orange-500/20 text-orange-500' :
                      'bg-bg-secondary text-text-secondary'
                    }`}>
                      {index + 1}º
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-text-primary">{seller.name}</p>
                      <p className="text-sm text-text-secondary">
                        {seller.contractsCount} contratos | Taxa conversão: {seller.conversionRate}%
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-text-primary">
                        {seller.totalSales.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <p className="text-sm text-accent-success">
                        Comissão: {seller.totalCommission.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <div className={`flex items-center gap-1 ${seller.trend >= 0 ? 'text-accent-success' : 'text-accent-danger'}`}>
                      <TrendingUp className={`h-4 w-4 ${seller.trend < 0 ? 'rotate-180' : ''}`} />
                      <span className="font-medium">{Math.abs(seller.trend)}%</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'simulation' && (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Simulador de Comissões
              </h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Valor Total de Vendas
                    </label>
                    <Input
                      type="number"
                      value={simulationValues.sales}
                      onChange={(e) => setSimulationValues(prev => ({ ...prev, sales: Number(e.target.value) }))}
                      placeholder="100000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Taxa de Comissão (%)
                    </label>
                    <Input
                      type="number"
                      step="0.5"
                      value={simulationValues.rate}
                      onChange={(e) => setSimulationValues(prev => ({ ...prev, rate: Number(e.target.value) }))}
                      placeholder="5"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">
                      Bônus Adicional
                    </label>
                    <Input
                      type="number"
                      value={simulationValues.bonus}
                      onChange={(e) => setSimulationValues(prev => ({ ...prev, bonus: Number(e.target.value) }))}
                      placeholder="0"
                    />
                  </div>
                </div>
                <div className="flex flex-col items-center justify-center p-8 bg-bg-tertiary rounded-xl">
                  <p className="text-text-secondary mb-2">Comissão Estimada</p>
                  <p className="text-4xl font-bold text-accent-success">
                    {simulatedCommission.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                  <div className="mt-4 text-sm text-text-secondary">
                    <p>Base: {(simulationValues.sales * simulationValues.rate / 100).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</p>
                    {simulationValues.bonus > 0 && (
                      <p>+ Bônus: {simulationValues.bonus.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</p>
                    )}
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes da Comissão"
          size="lg"
        >
          {selectedCommission && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-white text-xl font-bold">
                  {selectedCommission.salesperson.split(' ').map(n => n[0]).slice(0, 2).join('')}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedCommission.salesperson}</h3>
                  <p className="text-text-secondary">{selectedCommission.period}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary">Total Vendas</p>
                  <p className="text-xl font-semibold text-text-primary">
                    {selectedCommission.totalSales.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-secondary">Contratos</p>
                  <p className="text-xl font-semibold text-text-primary">{selectedCommission.contractsCount}</p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between p-3 bg-bg-secondary rounded-lg">
                  <span className="text-text-secondary">Comissão Base ({selectedCommission.commissionRate}%)</span>
                  <span className="text-text-primary">
                    {selectedCommission.commissionValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </span>
                </div>
                {selectedCommission.bonuses > 0 && (
                  <div className="flex justify-between p-3 bg-accent-success/10 rounded-lg">
                    <span className="text-accent-success">+ Bônus</span>
                    <span className="text-accent-success">
                      {selectedCommission.bonuses.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </span>
                  </div>
                )}
                {selectedCommission.deductions > 0 && (
                  <div className="flex justify-between p-3 bg-accent-danger/10 rounded-lg">
                    <span className="text-accent-danger">- Deduções</span>
                    <span className="text-accent-danger">
                      {selectedCommission.deductions.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </span>
                  </div>
                )}
                <div className="flex justify-between p-4 bg-accent-primary/10 rounded-lg border border-accent-primary/30">
                  <span className="font-semibold text-text-primary">Total Líquido</span>
                  <span className="font-bold text-xl text-accent-success">
                    {selectedCommission.netCommission.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </span>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fechar
                </Button>
                {selectedCommission.status === 'pending' && (
                  <Button variant="primary">
                    Aprovar Comissão
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}

export default CommissionsPage;
