'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Calendar,
  Clock,
  MapPin,
  Video,
  Phone,
  Users,
  User,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Eye,
  Edit2,
  Trash2,
  MoreHorizontal,
  Download,
  Mail,
  MessageSquare,
  Star,
  ThumbsUp,
  ThumbsDown,
  ChevronLeft,
  ChevronRight,
  Briefcase,
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
  LineChart,
  Line,
} from 'recharts';

// Types
interface Interview {
  id: string;
  candidateName: string;
  candidateEmail: string;
  position: string;
  department: string;
  type: 'presencial' | 'video' | 'phone';
  stage: 'technical' | 'hr' | 'manager' | 'final';
  date: string;
  time: string;
  duration: number;
  location: string | null;
  meetingLink: string | null;
  interviewers: string[];
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  feedback: string | null;
  rating: number | null;
  notes: string;
}

// Mock Data
const interviews: Interview[] = [
  {
    id: '1',
    candidateName: 'Lucas Oliveira',
    candidateEmail: 'lucas.oliveira@email.com',
    position: 'Vigilante',
    department: 'Operações',
    type: 'presencial',
    stage: 'technical',
    date: '2026-01-17',
    time: '10:00',
    duration: 60,
    location: 'Sala 301 - Matriz',
    meetingLink: null,
    interviewers: ['Carlos Mendes', 'Roberto Santos'],
    status: 'confirmed',
    feedback: null,
    rating: null,
    notes: 'Candidato confirmou presença',
  },
  {
    id: '2',
    candidateName: 'Amanda Costa',
    candidateEmail: 'amanda.costa@email.com',
    position: 'Analista Comercial',
    department: 'Comercial',
    type: 'video',
    stage: 'hr',
    date: '2026-01-17',
    time: '14:00',
    duration: 45,
    location: null,
    meetingLink: 'https://meet.google.com/abc-defg-hij',
    interviewers: ['Fernanda Lima'],
    status: 'scheduled',
    feedback: null,
    rating: null,
    notes: '',
  },
  {
    id: '3',
    candidateName: 'Roberto Mendes',
    candidateEmail: 'roberto.mendes@email.com',
    position: 'Supervisor de Segurança',
    department: 'Operações',
    type: 'presencial',
    stage: 'final',
    date: '2026-01-16',
    time: '09:00',
    duration: 90,
    location: 'Sala de Diretoria',
    meetingLink: null,
    interviewers: ['Diretor Operacional', 'Gerente RH'],
    status: 'completed',
    feedback: 'Candidato excelente, aprovado para contratação',
    rating: 5,
    notes: 'Encaminhar para admissão',
  },
  {
    id: '4',
    candidateName: 'Juliana Santos',
    candidateEmail: 'juliana.santos@email.com',
    position: 'Estagiário Financeiro',
    department: 'Financeiro',
    type: 'video',
    stage: 'technical',
    date: '2026-01-18',
    time: '11:00',
    duration: 30,
    location: null,
    meetingLink: 'https://meet.google.com/xyz-uvw-rst',
    interviewers: ['Ana Paula Souza'],
    status: 'scheduled',
    feedback: null,
    rating: null,
    notes: 'Entrevista técnica básica para estágio',
  },
  {
    id: '5',
    candidateName: 'Pedro Almeida',
    candidateEmail: 'pedro.almeida@email.com',
    position: 'Vigilante',
    department: 'Operações',
    type: 'presencial',
    stage: 'hr',
    date: '2026-01-15',
    time: '15:00',
    duration: 45,
    location: 'Sala 301 - Matriz',
    meetingLink: null,
    interviewers: ['Fernanda Lima'],
    status: 'no_show',
    feedback: 'Candidato não compareceu',
    rating: null,
    notes: 'Tentativa de contato por telefone sem sucesso',
  },
];

const weeklySchedule = [
  { day: 'Seg', count: 4 },
  { day: 'Ter', count: 6 },
  { day: 'Qua', count: 5 },
  { day: 'Qui', count: 7 },
  { day: 'Sex', count: 3 },
];

