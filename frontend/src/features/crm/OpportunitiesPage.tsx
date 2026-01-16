'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  DollarSign,
  Calendar,
  User,
  Building2,
  ArrowRight,
  Phone,
  Mail,
  GripVertical,
  TrendingUp,
  TrendingDown,
  Target,
  BarChart3,
  PieChartIcon,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Edit,
  Trash2,
  MessageSquare,
  FileText,
  Send,
  ChevronRight,
  ChevronDown,
  AlertTriangle,
  Zap,
  Award,
  Users,
  Download,
  RefreshCw,
  Settings,
  Percent,
  Activity,
  Star,
  ThumbsUp,
  ThumbsDown,
  History,
  MapPin,
  Briefcase,
  X,
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
  Modal,
  Select,
  StatCard,
  SimpleTabBar,
  DataTable,
  type Column,
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
  LineChart,
  Line,
  Legend,
  AreaChart,
  Area,
  FunnelChart,
  Funnel,
  LabelList,
  ComposedChart,
} from 'recharts';

// Types
interface OpportunityActivity {
  id: string;
  type: 'call' | 'email' | 'meeting' | 'note' | 'stage_change' | 'proposal_sent' | 'task';
  title: string;
  description: string;
  createdAt: string;
  createdBy: string;
  outcome?: 'positive' | 'neutral' | 'negative';
}

interface OpportunityTask {
  id: string;
  title: string;
  dueDate: string;
  completed: boolean;
  assignedTo: string;
}

interface Opportunity {
  id: string;
  title: string;
  client: string;
  clientCnpj?: string;
  clientEmail: string;
  clientPhone: string;
  clientAddress?: string;
  contactName?: string;
  contactRole?: string;
  value: number;
  recurrence: 'one_time' | 'monthly' | 'yearly';
  contractMonths?: number;
  stage: 'prospecting' | 'qualification' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  probability: number;
  expectedClose: string;
  assignedTo: string;
  assignedToAvatar?: string;
  lastActivity: string;
  tags: string[];
  source: 'website' | 'referral' | 'cold_call' | 'event' | 'partner' | 'marketing';
  competitor?: string;
  lossReason?: string;
  services: string[];
  notes?: string;
  activities: OpportunityActivity[];
  tasks: OpportunityTask[];
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
  stageHistory: { stage: string; date: string; days: number }[];
}

