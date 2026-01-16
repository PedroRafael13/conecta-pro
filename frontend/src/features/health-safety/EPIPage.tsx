'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  HardHat,
  Shield,
  Package,
  Users,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Edit2,
  Trash2,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar,
  QrCode,
  FileText,
  History,
  RefreshCw,
  ArrowRight,
  ChevronDown
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { DataTable, Column } from '../../design-system/components/Table';
import { SimpleTabBar } from '../../design-system/components/Tabs';
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
  LineChart,
  Line
} from 'recharts';

// Types
interface EPI {
  id: string;
  code: string;
  name: string;
  category: 'cabeca' | 'olhos' | 'respiratorio' | 'auditivo' | 'maos' | 'pes' | 'corpo' | 'queda';
  ca: string; // Certificado de Aprovação
  caValidity: string;
  manufacturer: string;
  stockQuantity: number;
  minStock: number;
  unitPrice: number;
  lastPurchase: string;
  status: 'active' | 'low_stock' | 'expired_ca' | 'inactive';
}

interface EPIDelivery {
  id: string;
  epiId: string;
  epiName: string;
  employeeId: string;
  employeeName: string;
  employeeRole: string;
  sector: string;
  deliveryDate: string;
  quantity: number;
  reason: 'initial' | 'replacement' | 'damage' | 'lost';
  validityMonths: number;
  expirationDate: string;
  returnDate: string | null;
  status: 'active' | 'returned' | 'expired' | 'lost';
  signatureUrl: string | null;
}

// Mock Data
const mockEPIs: EPI[] = [
  {
    id: '1',
    code: 'EPI-001',
    name: 'Capacete de Segurança Classe A',
    category: 'cabeca',
    ca: '12345',
    caValidity: '2025-06-30',
    manufacturer: '3M do Brasil',
    stockQuantity: 45,
    minStock: 20,
    unitPrice: 35.90,
    lastPurchase: '2024-01-15',
    status: 'active'
  },
  {
    id: '2',
    code: 'EPI-002',
    name: 'Óculos de Proteção Ampla Visão',
    category: 'olhos',
    ca: '23456',
    caValidity: '2024-12-31',
    manufacturer: 'Carbografite',
    stockQuantity: 120,
    minStock: 50,
    unitPrice: 18.50,
    lastPurchase: '2024-02-01',
    status: 'active'
  },
  {
    id: '3',
    code: 'EPI-003',
    name: 'Respirador PFF2',
    category: 'respiratorio',
    ca: '34567',
    caValidity: '2024-08-15',
    manufacturer: '3M do Brasil',
    stockQuantity: 200,
    minStock: 100,
    unitPrice: 8.90,
    lastPurchase: '2024-02-10',
    status: 'active'
  },
  {
    id: '4',
    code: 'EPI-004',
    name: 'Protetor Auricular Tipo Plug',
    category: 'auditivo',
    ca: '45678',
    caValidity: '2025-03-20',
    manufacturer: '3M do Brasil',
    stockQuantity: 15,
    minStock: 50,
    unitPrice: 2.50,
    lastPurchase: '2024-01-20',
    status: 'low_stock'
  },
  {
    id: '5',
    code: 'EPI-005',
    name: 'Luva de Vaqueta',
    category: 'maos',
    ca: '56789',
    caValidity: '2024-03-01',
    manufacturer: 'Danny',
    stockQuantity: 80,
    minStock: 30,
    unitPrice: 22.00,
    lastPurchase: '2024-01-25',
    status: 'expired_ca'
  },
  {
    id: '6',
    code: 'EPI-006',
    name: 'Botina de Segurança com Bico de Aço',
    category: 'pes',
    ca: '67890',
    caValidity: '2025-09-30',
    manufacturer: 'Marluvas',
    stockQuantity: 35,
    minStock: 15,
    unitPrice: 89.90,
    lastPurchase: '2024-02-05',
    status: 'active'
  }
];

