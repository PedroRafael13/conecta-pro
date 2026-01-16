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
  BookOpen,
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  TrendingUp,
  TrendingDown,
  ArrowRightLeft,
  FileText,
  Calendar,
  DollarSign,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
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
  Cell
} from 'recharts';

// Types
interface Account {
  id: string;
  code: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  parent?: string;
  level: number;
  balance: number;
  active: boolean;
}

interface JournalEntry {
  id: string;
  date: string;
  description: string;
  debitAccount: string;
  creditAccount: string;
  amount: number;
  reference: string;
  status: 'draft' | 'posted' | 'reversed';
  createdBy: string;
  createdAt: string;
}

// Mock data
const mockAccounts: Account[] = [
  { id: '1', code: '1.0.0.0', name: 'Ativo', type: 'asset', level: 1, balance: 2500000, active: true },
  { id: '2', code: '1.1.0.0', name: 'Ativo Circulante', type: 'asset', parent: '1', level: 2, balance: 1800000, active: true },
  { id: '3', code: '1.1.1.0', name: 'Caixa e Equivalentes', type: 'asset', parent: '2', level: 3, balance: 450000, active: true },
  { id: '4', code: '1.1.2.0', name: 'Contas a Receber', type: 'asset', parent: '2', level: 3, balance: 850000, active: true },
  { id: '5', code: '1.1.3.0', name: 'Estoques', type: 'asset', parent: '2', level: 3, balance: 500000, active: true },
  { id: '6', code: '2.0.0.0', name: 'Passivo', type: 'liability', level: 1, balance: 800000, active: true },
  { id: '7', code: '2.1.0.0', name: 'Passivo Circulante', type: 'liability', parent: '6', level: 2, balance: 650000, active: true },
  { id: '8', code: '2.1.1.0', name: 'Fornecedores', type: 'liability', parent: '7', level: 3, balance: 320000, active: true },
  { id: '9', code: '3.0.0.0', name: 'Patrimônio Líquido', type: 'equity', level: 1, balance: 1700000, active: true },
  { id: '10', code: '4.0.0.0', name: 'Receitas', type: 'revenue', level: 1, balance: 3500000, active: true },
  { id: '11', code: '5.0.0.0', name: 'Despesas', type: 'expense', level: 1, balance: 2800000, active: true }
];

const mockEntries: JournalEntry[] = [
  {
    id: '1',
    date: '2026-01-15',
    description: 'Recebimento de cliente - Fatura #1234',
    debitAccount: '1.1.1.0',
    creditAccount: '1.1.2.0',
    amount: 15000,
    reference: 'REC-2026-0045',
    status: 'posted',
    createdBy: 'Sistema',
    createdAt: '2026-01-15T10:30:00'
  },
  {
    id: '2',
    date: '2026-01-15',
    description: 'Pagamento fornecedor - NF #5678',
    debitAccount: '2.1.1.0',
    creditAccount: '1.1.1.0',
    amount: 8500,
    reference: 'PAG-2026-0089',
    status: 'posted',
    createdBy: 'João Silva',
    createdAt: '2026-01-15T14:20:00'
  },
  {
    id: '3',
    date: '2026-01-14',
    description: 'Provisão de salários - Janeiro',
    debitAccount: '5.1.1.0',
    creditAccount: '2.1.2.0',
    amount: 125000,
    reference: 'FOL-2026-001',
    status: 'posted',
    createdBy: 'Maria Santos',
    createdAt: '2026-01-14T16:45:00'
  },
  {
    id: '4',
    date: '2026-01-14',
    description: 'Ajuste de estoque',
    debitAccount: '5.2.1.0',
    creditAccount: '1.1.3.0',
    amount: 2500,
    reference: 'AJT-2026-012',
    status: 'draft',
    createdBy: 'Pedro Lima',
    createdAt: '2026-01-14T09:15:00'
  }
];

// Chart data
const balancesByType = [
  { name: 'Ativo', value: 2500000, color: '#10b981' },
  { name: 'Passivo', value: 800000, color: '#ef4444' },
  { name: 'PL', value: 1700000, color: '#6366f1' }
];

