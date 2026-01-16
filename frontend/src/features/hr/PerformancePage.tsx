'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Plus,
  Target,
  Award,
  TrendingUp,
  TrendingDown,
  Users,
  Star,
  BarChart2,
  Calendar,
  CheckCircle2,
  Clock,
  Eye,
  Edit2,
  MoreHorizontal,
  Download,
  MessageSquare,
  ArrowUp,
  ArrowDown,
  Minus,
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

// Types
interface PerformanceReview {
  id: string;
  employeeName: string;
  department: string;
  reviewPeriod: string;
  overallScore: number;
  previousScore: number;
  trend: 'up' | 'down' | 'stable';
  status: 'completed' | 'in_progress' | 'pending' | 'overdue';
  reviewer: string;
  completedAt: string | null;
  goals: { total: number; achieved: number };
}

interface Competency {
  name: string;
  score: number;
  maxScore: number;
}

// Mock Data
const reviews: PerformanceReview[] = [
  { id: '1', employeeName: 'Ana Costa', department: 'Comercial', reviewPeriod: 'Q4 2025', overallScore: 4.5, previousScore: 4.2, trend: 'up', status: 'completed', reviewer: 'Carlos Lima', completedAt: '2026-01-10', goals: { total: 5, achieved: 4 } },
  { id: '2', employeeName: 'Roberto Silva', department: 'TI', reviewPeriod: 'Q4 2025', overallScore: 4.8, previousScore: 4.6, trend: 'up', status: 'completed', reviewer: 'Maria Oliveira', completedAt: '2026-01-08', goals: { total: 6, achieved: 6 } },
  { id: '3', employeeName: 'Pedro Santos', department: 'Operacional', reviewPeriod: 'Q4 2025', overallScore: 3.8, previousScore: 4.0, trend: 'down', status: 'completed', reviewer: 'Ana Costa', completedAt: '2026-01-12', goals: { total: 4, achieved: 3 } },
  { id: '4', employeeName: 'Maria Oliveira', department: 'RH', reviewPeriod: 'Q4 2025', overallScore: 0, previousScore: 4.4, trend: 'stable', status: 'in_progress', reviewer: 'Carlos Lima', completedAt: null, goals: { total: 5, achieved: 0 } },
  { id: '5', employeeName: 'Carlos Lima', department: 'Financeiro', reviewPeriod: 'Q4 2025', overallScore: 0, previousScore: 4.3, trend: 'stable', status: 'pending', reviewer: 'Roberto Silva', completedAt: null, goals: { total: 4, achieved: 0 } },
];

const competencies: Competency[] = [
  { name: 'Liderança', score: 4.2, maxScore: 5 },
  { name: 'Comunicação', score: 4.5, maxScore: 5 },
  { name: 'Técnico', score: 4.8, maxScore: 5 },
  { name: 'Trabalho em Equipe', score: 4.3, maxScore: 5 },
  { name: 'Iniciativa', score: 4.0, maxScore: 5 },
  { name: 'Gestão de Tempo', score: 3.8, maxScore: 5 },
];

const departmentScores = [
  { dept: 'TI', score: 4.6 },
  { dept: 'Comercial', score: 4.3 },
  { dept: 'RH', score: 4.4 },
  { dept: 'Financeiro', score: 4.2 },
  { dept: 'Operacional', score: 3.9 },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'completed', label: 'Concluídas' },
  { id: 'in_progress', label: 'Em Andamento' },
  { id: 'pending', label: 'Pendentes' },
];

const statusColors = {
  completed: 'success',
  in_progress: 'warning',
  pending: 'secondary',
  overdue: 'danger',
} as const;

const statusLabels = {
  completed: 'Concluída',
  in_progress: 'Em Andamento',
  pending: 'Pendente',
  overdue: 'Atrasada',
};

const trendIcons = {
  up: ArrowUp,
  down: ArrowDown,
  stable: Minus,
};

const trendColors = {
  up: 'text-success',
  down: 'text-danger',
  stable: 'text-text-muted',
};

