'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Gavel,
  FileText,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  TrendingUp,
  DollarSign,
  Building2,
  Target,
  Award,
  Search,
  Filter,
  Eye,
  Plus,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Badge,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  Input,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Types
interface Bidding {
  id: string;
  number: string;
  title: string;
  agency: string;
  modality: 'pregao_eletronico' | 'pregao_presencial' | 'concorrencia' | 'tomada_precos' | 'convite' | 'dispensa' | 'inexigibilidade';
  status: 'aberto' | 'em_analise' | 'proposta_enviada' | 'aguardando_resultado' | 'ganho' | 'perdido' | 'cancelado';
  estimatedValue: number;
  deadline: string;
  openingDate: string;
  ourProposal: number | null;
  winningValue: number | null;
}

// Mock Data
const biddings: Bidding[] = [
  {
    id: '1',
    number: 'PE-001/2026',
    title: 'Serviços de vigilância patrimonial armada e desarmada',
    agency: 'Prefeitura Municipal de São Paulo',
    modality: 'pregao_eletronico',
    status: 'aberto',
    estimatedValue: 2500000,
    deadline: '2026-01-20',
    openingDate: '2026-01-25',
    ourProposal: null,
    winningValue: null,
  },
  {
    id: '2',
    number: 'PE-002/2026',
    title: 'Instalação e manutenção de CFTV',
    agency: 'Governo do Estado de SP',
    modality: 'pregao_eletronico',
    status: 'proposta_enviada',
    estimatedValue: 850000,
    deadline: '2026-01-15',
    openingDate: '2026-01-18',
    ourProposal: 780000,
    winningValue: null,
  },
  {
    id: '3',
    number: 'CC-003/2026',
    title: 'Segurança para evento municipal',
    agency: 'Câmara Municipal',
    modality: 'concorrencia',
    status: 'aguardando_resultado',
    estimatedValue: 180000,
    deadline: '2026-01-10',
    openingDate: '2026-01-12',
    ourProposal: 165000,
    winningValue: null,
  },
  {
    id: '4',
    number: 'PE-015/2025',
    title: 'Monitoramento eletrônico de frotas',
    agency: 'Secretaria de Transportes',
    modality: 'pregao_eletronico',
    status: 'ganho',
    estimatedValue: 420000,
    deadline: '2025-12-15',
    openingDate: '2025-12-20',
    ourProposal: 385000,
    winningValue: 385000,
  },
  {
    id: '5',
    number: 'TP-008/2025',
    title: 'Controle de acesso predial',
    agency: 'Tribunal de Justiça',
    modality: 'tomada_precos',
    status: 'perdido',
    estimatedValue: 320000,
    deadline: '2025-12-01',
    openingDate: '2025-12-10',
    ourProposal: 295000,
    winningValue: 278000,
  },
];

const monthlyData = [
  { month: 'Ago', participacoes: 8, ganhos: 3, valor: 450000 },
  { month: 'Set', participacoes: 12, ganhos: 5, valor: 680000 },
  { month: 'Out', participacoes: 10, ganhos: 4, valor: 520000 },
  { month: 'Nov', participacoes: 15, ganhos: 7, valor: 920000 },
  { month: 'Dez', participacoes: 11, ganhos: 5, valor: 780000 },
  { month: 'Jan', participacoes: 9, ganhos: 4, valor: 640000 },
];

const modalityData = [
  { name: 'Pregão Eletrônico', value: 45, color: '#6366f1' },
  { name: 'Pregão Presencial', value: 15, color: '#8b5cf6' },
  { name: 'Concorrência', value: 12, color: '#10b981' },
  { name: 'Tomada de Preços', value: 18, color: '#f59e0b' },
  { name: 'Outros', value: 10, color: '#64748b' },
];

const statusConfig = {
  aberto: { label: 'Aberto', color: 'info' as const },
  em_analise: { label: 'Em Análise', color: 'warning' as const },
  proposta_enviada: { label: 'Proposta Enviada', color: 'primary' as const },
  aguardando_resultado: { label: 'Aguardando Resultado', color: 'warning' as const },
  ganho: { label: 'Ganho', color: 'success' as const },
  perdido: { label: 'Perdido', color: 'danger' as const },
  cancelado: { label: 'Cancelado', color: 'neutral' as const },
};

