'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Users,
  UserPlus,
  Star,
  Mail,
  Phone,
  MapPin,
  Calendar,
  FileText,
  Eye,
  Edit2,
  Trash2,
  MoreHorizontal,
  Download,
  Upload,
  Linkedin,
  Globe,
  UserCheck,
  Clock,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Briefcase,
  GraduationCap,
  Award,
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
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Types
interface Candidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  photoUrl: string | null;
  currentPosition: string;
  currentCompany: string;
  experience: number;
  education: string;
  skills: string[];
  languages: string[];
  linkedinUrl: string | null;
  portfolioUrl: string | null;
  source: 'linkedin' | 'indeed' | 'site' | 'referral' | 'agency' | 'other';
  status: 'active' | 'in_process' | 'hired' | 'rejected' | 'blacklisted';
  rating: number;
  notes: string;
  appliedPositions: string[];
  createdAt: string;
  lastContact: string | null;
}

// Mock Data
const candidates: Candidate[] = [
  {
    id: '1',
    name: 'Lucas Oliveira',
    email: 'lucas.oliveira@email.com',
    phone: '(11) 98765-4321',
    location: 'São Paulo, SP',
    photoUrl: null,
    currentPosition: 'Vigilante',
    currentCompany: 'Segurança Total',
    experience: 5,
    education: 'Ensino Médio Completo',
    skills: ['Vigilância', 'Controle de Acesso', 'CFTV'],
    languages: ['Português'],
    linkedinUrl: 'https://linkedin.com/in/lucas-oliveira',
    portfolioUrl: null,
    source: 'linkedin',
    status: 'in_process',
    rating: 4,
    notes: 'Candidato com boa experiência em shopping centers',
    appliedPositions: ['Vigilante', 'Supervisor de Segurança'],
    createdAt: '2026-01-10',
    lastContact: '2026-01-15',
  },
  {
    id: '2',
    name: 'Amanda Costa',
    email: 'amanda.costa@email.com',
    phone: '(11) 91234-5678',
    location: 'São Paulo, SP',
    photoUrl: null,
    currentPosition: 'Analista Comercial',
    currentCompany: 'Tech Solutions',
    experience: 7,
    education: 'Superior em Administração',
    skills: ['Vendas B2B', 'CRM', 'Negociação', 'Apresentações'],
    languages: ['Português', 'Inglês Avançado', 'Espanhol Básico'],
    linkedinUrl: 'https://linkedin.com/in/amanda-costa',
    portfolioUrl: null,
    source: 'site',
    status: 'in_process',
    rating: 5,
    notes: 'Perfil excelente, alta performance em vendas',
    appliedPositions: ['Analista Comercial'],
    createdAt: '2026-01-08',
    lastContact: '2026-01-14',
  },
  {
    id: '3',
    name: 'Roberto Mendes',
    email: 'roberto.mendes@email.com',
    phone: '(11) 99876-5432',
    location: 'Guarulhos, SP',
    photoUrl: null,
    currentPosition: 'Supervisor de Segurança',
    currentCompany: 'Proteção Empresarial',
    experience: 12,
    education: 'Tecnólogo em Segurança',
    skills: ['Gestão de Equipe', 'Planejamento', 'Segurança Patrimonial', 'Treinamento'],
    languages: ['Português'],
    linkedinUrl: null,
    portfolioUrl: null,
    source: 'referral',
    status: 'hired',
    rating: 5,
    notes: 'Contratado como Supervisor em 15/01/2026',
    appliedPositions: ['Supervisor de Segurança'],
    createdAt: '2025-12-20',
    lastContact: '2026-01-15',
  },
  {
    id: '4',
    name: 'Juliana Santos',
    email: 'juliana.santos@email.com',
    phone: '(11) 98888-7777',
    location: 'São Bernardo do Campo, SP',
    photoUrl: null,
    currentPosition: 'Estagiária',
    currentCompany: 'Empresa Júnior FATEC',
    experience: 1,
    education: 'Cursando Contabilidade - 5º semestre',
    skills: ['Excel Avançado', 'Contabilidade Básica', 'SAP'],
    languages: ['Português', 'Inglês Intermediário'],
    linkedinUrl: 'https://linkedin.com/in/juliana-santos',
    portfolioUrl: null,
    source: 'site',
    status: 'active',
    rating: 3,
    notes: '',
    appliedPositions: ['Estagiário Financeiro'],
    createdAt: '2026-01-15',
    lastContact: null,
  },
  {
    id: '5',
    name: 'Pedro Almeida',
    email: 'pedro.almeida@email.com',
    phone: '(11) 97777-6666',
    location: 'Osasco, SP',
    photoUrl: null,
    currentPosition: 'Desempregado',
    currentCompany: '',
    experience: 3,
    education: 'Ensino Médio Completo',
    skills: ['Vigilância', 'Portaria', 'Atendimento'],
    languages: ['Português'],
    linkedinUrl: null,
    portfolioUrl: null,
    source: 'agency',
    status: 'rejected',
    rating: 2,
    notes: 'Não compareceu à entrevista agendada',
    appliedPositions: ['Vigilante'],
    createdAt: '2026-01-05',
    lastContact: '2026-01-10',
  },
];

