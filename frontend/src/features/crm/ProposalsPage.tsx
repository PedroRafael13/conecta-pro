'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  FileText,
  Download,
  Eye,
  Edit,
  Copy,
  Send,
  CheckCircle2,
  Clock,
  XCircle,
  AlertTriangle,
  Calendar,
  DollarSign,
  Building2,
  MoreHorizontal,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  BarChart3,
  PieChartIcon,
  Users,
  Settings,
  Trash2,
  Printer,
  Link,
  Mail,
  MessageSquare,
  History,
  RefreshCw,
  Briefcase,
  Target,
  Percent,
  Package,
  FileSignature,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  X,
  Sparkles,
  Zap,
  Award,
  ThumbsUp,
  ThumbsDown,
  Activity,
  Layout,
  Image,
  Type,
  List,
  Table,
  Grid3X3,
  Palette,
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
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
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
} from 'recharts';

// Types
interface ProposalItem {
  id: string;
  service: string;
  description: string;
  quantity: number;
  unit: string;
  unitPrice: number;
  total: number;
}

interface ProposalActivity {
  id: string;
  type: 'created' | 'sent' | 'viewed' | 'accepted' | 'rejected' | 'expired' | 'comment' | 'edited';
  title: string;
  description: string;
  createdAt: string;
  createdBy: string;
}

interface ProposalVersion {
  id: string;
  version: number;
  createdAt: string;
  createdBy: string;
  changes: string;
  value: number;
}

interface Proposal {
  id: string;
  number: string;
  title: string;
  client: string;
  clientCnpj: string;
  clientEmail: string;
  clientPhone: string;
  contactName: string;
  contactRole: string;
  opportunityId?: string;
  opportunityName?: string;
  value: number;
  discount: number;
  finalValue: number;
  status: 'draft' | 'sent' | 'viewed' | 'accepted' | 'rejected' | 'expired' | 'revision';
  validUntil: string;
  createdAt: string;
  sentAt: string | null;
  viewedAt: string | null;
  decidedAt: string | null;
  items: ProposalItem[];
  activities: ProposalActivity[];
  versions: ProposalVersion[];
  assignedTo: string;
  template: string;
  notes: string;
  paymentTerms: string;
  warranty: string;
  deliveryTime: string;
  rejectionReason?: string;
  viewCount: number;
  viewDuration: number; // seconds
  lastViewedPage: number;
}

