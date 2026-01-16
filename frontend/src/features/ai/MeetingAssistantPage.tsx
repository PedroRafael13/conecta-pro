'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Video,
  Mic,
  MicOff,
  FileText,
  Download,
  Share2,
  Clock,
  Calendar,
  Users,
  CheckCircle2,
  Play,
  Pause,
  Square,
  Sparkles,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  MessageSquare,
  ListTodo,
  AlertCircle,
  Target,
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
  Modal,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Dropdown,
  Avatar,
  Progress,
  EmptyState,
} from '@/design-system/components';

// Types
interface Meeting {
  id: string;
  title: string;
  date: string;
  duration: number;
  participants: string[];
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  hasRecording: boolean;
  hasTranscript: boolean;
  hasSummary: boolean;
  summary?: MeetingSummary;
}

interface MeetingSummary {
  overview: string;
  keyPoints: string[];
  actionItems: ActionItem[];
  decisions: string[];
  nextSteps: string[];
}

interface ActionItem {
  id: string;
  description: string;
  assignee: string;
  dueDate: string;
  status: 'pending' | 'in_progress' | 'completed';
}

// Mock Data
const mockMeetings: Meeting[] = [
  {
    id: '1',
    title: 'Reunião de Planejamento Sprint 34',
    date: '2026-01-16T10:00:00',
    duration: 60,
    participants: ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
    status: 'completed',
    hasRecording: true,
    hasTranscript: true,
    hasSummary: true,
    summary: {
      overview: 'Reunião de planejamento da Sprint 34 focada em melhorias no módulo financeiro e correções de bugs críticos.',
      keyPoints: [
        'Módulo de BI será priorizado',
        'Correção de bugs no fluxo de pagamentos',
        'Integração com novo banco aprovada',
        'Prazo de 2 semanas para entrega',
      ],
      actionItems: [
        { id: '1', description: 'Criar protótipo do dashboard BI', assignee: 'João Silva', dueDate: '2026-01-20', status: 'in_progress' },
        { id: '2', description: 'Revisar fluxo de pagamentos', assignee: 'Maria Santos', dueDate: '2026-01-18', status: 'pending' },
        { id: '3', description: 'Documentar API de integração bancária', assignee: 'Pedro Oliveira', dueDate: '2026-01-22', status: 'pending' },
      ],
      decisions: [
        'Usar React Query para cache de dados',
        'Implementar BI em fases',
        'Priorizar performance sobre features',
      ],
      nextSteps: [
        'Daily às 9h',
        'Review da sprint na sexta-feira',
        'Apresentação para stakeholders dia 30',
      ],
    },
  },
  {
    id: '2',
    title: 'Alinhamento com Cliente - Condomínio Aurora',
    date: '2026-01-15T14:00:00',
    duration: 45,
    participants: ['Ana Costa', 'Cliente Aurora'],
    status: 'completed',
    hasRecording: true,
    hasTranscript: true,
    hasSummary: true,
  },
  {
    id: '3',
    title: 'Review de Código - Módulo HR',
    date: '2026-01-15T16:00:00',
    duration: 30,
    participants: ['João Silva', 'Pedro Oliveira'],
    status: 'completed',
    hasRecording: false,
    hasTranscript: true,
    hasSummary: true,
  },
  {
    id: '4',
    title: 'Apresentação de Resultados Mensais',
    date: '2026-01-17T10:00:00',
    duration: 90,
    participants: ['Diretoria', 'Gerentes'],
    status: 'scheduled',
    hasRecording: false,
    hasTranscript: false,
    hasSummary: false,
  },
];

const statusConfig = {
  scheduled: { label: 'Agendada', color: 'info' as const },
  in_progress: { label: 'Em andamento', color: 'warning' as const },
  completed: { label: 'Concluída', color: 'success' as const },
  cancelled: { label: 'Cancelada', color: 'danger' as const },
};

const actionStatusConfig = {
  pending: { label: 'Pendente', color: 'secondary' as const },
  in_progress: { label: 'Em andamento', color: 'warning' as const },
  completed: { label: 'Concluída', color: 'success' as const },
};