const modalityConfig = {
  pregao_eletronico: 'Pregão Eletrônico',
  pregao_presencial: 'Pregão Presencial',
  concorrencia: 'Concorrência',
  tomada_precos: 'Tomada de Preços',
  convite: 'Convite',
  dispensa: 'Dispensa',
  inexigibilidade: 'Inexigibilidade',
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const recentColumns: Column<Bidding>[] = [
  {
    key: 'number',
    header: 'Número',
    render: (row) => (
      <span className="font-mono text-sm font-medium text-accent-primary">{row.number}</span>
    ),
  },
  {
    key: 'title',
    header: 'Objeto',
    render: (row) => (
      <div className="max-w-[300px]">
        <p className="text-sm text-text-primary truncate">{row.title}</p>
        <p className="text-xs text-text-muted">{row.agency}</p>
      </div>
    ),
  },
  {
    key: 'modality',
    header: 'Modalidade',
    render: (row) => (
      <span className="text-sm">{modalityConfig[row.modality]}</span>
    ),
  },
  {
    key: 'value',
    header: 'Valor Estimado',
    render: (row) => (
      <span className="font-medium">{formatCurrency(row.estimatedValue)}</span>
    ),
  },
  {
    key: 'deadline',
    header: 'Prazo',
    render: (row) => {
      const isUrgent = new Date(row.deadline) < new Date(Date.now() + 3 * 24 * 60 * 60 * 1000);
      return (
        <div className="flex items-center gap-2">
          <Calendar className={`w-4 h-4 ${isUrgent ? 'text-accent-danger' : 'text-text-muted'}`} />
          <span className={isUrgent ? 'text-accent-danger font-medium' : ''}>{row.deadline}</span>
        </div>
      );
    },
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
    render: () => (
      <Button variant="ghost" size="icon-sm">
        <Eye className="w-4 h-4" />
      </Button>
    ),
  },
];

export function BiddingDashboardPage() {
  // Stats
  const totalOpen = biddings.filter(b => b.status === 'aberto' || b.status === 'em_analise').length;
  const pendingResults = biddings.filter(b => b.status === 'aguardando_resultado' || b.status === 'proposta_enviada').length;
  const totalWon = biddings.filter(b => b.status === 'ganho').length;
  const totalLost = biddings.filter(b => b.status === 'perdido').length;
  const winRate = Math.round((totalWon / (totalWon + totalLost)) * 100);
  const totalWonValue = biddings.filter(b => b.status === 'ganho').reduce((acc, b) => acc + (b.winningValue || 0), 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Licitações
            </h1>
            <p className="text-text-secondary mt-1">
              Acompanhe processos licitatórios e oportunidades
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Search className="w-4 h-4" />}>
              Buscar Editais
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
              Nova Licitação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Em Aberto"
              value={totalOpen}
              icon={<Gavel className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Aguardando"
              value={pendingResults}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Ganhas"
              value={totalWon}
              icon={<Award className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Perdidas"
              value={totalLost}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Taxa de Sucesso"
              value={`${winRate}%`}
              icon={<Target className="w-6 h-6" />}
              iconColor={winRate >= 50 ? 'success' : 'warning'}
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <StatCard
              title="Valor Ganho"
              value={formatCurrency(totalWonValue)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="col-span-2"
          >
            <Card className="h-full">
              <CardHeader
                title="Desempenho Mensal"
                subtitle="Participações e vitórias nos últimos 6 meses"
              />
              <CardBody>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={monthlyData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                      <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                      <Legend />
                      <Bar dataKey="participacoes" name="Participações" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="ganhos" name="Vitórias" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Card className="h-full">
              <CardHeader
                title="Por Modalidade"
                subtitle="Distribuição de participações"
              />
              <CardBody>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={modalityData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {modalityData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#12121a',
                          border: '1px solid #2d2d3d',
                          borderRadius: '8px',
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        </div>

        {/* Urgent Deadlines */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <Card>
            <CardHeader
              title="Prazos Próximos"
              subtitle="Licitações com prazo nos próximos 7 dias"
              action={
                <Button variant="outline" size="sm">
                  Ver Todas
                </Button>
              }
            />
            <CardBody className="p-0">
              <DataTable
                columns={recentColumns}
                data={biddings.filter(b =>
                  (b.status === 'aberto' || b.status === 'em_analise') &&
                  new Date(b.deadline) <= new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                )}
                keyExtractor={(row) => row.id}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
          <Card>
            <CardHeader
              title="Licitações Recentes"
              subtitle="Últimas atualizações em processos"
              action={
                <Button variant="outline" size="sm">
                  Ver Todas
                </Button>
              }
            />
            <CardBody className="p-0">
              <DataTable
                columns={recentColumns}
                data={biddings}
                keyExtractor={(row) => row.id}
              />
            </CardBody>
          </Card>
        </motion.div>
      </div>
    </MainLayout>
  );
}
