'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Search,
  Plus,
  Download,
  Upload,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  DollarSign,
  TrendingUp,
  Eye,
  Printer,
  Send,
  RefreshCw,
  FileCheck,
  FileMinus,
  Building2,
  Calculator,
  XCircle,
  ArrowUpRight,
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
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Types
interface Invoice {
  id: string;
  number: string;
  series: string;
  type: 'nfe' | 'nfse' | 'nfce';
  client: string;
  clientCnpj: string;
  value: number;
  issDate: string;
  status: 'authorized' | 'cancelled' | 'pending' | 'rejected' | 'inutilized';
  protocol: string | null;
}

interface TaxObligation {
  id: string;
  name: string;
  type: 'monthly' | 'quarterly' | 'annual';
  reference: string;
  dueDate: string;
  value: number | null;
  status: 'pending' | 'processing' | 'submitted' | 'overdue';
  description: string;
}

interface TaxGuide {
  id: string;
  type: 'darf' | 'gps' | 'dare' | 'gare' | 'gnre';
  tax: string;
  reference: string;
  dueDate: string;
  value: number;
  status: 'pending' | 'paid' | 'overdue';
  barcode: string;
}

// Mock Data
const taxesByMonth = [
  { month: 'Set', pis: 8500, cofins: 39200, iss: 12000, icms: 0 },
  { month: 'Out', pis: 9200, cofins: 42400, iss: 13500, icms: 0 },
  { month: 'Nov', pis: 8800, cofins: 40600, iss: 12800, icms: 0 },
  { month: 'Dez', pis: 11200, cofins: 51700, iss: 15800, icms: 0 },
  { month: 'Jan', pis: 7500, cofins: 34600, iss: 10500, icms: 0 },
];

const invoices: Invoice[] = [
  {
    id: '1',
    number: '12458',
    series: '1',
    type: 'nfse',
    client: 'Shopping Center Norte',
    clientCnpj: '12.345.678/0001-90',
    value: 185000.00,
    issDate: '2026-01-15',
    status: 'authorized',
    protocol: '135260000012458',
  },
  {
    id: '2',
    number: '12457',
    series: '1',
    type: 'nfse',
    client: 'Hospital São Lucas',
    clientCnpj: '98.765.432/0001-10',
    value: 125000.00,
    issDate: '2026-01-14',
    status: 'authorized',
    protocol: '135260000012457',
  },
  {
    id: '3',
    number: '12456',
    series: '1',
    type: 'nfse',
    client: 'Tech Park Empresarial',
    clientCnpj: '45.678.901/0001-23',
    value: 95000.00,
    issDate: '2026-01-13',
    status: 'authorized',
    protocol: '135260000012456',
  },
  {
    id: '4',
    number: '12455',
    series: '1',
    type: 'nfse',
    client: 'Condomínio Residencial',
    clientCnpj: '56.789.012/0001-34',
    value: 45000.00,
    issDate: '2026-01-12',
    status: 'cancelled',
    protocol: null,
  },
  {
    id: '5',
    number: '12459',
    series: '1',
    type: 'nfse',
    client: 'Empresa ABC',
    clientCnpj: '67.890.123/0001-45',
    value: 75000.00,
    issDate: '2026-01-15',
    status: 'pending',
    protocol: null,
  },
];

const obligations: TaxObligation[] = [
  {
    id: '1',
    name: 'SPED Fiscal',
    type: 'monthly',
    reference: 'Janeiro/2026',
    dueDate: '2026-02-20',
    value: null,
    status: 'pending',
    description: 'Escrituração Fiscal Digital - ICMS/IPI',
  },
  {
    id: '2',
    name: 'EFD-Contribuições',
    type: 'monthly',
    reference: 'Janeiro/2026',
    dueDate: '2026-02-15',
    value: null,
    status: 'processing',
    description: 'PIS/PASEP e COFINS',
  },
  {
    id: '3',
    name: 'DCTF',
    type: 'monthly',
    reference: 'Dezembro/2025',
    dueDate: '2026-01-25',
    value: null,
    status: 'submitted',
    description: 'Declaração de Débitos e Créditos Tributários',
  },
  {
    id: '4',
    name: 'eSocial',
    type: 'monthly',
    reference: 'Janeiro/2026',
    dueDate: '2026-02-07',
    value: null,
    status: 'pending',
    description: 'Eventos de folha de pagamento',
  },
  {
    id: '5',
    name: 'DIRF',
    type: 'annual',
    reference: '2025',
    dueDate: '2026-02-28',
    value: null,
    status: 'pending',
    description: 'Declaração do Imposto Retido na Fonte',
  },
];

