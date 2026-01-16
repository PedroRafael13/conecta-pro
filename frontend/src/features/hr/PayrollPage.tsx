'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  DollarSign,
  Users,
  Calendar,
  Download,
  Upload,
  FileText,
  CheckCircle2,
  Clock,
  AlertTriangle,
  TrendingUp,
  Calculator,
  Building2,
  Filter,
  Search,
  Eye,
  Printer,
  Send,
  RefreshCw,
  Plus,
  ChevronRight,
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
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

// Types
interface PayrollPeriod {
  id: string;
  reference: string;
  type: 'monthly' | 'thirteenth' | 'vacation' | 'termination';
  employees: number;
  grossTotal: number;
  deductions: number;
  netTotal: number;
  status: 'draft' | 'calculating' | 'review' | 'approved' | 'paid';
  dueDate: string;
  paymentDate: string | null;
}

interface PayrollItem {
  id: string;
  employeeId: string;
  employeeName: string;
  position: string;
  department: string;
  baseSalary: number;
  overtime: number;
  bonuses: number;
  deductions: number;
  inss: number;
  irrf: number;
  netSalary: number;
  status: 'calculated' | 'review' | 'approved' | 'error';
}

// Mock Data
const payrollHistory = [
  { month: 'Ago', value: 2850000 },
  { month: 'Set', value: 2920000 },
  { month: 'Out', value: 2980000 },
  { month: 'Nov', value: 3100000 },
  { month: 'Dez', value: 4650000 },
  { month: 'Jan', value: 3050000 },
];

const costBreakdown = [
  { name: 'Salários', value: 2100000, color: '#6366f1' },
  { name: 'Encargos', value: 650000, color: '#8b5cf6' },
  { name: 'Benefícios', value: 180000, color: '#3b82f6' },
  { name: 'Horas Extras', value: 95000, color: '#10b981' },
  { name: 'Outros', value: 25000, color: '#f59e0b' },
];

const periods: PayrollPeriod[] = [
  {
    id: '1',
    reference: 'Janeiro/2026',
    type: 'monthly',
    employees: 342,
    grossTotal: 3050000,
    deductions: 680000,
    netTotal: 2370000,
    status: 'calculating',
    dueDate: '2026-01-30',
    paymentDate: null,
  },
  {
    id: '2',
    reference: 'Dezembro/2025',
    type: 'monthly',
    employees: 340,
    grossTotal: 3100000,
    deductions: 695000,
    netTotal: 2405000,
    status: 'paid',
    dueDate: '2025-12-30',
    paymentDate: '2025-12-28',
  },
  {
    id: '3',
    reference: '13º Salário 2025',
    type: 'thirteenth',
    employees: 340,
    grossTotal: 1550000,
    deductions: 350000,
    netTotal: 1200000,
    status: 'paid',
    dueDate: '2025-12-20',
    paymentDate: '2025-12-18',
  },
  {
    id: '4',
    reference: 'Novembro/2025',
    type: 'monthly',
    employees: 338,
    grossTotal: 3100000,
    deductions: 690000,
    netTotal: 2410000,
    status: 'paid',
    dueDate: '2025-11-30',
    paymentDate: '2025-11-28',
  },
];

