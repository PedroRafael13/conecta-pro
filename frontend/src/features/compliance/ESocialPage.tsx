'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  Modal,
  Select
} from '@/design-system/components';
import type { Column, SelectOption } from '@/design-system/components';
import {
  FileCheck,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Send,
  Users,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Play,
  RotateCcw,
  Upload,
  Calendar,
  Building2,
  User,
  Briefcase,
  AlertCircle,
  ChevronRight,
  ArrowUpRight,
  History,
  Settings,
  Database
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend,
  LineChart, Line, AreaChart, Area
} from 'recharts';

// Types
interface ESocialEvent {
  id: string;
  code: string;
  type: string;
  description: string;
  employeeId?: string;
  employeeName?: string;
  employeeCpf?: string;
  status: 'pending' | 'processing' | 'sent' | 'accepted' | 'rejected' | 'error';
  protocol?: string;
  receipt?: string;
  batchId?: string;
  errorMessage?: string;
  errorCode?: string;
  xmlContent?: string;
  sentAt?: string;
  processedAt?: string;
  createdAt: string;
  updatedAt: string;
}

interface EventBatch {
  id: string;
  name: string;
  type: 'periodic' | 'non_periodic' | 'table';
  period?: string;
  totalEvents: number;
  pending: number;
  sent: number;
  accepted: number;
  rejected: number;
  status: 'draft' | 'validating' | 'ready' | 'sending' | 'sent' | 'completed' | 'error';
  protocol?: string;
  sentAt?: string;
  createdAt: string;
}

interface ESocialEmployee {
  id: string;
  name: string;
  cpf: string;
  matricula: string;
  admissionDate: string;
  department: string;
  position: string;
  status: 'active' | 'on_leave' | 'terminated';
  eventsCount: number;
  lastEventDate?: string;
  pendingEvents: number;
  hasErrors: boolean;
}

interface EventError {
  id: string;
  eventId: string;
  eventCode: string;
  eventType: string;
  employeeName?: string;
  errorCode: string;
  errorMessage: string;
  severity: 'warning' | 'error' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'ignored';
  resolvedBy?: string;
  resolvedAt?: string;
  createdAt: string;
}

// Event types reference
const EVENT_TYPES: Record<string, { name: string; category: string }> = {
  'S-1000': { name: 'Informações do Empregador', category: 'table' },
  'S-1005': { name: 'Tabela de Estabelecimentos', category: 'table' },
  'S-1010': { name: 'Tabela de Rubricas', category: 'table' },
  'S-1020': { name: 'Tabela de Lotações Tributárias', category: 'table' },
  'S-1200': { name: 'Remuneração do Trabalhador', category: 'periodic' },
  'S-1210': { name: 'Pagamentos de Rendimentos', category: 'periodic' },
  'S-1299': { name: 'Fechamento dos Eventos Periódicos', category: 'periodic' },
  'S-2190': { name: 'Admissão Preliminar', category: 'non_periodic' },
  'S-2200': { name: 'Cadastramento Inicial/Admissão', category: 'non_periodic' },
  'S-2205': { name: 'Alteração de Dados Cadastrais', category: 'non_periodic' },
  'S-2206': { name: 'Alteração de Contrato', category: 'non_periodic' },
  'S-2210': { name: 'Comunicação de Acidente (CAT)', category: 'non_periodic' },
  'S-2220': { name: 'Monitoramento da Saúde', category: 'non_periodic' },
  'S-2230': { name: 'Afastamento Temporário', category: 'non_periodic' },
  'S-2240': { name: 'Condições Ambientais de Trabalho', category: 'non_periodic' },
  'S-2299': { name: 'Desligamento', category: 'non_periodic' },
  'S-2300': { name: 'Trabalhador Sem Vínculo', category: 'non_periodic' },
  'S-2399': { name: 'Término de TSVE', category: 'non_periodic' },
  'S-3000': { name: 'Exclusão de Eventos', category: 'non_periodic' }
};