const columns: Column<PerformanceReview>[] = [
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
    key: 'reviewPeriod',
    header: 'Período',
    render: (row) => <Badge variant="neutral">{row.reviewPeriod}</Badge>,
  },
  {
    key: 'overallScore',
    header: 'Nota',
    render: (row) => {
      if (row.overallScore === 0) return <span className="text-text-muted">-</span>;
      const TrendIcon = trendIcons[row.trend];
      return (
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-warning fill-warning" />
            <span className="font-bold text-lg">{row.overallScore.toFixed(1)}</span>
          </div>
          <TrendIcon className={`w-4 h-4 ${trendColors[row.trend]}`} />
        </div>
      );
    },
  },
  {
    key: 'goals',
    header: 'Metas',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Target className="w-4 h-4 text-text-muted" />
        <span>{row.goals.achieved}/{row.goals.total}</span>
        <div className="w-12 h-2 bg-bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-success rounded-full"
            style={{ width: `${row.goals.total > 0 ? (row.goals.achieved / row.goals.total) * 100 : 0}%` }}
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
        {statusLabels[row.status]}
      </Badge>
    ),
  },
  {
    key: 'reviewer',
    header: 'Avaliador',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.reviewer} size="xs" />
        <span className="text-sm">{row.reviewer}</span>
      </div>
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
        <Button variant="ghost" size="icon-sm" title="Feedback">
          <MessageSquare className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function PerformancePage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isNewCycleModalOpen, setIsNewCycleModalOpen] = useState(false);

  const filteredReviews = reviews.filter((review) => {
    const matchesSearch = review.employeeName.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && review.status === activeTab;
  });

  // Stats
  const totalReviews = reviews.length;
  const completedReviews = reviews.filter(r => r.status === 'completed').length;
  const avgScore = reviews.filter(r => r.overallScore > 0).reduce((acc, r) => acc + r.overallScore, 0) / reviews.filter(r => r.overallScore > 0).length;
  const goalsAchieved = reviews.reduce((acc, r) => acc + r.goals.achieved, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Avaliação de Desempenho
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie ciclos de avaliação e acompanhe o desempenho
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Relatórios
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsNewCycleModalOpen(true)}>
              Novo Ciclo
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Avaliações" value={totalReviews} icon={<BarChart2 className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Concluídas" value={completedReviews} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Nota Média" value={avgScore.toFixed(1)} icon={<Star className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Metas Alcançadas" value={goalsAchieved} icon={<Target className="w-6 h-6" />} iconColor="info" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Competências Médias</h3>
            </CardHeader>
            <CardBody>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={competencies}>
                    <PolarGrid stroke="var(--color-border)" />
                    <PolarAngleAxis dataKey="name" tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 5]} tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} />
                    <Radar name="Score" dataKey="score" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="font-semibold">Nota por Departamento</h3>
            </CardHeader>
            <CardBody>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={departmentScores} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis type="number" domain={[0, 5]} stroke="var(--color-text-muted)" />
                    <YAxis type="category" dataKey="dept" stroke="var(--color-text-muted)" width={80} />
                    <Tooltip />
                    <Bar dataKey="score" fill="#10B981" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Current Cycle Info */}
        <Card className="border-l-4 border-l-primary">
          <CardBody className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-primary/10">
                  <Calendar className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-medium text-text-primary">Ciclo Atual: Q4 2025</h3>
                  <p className="text-sm text-text-muted">Período de avaliação: 01/10/2025 - 31/12/2025</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-success">{completedReviews}</p>
                  <p className="text-xs text-text-muted">Concluídas</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-warning">{reviews.filter(r => r.status === 'in_progress').length}</p>
                  <p className="text-xs text-text-muted">Em Andamento</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-secondary">{reviews.filter(r => r.status === 'pending').length}</p>
                  <p className="text-xs text-text-muted">Pendentes</p>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <Input placeholder="Buscar colaborador..." leftIcon={<Search className="w-4 h-4" />} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
        </div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable columns={columns} data={filteredReviews} keyExtractor={(row) => row.id} />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Cycle Modal */}
        <Modal isOpen={isNewCycleModalOpen} onClose={() => setIsNewCycleModalOpen(false)} title="Novo Ciclo de Avaliação" size="md" footer={<><Button variant="secondary" onClick={() => setIsNewCycleModalOpen(false)}>Cancelar</Button><Button variant="primary">Criar Ciclo</Button></>}>
          <div className="space-y-4">
            <Input label="Nome do Ciclo" placeholder="Ex: Q1 2026" required />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data Início" type="date" />
              <Input label="Data Fim" type="date" />
            </div>
            <Select label="Modelo de Avaliação" options={[{ value: '360', label: 'Avaliação 360°' }, { value: 'top-down', label: 'Top-Down' }, { value: 'self', label: 'Autoavaliação' }]} value="" onChange={() => {}} placeholder="Selecione..." />
            <Textarea label="Descrição" placeholder="Objetivos e instruções do ciclo..." rows={3} />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