const payrollItems: PayrollItem[] = [
  {
    id: '1',
    employeeId: 'EMP001',
    employeeName: 'Roberto Silva',
    position: 'Supervisor de Segurança',
    department: 'Operações',
    baseSalary: 4500,
    overtime: 850,
    bonuses: 300,
    deductions: 120,
    inss: 576.47,
    irrf: 425.30,
    netSalary: 4528.23,
    status: 'calculated',
  },
  {
    id: '2',
    employeeId: 'EMP002',
    employeeName: 'Maria Santos',
    position: 'Vigilante',
    department: 'Operações',
    baseSalary: 2200,
    overtime: 440,
    bonuses: 0,
    deductions: 50,
    inss: 237.60,
    irrf: 0,
    netSalary: 2352.40,
    status: 'calculated',
  },
  {
    id: '3',
    employeeId: 'EMP003',
    employeeName: 'Carlos Eduardo',
    position: 'Coordenador Comercial',
    department: 'Comercial',
    baseSalary: 6500,
    overtime: 0,
    bonuses: 1200,
    deductions: 0,
    inss: 828.38,
    irrf: 892.45,
    netSalary: 5979.17,
    status: 'review',
  },
  {
    id: '4',
    employeeId: 'EMP004',
    employeeName: 'Ana Paula',
    position: 'Analista RH',
    department: 'RH',
    baseSalary: 4200,
    overtime: 0,
    bonuses: 200,
    deductions: 0,
    inss: 473.00,
    irrf: 287.65,
    netSalary: 3639.35,
    status: 'calculated',
  },
  {
    id: '5',
    employeeId: 'EMP005',
    employeeName: 'João Pereira',
    position: 'Vigilante',
    department: 'Operações',
    baseSalary: 2200,
    overtime: 660,
    bonuses: 100,
    deductions: 80,
    inss: 266.40,
    irrf: 45.20,
    netSalary: 2568.40,
    status: 'error',
  },
];

const typeLabels = {
  monthly: 'Mensal',
  thirteenth: '13º Salário',
  vacation: 'Férias',
  termination: 'Rescisão',
};

const statusConfig = {
  draft: { label: 'Rascunho', color: 'neutral' as const },
  calculating: { label: 'Calculando', color: 'primary' as const },
  review: { label: 'Em Revisão', color: 'warning' as const },
  approved: { label: 'Aprovada', color: 'info' as const },
  paid: { label: 'Paga', color: 'success' as const },
};

const itemStatusConfig = {
  calculated: { label: 'Calculado', color: 'success' as const },
  review: { label: 'Revisão', color: 'warning' as const },
  approved: { label: 'Aprovado', color: 'info' as const },
  error: { label: 'Erro', color: 'danger' as const },
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

const periodColumns: Column<PayrollPeriod>[] = [
  {
    key: 'reference',
    header: 'Referência',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.reference}</p>
        <p className="text-xs text-text-muted">{typeLabels[row.type]}</p>
      </div>
    ),
  },
  {
    key: 'employees',
    header: 'Funcionários',
    render: (row) => <span className="font-medium">{row.employees}</span>,
  },
  {
    key: 'grossTotal',
    header: 'Bruto',
    render: (row) => (
      <span className="font-medium text-text-primary">{formatCurrency(row.grossTotal)}</span>
    ),
  },
  {
    key: 'deductions',
    header: 'Descontos',
    render: (row) => (
      <span className="text-accent-danger">{formatCurrency(row.deductions)}</span>
    ),
  },
  {
    key: 'netTotal',
    header: 'Líquido',
    render: (row) => (
      <span className="font-bold text-accent-success">{formatCurrency(row.netTotal)}</span>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Visualizar">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'paid' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Imprimir">
              <Printer className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Baixar">
              <Download className="w-4 h-4" />
            </Button>
          </>
        )}
        {row.status === 'calculating' && (
          <Button variant="primary" size="sm" leftIcon={<RefreshCw className="w-3 h-3" />}>
            Atualizar
          </Button>
        )}
      </div>
    ),
  },
];