const sourceDistribution = [
  { name: 'LinkedIn', value: 35, color: '#0A66C2' },
  { name: 'Site', value: 28, color: '#3B82F6' },
  { name: 'Indicação', value: 20, color: '#10B981' },
  { name: 'Agências', value: 12, color: '#F59E0B' },
  { name: 'Outros', value: 5, color: '#6B7280' },
];

const statusDistribution = [
  { status: 'Ativos', count: 45 },
  { status: 'Em Processo', count: 28 },
  { status: 'Contratados', count: 12 },
  { status: 'Rejeitados', count: 35 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'active', label: 'Ativos' },
  { id: 'in_process', label: 'Em Processo' },
  { id: 'hired', label: 'Contratados' },
  { id: 'rejected', label: 'Rejeitados' },
];

const sourceLabels = {
  linkedin: 'LinkedIn',
  indeed: 'Indeed',
  site: 'Site',
  referral: 'Indicação',
  agency: 'Agência',
  other: 'Outro',
};

const sourceColors = {
  linkedin: 'info',
  indeed: 'primary',
  site: 'success',
  referral: 'warning',
  agency: 'secondary',
  other: 'neutral',
} as const;

const statusLabels = {
  active: 'Ativo',
  in_process: 'Em Processo',
  hired: 'Contratado',
  rejected: 'Rejeitado',
  blacklisted: 'Bloqueado',
};

const statusColors = {
  active: 'info',
  in_process: 'warning',
  hired: 'success',
  rejected: 'danger',
  blacklisted: 'neutral',
} as const;