const mockDeliveries: EPIDelivery[] = [
  {
    id: '1',
    epiId: '1',
    epiName: 'Capacete de Segurança Classe A',
    employeeId: 'EMP-001',
    employeeName: 'João Silva',
    employeeRole: 'Operador de Produção',
    sector: 'Produção Industrial',
    deliveryDate: '2024-01-15',
    quantity: 1,
    reason: 'initial',
    validityMonths: 24,
    expirationDate: '2026-01-15',
    returnDate: null,
    status: 'active',
    signatureUrl: '/signatures/joao-silva.png'
  },
  {
    id: '2',
    epiId: '2',
    epiName: 'Óculos de Proteção Ampla Visão',
    employeeId: 'EMP-002',
    employeeName: 'Maria Santos',
    employeeRole: 'Técnica de Laboratório',
    sector: 'Laboratório Químico',
    deliveryDate: '2024-02-01',
    quantity: 1,
    reason: 'initial',
    validityMonths: 12,
    expirationDate: '2025-02-01',
    returnDate: null,
    status: 'active',
    signatureUrl: '/signatures/maria-santos.png'
  },
  {
    id: '3',
    epiId: '4',
    epiName: 'Protetor Auricular Tipo Plug',
    employeeId: 'EMP-003',
    employeeName: 'Pedro Oliveira',
    employeeRole: 'Operador de Máquinas',
    sector: 'Produção Industrial',
    deliveryDate: '2024-01-20',
    quantity: 5,
    reason: 'replacement',
    validityMonths: 1,
    expirationDate: '2024-02-20',
    returnDate: null,
    status: 'expired',
    signatureUrl: '/signatures/pedro-oliveira.png'
  },
  {
    id: '4',
    epiId: '6',
    epiName: 'Botina de Segurança com Bico de Aço',
    employeeId: 'EMP-004',
    employeeName: 'Ana Costa',
    employeeRole: 'Almoxarife',
    sector: 'Almoxarifado',
    deliveryDate: '2024-02-05',
    quantity: 1,
    reason: 'damage',
    validityMonths: 12,
    expirationDate: '2025-02-05',
    returnDate: null,
    status: 'active',
    signatureUrl: '/signatures/ana-costa.png'
  }
];

const categoryDistributionData = [
  { name: 'Cabeça', value: 15, color: '#f59e0b' },
  { name: 'Olhos', value: 20, color: '#3b82f6' },
  { name: 'Respiratório', value: 25, color: '#10b981' },
  { name: 'Auditivo', value: 18, color: '#8b5cf6' },
  { name: 'Mãos', value: 12, color: '#ef4444' },
  { name: 'Pés', value: 10, color: '#6366f1' }
];

const monthlyDeliveriesData = [
  { month: 'Set', entregas: 45, custo: 2800 },
  { month: 'Out', entregas: 52, custo: 3200 },
  { month: 'Nov', entregas: 38, custo: 2400 },
  { month: 'Dez', entregas: 65, custo: 4100 },
  { month: 'Jan', entregas: 78, custo: 4800 },
  { month: 'Fev', entregas: 42, custo: 2650 }
];

const tabs = [
  { value: 'inventory', label: 'Estoque de EPIs', icon: <Package className="h-4 w-4" /> },
  { value: 'deliveries', label: 'Entregas', icon: <Users className="h-4 w-4" /> },
  { value: 'expiring', label: 'Vencimentos', icon: <Calendar className="h-4 w-4" /> },
  { value: 'history', label: 'Histórico', icon: <History className="h-4 w-4" /> }
];

