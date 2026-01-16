'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  RefreshCw,
  Download,
  Building2,
  CreditCard,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Eye,
  Link2,
  Unlink,
  DollarSign,
  TrendingUp,
  Calendar,
  FileText,
  ArrowRightLeft,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Types
interface BankAccount {
  id: string;
  bank: string;
  bankLogo: string;
  accountName: string;
  accountNumber: string;
  agency: string;
  type: 'checking' | 'savings' | 'investment';
  balance: number;
  lastSync: string;
  status: 'active' | 'inactive' | 'pending';
}

interface BankTransaction {
  id: string;
  date: string;
  description: string;
  type: 'credit' | 'debit';
  value: number;
  balance: number;
  category: string;
  reconciled: boolean;
  linkedTo: string | null;
}

// Mock Data
const bankAccounts: BankAccount[] = [
  {
    id: '1',
    bank: 'Itaú',
    bankLogo: '/banks/itau.png',
    accountName: 'Itaú Empresas',
    accountNumber: '12345-6',
    agency: '1234',
    type: 'checking',
    balance: 485000,
    lastSync: '2026-01-15T14:30:00',
    status: 'active',
  },
  {
    id: '2',
    bank: 'Bradesco',
    bankLogo: '/banks/bradesco.png',
    accountName: 'Bradesco PJ',
    accountNumber: '78901-2',
    agency: '5678',
    type: 'checking',
    balance: 215000,
    lastSync: '2026-01-15T14:25:00',
    status: 'active',
  },
  {
    id: '3',
    bank: 'Santander',
    bankLogo: '/banks/santander.png',
    accountName: 'Santander Select',
    accountNumber: '34567-8',
    agency: '9012',
    type: 'savings',
    balance: 150000,
    lastSync: '2026-01-15T10:00:00',
    status: 'active',
  },
  {
    id: '4',
    bank: 'BTG Pactual',
    bankLogo: '/banks/btg.png',
    accountName: 'BTG Investimentos',
    accountNumber: '90123-4',
    agency: '0001',
    type: 'investment',
    balance: 500000,
    lastSync: '2026-01-14T18:00:00',
    status: 'active',
  },
];

const transactions: BankTransaction[] = [
  {
    id: '1',
    date: '2026-01-15',
    description: 'PIX Recebido - Shopping Center Norte',
    type: 'credit',
    value: 128000,
    balance: 485000,
    category: 'Receita',
    reconciled: true,
    linkedTo: 'CR-2026-0089',
  },
  {
    id: '2',
    date: '2026-01-15',
    description: 'TED Enviada - Folha Janeiro',
    type: 'debit',
    value: 245000,
    balance: 357000,
    category: 'RH',
    reconciled: true,
    linkedTo: 'CP-2026-0124',
  },
  {
    id: '3',
    date: '2026-01-14',
    description: 'Pagamento Boleto - Fornecedor ABC',
    type: 'debit',
    value: 18500,
    balance: 602000,
    category: 'Fornecedor',
    reconciled: false,
    linkedTo: null,
  },
  {
    id: '4',
    date: '2026-01-14',
    description: 'Depósito Identificado',
    type: 'credit',
    value: 45000,
    balance: 620500,
    category: 'Receita',
    reconciled: true,
    linkedTo: 'CR-2026-0087',
  },
  {
    id: '5',
    date: '2026-01-13',
    description: 'Tarifa Bancária',
    type: 'debit',
    value: 150,
    balance: 575500,
    category: 'Administrativa',
    reconciled: true,
    linkedTo: null,
  },
  {
    id: '6',
    date: '2026-01-12',
    description: 'Débito Automático - Energia',
    type: 'debit',
    value: 4800,
    balance: 575650,
    category: 'Utilidades',
    reconciled: false,
    linkedTo: null,
  },
];

const balanceHistory = [
  { date: '10/01', balance: 520000 },
  { date: '11/01', balance: 575650 },
  { date: '12/01', balance: 580450 },
  { date: '13/01', balance: 575500 },
  { date: '14/01', balance: 620500 },
  { date: '15/01', balance: 485000 },
];