const itemColumns: Column<PayrollItem>[] = [
  {
    key: 'employeeName',
    header: 'Funcionário',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.employeeName}</p>
        <p className="text-xs text-text-muted">{row.employeeId} • {row.position}</p>
      </div>
    ),
  },
  {
    key: 'department',
    header: 'Departamento',
    render: (row) => <span className="text-sm">{row.department}</span>,
  },
  {
    key: 'baseSalary',
    header: 'Salário Base',
    render: (row) => <span className="text-sm">{formatCurrency(row.baseSalary)}</span>,
  },
  {
    key: 'overtime',
    header: 'Horas Extras',
    render: (row) => (
      <span className="text-sm text-accent-success">
        {row.overtime > 0 ? `+${formatCurrency(row.overtime)}` : '-'}
      </span>
    ),
  },
  {
    key: 'inss',
    header: 'INSS',
    render: (row) => (
      <span className="text-sm text-accent-danger">-{formatCurrency(row.inss)}</span>
    ),
  },
  {
    key: 'irrf',
    header: 'IRRF',
    render: (row) => (
      <span className="text-sm text-accent-danger">
        {row.irrf > 0 ? `-${formatCurrency(row.irrf)}` : '-'}
      </span>
    ),
  },
  {
    key: 'netSalary',
    header: 'Líquido',
    render: (row) => (
      <span className="font-bold text-text-primary">{formatCurrency(row.netSalary)}</span>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = itemStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
];

export function PayrollPage() {
  const [selectedTab, setSelectedTab] = useState('periods');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Filters
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [filterItemStatus, setFilterItemStatus] = useState('all');

  // Modal form
  const [folhaType, setFolhaType] = useState('monthly');
  const [referenceMonth, setReferenceMonth] = useState('01');
  const [referenceYear, setReferenceYear] = useState('2026');
  const [employeesFilter, setEmployeesFilter] = useState('all');

  // Stats
  const currentPayroll = periods.find(p => p.status === 'calculating');
  const totalMonthly = currentPayroll?.grossTotal || 0;
  const pendingApproval = payrollItems.filter(i => i.status === 'review').length;
  const withErrors = payrollItems.filter(i => i.status === 'error').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Folha de Pagamento
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de folha, cálculos e pagamentos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Upload className="w-4 h-4" />}>
              Importar
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Calculator className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Calcular Folha
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Folha do Mês"
              value={formatCurrency(totalMonthly)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="primary"
              trend="up"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Funcionários"
              value={currentPayroll?.employees || 0}
              icon={<Users className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Aguardando Revisão"
              value={pendingApproval}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Com Erros"
              value={withErrors}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Histórico de Folha</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={payrollHistory}>
                      <defs>
                        <linearGradient id="colorPayroll" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                      <XAxis dataKey="month" stroke="#64748b" />
                      <YAxis stroke="#64748b" tickFormatter={(v) => `R$ ${(v / 1000000).toFixed(1)}M`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }}
                        formatter={(value: number) => [formatCurrency(value), 'Total']}
                      />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="#6366f1"
                        fill="url(#colorPayroll)"
                        strokeWidth={2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Composição de Custos</h3>
              </CardHeader>
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={costBreakdown} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                      <XAxis type="number" stroke="#64748b" tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`} />
                      <YAxis type="category" dataKey="name" stroke="#64748b" width={80} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#12121a', border: '1px solid #2d2d3d' }}
                        formatter={(value: number) => [formatCurrency(value), 'Valor']}
                      />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {costBreakdown.map((entry, index) => (
                          <rect key={index} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Current Period Status */}
        {currentPayroll && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card className="border-accent-primary/30">
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-accent-primary/20 rounded-xl">
                      <Calculator className="w-6 h-6 text-accent-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-text-primary">Folha em Processamento</h3>
                      <p className="text-sm text-text-secondary">{currentPayroll.reference} • {currentPayroll.employees} funcionários</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-8">
                    <div className="text-center">
                      <p className="text-sm text-text-muted">Progresso</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="w-32 h-2 bg-bg-tertiary rounded-full overflow-hidden">
                          <div className="h-full bg-accent-primary rounded-full" style={{ width: '72%' }} />
                        </div>
                        <span className="text-sm font-medium">72%</span>
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-text-muted">Vencimento</p>
                      <p className="font-medium text-text-primary">{new Date(currentPayroll.dueDate).toLocaleDateString('pt-BR')}</p>
                    </div>
                    <Button variant="primary" rightIcon={<ChevronRight className="w-4 h-4" />}>
                      Ver Detalhes
                    </Button>
                  </div>
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
                { value: 'periods', label: 'Períodos' },
                { value: 'items', label: 'Itens da Folha' },
                { value: 'reports', label: 'Relatórios' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Card>
            {selectedTab === 'items' && (
              <CardBody className="border-b border-border-subtle">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Input
                      placeholder="Buscar funcionário..."
                      leftIcon={<Search className="w-4 h-4" />}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select
                    options={[
                      { value: 'all', label: 'Todos Departamentos' },
                      { value: 'operations', label: 'Operações' },
                      { value: 'commercial', label: 'Comercial' },
                      { value: 'rh', label: 'RH' },
                    ]}
                    value={filterDepartment}
                    onChange={(value) => setFilterDepartment(value)}
                    className="w-48"
                  />
                  <Select
                    options={[
                      { value: 'all', label: 'Todos Status' },
                      { value: 'calculated', label: 'Calculado' },
                      { value: 'review', label: 'Revisão' },
                      { value: 'error', label: 'Com Erro' },
                    ]}
                    value={filterItemStatus}
                    onChange={(value) => setFilterItemStatus(value)}
                    className="w-40"
                  />
                </div>
              </CardBody>
            )}
            <CardBody className="p-0">
              {selectedTab === 'periods' ? (
                <DataTable
                  columns={periodColumns}
                  data={periods}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'items' ? (
                <DataTable
                  columns={itemColumns}
                  data={payrollItems}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <div className="p-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      { name: 'Resumo da Folha', icon: FileText, desc: 'Relatório consolidado mensal' },
                      { name: 'Guia FGTS', icon: Building2, desc: 'GFIP e guias de recolhimento' },
                      { name: 'Guia INSS', icon: DollarSign, desc: 'GPS e contribuições' },
                      { name: 'Informe de Rendimentos', icon: TrendingUp, desc: 'Para declaração IR' },
                      { name: 'Holerite', icon: Users, desc: 'Contracheques individuais' },
                      { name: 'Provisões', icon: Calculator, desc: 'Férias e 13º salário' },
                    ].map((report, idx) => (
                      <Card key={idx} className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                        <CardBody>
                          <div className="flex items-start gap-3">
                            <div className="p-2 bg-bg-tertiary rounded-lg">
                              <report.icon className="w-5 h-5 text-accent-primary" />
                            </div>
                            <div>
                              <h4 className="font-medium text-text-primary">{report.name}</h4>
                              <p className="text-sm text-text-muted">{report.desc}</p>
                            </div>
                          </div>
                        </CardBody>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* Calculate Payroll Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Calcular Folha de Pagamento"
          description="Configure os parâmetros para o cálculo"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Iniciar Cálculo
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Tipo de Folha"
              options={[
                { value: 'monthly', label: 'Folha Mensal' },
                { value: 'thirteenth', label: '13º Salário' },
                { value: 'vacation', label: 'Férias' },
                { value: 'termination', label: 'Rescisão' },
              ]}
              value={folhaType}
              onChange={(value) => setFolhaType(value)}
            />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Mês de Referência"
                options={[
                  { value: '01', label: 'Janeiro' },
                  { value: '02', label: 'Fevereiro' },
                  { value: '03', label: 'Março' },
                ]}
                value={referenceMonth}
                onChange={(value) => setReferenceMonth(value)}
              />
              <Select
                label="Ano"
                options={[
                  { value: '2026', label: '2026' },
                  { value: '2025', label: '2025' },
                ]}
                value={referenceYear}
                onChange={(value) => setReferenceYear(value)}
              />
            </div>
            <Select
              label="Funcionários"
              options={[
                { value: 'all', label: 'Todos os Funcionários Ativos' },
                { value: 'department', label: 'Por Departamento' },
                { value: 'selected', label: 'Selecionados' },
              ]}
              value={employeesFilter}
              onChange={(value) => setEmployeesFilter(value)}
            />
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="text-sm font-medium text-text-primary mb-2">Itens a Processar</h4>
              <div className="space-y-2">
                {['Salário base', 'Horas extras', 'Adicional noturno', 'Descontos', 'INSS', 'IRRF', 'Benefícios'].map((item) => (
                  <label key={item} className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span className="text-sm text-text-secondary">{item}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