// Mock Data - Comprehensive
const initialOpportunities: Opportunity[] = [
  {
    id: '1',
    title: 'Segurança 24h - Condomínio Aurora',
    client: 'Condomínio Aurora',
    clientCnpj: '12.345.678/0001-90',
    clientEmail: 'contato@aurora.com.br',
    clientPhone: '(11) 3333-4444',
    clientAddress: 'Av. Paulista, 1000 - São Paulo/SP',
    contactName: 'João Mendes',
    contactRole: 'Síndico',
    value: 540000,
    recurrence: 'yearly',
    contractMonths: 12,
    stage: 'negotiation',
    probability: 80,
    expectedClose: '2026-02-15',
    assignedTo: 'Ana Costa',
    lastActivity: '2026-01-15',
    tags: ['Enterprise', 'Urgente'],
    source: 'referral',
    services: ['Vigilância Armada', 'Monitoramento CFTV', 'Ronda'],
    notes: 'Cliente muito interessado, preocupação principal é o custo.',
    priority: 'high',
    createdAt: '2025-12-01',
    stageHistory: [
      { stage: 'prospecting', date: '2025-12-01', days: 10 },
      { stage: 'qualification', date: '2025-12-11', days: 15 },
      { stage: 'proposal', date: '2025-12-26', days: 10 },
      { stage: 'negotiation', date: '2026-01-05', days: 11 },
    ],
    activities: [
      { id: '1', type: 'meeting', title: 'Reunião de apresentação', description: 'Apresentamos a proposta completa ao síndico', createdAt: '2026-01-15T14:00:00', createdBy: 'Ana Costa', outcome: 'positive' },
      { id: '2', type: 'email', title: 'Envio de proposta revisada', description: 'Proposta com desconto de 5% conforme negociado', createdAt: '2026-01-12T10:30:00', createdBy: 'Ana Costa', outcome: 'neutral' },
      { id: '3', type: 'call', title: 'Ligação de follow-up', description: 'Cliente solicitou redução no valor', createdAt: '2026-01-08T16:00:00', createdBy: 'Ana Costa', outcome: 'neutral' },
      { id: '4', type: 'proposal_sent', title: 'Proposta inicial enviada', description: 'PROP-2025-0089 enviada por email', createdAt: '2025-12-26T09:00:00', createdBy: 'Ana Costa', outcome: 'positive' },
    ],
    tasks: [
      { id: '1', title: 'Ligar para confirmar reunião final', dueDate: '2026-01-20', completed: false, assignedTo: 'Ana Costa' },
      { id: '2', title: 'Preparar contrato', dueDate: '2026-01-22', completed: false, assignedTo: 'Ana Costa' },
    ],
  },
  {
    id: '2',
    title: 'Facilities Completo - Shopping Center Norte',
    client: 'Shopping Center Norte',
    clientCnpj: '23.456.789/0001-01',
    clientEmail: 'comercial@scn.com.br',
    clientPhone: '(11) 2222-5555',
    clientAddress: 'Av. Brasil, 500 - São Paulo/SP',
    contactName: 'Roberto Lima',
    contactRole: 'Gerente Operacional',
    value: 1536000,
    recurrence: 'yearly',
    contractMonths: 24,
    stage: 'proposal',
    probability: 60,
    expectedClose: '2026-03-01',
    assignedTo: 'Carlos Lima',
    lastActivity: '2026-01-14',
    tags: ['Enterprise', 'Facilities'],
    source: 'event',
    competitor: 'Facility Group',
    services: ['Limpeza', 'Segurança', 'Manutenção', 'Jardinagem'],
    notes: 'Grande oportunidade. Concorrente atual tem problemas de SLA.',
    priority: 'high',
    createdAt: '2025-11-15',
    stageHistory: [
      { stage: 'prospecting', date: '2025-11-15', days: 14 },
      { stage: 'qualification', date: '2025-11-29', days: 21 },
      { stage: 'proposal', date: '2025-12-20', days: 26 },
    ],
    activities: [
      { id: '1', type: 'meeting', title: 'Visita técnica', description: 'Realizada visita para levantamento de necessidades', createdAt: '2026-01-14T10:00:00', createdBy: 'Carlos Lima', outcome: 'positive' },
      { id: '2', type: 'proposal_sent', title: 'Proposta completa enviada', description: 'Proposta incluindo todos os serviços solicitados', createdAt: '2025-12-20T15:00:00', createdBy: 'Carlos Lima', outcome: 'neutral' },
    ],
    tasks: [
      { id: '1', title: 'Enviar case studies de shoppings', dueDate: '2026-01-18', completed: false, assignedTo: 'Carlos Lima' },
    ],
  },
  {
    id: '3',
    title: 'Portaria Inteligente - Tech Park',
    client: 'Tech Park Empresarial',
    clientCnpj: '56.789.012/0001-34',
    clientEmail: 'admin@techpark.io',
    clientPhone: '(11) 5555-6666',
    contactName: 'Eduardo Ramos',
    contactRole: 'Facilities Manager',
    value: 324000,
    recurrence: 'yearly',
    contractMonths: 12,
    stage: 'qualification',
    probability: 40,
    expectedClose: '2026-04-01',
    assignedTo: 'Ana Costa',
    lastActivity: '2026-01-13',
    tags: ['Tecnologia', 'Inovação'],
    source: 'website',
    services: ['Portaria Remota', 'Controle de Acesso', 'CFTV IP'],
    priority: 'medium',
    createdAt: '2025-12-20',
    stageHistory: [
      { stage: 'prospecting', date: '2025-12-20', days: 10 },
      { stage: 'qualification', date: '2025-12-30', days: 15 },
    ],
    activities: [
      { id: '1', type: 'call', title: 'Ligação de qualificação', description: 'Levantamento inicial de necessidades', createdAt: '2026-01-13T11:00:00', createdBy: 'Ana Costa', outcome: 'positive' },
    ],
    tasks: [
      { id: '1', title: 'Agendar demo do sistema', dueDate: '2026-01-25', completed: false, assignedTo: 'Ana Costa' },
    ],
  },
  {
    id: '4',
    title: 'Limpeza Hospitalar - Hospital São Lucas',
    client: 'Hospital São Lucas',
    clientCnpj: '34.567.890/0001-12',
    clientEmail: 'compras@hsl.com.br',
    clientPhone: '(21) 4444-7777',
    contactName: 'Dr. Fernando Melo',
    contactRole: 'Diretor Administrativo',
    value: 2220000,
    recurrence: 'yearly',
    contractMonths: 24,
    stage: 'prospecting',
    probability: 20,
    expectedClose: '2026-05-01',
    assignedTo: 'Roberto Dias',
    lastActivity: '2026-01-12',
    tags: ['Healthcare', 'Grande Porte'],
    source: 'cold_call',
    services: ['Limpeza Hospitalar', 'Higienização', 'Tratamento de Resíduos'],
    notes: 'Primeira abordagem realizada. Contrato atual vence em Maio.',
    priority: 'medium',
    createdAt: '2026-01-05',
    stageHistory: [
      { stage: 'prospecting', date: '2026-01-05', days: 11 },
    ],
    activities: [
      { id: '1', type: 'cold_call', title: 'Primeira ligação', description: 'Consegui falar com a secretária do diretor', createdAt: '2026-01-12T09:30:00', createdBy: 'Roberto Dias', outcome: 'neutral' },
    ],
    tasks: [
      { id: '1', title: 'Enviar apresentação institucional', dueDate: '2026-01-17', completed: true, assignedTo: 'Roberto Dias' },
      { id: '2', title: 'Ligar para agendar reunião', dueDate: '2026-01-22', completed: false, assignedTo: 'Roberto Dias' },
    ],
  },
  {
    id: '5',
    title: 'Manutenção Predial - Edifício Corporate',
    client: 'Edifício Corporate Tower',
    clientCnpj: '45.678.901/0001-23',
    clientEmail: 'sindico@corporate.com',
    clientPhone: '(11) 7777-8888',
    contactName: 'Paulo César',
    contactRole: 'Síndico',
    value: 180000,
    recurrence: 'yearly',
    contractMonths: 12,
    stage: 'closed_won',
    probability: 100,
    expectedClose: '2026-01-10',
    assignedTo: 'Carlos Lima',
    lastActivity: '2026-01-10',
    tags: ['Manutenção'],
    source: 'referral',
    services: ['Manutenção Elétrica', 'Manutenção Hidráulica'],
    priority: 'low',
    createdAt: '2025-11-01',
    stageHistory: [
      { stage: 'prospecting', date: '2025-11-01', days: 7 },
      { stage: 'qualification', date: '2025-11-08', days: 14 },
      { stage: 'proposal', date: '2025-11-22', days: 21 },
      { stage: 'negotiation', date: '2025-12-13', days: 28 },
      { stage: 'closed_won', date: '2026-01-10', days: 0 },
    ],
    activities: [
      { id: '1', type: 'stage_change', title: 'Contrato fechado!', description: 'Cliente assinou contrato CONT-2026-0004', createdAt: '2026-01-10T16:00:00', createdBy: 'Sistema', outcome: 'positive' },
    ],
    tasks: [],
  },
  {
    id: '6',
    title: 'Segurança Bancária - Banco Regional',
    client: 'Banco Regional',
    clientCnpj: '67.890.123/0001-45',
    clientEmail: 'seguranca@bancoregional.com.br',
    clientPhone: '(11) 8888-9999',
    contactName: 'André Machado',
    contactRole: 'Gerente de Segurança',
    value: 2640000,
    recurrence: 'yearly',
    contractMonths: 36,
    stage: 'negotiation',
    probability: 75,
    expectedClose: '2026-02-28',
    assignedTo: 'Roberto Dias',
    lastActivity: '2026-01-15',
    tags: ['Financeiro', 'VIP', 'Enterprise'],
    source: 'partner',
    competitor: 'Securitas',
    services: ['Vigilância Armada', 'Escolta de Valores', 'Monitoramento 24h'],
    notes: 'Oportunidade estratégica. CEO demonstrou interesse pessoalmente.',
    priority: 'high',
    createdAt: '2025-10-15',
    stageHistory: [
      { stage: 'prospecting', date: '2025-10-15', days: 14 },
      { stage: 'qualification', date: '2025-10-29', days: 21 },
      { stage: 'proposal', date: '2025-11-19', days: 28 },
      { stage: 'negotiation', date: '2025-12-17', days: 30 },
    ],
    activities: [
      { id: '1', type: 'meeting', title: 'Reunião com diretoria', description: 'Apresentação para o board executivo', createdAt: '2026-01-15T14:00:00', createdBy: 'Roberto Dias', outcome: 'positive' },
    ],
    tasks: [
      { id: '1', title: 'Revisar condições comerciais', dueDate: '2026-01-20', completed: false, assignedTo: 'Roberto Dias' },
    ],
  },
  {
    id: '7',
    title: 'Limpeza Industrial - Metalúrgica ABC',
    client: 'Indústria Metalúrgica ABC',
    clientCnpj: '78.901.234/0001-56',
    clientEmail: 'compras@metalabc.com.br',
    clientPhone: '(11) 9999-0000',
    contactName: 'Fernanda Lima',
    contactRole: 'Gerente de Compras',
    value: 1068000,
    recurrence: 'yearly',
    contractMonths: 12,
    stage: 'closed_lost',
    probability: 0,
    expectedClose: '2026-01-05',
    assignedTo: 'Carlos Lima',
    lastActivity: '2026-01-05',
    tags: ['Industrial'],
    source: 'marketing',
    lossReason: 'Preço - concorrente ofereceu 15% menor',
    services: ['Limpeza Industrial'],
    priority: 'low',
    createdAt: '2025-11-20',
    stageHistory: [
      { stage: 'prospecting', date: '2025-11-20', days: 10 },
      { stage: 'qualification', date: '2025-11-30', days: 14 },
      { stage: 'proposal', date: '2025-12-14', days: 12 },
      { stage: 'negotiation', date: '2025-12-26', days: 10 },
      { stage: 'closed_lost', date: '2026-01-05', days: 0 },
    ],
    activities: [
      { id: '1', type: 'stage_change', title: 'Oportunidade perdida', description: 'Cliente optou pelo concorrente devido ao preço', createdAt: '2026-01-05T11:00:00', createdBy: 'Carlos Lima', outcome: 'negative' },
    ],
    tasks: [],
  },
  {
    id: '8',
    title: 'Vigilância - Universidade Federal',
    client: 'Universidade Federal',
    clientCnpj: '89.012.345/0001-67',
    clientEmail: 'licitacao@uf.edu.br',
    clientPhone: '(11) 1111-2222',
    contactName: 'Prof. Ricardo Gomes',
    contactRole: 'Pró-Reitor Administrativo',
    value: 804000,
    recurrence: 'yearly',
    contractMonths: 12,
    stage: 'prospecting',
    probability: 25,
    expectedClose: '2026-06-01',
    assignedTo: 'Ana Costa',
    lastActivity: '2026-01-10',
    tags: ['Educação', 'Licitação'],
    source: 'website',
    services: ['Portaria', 'Vigilância', 'Rondas'],
    notes: 'Processo licitatório previsto para Março. Preparar documentação.',
    priority: 'medium',
    createdAt: '2026-01-08',
    stageHistory: [
      { stage: 'prospecting', date: '2026-01-08', days: 8 },
    ],
    activities: [
      { id: '1', type: 'note', title: 'Pesquisa de edital', description: 'Verificando requisitos do edital anterior', createdAt: '2026-01-10T14:00:00', createdBy: 'Ana Costa', outcome: 'neutral' },
    ],
    tasks: [
      { id: '1', title: 'Levantar documentação para licitação', dueDate: '2026-02-15', completed: false, assignedTo: 'Ana Costa' },
    ],
  },
];