export function MeetingAssistantPage() {
  const [meetings, setMeetings] = useState(mockMeetings);
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [activeTab, setActiveTab] = useState('meetings');
  const [searchQuery, setSearchQuery] = useState('');
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);

  const stats = {
    total: meetings.length,
    completed: meetings.filter((m) => m.status === 'completed').length,
    scheduled: meetings.filter((m) => m.status === 'scheduled').length,
    totalHours: Math.round(meetings.reduce((sum, m) => sum + m.duration, 0) / 60),
  };

  const filteredMeetings = meetings.filter((meeting) =>
    meeting.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleGenerateSummary = async (id: string) => {
    setIsTranscribing(true);
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setMeetings((prev) =>
      prev.map((m) =>
        m.id === id ? { ...m, hasSummary: true } : m
      )
    );
    setIsTranscribing(false);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Video className="w-8 h-8 text-accent-primary" />
              Assistente de Reuniões
            </h1>
            <p className="text-text-secondary mt-1">
              Transcrição automática, resumos e atas com IA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant={isRecording ? 'danger' : 'secondary'}
              leftIcon={isRecording ? <Square className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              onClick={() => setIsRecording(!isRecording)}
            >
              {isRecording ? 'Parar Gravação' : 'Iniciar Gravação'}
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
              Nova Reunião
            </Button>
          </div>
        </div>

        {/* Recording Indicator */}
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-500/10 border border-red-500/30 rounded-lg p-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                <span className="font-medium text-red-500">Gravação em andamento</span>
                <span className="text-text-muted">00:15:32</span>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm">
                  <Pause className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setIsRecording(false)}>
                  <Square className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Reuniões"
              value={stats.total}
              icon={<Video className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Concluídas"
              value={stats.completed}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Agendadas"
              value={stats.scheduled}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Horas Totais"
              value={`${stats.totalHours}h`}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="meetings" label="Reuniões" />
          <Tab value="actions" label="Ações" />
          <Tab value="transcripts" label="Transcrições" />
          <Tab value="templates" label="Templates" />
        </Tabs>

        {activeTab === 'meetings' && (
          <>
            {/* Search */}
            <Card>
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="flex-1 relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                    <Input
                      placeholder="Buscar reuniões..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                    Filtros
                  </Button>
                </div>
              </CardBody>
            </Card>

            {/* Meetings List */}
            <div className="grid gap-4">
              {filteredMeetings.map((meeting) => (
                <Card key={meeting.id} className="hover:border-accent-primary/50 transition-colors">
                  <CardBody>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          meeting.status === 'completed' ? 'bg-green-500/10' :
                          meeting.status === 'scheduled' ? 'bg-blue-500/10' : 'bg-yellow-500/10'
                        }`}>
                          <Video className={`w-6 h-6 ${
                            meeting.status === 'completed' ? 'text-green-500' :
                            meeting.status === 'scheduled' ? 'text-blue-500' : 'text-yellow-500'
                          }`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-medium text-text-primary">{meeting.title}</h3>
                            <Badge variant={statusConfig[meeting.status].color}>
                              {statusConfig[meeting.status].label}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-text-muted">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {new Date(meeting.date).toLocaleDateString('pt-BR')}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {meeting.duration} min
                            </span>
                            <span className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              {meeting.participants.length} participantes
                            </span>
                          </div>
                          <div className="flex items-center gap-2 mt-3">
                            {meeting.hasRecording && (
                              <Badge variant="secondary" size="sm" leftIcon={<Video className="w-3 h-3" />}>
                                Gravação
                              </Badge>
                            )}
                            {meeting.hasTranscript && (
                              <Badge variant="secondary" size="sm" leftIcon={<FileText className="w-3 h-3" />}>
                                Transcrição
                              </Badge>
                            )}
                            {meeting.hasSummary && (
                              <Badge variant="success" size="sm" leftIcon={<Sparkles className="w-3 h-3" />}>
                                Resumo IA
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {meeting.status === 'completed' && !meeting.hasSummary && (
                          <Button
                            variant="primary"
                            size="sm"
                            leftIcon={<Sparkles className={`w-4 h-4 ${isTranscribing ? 'animate-spin' : ''}`} />}
                            onClick={() => handleGenerateSummary(meeting.id)}
                            disabled={isTranscribing}
                          >
                            Gerar Resumo
                          </Button>
                        )}
                        <Button
                          variant="secondary"
                          size="sm"
                          leftIcon={<Eye className="w-4 h-4" />}
                          onClick={() => {
                            setSelectedMeeting(meeting);
                            setDetailsOpen(true);
                          }}
                        >
                          Ver Detalhes
                        </Button>
                        <Dropdown
                          trigger={
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          }
                          items={[
                            { label: 'Editar', icon: <Edit className="w-4 h-4" /> },
                            { label: 'Download', icon: <Download className="w-4 h-4" /> },
                            { label: 'Compartilhar', icon: <Share2 className="w-4 h-4" /> },
                            { label: 'Excluir', icon: <Trash2 className="w-4 h-4" /> },
                          ]}
                        />
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          </>
        )}

        {activeTab === 'actions' && (
          <Card>
            <CardHeader
              title="Ações das Reuniões"
              subtitle="Itens de ação extraídos automaticamente"
            />
            <CardBody>
              <div className="space-y-4">
                {meetings
                  .filter((m) => m.summary?.actionItems)
                  .flatMap((m) =>
                    m.summary!.actionItems.map((action) => ({
                      ...action,
                      meetingTitle: m.title,
                    }))
                  )
                  .map((action) => (
                    <div
                      key={action.id}
                      className="flex items-start justify-between p-4 bg-bg-tertiary rounded-lg"
                    >
                      <div className="flex items-start gap-3">
                        <input
                          type="checkbox"
                          checked={action.status === 'completed'}
                          className="mt-1 rounded"
                          onChange={() => {}}
                        />
                        <div>
                          <p className="font-medium text-text-primary">{action.description}</p>
                          <div className="flex items-center gap-4 mt-2 text-sm text-text-muted">
                            <span className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {action.assignee}
                            </span>
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {new Date(action.dueDate).toLocaleDateString('pt-BR')}
                            </span>
                            <span className="text-xs">{action.meetingTitle}</span>
                          </div>
                        </div>
                      </div>
                      <Badge variant={actionStatusConfig[action.status].color}>
                        {actionStatusConfig[action.status].label}
                      </Badge>
                    </div>
                  ))}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'transcripts' && (
          <Card>
            <CardHeader title="Transcrições Disponíveis" />
            <CardBody>
              <div className="space-y-4">
                {meetings
                  .filter((m) => m.hasTranscript)
                  .map((meeting) => (
                    <div
                      key={meeting.id}
                      className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                          <FileText className="w-5 h-5 text-accent-primary" />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{meeting.title}</p>
                          <p className="text-sm text-text-muted">
                            {new Date(meeting.date).toLocaleDateString('pt-BR')} • {meeting.duration} min
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="secondary" size="sm" leftIcon={<Eye className="w-4 h-4" />}>
                          Ver
                        </Button>
                        <Button variant="ghost" size="sm" leftIcon={<Download className="w-4 h-4" />}>
                          Download
                        </Button>
                      </div>
                    </div>
                  ))}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'templates' && (
          <div className="grid grid-cols-3 gap-6">
            {[
              { name: 'Reunião de Sprint', description: 'Template para reuniões de planejamento', icon: Target },
              { name: 'Alinhamento Cliente', description: 'Template para reuniões com clientes', icon: Users },
              { name: 'Review de Código', description: 'Template para code reviews', icon: FileText },
              { name: 'Retrospectiva', description: 'Template para retrospectivas', icon: TrendingUp },
              { name: 'Brainstorming', description: 'Template para sessões criativas', icon: Sparkles },
              { name: 'Decisão', description: 'Template para tomada de decisões', icon: CheckCircle2 },
            ].map((template) => (
              <Card key={template.name} className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                <CardBody>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                      <template.icon className="w-5 h-5 text-accent-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{template.name}</p>
                      <p className="text-xs text-text-muted">{template.description}</p>
                    </div>
                  </div>
                  <Button variant="secondary" size="sm" className="w-full">
                    Usar Template
                  </Button>
                </CardBody>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Meeting Details Modal */}
      <Modal
        isOpen={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        title={selectedMeeting?.title || ''}
        size="lg"
      >
        {selectedMeeting && (
          <div className="space-y-6">
            {/* Meeting Info */}
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="flex items-center gap-4 text-sm text-text-muted">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {new Date(selectedMeeting.date).toLocaleDateString('pt-BR')}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {selectedMeeting.duration} min
                </span>
                <span className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  {selectedMeeting.participants.join(', ')}
                </span>
              </div>
            </div>

            {selectedMeeting.summary && (
              <>
                {/* Overview */}
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Resumo</h4>
                  <p className="text-text-secondary">{selectedMeeting.summary.overview}</p>
                </div>

                {/* Key Points */}
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Pontos Principais</h4>
                  <ul className="space-y-2">
                    {selectedMeeting.summary.keyPoints.map((point, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-text-secondary">
                        <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5" />
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action Items */}
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Ações</h4>
                  <div className="space-y-2">
                    {selectedMeeting.summary.actionItems.map((action) => (
                      <div
                        key={action.id}
                        className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <input type="checkbox" checked={action.status === 'completed'} className="rounded" />
                          <span className="text-text-primary">{action.description}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-text-muted">{action.assignee}</span>
                          <Badge variant={actionStatusConfig[action.status].color} size="sm">
                            {actionStatusConfig[action.status].label}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Decisions */}
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Decisões</h4>
                  <ul className="space-y-2">
                    {selectedMeeting.summary.decisions.map((decision, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-text-secondary">
                        <Target className="w-4 h-4 text-accent-primary mt-0.5" />
                        {decision}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Next Steps */}
                <div>
                  <h4 className="font-medium text-text-primary mb-2">Próximos Passos</h4>
                  <ul className="space-y-2">
                    {selectedMeeting.summary.nextSteps.map((step, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-text-secondary">
                        <TrendingUp className="w-4 h-4 text-blue-500 mt-0.5" />
                        {step}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
                Exportar Ata
              </Button>
              <Button variant="secondary" leftIcon={<Share2 className="w-4 h-4" />}>
                Compartilhar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}

export default MeetingAssistantPage;