const transactionColumns: Column<BankTransaction>[] = [
  {
    key: 'date',
    header: 'Data',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {new Date(row.date).toLocaleDateString('pt-BR')}
      </span>
    ),
  },
  {
    key: 'description',
    header: 'Descrição',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${row.type === 'credit' ? 'bg-success/10' : 'bg-danger/10'}`}>
          {row.type === 'credit' ? (
            <ArrowUpRight className="w-4 h-4 text-success" />
          ) : (
            <ArrowDownRight className="w-4 h-4 text-danger" />
          )}
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.description}</p>
          <p className="text-xs text-text-muted">{row.category}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'value',
    header: 'Valor',
    render: (row) => (
      <span className={`font-mono font-medium ${row.type === 'credit' ? 'text-success' : 'text-danger'}`}>
        {row.type === 'credit' ? '+' : '-'}
        {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'balance',
    header: 'Saldo',
    render: (row) => (
      <span className="font-mono text-text-primary">
        {row.balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'reconciled',
    header: 'Conciliado',
    render: (row) => (
      <div className="flex items-center gap-2">
        {row.reconciled ? (
          <Badge variant="success" size="sm" leftIcon={<CheckCircle2 className="w-3 h-3" />}>
            Conciliado
          </Badge>
        ) : (
          <Badge variant="warning" size="sm" leftIcon={<Clock className="w-3 h-3" />}>
            Pendente
          </Badge>
        )}
        {row.linkedTo && (
          <Badge variant="secondary" size="sm" leftIcon={<Link2 className="w-3 h-3" />}>
            {row.linkedTo}
          </Badge>
        )}
      </div>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        {!row.reconciled && (
          <Button variant="primary" size="sm" leftIcon={<Link2 className="w-3 h-3" />}>
            Vincular
          </Button>
        )}
      </div>
    ),
  },
];

function BankAccountCard({ account }: { account: BankAccount }) {
  const typeConfig = {
    checking: { label: 'Conta Corrente', color: 'primary' },
    savings: { label: 'Poupança', color: 'success' },
    investment: { label: 'Investimento', color: 'warning' },
  };

  return (
    <Card className="hover:border-accent-primary/50 transition-colors">
      <CardBody>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-bg-tertiary rounded-xl flex items-center justify-center">
              <Building2 className="w-6 h-6 text-accent-primary" />
            </div>
            <div>
              <p className="font-medium text-text-primary">{account.accountName}</p>
              <p className="text-sm text-text-muted">
                Ag: {account.agency} | Cc: {account.accountNumber}
              </p>
            </div>
          </div>
          <Badge variant={typeConfig[account.type].color as any} size="sm">
            {typeConfig[account.type].label}
          </Badge>
        </div>

        <div className="mb-4">
          <p className="text-xs text-text-muted mb-1">Saldo Atual</p>
          <p className="text-2xl font-mono font-bold text-text-primary">
            {account.balance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </p>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
          <div className="flex items-center gap-2 text-xs text-text-muted">
            <RefreshCw className="w-3 h-3" />
            <span>
              Sincronizado há{' '}
              {Math.round((Date.now() - new Date(account.lastSync).getTime()) / 1000 / 60)} min
            </span>
          </div>
          <Button variant="ghost" size="sm">
            <Eye className="w-4 h-4" />
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}

export function BankingPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [selectedTab, setSelectedTab] = useState('all');

  const totalBalance = bankAccounts.reduce((acc, account) => acc + account.balance, 0);
  const pendingReconciliation = transactions.filter((t) => !t.reconciled).length;

  const filteredTransactions = transactions.filter((t) => {
    const matchesSearch = t.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab =
      selectedTab === 'all' ||
      (selectedTab === 'pending' && !t.reconciled) ||
      (selectedTab === 'reconciled' && t.reconciled);
    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Contas Bancárias
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie suas contas e conciliação bancária
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Sincronizar
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar OFX
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
              Nova Conta
            </Button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-accent-primary/10 to-bg-secondary border-accent-primary/20">
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-accent-primary/10">
                  <DollarSign className="w-5 h-5 text-accent-primary" />
                </div>
                <span className="text-xs text-text-muted">Saldo Total</span>
              </div>
              <p className="text-2xl font-mono font-bold text-accent-primary">
                {totalBalance.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              </p>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-success/10">
                  <TrendingUp className="w-5 h-5 text-success" />
                </div>
                <span className="text-xs text-text-muted">Entradas (Mês)</span>
              </div>
              <p className="text-2xl font-mono font-bold text-success">
                R$ 173.000,00
              </p>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-danger/10">
                  <ArrowDownRight className="w-5 h-5 text-danger" />
                </div>
                <span className="text-xs text-text-muted">Saídas (Mês)</span>
              </div>
              <p className="text-2xl font-mono font-bold text-danger">
                R$ 268.450,00
              </p>
            </CardBody>
          </Card>

          <Card className={pendingReconciliation > 0 ? 'border-warning/30' : ''}>
            <CardBody className="py-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-warning/10">
                  <AlertTriangle className="w-5 h-5 text-warning" />
                </div>
                <span className="text-xs text-text-muted">Pendentes</span>
              </div>
              <p className="text-2xl font-bold text-warning">
                {pendingReconciliation} lançamentos
              </p>
            </CardBody>
          </Card>
        </div>

        {/* Bank Accounts Grid */}
        <div>
          <h2 className="text-lg font-medium text-text-primary mb-4">Minhas Contas</h2>
          <div className="grid grid-cols-4 gap-4">
            {bankAccounts.map((account) => (
              <BankAccountCard key={account.id} account={account} />
            ))}
          </div>
        </div>

        {/* Balance Chart & Transactions */}
        <div className="grid grid-cols-3 gap-6">
          {/* Balance History Chart */}
          <Card>
            <CardHeader title="Evolução do Saldo" subtitle="Últimos 7 dias" />
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={balanceHistory}>
                    <defs>
                      <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                    <YAxis
                      stroke="#64748b"
                      fontSize={12}
                      tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) =>
                        value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                      }
                    />
                    <Area
                      type="monotone"
                      dataKey="balance"
                      stroke="#6366f1"
                      fillOpacity={1}
                      fill="url(#colorBalance)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Recent Transactions */}
          <Card className="col-span-2">
            <CardHeader
              title="Extrato Bancário"
              action={
                <div className="flex items-center gap-3">
                  <Select
                    options={[
                      { value: 'all', label: 'Todas as Contas' },
                      ...bankAccounts.map((a) => ({ value: a.id, label: a.accountName })),
                    ]}
                    value={selectedAccount}
                    onChange={setSelectedAccount}
                    className="w-48"
                  />
                </div>
              }
            />
            <CardBody className="pt-0">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todos (${transactions.length})` },
                  { value: 'pending', label: `Pendentes (${pendingReconciliation})` },
                  { value: 'reconciled', label: `Conciliados (${transactions.length - pendingReconciliation})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
            </CardBody>
            <CardBody className="p-0 pt-0">
              <DataTable
                columns={transactionColumns}
                data={filteredTransactions}
                keyExtractor={(row) => row.id}
              />
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