const guides: TaxGuide[] = [
  {
    id: '1',
    type: 'darf',
    tax: 'IRRF',
    reference: 'Janeiro/2026',
    dueDate: '2026-01-20',
    value: 28500.00,
    status: 'paid',
    barcode: '23793.38128 60000.100045 18000.000003 1 90980000028500',
  },
  {
    id: '2',
    type: 'darf',
    tax: 'PIS',
    reference: 'Janeiro/2026',
    dueDate: '2026-01-25',
    value: 7500.00,
    status: 'pending',
    barcode: '23793.38128 60000.100045 18000.000004 1 90980000007500',
  },
  {
    id: '3',
    type: 'darf',
    tax: 'COFINS',
    reference: 'Janeiro/2026',
    dueDate: '2026-01-25',
    value: 34600.00,
    status: 'pending',
    barcode: '23793.38128 60000.100045 18000.000005 1 90980000034600',
  },
  {
    id: '4',
    type: 'gps',
    tax: 'INSS',
    reference: 'Janeiro/2026',
    dueDate: '2026-01-20',
    value: 185000.00,
    status: 'paid',
    barcode: '85890000001 85000018500 00000000000 12345678901234',
  },
  {
    id: '5',
    type: 'dare',
    tax: 'ISS',
    reference: 'Janeiro/2026',
    dueDate: '2026-01-15',
    value: 10500.00,
    status: 'overdue',
    barcode: '85860000001 05000010500 00000000000 12345678901234',
  },
];

const invoiceStatusConfig = {
  authorized: { label: 'Autorizada', color: 'success' as const },
  cancelled: { label: 'Cancelada', color: 'danger' as const },
  pending: { label: 'Pendente', color: 'warning' as const },
  rejected: { label: 'Rejeitada', color: 'danger' as const },
  inutilized: { label: 'Inutilizada', color: 'neutral' as const },
};

const obligationStatusConfig = {
  pending: { label: 'Pendente', color: 'warning' as const },
  processing: { label: 'Em Processamento', color: 'info' as const },
  submitted: { label: 'Entregue', color: 'success' as const },
  overdue: { label: 'Atrasada', color: 'danger' as const },
};

const guideStatusConfig = {
  pending: { label: 'A Pagar', color: 'warning' as const },
  paid: { label: 'Paga', color: 'success' as const },
  overdue: { label: 'Vencida', color: 'danger' as const },
};

const typeLabels = {
  nfe: 'NF-e',
  nfse: 'NFS-e',
  nfce: 'NFC-e',
};

const guideTypeLabels = {
  darf: 'DARF',
  gps: 'GPS',
  dare: 'DARE',
  gare: 'GARE',
  gnre: 'GNRE',
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

const invoiceColumns: Column<Invoice>[] = [
  {
    key: 'number',
    header: 'Número',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.number}</p>
        <p className="text-xs text-text-muted">Série {row.series} • {typeLabels[row.type]}</p>
      </div>
    ),
  },
  {
    key: 'client',
    header: 'Cliente',
    render: (row) => (
      <div>
        <p className="text-text-primary">{row.client}</p>
        <p className="text-xs text-text-muted">{row.clientCnpj}</p>
      </div>
    ),
  },
  {
    key: 'value',
    header: 'Valor',
    render: (row) => <span className="font-medium">{formatCurrency(row.value)}</span>,
  },
  {
    key: 'issDate',
    header: 'Emissão',
    render: (row) => <span className="text-sm">{new Date(row.issDate).toLocaleDateString('pt-BR')}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = invoiceStatusConfig[row.status];
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
        {row.status === 'authorized' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Imprimir DANFE">
              <Printer className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Download XML">
              <Download className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Enviar por e-mail">
              <Send className="w-4 h-4" />
            </Button>
          </>
        )}
        {row.status === 'pending' && (
          <Button variant="primary" size="sm" leftIcon={<Send className="w-3 h-3" />}>
            Transmitir
          </Button>
        )}
      </div>
    ),
  },
];

