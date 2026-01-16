'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  FileText,
  Users,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Eye,
  MoreHorizontal,
  Download,
  Mail,
  MessageSquare,
  Star,
  ThumbsUp,
  ThumbsDown,
  Calendar,
  Briefcase,
  ChevronRight,
  ArrowRight,
  UserCheck,
  UserX,
  Send,
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
  LineChart,
  Line,
} from 'recharts';

// Types
interface Application {
  id: string;
  candidateName: string;
  candidateEmail: string;
  position: string;
  department: string;
  appliedAt: string;
  source: 'linkedin' | 'indeed' | 'site' | 'referral' | 'agency';
  status: 'new' | 'screening' | 'interview' | 'test' | 'offer' | 'hired' | 'rejected' | 'withdrawn';
  stage: number;
  totalStages: number;
  lastActivity: string;
  rating: number;
  notes: string;
  cvUrl: string | null;
  coverLetter: string | null;
}

// Mock Data
const applications: Application[] = [
  {
    id: '1',
    candidateName: 'Lucas Oliveira',
    candidateEmail: 'lucas.oliveira@email.com',
    position: 'Vigilante',
    department: 'Operações',
    appliedAt: '2026-01-10',
    source: 'linkedin',
    status: 'interview',
    stage: 3,
    totalStages: 5,
    lastActivity: '2026-01-15',
    rating: 4,
    notes: 'Entrevista técnica agendada para 17/01',
    cvUrl: '/cv/lucas-oliveira.pdf',
    coverLetter: 'Tenho 5 anos de experiência na área...',
  },
  {
    id: '2',
    candidateName: 'Amanda Costa',
    candidateEmail: 'amanda.costa@email.com',
    position: 'Analista Comercial',
    department: 'Comercial',
    appliedAt: '2026-01-08',
    source: 'site',
    status: 'test',
    stage: 4,
    totalStages: 5,
    lastActivity: '2026-01-14',
    rating: 5,
    notes: 'Aguardando resultado do teste prático',
    cvUrl: '/cv/amanda-costa.pdf',
    coverLetter: null,
  },
  {
    id: '3',
    candidateName: 'Roberto Mendes',
    candidateEmail: 'roberto.mendes@email.com',
    position: 'Supervisor de Segurança',
    department: 'Operações',
    appliedAt: '2025-12-20',
    source: 'referral',
    status: 'hired',
    stage: 5,
    totalStages: 5,
    lastActivity: '2026-01-15',
    rating: 5,
    notes: 'Contratado em 15/01/2026',
    cvUrl: '/cv/roberto-mendes.pdf',
    coverLetter: null,
  },
  {
    id: '4',
    candidateName: 'Juliana Santos',
    candidateEmail: 'juliana.santos@email.com',
    position: 'Estagiário Financeiro',
    department: 'Financeiro',
    appliedAt: '2026-01-15',
    source: 'site',
    status: 'screening',
    stage: 2,
    totalStages: 4,
    lastActivity: '2026-01-16',
    rating: 3,
    notes: 'CV em análise pelo gestor',
    cvUrl: '/cv/juliana-santos.pdf',
    coverLetter: 'Estou cursando Contabilidade na FATEC...',
  },
  {
    id: '5',
    candidateName: 'Pedro Almeida',
    candidateEmail: 'pedro.almeida@email.com',
    position: 'Vigilante',
    department: 'Operações',
    appliedAt: '2026-01-05',
    source: 'agency',
    status: 'rejected',
    stage: 2,
    totalStages: 5,
    lastActivity: '2026-01-10',
    rating: 2,
    notes: 'Não compareceu à entrevista',
    cvUrl: '/cv/pedro-almeida.pdf',
    coverLetter: null,
  },
  {
    id: '6',
    candidateName: 'Maria Fernanda',
    candidateEmail: 'maria.fernanda@email.com',
    position: 'Analista de RH',
    department: 'RH',
    appliedAt: '2026-01-12',
    source: 'linkedin',
    status: 'new',
    stage: 1,
    totalStages: 5,
    lastActivity: '2026-01-12',
    rating: 0,
    notes: '',
    cvUrl: '/cv/maria-fernanda.pdf',
    coverLetter: null,
  },
];

