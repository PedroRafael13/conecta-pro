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
  GitCompare,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Upload,
  DollarSign,
  Calendar,
  Edit,
  Trash2,
  Eye,
  Check,
  X,
  Link,
  Unlink,
  ArrowLeftRight,
  Building2,
  FileText,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  CreditCard,
  ArrowDownCircle,
  ArrowUpCircle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  AreaChart,
  Area
} from 'recharts';

// Types
interface BankAccount {
  id: string;
  name: string;
  bank: string;
  agency: string;
  account: string;
  balance: number;
  lastSync: string;
  status: 'synced' | 'pending' | 'error';
}

interface BankTransaction {
  id: string;
  accountId: string;
  date: string;
  description: string;
  type: 'credit' | 'debit';
  value: number;
  balance: number;
  category: string;
  status: 'reconciled' | 'pending' | 'divergent';
  matchedEntry?: string;
}

interface SystemEntry {
  id: string;
  date: string;
  description: string;
  type: 'credit' | 'debit';
  value: number;
  category: string;
  status: 'matched' | 'unmatched';
}

// Mock data
const mockAccounts: BankAccount[] = [
  {
    id: '1',
    name: 'Conta Principal',
    bank: 'Banco do Brasil',
    agency: '1234-5',
    account: '12345-6',
    balance: 485000,
    lastSync: '2026-01-16T08:00:00',
    status: 'synced'
  },
  {
    id: '2',
    name: 'Conta Operacional',
    bank: 'Itaú',
    agency: '4567',
    account: '67890-1',
    balance: 125000,
    lastSync: '2026-01-16T07:30:00',
    status: 'synced'
  },
  {
    id: '3',
    name: 'Conta Reserva',
    bank: 'Bradesco',
    agency: '7890',
    account: '34567-8',
    balance: 250000,
    lastSync: '2026-01-15T18:00:00',
    status: 'pending'
  }
];

const mockTransactions: BankTransaction[] = [
  {
    id: '1',
    accountId: '1',
    date: '2026-01-16',
    description: 'TED RECEBIDA - CLIENTE ABC LTDA',
    type: 'credit',
    value: 15000,
    balance: 485000,
    category: 'Receita',
    status: 'reconciled',
    matchedEntry: 'ENT-001'
  },
  {
    id: '2',
    accountId: '1',
    date: '2026-01-15',
    description: 'PAGTO FORNECEDOR - TECH SOLUTIONS',
    type: 'debit',
    value: 8500,
    balance: 470000,
    category: 'Fornecedor',
    status: 'reconciled',
    matchedEntry: 'ENT-002'
  },
  {
    id: '3',
    accountId: '1',
    date: '2026-01-15',
    description: 'DOC RECEBIDO - CLIENTE XYZ SA',
    type: 'credit',
    value: 22500,
    balance: 478500,
    category: 'Receita',
    status: 'pending'
  },
  {
    id: '4',
    accountId: '1',
    date: '2026-01-14',
    description: 'TARIFA BANCÁRIA',
    type: 'debit',
    value: 45.50,
    balance: 456000,
    category: 'Taxas',
    status: 'reconciled',
    matchedEntry: 'ENT-003'
  },
  {
    id: '5',
    accountId: '1',
    date: '2026-01-14',
    description: 'PGTO FOLHA - JANEIRO',
    type: 'debit',
    value: 125000,
    balance: 456045.50,
    category: 'Folha',
    status: 'divergent'
  }
];

