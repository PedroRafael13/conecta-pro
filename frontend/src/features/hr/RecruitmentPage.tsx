'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Briefcase,
  Search,
  Filter,
  Plus,
  Calendar,
  MapPin,
  Clock,
  CheckCircle2,
  XCircle,
  UserPlus,
  FileText,
  Star,
  Mail,
  Phone,
  MoreVertical,
  Eye,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  ChevronRight,
  Building2,
  GraduationCap,
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
  Avatar,
} from '@/design-system/components';

// Types
interface JobOpening {
  id: string;
  title: string;
  department: string;
  location: string;
  type: 'full-time' | 'part-time' | 'temporary' | 'intern';
  level: 'junior' | 'pleno' | 'senior' | 'lead';
  salary: { min: number; max: number } | null;
  candidates: number;
  newCandidates: number;
  status: 'open' | 'paused' | 'closed' | 'filled';
  createdAt: string;
  deadline: string | null;
}

interface Candidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  position: string;
  source: 'linkedin' | 'site' | 'referral' | 'agency';
  experience: string;
  education: string;
  stage: 'new' | 'screening' | 'interview' | 'test' | 'offer' | 'hired' | 'rejected';
  rating: number;
  appliedAt: string;
  notes: string;
}

// Mock Data
const jobOpenings: JobOpening[] = [
  {
    id: '1',
    title: 'Vigilante',
    department: 'Operações',
    location: 'São Paulo - SP',
    type: 'full-time',
    level: 'junior',
    salary: { min: 2000, max: 2500 },
    candidates: 45,
    newCandidates: 8,
    status: 'open',
    createdAt: '2026-01-01',
    deadline: '2026-01-31',
  },
  {
    id: '2',
    title: 'Supervisor de Segurança',
    department: 'Operações',
    location: 'São Paulo - SP',
    type: 'full-time',
    level: 'senior',
    salary: { min: 4000, max: 5500 },
    candidates: 12,
    newCandidates: 2,
    status: 'open',
    createdAt: '2026-01-05',
    deadline: '2026-02-05',
  },
  {
    id: '3',
    title: 'Analista Comercial',
    department: 'Comercial',
    location: 'São Paulo - SP',
    type: 'full-time',
    level: 'pleno',
    salary: { min: 4500, max: 6000 },
    candidates: 28,
    newCandidates: 5,
    status: 'open',
    createdAt: '2026-01-08',
    deadline: '2026-02-08',
  },
  {
    id: '4',
    title: 'Analista de RH',
    department: 'RH',
    location: 'São Paulo - SP',
    type: 'full-time',
    level: 'pleno',
    salary: { min: 4000, max: 5000 },
    candidates: 35,
    newCandidates: 0,
    status: 'paused',
    createdAt: '2025-12-15',
    deadline: null,
  },
  {
    id: '5',
    title: 'Estagiário Financeiro',
    department: 'Financeiro',
    location: 'São Paulo - SP',
    type: 'intern',
    level: 'junior',
    salary: { min: 1500, max: 1800 },
    candidates: 52,
    newCandidates: 12,
    status: 'open',
    createdAt: '2026-01-10',
    deadline: '2026-01-25',
  },
];

const candidates: Candidate[] = [
  {
    id: '1',
    name: 'Lucas Oliveira',
    email: 'lucas.oliveira@email.com',
    phone: '(11) 98765-4321',
    position: 'Vigilante',
    source: 'linkedin',
    experience: '3 anos',
    education: 'Ensino Médio Completo',
    stage: 'interview',
    rating: 4,
    appliedAt: '2026-01-14',
    notes: 'Experiência prévia em shopping',
  },
  {
    id: '2',
    name: 'Amanda Costa',
    email: 'amanda.costa@email.com',
    phone: '(11) 91234-5678',
    position: 'Analista Comercial',
    source: 'site',
    experience: '5 anos',
    education: 'Superior em Administração',
    stage: 'test',
    rating: 5,
    appliedAt: '2026-01-13',
    notes: 'Perfil excelente, boa comunicação',
  },
  {
    id: '3',
    name: 'Roberto Mendes',
    email: 'roberto.mendes@email.com',
    phone: '(11) 99876-5432',
    position: 'Supervisor de Segurança',
    source: 'referral',
    experience: '8 anos',
    education: 'Tecnólogo em Segurança',
    stage: 'offer',
    rating: 5,
    appliedAt: '2026-01-10',
    notes: 'Indicação do gerente operacional',
  },
  {
    id: '4',
    name: 'Juliana Santos',
    email: 'juliana.santos@email.com',
    phone: '(11) 98888-7777',
    position: 'Estagiário Financeiro',
    source: 'site',
    experience: 'Sem experiência',
    education: 'Cursando Contabilidade',
    stage: 'screening',
    rating: 3,
    appliedAt: '2026-01-15',
    notes: '',
  },
  {
    id: '5',
    name: 'Pedro Almeida',
    email: 'pedro.almeida@email.com',
    phone: '(11) 97777-6666',
    position: 'Vigilante',
    source: 'agency',
    experience: '2 anos',
    education: 'Ensino Médio Completo',
    stage: 'new',
    rating: 0,
    appliedAt: '2026-01-15',
    notes: '',
  },
];