const obligationColumns: Column<TaxObligation>[] = [
  {
    key: 'name',
    header: 'Obrigação',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 bg-bg-tertiary rounded-lg">
          <FileText className="w-5 h-5 text-text-muted" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.description}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'reference',
    header: 'Referência',
    render: (row) => <span className="text-sm">{row.reference}</span>,
  },
  {
    key: 'dueDate',
    header: 'Vencimento',
    render: (row) => {
      const isOverdue = new Date(row.dueDate) < new Date() && row.status !== 'submitted';
      return (
        <span className={`text-sm ${isOverdue ? 'text-accent-danger font-medium' : ''}`}>
          {new Date(row.dueDate).toLocaleDateString('pt-BR')}
        </span>
      );
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = obligationStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        {row.status === 'pending' && (
          <Button variant="primary" size="sm" leftIcon={<Upload className="w-3 h-3" />}>
            Gerar
          </Button>
        )}
        {row.status === 'submitted' && (
          <Button variant="ghost" size="icon-sm" title="Download">
            <Download className="w-4 h-4" />
          </Button>
        )}
      </div>
    ),
  },
];

const guideColumns: Column<TaxGuide>[] = [
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => <Badge variant="info">{guideTypeLabels[row.type]}</Badge>,
  },
  {
    key: 'tax',
    header: 'Tributo',
    render: (row) => <span className="font-medium text-text-primary">{row.tax}</span>,
  },
  {
    key: 'reference',
    header: 'Referência',
    render: (row) => <span className="text-sm">{row.reference}</span>,
  },
  {
    key: 'dueDate',
    header: 'Vencimento',
    render: (row) => {
      const isOverdue = row.status === 'overdue';
      return (
        <span className={`text-sm ${isOverdue ? 'text-accent-danger font-medium' : ''}`}>
          {new Date(row.dueDate).toLocaleDateString('pt-BR')}
        </span>
      );
    },
  },
  {
    key: 'value',
    header: 'Valor',
    render: (row) => <span className="font-medium">{formatCurrency(row.value)}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = guideStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        {row.status !== 'paid' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Copiar código de barras">
              <FileCheck className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Imprimir">
              <Printer className="w-4 h-4" />
            </Button>
          </>
        )}
      </div>
    ),
  },
];