const mockSystemEntries: SystemEntry[] = [
  {
    id: 'ENT-001',
    date: '2026-01-16',
    description: 'Recebimento Cliente ABC Ltda - NF 1234',
    type: 'credit',
    value: 15000,
    category: 'Receita',
    status: 'matched'
  },
  {
    id: 'ENT-002',
    date: '2026-01-15',
    description: 'Pagamento Tech Solutions - Pedido 567',
    type: 'debit',
    value: 8500,
    category: 'Fornecedor',
    status: 'matched'
  },
  {
    id: 'ENT-003',
    date: '2026-01-14',
    description: 'Tarifa Bancária - Janeiro',
    type: 'debit',
    value: 45.50,
    category: 'Taxas',
    status: 'matched'
  },
  {
    id: 'ENT-004',
    date: '2026-01-16',
    description: 'Recebimento Cliente XYZ SA - NF 5678',
    type: 'credit',
    value: 22500,
    category: 'Receita',
    status: 'unmatched'
  },
  {
    id: 'ENT-005',
    date: '2026-01-14',
    description: 'Folha de Pagamento - Janeiro',
    type: 'debit',
    value: 128500,
    category: 'Folha',
    status: 'unmatched'
  }
];

// Chart data
const reconciliationProgress = [
  { date: '10/01', reconciled: 85, pending: 12, divergent: 3 },
  { date: '11/01', reconciled: 88, pending: 10, divergent: 2 },
  { date: '12/01', reconciled: 90, pending: 8, divergent: 2 },
  { date: '13/01', reconciled: 87, pending: 10, divergent: 3 },
  { date: '14/01', reconciled: 92, pending: 6, divergent: 2 },
  { date: '15/01', reconciled: 95, pending: 4, divergent: 1 },
  { date: '16/01', reconciled: 93, pending: 5, divergent: 2 }
];

const balanceHistory = [
  { date: '10/01', value: 420000 },
  { date: '11/01', value: 445000 },
  { date: '12/01', value: 438000 },
  { date: '13/01', value: 462000 },
  { date: '14/01', value: 470000 },
  { date: '15/01', value: 478000 },
  { date: '16/01', value: 485000 }
];

