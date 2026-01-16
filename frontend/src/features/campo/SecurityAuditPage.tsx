'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Shield,
  ShieldAlert,
  ShieldCheck,
  ClipboardCheck,
  FileText,
  Calendar,
  Clock,
  MapPin,
  User,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit2,
  Download,
  MoreHorizontal,
  Camera,
  Building2,
  TrendingUp,
  BarChart2,
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

// Types
interface SecurityAudit {
  id: string;
  title: string;
  location: string;
  client: string;
  auditor: string;
  type: 'routine' | 'special' | 'incident' | 'compliance';
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  scheduledDate: string;
  completedDate: string | null;
  score: number | null;
  findings: number;
  criticalFindings: number;
  photos: number;
  report: string | null;
}

// Mock Data
const audits: SecurityAudit[] = [
  {
    id: '1',
    title: 'Auditoria Trimestral - Shopping Center Norte',
    location: 'São Paulo - SP',
    client: 'Shopping Center Norte',
    auditor: 'Carlos Mendes',
    type: 'routine',
    status: 'completed',
    scheduledDate: '2026-01-15',
    completedDate: '2026-01-15',
    score: 92,
    findings: 5,
    criticalFindings: 0,
    photos: 24,
    report: '/reports/audit-001.pdf',
  },
  {
    id: '2',
    title: 'Auditoria de Incidente - Condomínio Aurora',
    location: 'Guarulhos - SP',
    client: 'Condomínio Aurora',
    auditor: 'Roberto Santos',
    type: 'incident',
    status: 'completed',
    scheduledDate: '2026-01-14',
    completedDate: '2026-01-14',
    score: 75,
    findings: 8,
    criticalFindings: 2,
    photos: 45,
    report: '/reports/audit-002.pdf',
  },
  {
    id: '3',
    title: 'Auditoria de Compliance - Hospital São Lucas',
    location: 'São Paulo - SP',
    client: 'Hospital São Lucas',
    auditor: 'Ana Paula',
    type: 'compliance',
    status: 'in_progress',
    scheduledDate: '2026-01-16',
    completedDate: null,
    score: null,
    findings: 3,
    criticalFindings: 1,
    photos: 12,
    report: null,
  },
  {
    id: '4',
    title: 'Auditoria Mensal - Edifício Corporate',
    location: 'São Paulo - SP',
    client: 'Edifício Corporate Tower',
    auditor: 'Pedro Lima',
    type: 'routine',
    status: 'scheduled',
    scheduledDate: '2026-01-20',
    completedDate: null,
    score: null,
    findings: 0,
    criticalFindings: 0,
    photos: 0,
    report: null,
  },
];

const scoresByCategory = [
  { category: 'Controle de Acesso', score: 95 },
  { category: 'CFTV', score: 88 },
  { category: 'Rondas', score: 92 },
  { category: 'Equipamentos', score: 85 },
  { category: 'Documentação', score: 78 },
  { category: 'Treinamento', score: 90 },
];

const findingsDistribution = [
  { name: 'Baixo', value: 45, color: '#10B981' },
  { name: 'Médio', value: 35, color: '#F59E0B' },
  { name: 'Alto', value: 15, color: '#EF4444' },
  { name: 'Crítico', value: 5, color: '#7C3AED' },
];

const monthlyAudits = [
  { month: 'Set', completed: 12, scheduled: 15 },
  { month: 'Out', completed: 14, scheduled: 14 },
  { month: 'Nov', completed: 11, scheduled: 12 },
  { month: 'Dez', completed: 8, scheduled: 10 },
  { month: 'Jan', completed: 6, scheduled: 12 },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'scheduled', label: 'Agendadas' },
  { id: 'in_progress', label: 'Em Andamento' },
  { id: 'completed', label: 'Concluídas' },
];

const typeLabels = {
  routine: 'Rotina',
  special: 'Especial',
  incident: 'Incidente',
  compliance: 'Compliance',
};

const typeColors = {
  routine: 'info',
  special: 'warning',
  incident: 'danger',
  compliance: 'primary',
} as const;

const statusLabels = {
  scheduled: 'Agendada',
  in_progress: 'Em Andamento',
  completed: 'Concluída',
  cancelled: 'Cancelada',
};

const statusColors = {
  scheduled: 'info',
  in_progress: 'warning',
  completed: 'success',
  cancelled: 'secondary',
} as const;

