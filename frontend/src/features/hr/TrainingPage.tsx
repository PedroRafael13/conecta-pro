'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Plus,
  GraduationCap,
  BookOpen,
  Video,
  Users,
  Clock,
  Calendar,
  CheckCircle2,
  Play,
  Award,
  Target,
  TrendingUp,
  BarChart2,
  Eye,
  Edit2,
  MoreHorizontal,
  Download,
  Star,
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
interface Training {
  id: string;
  title: string;
  category: 'technical' | 'leadership' | 'compliance' | 'soft_skills' | 'safety';
  format: 'online' | 'presencial' | 'hybrid';
  duration: number;
  instructor: string;
  enrolledCount: number;
  completedCount: number;
  rating: number;
  status: 'active' | 'scheduled' | 'completed' | 'draft';
  startDate: string;
  mandatory: boolean;
}

// Mock Data
const trainings: Training[] = [
  { id: '1', title: 'LGPD e Proteção de Dados', category: 'compliance', format: 'online', duration: 4, instructor: 'Dra. Ana Legal', enrolledCount: 200, completedCount: 185, rating: 4.8, status: 'active', startDate: '2026-01-01', mandatory: true },
  { id: '2', title: 'Liderança e Gestão de Equipes', category: 'leadership', format: 'presencial', duration: 16, instructor: 'Carlos Coach', enrolledCount: 25, completedCount: 20, rating: 4.9, status: 'active', startDate: '2026-01-10', mandatory: false },
  { id: '3', title: 'Segurança do Trabalho - NR35', category: 'safety', format: 'hybrid', duration: 8, instructor: 'Eng. Roberto Seg', enrolledCount: 45, completedCount: 45, rating: 4.5, status: 'completed', startDate: '2025-12-01', mandatory: true },
  { id: '4', title: 'Excel Avançado', category: 'technical', format: 'online', duration: 6, instructor: 'Maria Tech', enrolledCount: 80, completedCount: 62, rating: 4.6, status: 'active', startDate: '2026-01-05', mandatory: false },
  { id: '5', title: 'Comunicação Efetiva', category: 'soft_skills', format: 'presencial', duration: 8, instructor: 'Pedro Comunica', enrolledCount: 30, completedCount: 0, rating: 0, status: 'scheduled', startDate: '2026-02-01', mandatory: false },
];

const categoryDistribution = [
  { name: 'Técnico', value: 35, color: '#3B82F6' },
  { name: 'Compliance', value: 25, color: '#EF4444' },
  { name: 'Liderança', value: 20, color: '#F59E0B' },
  { name: 'Soft Skills', value: 12, color: '#10B981' },
  { name: 'Segurança', value: 8, color: '#8B5CF6' },
];

const completionTrend = [
  { month: 'Set', completed: 145 },
  { month: 'Out', completed: 178 },
  { month: 'Nov', completed: 210 },
  { month: 'Dez', completed: 156 },
  { month: 'Jan', completed: 198 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'active', label: 'Em Andamento' },
  { id: 'scheduled', label: 'Agendados' },
  { id: 'completed', label: 'Concluídos' },
];

const categoryConfig = {
  technical: { label: 'Técnico', color: 'primary' },
  leadership: { label: 'Liderança', color: 'warning' },
  compliance: { label: 'Compliance', color: 'danger' },
  soft_skills: { label: 'Soft Skills', color: 'success' },
  safety: { label: 'Segurança', color: 'info' },
};

const formatLabels = {
  online: 'Online',
  presencial: 'Presencial',
  hybrid: 'Híbrido',
};

const statusColors = {
  active: 'success',
  scheduled: 'warning',
  completed: 'secondary',
  draft: 'neutral',
} as const;

const statusLabels = {
  active: 'Em Andamento',
  scheduled: 'Agendado',
  completed: 'Concluído',
  draft: 'Rascunho',
};

