'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Plus,
  Briefcase,
  Users,
  DollarSign,
  Building,
  Edit2,
  Trash2,
  Eye,
  MoreHorizontal,
  TrendingUp,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Star,
  Download,
  Filter,
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
  Textarea,
} from '@/design-system/components';
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
} from 'recharts';

// Types
interface JobPosition {
  id: string;
  title: string;
  department: string;
  level: 'junior' | 'pleno' | 'senior' | 'lead' | 'manager' | 'director';
  headcount: number;
  occupied: number;
  salaryRange: { min: number; max: number };
  status: 'active' | 'inactive' | 'hiring';
  createdAt: string;
  description: string;
}

// Mock Data
const positions: JobPosition[] = [
  { id: '1', title: 'Desenvolvedor Full Stack', department: 'TI', level: 'senior', headcount: 5, occupied: 4, salaryRange: { min: 12000, max: 18000 }, status: 'hiring', createdAt: '2024-01-15', description: 'Desenvolvimento de aplicações web' },
  { id: '2', title: 'Analista de RH', department: 'RH', level: 'pleno', headcount: 3, occupied: 3, salaryRange: { min: 5000, max: 8000 }, status: 'active', createdAt: '2024-02-01', description: 'Processos de RH e DP' },
  { id: '3', title: 'Gerente Comercial', department: 'Comercial', level: 'manager', headcount: 2, occupied: 2, salaryRange: { min: 15000, max: 22000 }, status: 'active', createdAt: '2023-06-15', description: 'Gestão da equipe comercial' },
  { id: '4', title: 'Analista Financeiro', department: 'Financeiro', level: 'pleno', headcount: 4, occupied: 3, salaryRange: { min: 6000, max: 10000 }, status: 'hiring', createdAt: '2024-03-01', description: 'Análises financeiras e relatórios' },
  { id: '5', title: 'Técnico de Suporte', department: 'TI', level: 'junior', headcount: 6, occupied: 5, salaryRange: { min: 3000, max: 5000 }, status: 'hiring', createdAt: '2024-04-15', description: 'Suporte técnico ao usuário' },
  { id: '6', title: 'Diretor de Operações', department: 'Operacional', level: 'director', headcount: 1, occupied: 1, salaryRange: { min: 25000, max: 35000 }, status: 'active', createdAt: '2022-01-01', description: 'Direção de operações' },
];

const departmentDistribution = [
  { name: 'TI', value: 35, color: '#3B82F6' },
  { name: 'Comercial', value: 25, color: '#F59E0B' },
  { name: 'Operacional', value: 20, color: '#10B981' },
  { name: 'RH', value: 12, color: '#8B5CF6' },
  { name: 'Financeiro', value: 8, color: '#EF4444' },
];

const levelDistribution = [
  { level: 'Junior', count: 35 },
  { level: 'Pleno', count: 45 },
  { level: 'Sênior', count: 30 },
  { level: 'Lead', count: 12 },
  { level: 'Gerente', count: 10 },
  { level: 'Diretor', count: 5 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'active', label: 'Ativos' },
  { id: 'hiring', label: 'Em Contratação' },
  { id: 'inactive', label: 'Inativos' },
];

const levelLabels = {
  junior: 'Júnior',
  pleno: 'Pleno',
  senior: 'Sênior',
  lead: 'Lead',
  manager: 'Gerente',
  director: 'Diretor',
};

const levelColors = {
  junior: 'info',
  pleno: 'success',
  senior: 'warning',
  lead: 'primary',
  manager: 'danger',
  director: 'secondary',
} as const;

const statusColors = {
  active: 'success',
  inactive: 'secondary',
  hiring: 'warning',
} as const;

const statusLabels = {
  active: 'Ativo',
  inactive: 'Inativo',
  hiring: 'Contratando',
};

const columns: Column<JobPosition>[] = [
  {
    key: 'title',
    header: 'Cargo',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <Briefcase className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.title}</p>
          <p className="text-xs text-text-muted">{row.department}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'level',
    header: 'Nível',
    render: (row) => <Badge variant={levelColors[row.level]}>{levelLabels[row.level]}</Badge>,
  },
  {
    key: 'headcount',
    header: 'Headcount',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Users className="w-4 h-4 text-text-muted" />
        <span>{row.occupied}/{row.headcount}</span>
        {row.occupied < row.headcount && (
          <Badge variant="warning" size="sm">-{row.headcount - row.occupied}</Badge>
        )}
      </div>
    ),
  },
  {
    key: 'salaryRange',
    header: 'Faixa Salarial',
    render: (row) => (
      <div className="text-sm">
        <span className="text-text-muted">
          {row.salaryRange.min.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
        <span className="mx-1">-</span>
        <span className="font-medium">
          {row.salaryRange.max.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={statusColors[row.status]}>
        {statusLabels[row.status]}
      </Badge>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
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

const COLORS = ['#3B82F6', '#F59E0B', '#10B981', '#8B5CF6', '#EF4444'];

export function JobPositionsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newDepartment, setNewDepartment] = useState('');
  const [newLevel, setNewLevel] = useState('');

  const filteredPositions = positions.filter((position) => {
    const matchesSearch = position.title.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && position.status === activeTab;
  });

  // Stats
  const totalPositions = positions.length;
  const activePositions = positions.filter(p => p.status === 'active' || p.status === 'hiring').length;
  const totalHeadcount = positions.reduce((acc, p) => acc + p.headcount, 0);
  const vacancies = positions.reduce((acc, p) => acc + (p.headcount - p.occupied), 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Cargos e Funções
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie a estrutura de cargos da organização
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Novo Cargo
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Cargos" value={totalPositions} icon={<Briefcase className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Cargos Ativos" value={activePositions} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Headcount Total" value={totalHeadcount} icon={<Users className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Vagas Abertas" value={vacancies} icon={<AlertTriangle className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Building className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Distribuição por Departamento</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={departmentDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {departmentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {departmentDistribution.map((item) => (
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
                <h3 className="font-semibold">Distribuição por Nível</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={levelDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="level" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} name="Colaboradores" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex items-center gap-3">
            <Input placeholder="Buscar cargos..." leftIcon={<Search className="w-4 h-4" />} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
            <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>Filtros</Button>
          </div>
        </div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable columns={columns} data={filteredPositions} keyExtractor={(row) => row.id} />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Novo Cargo" size="lg" footer={<><Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>Cancelar</Button><Button variant="primary">Criar Cargo</Button></>}>
          <div className="space-y-4">
            <Input label="Título do Cargo" placeholder="Ex: Desenvolvedor Full Stack" required />
            <div className="grid grid-cols-2 gap-4">
              <Select label="Departamento" options={departmentDistribution.map(d => ({ value: d.name, label: d.name }))} value={newDepartment} onChange={(value) => setNewDepartment(value)} placeholder="Selecione..." />
              <Select label="Nível" options={Object.entries(levelLabels).map(([k, v]) => ({ value: k, label: v }))} value={newLevel} onChange={(value) => setNewLevel(value)} placeholder="Selecione..." />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Input label="Headcount" type="number" placeholder="1" />
              <Input label="Salário Mínimo" type="number" placeholder="5000" />
              <Input label="Salário Máximo" type="number" placeholder="10000" />
            </div>
            <Textarea label="Descrição do Cargo" placeholder="Descreva as responsabilidades e requisitos..." rows={4} />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