export function EPIPage() {
  const [activeTab, setActiveTab] = useState('inventory');
  const [searchTerm, setSearchTerm] = useState('');
  const [showDeliveryModal, setShowDeliveryModal] = useState(false);
  const [showEPIModal, setShowEPIModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const getCategoryInfo = (category: EPI['category']) => {
    const categories = {
      cabeca: { label: 'Cabeça', icon: HardHat, color: 'warning' as const },
      olhos: { label: 'Olhos/Face', icon: Eye, color: 'info' as const },
      respiratorio: { label: 'Respiratório', icon: Shield, color: 'success' as const },
      auditivo: { label: 'Auditivo', icon: Shield, color: 'info' as const },
      maos: { label: 'Mãos', icon: Shield, color: 'primary' as const },
      pes: { label: 'Pés', icon: Shield, color: 'warning' as const },
      corpo: { label: 'Corpo', icon: Shield, color: 'info' as const },
      queda: { label: 'Queda', icon: Shield, color: 'danger' as const }
    };
    return categories[category];
  };

  const getStatusInfo = (status: EPI['status']) => {
    const statuses = {
      active: { label: 'Ativo', color: 'success' as const },
      low_stock: { label: 'Estoque Baixo', color: 'warning' as const },
      expired_ca: { label: 'CA Vencido', color: 'danger' as const },
      inactive: { label: 'Inativo', color: 'info' as const }
    };
    return statuses[status];
  };

  const getDeliveryStatusInfo = (status: EPIDelivery['status']) => {
    const statuses = {
      active: { label: 'Em Uso', color: 'success' as const },
      returned: { label: 'Devolvido', color: 'info' as const },
      expired: { label: 'Vencido', color: 'warning' as const },
      lost: { label: 'Extraviado', color: 'danger' as const }
    };
    return statuses[status];
  };

  const getReasonLabel = (reason: EPIDelivery['reason']) => {
    const reasons = {
      initial: 'Entrega Inicial',
      replacement: 'Reposição',
      damage: 'Danificado',
      lost: 'Extraviado'
    };
    return reasons[reason];
  };

  const epiColumns: Column<EPI>[] = [
    {
      key: 'code',
      header: 'Código',
      sortable: true,
      render: (row) => (
        <span className="font-mono text-text-primary">{row.code}</span>
      )
    },
    {
      key: 'name',
      header: 'Equipamento',
      sortable: true,
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-secondary">{row.manufacturer}</p>
        </div>
      )
    },
    {
      key: 'category',
      header: 'Categoria',
      sortable: true,
      render: (row) => {
        const info = getCategoryInfo(row.category);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'ca',
      header: 'CA',
      sortable: true,
      render: (row) => {
        const isExpired = new Date(row.caValidity) < new Date();
        return (
          <div>
            <span className="font-mono text-text-primary">{row.ca}</span>
            <p className={`text-xs ${isExpired ? 'text-accent-danger' : 'text-text-secondary'}`}>
              Val: {new Date(row.caValidity).toLocaleDateString('pt-BR')}
            </p>
          </div>
        );
      }
    },
    {
      key: 'stockQuantity',
      header: 'Estoque',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <span className={`font-medium ${
            row.stockQuantity <= row.minStock ? 'text-accent-danger' : 'text-text-primary'
          }`}>
            {row.stockQuantity}
          </span>
          <span className="text-text-secondary text-xs">/ mín. {row.minStock}</span>
        </div>
      )
    },
    {
      key: 'unitPrice',
      header: 'Preço Unit.',
      sortable: true,
      render: (row) => (
        <span className="text-text-primary">
          {row.unitPrice.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row) => {
        const info = getStatusInfo(row.status);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <QrCode className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const deliveryColumns: Column<EPIDelivery>[] = [
    {
      key: 'deliveryDate',
      header: 'Data',
      sortable: true,
      render: (row) => (
        <span className="text-text-primary">
          {new Date(row.deliveryDate).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      key: 'employeeName',
      header: 'Funcionário',
      sortable: true,
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.employeeName}</p>
          <p className="text-xs text-text-secondary">{row.employeeRole}</p>
        </div>
      )
    },
    {
      key: 'sector',
      header: 'Setor',
      sortable: true
    },
    {
      key: 'epiName',
      header: 'EPI',
      sortable: true,
      render: (row) => (
        <p className="text-text-primary max-w-xs truncate">{row.epiName}</p>
      )
    },
    {
      key: 'quantity',
      header: 'Qtd',
      sortable: true,
      render: (row) => (
        <span className="font-medium text-text-primary">{row.quantity}</span>
      )
    },
    {
      key: 'reason',
      header: 'Motivo',
      render: (row) => (
        <span className="text-text-secondary text-sm">{getReasonLabel(row.reason)}</span>
      )
    },
    {
      key: 'expirationDate',
      header: 'Validade',
      sortable: true,
      render: (row) => {
        const isExpired = new Date(row.expirationDate) < new Date();
        return (
          <span className={isExpired ? 'text-accent-danger' : 'text-text-primary'}>
            {new Date(row.expirationDate).toLocaleDateString('pt-BR')}
          </span>
        );
      }
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row) => {
        const info = getDeliveryStatusInfo(row.status);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <FileText className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const filteredEPIs = mockEPIs.filter(epi => {
    const matchesSearch = epi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         epi.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || epi.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const filteredDeliveries = mockDeliveries.filter(delivery =>
    delivery.employeeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    delivery.epiName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Compute expiring items
  const expiringItems = mockDeliveries.filter(d => {
    const expDate = new Date(d.expirationDate);
    const today = new Date();
    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(today.getDate() + 30);
    return d.status === 'active' && expDate <= thirtyDaysFromNow;
  });

  const expiringCAs = mockEPIs.filter(epi => {
    const expDate = new Date(epi.caValidity);
    const today = new Date();
    const sixtyDaysFromNow = new Date();
    sixtyDaysFromNow.setDate(today.getDate() + 60);
    return expDate <= sixtyDaysFromNow;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-text-primary">
            Gestão de EPIs
          </h1>
          <p className="text-text-secondary mt-1">
            Equipamentos de Proteção Individual - NR-6
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Ficha de EPI
          </Button>
          <Button variant="primary" onClick={() => setShowDeliveryModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Entrega
          </Button>
        </div>
      </div>

      {/* Stats */}
      <StatGrid columns={5}>
        <StatCard
          title="Tipos de EPIs"
          value="24"
          changeLabel="cadastrados"
          icon={<Package className="h-5 w-5" />}
        />
        <StatCard
          title="Entregas no Mês"
          value="42"
          change={12}
          changeLabel="vs mês anterior"
          icon={<Users className="h-5 w-5" />}
        />
        <StatCard
          title="Estoque Baixo"
          value="3"
          changeLabel="itens críticos"
          icon={<AlertTriangle className="h-5 w-5" />}
          iconColor="warning"
        />
        <StatCard
          title="CAs Vencendo"
          value="2"
          changeLabel="próximos 60 dias"
          icon={<Calendar className="h-5 w-5" />}
          iconColor="danger"
        />
        <StatCard
          title="Custo Mensal"
          value="R$ 4.800"
          change={-8}
          changeLabel="economia"
          icon={<Shield className="h-5 w-5" />}
          iconColor="success"
        />
      </StatGrid>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Distribuição por Categoria
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {categoryDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Monthly Deliveries */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Entregas e Custos Mensais
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyDeliveriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                  <XAxis dataKey="month" stroke="#64748b" />
                  <YAxis yAxisId="left" stroke="#64748b" />
                  <YAxis yAxisId="right" orientation="right" stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar yAxisId="left" dataKey="entregas" name="Entregas" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Line yAxisId="right" type="monotone" dataKey="custo" name="Custo (R$)" stroke="#10b981" strokeWidth={2} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Tabs */}
      <SimpleTabBar
        tabs={tabs}
        value={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Content */}
      {activeTab === 'inventory' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Estoque de EPIs
              </h3>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                  <Input
                    placeholder="Buscar EPIs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <select
                  className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary text-sm"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="all">Todas categorias</option>
                  <option value="cabeca">Cabeça</option>
                  <option value="olhos">Olhos/Face</option>
                  <option value="respiratorio">Respiratório</option>
                  <option value="auditivo">Auditivo</option>
                  <option value="maos">Mãos</option>
                  <option value="pes">Pés</option>
                  <option value="corpo">Corpo</option>
                  <option value="queda">Queda</option>
                </select>
                <Button variant="outline" onClick={() => setShowEPIModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo EPI
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <DataTable<EPI>
              data={filteredEPIs}
              columns={epiColumns}
              keyExtractor={(row) => row.id}
            />
          </CardBody>
        </Card>
      )}

      {activeTab === 'deliveries' && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Registro de Entregas
              </h3>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                  <Input
                    placeholder="Buscar entregas..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <Button variant="primary" onClick={() => setShowDeliveryModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Nova Entrega
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <DataTable<EPIDelivery>
              data={filteredDeliveries}
              columns={deliveryColumns}
              keyExtractor={(row) => row.id}
            />
          </CardBody>
        </Card>
      )}

      {activeTab === 'expiring' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* EPIs vencendo */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-accent-warning" />
                <h3 className="text-lg font-semibold text-text-primary">
                  EPIs Vencendo (30 dias)
                </h3>
              </div>
            </CardHeader>
            <CardBody className="space-y-3">
              {expiringItems.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-accent-success mx-auto mb-3" />
                  <p className="text-text-secondary">Nenhum EPI vencendo nos próximos 30 dias</p>
                </div>
              ) : (
                expiringItems.map((item, index) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-4 bg-bg-tertiary rounded-lg border border-accent-warning/30"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-text-primary">{item.employeeName}</p>
                        <p className="text-sm text-text-secondary">{item.epiName}</p>
                        <p className="text-xs text-text-secondary mt-1">
                          Entregue em {new Date(item.deliveryDate).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-accent-warning font-medium">
                          Vence: {new Date(item.expirationDate).toLocaleDateString('pt-BR')}
                        </p>
                        <Button variant="outline" size="sm" className="mt-2">
                          <RefreshCw className="h-4 w-4 mr-1" />
                          Renovar
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </CardBody>
          </Card>

          {/* CAs vencendo */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-accent-danger" />
                <h3 className="text-lg font-semibold text-text-primary">
                  CAs Vencendo (60 dias)
                </h3>
              </div>
            </CardHeader>
            <CardBody className="space-y-3">
              {expiringCAs.map((epi, index) => (
                <motion.div
                  key={epi.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-bg-tertiary rounded-lg border border-accent-danger/30"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-text-primary">{epi.name}</p>
                      <p className="text-sm text-text-secondary">
                        CA: {epi.ca} | {epi.manufacturer}
                      </p>
                      <p className="text-xs text-text-secondary mt-1">
                        Estoque atual: {epi.stockQuantity} unidades
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${
                        new Date(epi.caValidity) < new Date() ? 'text-accent-danger' : 'text-accent-warning'
                      }`}>
                        {new Date(epi.caValidity) < new Date() ? 'VENCIDO' : 'Vence:'} {new Date(epi.caValidity).toLocaleDateString('pt-BR')}
                      </p>
                      <Badge
                        variant={new Date(epi.caValidity) < new Date() ? 'danger' : 'warning'}
                        size="sm"
                        className="mt-2"
                      >
                        {new Date(epi.caValidity) < new Date() ? 'Providenciar substituição' : 'Atualizar CA'}
                      </Badge>
                    </div>
                  </div>
                </motion.div>
              ))}
            </CardBody>
          </Card>
        </div>
      )}

      {activeTab === 'history' && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Histórico de Movimentações
            </h3>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              {[
                { date: '2024-02-15 14:32', action: 'Entrega', user: 'Maria Admin', description: 'Entrega de Capacete de Segurança para João Silva', type: 'delivery' },
                { date: '2024-02-15 10:15', action: 'Entrada', user: 'Sistema', description: 'Entrada de estoque: 50 unidades de Respirador PFF2', type: 'stock_in' },
                { date: '2024-02-14 16:45', action: 'Devolução', user: 'Maria Admin', description: 'Devolução de Luva de Vaqueta por Pedro Oliveira (danificada)', type: 'return' },
                { date: '2024-02-14 09:20', action: 'Alerta', user: 'Sistema', description: 'Estoque baixo: Protetor Auricular Tipo Plug (15 unidades)', type: 'alert' },
                { date: '2024-02-13 11:30', action: 'Cadastro', user: 'Maria Admin', description: 'Novo EPI cadastrado: Óculos de Proteção UV', type: 'new' }
              ].map((event, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-4 p-4 bg-bg-tertiary rounded-lg"
                >
                  <div className={`p-2 rounded-lg ${
                    event.type === 'delivery' ? 'bg-accent-success/20' :
                    event.type === 'stock_in' ? 'bg-accent-info/20' :
                    event.type === 'return' ? 'bg-accent-warning/20' :
                    event.type === 'alert' ? 'bg-accent-danger/20' :
                    'bg-accent-primary/20'
                  }`}>
                    {event.type === 'delivery' && <ArrowRight className="h-5 w-5 text-accent-success" />}
                    {event.type === 'stock_in' && <Package className="h-5 w-5 text-accent-info" />}
                    {event.type === 'return' && <RefreshCw className="h-5 w-5 text-accent-warning" />}
                    {event.type === 'alert' && <AlertTriangle className="h-5 w-5 text-accent-danger" />}
                    {event.type === 'new' && <Plus className="h-5 w-5 text-accent-primary" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-text-primary">{event.action}</span>
                      <span className="text-xs text-text-secondary">{event.date}</span>
                    </div>
                    <p className="text-sm text-text-secondary mt-1">{event.description}</p>
                    <p className="text-xs text-text-secondary mt-1">Por: {event.user}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Delivery Modal */}
      <Modal
        isOpen={showDeliveryModal}
        onClose={() => setShowDeliveryModal(false)}
        title="Nova Entrega de EPI"
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Funcionário *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Selecione...</option>
                <option value="1">João Silva - Operador</option>
                <option value="2">Maria Santos - Técnica</option>
                <option value="3">Pedro Oliveira - Operador</option>
                <option value="4">Ana Costa - Almoxarife</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                EPI *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Selecione...</option>
                {mockEPIs.map(epi => (
                  <option key={epi.id} value={epi.id}>
                    {epi.name} (Estoque: {epi.stockQuantity})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Quantidade *
              </label>
              <Input type="number" placeholder="1" defaultValue={1} />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Motivo *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="initial">Entrega Inicial</option>
                <option value="replacement">Reposição</option>
                <option value="damage">Danificado</option>
                <option value="lost">Extraviado</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Validade (meses)
              </label>
              <Input type="number" placeholder="12" defaultValue={12} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Observações
            </label>
            <textarea
              className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
              rows={3}
              placeholder="Observações sobre a entrega..."
            />
          </div>

          <div className="p-4 bg-bg-tertiary rounded-lg">
            <p className="text-sm text-text-secondary mb-2">
              Assinatura Digital
            </p>
            <div className="h-32 border-2 border-dashed border-border-default rounded-lg flex items-center justify-center">
              <p className="text-text-secondary">Área para assinatura digital</p>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="ghost" onClick={() => setShowDeliveryModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              <CheckCircle className="h-4 w-4 mr-2" />
              Registrar Entrega
            </Button>
          </div>
        </div>
      </Modal>

      {/* EPI Modal */}
      <Modal
        isOpen={showEPIModal}
        onClose={() => setShowEPIModal(false)}
        title="Novo EPI"
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Código *
              </label>
              <Input placeholder="EPI-XXX" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Categoria *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Selecione...</option>
                <option value="cabeca">Proteção da Cabeça</option>
                <option value="olhos">Proteção dos Olhos/Face</option>
                <option value="respiratorio">Proteção Respiratória</option>
                <option value="auditivo">Proteção Auditiva</option>
                <option value="maos">Proteção das Mãos</option>
                <option value="pes">Proteção dos Pés</option>
                <option value="corpo">Proteção do Corpo</option>
                <option value="queda">Proteção contra Quedas</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Nome do Equipamento *
            </label>
            <Input placeholder="Ex: Capacete de Segurança Classe A" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Fabricante *
              </label>
              <Input placeholder="Ex: 3M do Brasil" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                CA (Certificado de Aprovação) *
              </label>
              <Input placeholder="Ex: 12345" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Validade do CA *
              </label>
              <Input type="date" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Estoque Mínimo
              </label>
              <Input type="number" placeholder="0" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Preço Unitário
              </label>
              <Input type="number" step="0.01" placeholder="0,00" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-secondary mb-1">
              Descrição / Especificações
            </label>
            <textarea
              className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
              rows={3}
              placeholder="Especificações técnicas do EPI..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="ghost" onClick={() => setShowEPIModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary">
              Cadastrar EPI
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default EPIPage;