const monthlyTrend = [
  { week: 'Sem 1', scheduled: 12, completed: 10 },
  { week: 'Sem 2', scheduled: 15, completed: 14 },
  { week: 'Sem 3', scheduled: 18, completed: 15 },
  { week: 'Sem 4', scheduled: 10, completed: 8 },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'today', label: 'Hoje' },
  { id: 'scheduled', label: 'Agendadas' },
  { id: 'completed', label: 'Realizadas' },
  { id: 'cancelled', label: 'Canceladas' },
];

const typeIcons = {
  presencial: MapPin,
  video: Video,
  phone: Phone,
};

const typeLabels = {
  presencial: 'Presencial',
  video: 'Videoconferência',
  phone: 'Telefone',
};

const stageLabels = {
  technical: 'Técnica',
  hr: 'RH',
  manager: 'Gestor',
  final: 'Final',
};

const stageColors = {
  technical: 'info',
  hr: 'primary',
  manager: 'warning',
  final: 'success',
} as const;

const statusLabels = {
  scheduled: 'Agendada',
  confirmed: 'Confirmada',
  completed: 'Realizada',
  cancelled: 'Cancelada',
  no_show: 'Não Compareceu',
};

const statusColors = {
  scheduled: 'info',
  confirmed: 'success',
  completed: 'primary',
  cancelled: 'danger',
  no_show: 'warning',
} as const;

