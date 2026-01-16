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
  Modal,
  Select
} from '@/design-system/components';
import type { Column, SelectOption } from '@/design-system/components';
import {
  Building2,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  CreditCard,
  ArrowUpRight,
  ArrowDownLeft,
  Link,
  Link2Off,
  Eye,
  Settings,
  Trash2,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Calendar,
  DollarSign,
  Wallet,
  PiggyBank
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';

// Types
interface BankConnection {
  id: string;
  bankCode: string;
  bankName: string;
  bankLogo: string;
  status: 'connected' | 'disconnected' | 'pending' | 'error';
  consentId: string;
  consentExpiry: string;
  accountsCount: number;
  lastSync: string;
  autoSync: boolean;
  syncInterval: number;
  createdAt: string;
}

interface BankAccount {
  id: string;
  bankId: string;
  bankName: string;
  accountType: 'checking' | 'savings' | 'investment' | 'credit';
  accountNumber: string;
  agency: string;
  balance: number;
  availableBalance: number;
  currency: string;
  lastTransaction: string;
  status: 'active' | 'inactive' | 'blocked';
}

interface Transaction {
  id: string;
  accountId: string;
  accountName: string;
  bankName: string;
  type: 'credit' | 'debit';
  category: string;
  description: string;
  amount: number;
  balance: number;
  date: string;
  status: 'completed' | 'pending' | 'canceled';
  counterparty?: string;
}

// Mock data
const mockConnections: BankConnection[] = [
  {
    id: '1',
    bankCode: '001',
    bankName: 'Banco do Brasil',
    bankLogo: '/banks/bb.png',
    status: 'connected',
    consentId: 'urn:bancocentral:C1DD33123',
    consentExpiry: '2024-06-15',
    accountsCount: 3,
    lastSync: '2024-01-15T08:30:00',
    autoSync: true,
    syncInterval: 30,
    createdAt: '2023-06-01'
  },
  {
    id: '2',
    bankCode: '341',
    bankName: 'Itaú Unibanco',
    bankLogo: '/banks/itau.png',
    status: 'connected',
    consentId: 'urn:bancocentral:C2DD44234',
    consentExpiry: '2024-07-20',
    accountsCount: 2,
    lastSync: '2024-01-15T08:25:00',
    autoSync: true,
    syncInterval: 60,
    createdAt: '2023-07-15'
  },
  {
    id: '3',
    bankCode: '033',
    bankName: 'Santander',
    bankLogo: '/banks/santander.png',
    status: 'connected',
    consentId: 'urn:bancocentral:C3DD55345',
    consentExpiry: '2024-05-10',
    accountsCount: 2,
    lastSync: '2024-01-15T08:20:00',
    autoSync: true,
    syncInterval: 30,
    createdAt: '2023-08-20'
  },
  {
    id: '4',
    bankCode: '237',
    bankName: 'Bradesco',
    bankLogo: '/banks/bradesco.png',
    status: 'error',
    consentId: 'urn:bancocentral:C4DD66456',
    consentExpiry: '2024-04-01',
    accountsCount: 3,
    lastSync: '2024-01-14T18:00:00',
    autoSync: true,
    syncInterval: 30,
    createdAt: '2023-09-10'
  },
  {
    id: '5',
    bankCode: '260',
    bankName: 'Nubank',
    bankLogo: '/banks/nubank.png',
    status: 'pending',
    consentId: '',
    consentExpiry: '',
    accountsCount: 0,
    lastSync: '',
    autoSync: false,
    syncInterval: 60,
    createdAt: '2024-01-10'
  }
];

const mockAccounts: BankAccount[] = [
  {
    id: 'ACC001',
    bankId: '1',
    bankName: 'Banco do Brasil',
    accountType: 'checking',
    accountNumber: '12345-6',
    agency: '1234-5',
    balance: 125678.90,
    availableBalance: 120000.00,
    currency: 'BRL',
    lastTransaction: '2024-01-15T08:30:00',
    status: 'active'
  },
  {
    id: 'ACC002',
    bankId: '1',
    bankName: 'Banco do Brasil',
    accountType: 'savings',
    accountNumber: '12345-7',
    agency: '1234-5',
    balance: 45000.00,
    availableBalance: 45000.00,
    currency: 'BRL',
    lastTransaction: '2024-01-10T14:20:00',
    status: 'active'
  },
  {
    id: 'ACC003',
    bankId: '2',
    bankName: 'Itaú Unibanco',
    accountType: 'checking',
    accountNumber: '98765-4',
    agency: '4567-8',
    balance: 89234.56,
    availableBalance: 85000.00,
    currency: 'BRL',
    lastTransaction: '2024-01-15T07:45:00',
    status: 'active'
  },
  {
    id: 'ACC004',
    bankId: '3',
    bankName: 'Santander',
    accountType: 'checking',
    accountNumber: '54321-0',
    agency: '7890-1',
    balance: 67890.12,
    availableBalance: 60000.00,
    currency: 'BRL',
    lastTransaction: '2024-01-14T16:30:00',
    status: 'active'
  },
  {
    id: 'ACC005',
    bankId: '4',
    bankName: 'Bradesco',
    accountType: 'investment',
    accountNumber: '11111-1',
    agency: '2222-2',
    balance: 250000.00,
    availableBalance: 0,
    currency: 'BRL',
    lastTransaction: '2024-01-01T00:00:00',
    status: 'inactive'
  }
];

const mockTransactions: Transaction[] = [
  {
    id: 'TRX001',
    accountId: 'ACC001',
    accountName: 'C/C Banco do Brasil',
    bankName: 'Banco do Brasil',
    type: 'credit',
    category: 'Recebimento',
    description: 'TED Recebido - Pagamento NF 1234',
    amount: 15000.00,
    balance: 125678.90,
    date: '2024-01-15T08:30:00',
    status: 'completed',
    counterparty: 'Cliente XYZ Ltda'
  },
  {
    id: 'TRX002',
    accountId: 'ACC001',
    accountName: 'C/C Banco do Brasil',
    bankName: 'Banco do Brasil',
    type: 'debit',
    category: 'Pagamento',
    description: 'Pagamento de Fornecedor',
    amount: 8500.00,
    balance: 110678.90,
    date: '2024-01-15T07:15:00',
    status: 'completed',
    counterparty: 'Fornecedor ABC'
  },
  {
    id: 'TRX003',
    accountId: 'ACC003',
    accountName: 'C/C Itaú',
    bankName: 'Itaú Unibanco',
    type: 'debit',
    category: 'Taxa',
    description: 'Tarifa de Manutenção',
    amount: 45.00,
    balance: 89234.56,
    date: '2024-01-15T00:00:00',
    status: 'completed'
  },
  {
    id: 'TRX004',
    accountId: 'ACC001',
    accountName: 'C/C Banco do Brasil',
    bankName: 'Banco do Brasil',
    type: 'credit',
    category: 'PIX',
    description: 'PIX Recebido',
    amount: 2500.00,
    balance: 113178.90,
    date: '2024-01-14T16:45:00',
    status: 'completed',
    counterparty: 'João Silva'
  },
  {
    id: 'TRX005',
    accountId: 'ACC004',
    accountName: 'C/C Santander',
    bankName: 'Santander',
    type: 'debit',
    category: 'Boleto',
    description: 'Pagamento de Boleto',
    amount: 1234.56,
    balance: 67890.12,
    date: '2024-01-14T14:30:00',
    status: 'pending'
  }
];

// Chart data
const balanceHistoryData = [
  { date: '01/01', balance: 320000 },
  { date: '05/01', balance: 345000 },
  { date: '10/01', balance: 312000 },
  { date: '15/01', balance: 328000 },
  { date: '20/01', balance: 356000 },
  { date: '25/01', balance: 342000 },
  { date: '30/01', balance: 377803 }
];

const transactionsByTypeData = [
  { name: 'Recebimentos', value: 156, color: '#10b981' },
  { name: 'Pagamentos', value: 234, color: '#ef4444' },
  { name: 'Transferências', value: 89, color: '#6366f1' },
  { name: 'Taxas', value: 45, color: '#f59e0b' }
];

const transactionsByBankData = [
  { name: 'Banco do Brasil', credits: 45000, debits: 32000 },
  { name: 'Itaú', credits: 28000, debits: 18000 },
  { name: 'Santander', credits: 15000, debits: 12000 },
  { name: 'Bradesco', credits: 8000, debits: 5000 }
];

const balanceByAccountData = [
  { name: 'C/C BB', value: 125678.90, color: '#FFCE56' },
  { name: 'Poup BB', value: 45000, color: '#36A2EB' },
  { name: 'C/C Itaú', value: 89234.56, color: '#FF6384' },
  { name: 'C/C Santander', value: 67890.12, color: '#4BC0C0' },
  { name: 'Invest Bradesco', value: 250000, color: '#9966FF' }
];

export function OpenBankingPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedConnection, setSelectedConnection] = useState<BankConnection | null>(null);
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [showAddBankModal, setShowAddBankModal] = useState(false);
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<BankAccount | null>(null);
  const [transactionFilter, setTransactionFilter] = useState('all');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Building2 className="h-4 w-4" /> },
    { value: 'banks', label: 'Bancos', icon: <Link className="h-4 w-4" /> },
    { value: 'accounts', label: 'Contas', icon: <Wallet className="h-4 w-4" /> },
    { value: 'transactions', label: 'Transações', icon: <CreditCard className="h-4 w-4" /> }
  ];

  const transactionFilterOptions: SelectOption[] = [
    { value: 'all', label: 'Todas' },
    { value: 'credit', label: 'Créditos' },
    { value: 'debit', label: 'Débitos' },
    { value: 'pending', label: 'Pendentes' }
  ];

  const getConnectionStatusBadge = (status: BankConnection['status']) => {
    const statusConfig = {
      connected: { label: 'Conectado', variant: 'success' as const, icon: <CheckCircle className="h-3 w-3" /> },
      disconnected: { label: 'Desconectado', variant: 'neutral' as const, icon: <Link2Off className="h-3 w-3" /> },
      pending: { label: 'Pendente', variant: 'warning' as const, icon: <Clock className="h-3 w-3" /> },
      error: { label: 'Erro', variant: 'danger' as const, icon: <AlertTriangle className="h-3 w-3" /> }
    };
    const config = statusConfig[status];
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        {config.icon}
        {config.label}
      </Badge>
    );
  };

  const getAccountTypeBadge = (type: BankAccount['accountType']) => {
    const typeConfig = {
      checking: { label: 'Corrente', variant: 'primary' as const },
      savings: { label: 'Poupança', variant: 'info' as const },
      investment: { label: 'Investimento', variant: 'success' as const },
      credit: { label: 'Crédito', variant: 'warning' as const }
    };
    const config = typeConfig[type];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const connectionColumns: Column<BankConnection>[] = [
    {
      key: 'bank',
      header: 'Banco',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-lg bg-white flex items-center justify-center p-2">
            <Building2 className="h-6 w-6 text-gray-600" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.bankName}</p>
            <p className="text-sm text-text-secondary">Código: {row.bankCode}</p>
          </div>
        </div>
      )
    },
    {
      key: 'accounts',
      header: 'Contas',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Wallet className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary">{row.accountsCount}</span>
        </div>
      )
    },
    {
      key: 'consent',
      header: 'Consentimento',
      render: (row) => (
        <div>
          {row.consentExpiry ? (
            <>
              <p className="text-text-primary">Expira em</p>
              <p className="text-sm text-text-secondary">
                {new Date(row.consentExpiry).toLocaleDateString('pt-BR')}
              </p>
            </>
          ) : (
            <span className="text-text-secondary">-</span>
          )}
        </div>
      )
    },
    {
      key: 'lastSync',
      header: 'Última Sinc.',
      render: (row) => (
        <div>
          {row.lastSync ? (
            <>
              <p className="text-text-primary">
                {new Date(row.lastSync).toLocaleTimeString('pt-BR')}
              </p>
              <p className="text-sm text-text-secondary">
                {new Date(row.lastSync).toLocaleDateString('pt-BR')}
              </p>
            </>
          ) : (
            <span className="text-text-secondary">Nunca</span>
          )}
        </div>
      )
    },
    {
      key: 'autoSync',
      header: 'Auto Sync',
      render: (row) => (
        <Badge variant={row.autoSync ? 'success' : 'neutral'}>
          {row.autoSync ? `${row.syncInterval}min` : 'Desativado'}
        </Badge>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getConnectionStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedConnection(row);
              setShowConnectionModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" disabled={row.status !== 'connected'}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="ghost">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const accountColumns: Column<BankAccount>[] = [
    {
      key: 'account',
      header: 'Conta',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-bg-tertiary flex items-center justify-center">
            {row.accountType === 'checking' && <CreditCard className="h-5 w-5 text-accent-primary" />}
            {row.accountType === 'savings' && <PiggyBank className="h-5 w-5 text-blue-400" />}
            {row.accountType === 'investment' && <TrendingUp className="h-5 w-5 text-green-400" />}
            {row.accountType === 'credit' && <CreditCard className="h-5 w-5 text-yellow-400" />}
          </div>
          <div>
            <p className="font-medium text-text-primary">Ag: {row.agency} / CC: {row.accountNumber}</p>
            <p className="text-sm text-text-secondary">{row.bankName}</p>
          </div>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => getAccountTypeBadge(row.accountType)
    },
    {
      key: 'balance',
      header: 'Saldo',
      render: (row) => (
        <div>
          <p className="text-text-primary font-medium">{formatCurrency(row.balance)}</p>
          <p className="text-sm text-text-secondary">
            Disponível: {formatCurrency(row.availableBalance)}
          </p>
        </div>
      )
    },
    {
      key: 'lastTransaction',
      header: 'Última Movim.',
      render: (row) => (
        <div>
          <p className="text-text-primary">
            {new Date(row.lastTransaction).toLocaleTimeString('pt-BR')}
          </p>
          <p className="text-sm text-text-secondary">
            {new Date(row.lastTransaction).toLocaleDateString('pt-BR')}
          </p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={row.status === 'active' ? 'success' : row.status === 'blocked' ? 'danger' : 'neutral'}>
          {row.status === 'active' ? 'Ativa' : row.status === 'blocked' ? 'Bloqueada' : 'Inativa'}
        </Badge>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            onClick={() => {
              setSelectedAccount(row);
              setShowAccountModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const transactionColumns: Column<Transaction>[] = [
    {
      key: 'description',
      header: 'Descrição',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
            row.type === 'credit' ? 'bg-green-500/20' : 'bg-red-500/20'
          }`}>
            {row.type === 'credit' ? (
              <ArrowDownLeft className="h-5 w-5 text-green-400" />
            ) : (
              <ArrowUpRight className="h-5 w-5 text-red-400" />
            )}
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.description}</p>
            <p className="text-sm text-text-secondary">{row.counterparty || row.category}</p>
          </div>
        </div>
      )
    },
    {
      key: 'account',
      header: 'Conta',
      render: (row) => (
        <div>
          <p className="text-text-primary">{row.accountName}</p>
          <p className="text-sm text-text-secondary">{row.bankName}</p>
        </div>
      )
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <div>
          <p className="text-text-primary">{new Date(row.date).toLocaleDateString('pt-BR')}</p>
          <p className="text-sm text-text-secondary">{new Date(row.date).toLocaleTimeString('pt-BR')}</p>
        </div>
      )
    },
    {
      key: 'amount',
      header: 'Valor',
      render: (row) => (
        <span className={`font-medium ${row.type === 'credit' ? 'text-green-400' : 'text-red-400'}`}>
          {row.type === 'credit' ? '+' : '-'}{formatCurrency(row.amount)}
        </span>
      )
    },
    {
      key: 'balance',
      header: 'Saldo',
      render: (row) => (
        <span className="text-text-primary font-medium">{formatCurrency(row.balance)}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={row.status === 'completed' ? 'success' : row.status === 'pending' ? 'warning' : 'neutral'}>
          {row.status === 'completed' ? 'Concluída' : row.status === 'pending' ? 'Pendente' : 'Cancelada'}
        </Badge>
      )
    }
  ];

  const connectedBanks = mockConnections.filter(c => c.status === 'connected').length;
  const totalAccounts = mockAccounts.filter(a => a.status === 'active').length;
  const totalBalance = mockAccounts.reduce((sum, acc) => sum + acc.balance, 0);
  const lastSync = mockConnections
    .filter(c => c.lastSync)
    .sort((a, b) => new Date(b.lastSync).getTime() - new Date(a.lastSync).getTime())[0];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Open Banking
            </h1>
            <p className="text-text-secondary mt-1">
              Integração com instituições financeiras
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Sincronizar Todos
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowAddBankModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Conectar Banco
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Bancos Conectados"
            value={connectedBanks.toString()}
            icon={<Building2 className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Contas Ativas"
            value={totalAccounts.toString()}
            icon={<Wallet className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Saldo Total"
            value={formatCurrency(totalBalance)}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Última Sinc."
            value={lastSync ? `${Math.round((Date.now() - new Date(lastSync.lastSync).getTime()) / 60000)} min` : '-'}
            icon={<RefreshCw className="h-5 w-5" />}
            iconColor="warning"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Balance History */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Evolução do Saldo
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={balanceHistoryData}>
                    <defs>
                      <linearGradient id="balanceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => [formatCurrency(value), 'Saldo']}
                    />
                    <Area
                      type="monotone"
                      dataKey="balance"
                      stroke="#10b981"
                      fill="url(#balanceGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              {/* Balance by Account */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Saldo por Conta
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={balanceByAccountData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {balanceByAccountData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => [formatCurrency(value), 'Saldo']}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Transactions by Bank & Type */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Transactions by Bank */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Movimentação por Banco
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={transactionsByBankData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => [formatCurrency(value)]}
                    />
                    <Legend />
                    <Bar dataKey="credits" name="Créditos" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="debits" name="Débitos" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              {/* Transactions by Type */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Tipos de Transação
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={transactionsByTypeData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {transactionsByTypeData.map((entry, index) => (
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
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Recent Transactions */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Transações Recentes
                </h3>
                <Button variant="outline" size="sm" onClick={() => setActiveTab('transactions')}>
                  Ver Todas
                </Button>
              </div>
              <div className="space-y-3">
                {mockTransactions.slice(0, 5).map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
                        transaction.type === 'credit' ? 'bg-green-500/20' : 'bg-red-500/20'
                      }`}>
                        {transaction.type === 'credit' ? (
                          <ArrowDownLeft className="h-5 w-5 text-green-400" />
                        ) : (
                          <ArrowUpRight className="h-5 w-5 text-red-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{transaction.description}</p>
                        <p className="text-sm text-text-secondary">{transaction.accountName}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-medium ${transaction.type === 'credit' ? 'text-green-400' : 'text-red-400'}`}>
                        {transaction.type === 'credit' ? '+' : '-'}{formatCurrency(transaction.amount)}
                      </p>
                      <p className="text-sm text-text-secondary">
                        {new Date(transaction.date).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'banks' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar banco..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
              <Button onClick={() => setShowAddBankModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Conectar Banco
              </Button>
            </div>

            <DataTable
              data={mockConnections}
              columns={connectionColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'accounts' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar conta..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>

            <DataTable
              data={mockAccounts}
              columns={accountColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'transactions' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar transação..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <Select
                options={transactionFilterOptions}
                value={transactionFilter}
                onChange={(value) => setTransactionFilter(value)}
              />
              <Button variant="outline">
                <Calendar className="h-4 w-4 mr-2" />
                Período
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>

            <DataTable
              data={mockTransactions}
              columns={transactionColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}
      </div>

      {/* Connection Detail Modal */}
      <Modal
        isOpen={showConnectionModal}
        onClose={() => setShowConnectionModal(false)}
        title="Detalhes da Conexão"
        size="lg"
      >
        {selectedConnection && (
          <div className="space-y-6">
            {/* Bank Header */}
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="h-16 w-16 rounded-lg bg-white flex items-center justify-center p-2">
                <Building2 className="h-8 w-8 text-gray-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedConnection.bankName}
                </h3>
                <p className="text-text-secondary">Código: {selectedConnection.bankCode}</p>
              </div>
              <div className="ml-auto">
                {getConnectionStatusBadge(selectedConnection.status)}
              </div>
            </div>

            {/* Details */}
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Consentimento</p>
                  <p className="text-text-primary font-mono text-sm mt-1">
                    {selectedConnection.consentId || '-'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Expira em</p>
                  <p className="text-text-primary mt-1">
                    {selectedConnection.consentExpiry
                      ? new Date(selectedConnection.consentExpiry).toLocaleDateString('pt-BR')
                      : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Contas Vinculadas</p>
                  <p className="text-text-primary mt-1">{selectedConnection.accountsCount}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-text-secondary">Última Sincronização</p>
                  <p className="text-text-primary mt-1">
                    {selectedConnection.lastSync
                      ? new Date(selectedConnection.lastSync).toLocaleString('pt-BR')
                      : 'Nunca'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Sincronização Automática</p>
                  <p className="text-text-primary mt-1">
                    {selectedConnection.autoSync
                      ? `A cada ${selectedConnection.syncInterval} minutos`
                      : 'Desativada'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Conectado desde</p>
                  <p className="text-text-primary mt-1">
                    {new Date(selectedConnection.createdAt).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>
            </div>

            {/* Warning for expiring consent */}
            {selectedConnection.consentExpiry &&
              new Date(selectedConnection.consentExpiry) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) && (
              <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-400" />
                  <span className="text-yellow-400 font-medium">Consentimento Expirando</span>
                </div>
                <p className="text-text-secondary">
                  O consentimento expira em breve. Renove para continuar sincronizando.
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Configurar
              </Button>
              <Button
                variant="outline"
                disabled={selectedConnection.status !== 'connected'}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Sincronizar
              </Button>
              <Button variant="danger">
                <Link2Off className="h-4 w-4 mr-2" />
                Desconectar
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Add Bank Modal */}
      <Modal
        isOpen={showAddBankModal}
        onClose={() => setShowAddBankModal(false)}
        title="Conectar Novo Banco"
        size="lg"
      >
        <div className="space-y-6">
          <p className="text-text-secondary">
            Selecione o banco que deseja conectar. Você será redirecionado para autorizar o acesso.
          </p>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {['Banco do Brasil', 'Itaú', 'Bradesco', 'Santander', 'Nubank', 'Inter'].map((bank) => (
              <button
                key={bank}
                className="p-4 bg-bg-tertiary rounded-lg hover:bg-bg-hover transition-colors text-left"
              >
                <div className="h-12 w-12 rounded-lg bg-white flex items-center justify-center mb-3">
                  <Building2 className="h-6 w-6 text-gray-600" />
                </div>
                <p className="font-medium text-text-primary">{bank}</p>
              </button>
            ))}
          </div>

          <div className="p-4 bg-bg-tertiary rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-5 w-5 text-accent-primary" />
              <span className="font-medium text-text-primary">Conexão Segura</span>
            </div>
            <p className="text-sm text-text-secondary">
              Utilizamos o Open Banking regulamentado pelo Banco Central. Seus dados são
              protegidos e você pode revogar o acesso a qualquer momento.
            </p>
          </div>
        </div>
      </Modal>

      {/* Account Detail Modal */}
      <Modal
        isOpen={showAccountModal}
        onClose={() => setShowAccountModal(false)}
        title="Detalhes da Conta"
        size="md"
      >
        {selectedAccount && (
          <div className="space-y-6">
            {/* Account Header */}
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="h-16 w-16 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                <Wallet className="h-8 w-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-text-primary">
                  {selectedAccount.bankName}
                </h3>
                <p className="text-text-secondary">
                  Ag: {selectedAccount.agency} / CC: {selectedAccount.accountNumber}
                </p>
              </div>
            </div>

            {/* Balance */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-secondary">Saldo Total</p>
                <p className="text-2xl font-bold text-accent-primary mt-1">
                  {formatCurrency(selectedAccount.balance)}
                </p>
              </div>
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-secondary">Saldo Disponível</p>
                <p className="text-2xl font-bold text-text-primary mt-1">
                  {formatCurrency(selectedAccount.availableBalance)}
                </p>
              </div>
            </div>

            {/* Details */}
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-border-subtle">
                <span className="text-text-secondary">Tipo de Conta</span>
                {getAccountTypeBadge(selectedAccount.accountType)}
              </div>
              <div className="flex justify-between items-center py-2 border-b border-border-subtle">
                <span className="text-text-secondary">Moeda</span>
                <span className="text-text-primary">{selectedAccount.currency}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-border-subtle">
                <span className="text-text-secondary">Última Movimentação</span>
                <span className="text-text-primary">
                  {new Date(selectedAccount.lastTransaction).toLocaleString('pt-BR')}
                </span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-text-secondary">Status</span>
                <Badge variant={selectedAccount.status === 'active' ? 'success' : 'neutral'}>
                  {selectedAccount.status === 'active' ? 'Ativa' : 'Inativa'}
                </Badge>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
              <Button variant="outline" onClick={() => setActiveTab('transactions')}>
                Ver Transações
              </Button>
              <Button>
                <RefreshCw className="h-4 w-4 mr-2" />
                Atualizar Saldo
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}