const stages = [
  { id: 'prospecting', label: 'Prospecção', color: '#3b82f6', bgColor: 'bg-info' },
  { id: 'qualification', label: 'Qualificação', color: '#6366f1', bgColor: 'bg-primary' },
  { id: 'proposal', label: 'Proposta', color: '#f59e0b', bgColor: 'bg-warning' },
  { id: 'negotiation', label: 'Negociação', color: '#8b5cf6', bgColor: 'bg-accent-secondary' },
  { id: 'closed_won', label: 'Ganho', color: '#10b981', bgColor: 'bg-success' },
  { id: 'closed_lost', label: 'Perdido', color: '#ef4444', bgColor: 'bg-danger' },
];

const sourceLabels: Record<string, string> = {
  website: 'Website',
  referral: 'Indicação',
  cold_call: 'Cold Call',
  event: 'Evento',
  partner: 'Parceiro',
  marketing: 'Marketing',
};

const priorityConfig = {
  low: { label: 'Baixa', color: 'neutral' as const },
  medium: { label: 'Média', color: 'warning' as const },
  high: { label: 'Alta', color: 'danger' as const },
};

// Opportunity Card Component
function OpportunityCard({
  opportunity,
  onClick,
}: {
  opportunity: Opportunity;
  onClick: () => void;
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className={`bg-bg-secondary border rounded-lg p-4 cursor-pointer hover:border-accent-primary/50 transition-colors group ${
        opportunity.priority === 'high' ? 'border-l-4 border-l-danger border-border' : 'border-border'
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-medium text-text-primary text-sm line-clamp-2">
            {opportunity.title}
          </h4>
          <p className="text-xs text-text-muted mt-0.5 flex items-center gap-1">
            <Building2 className="w-3 h-3" />
            {opportunity.client}
          </p>
        </div>
        {opportunity.priority === 'high' && (
          <Badge variant="danger" size="sm">
            <Zap className="w-3 h-3" />
          </Badge>
        )}
      </div>

      <div className="flex items-center gap-2 mb-3">
        <DollarSign className="w-4 h-4 text-success" />
        <span className="font-mono text-sm font-medium text-text-primary">
          {opportunity.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
        <span className="text-xs text-text-muted">
          /{opportunity.recurrence === 'monthly' ? 'mês' : 'ano'}
        </span>
      </div>

      <div className="flex items-center justify-between text-xs text-text-muted mb-3">
        <div className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          <span>{new Date(opportunity.expectedClose).toLocaleDateString('pt-BR')}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-12 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                opportunity.probability >= 70 ? 'bg-success' :
                opportunity.probability >= 40 ? 'bg-warning' : 'bg-danger'
              }`}
              style={{ width: `${opportunity.probability}%` }}
            />
          </div>
          <span className="font-medium">{opportunity.probability}%</span>
        </div>
      </div>

      {opportunity.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {opportunity.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="outline" size="sm">
              {tag}
            </Badge>
          ))}
          {opportunity.tags.length > 2 && (
            <Badge variant="neutral" size="sm">
              +{opportunity.tags.length - 2}
            </Badge>
          )}
        </div>
      )}

      <div className="flex items-center justify-between pt-3 border-t border-border-subtle">
        <div className="flex items-center gap-2">
          <Avatar name={opportunity.assignedTo} size="xs" />
          <span className="text-xs text-text-secondary">{opportunity.assignedTo}</span>
        </div>
        {opportunity.tasks.filter(t => !t.completed).length > 0 && (
          <Badge variant="info" size="sm">
            {opportunity.tasks.filter(t => !t.completed).length} tarefa(s)
          </Badge>
        )}
      </div>
    </motion.div>
  );
}