const statusDistribution = [
  { name: 'Novas', value: 15, color: '#6B7280' },
  { name: 'Triagem', value: 25, color: '#3B82F6' },
  { name: 'Entrevista', value: 18, color: '#8B5CF6' },
  { name: 'Teste', value: 8, color: '#F59E0B' },
  { name: 'Proposta', value: 5, color: '#10B981' },
];

const weeklyApplications = [
  { week: 'Sem 1', applications: 28 },
  { week: 'Sem 2', applications: 35 },
  { week: 'Sem 3', applications: 42 },
  { week: 'Sem 4', applications: 31 },
];

const conversionFunnel = [
  { stage: 'Candidaturas', count: 150 },
  { stage: 'Triagem', count: 80 },
  { stage: 'Entrevistas', count: 35 },
  { stage: 'Testes', count: 20 },
  { stage: 'Propostas', count: 12 },
  { stage: 'Contratados', count: 8 },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'new', label: 'Novas' },
  { id: 'in_progress', label: 'Em Andamento' },
  { id: 'hired', label: 'Contratados' },
  { id: 'rejected', label: 'Rejeitadas' },
];

const sourceLabels = {
  linkedin: 'LinkedIn',
  indeed: 'Indeed',
  site: 'Site',
  referral: 'Indicação',
  agency: 'Agência',
};

const sourceColors = {
  linkedin: 'info',
  indeed: 'primary',
  site: 'success',
  referral: 'warning',
  agency: 'secondary',
} as const;

const statusLabels = {
  new: 'Nova',
  screening: 'Triagem',
  interview: 'Entrevista',
  test: 'Teste',
  offer: 'Proposta',
  hired: 'Contratado',
  rejected: 'Rejeitada',
  withdrawn: 'Desistência',
};

const statusColors = {
  new: 'neutral',
  screening: 'info',
  interview: 'primary',
  test: 'warning',
  offer: 'success',
  hired: 'success',
  rejected: 'danger',
  withdrawn: 'secondary',
} as const;

const pipelineStages = ['Nova', 'Triagem', 'Entrevista', 'Teste', 'Proposta', 'Contratado'];

