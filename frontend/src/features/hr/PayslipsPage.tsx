'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Download,
  Calendar,
  DollarSign,
  FileText,
  Users,
  Mail,
  Printer,
  Eye,
  MoreHorizontal,
  CheckCircle2,
  Clock,
  Send,
  Lock,
  TrendingUp,
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
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Types
interface Payslip {
  id: string;
  employeeName: string;
  department: string;
  month: string;
  grossSalary: number;
  deductions: number;
  netSalary: number;
  status: 'pending' | 'generated' | 'sent' | 'viewed';
  generatedAt: string | null;
  viewedAt: string | null;
}

// Mock Data
const payslips: Payslip[] = [
  { id: '1', employeeName: 'Ana Costa', department: 'Comercial', month: 'Janeiro 2026', grossSalary: 8500, deductions: 2125, netSalary: 6375, status: 'viewed', generatedAt: '2026-01-05', viewedAt: '2026-01-06' },
  { id: '2', employeeName: 'Roberto Silva', department: 'TI', month: 'Janeiro 2026', grossSalary: 12000, deductions: 3600, netSalary: 8400, status: 'sent', generatedAt: '2026-01-05', viewedAt: null },
  { id: '3', employeeName: 'Pedro Santos', department: 'Operacional', month: 'Janeiro 2026', grossSalary: 4500, deductions: 900, netSalary: 3600, status: 'generated', generatedAt: '2026-01-05', viewedAt: null },
  { id: '4', employeeName: 'Maria Oliveira', department: 'RH', month: 'Janeiro 2026', grossSalary: 7500, deductions: 1875, netSalary: 5625, status: 'viewed', generatedAt: '2026-01-05', viewedAt: '2026-01-07' },
  { id: '5', employeeName: 'Carlos Lima', department: 'Financeiro', month: 'Janeiro 2026', grossSalary: 15000, deductions: 4875, netSalary: 10125, status: 'pending', generatedAt: null, viewedAt: null },
];

const monthlyPayroll = [
  { month: 'Set', total: 485000 },
  { month: 'Out', total: 492000 },
  { month: 'Nov', total: 498000 },
  { month: 'Dez', total: 545000 },
  { month: 'Jan', total: 512000 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'pending', label: 'Pendentes' },
  { id: 'generated', label: 'Gerados' },
  { id: 'sent', label: 'Enviados' },
  { id: 'viewed', label: 'Visualizados' },
];

const statusColors = {
  pending: 'secondary',
  generated: 'warning',
  sent: 'info',
  viewed: 'success',
} as const;

const statusLabels = {
  pending: 'Pendente',
  generated: 'Gerado',
  sent: 'Enviado',
  viewed: 'Visualizado',
};

const statusIcons = {
  pending: Clock,
  generated: FileText,
  sent: Send,
  viewed: CheckCircle2,
};