// Mock Data - Comprehensive
const proposals: Proposal[] = [
  {
    id: '1',
    number: 'PROP-2026-0045',
    title: 'Segurança Patrimonial 24h',
    client: 'Condomínio Aurora',
    clientCnpj: '12.345.678/0001-90',
    clientEmail: 'sindico@aurora.com.br',
    clientPhone: '(11) 3333-4444',
    contactName: 'João Mendes',
    contactRole: 'Síndico',
    opportunityId: '1',
    opportunityName: 'Segurança 24h - Condomínio Aurora',
    value: 45000,
    discount: 2250,
    finalValue: 42750,
    status: 'sent',
    validUntil: '2026-02-15',
    createdAt: '2026-01-10',
    sentAt: '2026-01-11',
    viewedAt: null,
    decidedAt: null,
    items: [
      { id: '1', service: 'Vigilância Armada', description: 'Posto 24h com vigilante armado', quantity: 4, unit: 'Posto', unitPrice: 8500, total: 34000 },
      { id: '2', service: 'Monitoramento CFTV', description: 'Central de monitoramento 24h', quantity: 1, unit: 'Serviço', unitPrice: 6000, total: 6000 },
      { id: '3', service: 'Controle de Acesso', description: 'Gestão de entrada e saída', quantity: 1, unit: 'Serviço', unitPrice: 5000, total: 5000 },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Proposta criada', description: 'Proposta criada a partir da oportunidade', createdAt: '2026-01-10T10:00:00', createdBy: 'Ana Costa' },
      { id: '2', type: 'sent', title: 'Proposta enviada', description: 'Enviada por email para sindico@aurora.com.br', createdAt: '2026-01-11T14:30:00', createdBy: 'Ana Costa' },
    ],
    versions: [
      { id: '1', version: 1, createdAt: '2026-01-10T10:00:00', createdBy: 'Ana Costa', changes: 'Versão inicial', value: 45000 },
    ],
    assignedTo: 'Ana Costa',
    template: 'premium',
    notes: 'Cliente solicitou urgência. Preferência por contrato de 12 meses.',
    paymentTerms: 'Boleto bancário, vencimento dia 10',
    warranty: '12 meses de garantia nos serviços',
    deliveryTime: 'Início em 15 dias após aprovação',
    viewCount: 0,
    viewDuration: 0,
    lastViewedPage: 0,
  },
  {
    id: '2',
    number: 'PROP-2026-0044',
    title: 'Facilities Completo',
    client: 'Shopping Center Norte',
    clientCnpj: '23.456.789/0001-01',
    clientEmail: 'operacoes@scn.com.br',
    clientPhone: '(11) 2222-5555',
    contactName: 'Roberto Lima',
    contactRole: 'Gerente Operacional',
    opportunityId: '2',
    opportunityName: 'Facilities Completo - Shopping Center Norte',
    value: 128000,
    discount: 6400,
    finalValue: 121600,
    status: 'viewed',
    validUntil: '2026-02-20',
    createdAt: '2026-01-08',
    sentAt: '2026-01-09',
    viewedAt: '2026-01-14T09:15:00',
    decidedAt: null,
    items: [
      { id: '1', service: 'Limpeza Geral', description: 'Limpeza de áreas comuns e lojas', quantity: 20, unit: 'Funcionário', unitPrice: 3000, total: 60000 },
      { id: '2', service: 'Manutenção Predial', description: 'Equipe técnica residente', quantity: 4, unit: 'Técnico', unitPrice: 6000, total: 24000 },
      { id: '3', service: 'Segurança', description: 'Vigilância patrimonial', quantity: 8, unit: 'Posto', unitPrice: 5000, total: 40000 },
      { id: '4', service: 'Jardinagem', description: 'Manutenção de jardins', quantity: 2, unit: 'Jardineiro', unitPrice: 2000, total: 4000 },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Proposta criada', description: 'Proposta completa de facilities', createdAt: '2026-01-08T10:00:00', createdBy: 'Carlos Lima' },
      { id: '2', type: 'sent', title: 'Proposta enviada', description: 'Enviada por email', createdAt: '2026-01-09T11:00:00', createdBy: 'Carlos Lima' },
      { id: '3', type: 'viewed', title: 'Proposta visualizada', description: 'Cliente visualizou por 4min 32s', createdAt: '2026-01-14T09:15:00', createdBy: 'Sistema' },
    ],
    versions: [
      { id: '1', version: 1, createdAt: '2026-01-08T10:00:00', createdBy: 'Carlos Lima', changes: 'Versão inicial', value: 135000 },
      { id: '2', version: 2, createdAt: '2026-01-09T09:00:00', createdBy: 'Carlos Lima', changes: 'Ajuste de preços e desconto de 5%', value: 128000 },
    ],
    assignedTo: 'Carlos Lima',
    template: 'corporate',
    notes: 'Contrato atual vence em março. Grande oportunidade de expansão.',
    paymentTerms: 'Boleto bancário, vencimento dia 15',
    warranty: '24 meses de garantia',
    deliveryTime: 'Início imediato após aprovação',
    viewCount: 3,
    viewDuration: 272,
    lastViewedPage: 4,
  },
  {
    id: '3',
    number: 'PROP-2026-0043',
    title: 'Limpeza Hospitalar',
    client: 'Hospital São Lucas',
    clientCnpj: '34.567.890/0001-12',
    clientEmail: 'compras@hsl.com.br',
    clientPhone: '(21) 4444-7777',
    contactName: 'Dr. Fernando Melo',
    contactRole: 'Diretor Administrativo',
    value: 185000,
    discount: 9250,
    finalValue: 175750,
    status: 'accepted',
    validUntil: '2026-01-30',
    createdAt: '2026-01-05',
    sentAt: '2026-01-06',
    viewedAt: '2026-01-07T14:00:00',
    decidedAt: '2026-01-12T16:30:00',
    items: [
      { id: '1', service: 'Limpeza Hospitalar', description: 'Equipe especializada em ambiente hospitalar', quantity: 15, unit: 'Funcionário', unitPrice: 8000, total: 120000 },
      { id: '2', service: 'Desinfecção', description: 'Serviço de desinfecção de áreas críticas', quantity: 1, unit: 'Serviço', unitPrice: 35000, total: 35000 },
      { id: '3', service: 'Gerenciamento de Resíduos', description: 'Coleta e destinação de resíduos', quantity: 1, unit: 'Serviço', unitPrice: 30000, total: 30000 },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Proposta criada', description: 'Proposta especializada para ambiente hospitalar', createdAt: '2026-01-05T10:00:00', createdBy: 'Roberto Dias' },
      { id: '2', type: 'sent', title: 'Proposta enviada', description: 'Enviada por email', createdAt: '2026-01-06T09:00:00', createdBy: 'Roberto Dias' },
      { id: '3', type: 'viewed', title: 'Proposta visualizada', description: 'Cliente visualizou a proposta', createdAt: '2026-01-07T14:00:00', createdBy: 'Sistema' },
      { id: '4', type: 'accepted', title: 'Proposta aceita!', description: 'Cliente aceitou a proposta. Contrato CONT-2026-0003 gerado.', createdAt: '2026-01-12T16:30:00', createdBy: 'Sistema' },
    ],
    versions: [
      { id: '1', version: 1, createdAt: '2026-01-05T10:00:00', createdBy: 'Roberto Dias', changes: 'Versão inicial', value: 185000 },
    ],
    assignedTo: 'Roberto Dias',
    template: 'healthcare',
    notes: 'Cliente exigente com certificações. Verificar ISO 14001.',
    paymentTerms: 'Boleto bancário, vencimento dia 5',
    warranty: '12 meses',
    deliveryTime: 'Início em 30 dias',
    viewCount: 5,
    viewDuration: 720,
    lastViewedPage: 8,
  },
  {
    id: '4',
    number: 'PROP-2026-0042',
    title: 'Portaria Eletrônica',
    client: 'Condomínio Vida Nova',
    clientCnpj: '45.678.901/0001-23',
    clientEmail: 'sindico@vidanova.com.br',
    clientPhone: '(11) 5555-6666',
    contactName: 'Maria Santos',
    contactRole: 'Síndica',
    value: 12000,
    discount: 0,
    finalValue: 12000,
    status: 'rejected',
    validUntil: '2026-01-20',
    createdAt: '2026-01-02',
    sentAt: '2026-01-03',
    viewedAt: '2026-01-10T10:00:00',
    decidedAt: '2026-01-15T11:00:00',
    items: [
      { id: '1', service: 'Portaria Remota', description: 'Sistema de portaria eletrônica', quantity: 1, unit: 'Sistema', unitPrice: 8000, total: 8000 },
      { id: '2', service: 'Monitoramento 24h', description: 'Central de monitoramento', quantity: 1, unit: 'Serviço', unitPrice: 4000, total: 4000 },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Proposta criada', description: 'Proposta de portaria remota', createdAt: '2026-01-02T10:00:00', createdBy: 'Ana Costa' },
      { id: '2', type: 'sent', title: 'Proposta enviada', description: 'Enviada por email', createdAt: '2026-01-03T09:00:00', createdBy: 'Ana Costa' },
      { id: '3', type: 'viewed', title: 'Proposta visualizada', description: 'Cliente visualizou', createdAt: '2026-01-10T10:00:00', createdBy: 'Sistema' },
      { id: '4', type: 'rejected', title: 'Proposta recusada', description: 'Cliente optou por manter porteiro físico', createdAt: '2026-01-15T11:00:00', createdBy: 'Sistema' },
    ],
    versions: [
      { id: '1', version: 1, createdAt: '2026-01-02T10:00:00', createdBy: 'Ana Costa', changes: 'Versão inicial', value: 12000 },
    ],
    assignedTo: 'Ana Costa',
    template: 'standard',
    notes: '',
    paymentTerms: 'Boleto bancário',
    warranty: '12 meses',
    deliveryTime: 'Início em 15 dias',
    rejectionReason: 'Cliente preferiu manter porteiro físico por questões de segurança dos moradores idosos.',
    viewCount: 2,
    viewDuration: 180,
    lastViewedPage: 3,
  },
  {
    id: '5',
    number: 'PROP-2026-0041',
    title: 'Manutenção Predial',
    client: 'Edifício Corporate Tower',
    clientCnpj: '56.789.012/0001-34',
    clientEmail: 'facilities@corporate.com.br',
    clientPhone: '(11) 7777-8888',
    contactName: 'Eduardo Ramos',
    contactRole: 'Gerente de Facilities',
    value: 67000,
    discount: 0,
    finalValue: 67000,
    status: 'draft',
    validUntil: '2026-02-28',
    createdAt: '2026-01-15',
    sentAt: null,
    viewedAt: null,
    decidedAt: null,
    items: [
      { id: '1', service: 'Manutenção Elétrica', description: 'Equipe de eletricistas', quantity: 2, unit: 'Técnico', unitPrice: 15000, total: 30000 },
      { id: '2', service: 'Manutenção Hidráulica', description: 'Equipe de encanadores', quantity: 2, unit: 'Técnico', unitPrice: 12000, total: 24000 },
      { id: '3', service: 'Ar Condicionado', description: 'Manutenção preventiva', quantity: 1, unit: 'Serviço', unitPrice: 13000, total: 13000 },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Proposta criada', description: 'Rascunho de proposta', createdAt: '2026-01-15T10:00:00', createdBy: 'Carlos Lima' },
    ],
    versions: [
      { id: '1', version: 1, createdAt: '2026-01-15T10:00:00', createdBy: 'Carlos Lima', changes: 'Versão inicial', value: 67000 },
    ],
    assignedTo: 'Carlos Lima',
    template: 'corporate',
    notes: 'Aguardando aprovação do gerente para envio.',
    paymentTerms: 'Boleto bancário',
    warranty: '12 meses',
    deliveryTime: 'Início em 15 dias',
    viewCount: 0,
    viewDuration: 0,
    lastViewedPage: 0,
  },
  {
    id: '6',
    number: 'PROP-2026-0040',
    title: 'Segurança Bancária Premium',
    client: 'Banco Regional',
    clientCnpj: '67.890.123/0001-45',
    clientEmail: 'seguranca@bancoregional.com.br',
    clientPhone: '(11) 8888-9999',
    contactName: 'André Machado',
    contactRole: 'Gerente de Segurança',
    opportunityId: '6',
    opportunityName: 'Segurança Bancária - Banco Regional',
    value: 220000,
    discount: 11000,
    finalValue: 209000,
    status: 'revision',
    validUntil: '2026-02-25',
    createdAt: '2026-01-12',
    sentAt: '2026-01-13',
    viewedAt: '2026-01-14T16:00:00',
    decidedAt: null,
    items: [
      { id: '1', service: 'Vigilância Armada', description: 'Segurança de agências', quantity: 15, unit: 'Posto', unitPrice: 9000, total: 135000 },
      { id: '2', service: 'Escolta de Valores', description: 'Transporte de numerário', quantity: 5, unit: 'Veículo', unitPrice: 12000, total: 60000 },
      { id: '3', service: 'Monitoramento 24h', description: 'Central de monitoramento', quantity: 1, unit: 'Serviço', unitPrice: 25000, total: 25000 },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Proposta criada', description: 'Proposta premium para banco', createdAt: '2026-01-12T10:00:00', createdBy: 'Roberto Dias' },
      { id: '2', type: 'sent', title: 'Proposta enviada', description: 'Enviada por email', createdAt: '2026-01-13T09:00:00', createdBy: 'Roberto Dias' },
      { id: '3', type: 'viewed', title: 'Proposta visualizada', description: 'Cliente analisou proposta', createdAt: '2026-01-14T16:00:00', createdBy: 'Sistema' },
      { id: '4', type: 'comment', title: 'Solicitação de revisão', description: 'Cliente solicitou revisão de valores da escolta', createdAt: '2026-01-15T10:00:00', createdBy: 'André Machado' },
    ],
    versions: [
      { id: '1', version: 1, createdAt: '2026-01-12T10:00:00', createdBy: 'Roberto Dias', changes: 'Versão inicial', value: 230000 },
      { id: '2', version: 2, createdAt: '2026-01-13T08:00:00', createdBy: 'Roberto Dias', changes: 'Ajuste de desconto de 5%', value: 220000 },
    ],
    assignedTo: 'Roberto Dias',
    template: 'premium',
    notes: 'Cliente VIP. Prioridade máxima.',
    paymentTerms: 'Boleto bancário, vencimento dia 1',
    warranty: '24 meses',
    deliveryTime: 'Início imediato',
    viewCount: 4,
    viewDuration: 540,
    lastViewedPage: 6,
  },
  {
    id: '7',
    number: 'PROP-2025-0198',
    title: 'Segurança de Eventos',
    client: 'Centro de Convenções',
    clientCnpj: '78.901.234/0001-56',
    clientEmail: 'eventos@cc.com.br',
    clientPhone: '(11) 9999-0000',
    contactName: 'Paulo César',
    contactRole: 'Gerente de Eventos',
    value: 35000,
    discount: 0,
    finalValue: 35000,
    status: 'expired',
    validUntil: '2025-12-31',
    createdAt: '2025-12-15',
    sentAt: '2025-12-16',
    viewedAt: '2025-12-20T10:00:00',
    decidedAt: null,
    items: [
      { id: '1', service: 'Segurança de Eventos', description: 'Equipe para eventos', quantity: 10, unit: 'Segurança', unitPrice: 2500, total: 25000 },
      { id: '2', service: 'Brigadistas', description: 'Equipe de brigada de incêndio', quantity: 5, unit: 'Brigadista', unitPrice: 2000, total: 10000 },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Proposta criada', description: 'Proposta para eventos', createdAt: '2025-12-15T10:00:00', createdBy: 'Roberto Dias' },
      { id: '2', type: 'sent', title: 'Proposta enviada', description: 'Enviada por email', createdAt: '2025-12-16T09:00:00', createdBy: 'Roberto Dias' },
      { id: '3', type: 'viewed', title: 'Proposta visualizada', description: 'Cliente visualizou', createdAt: '2025-12-20T10:00:00', createdBy: 'Sistema' },
      { id: '4', type: 'expired', title: 'Proposta expirada', description: 'Validade encerrada sem resposta', createdAt: '2026-01-01T00:00:00', createdBy: 'Sistema' },
    ],
    versions: [
      { id: '1', version: 1, createdAt: '2025-12-15T10:00:00', createdBy: 'Roberto Dias', changes: 'Versão inicial', value: 35000 },
    ],
    assignedTo: 'Roberto Dias',
    template: 'standard',
    notes: '',
    paymentTerms: 'Boleto bancário',
    warranty: '3 meses',
    deliveryTime: 'Conforme evento',
    viewCount: 1,
    viewDuration: 120,
    lastViewedPage: 2,
  },
];