// Kanban Column Component
function KanbanColumn({
  stage,
  opportunities,
  totalValue,
  onCardClick,
}: {
  stage: typeof stages[0];
  opportunities: Opportunity[];
  totalValue: number;
  onCardClick: (opp: Opportunity) => void;
}) {
  return (
    <div className="flex flex-col min-w-[300px] max-w-[300px]">
      {/* Column Header */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: stage.color }} />
          <h3 className="font-medium text-text-primary">{stage.label}</h3>
          <Badge variant="neutral" size="sm">{opportunities.length}</Badge>
        </div>
        <span className="text-xs font-mono text-text-muted">
          {totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      </div>

      {/* Column Cards */}
      <div className="flex-1 space-y-3 min-h-[200px] p-2 bg-bg-primary/50 rounded-lg border border-border-subtle overflow-y-auto max-h-[calc(100vh-400px)]">
        <AnimatePresence>
          {opportunities.map((opportunity) => (
            <OpportunityCard
              key={opportunity.id}
              opportunity={opportunity}
              onClick={() => onCardClick(opportunity)}
            />
          ))}
        </AnimatePresence>

        {opportunities.length === 0 && (
          <div className="flex items-center justify-center h-32 text-text-muted text-sm">
            Nenhuma oportunidade
          </div>
        )}
      </div>
    </div>
  );
}