export function FiscalPage() {
  const [selectedTab, setSelectedTab] = useState('invoices');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Stats
  const invoicedThisMonth = invoices.filter(i => i.status === 'authorized').reduce((acc, i) => acc + i.value, 0);
  const pendingInvoices = invoices.filter(i => i.status === 'pending').length;
  const pendingObligations = obligations.filter(o => o.status === 'pending' || o.status === 'overdue').length;
  const pendingGuides = guides.filter(g => g.status === 'pending' || g.status === 'overdue').reduce((acc, g) => acc + g.value, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Fiscal e Tributário
            </h1>
            <p className="text-text-secondary mt-1">
              Notas fiscais, obrigações e guias de recolhimento
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
              Emitir NF
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Faturado no Mês"
              value={formatCurrency(invoicedThisMonth)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
              trend="up"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="NF Pendentes"
              value={pendingInvoices}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Obrigações Pendentes"
              value={pendingObligations}
              icon={<FileText className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Guias a Pagar"
              value={formatCurrency(pendingGuides)}
              icon={<Calculator className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
        </StatGrid>

        {/* Tax Chart */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">Impostos por Mês</h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={taxesByMonth}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }}
                      formatter={(value: number) => [formatCurrency(value), '']}
                    />
                    <Bar dataKey="pis" name="PIS" fill="#6366f1" radius={[4, 4, 0, 0]} stackId="a" />
                    <Bar dataKey="cofins" name="COFINS" fill="#8b5cf6" radius={[0, 0, 0, 0]} stackId="a" />
                    <Bar dataKey="iss" name="ISS" fill="#3b82f6" radius={[0, 0, 0, 0]} stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </motion.div>

        {/* Overdue Alert */}
        {guides.some(g => g.status === 'overdue') && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card className="border-accent-danger/30 bg-accent-danger/5">
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent-danger/20 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-accent-danger" />
                    </div>
                    <div>
                      <h4 className="font-medium text-text-primary">Guias Vencidas</h4>
                      <p className="text-sm text-text-secondary">
                        Existem guias de recolhimento com vencimento em atraso
                      </p>
                    </div>
                  </div>
                  <Button variant="danger" size="sm">
                    Ver Guias
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
                { value: 'invoices', label: 'Notas Fiscais' },
                { value: 'obligations', label: 'Obrigações Acessórias' },
                { value: 'guides', label: 'Guias de Recolhimento' },
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
                {selectedTab === 'invoices' && (
                  <>
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Tipos' },
                        { value: 'nfse', label: 'NFS-e' },
                        { value: 'nfe', label: 'NF-e' },
                        { value: 'nfce', label: 'NFC-e' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-36"
                    />
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Status' },
                        { value: 'authorized', label: 'Autorizadas' },
                        { value: 'pending', label: 'Pendentes' },
                        { value: 'cancelled', label: 'Canceladas' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-40"
                    />
                  </>
                )}
                {selectedTab === 'guides' && (
                  <Select
                    options={[
                      { value: 'all', label: 'Todos Status' },
                      { value: 'pending', label: 'A Pagar' },
                      { value: 'paid', label: 'Pagas' },
                      { value: 'overdue', label: 'Vencidas' },
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-40"
                  />
                )}
              </div>
            </CardBody>
            <CardBody className="p-0">
              {selectedTab === 'invoices' ? (
                <DataTable
                  columns={invoiceColumns}
                  data={invoices}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'obligations' ? (
                <DataTable
                  columns={obligationColumns}
                  data={obligations}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <DataTable
                  columns={guideColumns}
                  data={guides}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Invoice Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Emitir Nota Fiscal"
          description="Preencha os dados para emissão da NF"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Emitir NF
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Tipo de Nota"
              options={[
                { value: 'nfse', label: 'NFS-e - Nota Fiscal de Serviço' },
                { value: 'nfe', label: 'NF-e - Nota Fiscal Eletrônica' },
                { value: 'nfce', label: 'NFC-e - Nota Fiscal Consumidor' },
              ]}
              value="nfse"
              onChange={() => {}}
            />
            <Select
              label="Cliente"
              options={[
                { value: '1', label: 'Shopping Center Norte' },
                { value: '2', label: 'Hospital São Lucas' },
                { value: '3', label: 'Tech Park Empresarial' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o cliente..."
            />
            <Select
              label="Contrato"
              options={[
                { value: '1', label: 'CTR-2025-001 - Vigilância Patrimonial' },
                { value: '2', label: 'CTR-2025-002 - Portaria 24h' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o contrato..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Competência" type="month" />
              <Input label="Valor dos Serviços" type="number" placeholder="R$ 0,00" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Descrição dos Serviços</label>
              <textarea
                className="w-full h-24 px-3 py-2 bg-bg-tertiary border border-border-default rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent"
                placeholder="Descreva os serviços prestados..."
              />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="text-sm font-medium text-text-primary mb-2">Tributos Calculados</h4>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-text-muted">ISS (5%)</p>
                  <p className="font-medium">R$ 0,00</p>
                </div>
                <div>
                  <p className="text-text-muted">PIS (0,65%)</p>
                  <p className="font-medium">R$ 0,00</p>
                </div>
                <div>
                  <p className="text-text-muted">COFINS (3%)</p>
                  <p className="font-medium">R$ 0,00</p>
                </div>
              </div>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