const columns: Column<SecurityAudit>[] = [
  {
    key: 'title',
    header: 'Auditoria',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${row.type === 'incident' ? 'bg-danger/10' : 'bg-primary/10'}`}>
          {row.type === 'incident' ? (
            <ShieldAlert className="w-5 h-5 text-danger" />
          ) : (
            <ShieldCheck className="w-5 h-5 text-primary" />
          )}
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.title}</p>
          <p className="text-xs text-text-muted">{row.client}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => <Badge variant={typeColors[row.type]}>{typeLabels[row.type]}</Badge>,
  },
  {
    key: 'auditor',
    header: 'Auditor',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.auditor} size="xs" />
        <span className="text-sm">{row.auditor}</span>
      </div>
    ),
  },
  {
    key: 'scheduledDate',
    header: 'Data',
    render: (row) => (
      <div className="flex items-center gap-2 text-sm">
        <Calendar className="w-4 h-4 text-text-muted" />
        <span>{new Date(row.scheduledDate).toLocaleDateString('pt-BR')}</span>
      </div>
    ),
  },
  {
    key: 'score',
    header: 'Score',
    render: (row) => (
      row.score !== null ? (
        <div className="flex items-center gap-2">
          <div className={`px-2 py-1 rounded font-medium ${row.score >= 90 ? 'bg-success/20 text-success' : row.score >= 70 ? 'bg-warning/20 text-warning' : 'bg-danger/20 text-danger'}`}>
            {row.score}%
          </div>
        </div>
      ) : (
        <span className="text-text-muted">-</span>
      )
    ),
  },
  {
    key: 'findings',
    header: 'Achados',
    render: (row) => (
      <div className="flex items-center gap-2">
        <span className="font-medium">{row.findings}</span>
        {row.criticalFindings > 0 && (
          <Badge variant="danger" size="sm">{row.criticalFindings} críticos</Badge>
        )}
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => <Badge variant={statusColors[row.status]}>{statusLabels[row.status]}</Badge>,
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        {row.report && (
          <Button variant="ghost" size="icon-sm" title="Download">
            <Download className="w-4 h-4" />
          </Button>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function SecurityAuditPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedAudit, setSelectedAudit] = useState<SecurityAudit | null>(null);
  const [newClient, setNewClient] = useState('');
  const [newAuditType, setNewAuditType] = useState('');
  const [newAuditor, setNewAuditor] = useState('');

  const filteredAudits = audits.filter((audit) => {
    const matchesSearch = audit.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      audit.client.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && audit.status === activeTab;
  });

  // Stats
  const totalAudits = audits.length;
  const completedAudits = audits.filter((a) => a.status === 'completed').length;
  const avgScore = audits.filter((a) => a.score !== null).reduce((acc, a, _, arr) => acc + (a.score || 0) / arr.length, 0).toFixed(1);
  const criticalFindings = audits.reduce((acc, a) => acc + a.criticalFindings, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Auditoria de Segurança</h1>
            <p className="text-text-secondary mt-1">Gestão de auditorias e inspeções de segurança</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Nova Auditoria
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Auditorias" value={totalAudits} icon={<ClipboardCheck className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Concluídas" value={completedAudits} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Score Médio" value={`${avgScore}%`} icon={<TrendingUp className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Achados Críticos" value={criticalFindings} icon={<AlertTriangle className="w-6 h-6" />} iconColor="danger" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Score por Categoria</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={scoresByCategory}>
                    <PolarGrid stroke="var(--color-border)" />
                    <PolarAngleAxis dataKey="category" tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} />
                    <Radar name="Score" dataKey="score" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.5} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-warning" />
                <h3 className="font-semibold">Achados por Severidade</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={findingsDistribution} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                      {findingsDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-3 mt-2">
                {findingsDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-text-muted">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Auditorias Mensais</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyAudits}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="completed" fill="#10B981" name="Concluídas" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="scheduled" fill="#3B82F6" name="Agendadas" radius={[4, 4, 0, 0]} />
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
            <Input
              placeholder="Buscar auditorias..."
              leftIcon={<Search className="w-4 h-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
            <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
              Filtros
            </Button>
          </div>
        </div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredAudits}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedAudit(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Nova Auditoria"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary">Criar Auditoria</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Título da Auditoria" placeholder="Ex: Auditoria Trimestral - Cliente X" required />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Cliente"
                options={[
                  { value: '1', label: 'Shopping Center Norte' },
                  { value: '2', label: 'Condomínio Aurora' },
                  { value: '3', label: 'Hospital São Lucas' },
                  { value: '4', label: 'Edifício Corporate Tower' },
                ]}
                value={newClient}
                onChange={(value) => setNewClient(value)}
                placeholder="Selecione..."
              />
              <Select
                label="Tipo de Auditoria"
                options={[
                  { value: 'routine', label: 'Rotina' },
                  { value: 'special', label: 'Especial' },
                  { value: 'incident', label: 'Incidente' },
                  { value: 'compliance', label: 'Compliance' },
                ]}
                value={newAuditType}
                onChange={(value) => setNewAuditType(value)}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Auditor Responsável"
                options={[
                  { value: '1', label: 'Carlos Mendes' },
                  { value: '2', label: 'Roberto Santos' },
                  { value: '3', label: 'Ana Paula' },
                  { value: '4', label: 'Pedro Lima' },
                ]}
                value={newAuditor}
                onChange={(value) => setNewAuditor(value)}
                placeholder="Selecione..."
              />
              <Input label="Data Agendada" type="date" required />
            </div>
            <Input label="Local" placeholder="São Paulo - SP" leftIcon={<MapPin className="w-4 h-4" />} />
            <Textarea label="Observações" placeholder="Informações adicionais sobre a auditoria..." rows={3} />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={!!selectedAudit}
          onClose={() => setSelectedAudit(null)}
          title="Detalhes da Auditoria"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedAudit(null)}>
                Fechar
              </Button>
              {selectedAudit?.report && (
                <Button variant="primary" leftIcon={<Download className="w-4 h-4" />}>
                  Download Relatório
                </Button>
              )}
            </>
          }
        >
          {selectedAudit && (
            <div className="space-y-6">
              {/* Header */}
              <div className="p-4 rounded-lg bg-bg-secondary">
                <div className="flex items-center justify-between mb-3">
                  <Badge variant={typeColors[selectedAudit.type]}>{typeLabels[selectedAudit.type]}</Badge>
                  <Badge variant={statusColors[selectedAudit.status]}>{statusLabels[selectedAudit.status]}</Badge>
                </div>
                <h3 className="text-lg font-semibold text-text-primary">{selectedAudit.title}</h3>
                <p className="text-text-secondary mt-1">{selectedAudit.client}</p>
              </div>

              {/* Score */}
              {selectedAudit.score !== null && (
                <div className={`p-6 rounded-lg text-center ${selectedAudit.score >= 90 ? 'bg-success/10' : selectedAudit.score >= 70 ? 'bg-warning/10' : 'bg-danger/10'}`}>
                  <p className="text-sm text-text-muted mb-1">Score da Auditoria</p>
                  <p className={`text-5xl font-bold ${selectedAudit.score >= 90 ? 'text-success' : selectedAudit.score >= 70 ? 'text-warning' : 'text-danger'}`}>
                    {selectedAudit.score}%
                  </p>
                </div>
              )}

              {/* Details */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <User className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-xs text-text-muted">Auditor</p>
                    <p className="text-sm font-medium text-text-primary">{selectedAudit.auditor}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <MapPin className="w-5 h-5 text-success" />
                  <div>
                    <p className="text-xs text-text-muted">Local</p>
                    <p className="text-sm font-medium text-text-primary">{selectedAudit.location}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Calendar className="w-5 h-5 text-warning" />
                  <div>
                    <p className="text-xs text-text-muted">Data Agendada</p>
                    <p className="text-sm font-medium text-text-primary">{new Date(selectedAudit.scheduledDate).toLocaleDateString('pt-BR')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Camera className="w-5 h-5 text-info" />
                  <div>
                    <p className="text-xs text-text-muted">Fotos</p>
                    <p className="text-sm font-medium text-text-primary">{selectedAudit.photos} registradas</p>
                  </div>
                </div>
              </div>

              {/* Findings */}
              <div className="p-4 rounded-lg border border-border">
                <h4 className="font-medium text-text-primary mb-3">Achados da Auditoria</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary">
                    <span className="text-text-muted">Total de Achados</span>
                    <Badge variant="info">{selectedAudit.findings}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary">
                    <span className="text-text-muted">Achados Críticos</span>
                    <Badge variant={selectedAudit.criticalFindings > 0 ? 'danger' : 'success'}>{selectedAudit.criticalFindings}</Badge>
                  </div>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