const typeLabels = {
  'full-time': 'CLT',
  'part-time': 'Meio Período',
  temporary: 'Temporário',
  intern: 'Estágio',
};

const levelLabels = {
  junior: 'Júnior',
  pleno: 'Pleno',
  senior: 'Sênior',
  lead: 'Líder',
};

const statusConfig = {
  open: { label: 'Aberta', color: 'success' as const },
  paused: { label: 'Pausada', color: 'warning' as const },
  closed: { label: 'Fechada', color: 'neutral' as const },
  filled: { label: 'Preenchida', color: 'info' as const },
};

const stageConfig = {
  new: { label: 'Novo', color: 'neutral' as const },
  screening: { label: 'Triagem', color: 'info' as const },
  interview: { label: 'Entrevista', color: 'primary' as const },
  test: { label: 'Teste', color: 'warning' as const },
  offer: { label: 'Proposta', color: 'success' as const },
  hired: { label: 'Contratado', color: 'success' as const },
  rejected: { label: 'Rejeitado', color: 'danger' as const },
};

const sourceLabels = {
  linkedin: 'LinkedIn',
  site: 'Site',
  referral: 'Indicação',
  agency: 'Agência',
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(value);
};

const jobColumns: Column<JobOpening>[] = [
  {
    key: 'title',
    header: 'Vaga',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.title}</p>
        <p className="text-xs text-text-muted">{row.department}</p>
      </div>
    ),
  },
  {
    key: 'location',
    header: 'Local',
    render: (row) => (
      <div className="flex items-center gap-1 text-sm text-text-secondary">
        <MapPin className="w-3 h-3" />
        {row.location}
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Badge variant="info">{typeLabels[row.type]}</Badge>
        <span className="text-xs text-text-muted">{levelLabels[row.level]}</span>
      </div>
    ),
  },
  {
    key: 'salary',
    header: 'Faixa Salarial',
    render: (row) => (
      <span className="text-sm">
        {row.salary ? `${formatCurrency(row.salary.min)} - ${formatCurrency(row.salary.max)}` : 'A combinar'}
      </span>
    ),
  },
  {
    key: 'candidates',
    header: 'Candidatos',
    render: (row) => (
      <div className="flex items-center gap-2">
        <span className="font-medium">{row.candidates}</span>
        {row.newCandidates > 0 && (
          <Badge variant="success" size="sm">+{row.newCandidates} novos</Badge>
        )}
      </div>
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
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Mais opções">
          <MoreVertical className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const candidateColumns: Column<Candidate>[] = [
  {
    key: 'name',
    header: 'Candidato',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.name} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.email}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'position',
    header: 'Vaga',
    render: (row) => <span className="text-sm">{row.position}</span>,
  },
  {
    key: 'source',
    header: 'Origem',
    render: (row) => <Badge variant="info">{sourceLabels[row.source]}</Badge>,
  },
  {
    key: 'experience',
    header: 'Experiência',
    render: (row) => <span className="text-sm text-text-secondary">{row.experience}</span>,
  },
  {
    key: 'rating',
    header: 'Avaliação',
    render: (row) => (
      <div className="flex items-center gap-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <Star
            key={i}
            className={`w-4 h-4 ${i < row.rating ? 'text-accent-warning fill-accent-warning' : 'text-text-muted'}`}
          />
        ))}
      </div>
    ),
  },
  {
    key: 'stage',
    header: 'Etapa',
    render: (row) => {
      const config = stageConfig[row.stage];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver perfil">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Agendar">
          <Calendar className="w-4 h-4" />
        </Button>
        {row.stage !== 'hired' && row.stage !== 'rejected' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Aprovar">
              <ThumbsUp className="w-4 h-4 text-accent-success" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Reprovar">
              <ThumbsDown className="w-4 h-4 text-accent-danger" />
            </Button>
          </>
        )}
      </div>
    ),
  },
];