const columns: Column<Training>[] = [
  {
    key: 'title',
    header: 'Treinamento',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <GraduationCap className="w-5 h-5 text-primary" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <p className="font-medium text-text-primary">{row.title}</p>
            {row.mandatory && <Badge variant="danger" size="sm">Obrigatório</Badge>}
          </div>
          <p className="text-xs text-text-muted">{row.instructor}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => {
      const config = categoryConfig[row.category];
      return <Badge variant={config.color as any}>{config.label}</Badge>;
    },
  },
  {
    key: 'format',
    header: 'Formato',
    render: (row) => <Badge variant="neutral">{formatLabels[row.format]}</Badge>,
  },
  {
    key: 'duration',
    header: 'Duração',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-text-muted" />
        <span>{row.duration}h</span>
      </div>
    ),
  },
  {
    key: 'enrolledCount',
    header: 'Progresso',
    render: (row) => (
      <div className="flex items-center gap-2">
        <span className="text-sm">{row.completedCount}/{row.enrolledCount}</span>
        <div className="w-16 h-2 bg-bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-success rounded-full"
            style={{ width: `${row.enrolledCount > 0 ? (row.completedCount / row.enrolledCount) * 100 : 0}%` }}
          />
        </div>
      </div>
    ),
  },
  {
    key: 'rating',
    header: 'Avaliação',
    render: (row) => row.rating > 0 ? (
      <div className="flex items-center gap-1">
        <Star className="w-4 h-4 text-warning fill-warning" />
        <span className="font-medium">{row.rating.toFixed(1)}</span>
      </div>
    ) : <span className="text-text-muted">-</span>,
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

const COLORS = ['#3B82F6', '#EF4444', '#F59E0B', '#10B981', '#8B5CF6'];

export function TrainingPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const filteredTrainings = trainings.filter((training) => {
    const matchesSearch = training.title.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && training.status === activeTab;
  });

  // Stats
  const totalTrainings = trainings.length;
  const activeTrainings = trainings.filter(t => t.status === 'active').length;
  const totalCompleted = trainings.reduce((acc, t) => acc + t.completedCount, 0);
  const avgRating = trainings.filter(t => t.rating > 0).reduce((acc, t) => acc + t.rating, 0) / trainings.filter(t => t.rating > 0).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Treinamentos e Capacitação
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie programas de desenvolvimento dos colaboradores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Relatórios
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Novo Treinamento
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Treinamentos" value={totalTrainings} icon={<GraduationCap className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Em Andamento" value={activeTrainings} icon={<Play className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Conclusões" value={totalCompleted} icon={<Award className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Avaliação Média" value={avgRating.toFixed(1)} icon={<Star className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Distribuição por Categoria</h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={categoryDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {categoryDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {categoryDistribution.map((item) => (
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
                <h3 className="font-semibold">Conclusões por Mês</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={completionTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="completed" fill="#10B981" radius={[4, 4, 0, 0]} name="Conclusões" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <Input placeholder="Buscar treinamentos..." leftIcon={<Search className="w-4 h-4" />} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
        </div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable columns={columns} data={filteredTrainings} keyExtractor={(row) => row.id} />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Novo Treinamento" size="lg" footer={<><Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>Cancelar</Button><Button variant="primary">Criar</Button></>}>
          <div className="space-y-4">
            <Input label="Título do Treinamento" placeholder="Ex: Liderança e Gestão" required />
            <div className="grid grid-cols-2 gap-4">
              <Select label="Categoria" options={Object.entries(categoryConfig).map(([k, v]) => ({ value: k, label: v.label }))} value="" onChange={() => {}} placeholder="Selecione..." />
              <Select label="Formato" options={Object.entries(formatLabels).map(([k, v]) => ({ value: k, label: v }))} value="" onChange={() => {}} placeholder="Selecione..." />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Instrutor" placeholder="Nome do instrutor" />
              <Input label="Duração (horas)" type="number" placeholder="8" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data de Início" type="date" />
              <div className="flex items-center gap-2 mt-6">
                <input type="checkbox" id="mandatory" className="rounded" />
                <label htmlFor="mandatory" className="text-sm">Treinamento obrigatório</label>
              </div>
            </div>
            <Textarea label="Descrição" placeholder="Descreva o conteúdo do treinamento..." rows={3} />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