// Mock Data
const mockEvents: ESocialEvent[] = [
  {
    id: '1',
    code: 'S-2200',
    type: 'Cadastramento Inicial/Admissão',
    description: 'Admissão de novo funcionário',
    employeeId: 'emp1',
    employeeName: 'Maria Silva Santos',
    employeeCpf: '123.456.789-00',
    status: 'pending',
    createdAt: '2024-01-15T10:00:00',
    updatedAt: '2024-01-15T10:00:00'
  },
  {
    id: '2',
    code: 'S-1200',
    type: 'Remuneração do Trabalhador',
    description: 'Folha de pagamento 01/2024',
    employeeId: 'emp2',
    employeeName: 'João Carlos Oliveira',
    employeeCpf: '987.654.321-00',
    status: 'sent',
    protocol: 'PROT2024011500001',
    sentAt: '2024-01-15T08:30:00',
    createdAt: '2024-01-14T16:00:00',
    updatedAt: '2024-01-15T08:30:00'
  },
  {
    id: '3',
    code: 'S-2299',
    type: 'Desligamento',
    description: 'Rescisão contratual',
    employeeId: 'emp3',
    employeeName: 'Ana Paula Costa',
    employeeCpf: '456.789.123-00',
    status: 'accepted',
    protocol: 'PROT2024011500002',
    receipt: 'REC2024011500002',
    sentAt: '2024-01-14T14:00:00',
    processedAt: '2024-01-14T14:05:00',
    createdAt: '2024-01-14T10:00:00',
    updatedAt: '2024-01-14T14:05:00'
  },
  {
    id: '4',
    code: 'S-2230',
    type: 'Afastamento Temporário',
    description: 'Licença médica - CID B34.2',
    employeeId: 'emp4',
    employeeName: 'Pedro Henrique Lima',
    employeeCpf: '321.654.987-00',
    status: 'rejected',
    protocol: 'PROT2024011500003',
    errorCode: 'ERR-401',
    errorMessage: 'Data de início do afastamento inválida',
    sentAt: '2024-01-15T09:00:00',
    processedAt: '2024-01-15T09:02:00',
    createdAt: '2024-01-15T08:00:00',
    updatedAt: '2024-01-15T09:02:00'
  },
  {
    id: '5',
    code: 'S-1010',
    type: 'Tabela de Rubricas',
    description: 'Atualização de rubrica salarial',
    status: 'processing',
    createdAt: '2024-01-15T11:00:00',
    updatedAt: '2024-01-15T11:00:00'
  },
  {
    id: '6',
    code: 'S-2210',
    type: 'Comunicação de Acidente (CAT)',
    description: 'Acidente de trabalho',
    employeeId: 'emp5',
    employeeName: 'Carlos Eduardo Souza',
    employeeCpf: '654.321.987-00',
    status: 'error',
    errorCode: 'ERR-500',
    errorMessage: 'Erro de comunicação com o servidor do eSocial',
    createdAt: '2024-01-15T07:30:00',
    updatedAt: '2024-01-15T07:35:00'
  }
];

const mockBatches: EventBatch[] = [
  {
    id: '1',
    name: 'Folha de Pagamento 01/2024',
    type: 'periodic',
    period: '01/2024',
    totalEvents: 856,
    pending: 0,
    sent: 856,
    accepted: 850,
    rejected: 6,
    status: 'completed',
    protocol: 'BATCH2024011500001',
    sentAt: '2024-01-10T06:00:00',
    createdAt: '2024-01-05T10:00:00'
  },
  {
    id: '2',
    name: 'Eventos Não Periódicos - Semana 3',
    type: 'non_periodic',
    totalEvents: 45,
    pending: 12,
    sent: 33,
    accepted: 30,
    rejected: 3,
    status: 'sending',
    createdAt: '2024-01-15T08:00:00'
  },
  {
    id: '3',
    name: 'Atualização de Tabelas',
    type: 'table',
    totalEvents: 15,
    pending: 15,
    sent: 0,
    accepted: 0,
    rejected: 0,
    status: 'ready',
    createdAt: '2024-01-15T09:00:00'
  },
  {
    id: '4',
    name: 'Folha de Pagamento 12/2023',
    type: 'periodic',
    period: '12/2023',
    totalEvents: 845,
    pending: 0,
    sent: 845,
    accepted: 845,
    rejected: 0,
    status: 'completed',
    protocol: 'BATCH2023120500001',
    sentAt: '2023-12-05T06:00:00',
    createdAt: '2023-12-01T10:00:00'
  }
];