const statusConfig = {
  draft: { label: 'Rascunho', color: 'neutral' as const, icon: FileText },
  sent: { label: 'Enviada', color: 'info' as const, icon: Send },
  viewed: { label: 'Visualizada', color: 'warning' as const, icon: Eye },
  accepted: { label: 'Aceita', color: 'success' as const, icon: CheckCircle2 },
  rejected: { label: 'Recusada', color: 'danger' as const, icon: XCircle },
  expired: { label: 'Expirada', color: 'neutral' as const, icon: Clock },
  revision: { label: 'Em Revisão', color: 'warning' as const, icon: RefreshCw },
};

const templateConfig = {
  standard: { label: 'Padrão', color: 'neutral' as const },
  premium: { label: 'Premium', color: 'primary' as const },
  corporate: { label: 'Corporativo', color: 'info' as const },
  healthcare: { label: 'Saúde', color: 'success' as const },
};

// Chart data
const conversionFunnel = [
  { stage: 'Enviadas', count: 25, value: 1200000 },
  { stage: 'Visualizadas', count: 20, value: 980000 },
  { stage: 'Em Negociação', count: 8, value: 450000 },
  { stage: 'Aceitas', count: 5, value: 320000 },
];

const monthlyProposals = [
  { month: 'Ago', enviadas: 12, aceitas: 4, valor: 380000 },
  { month: 'Set', enviadas: 15, aceitas: 6, valor: 520000 },
  { month: 'Out', enviadas: 18, aceitas: 5, valor: 410000 },
  { month: 'Nov', enviadas: 14, aceitas: 7, valor: 680000 },
  { month: 'Dez', enviadas: 10, aceitas: 4, valor: 350000 },
  { month: 'Jan', enviadas: 8, aceitas: 2, valor: 220000 },
];