const monthlyMovements = [
  { month: 'Ago', debits: 280000, credits: 290000 },
  { month: 'Set', debits: 310000, credits: 305000 },
  { month: 'Out', debits: 295000, credits: 300000 },
  { month: 'Nov', debits: 320000, credits: 315000 },
  { month: 'Dez', debits: 450000, credits: 440000 },
  { month: 'Jan', debits: 380000, credits: 385000 }
];

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0
  }).format(value);
};

export function AccountingPage() {
  const [activeTab, setActiveTab] = useState('accounts');
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewEntryModal, setShowNewEntryModal] = useState(false);
  const [showNewAccountModal, setShowNewAccountModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<JournalEntry | null>(null);
  const [filterType, setFilterType] = useState('all');
  const [filterPeriod, setFilterPeriod] = useState('month');

  // Estados do formulário de novo lançamento
  const [newEntryDebitAccount, setNewEntryDebitAccount] = useState('');
  const [newEntryCreditAccount, setNewEntryCreditAccount] = useState('');

  // Estados do formulário de nova conta
  const [newAccountType, setNewAccountType] = useState('');
  const [newAccountParent, setNewAccountParent] = useState('');

  const tabs = [
    { value: 'accounts', label: 'Plano de Contas', icon: <BookOpen className="h-4 w-4" /> },
    { value: 'entries', label: 'Lançamentos', icon: <ArrowRightLeft className="h-4 w-4" /> },
    { value: 'reports', label: 'Relatórios', icon: <FileText className="h-4 w-4" /> }
  ];

  const getTypeColor = (type: Account['type']) => {
    const colors = {
      asset: 'success',
      liability: 'danger',
      equity: 'primary',
      revenue: 'info',
      expense: 'warning'
    };
    return colors[type] as 'success' | 'danger' | 'primary' | 'info' | 'warning';
  };

  const getTypeLabel = (type: Account['type']) => {
    const labels = {
      asset: 'Ativo',
      liability: 'Passivo',
      equity: 'Patrimônio',
      revenue: 'Receita',
      expense: 'Despesa'
    };
    return labels[type];
  };

  const accountColumns: Column<Account>[] = [
    {
      key: 'code',
      header: 'Código',
      render: (row) => (
        <span className="font-mono text-text-primary" style={{ paddingLeft: `${(row.level - 1) * 20}px` }}>
          {row.code}
        </span>
      )
    },
    {
      key: 'name',
      header: 'Conta',
      render: (row) => (
        <span className={`${row.level === 1 ? 'font-semibold' : ''} text-text-primary`}>
          {row.name}
        </span>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        <Badge variant={getTypeColor(row.type)} size="sm">
          {getTypeLabel(row.type)}
        </Badge>
      )
    },
    {
      key: 'balance',
      header: 'Saldo',
      render: (row) => (
        <span className={`font-medium ${row.type === 'expense' || row.type === 'liability' ? 'text-danger' : 'text-success'}`}>
          {formatCurrency(row.balance)}
        </span>
      )
    },
    {
      key: 'active',
      header: 'Status',
      render: (row) => (
        <Badge variant={row.active ? 'success' : 'neutral'} size="sm">
          {row.active ? 'Ativa' : 'Inativa'}
        </Badge>
      )
    },
    {
      key: 'id',
      header: 'Ações',
      render: () => (
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const entryColumns: Column<JournalEntry>[] = [
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
      key: 'reference',
      header: 'Referência',
      render: (row) => (
        <span className="font-mono text-text-primary">{row.reference}</span>
      )
    },
    {
      key: 'description',
      header: 'Descrição',
      render: (row) => (
        <span className="text-text-primary truncate max-w-xs block">{row.description}</span>
      )
    },
    {
      key: 'debitAccount',
      header: 'Débito',
      render: (row) => (
        <span className="font-mono text-sm">{row.debitAccount}</span>
      )
    },
    {
      key: 'creditAccount',
      header: 'Crédito',
      render: (row) => (
        <span className="font-mono text-sm">{row.creditAccount}</span>
      )
    },
    {
      key: 'amount',
      header: 'Valor',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {formatCurrency(row.amount)}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={
          row.status === 'posted' ? 'success' :
          row.status === 'draft' ? 'warning' : 'danger'
        } size="sm">
          {row.status === 'posted' ? 'Lançado' :
           row.status === 'draft' ? 'Rascunho' : 'Estornado'}
        </Badge>
      )
    },
    {
      key: 'id',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => setSelectedEntry(row)}>
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'draft' && (
            <>
              <Button variant="ghost" size="sm">
                <Edit className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <CheckCircle className="h-4 w-4 text-success" />
              </Button>
            </>
          )}
        </div>
      )
    }
  ];

  const filteredAccounts = mockAccounts.filter(account => {
    const matchesSearch = account.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         account.code.includes(searchTerm);
    const matchesType = filterType === 'all' || account.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Contabilidade
            </h1>
            <p className="text-text-secondary mt-1">
              Plano de contas e lançamentos contábeis
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              value={filterPeriod}
              onChange={setFilterPeriod}
              options={[
                { value: 'month', label: 'Este mês' },
                { value: 'quarter', label: 'Este trimestre' },
                { value: 'year', label: 'Este ano' }
              ]}
              className="w-40"
            />
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewEntryModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Lançamento
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Total Ativo"
            value={formatCurrency(2500000)}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Total Passivo"
            value={formatCurrency(800000)}
            icon={<TrendingDown className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Patrimônio Líquido"
            value={formatCurrency(1700000)}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Receitas (mês)"
            value={formatCurrency(385000)}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="success"
            change={8}
            changeLabel="vs. mês anterior"
          />
          <StatCard
            title="Despesas (mês)"
            value={formatCurrency(380000)}
            icon={<TrendingDown className="h-5 w-5" />}
            iconColor="warning"
            change={-3}
            changeLabel="vs. mês anterior"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Accounts Tab */}
        {activeTab === 'accounts' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4 flex-1">
                <div className="flex-1 max-w-md">
                  <Input
                    placeholder="Buscar conta..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Select
                  value={filterType}
                  onChange={setFilterType}
                  options={[
                    { value: 'all', label: 'Todos os tipos' },
                    { value: 'asset', label: 'Ativo' },
                    { value: 'liability', label: 'Passivo' },
                    { value: 'equity', label: 'Patrimônio' },
                    { value: 'revenue', label: 'Receita' },
                    { value: 'expense', label: 'Despesa' }
                  ]}
                  className="w-40"
                />
              </div>
              <Button variant="outline" onClick={() => setShowNewAccountModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Conta
              </Button>
            </div>
            <DataTable
              columns={accountColumns}
              data={filteredAccounts}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Entries Tab */}
        {activeTab === 'entries' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1 max-w-md">
                <Input
                  placeholder="Buscar lançamento..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                Importar
              </Button>
            </div>
            <DataTable
              columns={entryColumns}
              data={mockEntries}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Composição Patrimonial
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={balancesByType}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${formatCurrency(value)}`}
                    >
                      {balancesByType.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Movimentação Mensal
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyMovements}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" tickFormatter={(v) => `${v/1000}k`} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Bar dataKey="debits" name="Débitos" fill="#ef4444" />
                    <Bar dataKey="credits" name="Créditos" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="p-6 lg:col-span-2">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Relatórios Disponíveis
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { name: 'Balancete', desc: 'Saldos de todas as contas', icon: FileText },
                  { name: 'Razão', desc: 'Movimentação por conta', icon: BookOpen },
                  { name: 'DRE', desc: 'Demonstração de resultado', icon: TrendingUp },
                  { name: 'Balanço', desc: 'Balanço patrimonial', icon: DollarSign },
                  { name: 'Diário', desc: 'Livro diário contábil', icon: Calendar },
                  { name: 'SPED', desc: 'Escrituração digital', icon: Upload }
                ].map((report) => (
                  <div
                    key={report.name}
                    className="p-4 rounded-lg bg-bg-tertiary hover:bg-bg-hover transition-colors cursor-pointer flex items-center gap-4"
                  >
                    <div className="p-3 rounded-lg bg-accent-primary/10 text-accent-primary">
                      <report.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{report.name}</p>
                      <p className="text-sm text-text-secondary">{report.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* New Entry Modal */}
        <Modal
          isOpen={showNewEntryModal}
          onClose={() => setShowNewEntryModal(false)}
          title="Novo Lançamento Contábil"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Data
                </label>
                <Input type="date" defaultValue={new Date().toISOString().split('T')[0]} />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Referência
                </label>
                <Input placeholder="Ex: REC-2026-0046" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Descrição
              </label>
              <Input placeholder="Descrição do lançamento" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Conta Débito
                </label>
                <Select
                  value={newEntryDebitAccount}
                  onChange={(value) => setNewEntryDebitAccount(value)}
                  placeholder="Selecione..."
                  options={mockAccounts.map(a => ({ value: a.code, label: `${a.code} - ${a.name}` }))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Conta Crédito
                </label>
                <Select
                  value={newEntryCreditAccount}
                  onChange={(value) => setNewEntryCreditAccount(value)}
                  placeholder="Selecione..."
                  options={mockAccounts.map(a => ({ value: a.code, label: `${a.code} - ${a.name}` }))}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Valor
              </label>
              <Input type="number" placeholder="0,00" />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewEntryModal(false)}>
                Cancelar
              </Button>
              <Button variant="outline">
                Salvar Rascunho
              </Button>
              <Button onClick={() => setShowNewEntryModal(false)}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Lançar
              </Button>
            </div>
          </div>
        </Modal>

        {/* New Account Modal */}
        <Modal
          isOpen={showNewAccountModal}
          onClose={() => setShowNewAccountModal(false)}
          title="Nova Conta Contábil"
          size="md"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Código
                </label>
                <Input placeholder="Ex: 1.1.4.0" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Tipo
                </label>
                <Select
                  value={newAccountType}
                  onChange={(value) => setNewAccountType(value)}
                  placeholder="Selecione..."
                  options={[
                    { value: 'asset', label: 'Ativo' },
                    { value: 'liability', label: 'Passivo' },
                    { value: 'equity', label: 'Patrimônio Líquido' },
                    { value: 'revenue', label: 'Receita' },
                    { value: 'expense', label: 'Despesa' }
                  ]}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Nome da Conta
              </label>
              <Input placeholder="Nome da conta contábil" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Conta Pai (opcional)
              </label>
              <Select
                value={newAccountParent}
                onChange={(value) => setNewAccountParent(value)}
                placeholder="Selecione..."
                options={mockAccounts.filter(a => a.level < 3).map(a => ({ value: a.id, label: `${a.code} - ${a.name}` }))}
              />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewAccountModal(false)}>
                Cancelar
              </Button>
              <Button onClick={() => setShowNewAccountModal(false)}>
                <Plus className="h-4 w-4 mr-2" />
                Criar Conta
              </Button>
            </div>
          </div>
        </Modal>

        {/* Entry Detail Modal */}
        <Modal
          isOpen={!!selectedEntry}
          onClose={() => setSelectedEntry(null)}
          title="Detalhes do Lançamento"
          size="md"
        >
          {selectedEntry && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Referência</p>
                  <p className="font-mono text-text-primary">{selectedEntry.reference}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Data</p>
                  <p className="text-text-primary">
                    {new Date(selectedEntry.date).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Descrição</p>
                <p className="text-text-primary">{selectedEntry.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Débito</p>
                  <p className="font-mono text-text-primary">{selectedEntry.debitAccount}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Crédito</p>
                  <p className="font-mono text-text-primary">{selectedEntry.creditAccount}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Valor</p>
                  <p className="text-lg font-semibold text-text-primary">
                    {formatCurrency(selectedEntry.amount)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Status</p>
                  <Badge variant={selectedEntry.status === 'posted' ? 'success' : 'warning'}>
                    {selectedEntry.status === 'posted' ? 'Lançado' : 'Rascunho'}
                  </Badge>
                </div>
              </div>
              <div className="pt-4 border-t border-border-subtle">
                <p className="text-xs text-text-muted">
                  Criado por {selectedEntry.createdBy} em {new Date(selectedEntry.createdAt).toLocaleString('pt-BR')}
                </p>
              </div>
              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedEntry(null)}>
                  Fechar
                </Button>
                {selectedEntry.status === 'posted' && (
                  <Button variant="danger">
                    <XCircle className="h-4 w-4 mr-2" />
                    Estornar
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
