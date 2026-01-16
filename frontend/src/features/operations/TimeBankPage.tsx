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
  Clock,
  Plus,
  Search,
  Filter,
  Download,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Calendar,
  User,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle,
  History,
  RefreshCw
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area
} from 'recharts';

// Types
interface EmployeeTimeBank {
  id: string;
  employeeName: string;
  department: string;
  positiveBalance: number;
  negativeBalance: number;
  netBalance: number;
  expiringHours: number;
  expirationDate: string;
  status: 'positive' | 'negative' | 'neutral';
}

interface TimeBankTransaction {
  id: string;
  employeeId: string;
  employeeName: string;
  type: 'credit' | 'debit' | 'compensation';
  hours: number;
  date: string;
  reason: string;
  approvedBy: string;
  status: 'approved' | 'pending' | 'rejected';
}

// Mock data
const mockEmployees: EmployeeTimeBank[] = [
  {
    id: '1',
    employeeName: 'João Silva',
    department: 'Operações',
    positiveBalance: 24,
    negativeBalance: 0,
    netBalance: 24,
    expiringHours: 8,
    expirationDate: '2026-02-28',
    status: 'positive'
  },
  {
    id: '2',
    employeeName: 'Maria Santos',
    department: 'Administrativo',
    positiveBalance: 16,
    negativeBalance: 4,
    netBalance: 12,
    expiringHours: 0,
    expirationDate: '-',
    status: 'positive'
  },
  {
    id: '3',
    employeeName: 'Pedro Lima',
    department: 'Operações',
    positiveBalance: 0,
    negativeBalance: 8,
    netBalance: -8,
    expiringHours: 0,
    expirationDate: '-',
    status: 'negative'
  },
  {
    id: '4',
    employeeName: 'Ana Costa',
    department: 'Segurança',
    positiveBalance: 32,
    negativeBalance: 0,
    netBalance: 32,
    expiringHours: 16,
    expirationDate: '2026-01-31',
    status: 'positive'
  },
  {
    id: '5',
    employeeName: 'Carlos Souza',
    department: 'Manutenção',
    positiveBalance: 8,
    negativeBalance: 8,
    netBalance: 0,
    expiringHours: 0,
    expirationDate: '-',
    status: 'neutral'
  }
];

const mockTransactions: TimeBankTransaction[] = [
  {
    id: '1',
    employeeId: '1',
    employeeName: 'João Silva',
    type: 'credit',
    hours: 4,
    date: '2026-01-15',
    reason: 'Hora extra - Evento especial',
    approvedBy: 'Supervisor Carlos',
    status: 'approved'
  },
  {
    id: '2',
    employeeId: '2',
    employeeName: 'Maria Santos',
    type: 'compensation',
    hours: 4,
    date: '2026-01-14',
    reason: 'Compensação de folga',
    approvedBy: 'Supervisor Carlos',
    status: 'approved'
  },
  {
    id: '3',
    employeeId: '3',
    employeeName: 'Pedro Lima',
    type: 'debit',
    hours: 2,
    date: '2026-01-14',
    reason: 'Saída antecipada',
    approvedBy: 'Supervisor Maria',
    status: 'pending'
  },
  {
    id: '4',
    employeeId: '4',
    employeeName: 'Ana Costa',
    type: 'credit',
    hours: 8,
    date: '2026-01-13',
    reason: 'Cobertura de turno',
    approvedBy: 'Gerente João',
    status: 'approved'
  }
];

// Chart data
const monthlyBalance = [
  { month: 'Set', positive: 850, negative: 120 },
  { month: 'Out', positive: 920, negative: 150 },
  { month: 'Nov', positive: 1050, negative: 180 },
  { month: 'Dez', positive: 1180, negative: 200 },
  { month: 'Jan', positive: 1234, negative: 210 }
];

const departmentBalance = [
  { department: 'Operações', balance: 456 },
  { department: 'Segurança', balance: 320 },
  { department: 'Manutenção', balance: 215 },
  { department: 'Admin', balance: 180 },
  { department: 'Limpeza', balance: 63 }
];