const proposalsByService = [
  { name: 'Segurança', value: 35, color: '#6366f1' },
  { name: 'Limpeza', value: 28, color: '#10b981' },
  { name: 'Manutenção', value: 20, color: '#f59e0b' },
  { name: 'Facilities', value: 12, color: '#3b82f6' },
  { name: 'Outros', value: 5, color: '#8b5cf6' },
];

export function ProposalsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [mainTab, setMainTab] = useState('proposals');
  const [showNewModal, setShowNewModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [detailTab, setDetailTab] = useState('overview');
  const [filterAssignee, setFilterAssignee] = useState('');

  // Filtered proposals
  const filteredProposals = useMemo(() => {
    return proposals.filter((proposal) => {
      const matchesSearch =
        proposal.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        proposal.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
        proposal.title.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTab = selectedTab === 'all' || proposal.status === selectedTab;
      const matchesAssignee = !filterAssignee || proposal.assignedTo === filterAssignee;
      return matchesSearch && matchesTab && matchesAssignee;
    });
  }, [proposals, searchTerm, selectedTab, filterAssignee]);

  // Stats
  const stats = useMemo(() => {
    const totalProposals = proposals.length;
    const draftCount = proposals.filter((p) => p.status === 'draft').length;
    const sentCount = proposals.filter((p) => ['sent', 'viewed', 'revision'].includes(p.status)).length;
    const acceptedCount = proposals.filter((p) => p.status === 'accepted').length;
    const rejectedCount = proposals.filter((p) => p.status === 'rejected').length;
    const expiredCount = proposals.filter((p) => p.status === 'expired').length;

    const totalValue = proposals.reduce((acc, p) => acc + p.finalValue, 0);
    const acceptedValue = proposals
      .filter((p) => p.status === 'accepted')
      .reduce((acc, p) => acc + p.finalValue, 0);
    const pendingValue = proposals
      .filter((p) => ['sent', 'viewed', 'revision'].includes(p.status))
      .reduce((acc, p) => acc + p.finalValue, 0);

    const closedDeals = proposals.filter((p) => ['accepted', 'rejected'].includes(p.status));
    const conversionRate = closedDeals.length > 0
      ? Math.round((acceptedCount / closedDeals.length) * 100)
      : 0;

    const avgDealSize = acceptedCount > 0 ? acceptedValue / acceptedCount : 0;

    // Average view duration
    const viewedProposals = proposals.filter((p) => p.viewDuration > 0);
    const avgViewDuration = viewedProposals.length > 0
      ? Math.round(viewedProposals.reduce((acc, p) => acc + p.viewDuration, 0) / viewedProposals.length / 60)
      : 0;

    return {
      totalProposals,
      draftCount,
      sentCount,
      acceptedCount,
      rejectedCount,
      expiredCount,
      totalValue,
      acceptedValue,
      pendingValue,
      conversionRate,
      avgDealSize,
      avgViewDuration,
    };
  }, []);

  // Unique assignees
  const assignees = useMemo(() => {
    const unique = [...new Set(proposals.map((p) => p.assignedTo))];
    return unique.map((name) => ({ value: name, label: name }));
  }, []);

  // Open detail modal
  const openDetail = (proposal: Proposal) => {
    setSelectedProposal(proposal);
    setDetailTab('overview');
    setShowDetailModal(true);
  };

  // Table columns
  const columns: Column<Proposal>[] = [
    {
      key: 'number',
      header: 'Proposta',
      render: (row) => (
        <div>
          <p className="font-mono text-sm font-medium text-accent-primary">{row.number}</p>
          <p className="text-xs text-text-muted line-clamp-1">{row.title}</p>
        </div>
      ),
    },
    {
      key: 'client',
      header: 'Cliente',
      render: (row) => (
        <div className="flex items-center gap-3">
          <Avatar name={row.client} size="sm" />
          <div>
            <span className="font-medium">{row.client}</span>
            <p className="text-xs text-text-muted">{row.contactName}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'value',
      header: 'Valor',
      sortable: true,
      render: (row) => (
        <div>
          <span className="font-mono text-text-primary">
            {row.finalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </span>
          {row.discount > 0 && (
            <p className="text-xs text-success">-{((row.discount / row.value) * 100).toFixed(0)}% desconto</p>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => {
        const config = statusConfig[row.status];
        return (
          <Badge variant={config.color} leftIcon={<config.icon className="w-3 h-3" />}>
            {config.label}
          </Badge>
        );
      },
    },
    {
      key: 'template',
      header: 'Template',
      render: (row) => {
        const config = templateConfig[row.template as keyof typeof templateConfig];
        return <Badge variant={config.color} size="sm">{config.label}</Badge>;
      },
    },
    {
      key: 'validUntil',
      header: 'Validade',
      render: (row) => {
        const isExpired = new Date(row.validUntil) < new Date();
        const isExpiring = new Date(row.validUntil) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        return (
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-text-muted" />
            <span className={`text-sm ${isExpired ? 'text-danger' : isExpiring ? 'text-warning' : 'text-text-secondary'}`}>
              {new Date(row.validUntil).toLocaleDateString('pt-BR')}
            </span>
          </div>
        );
      },
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
      key: 'viewCount',
      header: 'Visualizações',
      render: (row) => (
        row.viewCount > 0 ? (
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-text-muted" />
            <span className="text-sm">{row.viewCount}x</span>
          </div>
        ) : (
          <span className="text-text-muted">-</span>
        )
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            title="Visualizar"
            onClick={(e) => {
              e.stopPropagation();
              openDetail(row);
            }}
          >
            <Eye className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon-sm" title="Editar">
            <Edit className="w-4 h-4" />
          </Button>
          {row.status === 'draft' && (
            <Button variant="ghost" size="icon-sm" title="Enviar">
              <Send className="w-4 h-4" />
            </Button>
          )}
          <Button variant="ghost" size="icon-sm" title="Download PDF">
            <Download className="w-4 h-4" />
          </Button>
        </div>
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
              Propostas Comerciais
            </h1>
            <p className="text-text-secondary mt-1">
              Crie, envie e acompanhe propostas para seus clientes
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
              Nova Proposta
            </Button>
          </div>
        </div>

        {/* Main Tabs */}
        <SimpleTabBar
          tabs={[
            { value: 'proposals', label: 'Propostas', icon: <FileText className="w-4 h-4" /> },
            { value: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
            { value: 'templates', label: 'Templates', icon: <Layout className="w-4 h-4" /> },
          ]}
          value={mainTab}
          onChange={setMainTab}
        />

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Propostas"
              value={stats.totalProposals}
              change={15}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Aguardando Resposta"
              value={stats.sentCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Valor Aceito"
              value={stats.acceptedValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              change={22}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Valor Pendente"
              value={stats.pendingValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Target className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Taxa de Conversão"
              value={`${stats.conversionRate}%`}
              change={5}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="secondary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <StatCard
              title="Tempo Médio Leitura"
              value={`${stats.avgViewDuration} min`}
              icon={<Eye className="w-6 h-6" />}
              iconColor="neutral"
            />
          </motion.div>
        </div>

        {/* Proposals Tab */}
        {mainTab === 'proposals' && (
          <>
            {/* Filters */}
            <Card>
              <CardBody className="py-4">
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <SimpleTabBar
                    tabs={[
                      { value: 'all', label: `Todas (${proposals.length})` },
                      { value: 'draft', label: `Rascunhos (${stats.draftCount})` },
                      { value: 'sent', label: `Enviadas (${proposals.filter((p) => p.status === 'sent').length})` },
                      { value: 'viewed', label: `Visualizadas (${proposals.filter((p) => p.status === 'viewed').length})` },
                      { value: 'accepted', label: `Aceitas (${stats.acceptedCount})` },
                      { value: 'rejected', label: `Recusadas (${stats.rejectedCount})` },
                    ]}
                    value={selectedTab}
                    onChange={setSelectedTab}
                    variant="pills"
                  />
                  <div className="flex items-center gap-3">
                    <Input
                      placeholder="Buscar propostas..."
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
                    <Button variant="outline" leftIcon={<Filter className="w-4 h-4" />}>
                      Filtros
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Proposals Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card>
                <CardBody className="p-0">
                  <DataTable
                    columns={columns}
                    data={filteredProposals}
                    keyExtractor={(row) => row.id}
                    onRowClick={openDetail}
                  />
                </CardBody>
              </Card>
            </motion.div>

            {/* Expiring Alert */}
            {proposals.filter((p) => {
              const daysLeft = Math.ceil((new Date(p.validUntil).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
              return ['sent', 'viewed'].includes(p.status) && daysLeft <= 7 && daysLeft > 0;
            }).length > 0 && (
              <Card className="border-warning/30 bg-warning/5">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-warning/10">
                      <AlertTriangle className="w-6 h-6 text-warning" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-text-primary">
                        {proposals.filter((p) => {
                          const daysLeft = Math.ceil((new Date(p.validUntil).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
                          return ['sent', 'viewed'].includes(p.status) && daysLeft <= 7 && daysLeft > 0;
                        }).length} proposta(s) expirando em até 7 dias
                      </p>
                      <p className="text-sm text-text-secondary mt-1">
                        Entre em contato com os clientes para acelerar a decisão
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      Ver Propostas
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
            {/* Conversion Funnel */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Funil de Conversão</h3>
                    <p className="text-sm text-text-secondary">Jornada das propostas</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {conversionFunnel.map((stage, index) => {
                    const maxCount = Math.max(...conversionFunnel.map((s) => s.count));
                    const width = (stage.count / maxCount) * 100;
                    return (
                      <div key={stage.stage} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-text-primary">{stage.stage}</span>
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
                            className="h-full rounded-lg bg-gradient-to-r from-accent-primary to-accent-secondary"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>

            {/* Monthly Trend */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Tendência Mensal</h3>
                    <p className="text-sm text-text-secondary">Propostas enviadas vs aceitas</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={monthlyProposals}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Bar dataKey="enviadas" name="Enviadas" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="aceitas" name="Aceitas" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>

            {/* By Service */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Propostas por Serviço</h3>
                    <p className="text-sm text-text-secondary">Distribuição percentual</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="flex items-center gap-6">
                  <div className="w-48 h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={proposalsByService}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          dataKey="value"
                        >
                          {proposalsByService.map((entry, index) => (
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
                    {proposalsByService.map((service) => (
                      <div key={service.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: service.color }} />
                          <span className="text-sm text-text-secondary">{service.name}</span>
                        </div>
                        <span className="text-sm font-medium text-text-primary">{service.value}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Performance by Assignee */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Performance por Vendedor</h3>
                    <p className="text-sm text-text-secondary">Taxa de conversão individual</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {assignees.map((assignee) => {
                    const assigneeProposals = proposals.filter((p) => p.assignedTo === assignee.value);
                    const accepted = assigneeProposals.filter((p) => p.status === 'accepted').length;
                    const total = assigneeProposals.filter((p) => !['draft', 'expired'].includes(p.status)).length;
                    const rate = total > 0 ? Math.round((accepted / total) * 100) : 0;
                    const value = assigneeProposals
                      .filter((p) => p.status === 'accepted')
                      .reduce((acc, p) => acc + p.finalValue, 0);

                    return (
                      <div key={assignee.value} className="flex items-center gap-4 p-3 rounded-lg bg-bg-tertiary">
                        <Avatar name={assignee.value} size="md" />
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{assignee.value}</p>
                          <p className="text-xs text-text-muted">
                            {assigneeProposals.length} propostas • {accepted} aceitas
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-text-primary">
                            {value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                          <Badge variant={rate >= 50 ? 'success' : rate >= 30 ? 'warning' : 'danger'} size="sm">
                            {rate}% conversão
                          </Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Templates Tab */}
        {mainTab === 'templates' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(templateConfig).map(([key, config]) => (
              <Card key={key} className="group hover:border-accent-primary/50 transition-colors cursor-pointer">
                <CardBody className="p-6">
                  <div className="aspect-[4/3] rounded-lg bg-bg-tertiary mb-4 flex items-center justify-center">
                    <FileText className="w-12 h-12 text-text-muted" />
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-text-primary">{config.label}</h3>
                    <Badge variant={config.color} size="sm">Template</Badge>
                  </div>
                  <p className="text-sm text-text-secondary mb-4">
                    {key === 'standard' && 'Template básico para propostas simples'}
                    {key === 'premium' && 'Design premium para clientes VIP'}
                    {key === 'corporate' && 'Layout corporativo profissional'}
                    {key === 'healthcare' && 'Especializado para área de saúde'}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Eye className="w-4 h-4 mr-2" />
                      Preview
                    </Button>
                    <Button variant="primary" size="sm" className="flex-1">
                      <Plus className="w-4 h-4 mr-2" />
                      Usar
                    </Button>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedProposal?.number || 'Detalhes'}
          size="xl"
        >
          {selectedProposal && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-accent-primary/10">
                    <FileText className="w-8 h-8 text-accent-primary" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedProposal.title}</h3>
                    <p className="text-sm text-text-secondary">{selectedProposal.client}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={statusConfig[selectedProposal.status].color}>
                        {statusConfig[selectedProposal.status].label}
                      </Badge>
                      <Badge variant={templateConfig[selectedProposal.template as keyof typeof templateConfig].color}>
                        {templateConfig[selectedProposal.template as keyof typeof templateConfig].label}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  {selectedProposal.discount > 0 ? (
                    <>
                      <p className="text-lg text-text-muted line-through">
                        {selectedProposal.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <p className="text-3xl font-bold text-accent-primary">
                        {selectedProposal.finalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </p>
                      <Badge variant="success" size="sm">
                        -{((selectedProposal.discount / selectedProposal.value) * 100).toFixed(0)}% desconto
                      </Badge>
                    </>
                  ) : (
                    <p className="text-3xl font-bold text-accent-primary">
                      {selectedProposal.finalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                  )}
                </div>
              </div>

              {/* Detail Tabs */}
              <SimpleTabBar
                tabs={[
                  { value: 'overview', label: 'Visão Geral', icon: <FileText className="w-4 h-4" /> },
                  { value: 'items', label: 'Itens', icon: <Package className="w-4 h-4" /> },
                  { value: 'activity', label: 'Atividade', icon: <Activity className="w-4 h-4" /> },
                  { value: 'versions', label: 'Versões', icon: <History className="w-4 h-4" /> },
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
                        <Building2 className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Cliente</span>
                      </div>
                      <p className="text-text-primary font-medium">{selectedProposal.client}</p>
                      <p className="text-sm text-text-muted">{selectedProposal.clientCnpj}</p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Contato</span>
                      </div>
                      <p className="text-text-primary">{selectedProposal.contactName}</p>
                      <p className="text-sm text-text-muted">{selectedProposal.contactRole}</p>
                      <div className="mt-2 space-y-1 text-sm text-text-secondary">
                        <p className="flex items-center gap-2">
                          <Mail className="w-4 h-4" />
                          {selectedProposal.clientEmail}
                        </p>
                      </div>
                    </div>

                    {selectedProposal.opportunityName && (
                      <div className="p-4 rounded-lg bg-bg-tertiary">
                        <div className="flex items-center gap-2 mb-3">
                          <Target className="w-4 h-4 text-text-muted" />
                          <span className="text-sm font-medium text-text-secondary">Oportunidade</span>
                        </div>
                        <p className="text-text-primary">{selectedProposal.opportunityName}</p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Calendar className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Datas</span>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-text-muted">Criada em:</span>
                          <span className="text-text-primary">{new Date(selectedProposal.createdAt).toLocaleDateString('pt-BR')}</span>
                        </div>
                        {selectedProposal.sentAt && (
                          <div className="flex justify-between">
                            <span className="text-text-muted">Enviada em:</span>
                            <span className="text-text-primary">{new Date(selectedProposal.sentAt).toLocaleDateString('pt-BR')}</span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span className="text-text-muted">Válida até:</span>
                          <span className="text-text-primary">{new Date(selectedProposal.validUntil).toLocaleDateString('pt-BR')}</span>
                        </div>
                      </div>
                    </div>

                    {selectedProposal.viewCount > 0 && (
                      <div className="p-4 rounded-lg bg-info/5 border border-info/20">
                        <div className="flex items-center gap-2 mb-3">
                          <Eye className="w-4 h-4 text-info" />
                          <span className="text-sm font-medium text-info">Engajamento</span>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-text-secondary">Visualizações:</span>
                            <span className="text-text-primary font-medium">{selectedProposal.viewCount}x</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-text-secondary">Tempo de leitura:</span>
                            <span className="text-text-primary font-medium">{Math.round(selectedProposal.viewDuration / 60)} min</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-text-secondary">Última página vista:</span>
                            <span className="text-text-primary font-medium">Página {selectedProposal.lastViewedPage}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Briefcase className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Responsável</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Avatar name={selectedProposal.assignedTo} size="md" />
                        <p className="text-text-primary">{selectedProposal.assignedTo}</p>
                      </div>
                    </div>
                  </div>

                  {selectedProposal.notes && (
                    <div className="col-span-2 p-4 rounded-lg bg-warning/5 border border-warning/20">
                      <div className="flex items-center gap-2 mb-2">
                        <MessageSquare className="w-4 h-4 text-warning" />
                        <span className="text-sm font-medium text-warning">Observações</span>
                      </div>
                      <p className="text-text-primary">{selectedProposal.notes}</p>
                    </div>
                  )}

                  {selectedProposal.rejectionReason && (
                    <div className="col-span-2 p-4 rounded-lg bg-danger/5 border border-danger/20">
                      <div className="flex items-center gap-2 mb-2">
                        <XCircle className="w-4 h-4 text-danger" />
                        <span className="text-sm font-medium text-danger">Motivo da Recusa</span>
                      </div>
                      <p className="text-text-primary">{selectedProposal.rejectionReason}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Items Tab */}
              {detailTab === 'items' && (
                <div className="space-y-4">
                  {selectedProposal.items.map((item) => (
                    <div key={item.id} className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-text-primary">{item.service}</h4>
                          <p className="text-sm text-text-secondary mt-1">{item.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono font-bold text-accent-primary">
                            {item.total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                          <p className="text-xs text-text-muted">
                            {item.quantity} {item.unit} x {item.unitPrice.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}

                  <div className="p-4 rounded-lg bg-accent-primary/10 border border-accent-primary/20">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-text-primary">Subtotal</span>
                      <span className="font-mono text-text-primary">
                        {selectedProposal.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                    </div>
                    {selectedProposal.discount > 0 && (
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-success">Desconto</span>
                        <span className="font-mono text-success">
                          -{selectedProposal.discount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-accent-primary/20">
                      <span className="font-bold text-text-primary">Total</span>
                      <span className="text-xl font-mono font-bold text-accent-primary">
                        {selectedProposal.finalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Activity Tab */}
              {detailTab === 'activity' && (
                <div className="space-y-4">
                  {selectedProposal.activities.map((activity, index) => (
                    <div key={activity.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          activity.type === 'accepted' ? 'bg-success/10 text-success' :
                          activity.type === 'rejected' ? 'bg-danger/10 text-danger' :
                          activity.type === 'viewed' ? 'bg-info/10 text-info' :
                          'bg-bg-tertiary text-text-muted'
                        }`}>
                          {activity.type === 'created' && <Plus className="w-5 h-5" />}
                          {activity.type === 'sent' && <Send className="w-5 h-5" />}
                          {activity.type === 'viewed' && <Eye className="w-5 h-5" />}
                          {activity.type === 'accepted' && <CheckCircle2 className="w-5 h-5" />}
                          {activity.type === 'rejected' && <XCircle className="w-5 h-5" />}
                          {activity.type === 'expired' && <Clock className="w-5 h-5" />}
                          {activity.type === 'comment' && <MessageSquare className="w-5 h-5" />}
                          {activity.type === 'edited' && <Edit className="w-5 h-5" />}
                        </div>
                        {index < selectedProposal.activities.length - 1 && (
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

              {/* Versions Tab */}
              {detailTab === 'versions' && (
                <div className="space-y-4">
                  {selectedProposal.versions.map((version) => (
                    <div key={version.id} className="flex items-center gap-4 p-4 rounded-lg bg-bg-tertiary">
                      <div className="w-12 h-12 rounded-full bg-accent-primary/10 flex items-center justify-center">
                        <span className="text-lg font-bold text-accent-primary">v{version.version}</span>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-text-primary">{version.changes}</p>
                        <p className="text-sm text-text-secondary">
                          {new Date(version.createdAt).toLocaleDateString('pt-BR')} • {version.createdBy}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-mono text-text-primary">
                          {version.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-border-default">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" leftIcon={<Download className="w-4 h-4" />}>
                    PDF
                  </Button>
                  <Button variant="ghost" leftIcon={<Printer className="w-4 h-4" />}>
                    Imprimir
                  </Button>
                  <Button variant="ghost" leftIcon={<Copy className="w-4 h-4" />}>
                    Duplicar
                  </Button>
                </div>
                <div className="flex items-center gap-2">
                  {selectedProposal.status === 'draft' && (
                    <>
                      <Button variant="outline" leftIcon={<Edit className="w-4 h-4" />}>
                        Editar
                      </Button>
                      <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                        Enviar
                      </Button>
                    </>
                  )}
                  {['sent', 'viewed', 'revision'].includes(selectedProposal.status) && (
                    <>
                      <Button variant="outline" leftIcon={<RefreshCw className="w-4 h-4" />}>
                        Nova Versão
                      </Button>
                      <Button variant="ghost" leftIcon={<Mail className="w-4 h-4" />}>
                        Reenviar
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </Modal>

        {/* New Proposal Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Nova Proposta"
          size="lg"
        >
          <div className="space-y-6">
            <Input label="Título da Proposta" placeholder="Ex: Segurança Patrimonial 24h" required />

            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Cliente"
                options={[
                  { value: '1', label: 'Condomínio Aurora' },
                  { value: '2', label: 'Shopping Center Norte' },
                  { value: '3', label: 'Hospital São Lucas' },
                  { value: '4', label: 'Tech Park' },
                ]}
                value=""
                onChange={() => {}}
              />
              <Select
                label="Oportunidade"
                options={[
                  { value: '1', label: 'Segurança 24h - Aurora' },
                  { value: '2', label: 'Facilities - SCN' },
                ]}
                value=""
                onChange={() => {}}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Input
                label="Valor Total"
                placeholder="R$ 0,00"
                leftIcon={<DollarSign className="w-4 h-4" />}
              />
              <Input
                label="Desconto (%)"
                placeholder="0"
                rightIcon={<Percent className="w-4 h-4" />}
              />
              <Input label="Validade" type="date" />
            </div>

            <Select
              label="Template"
              options={Object.entries(templateConfig).map(([key, config]) => ({
                value: key,
                label: config.label,
              }))}
              value="standard"
              onChange={() => {}}
            />

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
              <Button variant="outline" leftIcon={<FileText className="w-4 h-4" />}>
                Salvar Rascunho
              </Button>
              <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                Criar e Enviar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