const mockEmployees: ESocialEmployee[] = [
  {
    id: 'emp1',
    name: 'Maria Silva Santos',
    cpf: '123.456.789-00',
    matricula: 'MAT001',
    admissionDate: '2024-01-15',
    department: 'Administrativo',
    position: 'Analista Administrativo',
    status: 'active',
    eventsCount: 1,
    pendingEvents: 1,
    hasErrors: false
  },
  {
    id: 'emp2',
    name: 'João Carlos Oliveira',
    cpf: '987.654.321-00',
    matricula: 'MAT002',
    admissionDate: '2023-03-01',
    department: 'Financeiro',
    position: 'Contador',
    status: 'active',
    eventsCount: 24,
    lastEventDate: '2024-01-15',
    pendingEvents: 0,
    hasErrors: false
  },
  {
    id: 'emp3',
    name: 'Ana Paula Costa',
    cpf: '456.789.123-00',
    matricula: 'MAT003',
    admissionDate: '2022-06-15',
    department: 'RH',
    position: 'Assistente de RH',
    status: 'terminated',
    eventsCount: 36,
    lastEventDate: '2024-01-14',
    pendingEvents: 0,
    hasErrors: false
  },
  {
    id: 'emp4',
    name: 'Pedro Henrique Lima',
    cpf: '321.654.987-00',
    matricula: 'MAT004',
    admissionDate: '2023-08-01',
    department: 'Operações',
    position: 'Supervisor de Operações',
    status: 'on_leave',
    eventsCount: 12,
    lastEventDate: '2024-01-15',
    pendingEvents: 1,
    hasErrors: true
  },
  {
    id: 'emp5',
    name: 'Carlos Eduardo Souza',
    cpf: '654.321.987-00',
    matricula: 'MAT005',
    admissionDate: '2023-01-10',
    department: 'Produção',
    position: 'Operador de Máquinas',
    status: 'active',
    eventsCount: 18,
    lastEventDate: '2024-01-15',
    pendingEvents: 1,
    hasErrors: true
  }
];

const mockErrors: EventError[] = [
  {
    id: '1',
    eventId: '4',
    eventCode: 'S-2230',
    eventType: 'Afastamento Temporário',
    employeeName: 'Pedro Henrique Lima',
    errorCode: 'ERR-401',
    errorMessage: 'Data de início do afastamento inválida. A data informada é anterior à data de admissão do trabalhador.',
    severity: 'error',
    status: 'open',
    createdAt: '2024-01-15T09:02:00'
  },
  {
    id: '2',
    eventId: '6',
    eventCode: 'S-2210',
    eventType: 'Comunicação de Acidente (CAT)',
    employeeName: 'Carlos Eduardo Souza',
    errorCode: 'ERR-500',
    errorMessage: 'Erro de comunicação com o servidor do eSocial. Tente novamente mais tarde.',
    severity: 'critical',
    status: 'open',
    createdAt: '2024-01-15T07:35:00'
  },
  {
    id: '3',
    eventId: '10',
    eventCode: 'S-1200',
    eventType: 'Remuneração do Trabalhador',
    employeeName: 'Roberto Alves',
    errorCode: 'WARN-101',
    errorMessage: 'Valor de desconto INSS superior ao teto. Verificar cálculo.',
    severity: 'warning',
    status: 'resolved',
    resolvedBy: 'admin@empresa.com',
    resolvedAt: '2024-01-14T16:00:00',
    createdAt: '2024-01-14T10:00:00'
  }
];

// Chart colors
const CHART_COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];