export function TimeBankPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [showCompensationModal, setShowCompensationModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeTimeBank | null>(null);
  const [newEmployeeId, setNewEmployeeId] = useState('');
  const [newTransactionType, setNewTransactionType] = useState('');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Clock className="h-4 w-4" /> },
    { value: 'employees', label: 'Colaboradores', icon: <User className="h-4 w-4" /> },
    { value: 'transactions', label: 'Movimentações', icon: <History className="h-4 w-4" /> }
  ];

  const getBalanceColor = (balance: number) => {
    if (balance > 0) return 'text-success';
    if (balance < 0) return 'text-danger';
    return 'text-text-secondary';
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'positive': return <Badge variant="success">Positivo</Badge>;
      case 'negative': return <Badge variant="danger">Negativo</Badge>;
      case 'neutral': return <Badge variant="neutral">Zerado</Badge>;
      case 'approved': return <Badge variant="success">Aprovado</Badge>;
      case 'pending': return <Badge variant="warning">Pendente</Badge>;
      case 'rejected': return <Badge variant="danger">Rejeitado</Badge>;
      default: return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const getTransactionBadge = (type: string) => {
    switch (type) {
      case 'credit': return <Badge variant="success">Crédito</Badge>;
      case 'debit': return <Badge variant="danger">Débito</Badge>;
      case 'compensation': return <Badge variant="info">Compensação</Badge>;
      default: return <Badge variant="neutral">{type}</Badge>;
    }
  };

  const employeeColumns: Column<EmployeeTimeBank>[] = [
    {
      key: 'employeeName',
      header: 'Colaborador',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.employeeName}</p>
          <p className="text-sm text-text-secondary">{row.department}</p>
        </div>
      )
    },
    {
      key: 'positiveBalance',
      header: 'Crédito',
      render: (row) => (
        <div className="flex items-center gap-1 text-success">
          <ArrowUpRight className="h-4 w-4" />
          <span>{row.positiveBalance}h</span>
        </div>
      )
    },
    {
      key: 'negativeBalance',
      header: 'Débito',
      render: (row) => (
        <div className="flex items-center gap-1 text-danger">
          <ArrowDownRight className="h-4 w-4" />
          <span>{row.negativeBalance}h</span>
        </div>
      )
    },
    {
      key: 'netBalance',
      header: 'Saldo',
      render: (row) => (
        <span className={`font-bold ${getBalanceColor(row.netBalance)}`}>
          {row.netBalance > 0 ? '+' : ''}{row.netBalance}h
        </span>
      )
    },
    {
      key: 'expiringHours',
      header: 'Vencendo',
      render: (row) => (
        row.expiringHours > 0 ? (
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-warning" />
            <span className="text-warning">{row.expiringHours}h</span>
            <span className="text-xs text-text-muted">
              até {new Date(row.expirationDate).toLocaleDateString('pt-BR')}
            </span>
          </div>
        ) : (
          <span className="text-text-muted">-</span>
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
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelectedEmployee(row)}
        >
          <RefreshCw className="h-4 w-4 mr-1" />
          Compensar
        </Button>
      )
    }
  ];

  const transactionColumns: Column<TimeBankTransaction>[] = [
    {
      key: 'employeeName',
      header: 'Colaborador',
      render: (row) => (
        <span className="font-medium text-text-primary">{row.employeeName}</span>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => getTransactionBadge(row.type)
    },
    {
      key: 'hours',
      header: 'Horas',
      render: (row) => (
        <span className={`font-medium ${
          row.type === 'credit' ? 'text-success' :
          row.type === 'debit' ? 'text-danger' : 'text-info'
        }`}>
          {row.type === 'credit' ? '+' : row.type === 'debit' ? '-' : ''}{row.hours}h
        </span>
      )
    },
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
      key: 'reason',
      header: 'Motivo',
      render: (row) => (
        <span className="text-text-secondary">{row.reason}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    }
  ];

  const filteredEmployees = mockEmployees.filter(emp => {
    const matchesSearch = emp.employeeName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || emp.status === filterStatus;
    const matchesDepartment = filterDepartment === 'all' || emp.department === filterDepartment;
    return matchesSearch && matchesStatus && matchesDepartment;
  });

  const totalPositive = mockEmployees.reduce((sum, e) => sum + e.positiveBalance, 0);
  const totalNegative = mockEmployees.reduce((sum, e) => sum + e.negativeBalance, 0);
  const totalExpiring = mockEmployees.reduce((sum, e) => sum + e.expiringHours, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Banco de Horas
            </h1>
            <p className="text-text-secondary mt-1">
              Controle e gestão de banco de horas dos colaboradores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowCompensationModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Movimentação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Saldo Total"
            value={`+${totalPositive - totalNegative}h`}
            icon={<Clock className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Horas a Compensar"
            value={`${totalNegative}h`}
            icon={<TrendingDown className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Colaboradores"
            value={mockEmployees.length.toString()}
            icon={<User className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Horas Vencendo"
            value={`${totalExpiring}h`}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
            changeLabel="próximos 30 dias"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Monthly Balance */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Evolução Mensal
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={monthlyBalance}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
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
                      dataKey="positive"
                      name="Créditos"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.3}
                    />
                    <Area
                      type="monotone"
                      dataKey="negative"
                      name="Débitos"
                      stroke="#ef4444"
                      fill="#ef4444"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Department Balance */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Saldo por Departamento
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={departmentBalance} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#64748b" />
                    <YAxis dataKey="department" type="category" stroke="#64748b" width={100} />
                    <Tooltip
                      formatter={(value: number) => `${value}h`}
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="balance" name="Saldo" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Expiring Soon */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Horas Vencendo
                </h3>
                <Badge variant="danger">{totalExpiring}h total</Badge>
              </div>
              <div className="space-y-4">
                {mockEmployees.filter(e => e.expiringHours > 0).map((emp) => (
                  <div key={emp.id} className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-danger/10 flex items-center justify-center">
                        <AlertTriangle className="h-5 w-5 text-danger" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{emp.employeeName}</p>
                        <p className="text-sm text-text-secondary">{emp.department}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-danger">{emp.expiringHours}h</p>
                      <p className="text-sm text-text-muted">
                        até {new Date(emp.expirationDate).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Recent Transactions */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Movimentações Recentes
              </h3>
              <div className="space-y-4">
                {mockTransactions.slice(0, 4).map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                        transaction.type === 'credit' ? 'bg-success/10' :
                        transaction.type === 'debit' ? 'bg-danger/10' : 'bg-info/10'
                      }`}>
                        {transaction.type === 'credit' ? (
                          <ArrowUpRight className="h-5 w-5 text-success" />
                        ) : transaction.type === 'debit' ? (
                          <ArrowDownRight className="h-5 w-5 text-danger" />
                        ) : (
                          <RefreshCw className="h-5 w-5 text-info" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{transaction.employeeName}</p>
                        <p className="text-sm text-text-secondary">{transaction.reason}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        transaction.type === 'credit' ? 'text-success' :
                        transaction.type === 'debit' ? 'text-danger' : 'text-info'
                      }`}>
                        {transaction.type === 'credit' ? '+' : transaction.type === 'debit' ? '-' : ''}{transaction.hours}h
                      </p>
                      <p className="text-sm text-text-muted">
                        {new Date(transaction.date).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Employees Tab */}
        {activeTab === 'employees' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar colaborador..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={filterDepartment}
                onChange={setFilterDepartment}
                options={[
                  { value: 'all', label: 'Todos os departamentos' },
                  { value: 'Operações', label: 'Operações' },
                  { value: 'Administrativo', label: 'Administrativo' },
                  { value: 'Segurança', label: 'Segurança' },
                  { value: 'Manutenção', label: 'Manutenção' }
                ]}
                className="w-48"
              />
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                options={[
                  { value: 'all', label: 'Todos os status' },
                  { value: 'positive', label: 'Positivo' },
                  { value: 'negative', label: 'Negativo' },
                  { value: 'neutral', label: 'Zerado' }
                ]}
                className="w-40"
              />
            </div>
            <DataTable
              columns={employeeColumns}
              data={filteredEmployees}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Transactions Tab */}
        {activeTab === 'transactions' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar movimentação..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Input type="date" className="w-40" />
              <Input type="date" className="w-40" />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={transactionColumns}
              data={mockTransactions}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Compensation Modal */}
        <Modal
          isOpen={showCompensationModal || !!selectedEmployee}
          onClose={() => {
            setShowCompensationModal(false);
            setSelectedEmployee(null);
          }}
          title={selectedEmployee ? `Compensar - ${selectedEmployee.employeeName}` : 'Nova Movimentação'}
          size="md"
        >
          <div className="space-y-4">
            {!selectedEmployee && (
              <Select
                value={newEmployeeId}
                onChange={(value) => setNewEmployeeId(value)}
                options={[
                  { value: '', label: 'Selecione o colaborador' },
                  ...mockEmployees.map(e => ({ value: e.id, label: e.employeeName }))
                ]}
                className="w-full"
              />
            )}
            {selectedEmployee && (
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-text-primary">{selectedEmployee.employeeName}</p>
                    <p className="text-sm text-text-secondary">{selectedEmployee.department}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-2xl font-bold ${getBalanceColor(selectedEmployee.netBalance)}`}>
                      {selectedEmployee.netBalance > 0 ? '+' : ''}{selectedEmployee.netBalance}h
                    </p>
                    <p className="text-sm text-text-muted">saldo atual</p>
                  </div>
                </div>
              </div>
            )}
            <Select
              value={newTransactionType}
              onChange={(value) => setNewTransactionType(value)}
              options={[
                { value: '', label: 'Tipo de movimentação' },
                { value: 'credit', label: 'Crédito (hora extra)' },
                { value: 'debit', label: 'Débito (saída antecipada)' },
                { value: 'compensation', label: 'Compensação (folga)' }
              ]}
              className="w-full"
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Horas" type="number" placeholder="0" />
              <Input label="Data" type="date" />
            </div>
            <Input label="Motivo" placeholder="Descreva o motivo da movimentação" />
            <div className="flex justify-end gap-3 pt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setShowCompensationModal(false);
                  setSelectedEmployee(null);
                }}
              >
                Cancelar
              </Button>
              <Button>
                <CheckCircle className="h-4 w-4 mr-2" />
                Registrar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