const columns: Column<Interview>[] = [
  {
    key: 'candidateName',
    header: 'Candidato',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.candidateName} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.candidateName}</p>
          <p className="text-xs text-text-muted">{row.position}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'date',
    header: 'Data/Hora',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Calendar className="w-4 h-4 text-text-muted" />
        <div>
          <p className="text-sm text-text-primary">{new Date(row.date).toLocaleDateString('pt-BR')}</p>
          <p className="text-xs text-text-muted">{row.time} ({row.duration}min)</p>
        </div>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const Icon = typeIcons[row.type];
      return (
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-text-muted" />
          <span className="text-sm">{typeLabels[row.type]}</span>
        </div>
      );
    },
  },
  {
    key: 'stage',
    header: 'Etapa',
    render: (row) => <Badge variant={stageColors[row.stage]}>{stageLabels[row.stage]}</Badge>,
  },
  {
    key: 'interviewers',
    header: 'Entrevistadores',
    render: (row) => (
      <div className="flex items-center gap-2">
        <div className="flex -space-x-2">
          {row.interviewers.slice(0, 3).map((name, i) => (
            <Avatar key={i} name={name} size="xs" className="ring-2 ring-bg-primary" />
          ))}
        </div>
        {row.interviewers.length > 3 && (
          <span className="text-xs text-text-muted">+{row.interviewers.length - 3}</span>
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
        <Button variant="ghost" size="icon-sm" title="Ver Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'scheduled' && (
          <>
            <Button variant="ghost" size="icon-sm" title="Confirmar">
              <CheckCircle2 className="w-4 h-4 text-success" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Cancelar">
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

export function InterviewsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState<Interview | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [newCandidate, setNewCandidate] = useState('');
  const [newInterviewType, setNewInterviewType] = useState('');
  const [newStage, setNewStage] = useState('');

  const today = new Date().toISOString().split('T')[0];

  const filteredInterviews = interviews.filter((interview) => {
    const matchesSearch =
      interview.candidateName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      interview.position.toLowerCase().includes(searchTerm.toLowerCase());

    switch (activeTab) {
      case 'today':
        return matchesSearch && interview.date === today;
      case 'scheduled':
        return matchesSearch && (interview.status === 'scheduled' || interview.status === 'confirmed');
      case 'completed':
        return matchesSearch && interview.status === 'completed';
      case 'cancelled':
        return matchesSearch && (interview.status === 'cancelled' || interview.status === 'no_show');
      default:
        return matchesSearch;
    }
  });

  // Stats
  const todayInterviews = interviews.filter((i) => i.date === today).length;
  const weekInterviews = interviews.filter((i) => i.status === 'scheduled' || i.status === 'confirmed').length;
  const completedInterviews = interviews.filter((i) => i.status === 'completed').length;
  const avgRating = interviews
    .filter((i) => i.rating !== null)
    .reduce((acc, i, _, arr) => acc + (i.rating || 0) / arr.length, 0)
    .toFixed(1);

  // Calendar helpers
  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const days = [];

    // Previous month days
    const startDay = firstDay.getDay();
    for (let i = startDay - 1; i >= 0; i--) {
      const d = new Date(year, month, -i);
      days.push({ date: d, currentMonth: false });
    }

    // Current month days
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push({ date: new Date(year, month, i), currentMonth: true });
    }

    // Next month days
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      days.push({ date: new Date(year, month + 1, i), currentMonth: false });
    }

    return days;
  };

  const getInterviewsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return interviews.filter((i) => i.date === dateStr);
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Entrevistas</h1>
            <p className="text-text-secondary mt-1">Gerencie agendamentos de entrevistas</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Agendar Entrevista
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Entrevistas Hoje" value={todayInterviews} icon={<Calendar className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Agendadas (Semana)" value={weekInterviews} icon={<Clock className="w-6 h-6" />} iconColor="info" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="Realizadas (Mês)" value={completedInterviews} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Avaliação Média" value={avgRating} icon={<Star className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
        </StatGrid>

        {/* Calendar & Charts */}
        <div className="grid grid-cols-3 gap-6">
          {/* Mini Calendar */}
          <Card className="col-span-1">
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</h3>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-7 gap-1 text-center text-xs">
                {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map((d) => (
                  <div key={d} className="p-2 font-medium text-text-muted">{d}</div>
                ))}
                {days.map((day, i) => {
                  const dayInterviews = getInterviewsForDate(day.date);
                  const isToday = day.date.toDateString() === new Date().toDateString();
                  return (
                    <div
                      key={i}
                      className={`p-2 rounded-lg cursor-pointer transition-colors ${
                        day.currentMonth ? 'text-text-primary hover:bg-bg-secondary' : 'text-text-muted'
                      } ${isToday ? 'bg-primary text-white' : ''}`}
                    >
                      <span>{day.date.getDate()}</span>
                      {dayInterviews.length > 0 && (
                        <div className="flex justify-center mt-1">
                          <div className={`w-1.5 h-1.5 rounded-full ${isToday ? 'bg-white' : 'bg-primary'}`} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>

          {/* Charts */}
          <Card className="col-span-2">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Entrevistas por Semana</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="week" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="scheduled" fill="#3B82F6" name="Agendadas" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="completed" fill="#10B981" name="Realizadas" radius={[4, 4, 0, 0]} />
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
              placeholder="Buscar entrevistas..."
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
                data={filteredInterviews}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedInterview(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Agendar Entrevista"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary">Agendar</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Candidato"
              options={[
                { value: '1', label: 'Lucas Oliveira - Vigilante' },
                { value: '2', label: 'Amanda Costa - Analista Comercial' },
                { value: '4', label: 'Juliana Santos - Estagiário Financeiro' },
              ]}
              value={newCandidate}
              onChange={(value) => setNewCandidate(value)}
              placeholder="Selecione o candidato..."
              required
            />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Entrevista"
                options={[
                  { value: 'presencial', label: 'Presencial' },
                  { value: 'video', label: 'Videoconferência' },
                  { value: 'phone', label: 'Telefone' },
                ]}
                value={newInterviewType}
                onChange={(value) => setNewInterviewType(value)}
                placeholder="Selecione..."
              />
              <Select
                label="Etapa"
                options={[
                  { value: 'technical', label: 'Técnica' },
                  { value: 'hr', label: 'RH' },
                  { value: 'manager', label: 'Gestor' },
                  { value: 'final', label: 'Final' },
                ]}
                value={newStage}
                onChange={(value) => setNewStage(value)}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Input label="Data" type="date" required />
              <Input label="Horário" type="time" required />
              <Input label="Duração (min)" type="number" placeholder="60" />
            </div>
            <Input label="Local / Link da Reunião" placeholder="Sala 301 ou https://meet.google.com/..." />
            <Input label="Entrevistadores" placeholder="Separe por vírgula" />
            <Textarea label="Observações" placeholder="Informações adicionais..." rows={3} />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={!!selectedInterview}
          onClose={() => setSelectedInterview(null)}
          title="Detalhes da Entrevista"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedInterview(null)}>
                Fechar
              </Button>
              {selectedInterview?.status === 'completed' ? (
                <Button variant="primary" leftIcon={<Star className="w-4 h-4" />}>
                  Avaliar
                </Button>
              ) : (
                <Button variant="primary" leftIcon={<Mail className="w-4 h-4" />}>
                  Enviar Lembrete
                </Button>
              )}
            </>
          }
        >
          {selectedInterview && (
            <div className="space-y-6">
              {/* Candidate Info */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                <Avatar name={selectedInterview.candidateName} size="lg" />
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-text-primary">{selectedInterview.candidateName}</h3>
                    <Badge variant={statusColors[selectedInterview.status]}>{statusLabels[selectedInterview.status]}</Badge>
                  </div>
                  <p className="text-text-secondary">{selectedInterview.position}</p>
                  <p className="text-sm text-text-muted">{selectedInterview.department}</p>
                </div>
              </div>

              {/* Interview Details */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Calendar className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-xs text-text-muted">Data</p>
                    <p className="text-sm text-text-primary">{new Date(selectedInterview.date).toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Clock className="w-5 h-5 text-success" />
                  <div>
                    <p className="text-xs text-text-muted">Horário</p>
                    <p className="text-sm text-text-primary">{selectedInterview.time} ({selectedInterview.duration} minutos)</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  {(() => {
                    const Icon = typeIcons[selectedInterview.type];
                    return <Icon className="w-5 h-5 text-warning" />;
                  })()}
                  <div>
                    <p className="text-xs text-text-muted">Tipo</p>
                    <p className="text-sm text-text-primary">{typeLabels[selectedInterview.type]}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg border border-border">
                  <Briefcase className="w-5 h-5 text-info" />
                  <div>
                    <p className="text-xs text-text-muted">Etapa</p>
                    <p className="text-sm text-text-primary">{stageLabels[selectedInterview.stage]}</p>
                  </div>
                </div>
              </div>

              {/* Location/Link */}
              {(selectedInterview.location || selectedInterview.meetingLink) && (
                <div className="p-4 rounded-lg bg-bg-secondary">
                  <p className="text-xs text-text-muted mb-1">
                    {selectedInterview.type === 'presencial' ? 'Local' : 'Link da Reunião'}
                  </p>
                  <p className="text-sm text-text-primary">
                    {selectedInterview.location || selectedInterview.meetingLink}
                  </p>
                </div>
              )}

              {/* Interviewers */}
              <div>
                <h4 className="font-medium text-text-primary mb-3">Entrevistadores</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedInterview.interviewers.map((name) => (
                    <div key={name} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-bg-secondary">
                      <Avatar name={name} size="xs" />
                      <span className="text-sm text-text-primary">{name}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Feedback (if completed) */}
              {selectedInterview.status === 'completed' && selectedInterview.feedback && (
                <div className="p-4 rounded-lg bg-success/10 border border-success/20">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="w-5 h-5 text-success" />
                    <p className="font-medium text-success">Feedback</p>
                    {selectedInterview.rating && (
                      <div className="flex items-center gap-1 ml-auto">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <Star
                            key={i}
                            className={`w-4 h-4 ${i < selectedInterview.rating! ? 'text-accent-warning fill-accent-warning' : 'text-text-muted'}`}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                  <p className="text-sm text-text-secondary">{selectedInterview.feedback}</p>
                </div>
              )}

              {/* Notes */}
              {selectedInterview.notes && (
                <div className="p-4 rounded-lg bg-warning/10 border border-warning/20">
                  <p className="text-sm font-medium text-warning mb-1">Observações</p>
                  <p className="text-sm text-text-secondary">{selectedInterview.notes}</p>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