export function ESocialPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<ESocialEvent | null>(null);
  const [selectedBatch, setSelectedBatch] = useState<EventBatch | null>(null);
  const [selectedEmployee, setSelectedEmployee] = useState<ESocialEmployee | null>(null);
  const [selectedError, setSelectedError] = useState<EventError | null>(null);
  const [showNewEventModal, setShowNewEventModal] = useState(false);
  const [showNewBatchModal, setShowNewBatchModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterEventCode, setFilterEventCode] = useState('all');
  const [newEventType, setNewEventType] = useState('');
  const [newEventEmployee, setNewEventEmployee] = useState('');
  const [newBatchType, setNewBatchType] = useState('periodic');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <FileCheck className="h-4 w-4" /> },
    { value: 'events', label: 'Eventos', icon: <FileText className="h-4 w-4" /> },
    { value: 'batches', label: 'Lotes', icon: <Database className="h-4 w-4" /> },
    { value: 'employees', label: 'Funcionários', icon: <Users className="h-4 w-4" /> },
    { value: 'errors', label: 'Erros', icon: <AlertTriangle className="h-4 w-4" /> }
  ];

  const eventStatusOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Status' },
    { value: 'pending', label: 'Pendente' },
    { value: 'processing', label: 'Processando' },
    { value: 'sent', label: 'Enviado' },
    { value: 'accepted', label: 'Aceito' },
    { value: 'rejected', label: 'Rejeitado' },
    { value: 'error', label: 'Com Erro' }
  ];

  const eventCodeOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Tipos' },
    ...Object.entries(EVENT_TYPES).map(([code, info]) => ({
      value: code,
      label: `${code} - ${info.name}`
    }))
  ];

  // Calculated stats
  const pendingEvents = mockEvents.filter(e => e.status === 'pending').length;
  const sentToday = mockEvents.filter(e => {
    const today = new Date().toDateString();
    return e.sentAt && new Date(e.sentAt).toDateString() === today;
  }).length;
  const errorEvents = mockEvents.filter(e => e.status === 'error' || e.status === 'rejected').length;
  const totalEmployees = mockEmployees.length;

  // Chart data
  const eventsByTypeData = [
    { name: 'Periódicos', value: mockEvents.filter(e => EVENT_TYPES[e.code]?.category === 'periodic').length },
    { name: 'Não Periódicos', value: mockEvents.filter(e => EVENT_TYPES[e.code]?.category === 'non_periodic').length },
    { name: 'Tabelas', value: mockEvents.filter(e => EVENT_TYPES[e.code]?.category === 'table').length }
  ];

  const eventStatusData = [
    { name: 'Aceitos', value: mockEvents.filter(e => e.status === 'accepted').length, color: '#10b981' },
    { name: 'Enviados', value: mockEvents.filter(e => e.status === 'sent').length, color: '#6366f1' },
    { name: 'Pendentes', value: mockEvents.filter(e => e.status === 'pending').length, color: '#f59e0b' },
    { name: 'Rejeitados', value: mockEvents.filter(e => e.status === 'rejected').length, color: '#ef4444' },
    { name: 'Com Erro', value: mockEvents.filter(e => e.status === 'error').length, color: '#dc2626' }
  ];

  const submissionTrendData = [
    { day: 'Seg', enviados: 120, aceitos: 118, rejeitados: 2 },
    { day: 'Ter', enviados: 85, aceitos: 82, rejeitados: 3 },
    { day: 'Qua', enviados: 156, aceitos: 150, rejeitados: 6 },
    { day: 'Qui', enviados: 234, aceitos: 230, rejeitados: 4 },
    { day: 'Sex', enviados: 189, aceitos: 185, rejeitados: 4 },
    { day: 'Sáb', enviados: 45, aceitos: 45, rejeitados: 0 },
    { day: 'Dom', enviados: 12, aceitos: 12, rejeitados: 0 }
  ];

  const monthlyEventsData = [
    { month: 'Set', eventos: 2456 },
    { month: 'Out', eventos: 2678 },
    { month: 'Nov', eventos: 2890 },
    { month: 'Dez', eventos: 3012 },
    { month: 'Jan', eventos: 2345 }
  ];

  // Format functions
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  const formatDateTime = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEventStatusBadge = (status: ESocialEvent['status']) => {
    const config = {
      pending: { variant: 'warning' as const, label: 'Pendente', icon: Clock },
      processing: { variant: 'info' as const, label: 'Processando', icon: RefreshCw },
      sent: { variant: 'primary' as const, label: 'Enviado', icon: Send },
      accepted: { variant: 'success' as const, label: 'Aceito', icon: CheckCircle },
      rejected: { variant: 'danger' as const, label: 'Rejeitado', icon: XCircle },
      error: { variant: 'danger' as const, label: 'Erro', icon: AlertTriangle }
    };
    const { variant, label, icon: Icon } = config[status];
    return (
      <Badge variant={variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {label}
      </Badge>
    );
  };

  const getBatchStatusBadge = (status: EventBatch['status']) => {
    const config = {
      draft: { variant: 'neutral' as const, label: 'Rascunho' },
      validating: { variant: 'info' as const, label: 'Validando' },
      ready: { variant: 'primary' as const, label: 'Pronto' },
      sending: { variant: 'warning' as const, label: 'Enviando' },
      sent: { variant: 'info' as const, label: 'Enviado' },
      completed: { variant: 'success' as const, label: 'Concluído' },
      error: { variant: 'danger' as const, label: 'Erro' }
    };
    const { variant, label } = config[status];
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getEmployeeStatusBadge = (status: ESocialEmployee['status']) => {
    const config = {
      active: { variant: 'success' as const, label: 'Ativo' },
      on_leave: { variant: 'warning' as const, label: 'Afastado' },
      terminated: { variant: 'neutral' as const, label: 'Desligado' }
    };
    const { variant, label } = config[status];
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getErrorSeverityBadge = (severity: EventError['severity']) => {
    const config = {
      warning: { variant: 'warning' as const, label: 'Aviso' },
      error: { variant: 'danger' as const, label: 'Erro' },
      critical: { variant: 'danger' as const, label: 'Crítico' }
    };
    const { variant, label } = config[severity];
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getErrorStatusBadge = (status: EventError['status']) => {
    const config = {
      open: { variant: 'danger' as const, label: 'Aberto' },
      in_progress: { variant: 'warning' as const, label: 'Em Análise' },
      resolved: { variant: 'success' as const, label: 'Resolvido' },
      ignored: { variant: 'neutral' as const, label: 'Ignorado' }
    };
    const { variant, label } = config[status];
    return <Badge variant={variant}>{label}</Badge>;
  };

  // Table columns
  const eventColumns: Column<ESocialEvent>[] = [
    {
      key: 'code',
      header: 'Evento',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.code}</p>
          <p className="text-sm text-text-secondary">{row.type}</p>
        </div>
      )
    },
    {
      key: 'employee',
      header: 'Funcionário',
      render: (row) => row.employeeName ? (
        <div>
          <p className="font-medium text-text-primary">{row.employeeName}</p>
          <p className="text-sm text-text-secondary">{row.employeeCpf}</p>
        </div>
      ) : (
        <span className="text-text-secondary">-</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getEventStatusBadge(row.status)
    },
    {
      key: 'protocol',
      header: 'Protocolo',
      render: (row) => (
        <span className="text-text-primary font-mono text-sm">
          {row.protocol || '-'}
        </span>
      )
    },
    {
      key: 'createdAt',
      header: 'Data',
      render: (row) => (
        <span className="text-text-secondary">
          {formatDateTime(row.createdAt)}
        </span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedEvent(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'pending' && (
            <Button variant="ghost" size="sm">
              <Send className="h-4 w-4" />
            </Button>
          )}
          {(row.status === 'error' || row.status === 'rejected') && (
            <Button variant="ghost" size="sm">
              <RotateCcw className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const batchColumns: Column<EventBatch>[] = [
    {
      key: 'name',
      header: 'Lote',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          {row.period && (
            <p className="text-sm text-text-secondary">Período: {row.period}</p>
          )}
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        <Badge variant="outline">
          {row.type === 'periodic' ? 'Periódico' : row.type === 'non_periodic' ? 'Não Periódico' : 'Tabelas'}
        </Badge>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getBatchStatusBadge(row.status)
    },
    {
      key: 'progress',
      header: 'Progresso',
      render: (row) => {
        const progress = row.totalEvents > 0
          ? Math.round(((row.accepted + row.rejected) / row.totalEvents) * 100)
          : 0;
        return (
          <div className="w-32">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-text-secondary">{row.accepted + row.rejected}/{row.totalEvents}</span>
              <span className="text-text-primary">{progress}%</span>
            </div>
            <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        );
      }
    },
    {
      key: 'metrics',
      header: 'Resultados',
      render: (row) => (
        <div className="flex items-center gap-3 text-sm">
          <span className="text-green-400" title="Aceitos">
            <CheckCircle className="h-3 w-3 inline mr-1" />
            {row.accepted}
          </span>
          <span className="text-red-400" title="Rejeitados">
            <XCircle className="h-3 w-3 inline mr-1" />
            {row.rejected}
          </span>
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedBatch(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'ready' && (
            <Button variant="ghost" size="sm">
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const employeeColumns: Column<ESocialEmployee>[] = [
    {
      key: 'employee',
      header: 'Funcionário',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
            <User className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <p className="font-medium text-text-primary">{row.name}</p>
              {row.hasErrors && (
                <AlertCircle className="h-4 w-4 text-red-400" />
              )}
            </div>
            <p className="text-sm text-text-secondary">{row.cpf}</p>
          </div>
        </div>
      )
    },
    {
      key: 'matricula',
      header: 'Matrícula',
      render: (row) => (
        <span className="text-text-primary font-mono">{row.matricula}</span>
      )
    },
    {
      key: 'status',
      header: 'Situação',
      render: (row) => getEmployeeStatusBadge(row.status)
    },
    {
      key: 'department',
      header: 'Departamento',
      render: (row) => (
        <span className="text-text-secondary">{row.department}</span>
      )
    },
    {
      key: 'events',
      header: 'Eventos',
      render: (row) => (
        <div className="text-sm">
          <p className="text-text-primary">{row.eventsCount} total</p>
          {row.pendingEvents > 0 && (
            <p className="text-amber-400">{row.pendingEvents} pendente(s)</p>
          )}
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedEmployee(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <History className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const errorColumns: Column<EventError>[] = [
    {
      key: 'event',
      header: 'Evento',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.eventCode}</p>
          <p className="text-sm text-text-secondary">{row.eventType}</p>
        </div>
      )
    },
    {
      key: 'employee',
      header: 'Funcionário',
      render: (row) => (
        <span className="text-text-primary">{row.employeeName || '-'}</span>
      )
    },
    {
      key: 'error',
      header: 'Erro',
      render: (row) => (
        <div className="max-w-xs">
          <p className="font-mono text-sm text-red-400">{row.errorCode}</p>
          <p className="text-sm text-text-secondary truncate">{row.errorMessage}</p>
        </div>
      )
    },
    {
      key: 'severity',
      header: 'Severidade',
      render: (row) => getErrorSeverityBadge(row.severity)
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getErrorStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedError(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'open' && (
            <Button variant="ghost" size="sm">
              <RotateCcw className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  // Filtered data
  const filteredEvents = mockEvents.filter(e => {
    const matchesSearch = e.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.employeeName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.employeeCpf?.includes(searchTerm);
    const matchesStatus = filterStatus === 'all' || e.status === filterStatus;
    const matchesCode = filterEventCode === 'all' || e.code === filterEventCode;
    return matchesSearch && matchesStatus && matchesCode;
  });

  const filteredBatches = mockBatches.filter(b => {
    const matchesSearch = b.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const filteredEmployees = mockEmployees.filter(e => {
    const matchesSearch = e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.cpf.includes(searchTerm) ||
      e.matricula.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const filteredErrors = mockErrors.filter(e => {
    const matchesSearch = e.eventCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.errorCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.employeeName?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              eSocial
            </h1>
            <p className="text-text-secondary mt-1">
              Gerenciamento de eventos eSocial
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Sincronizar
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewEventModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Evento
            </Button>
          </div>
        </div>

        {/* Connection Status */}
        <Card className="p-4 bg-gradient-to-r from-blue-500/10 to-indigo-600/5 border-blue-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                <Building2 className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-text-primary">Ambiente eSocial</h3>
                  <Badge variant="success">Produção</Badge>
                </div>
                <p className="text-sm text-text-secondary">
                  CNPJ: 12.345.678/0001-90 | Versão: S-1.1
                </p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm">
              <div className="text-center">
                <p className="text-text-secondary">Certificado</p>
                <p className="font-semibold text-green-400">Válido até 15/06/2025</p>
              </div>
              <div className="text-center">
                <p className="text-text-secondary">Última Sync</p>
                <p className="font-semibold text-text-primary">Há 5 min</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Eventos Pendentes"
            value={pendingEvents.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Enviados Hoje"
            value={sentToday.toString()}
            icon={<Send className="h-5 w-5" />}
            iconColor="success"
            change={12}
            changeLabel="vs ontem"
          />
          <StatCard
            title="Com Erros"
            value={errorEvents.toString()}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Funcionários"
            value={totalEmployees.toString()}
            icon={<Users className="h-5 w-5" />}
            iconColor="info"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Status dos Eventos
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={eventStatusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {eventStatusData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Envios da Semana
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={submissionTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Bar dataKey="aceitos" name="Aceitos" fill="#10b981" />
                    <Bar dataKey="rejeitados" name="Rejeitados" fill="#ef4444" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Second Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="p-6 col-span-2">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Volume Mensal de Eventos
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={monthlyEventsData}>
                    <defs>
                      <linearGradient id="eventGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="eventos"
                      name="Eventos"
                      stroke="#6366f1"
                      fill="url(#eventGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Ações Rápidas
                </h3>
                <div className="space-y-3">
                  <Button variant="outline" className="w-full justify-start">
                    <Plus className="h-4 w-4 mr-3" />
                    Novo Evento
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Upload className="h-4 w-4 mr-3" />
                    Importar Lote
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Send className="h-4 w-4 mr-3" />
                    Enviar Pendentes
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Settings className="h-4 w-4 mr-3" />
                    Configurações
                  </Button>
                </div>
              </Card>
            </div>

            {/* Recent Events & Errors */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Eventos Recentes
                  </h3>
                  <Button variant="ghost" size="sm" onClick={() => setActiveTab('events')}>
                    Ver Todos
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
                <div className="space-y-3">
                  {mockEvents.slice(0, 4).map((event) => (
                    <div
                      key={event.id}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-bg-tertiary transition-colors cursor-pointer"
                      onClick={() => setSelectedEvent(event)}
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-bg-tertiary flex items-center justify-center">
                          <FileText className="h-5 w-5 text-text-secondary" />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{event.code}</p>
                          <p className="text-sm text-text-secondary">
                            {event.employeeName || event.type}
                          </p>
                        </div>
                      </div>
                      {getEventStatusBadge(event.status)}
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Erros Pendentes
                  </h3>
                  <Button variant="ghost" size="sm" onClick={() => setActiveTab('errors')}>
                    Ver Todos
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
                <div className="space-y-3">
                  {mockErrors.filter(e => e.status === 'open').slice(0, 4).map((error) => (
                    <div
                      key={error.id}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-bg-tertiary transition-colors cursor-pointer"
                      onClick={() => setSelectedError(error)}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                          error.severity === 'critical' ? 'bg-red-500/20' : 'bg-amber-500/20'
                        }`}>
                          <AlertTriangle className={`h-5 w-5 ${
                            error.severity === 'critical' ? 'text-red-400' : 'text-amber-400'
                          }`} />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{error.eventCode}</p>
                          <p className="text-sm text-text-secondary truncate max-w-xs">
                            {error.errorMessage.substring(0, 40)}...
                          </p>
                        </div>
                      </div>
                      {getErrorSeverityBadge(error.severity)}
                    </div>
                  ))}
                  {mockErrors.filter(e => e.status === 'open').length === 0 && (
                    <div className="text-center py-8 text-text-secondary">
                      <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-400" />
                      <p>Nenhum erro pendente</p>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          </div>
        )}

        {/* Events Tab */}
        {activeTab === 'events' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar eventos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Select
                options={eventCodeOptions}
                value={filterEventCode}
                onChange={(value) => setFilterEventCode(value)}
                className="w-64"
              />
              <Select
                options={eventStatusOptions}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value)}
                className="w-48"
              />
              <Button onClick={() => setShowNewEventModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Novo Evento
              </Button>
            </div>

            <DataTable
              data={filteredEvents}
              columns={eventColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Batches Tab */}
        {activeTab === 'batches' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar lotes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                Importar
              </Button>
              <Button onClick={() => setShowNewBatchModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Novo Lote
              </Button>
            </div>

            <DataTable
              data={filteredBatches}
              columns={batchColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Employees Tab */}
        {activeTab === 'employees' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar funcionários..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>

            <DataTable
              data={filteredEmployees}
              columns={employeeColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Errors Tab */}
        {activeTab === 'errors' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar erros..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'Todos os Status' },
                  { value: 'open', label: 'Abertos' },
                  { value: 'in_progress', label: 'Em Análise' },
                  { value: 'resolved', label: 'Resolvidos' }
                ]}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value)}
                className="w-48"
              />
            </div>

            <DataTable
              data={filteredErrors}
              columns={errorColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Event Detail Modal */}
        <Modal
          isOpen={!!selectedEvent}
          onClose={() => setSelectedEvent(null)}
          title="Detalhes do Evento"
          size="lg"
        >
          {selectedEvent && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedEvent.code}</h3>
                  <p className="text-text-secondary">{selectedEvent.type}</p>
                </div>
                {getEventStatusBadge(selectedEvent.status)}
              </div>

              {selectedEvent.employeeName && (
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-sm text-text-secondary mb-1">Funcionário</p>
                  <p className="font-medium text-text-primary">{selectedEvent.employeeName}</p>
                  <p className="text-sm text-text-secondary">{selectedEvent.employeeCpf}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Protocolo</p>
                  <p className="font-mono text-text-primary">{selectedEvent.protocol || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Recibo</p>
                  <p className="font-mono text-text-primary">{selectedEvent.receipt || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Criado em</p>
                  <p className="text-text-primary">{formatDateTime(selectedEvent.createdAt)}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Enviado em</p>
                  <p className="text-text-primary">{selectedEvent.sentAt ? formatDateTime(selectedEvent.sentAt) : '-'}</p>
                </div>
              </div>

              {selectedEvent.errorMessage && (
                <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-5 w-5 text-red-400" />
                    <p className="font-medium text-red-400">{selectedEvent.errorCode}</p>
                  </div>
                  <p className="text-text-secondary">{selectedEvent.errorMessage}</p>
                </div>
              )}

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedEvent(null)}>
                  Fechar
                </Button>
                {selectedEvent.status === 'pending' && (
                  <Button>
                    <Send className="h-4 w-4 mr-2" />
                    Enviar
                  </Button>
                )}
                {(selectedEvent.status === 'error' || selectedEvent.status === 'rejected') && (
                  <Button>
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reenviar
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* Batch Detail Modal */}
        <Modal
          isOpen={!!selectedBatch}
          onClose={() => setSelectedBatch(null)}
          title="Detalhes do Lote"
          size="lg"
        >
          {selectedBatch && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedBatch.name}</h3>
                  {selectedBatch.period && (
                    <p className="text-text-secondary">Período: {selectedBatch.period}</p>
                  )}
                </div>
                {getBatchStatusBadge(selectedBatch.status)}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedBatch.totalEvents}</p>
                  <p className="text-sm text-text-secondary">Total</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-amber-400">{selectedBatch.pending}</p>
                  <p className="text-sm text-text-secondary">Pendentes</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-green-400">{selectedBatch.accepted}</p>
                  <p className="text-sm text-text-secondary">Aceitos</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-red-400">{selectedBatch.rejected}</p>
                  <p className="text-sm text-text-secondary">Rejeitados</p>
                </div>
              </div>

              {selectedBatch.protocol && (
                <div>
                  <p className="text-sm text-text-secondary">Protocolo</p>
                  <p className="font-mono text-text-primary">{selectedBatch.protocol}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Criado em</p>
                  <p className="text-text-primary">{formatDateTime(selectedBatch.createdAt)}</p>
                </div>
                {selectedBatch.sentAt && (
                  <div>
                    <p className="text-sm text-text-secondary">Enviado em</p>
                    <p className="text-text-primary">{formatDateTime(selectedBatch.sentAt)}</p>
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedBatch(null)}>
                  Fechar
                </Button>
                {selectedBatch.status === 'ready' && (
                  <Button>
                    <Send className="h-4 w-4 mr-2" />
                    Enviar Lote
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* Error Detail Modal */}
        <Modal
          isOpen={!!selectedError}
          onClose={() => setSelectedError(null)}
          title="Detalhes do Erro"
          size="lg"
        >
          {selectedError && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getErrorSeverityBadge(selectedError.severity)}
                  {getErrorStatusBadge(selectedError.status)}
                </div>
                <span className="text-sm text-text-secondary">
                  {formatDateTime(selectedError.createdAt)}
                </span>
              </div>

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <p className="text-sm text-text-secondary mb-1">Evento</p>
                <p className="font-medium text-text-primary">{selectedError.eventCode}</p>
                <p className="text-sm text-text-secondary">{selectedError.eventType}</p>
              </div>

              {selectedError.employeeName && (
                <div>
                  <p className="text-sm text-text-secondary">Funcionário</p>
                  <p className="text-text-primary">{selectedError.employeeName}</p>
                </div>
              )}

              <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-5 w-5 text-red-400" />
                  <p className="font-mono font-medium text-red-400">{selectedError.errorCode}</p>
                </div>
                <p className="text-text-primary">{selectedError.errorMessage}</p>
              </div>

              {selectedError.resolvedAt && (
                <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <p className="font-medium text-green-400">Resolvido</p>
                  </div>
                  <p className="text-text-secondary text-sm">
                    Por {selectedError.resolvedBy} em {formatDateTime(selectedError.resolvedAt)}
                  </p>
                </div>
              )}

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedError(null)}>
                  Fechar
                </Button>
                {selectedError.status === 'open' && (
                  <>
                    <Button variant="outline">
                      Ignorar
                    </Button>
                    <Button>
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Corrigir e Reenviar
                    </Button>
                  </>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* New Event Modal */}
        <Modal
          isOpen={showNewEventModal}
          onClose={() => setShowNewEventModal(false)}
          title="Novo Evento eSocial"
          size="lg"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Tipo de Evento
              </label>
              <Select
                options={Object.entries(EVENT_TYPES).map(([code, info]) => ({
                  value: code,
                  label: `${code} - ${info.name}`
                }))}
                value={newEventType}
                onChange={(value) => setNewEventType(value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Funcionário (se aplicável)
              </label>
              <Select
                options={[
                  { value: '', label: 'Selecione um funcionário' },
                  ...mockEmployees.map(e => ({
                    value: e.id,
                    label: `${e.name} - ${e.cpf}`
                  }))
                ]}
                value={newEventEmployee}
                onChange={(value) => setNewEventEmployee(value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Descrição
              </label>
              <Input placeholder="Descrição do evento" />
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewEventModal(false)}>
                Cancelar
              </Button>
              <Button>
                Criar Evento
              </Button>
            </div>
          </div>
        </Modal>

        {/* New Batch Modal */}
        <Modal
          isOpen={showNewBatchModal}
          onClose={() => setShowNewBatchModal(false)}
          title="Novo Lote"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nome do Lote
              </label>
              <Input placeholder="Ex: Folha de Pagamento 01/2024" />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Tipo
              </label>
              <Select
                options={[
                  { value: 'periodic', label: 'Eventos Periódicos' },
                  { value: 'non_periodic', label: 'Eventos Não Periódicos' },
                  { value: 'table', label: 'Eventos de Tabelas' }
                ]}
                value={newBatchType}
                onChange={(value) => setNewBatchType(value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Período (para eventos periódicos)
              </label>
              <Input placeholder="MM/AAAA" />
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewBatchModal(false)}>
                Cancelar
              </Button>
              <Button>
                Criar Lote
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