// Kanban stages for pipeline view
const pipelineStages = [
  { key: 'new', label: 'Novos', color: 'bg-text-muted' },
  { key: 'screening', label: 'Triagem', color: 'bg-accent-info' },
  { key: 'interview', label: 'Entrevista', color: 'bg-accent-primary' },
  { key: 'test', label: 'Teste', color: 'bg-accent-warning' },
  { key: 'offer', label: 'Proposta', color: 'bg-accent-success' },
];

export function RecruitmentPage() {
  const [selectedTab, setSelectedTab] = useState('openings');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'kanban'>('list');

  // Stats
  const openVacancies = jobOpenings.filter(j => j.status === 'open').length;
  const totalCandidates = jobOpenings.reduce((acc, j) => acc + j.candidates, 0);
  const newCandidates = jobOpenings.reduce((acc, j) => acc + j.newCandidates, 0);
  const inProcess = candidates.filter(c => !['new', 'hired', 'rejected'].includes(c.stage)).length;

  const getCandidatesByStage = (stage: string) => candidates.filter(c => c.stage === stage);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Recrutamento e Seleção
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie vagas e candidatos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<FileText className="w-4 h-4" />}>
              Relatórios
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Vaga
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Vagas Abertas"
              value={openVacancies}
              icon={<Briefcase className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Total Candidatos"
              value={totalCandidates}
              icon={<Users className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Novos Esta Semana"
              value={newCandidates}
              icon={<UserPlus className="w-6 h-6" />}
              iconColor="success"
              trend="up"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Em Processo"
              value={inProcess}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between">
              <SimpleTabBar
                tabs={[
                  { value: 'openings', label: 'Vagas' },
                  { value: 'candidates', label: 'Candidatos' },
                  { value: 'pipeline', label: 'Pipeline' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              {selectedTab === 'candidates' && (
                <div className="flex items-center gap-2">
                  <Button
                    variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                  >
                    Lista
                  </Button>
                  <Button
                    variant={viewMode === 'kanban' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('kanban')}
                  >
                    Kanban
                  </Button>
                </div>
              )}
            </div>
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          {selectedTab === 'openings' && (
            <Card>
              <CardBody className="border-b border-border-subtle">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Input
                      placeholder="Buscar vaga..."
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
                    value="all"
                    onChange={() => {}}
                    className="w-48"
                  />
                  <Select
                    options={[
                      { value: 'all', label: 'Todos Status' },
                      { value: 'open', label: 'Abertas' },
                      { value: 'paused', label: 'Pausadas' },
                      { value: 'filled', label: 'Preenchidas' },
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-40"
                  />
                </div>
              </CardBody>
              <CardBody className="p-0">
                <DataTable
                  columns={jobColumns}
                  data={jobOpenings}
                  keyExtractor={(row) => row.id}
                />
              </CardBody>
            </Card>
          )}

          {selectedTab === 'candidates' && viewMode === 'list' && (
            <Card>
              <CardBody className="border-b border-border-subtle">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Input
                      placeholder="Buscar candidato..."
                      leftIcon={<Search className="w-4 h-4" />}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select
                    options={[
                      { value: 'all', label: 'Todas Vagas' },
                      ...jobOpenings.map(j => ({ value: j.id, label: j.title })),
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-48"
                  />
                  <Select
                    options={[
                      { value: 'all', label: 'Todas Etapas' },
                      { value: 'new', label: 'Novos' },
                      { value: 'screening', label: 'Triagem' },
                      { value: 'interview', label: 'Entrevista' },
                      { value: 'test', label: 'Teste' },
                      { value: 'offer', label: 'Proposta' },
                    ]}
                    value="all"
                    onChange={() => {}}
                    className="w-40"
                  />
                </div>
              </CardBody>
              <CardBody className="p-0">
                <DataTable
                  columns={candidateColumns}
                  data={candidates}
                  keyExtractor={(row) => row.id}
                />
              </CardBody>
            </Card>
          )}

          {selectedTab === 'candidates' && viewMode === 'kanban' && (
            <div className="flex gap-4 overflow-x-auto pb-4">
              {pipelineStages.map((stage) => {
                const stageCandidates = getCandidatesByStage(stage.key);
                return (
                  <div key={stage.key} className="flex-shrink-0 w-72">
                    <div className="bg-bg-secondary rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-4">
                        <div className={`w-3 h-3 rounded-full ${stage.color}`} />
                        <h3 className="font-medium text-text-primary">{stage.label}</h3>
                        <Badge variant="neutral" size="sm">{stageCandidates.length}</Badge>
                      </div>
                      <div className="space-y-3">
                        {stageCandidates.map((candidate) => (
                          <Card key={candidate.id} className="cursor-pointer hover:border-accent-primary/50">
                            <CardBody className="p-3">
                              <div className="flex items-start gap-3">
                                <Avatar name={candidate.name} size="sm" />
                                <div className="flex-1 min-w-0">
                                  <p className="font-medium text-text-primary truncate">{candidate.name}</p>
                                  <p className="text-xs text-text-muted truncate">{candidate.position}</p>
                                  <div className="flex items-center gap-2 mt-2">
                                    <Badge variant="info" size="sm">{sourceLabels[candidate.source]}</Badge>
                                    <div className="flex items-center">
                                      {Array.from({ length: 5 }).map((_, i) => (
                                        <Star
                                          key={i}
                                          className={`w-3 h-3 ${i < candidate.rating ? 'text-accent-warning fill-accent-warning' : 'text-text-muted'}`}
                                        />
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </CardBody>
                          </Card>
                        ))}
                        {stageCandidates.length === 0 && (
                          <div className="text-center py-8 text-text-muted text-sm">
                            Nenhum candidato
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {selectedTab === 'pipeline' && (
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-text-primary">Funil de Recrutamento</h3>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {pipelineStages.map((stage, index) => {
                    const count = getCandidatesByStage(stage.key).length;
                    const maxCount = Math.max(...pipelineStages.map(s => getCandidatesByStage(s.key).length));
                    const width = maxCount > 0 ? (count / maxCount) * 100 : 0;
                    return (
                      <div key={stage.key} className="flex items-center gap-4">
                        <div className="w-24 text-sm text-text-secondary">{stage.label}</div>
                        <div className="flex-1 bg-bg-tertiary rounded-full h-8 overflow-hidden">
                          <motion.div
                            className={`h-full ${stage.color} flex items-center justify-end pr-3`}
                            initial={{ width: 0 }}
                            animate={{ width: `${width}%` }}
                            transition={{ delay: index * 0.1, duration: 0.5 }}
                          >
                            {width > 20 && (
                              <span className="text-sm font-medium text-white">{count}</span>
                            )}
                          </motion.div>
                        </div>
                        {width <= 20 && (
                          <span className="text-sm font-medium text-text-primary w-8">{count}</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          )}
        </motion.div>

        {/* New Job Opening Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Vaga"
          description="Cadastre uma nova vaga de emprego"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Publicar Vaga
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Título da Vaga" placeholder="Ex: Vigilante, Supervisor..." />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Departamento"
                options={[
                  { value: 'operations', label: 'Operações' },
                  { value: 'commercial', label: 'Comercial' },
                  { value: 'rh', label: 'RH' },
                  { value: 'financial', label: 'Financeiro' },
                  { value: 'ti', label: 'TI' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Input label="Local" placeholder="São Paulo - SP" leftIcon={<MapPin className="w-4 h-4" />} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Contrato"
                options={[
                  { value: 'full-time', label: 'CLT' },
                  { value: 'part-time', label: 'Meio Período' },
                  { value: 'temporary', label: 'Temporário' },
                  { value: 'intern', label: 'Estágio' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Nível"
                options={[
                  { value: 'junior', label: 'Júnior' },
                  { value: 'pleno', label: 'Pleno' },
                  { value: 'senior', label: 'Sênior' },
                  { value: 'lead', label: 'Líder' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Salário Mínimo" type="number" placeholder="R$ 0,00" />
              <Input label="Salário Máximo" type="number" placeholder="R$ 0,00" />
            </div>
            <Input label="Data Limite" type="date" />
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Requisitos</label>
              <textarea
                className="w-full h-24 px-3 py-2 bg-bg-tertiary border border-border-default rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent"
                placeholder="Descreva os requisitos da vaga..."
              />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
