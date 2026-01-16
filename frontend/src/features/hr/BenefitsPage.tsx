'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Edit2,
  Trash2,
  Eye,
  MoreHorizontal,
  Gift,
  Heart,
  Car,
  Utensils,
  GraduationCap,
  Baby,
  Briefcase,
  DollarSign,
  Users,
  Settings,
  Download,
  CheckCircle2,
  Clock,
  XCircle,
  Calendar,
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
  Textarea,
} from '@/design-system/components';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

// Types
interface Benefit {
  id: string;
  name: string;
  type: 'health' | 'dental' | 'food' | 'transport' | 'education' | 'childcare' | 'life_insurance' | 'other';
  provider: string;
  monthlyValue: number;
  employeeContribution: number;
  companyContribution: number;
  enrolledCount: number;
  eligibleCount: number;
  status: 'active' | 'inactive' | 'pending';
  startDate: string;
}

interface EmployeeBenefit {
  id: string;
  employeeName: string;
  department: string;
  benefit: string;
  benefitType: string;
  value: number;
  status: 'active' | 'pending' | 'cancelled';
  enrollmentDate: string;
}

// Mock Data
const benefits: Benefit[] = [
  { id: '1', name: 'Plano de Saúde Premium', type: 'health', provider: 'Unimed', monthlyValue: 850, employeeContribution: 150, companyContribution: 700, enrolledCount: 180, eligibleCount: 200, status: 'active', startDate: '2024-01-01' },
  { id: '2', name: 'Plano Odontológico', type: 'dental', provider: 'OdontoPrev', monthlyValue: 120, employeeContribution: 30, companyContribution: 90, enrolledCount: 165, eligibleCount: 200, status: 'active', startDate: '2024-01-01' },
  { id: '3', name: 'Vale Refeição', type: 'food', provider: 'Alelo', monthlyValue: 880, employeeContribution: 0, companyContribution: 880, enrolledCount: 195, eligibleCount: 200, status: 'active', startDate: '2024-01-01' },
  { id: '4', name: 'Vale Transporte', type: 'transport', provider: 'VT Express', monthlyValue: 350, employeeContribution: 105, companyContribution: 245, enrolledCount: 145, eligibleCount: 200, status: 'active', startDate: '2024-01-01' },
  { id: '5', name: 'Auxílio Educação', type: 'education', provider: 'Interno', monthlyValue: 500, employeeContribution: 0, companyContribution: 500, enrolledCount: 45, eligibleCount: 200, status: 'active', startDate: '2024-06-01' },
  { id: '6', name: 'Auxílio Creche', type: 'childcare', provider: 'Interno', monthlyValue: 600, employeeContribution: 0, companyContribution: 600, enrolledCount: 28, eligibleCount: 50, status: 'active', startDate: '2024-01-01' },
  { id: '7', name: 'Seguro de Vida', type: 'life_insurance', provider: 'Porto Seguro', monthlyValue: 80, employeeContribution: 0, companyContribution: 80, enrolledCount: 200, eligibleCount: 200, status: 'active', startDate: '2024-01-01' },
];

const employeeBenefits: EmployeeBenefit[] = [
  { id: '1', employeeName: 'Ana Costa', department: 'Comercial', benefit: 'Plano de Saúde Premium', benefitType: 'health', value: 850, status: 'active', enrollmentDate: '2024-01-15' },
  { id: '2', employeeName: 'Carlos Lima', department: 'Financeiro', benefit: 'Vale Refeição', benefitType: 'food', value: 880, status: 'active', enrollmentDate: '2024-01-01' },
  { id: '3', employeeName: 'Roberto Silva', department: 'TI', benefit: 'Auxílio Educação', benefitType: 'education', value: 500, status: 'pending', enrollmentDate: '2026-01-10' },
  { id: '4', employeeName: 'Maria Oliveira', department: 'RH', benefit: 'Plano Odontológico', benefitType: 'dental', value: 120, status: 'active', enrollmentDate: '2024-02-01' },
];

const benefitDistribution = [
  { name: 'Saúde', value: 45, color: '#EF4444' },
  { name: 'Alimentação', value: 25, color: '#F59E0B' },
  { name: 'Transporte', value: 15, color: '#3B82F6' },
  { name: 'Educação', value: 10, color: '#10B981' },
  { name: 'Outros', value: 5, color: '#6B7280' },
];

const costTrend = [
  { month: 'Set', cost: 285000 },
  { month: 'Out', cost: 292000 },
  { month: 'Nov', cost: 298000 },
  { month: 'Dez', cost: 310000 },
  { month: 'Jan', cost: 305000 },
];

const tabs = [
  { id: 'catalog', label: 'Catálogo' },
  { id: 'employees', label: 'Por Colaborador' },
  { id: 'reports', label: 'Relatórios' },
];

const typeIcons = {
  health: Heart,
  dental: Heart,
  food: Utensils,
  transport: Car,
  education: GraduationCap,
  childcare: Baby,
  life_insurance: Briefcase,
  other: Gift,
};