const columns: Column<Payslip>[] = [
  {
    key: 'employeeName',
    header: 'Colaborador',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.employeeName} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.employeeName}</p>
          <p className="text-xs text-text-muted">{row.department}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'month',
    header: 'Competência',
    render: (row) => <Badge variant="neutral">{row.month}</Badge>,
  },
  {
    key: 'grossSalary',
    header: 'Bruto',
    render: (row) => (
      <span className="font-medium">
        {row.grossSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'deductions',
    header: 'Descontos',
    render: (row) => (
      <span className="text-danger">
        -{row.deductions.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'netSalary',
    header: 'Líquido',
    render: (row) => (
      <span className="font-bold text-success">
        {row.netSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const Icon = statusIcons[row.status];
      return (
        <Badge variant={statusColors[row.status]}>
          <Icon className="w-3 h-3 mr-1" />
          {statusLabels[row.status]}
        </Badge>
      );
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Holerite">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Download">
          <Download className="w-4 h-4" />
        </Button>
        {row.status === 'generated' && (
          <Button variant="ghost" size="icon-sm" title="Enviar">
            <Send className="w-4 h-4" />
          </Button>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function PayslipsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMonth, setSelectedMonth] = useState('2026-01');
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);

  const filteredPayslips = payslips.filter((payslip) => {
    const matchesSearch = payslip.employeeName.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && payslip.status === activeTab;
  });

  // Stats
  const totalPayslips = payslips.length;
  const sentPayslips = payslips.filter(p => p.status === 'sent' || p.status === 'viewed').length;
  const totalGross = payslips.reduce((acc, p) => acc + p.grossSalary, 0);
  const totalNet = payslips.reduce((acc, p) => acc + p.netSalary, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Holerites
            </h1>
            <p className="text-text-secondary mt-1">
              Geração e distribuição de contracheques
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              options={[
                { value: '2026-01', label: 'Janeiro 2026' },
                { value: '2025-12', label: 'Dezembro 2025' },
                { value: '2025-11', label: 'Novembro 2025' },
              ]}
              value={selectedMonth}
              onChange={(value) => setSelectedMonth(value)}
              className="w-40"
            />
            <Button variant="secondary" leftIcon={<Mail className="w-4 h-4" />}>
              Enviar Todos
            </Button>
            <Button variant="primary" leftIcon={<FileText className="w-4 h-4" />}>
              Gerar Holerites
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Holerites" value={totalPayslips} icon={<FileText className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Enviados" value={sentPayslips} icon={<Send className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Total Bruto" value={totalGross.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} icon={<DollarSign className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Total Líquido" value={totalNet.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} icon={<DollarSign className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-success" />
              <h3 className="font-semibold">Evolução da Folha de Pagamento</h3>
            </div>
          </CardHeader>
          <CardBody>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyPayroll}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                  <YAxis stroke="var(--color-text-muted)" tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                  <Tooltip formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} />
                  <Bar dataKey="total" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Total" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex items-center gap-3">
            <Input placeholder="Buscar colaborador..." leftIcon={<Search className="w-4 h-4" />} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
            <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>Filtros</Button>
          </div>
        </div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable columns={columns} data={filteredPayslips} keyExtractor={(row) => row.id} onRowClick={(row) => setSelectedPayslip(row)} />
            </CardBody>
          </Card>
        </motion.div>

        {/* Payslip Detail Modal */}
        <Modal isOpen={!!selectedPayslip} onClose={() => setSelectedPayslip(null)} title="Detalhes do Holerite" size="lg" footer={<><Button variant="secondary" onClick={() => setSelectedPayslip(null)}>Fechar</Button><Button variant="secondary" leftIcon={<Printer className="w-4 h-4" />}>Imprimir</Button><Button variant="primary" leftIcon={<Download className="w-4 h-4" />}>Download PDF</Button></>}>
          {selectedPayslip && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between p-4 rounded-lg bg-bg-secondary">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedPayslip.employeeName} size="lg" />
                  <div>
                    <h3 className="font-semibold text-text-primary">{selectedPayslip.employeeName}</h3>
                    <p className="text-sm text-text-muted">{selectedPayslip.department}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant={statusColors[selectedPayslip.status]}>
                    {statusLabels[selectedPayslip.status]}
                  </Badge>
                  <p className="text-sm text-text-muted mt-1">{selectedPayslip.month}</p>
                </div>
              </div>

              {/* Values */}
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg border border-border">
                  <span className="text-text-secondary">Salário Bruto</span>
                  <span className="text-xl font-bold">{selectedPayslip.grossSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                </div>

                <div className="p-4 rounded-lg bg-danger/10 border border-danger/20">
                  <p className="text-sm font-medium text-danger mb-3">Descontos</p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span>INSS</span><span>-R$ {(selectedPayslip.deductions * 0.5).toFixed(2)}</span></div>
                    <div className="flex justify-between"><span>IRRF</span><span>-R$ {(selectedPayslip.deductions * 0.35).toFixed(2)}</span></div>
                    <div className="flex justify-between"><span>Vale Transporte</span><span>-R$ {(selectedPayslip.deductions * 0.1).toFixed(2)}</span></div>
                    <div className="flex justify-between"><span>Plano de Saúde</span><span>-R$ {(selectedPayslip.deductions * 0.05).toFixed(2)}</span></div>
                    <div className="flex justify-between font-medium border-t border-danger/20 pt-2 mt-2">
                      <span>Total Descontos</span>
                      <span>-{selectedPayslip.deductions.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg bg-success/10 border border-success/20">
                  <span className="text-success font-medium">Salário Líquido</span>
                  <span className="text-2xl font-bold text-success">{selectedPayslip.netSalary.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                </div>
              </div>

              {/* Footer Info */}
              <div className="flex items-center gap-4 text-sm text-text-muted">
                {selectedPayslip.generatedAt && (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>Gerado em: {new Date(selectedPayslip.generatedAt).toLocaleDateString('pt-BR')}</span>
                  </div>
                )}
                {selectedPayslip.viewedAt && (
                  <div className="flex items-center gap-2">
                    <Eye className="w-4 h-4" />
                    <span>Visualizado em: {new Date(selectedPayslip.viewedAt).toLocaleDateString('pt-BR')}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