const columns: Column<Candidate>[] = [
  {
    key: 'name',
    header: 'Candidato',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.name} size="md" />
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.email}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'currentPosition',
    header: 'Posição Atual',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.currentPosition}</p>
        <p className="text-xs text-text-muted">{row.currentCompany || 'Não informado'}</p>
      </div>
    ),
  },
  {
    key: 'experience',
    header: 'Experiência',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Briefcase className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.experience} anos</span>
      </div>
    ),
  },
  {
    key: 'source',
    header: 'Origem',
    render: (row) => <Badge variant={sourceColors[row.source]}>{sourceLabels[row.source]}</Badge>,
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
    key: 'status',
    header: 'Status',
    render: (row) => <Badge variant={statusColors[row.status]}>{statusLabels[row.status]}</Badge>,
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Perfil">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Mensagem">
          <MessageSquare className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function CandidatesPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  const filteredCandidates = candidates.filter((candidate) => {
    const matchesSearch =
      candidate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      candidate.email.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && candidate.status === activeTab;
  });

  // Stats
  const totalCandidates = candidates.length;
  const activeCandidates = candidates.filter((c) => c.status === 'active' || c.status === 'in_process').length;
  const hiredThisMonth = candidates.filter((c) => c.status === 'hired').length;
  const avgRating = (candidates.reduce((acc, c) => acc + c.rating, 0) / candidates.length).toFixed(1);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Banco de Candidatos</h1>
            <p className="text-text-secondary mt-1">Gerencie o banco de talentos da empresa</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Upload className="w-4 h-4" />}>
              Importar CV
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Novo Candidato
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Candidatos" value={totalCandidates} icon={<Users className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Candidatos Ativos" value={activeCandidates} icon={<UserPlus className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Contratados (Mês)" value={hiredThisMonth} icon={<UserCheck className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Avaliação Média" value={avgRating} icon={<Star className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
        </StatGrid>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Origem dos Candidatos</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={sourceDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {sourceDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {sourceDistribution.map((item) => (
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
                <Users className="w-5 h-5 text-success" />
                <h3 className="font-semibold">Status dos Candidatos</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statusDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="status" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
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
              placeholder="Buscar candidatos..."
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
                data={filteredCandidates}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedCandidate(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Novo Candidato"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary">Cadastrar</Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Nome Completo" placeholder="Nome do candidato" required />
              <Input label="Email" type="email" placeholder="email@exemplo.com" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Telefone" placeholder="(11) 99999-9999" />
              <Input label="Localização" placeholder="Cidade, Estado" leftIcon={<MapPin className="w-4 h-4" />} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Cargo Atual" placeholder="Posição atual" />
              <Input label="Empresa Atual" placeholder="Nome da empresa" />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Input label="Anos de Experiência" type="number" placeholder="0" />
              <Select
                label="Escolaridade"
                options={[
                  { value: 'fundamental', label: 'Ensino Fundamental' },
                  { value: 'medio', label: 'Ensino Médio' },
                  { value: 'tecnico', label: 'Técnico' },
                  { value: 'superior', label: 'Superior' },
                  { value: 'pos', label: 'Pós-Graduação' },
                  { value: 'mestrado', label: 'Mestrado' },
                  { value: 'doutorado', label: 'Doutorado' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Origem"
                options={[
                  { value: 'linkedin', label: 'LinkedIn' },
                  { value: 'indeed', label: 'Indeed' },
                  { value: 'site', label: 'Site' },
                  { value: 'referral', label: 'Indicação' },
                  { value: 'agency', label: 'Agência' },
                  { value: 'other', label: 'Outro' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="LinkedIn" placeholder="https://linkedin.com/in/..." leftIcon={<Linkedin className="w-4 h-4" />} />
              <Input label="Portfólio/Site" placeholder="https://..." leftIcon={<Globe className="w-4 h-4" />} />
            </div>
            <Input label="Habilidades" placeholder="Separe as habilidades por vírgula" />
            <Textarea label="Observações" placeholder="Observações sobre o candidato..." rows={3} />
          </div>
        </Modal>

        {/* Candidate Detail Modal */}
        <Modal
          isOpen={!!selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
          title="Perfil do Candidato"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedCandidate(null)}>
                Fechar
              </Button>
              <Button variant="primary" leftIcon={<MessageSquare className="w-4 h-4" />}>
                Enviar Mensagem
              </Button>
            </>
          }
        >
          {selectedCandidate && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                <Avatar name={selectedCandidate.name} size="xl" />
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-semibold text-text-primary">{selectedCandidate.name}</h3>
                    <Badge variant={statusColors[selectedCandidate.status]}>{statusLabels[selectedCandidate.status]}</Badge>
                  </div>
                  <p className="text-text-secondary mt-1">{selectedCandidate.currentPosition}</p>
                  <p className="text-sm text-text-muted">{selectedCandidate.currentCompany}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`w-5 h-5 ${i < selectedCandidate.rating ? 'text-accent-warning fill-accent-warning' : 'text-text-muted'}`}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Mail className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-xs text-text-muted">Email</p>
                    <p className="text-sm text-text-primary">{selectedCandidate.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Phone className="w-5 h-5 text-success" />
                  <div>
                    <p className="text-xs text-text-muted">Telefone</p>
                    <p className="text-sm text-text-primary">{selectedCandidate.phone}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <MapPin className="w-5 h-5 text-warning" />
                  <div>
                    <p className="text-xs text-text-muted">Localização</p>
                    <p className="text-sm text-text-primary">{selectedCandidate.location}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Briefcase className="w-5 h-5 text-info" />
                  <div>
                    <p className="text-xs text-text-muted">Experiência</p>
                    <p className="text-sm text-text-primary">{selectedCandidate.experience} anos</p>
                  </div>
                </div>
              </div>

              {/* Skills */}
              <div>
                <h4 className="font-medium text-text-primary mb-3">Habilidades</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedCandidate.skills.map((skill) => (
                    <Badge key={skill} variant="info">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Education */}
              <div className="flex items-center gap-3 p-4 rounded-lg bg-bg-secondary">
                <GraduationCap className="w-6 h-6 text-primary" />
                <div>
                  <p className="text-xs text-text-muted">Escolaridade</p>
                  <p className="font-medium text-text-primary">{selectedCandidate.education}</p>
                </div>
              </div>

              {/* Applied Positions */}
              <div>
                <h4 className="font-medium text-text-primary mb-3">Vagas Aplicadas</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedCandidate.appliedPositions.map((position) => (
                    <Badge key={position} variant="secondary">
                      {position}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Notes */}
              {selectedCandidate.notes && (
                <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
                  <p className="text-sm font-medium text-warning mb-1">Observações</p>
                  <p className="text-sm text-text-secondary">{selectedCandidate.notes}</p>
                </div>
              )}

              {/* Footer Info */}
              <div className="flex items-center gap-6 text-sm text-text-muted pt-4 border-t border-border">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>Cadastrado em: {new Date(selectedCandidate.createdAt).toLocaleDateString('pt-BR')}</span>
                </div>
                {selectedCandidate.lastContact && (
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>Último contato: {new Date(selectedCandidate.lastContact).toLocaleDateString('pt-BR')}</span>
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