const columns: Column<Application>[] = [
  {
    key: 'candidateName',
    header: 'Candidato',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.candidateName} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.candidateName}</p>
          <p className="text-xs text-text-muted">{row.candidateEmail}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'position',
    header: 'Vaga',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.position}</p>
        <p className="text-xs text-text-muted">{row.department}</p>
      </div>
    ),
  },
  {
    key: 'appliedAt',
    header: 'Data',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Calendar className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{new Date(row.appliedAt).toLocaleDateString('pt-BR')}</span>
      </div>
    ),
  },
  {
    key: 'source',
    header: 'Origem',
    render: (row) => <Badge variant={sourceColors[row.source]}>{sourceLabels[row.source]}</Badge>,
  },
  {
    key: 'stage',
    header: 'Progresso',
    render: (row) => (
      <div className="flex items-center gap-2">
        <div className="w-24 h-2 bg-bg-secondary rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${row.status === 'rejected' || row.status === 'withdrawn' ? 'bg-danger' : 'bg-primary'}`}
            style={{ width: `${(row.stage / row.totalStages) * 100}%` }}
          />
        </div>
        <span className="text-xs text-text-muted">{row.stage}/{row.totalStages}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => <Badge variant={statusColors[row.status]}>{statusLabels[row.status]}</Badge>,
  },
  {
    key: 'rating',
    header: 'Avaliação',
    render: (row) => (
      row.rating > 0 ? (
        <div className="flex items-center gap-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              className={`w-3 h-3 ${i < row.rating ? 'text-accent-warning fill-accent-warning' : 'text-text-muted'}`}
            />
          ))}
        </div>
      ) : (
        <span className="text-xs text-text-muted">Não avaliado</span>
      )
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status !== 'hired' && row.status !== 'rejected' && row.status !== 'withdrawn' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Avançar">
              <ArrowRight className="w-4 h-4 text-success" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Rejeitar">
              <XCircle className="w-4 h-4 text-danger" />
            </Button>
          </>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function ApplicationsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);

  const filteredApplications = applications.filter((app) => {
    const matchesSearch =
      app.candidateName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.position.toLowerCase().includes(searchTerm.toLowerCase());

    switch (activeTab) {
      case 'new':
        return matchesSearch && app.status === 'new';
      case 'in_progress':
        return matchesSearch && ['screening', 'interview', 'test', 'offer'].includes(app.status);
      case 'hired':
        return matchesSearch && app.status === 'hired';
      case 'rejected':
        return matchesSearch && (app.status === 'rejected' || app.status === 'withdrawn');
      default:
        return matchesSearch;
    }
  });

  // Stats
  const totalApplications = applications.length;
  const newApplications = applications.filter((a) => a.status === 'new').length;
  const inProgress = applications.filter((a) => ['screening', 'interview', 'test', 'offer'].includes(a.status)).length;
  const hiredCount = applications.filter((a) => a.status === 'hired').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Candidaturas</h1>
            <p className="text-text-secondary mt-1">Acompanhe todas as candidaturas e seu progresso</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
              Enviar Feedback em Massa
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Candidaturas" value={totalApplications} icon={<FileText className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Novas" value={newApplications} icon={<AlertCircle className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Em Andamento" value={inProgress} icon={<Clock className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Contratados" value={hiredCount} icon={<UserCheck className="w-6 h-6" />} iconColor="success" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-3 gap-6">
          {/* Conversion Funnel */}
          <Card className="col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Funil de Conversão</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                {conversionFunnel.map((stage, index) => {
                  const maxCount = conversionFunnel[0].count;
                  const width = (stage.count / maxCount) * 100;
                  const conversionRate = index > 0
                    ? ((stage.count / conversionFunnel[index - 1].count) * 100).toFixed(0)
                    : 100;
                  return (
                    <div key={stage.stage} className="flex items-center gap-4">
                      <div className="w-24 text-sm text-text-secondary">{stage.stage}</div>
                      <div className="flex-1 relative">
                        <div className="h-8 bg-bg-secondary rounded-full overflow-hidden">
                          <motion.div
                            className="h-full bg-gradient-to-r from-primary to-primary/60 flex items-center justify-end pr-3"
                            initial={{ width: 0 }}
                            animate={{ width: `${width}%` }}
                            transition={{ delay: index * 0.1, duration: 0.5 }}
                          >
                            {width > 20 && (
                              <span className="text-sm font-medium text-white">{stage.count}</span>
                            )}
                          </motion.div>
                        </div>
                      </div>
                      {width <= 20 && (
                        <span className="text-sm font-medium text-text-primary w-8">{stage.count}</span>
                      )}
                      {index > 0 && (
                        <span className="text-xs text-text-muted w-12">{conversionRate}%</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>

          {/* Status Distribution */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Por Status</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={statusDistribution} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                      {statusDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-3 mt-2">
                {statusDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-text-muted">{item.name}</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex items-center gap-3">
            <Input
              placeholder="Buscar candidaturas..."
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
                data={filteredApplications}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedApplication(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Detail Modal */}
        <Modal
          isOpen={!!selectedApplication}
          onClose={() => setSelectedApplication(null)}
          title="Detalhes da Candidatura"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedApplication(null)}>
                Fechar
              </Button>
              {selectedApplication && selectedApplication.status !== 'hired' && selectedApplication.status !== 'rejected' && (
                <>
                  <Button variant="danger" leftIcon={<UserX className="w-4 h-4" />}>
                    Rejeitar
                  </Button>
                  <Button variant="primary" leftIcon={<ArrowRight className="w-4 h-4" />}>
                    Avançar Etapa
                  </Button>
                </>
              )}
            </>
          }
        >
          {selectedApplication && (
            <div className="space-y-6">
              {/* Candidate Info */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                <Avatar name={selectedApplication.candidateName} size="lg" />
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-text-primary">{selectedApplication.candidateName}</h3>
                    <Badge variant={statusColors[selectedApplication.status]}>{statusLabels[selectedApplication.status]}</Badge>
                  </div>
                  <p className="text-text-secondary">{selectedApplication.position}</p>
                  <p className="text-sm text-text-muted">{selectedApplication.department}</p>
                </div>
                <Badge variant={sourceColors[selectedApplication.source]}>{sourceLabels[selectedApplication.source]}</Badge>
              </div>

              {/* Progress Pipeline */}
              <div>
                <h4 className="font-medium text-text-primary mb-4">Progresso da Candidatura</h4>
                <div className="flex items-center justify-between">
                  {pipelineStages.map((stage, index) => {
                    const isCompleted = index < selectedApplication.stage;
                    const isCurrent = index === selectedApplication.stage - 1;
                    const isRejected = selectedApplication.status === 'rejected' && isCurrent;
                    return (
                      <div key={stage} className="flex items-center">
                        <div className="flex flex-col items-center">
                          <div
                            className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              isRejected
                                ? 'bg-danger text-white'
                                : isCompleted
                                ? 'bg-success text-white'
                                : isCurrent
                                ? 'bg-primary text-white'
                                : 'bg-bg-secondary text-text-muted'
                            }`}
                          >
                            {isRejected ? (
                              <XCircle className="w-5 h-5" />
                            ) : isCompleted ? (
                              <CheckCircle2 className="w-5 h-5" />
                            ) : (
                              <span className="text-sm font-medium">{index + 1}</span>
                            )}
                          </div>
                          <span className={`text-xs mt-2 ${isCurrent ? 'text-primary font-medium' : 'text-text-muted'}`}>
                            {stage}
                          </span>
                        </div>
                        {index < pipelineStages.length - 1 && (
                          <div className={`w-12 h-1 mx-2 rounded ${isCompleted ? 'bg-success' : 'bg-bg-secondary'}`} />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Details */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Calendar className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-xs text-text-muted">Data da Candidatura</p>
                    <p className="text-sm text-text-primary">{new Date(selectedApplication.appliedAt).toLocaleDateString('pt-BR')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Clock className="w-5 h-5 text-success" />
                  <div>
                    <p className="text-xs text-text-muted">Última Atividade</p>
                    <p className="text-sm text-text-primary">{new Date(selectedApplication.lastActivity).toLocaleDateString('pt-BR')}</p>
                  </div>
                </div>
              </div>

              {/* Rating */}
              {selectedApplication.rating > 0 && (
                <div className="flex items-center gap-4 p-4 rounded-lg bg-bg-secondary">
                  <span className="text-sm text-text-secondary">Avaliação:</span>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`w-5 h-5 ${i < selectedApplication.rating ? 'text-accent-warning fill-accent-warning' : 'text-text-muted'}`}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* CV and Cover Letter */}
              <div className="flex gap-4">
                {selectedApplication.cvUrl && (
                  <Button variant="secondary" leftIcon={<FileText className="w-4 h-4" />}>
                    Ver Currículo
                  </Button>
                )}
                {selectedApplication.coverLetter && (
                  <Button variant="secondary" leftIcon={<Mail className="w-4 h-4" />}>
                    Ver Carta de Apresentação
                  </Button>
                )}
              </div>

              {/* Cover Letter Preview */}
              {selectedApplication.coverLetter && (
                <div className="p-4 rounded-lg bg-bg-secondary">
                  <p className="text-xs text-text-muted mb-2">Carta de Apresentação</p>
                  <p className="text-sm text-text-secondary italic">"{selectedApplication.coverLetter}"</p>
                </div>
              )}

              {/* Notes */}
              {selectedApplication.notes && (
                <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
                  <p className="text-sm font-medium text-warning mb-1">Observações</p>
                  <p className="text-sm text-text-secondary">{selectedApplication.notes}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-4 pt-4 border-t border-border">
                <Button variant="secondary" size="sm" leftIcon={<Mail className="w-4 h-4" />}>
                  Enviar Email
                </Button>
                <Button variant="secondary" size="sm" leftIcon={<MessageSquare className="w-4 h-4" />}>
                  Adicionar Nota
                </Button>
                <Button variant="secondary" size="sm" leftIcon={<Calendar className="w-4 h-4" />}>
                  Agendar Entrevista
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