export function BankReconciliationPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showMatchModal, setShowMatchModal] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<BankTransaction | null>(null);

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <GitCompare className="h-4 w-4" /> },
    { value: 'transactions', label: 'Transações', icon: <ArrowLeftRight className="h-4 w-4" /> },
    { value: 'accounts', label: 'Contas', icon: <Building2 className="h-4 w-4" /> }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'reconciled':
      case 'matched':
      case 'synced':
        return <Badge variant="success">Conciliado</Badge>;
      case 'pending':
        return <Badge variant="warning">Pendente</Badge>;
      case 'divergent':
      case 'error':
        return <Badge variant="danger">Divergente</Badge>;
      case 'unmatched':
        return <Badge variant="warning">Não Conciliado</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const transactionColumns: Column<BankTransaction>[] = [
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
      key: 'description',
      header: 'Descrição',
      render: (row) => (
        <div className="max-w-md">
          <p className="font-medium text-text-primary truncate">{row.description}</p>
          <p className="text-sm text-text-secondary">{row.category}</p>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        <div className="flex items-center gap-2">
          {row.type === 'credit' ? (
            <ArrowDownCircle className="h-4 w-4 text-success" />
          ) : (
            <ArrowUpCircle className="h-4 w-4 text-danger" />
          )}
          <span className={row.type === 'credit' ? 'text-success' : 'text-danger'}>
            {row.type === 'credit' ? 'Crédito' : 'Débito'}
          </span>
        </div>
      )
    },
    {
      key: 'value',
      header: 'Valor',
      render: (row) => (
        <span className={`font-medium ${row.type === 'credit' ? 'text-success' : 'text-danger'}`}>
          {row.type === 'credit' ? '+' : '-'}
          {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'matchedEntry',
      header: 'Lançamento',
      render: (row) => (
        row.matchedEntry ? (
          <div className="flex items-center gap-2">
            <Link className="h-4 w-4 text-success" />
            <span className="text-text-secondary font-mono text-sm">{row.matchedEntry}</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Unlink className="h-4 w-4 text-text-muted" />
            <span className="text-text-muted">-</span>
          </div>
        )
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
          {row.status !== 'reconciled' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSelectedTransaction(row);
                setShowMatchModal(true);
              }}
            >
              <Link className="h-4 w-4" />
            </Button>
          )}
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const accountColumns: Column<BankAccount>[] = [
    {
      key: 'name',
      header: 'Conta',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Building2 className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.bank}</p>
          </div>
        </div>
      )
    },
    {
      key: 'agency',
      header: 'Agência/Conta',
      render: (row) => (
        <span className="font-mono text-text-secondary">
          {row.agency} / {row.account}
        </span>
      )
    },
    {
      key: 'balance',
      header: 'Saldo',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {row.balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      )
    },
    {
      key: 'lastSync',
      header: 'Última Sincronização',
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.lastSync).toLocaleString('pt-BR')}
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
          <Button variant="ghost" size="sm">
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const filteredTransactions = mockTransactions.filter(t => {
    const matchesSearch = t.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || t.status === filterStatus;
    const matchesAccount = selectedAccount === 'all' || t.accountId === selectedAccount;
    return matchesSearch && matchesStatus && matchesAccount;
  });

  const pendingCount = mockTransactions.filter(t => t.status === 'pending').length;
  const reconciledCount = mockTransactions.filter(t => t.status === 'reconciled').length;
  const divergentCount = mockTransactions.filter(t => t.status === 'divergent').length;
  const totalBalance = mockAccounts.reduce((sum, a) => sum + a.balance, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Conciliação Bancária
            </h1>
            <p className="text-text-secondary mt-1">
              Reconciliação de extratos e lançamentos do sistema
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => setShowUploadModal(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Importar Extrato
            </Button>
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Sincronizar
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Pendentes"
            value={pendingCount.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Conciliados"
            value={reconciledCount.toString()}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Divergentes"
            value={divergentCount.toString()}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Saldo Total"
            value={totalBalance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="info"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Reconciliation Progress */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Progresso da Conciliação
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={reconciliationProgress}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="reconciled"
                      name="Conciliados"
                      stackId="1"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.6}
                    />
                    <Area
                      type="monotone"
                      dataKey="pending"
                      name="Pendentes"
                      stackId="1"
                      stroke="#f59e0b"
                      fill="#f59e0b"
                      fillOpacity={0.6}
                    />
                    <Area
                      type="monotone"
                      dataKey="divergent"
                      name="Divergentes"
                      stackId="1"
                      stroke="#ef4444"
                      fill="#ef4444"
                      fillOpacity={0.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Balance History */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Evolução do Saldo
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={balanceHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" tickFormatter={(value) => `${value / 1000}K`} />
                    <Tooltip
                      formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      name="Saldo"
                      stroke="#6366f1"
                      strokeWidth={2}
                      dot={{ fill: '#6366f1', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Account Summary */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Resumo por Conta
              </h3>
              <div className="space-y-4">
                {mockAccounts.map((account) => (
                  <div key={account.id} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Building2 className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{account.name}</p>
                        <p className="text-sm text-text-secondary">{account.bank}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-text-primary">
                        {account.balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      {getStatusBadge(account.status)}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Pending Items */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Itens Pendentes
              </h3>
              <div className="space-y-4">
                {mockTransactions.filter(t => t.status !== 'reconciled').slice(0, 4).map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                        transaction.status === 'pending' ? 'bg-warning/10' : 'bg-danger/10'
                      }`}>
                        {transaction.type === 'credit' ? (
                          <ArrowDownCircle className={`h-5 w-5 ${
                            transaction.status === 'pending' ? 'text-warning' : 'text-danger'
                          }`} />
                        ) : (
                          <ArrowUpCircle className={`h-5 w-5 ${
                            transaction.status === 'pending' ? 'text-warning' : 'text-danger'
                          }`} />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary truncate max-w-[200px]">
                          {transaction.description}
                        </p>
                        <p className="text-sm text-text-secondary">
                          {new Date(transaction.date).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`font-medium ${
                        transaction.type === 'credit' ? 'text-success' : 'text-danger'
                      }`}>
                        {transaction.type === 'credit' ? '+' : '-'}
                        {transaction.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                      {getStatusBadge(transaction.status)}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Transactions Tab */}
        {activeTab === 'transactions' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar transação..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={selectedAccount}
                onChange={setSelectedAccount}
                options={[
                  { value: 'all', label: 'Todas as contas' },
                  ...mockAccounts.map(a => ({ value: a.id, label: a.name }))
                ]}
                className="w-48"
              />
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={[
                  { value: 'all', label: 'Todos os status' },
                  { value: 'reconciled', label: 'Conciliados' },
                  { value: 'pending', label: 'Pendentes' },
                  { value: 'divergent', label: 'Divergentes' }
                ]}
                className="w-40"
              />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={transactionColumns}
              data={filteredTransactions}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Accounts Tab */}
        {activeTab === 'accounts' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar conta..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-md"
                />
              </div>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Nova Conta
              </Button>
            </div>
            <DataTable
              columns={accountColumns}
              data={mockAccounts}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Upload Modal */}
        <Modal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          title="Importar Extrato Bancário"
          size="md"
        >
          <div className="space-y-4">
            <Select
              value=""
              onChange={() => {}}
              options={[
                { value: '', label: 'Selecione a conta' },
                ...mockAccounts.map(a => ({ value: a.id, label: `${a.name} - ${a.bank}` }))
              ]}
              className="w-full"
            />
            <div className="border-2 border-dashed border-border-default rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 text-text-muted mx-auto mb-4" />
              <p className="text-text-primary font-medium mb-2">
                Arraste o arquivo ou clique para selecionar
              </p>
              <p className="text-sm text-text-secondary">
                Formatos suportados: OFX, CSV, XLSX
              </p>
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowUploadModal(false)}>
                Cancelar
              </Button>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Importar
              </Button>
            </div>
          </div>
        </Modal>

        {/* Match Modal */}
        {selectedTransaction && (
          <Modal
            isOpen={showMatchModal}
            onClose={() => {
              setShowMatchModal(false);
              setSelectedTransaction(null);
            }}
            title="Conciliar Transação"
            size="lg"
          >
            <div className="space-y-6">
              {/* Bank Transaction */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Transação Bancária</h4>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-text-primary">{selectedTransaction.description}</p>
                    <p className="text-sm text-text-secondary">
                      {new Date(selectedTransaction.date).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                  <span className={`text-lg font-bold ${
                    selectedTransaction.type === 'credit' ? 'text-success' : 'text-danger'
                  }`}>
                    {selectedTransaction.type === 'credit' ? '+' : '-'}
                    {selectedTransaction.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </span>
                </div>
              </div>

              {/* System Entries */}
              <div>
                <h4 className="text-sm font-medium text-text-secondary mb-3">Lançamentos do Sistema</h4>
                <div className="space-y-2">
                  {mockSystemEntries.filter(e => e.status === 'unmatched').map((entry) => (
                    <div
                      key={entry.id}
                      className="flex items-center justify-between p-4 border border-border-default rounded-lg cursor-pointer hover:bg-bg-tertiary transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <input type="radio" name="entry" className="h-4 w-4" />
                        <div>
                          <p className="font-medium text-text-primary">{entry.description}</p>
                          <p className="text-sm text-text-secondary">
                            {new Date(entry.date).toLocaleDateString('pt-BR')} • {entry.id}
                          </p>
                        </div>
                      </div>
                      <span className={`font-medium ${
                        entry.type === 'credit' ? 'text-success' : 'text-danger'
                      }`}>
                        {entry.type === 'credit' ? '+' : '-'}
                        {entry.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowMatchModal(false);
                    setSelectedTransaction(null);
                  }}
                >
                  Cancelar
                </Button>
                <Button variant="outline">
                  <Plus className="h-4 w-4 mr-2" />
                  Criar Lançamento
                </Button>
                <Button>
                  <Link className="h-4 w-4 mr-2" />
                  Conciliar
                </Button>
              </div>
            </div>
          </Modal>
        )}
      </div>
    </MainLayout>
  );
}