export function OpportunitiesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [opportunities] = useState(initialOpportunities);
  const [showNewModal, setShowNewModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [mainTab, setMainTab] = useState('kanban');
  const [detailTab, setDetailTab] = useState('overview');
  const [filterAssignee, setFilterAssignee] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [viewMode, setViewMode] = useState<'kanban' | 'table'>('kanban');

  // Filtered opportunities
  const filteredOpportunities = useMemo(() => {
    return opportunities.filter((opp) => {
      const matchesSearch =
        opp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        opp.client.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesAssignee = !filterAssignee || opp.assignedTo === filterAssignee;
      const matchesPriority = !filterPriority || opp.priority === filterPriority;
      const matchesSource = !filterSource || opp.source === filterSource;
      return matchesSearch && matchesAssignee && matchesPriority && matchesSource;
    });
  }, [opportunities, searchTerm, filterAssignee, filterPriority, filterSource]);

  // Pipeline stats
  const stats = useMemo(() => {
    const activeOpportunities = opportunities.filter(
      (o) => !['closed_won', 'closed_lost'].includes(o.stage)
    );

    const totalPipeline = activeOpportunities.reduce((acc, o) => acc + o.value, 0);
    const weightedPipeline = activeOpportunities.reduce(
      (acc, o) => acc + o.value * (o.probability / 100),
      0
    );
    const wonValue = opportunities
      .filter((o) => o.stage === 'closed_won')
      .reduce((acc, o) => acc + o.value, 0);
    const lostValue = opportunities
      .filter((o) => o.stage === 'closed_lost')
      .reduce((acc, o) => acc + o.value, 0);
    const wonCount = opportunities.filter((o) => o.stage === 'closed_won').length;
    const lostCount = opportunities.filter((o) => o.stage === 'closed_lost').length;
    const winRate = wonCount + lostCount > 0 ? Math.round((wonCount / (wonCount + lostCount)) * 100) : 0;
    const avgDealSize = activeOpportunities.length > 0
      ? totalPipeline / activeOpportunities.length
      : 0;
    const highPriorityCount = activeOpportunities.filter((o) => o.priority === 'high').length;
    const thisMonthClosing = activeOpportunities.filter((o) => {
      const closeDate = new Date(o.expectedClose);
      const now = new Date();
      return closeDate.getMonth() === now.getMonth() && closeDate.getFullYear() === now.getFullYear();
    });
    const thisMonthValue = thisMonthClosing.reduce((acc, o) => acc + o.value, 0);

    return {
      totalPipeline,
      weightedPipeline,
      wonValue,
      lostValue,
      winRate,
      avgDealSize,
      activeCount: activeOpportunities.length,
      highPriorityCount,
      thisMonthValue,
      thisMonthCount: thisMonthClosing.length,
    };
  }, [opportunities]);

  // Chart data
  const funnelData = useMemo(() => {
    return stages
      .filter((s) => !['closed_won', 'closed_lost'].includes(s.id))
      .map((stage) => {
        const stageOpps = opportunities.filter((o) => o.stage === stage.id);
        return {
          name: stage.label,
          value: stageOpps.reduce((acc, o) => acc + o.value, 0),
          count: stageOpps.length,
          fill: stage.color,
        };
      });
  }, [opportunities]);

  const pipelineByAssignee = useMemo(() => {
    const byAssignee: Record<string, number> = {};
    opportunities
      .filter((o) => !['closed_won', 'closed_lost'].includes(o.stage))
      .forEach((o) => {
        byAssignee[o.assignedTo] = (byAssignee[o.assignedTo] || 0) + o.value;
      });
    return Object.entries(byAssignee).map(([name, value]) => ({ name, value }));
  }, [opportunities]);

  const monthlyForecast = [
    { month: 'Jan', previsto: 380000, realizado: 180000 },
    { month: 'Fev', previsto: 1240000, realizado: 0 },
    { month: 'Mar', previsto: 1860000, realizado: 0 },
    { month: 'Abr', previsto: 524000, realizado: 0 },
    { month: 'Mai', previsto: 2220000, realizado: 0 },
    { month: 'Jun', previsto: 804000, realizado: 0 },
  ];

  const sourceDistribution = useMemo(() => {
    const bySource: Record<string, number> = {};
    opportunities.forEach((o) => {
      bySource[o.source] = (bySource[o.source] || 0) + 1;
    });
    return Object.entries(bySource).map(([source, count], index) => ({
      name: sourceLabels[source] || source,
      value: count,
      color: ['#6366f1', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ef4444'][index % 6],
    }));
  }, [opportunities]);

  // Open detail modal
  const openDetail = (opp: Opportunity) => {
    setSelectedOpportunity(opp);
    setDetailTab('overview');
    setShowDetailModal(true);
  };

  // Unique assignees for filter
  const assignees = useMemo(() => {
    const unique = [...new Set(opportunities.map((o) => o.assignedTo))];
    return unique.map((name) => ({ value: name, label: name }));
  }, [opportunities]);

  // Table columns
  const columns: Column<Opportunity>[] = [
    {
      key: 'title',
      header: 'Oportunidade',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.title}</p>
          <p className="text-xs text-text-muted flex items-center gap-1">
            <Building2 className="w-3 h-3" />
            {row.client}
          </p>
        </div>
      ),
    },
    {
      key: 'value',
      header: 'Valor',
      sortable: true,
      render: (row) => (
        <span className="font-mono text-text-primary">
          {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
      ),
    },
    {
      key: 'stage',
      header: 'Etapa',
      render: (row) => {
        const stage = stages.find((s) => s.id === row.stage);
        return (
          <Badge
            variant={row.stage === 'closed_won' ? 'success' : row.stage === 'closed_lost' ? 'danger' : 'primary'}
          >
            {stage?.label}
          </Badge>
        );
      },
    },
    {
      key: 'probability',
      header: 'Probabilidade',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <div className="w-16 h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                row.probability >= 70 ? 'bg-success' :
                row.probability >= 40 ? 'bg-warning' : 'bg-danger'
              }`}
              style={{ width: `${row.probability}%` }}
            />
          </div>
          <span className="text-sm">{row.probability}%</span>
        </div>
      ),
    },
    {
      key: 'expectedClose',
      header: 'Fechamento',
      sortable: true,
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.expectedClose).toLocaleDateString('pt-BR')}
        </span>
      ),
    },
    {
      key: 'assignedTo',
      header: 'Responsável',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Avatar name={row.assignedTo} size="xs" />
          <span className="text-sm">{row.assignedTo}</span>
        </div>
      ),
    },
    {
      key: 'priority',
      header: 'Prioridade',
      render: (row) => (
        <Badge variant={priorityConfig[row.priority].color} size="sm">
          {priorityConfig[row.priority].label}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={(e) => {
            e.stopPropagation();
            openDetail(row);
          }}
        >
          <Eye className="w-4 h-4" />
        </Button>
      ),
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Pipeline de Oportunidades
            </h1>
            <p className="text-text-secondary mt-1">
              Visualize e gerencie o funil de vendas
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setShowNewModal(true)}
            >
              Nova Oportunidade
            </Button>
          </div>
        </div>

        {/* Main Tabs */}
        <SimpleTabBar
          tabs={[
            { value: 'kanban', label: 'Pipeline', icon: <Target className="w-4 h-4" /> },
            { value: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
            { value: 'forecast', label: 'Forecast', icon: <TrendingUp className="w-4 h-4" /> },
          ]}
          value={mainTab}
          onChange={setMainTab}
        />

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Pipeline Total"
              value={stats.totalPipeline.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Target className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Pipeline Ponderado"
              value={stats.weightedPipeline.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Percent className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Ganhos"
              value={stats.wonValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Taxa de Conversão"
              value={`${stats.winRate}%`}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="secondary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Oportunidades Ativas"
              value={stats.activeCount}
              icon={<Activity className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <StatCard
              title="Alta Prioridade"
              value={stats.highPriorityCount}
              icon={<Zap className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </div>

        {/* Kanban Tab */}
        {mainTab === 'kanban' && (
          <>
            {/* Filters */}
            <Card>
              <CardBody className="py-4">
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <div className="flex items-center gap-3">
                    <Input
                      placeholder="Buscar oportunidades..."
                      leftIcon={<Search className="w-4 h-4" />}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-64"
                    />
                    <Select
                      options={[{ value: '', label: 'Todos responsáveis' }, ...assignees]}
                      value={filterAssignee}
                      onChange={setFilterAssignee}
                      className="w-40"
                    />
                    <Select
                      options={[
                        { value: '', label: 'Todas prioridades' },
                        { value: 'high', label: 'Alta' },
                        { value: 'medium', label: 'Média' },
                        { value: 'low', label: 'Baixa' },
                      ]}
                      value={filterPriority}
                      onChange={setFilterPriority}
                      className="w-36"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant={viewMode === 'kanban' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('kanban')}
                    >
                      Kanban
                    </Button>
                    <Button
                      variant={viewMode === 'table' ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('table')}
                    >
                      Tabela
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Kanban Board */}
            {viewMode === 'kanban' ? (
              <div className="overflow-x-auto pb-4">
                <div className="flex gap-4 min-w-max">
                  {stages
                    .filter((s) => s.id !== 'closed_lost')
                    .map((stage) => {
                      const stageOpportunities = filteredOpportunities.filter(
                        (o) => o.stage === stage.id
                      );
                      const totalValue = stageOpportunities.reduce((acc, o) => acc + o.value, 0);

                      return (
                        <KanbanColumn
                          key={stage.id}
                          stage={stage}
                          opportunities={stageOpportunities}
                          totalValue={totalValue}
                          onCardClick={openDetail}
                        />
                      );
                    })}
                </div>
              </div>
            ) : (
              <Card>
                <CardBody className="p-0">
                  <DataTable
                    columns={columns}
                    data={filteredOpportunities}
                    keyExtractor={(row) => row.id}
                    onRowClick={openDetail}
                  />
                </CardBody>
              </Card>
            )}

            {/* This Month Alert */}
            {stats.thisMonthCount > 0 && (
              <Card className="border-info/30 bg-info/5">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-info/10">
                      <Calendar className="w-6 h-6 text-info" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-text-primary">
                        {stats.thisMonthCount} oportunidade(s) com fechamento previsto este mês
                      </p>
                      <p className="text-sm text-text-secondary mt-1">
                        Valor total: {stats.thisMonthValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Ver Detalhes
                    </Button>
                  </div>
                </CardBody>
              </Card>
            )}
          </>
        )}

        {/* Analytics Tab */}
        {mainTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Funnel Chart */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Funil de Vendas</h3>
                    <p className="text-sm text-text-secondary">Distribuição por etapa</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {funnelData.map((stage, index) => {
                    const maxValue = Math.max(...funnelData.map((s) => s.value));
                    const width = maxValue > 0 ? (stage.value / maxValue) * 100 : 0;
                    return (
                      <div key={stage.name} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-text-primary">{stage.name}</span>
                          <div className="flex items-center gap-3">
                            <Badge variant="neutral" size="sm">{stage.count}</Badge>
                            <span className="font-mono text-text-muted">
                              {stage.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </span>
                          </div>
                        </div>
                        <div className="h-8 bg-bg-tertiary rounded-lg overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${width}%` }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className="h-full rounded-lg"
                            style={{ backgroundColor: stage.fill }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>

            {/* Pipeline by Assignee */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Pipeline por Vendedor</h3>
                    <p className="text-sm text-text-secondary">Distribuição de valor</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={pipelineByAssignee} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#64748b" fontSize={12} tickFormatter={(v) => `${(v/1000)}K`} />
                    <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={12} width={100} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      formatter={(value: number) => [value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), 'Pipeline']}
                    />
                    <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>

            {/* Source Distribution */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Origem das Oportunidades</h3>
                    <p className="text-sm text-text-secondary">Canais de aquisição</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="flex items-center gap-6">
                  <div className="w-48 h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={sourceDistribution}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          dataKey="value"
                        >
                          {sourceDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex-1 space-y-3">
                    {sourceDistribution.map((source) => (
                      <div key={source.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: source.color }} />
                          <span className="text-sm text-text-secondary">{source.name}</span>
                        </div>
                        <span className="text-sm font-medium text-text-primary">{source.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Win/Loss Analysis */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Análise de Conversão</h3>
                    <p className="text-sm text-text-secondary">Ganhos vs Perdas</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="grid grid-cols-2 gap-6">
                  <div className="text-center p-6 rounded-lg bg-success/5 border border-success/20">
                    <CheckCircle2 className="w-10 h-10 text-success mx-auto mb-3" />
                    <p className="text-3xl font-bold text-success">
                      {opportunities.filter((o) => o.stage === 'closed_won').length}
                    </p>
                    <p className="text-sm text-text-secondary mt-1">Oportunidades Ganhas</p>
                    <p className="text-lg font-mono text-success mt-2">
                      {stats.wonValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                  </div>
                  <div className="text-center p-6 rounded-lg bg-danger/5 border border-danger/20">
                    <XCircle className="w-10 h-10 text-danger mx-auto mb-3" />
                    <p className="text-3xl font-bold text-danger">
                      {opportunities.filter((o) => o.stage === 'closed_lost').length}
                    </p>
                    <p className="text-sm text-text-secondary mt-1">Oportunidades Perdidas</p>
                    <p className="text-lg font-mono text-danger mt-2">
                      {stats.lostValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                  </div>
                </div>

                <div className="mt-6 p-4 rounded-lg bg-bg-tertiary">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-text-secondary">Taxa de Conversão</span>
                    <span className="text-lg font-bold text-text-primary">{stats.winRate}%</span>
                  </div>
                  <div className="h-3 bg-bg-primary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-success rounded-full"
                      style={{ width: `${stats.winRate}%` }}
                    />
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Forecast Tab */}
        {mainTab === 'forecast' && (
          <div className="space-y-6">
            {/* Monthly Forecast Chart */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Previsão de Fechamento</h3>
                    <p className="text-sm text-text-secondary">Próximos 6 meses</p>
                  </div>
                  <Badge variant="info">Baseado no pipeline atual</Badge>
                </div>
              </CardHeader>
              <CardBody>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={monthlyForecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${(v/1000)}K`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      formatter={(value: number) => [value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), '']}
                    />
                    <Legend />
                    <Bar dataKey="previsto" name="Previsto" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="realizado" name="Realizado" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>

            {/* Upcoming Closes */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Próximos Fechamentos</h3>
                    <p className="text-sm text-text-secondary">Oportunidades por data de fechamento</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {opportunities
                    .filter((o) => !['closed_won', 'closed_lost'].includes(o.stage))
                    .sort((a, b) => new Date(a.expectedClose).getTime() - new Date(b.expectedClose).getTime())
                    .slice(0, 6)
                    .map((opp) => {
                      const daysLeft = Math.ceil((new Date(opp.expectedClose).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
                      return (
                        <div
                          key={opp.id}
                          className="flex items-center gap-4 p-4 rounded-lg bg-bg-tertiary hover:bg-bg-hover transition-colors cursor-pointer"
                          onClick={() => openDetail(opp)}
                        >
                          <div className={`p-2 rounded-lg ${
                            daysLeft <= 7 ? 'bg-danger/10' :
                            daysLeft <= 30 ? 'bg-warning/10' : 'bg-info/10'
                          }`}>
                            <Calendar className={`w-5 h-5 ${
                              daysLeft <= 7 ? 'text-danger' :
                              daysLeft <= 30 ? 'text-warning' : 'text-info'
                            }`} />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-text-primary">{opp.title}</p>
                            <p className="text-sm text-text-secondary">{opp.client}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-mono font-medium text-text-primary">
                              {opp.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </p>
                            <p className="text-xs text-text-muted">
                              {daysLeft > 0 ? `em ${daysLeft} dias` : 'Atrasado'}
                            </p>
                          </div>
                          <Badge variant={opp.probability >= 70 ? 'success' : opp.probability >= 40 ? 'warning' : 'danger'}>
                            {opp.probability}%
                          </Badge>
                        </div>
                      );
                    })}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedOpportunity?.title || 'Detalhes'}
          size="xl"
        >
          {selectedOpportunity && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-accent-primary/10">
                    <Target className="w-8 h-8 text-accent-primary" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedOpportunity.client}</h3>
                    <p className="text-sm text-text-secondary">{selectedOpportunity.clientCnpj}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={priorityConfig[selectedOpportunity.priority].color}>
                        {priorityConfig[selectedOpportunity.priority].label}
                      </Badge>
                      <Badge variant={selectedOpportunity.stage === 'closed_won' ? 'success' : selectedOpportunity.stage === 'closed_lost' ? 'danger' : 'primary'}>
                        {stages.find((s) => s.id === selectedOpportunity.stage)?.label}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-accent-primary">
                    {selectedOpportunity.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                  <p className="text-sm text-text-muted">
                    /{selectedOpportunity.recurrence === 'monthly' ? 'mês' : 'ano'}
                    {selectedOpportunity.contractMonths && ` • ${selectedOpportunity.contractMonths} meses`}
                  </p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="p-4 rounded-lg bg-bg-tertiary">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-text-secondary">Probabilidade de Fechamento</span>
                  <span className="text-lg font-bold text-text-primary">{selectedOpportunity.probability}%</span>
                </div>
                <div className="h-3 bg-bg-primary rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      selectedOpportunity.probability >= 70 ? 'bg-success' :
                      selectedOpportunity.probability >= 40 ? 'bg-warning' : 'bg-danger'
                    }`}
                    style={{ width: `${selectedOpportunity.probability}%` }}
                  />
                </div>
              </div>

              {/* Detail Tabs */}
              <SimpleTabBar
                tabs={[
                  { value: 'overview', label: 'Visão Geral', icon: <FileText className="w-4 h-4" /> },
                  { value: 'activities', label: 'Atividades', icon: <Activity className="w-4 h-4" /> },
                  { value: 'tasks', label: 'Tarefas', icon: <CheckCircle2 className="w-4 h-4" /> },
                  { value: 'history', label: 'Histórico', icon: <History className="w-4 h-4" /> },
                ]}
                value={detailTab}
                onChange={setDetailTab}
                variant="pills"
              />

              {/* Overview Tab */}
              {detailTab === 'overview' && (
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <User className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Contato</span>
                      </div>
                      <p className="text-text-primary">{selectedOpportunity.contactName || '-'}</p>
                      <p className="text-sm text-text-muted">{selectedOpportunity.contactRole}</p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Mail className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Email</span>
                      </div>
                      <p className="text-text-primary">{selectedOpportunity.clientEmail}</p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Phone className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Telefone</span>
                      </div>
                      <p className="text-text-primary">{selectedOpportunity.clientPhone}</p>
                    </div>

                    {selectedOpportunity.clientAddress && (
                      <div className="p-4 rounded-lg bg-bg-tertiary">
                        <div className="flex items-center gap-2 mb-3">
                          <MapPin className="w-4 h-4 text-text-muted" />
                          <span className="text-sm font-medium text-text-secondary">Endereço</span>
                        </div>
                        <p className="text-text-primary">{selectedOpportunity.clientAddress}</p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Calendar className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Fechamento Previsto</span>
                      </div>
                      <p className="text-text-primary">
                        {new Date(selectedOpportunity.expectedClose).toLocaleDateString('pt-BR', {
                          weekday: 'long',
                          day: '2-digit',
                          month: 'long',
                          year: 'numeric',
                        })}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Briefcase className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Serviços</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {selectedOpportunity.services.map((service) => (
                          <Badge key={service} variant="outline">{service}</Badge>
                        ))}
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Responsável</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Avatar name={selectedOpportunity.assignedTo} size="md" />
                        <p className="text-text-primary">{selectedOpportunity.assignedTo}</p>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Target className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Origem</span>
                      </div>
                      <Badge variant="info">{sourceLabels[selectedOpportunity.source]}</Badge>
                    </div>
                  </div>

                  {selectedOpportunity.notes && (
                    <div className="col-span-2 p-4 rounded-lg bg-warning/5 border border-warning/20">
                      <div className="flex items-center gap-2 mb-2">
                        <MessageSquare className="w-4 h-4 text-warning" />
                        <span className="text-sm font-medium text-warning">Observações</span>
                      </div>
                      <p className="text-text-primary">{selectedOpportunity.notes}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Activities Tab */}
              {detailTab === 'activities' && (
                <div className="space-y-4">
                  {selectedOpportunity.activities.map((activity, index) => (
                    <div key={activity.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          activity.outcome === 'positive' ? 'bg-success/10 text-success' :
                          activity.outcome === 'negative' ? 'bg-danger/10 text-danger' :
                          'bg-bg-tertiary text-text-muted'
                        }`}>
                          {activity.type === 'call' && <Phone className="w-5 h-5" />}
                          {activity.type === 'email' && <Mail className="w-5 h-5" />}
                          {activity.type === 'meeting' && <Users className="w-5 h-5" />}
                          {activity.type === 'note' && <MessageSquare className="w-5 h-5" />}
                          {activity.type === 'stage_change' && <ArrowRight className="w-5 h-5" />}
                          {activity.type === 'proposal_sent' && <FileText className="w-5 h-5" />}
                          {activity.type === 'task' && <CheckCircle2 className="w-5 h-5" />}
                        </div>
                        {index < selectedOpportunity.activities.length - 1 && (
                          <div className="w-px flex-1 bg-border-default my-2" />
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-text-primary">{activity.title}</h4>
                          <span className="text-xs text-text-muted">
                            {new Date(activity.createdAt).toLocaleDateString('pt-BR', {
                              day: '2-digit',
                              month: 'short',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        </div>
                        <p className="text-sm text-text-secondary mt-1">{activity.description}</p>
                        <p className="text-xs text-text-muted mt-2">por {activity.createdBy}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Tasks Tab */}
              {detailTab === 'tasks' && (
                <div className="space-y-4">
                  {selectedOpportunity.tasks.map((task) => (
                    <div
                      key={task.id}
                      className={`flex items-center gap-4 p-4 rounded-lg ${
                        task.completed ? 'bg-success/5 border border-success/20' : 'bg-bg-tertiary'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                        task.completed ? 'border-success bg-success' : 'border-border-default'
                      }`}>
                        {task.completed && <CheckCircle2 className="w-4 h-4 text-white" />}
                      </div>
                      <div className="flex-1">
                        <p className={`font-medium ${task.completed ? 'text-text-muted line-through' : 'text-text-primary'}`}>
                          {task.title}
                        </p>
                        <p className="text-sm text-text-secondary">
                          {task.assignedTo} • Vence em {new Date(task.dueDate).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                  ))}

                  {selectedOpportunity.tasks.length === 0 && (
                    <div className="text-center py-8 text-text-muted">
                      Nenhuma tarefa cadastrada
                    </div>
                  )}

                  <Button variant="outline" className="w-full" leftIcon={<Plus className="w-4 h-4" />}>
                    Adicionar Tarefa
                  </Button>
                </div>
              )}

              {/* History Tab */}
              {detailTab === 'history' && (
                <div className="space-y-4">
                  {selectedOpportunity.stageHistory.map((history, index) => {
                    const stage = stages.find((s) => s.id === history.stage);
                    return (
                      <div key={index} className="flex items-center gap-4 p-4 rounded-lg bg-bg-tertiary">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: stage?.color }}
                        />
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{stage?.label}</p>
                          <p className="text-sm text-text-secondary">
                            {new Date(history.date).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                        {history.days > 0 && (
                          <Badge variant="neutral">{history.days} dias</Badge>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-border-default">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" leftIcon={<Phone className="w-4 h-4" />}>
                    Ligar
                  </Button>
                  <Button variant="ghost" leftIcon={<Mail className="w-4 h-4" />}>
                    Email
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" leftIcon={<Edit className="w-4 h-4" />}>
                    Editar
                  </Button>
                  <Button variant="primary" leftIcon={<ArrowRight className="w-4 h-4" />}>
                    Avançar Etapa
                  </Button>
                </div>
              </div>
            </div>
          )}
        </Modal>

        {/* New Opportunity Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Nova Oportunidade"
          size="lg"
        >
          <div className="space-y-6">
            <Input label="Título" placeholder="Ex: Segurança 24h - Cliente" required />

            <div className="grid grid-cols-2 gap-4">
              <Input label="Cliente" placeholder="Nome do cliente" required />
              <Input label="CNPJ" placeholder="00.000.000/0001-00" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input label="Email" type="email" placeholder="email@cliente.com" />
              <Input label="Telefone" placeholder="(00) 00000-0000" />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Input
                label="Valor"
                placeholder="R$ 0,00"
                leftIcon={<DollarSign className="w-4 h-4" />}
              />
              <Select
                label="Recorrência"
                options={[
                  { value: 'one_time', label: 'Único' },
                  { value: 'monthly', label: 'Mensal' },
                  { value: 'yearly', label: 'Anual' },
                ]}
                value="yearly"
                onChange={() => {}}
              />
              <Input label="Meses de Contrato" type="number" placeholder="12" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Etapa"
                options={stages.slice(0, 4).map((s) => ({ value: s.id, label: s.label }))}
                value="prospecting"
                onChange={() => {}}
              />
              <Input
                label="Probabilidade"
                type="number"
                placeholder="20"
                rightIcon={<Percent className="w-4 h-4" />}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input label="Fechamento Previsto" type="date" />
              <Select
                label="Prioridade"
                options={[
                  { value: 'low', label: 'Baixa' },
                  { value: 'medium', label: 'Média' },
                  { value: 'high', label: 'Alta' },
                ]}
                value="medium"
                onChange={() => {}}
              />
            </div>

            <Select
              label="Responsável"
              options={assignees}
              value=""
              onChange={() => {}}
            />

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
                Criar Oportunidade
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