const typeLabels = {
  health: 'Saúde',
  dental: 'Odontológico',
  food: 'Alimentação',
  transport: 'Transporte',
  education: 'Educação',
  childcare: 'Creche',
  life_insurance: 'Seguro de Vida',
  other: 'Outros',
};

const statusColors = {
  active: 'success',
  inactive: 'secondary',
  pending: 'warning',
  cancelled: 'danger',
} as const;

const columns: Column<Benefit>[] = [
  {
    key: 'name',
    header: 'Benefício',
    render: (row) => {
      const Icon = typeIcons[row.type];
      return (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.provider}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => <Badge variant="neutral">{typeLabels[row.type]}</Badge>,
  },
  {
    key: 'monthlyValue',
    header: 'Valor Mensal',
    render: (row) => (
      <span className="font-medium">
        {row.monthlyValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'companyContribution',
    header: 'Empresa',
    render: (row) => (
      <span className="text-success">
        {row.companyContribution.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'enrolledCount',
    header: 'Adesão',
    render: (row) => (
      <div className="flex items-center gap-2">
        <span>{row.enrolledCount}/{row.eligibleCount}</span>
        <div className="w-16 h-2 bg-bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-success rounded-full"
            style={{ width: `${(row.enrolledCount / row.eligibleCount) * 100}%` }}
          />
        </div>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={statusColors[row.status]}>
        {row.status === 'active' ? 'Ativo' : row.status === 'inactive' ? 'Inativo' : 'Pendente'}
      </Badge>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const COLORS = ['#EF4444', '#F59E0B', '#3B82F6', '#10B981', '#6B7280'];

export function BenefitsPage() {
  const [activeTab, setActiveTab] = useState('catalog');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const filteredBenefits = benefits.filter((benefit) =>
    benefit.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Stats
  const totalBenefits = benefits.length;
  const activeBenefits = benefits.filter(b => b.status === 'active').length;
  const totalMonthlyCost = benefits.reduce((acc, b) => acc + (b.companyContribution * b.enrolledCount), 0);
  const avgAdhesion = benefits.reduce((acc, b) => acc + (b.enrolledCount / b.eligibleCount), 0) / benefits.length * 100;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Benefícios
            </h1>
            <p className="text-text-secondary mt-1">
              Administre os benefícios oferecidos aos colaboradores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Novo Benefício
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Benefícios" value={totalBenefits} icon={<Gift className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Benefícios Ativos" value={activeBenefits} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Custo Mensal" value={totalMonthlyCost.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} icon={<DollarSign className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Adesão Média" value={`${avgAdhesion.toFixed(0)}%`} icon={<Users className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Distribuição por Tipo</h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={benefitDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {benefitDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-4">
                {benefitDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-text-muted">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Evolução de Custos</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={costTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} />
                    <Tooltip formatter={(value: number) => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} />
                    <Bar dataKey="cost" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === 'catalog' && (
          <>
            <div className="flex items-center justify-end">
              <Input placeholder="Buscar benefícios..." leftIcon={<Search className="w-4 h-4" />} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable columns={columns} data={filteredBenefits} keyExtractor={(row) => row.id} />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'employees' && (
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Benefícios por Colaborador</h3>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                {employeeBenefits.map((eb) => (
                  <div key={eb.id} className="flex items-center justify-between p-4 rounded-lg border border-border">
                    <div className="flex items-center gap-3">
                      <Avatar name={eb.employeeName} size="sm" />
                      <div>
                        <p className="font-medium text-text-primary">{eb.employeeName}</p>
                        <p className="text-sm text-text-muted">{eb.department}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge variant="neutral">{eb.benefit}</Badge>
                      <span className="font-medium">{eb.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                      <Badge variant={statusColors[eb.status]}>{eb.status === 'active' ? 'Ativo' : eb.status === 'pending' ? 'Pendente' : 'Cancelado'}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'reports' && (
          <Card>
            <CardBody className="p-8 text-center">
              <TrendingUp className="w-12 h-12 mx-auto mb-4 text-text-muted" />
              <h3 className="font-medium text-text-primary mb-2">Relatórios de Benefícios</h3>
              <p className="text-text-muted mb-4">Gere relatórios detalhados sobre custos e adesão</p>
              <Button variant="primary">Gerar Relatório</Button>
            </CardBody>
          </Card>
        )}

        {/* Create Modal */}
        <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Novo Benefício" size="md" footer={<><Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>Cancelar</Button><Button variant="primary">Criar</Button></>}>
          <div className="space-y-4">
            <Input label="Nome do Benefício" placeholder="Ex: Plano de Saúde" required />
            <Select label="Tipo" options={Object.entries(typeLabels).map(([k, v]) => ({ value: k, label: v }))} value="" onChange={() => {}} placeholder="Selecione..." />
            <Input label="Fornecedor" placeholder="Nome do fornecedor" />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Valor Mensal" type="number" placeholder="0.00" />
              <Input label="Contribuição Empresa" type="number" placeholder="0.00" />
            </div>
            <Textarea label="Descrição" placeholder="Descreva o benefício..." rows={3} />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
