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
  FileText,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Send,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Eye,
  Edit,
  Trash2,
  Printer,
  Mail,
  Copy,
  RotateCcw,
  Building2,
  Package,
  DollarSign,
  TrendingUp,
  Calendar,
  ChevronRight,
  FileWarning,
  Ban,
  ExternalLink,
  QrCode,
  Settings,
  History
} from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend,
  LineChart, Line, AreaChart, Area
} from 'recharts';

// Types
interface NFe {
  id: string;
  number: string;
  series: string;
  accessKey: string;
  type: 'saida' | 'entrada';
  nature: string;
  recipientId: string;
  recipientName: string;
  recipientCnpj: string;
  status: 'draft' | 'pending' | 'authorized' | 'denied' | 'cancelled' | 'inutilized';
  totalValue: number;
  icmsValue: number;
  ipiValue: number;
  pisValue: number;
  cofinsValue: number;
  issueDate: string;
  authorizationDate?: string;
  protocol?: string;
  cancelProtocol?: string;
  cancelReason?: string;
  items: NFeItem[];
  events: NFeEvent[];
  xmlPath?: string;
  danfePath?: string;
  createdAt: string;
  updatedAt: string;
}

interface NFeItem {
  id: string;
  code: string;
  description: string;
  ncm: string;
  cfop: string;
  quantity: number;
  unit: string;
  unitValue: number;
  totalValue: number;
  icmsBase: number;
  icmsRate: number;
  icmsValue: number;
}

interface NFeRecipient {
  id: string;
  type: 'pj' | 'pf';
  name: string;
  document: string;
  ie?: string;
  email?: string;
  phone?: string;
  address: {
    street: string;
    number: string;
    complement?: string;
    neighborhood: string;
    city: string;
    state: string;
    zipCode: string;
  };
  totalNFe: number;
  totalValue: number;
  lastNFeDate?: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

interface NFeEvent {
  id: string;
  nfeId: string;
  type: 'authorization' | 'cancellation' | 'correction' | 'awareness' | 'operation_refusal';
  description: string;
  protocol?: string;
  correctionText?: string;
  status: 'pending' | 'processed' | 'rejected';
  createdAt: string;
  processedAt?: string;
}

// Mock Data
const mockNFes: NFe[] = [
  {
    id: '1',
    number: '000001234',
    series: '1',
    accessKey: '35240112345678000199550010000012341234567890',
    type: 'saida',
    nature: 'Venda de mercadoria',
    recipientId: 'r1',
    recipientName: 'ABC Comércio Ltda',
    recipientCnpj: '12.345.678/0001-90',
    status: 'authorized',
    totalValue: 15680.50,
    icmsValue: 2824.49,
    ipiValue: 784.03,
    pisValue: 258.73,
    cofinsValue: 1191.72,
    issueDate: '2024-01-15T10:30:00',
    authorizationDate: '2024-01-15T10:31:00',
    protocol: '135240000123456',
    items: [],
    events: [],
    xmlPath: '/xml/nfe_000001234.xml',
    danfePath: '/pdf/danfe_000001234.pdf',
    createdAt: '2024-01-15T10:00:00',
    updatedAt: '2024-01-15T10:31:00'
  },
  {
    id: '2',
    number: '000001235',
    series: '1',
    accessKey: '35240112345678000199550010000012351234567891',
    type: 'saida',
    nature: 'Venda de mercadoria',
    recipientId: 'r2',
    recipientName: 'XYZ Indústria S.A.',
    recipientCnpj: '98.765.432/0001-10',
    status: 'authorized',
    totalValue: 45230.00,
    icmsValue: 8141.40,
    ipiValue: 2261.50,
    pisValue: 746.30,
    cofinsValue: 3437.48,
    issueDate: '2024-01-15T14:00:00',
    authorizationDate: '2024-01-15T14:01:00',
    protocol: '135240000123457',
    items: [],
    events: [],
    xmlPath: '/xml/nfe_000001235.xml',
    danfePath: '/pdf/danfe_000001235.pdf',
    createdAt: '2024-01-15T13:30:00',
    updatedAt: '2024-01-15T14:01:00'
  },
  {
    id: '3',
    number: '000001236',
    series: '1',
    accessKey: '35240112345678000199550010000012361234567892',
    type: 'saida',
    nature: 'Prestação de serviços',
    recipientId: 'r3',
    recipientName: 'Tech Solutions ME',
    recipientCnpj: '11.222.333/0001-44',
    status: 'pending',
    totalValue: 8500.00,
    icmsValue: 0,
    ipiValue: 0,
    pisValue: 140.25,
    cofinsValue: 646.00,
    issueDate: '2024-01-15T16:00:00',
    items: [],
    events: [],
    createdAt: '2024-01-15T15:45:00',
    updatedAt: '2024-01-15T16:00:00'
  },
  {
    id: '4',
    number: '000001230',
    series: '1',
    accessKey: '35240112345678000199550010000012301234567886',
    type: 'saida',
    nature: 'Venda de mercadoria',
    recipientId: 'r1',
    recipientName: 'ABC Comércio Ltda',
    recipientCnpj: '12.345.678/0001-90',
    status: 'cancelled',
    totalValue: 5400.00,
    icmsValue: 972.00,
    ipiValue: 270.00,
    pisValue: 89.10,
    cofinsValue: 410.40,
    issueDate: '2024-01-10T09:00:00',
    authorizationDate: '2024-01-10T09:01:00',
    protocol: '135240000123450',
    cancelProtocol: '135240000123455',
    cancelReason: 'Erro na quantidade de produtos',
    items: [],
    events: [],
    createdAt: '2024-01-10T08:30:00',
    updatedAt: '2024-01-10T15:00:00'
  },
  {
    id: '5',
    number: '000001237',
    series: '1',
    accessKey: '35240112345678000199550010000012371234567893',
    type: 'saida',
    nature: 'Venda de mercadoria',
    recipientId: 'r4',
    recipientName: 'Distribuidora Central',
    recipientCnpj: '55.666.777/0001-88',
    status: 'denied',
    totalValue: 12350.00,
    icmsValue: 2223.00,
    ipiValue: 617.50,
    pisValue: 203.78,
    cofinsValue: 938.60,
    issueDate: '2024-01-15T11:00:00',
    items: [],
    events: [],
    createdAt: '2024-01-15T10:45:00',
    updatedAt: '2024-01-15T11:02:00'
  },
  {
    id: '6',
    number: '',
    series: '1',
    accessKey: '',
    type: 'saida',
    nature: 'Venda de mercadoria',
    recipientId: 'r2',
    recipientName: 'XYZ Indústria S.A.',
    recipientCnpj: '98.765.432/0001-10',
    status: 'draft',
    totalValue: 23400.00,
    icmsValue: 4212.00,
    ipiValue: 1170.00,
    pisValue: 386.10,
    cofinsValue: 1778.40,
    issueDate: '',
    items: [],
    events: [],
    createdAt: '2024-01-15T17:00:00',
    updatedAt: '2024-01-15T17:00:00'
  }
];

const mockRecipients: NFeRecipient[] = [
  {
    id: 'r1',
    type: 'pj',
    name: 'ABC Comércio Ltda',
    document: '12.345.678/0001-90',
    ie: '123.456.789.012',
    email: 'financeiro@abccomercio.com.br',
    phone: '(11) 3456-7890',
    address: {
      street: 'Av. Paulista',
      number: '1000',
      complement: 'Sala 501',
      neighborhood: 'Bela Vista',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '01310-100'
    },
    totalNFe: 45,
    totalValue: 234567.89,
    lastNFeDate: '2024-01-15',
    status: 'active',
    createdAt: '2023-01-15T10:00:00'
  },
  {
    id: 'r2',
    type: 'pj',
    name: 'XYZ Indústria S.A.',
    document: '98.765.432/0001-10',
    ie: '987.654.321.098',
    email: 'nfe@xyzindustria.com.br',
    phone: '(11) 2345-6789',
    address: {
      street: 'Rua Industrial',
      number: '500',
      neighborhood: 'Distrito Industrial',
      city: 'Guarulhos',
      state: 'SP',
      zipCode: '07220-000'
    },
    totalNFe: 128,
    totalValue: 1567890.45,
    lastNFeDate: '2024-01-15',
    status: 'active',
    createdAt: '2022-06-10T14:00:00'
  },
  {
    id: 'r3',
    type: 'pj',
    name: 'Tech Solutions ME',
    document: '11.222.333/0001-44',
    ie: '',
    email: 'contato@techsolutions.com.br',
    phone: '(11) 98765-4321',
    address: {
      street: 'Rua das Startups',
      number: '123',
      neighborhood: 'Vila Madalena',
      city: 'São Paulo',
      state: 'SP',
      zipCode: '05443-000'
    },
    totalNFe: 12,
    totalValue: 45678.90,
    lastNFeDate: '2024-01-15',
    status: 'active',
    createdAt: '2023-08-20T09:00:00'
  },
  {
    id: 'r4',
    type: 'pj',
    name: 'Distribuidora Central',
    document: '55.666.777/0001-88',
    ie: '556.667.778.889',
    email: 'compras@distribuidoracentral.com.br',
    phone: '(11) 4567-8901',
    address: {
      street: 'Rodovia Anhanguera',
      number: 'KM 32',
      neighborhood: 'Distrito Industrial',
      city: 'Cajamar',
      state: 'SP',
      zipCode: '07750-000'
    },
    totalNFe: 67,
    totalValue: 456789.12,
    lastNFeDate: '2024-01-15',
    status: 'active',
    createdAt: '2023-03-15T11:00:00'
  }
];

const mockEvents: NFeEvent[] = [
  {
    id: 'e1',
    nfeId: '1',
    type: 'authorization',
    description: 'NF-e autorizada com sucesso',
    protocol: '135240000123456',
    status: 'processed',
    createdAt: '2024-01-15T10:31:00',
    processedAt: '2024-01-15T10:31:00'
  },
  {
    id: 'e2',
    nfeId: '4',
    type: 'cancellation',
    description: 'Cancelamento da NF-e',
    protocol: '135240000123455',
    status: 'processed',
    createdAt: '2024-01-10T15:00:00',
    processedAt: '2024-01-10T15:00:00'
  },
  {
    id: 'e3',
    nfeId: '2',
    type: 'correction',
    description: 'Carta de Correção Eletrônica',
    protocol: '135240000123458',
    correctionText: 'Onde se lê "10 unidades" leia-se "12 unidades"',
    status: 'processed',
    createdAt: '2024-01-15T15:00:00',
    processedAt: '2024-01-15T15:01:00'
  }
];

// Chart colors
const CHART_COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];

export function SEFAZPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNFe, setSelectedNFe] = useState<NFe | null>(null);
  const [selectedRecipient, setSelectedRecipient] = useState<NFeRecipient | null>(null);
  const [showNewNFeModal, setShowNewNFeModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showCorrectionModal, setShowCorrectionModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <FileText className="h-4 w-4" /> },
    { value: 'nfe', label: 'NF-e', icon: <FileText className="h-4 w-4" /> },
    { value: 'recipients', label: 'Destinatários', icon: <Users className="h-4 w-4" /> },
    { value: 'events', label: 'Eventos', icon: <History className="h-4 w-4" /> },
    { value: 'settings', label: 'Configurações', icon: <Settings className="h-4 w-4" /> }
  ];

  const statusOptions: SelectOption[] = [
    { value: 'all', label: 'Todos os Status' },
    { value: 'draft', label: 'Rascunho' },
    { value: 'pending', label: 'Pendente' },
    { value: 'authorized', label: 'Autorizada' },
    { value: 'denied', label: 'Denegada' },
    { value: 'cancelled', label: 'Cancelada' },
    { value: 'inutilized', label: 'Inutilizada' }
  ];

  // Calculated stats
  const authorizedNFes = mockNFes.filter(n => n.status === 'authorized').length;
  const pendingNFes = mockNFes.filter(n => n.status === 'pending' || n.status === 'draft').length;
  const cancelledNFes = mockNFes.filter(n => n.status === 'cancelled').length;
  const totalValue = mockNFes
    .filter(n => n.status === 'authorized')
    .reduce((sum, n) => sum + n.totalValue, 0);

  // Chart data
  const statusDistributionData = [
    { name: 'Autorizadas', value: authorizedNFes, color: '#10b981' },
    { name: 'Pendentes', value: pendingNFes, color: '#f59e0b' },
    { name: 'Canceladas', value: cancelledNFes, color: '#ef4444' },
    { name: 'Denegadas', value: mockNFes.filter(n => n.status === 'denied').length, color: '#dc2626' }
  ];

  const dailyEmissionsData = [
    { day: '10/01', emitidas: 12, valor: 45000 },
    { day: '11/01', emitidas: 8, valor: 32000 },
    { day: '12/01', emitidas: 15, valor: 58000 },
    { day: '13/01', emitidas: 10, valor: 41000 },
    { day: '14/01', emitidas: 18, valor: 72000 },
    { day: '15/01', emitidas: 14, valor: 55000 }
  ];

  const valueByRecipientData = mockRecipients
    .sort((a, b) => b.totalValue - a.totalValue)
    .slice(0, 5)
    .map(r => ({
      name: r.name.substring(0, 15) + '...',
      valor: r.totalValue / 1000
    }));

  const monthlyTrendData = [
    { month: 'Set', nfes: 156, valor: 450000 },
    { month: 'Out', nfes: 178, valor: 520000 },
    { month: 'Nov', nfes: 192, valor: 580000 },
    { month: 'Dez', nfes: 245, valor: 720000 },
    { month: 'Jan', nfes: 134, valor: 380000 }
  ];

  // Format functions
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

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

  const formatAccessKey = (key: string) => {
    if (!key) return '-';
    return key.replace(/(\d{4})/g, '$1 ').trim();
  };

  const getNFeStatusBadge = (status: NFe['status']) => {
    const config = {
      draft: { variant: 'neutral' as const, label: 'Rascunho', icon: Edit },
      pending: { variant: 'warning' as const, label: 'Pendente', icon: Clock },
      authorized: { variant: 'success' as const, label: 'Autorizada', icon: CheckCircle },
      denied: { variant: 'danger' as const, label: 'Denegada', icon: XCircle },
      cancelled: { variant: 'danger' as const, label: 'Cancelada', icon: Ban },
      inutilized: { variant: 'neutral' as const, label: 'Inutilizada', icon: FileWarning }
    };
    const { variant, label, icon: Icon } = config[status];
    return (
      <Badge variant={variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {label}
      </Badge>
    );
  };

  const getEventTypeBadge = (type: NFeEvent['type']) => {
    const config = {
      authorization: { variant: 'success' as const, label: 'Autorização' },
      cancellation: { variant: 'danger' as const, label: 'Cancelamento' },
      correction: { variant: 'warning' as const, label: 'Carta de Correção' },
      awareness: { variant: 'info' as const, label: 'Ciência da Operação' },
      operation_refusal: { variant: 'danger' as const, label: 'Recusa da Operação' }
    };
    const { variant, label } = config[type];
    return <Badge variant={variant}>{label}</Badge>;
  };

  // Table columns
  const nfeColumns: Column<NFe>[] = [
    {
      key: 'number',
      header: 'NF-e',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary font-mono">
            {row.number || 'Rascunho'}
          </p>
          <p className="text-xs text-text-secondary">Série {row.series}</p>
        </div>
      )
    },
    {
      key: 'recipient',
      header: 'Destinatário',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.recipientName}</p>
          <p className="text-sm text-text-secondary">{row.recipientCnpj}</p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getNFeStatusBadge(row.status)
    },
    {
      key: 'value',
      header: 'Valor Total',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {formatCurrency(row.totalValue)}
        </span>
      )
    },
    {
      key: 'issueDate',
      header: 'Emissão',
      render: (row) => (
        <span className="text-text-secondary">
          {row.issueDate ? formatDateTime(row.issueDate) : '-'}
        </span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedNFe(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {row.status === 'authorized' && (
            <>
              <Button variant="ghost" size="sm">
                <Printer className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Mail className="h-4 w-4" />
              </Button>
            </>
          )}
          {row.status === 'draft' && (
            <Button variant="ghost" size="sm">
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const recipientColumns: Column<NFeRecipient>[] = [
    {
      key: 'name',
      header: 'Destinatário',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
            <Building2 className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.document}</p>
          </div>
        </div>
      )
    },
    {
      key: 'ie',
      header: 'IE',
      render: (row) => (
        <span className="text-text-secondary font-mono">
          {row.ie || 'Isento'}
        </span>
      )
    },
    {
      key: 'location',
      header: 'Cidade/UF',
      render: (row) => (
        <span className="text-text-secondary">
          {row.address.city}/{row.address.state}
        </span>
      )
    },
    {
      key: 'totalNFe',
      header: 'NF-e',
      render: (row) => (
        <span className="text-text-primary">{row.totalNFe}</span>
      )
    },
    {
      key: 'totalValue',
      header: 'Valor Total',
      render: (row) => (
        <span className="font-medium text-text-primary">
          {formatCurrency(row.totalValue)}
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
            onClick={() => setSelectedRecipient(row)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const eventColumns: Column<NFeEvent>[] = [
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => getEventTypeBadge(row.type)
    },
    {
      key: 'nfe',
      header: 'NF-e',
      render: (row) => {
        const nfe = mockNFes.find(n => n.id === row.nfeId);
        return (
          <span className="font-mono text-text-primary">
            {nfe?.number || '-'}
          </span>
        );
      }
    },
    {
      key: 'description',
      header: 'Descrição',
      render: (row) => (
        <p className="text-text-secondary max-w-xs truncate">{row.description}</p>
      )
    },
    {
      key: 'protocol',
      header: 'Protocolo',
      render: (row) => (
        <span className="font-mono text-text-secondary text-sm">
          {row.protocol || '-'}
        </span>
      )
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <span className="text-text-secondary">
          {formatDateTime(row.createdAt)}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <Badge variant={row.status === 'processed' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'}>
          {row.status === 'processed' ? 'Processado' : row.status === 'rejected' ? 'Rejeitado' : 'Pendente'}
        </Badge>
      )
    }
  ];

  // Filtered data
  const filteredNFes = mockNFes.filter(n => {
    const matchesSearch = n.number.includes(searchTerm) ||
      n.recipientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.recipientCnpj.includes(searchTerm) ||
      n.accessKey.includes(searchTerm);
    const matchesStatus = filterStatus === 'all' || n.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const filteredRecipients = mockRecipients.filter(r => {
    const matchesSearch = r.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.document.includes(searchTerm);
    return matchesSearch;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              SEFAZ - NF-e
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de notas fiscais eletrônicas
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Consultar SEFAZ
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button onClick={() => setShowNewNFeModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova NF-e
            </Button>
          </div>
        </div>

        {/* Connection Status */}
        <Card className="p-4 bg-gradient-to-r from-emerald-500/10 to-green-600/5 border-emerald-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                <FileText className="h-6 w-6 text-emerald-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-text-primary">SEFAZ SP</h3>
                  <Badge variant="success">Online</Badge>
                </div>
                <p className="text-sm text-text-secondary">
                  CNPJ: 12.345.678/0001-90 | Ambiente: Produção
                </p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm">
              <div className="text-center">
                <p className="text-text-secondary">Certificado</p>
                <p className="font-semibold text-green-400">Válido até 15/06/2025</p>
              </div>
              <div className="text-center">
                <p className="text-text-secondary">Última Consulta</p>
                <p className="font-semibold text-text-primary">Há 2 min</p>
              </div>
              <div className="text-center">
                <p className="text-text-secondary">Versão NF-e</p>
                <p className="font-semibold text-text-primary">4.00</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="NF-e Autorizadas"
            value={authorizedNFes.toString()}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
            change={8}
            changeLabel="este mês"
          />
          <StatCard
            title="Pendentes"
            value={pendingNFes.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Canceladas"
            value={cancelledNFes.toString()}
            icon={<Ban className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Valor Total"
            value={formatCurrency(totalValue)}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="info"
            change={15}
            changeLabel="vs mês anterior"
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
                  Distribuição por Status
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statusDistributionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {statusDistributionData.map((entry, index) => (
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
                  Emissões por Dia
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dailyEmissionsData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      formatter={(value: number, name: string) => [
                        name === 'valor' ? formatCurrency(value) : value,
                        name === 'emitidas' ? 'NF-e' : 'Valor'
                      ]}
                    />
                    <Legend />
                    <Bar dataKey="emitidas" name="NF-e Emitidas" fill="#6366f1" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Second Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="p-6 col-span-2">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Evolução Mensal
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={monthlyTrendData}>
                    <defs>
                      <linearGradient id="nfeGradient" x1="0" y1="0" x2="0" y2="1">
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
                      dataKey="nfes"
                      name="NF-e"
                      stroke="#6366f1"
                      fill="url(#nfeGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Ações Rápidas
                </h3>
                <div className="space-y-3">
                  <Button variant="outline" className="w-full justify-start" onClick={() => setShowNewNFeModal(true)}>
                    <Plus className="h-4 w-4 mr-3" />
                    Nova NF-e
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <FileWarning className="h-4 w-4 mr-3" />
                    Inutilizar Numeração
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="h-4 w-4 mr-3" />
                    Baixar XML em Lote
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Settings className="h-4 w-4 mr-3" />
                    Configurações
                  </Button>
                </div>
              </Card>
            </div>

            {/* Recent NFes */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  NF-e Recentes
                </h3>
                <Button variant="ghost" size="sm" onClick={() => setActiveTab('nfe')}>
                  Ver Todas
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
              <div className="space-y-3">
                {mockNFes.slice(0, 5).map((nfe) => (
                  <div
                    key={nfe.id}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-bg-tertiary transition-colors cursor-pointer"
                    onClick={() => setSelectedNFe(nfe)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-bg-tertiary flex items-center justify-center">
                        <FileText className="h-5 w-5 text-text-secondary" />
                      </div>
                      <div>
                        <p className="font-medium text-text-primary font-mono">
                          {nfe.number || 'Rascunho'}
                        </p>
                        <p className="text-sm text-text-secondary">
                          {nfe.recipientName}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-medium text-text-primary">
                        {formatCurrency(nfe.totalValue)}
                      </span>
                      {getNFeStatusBadge(nfe.status)}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* NF-e Tab */}
        {activeTab === 'nfe' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar por número, chave, destinatário..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Select
                options={statusOptions}
                value={filterStatus}
                onChange={(value) => setFilterStatus(value)}
                className="w-48"
              />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Mais Filtros
              </Button>
              <Button onClick={() => setShowNewNFeModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nova NF-e
              </Button>
            </div>

            <DataTable
              data={filteredNFes}
              columns={nfeColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Recipients Tab */}
        {activeTab === 'recipients' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar destinatários..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  icon={<Search className="h-4 w-4" />}
                />
              </div>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Novo Destinatário
              </Button>
            </div>

            <DataTable
              data={filteredRecipients}
              columns={recipientColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
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
                options={[
                  { value: 'all', label: 'Todos os Tipos' },
                  { value: 'authorization', label: 'Autorização' },
                  { value: 'cancellation', label: 'Cancelamento' },
                  { value: 'correction', label: 'Carta de Correção' }
                ]}
                value="all"
                onChange={() => {}}
                className="w-48"
              />
            </div>

            <DataTable
              data={mockEvents}
              columns={eventColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Dados do Emitente
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">
                    Razão Social
                  </label>
                  <Input value="Conecta PRO Tecnologia Ltda" disabled />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      CNPJ
                    </label>
                    <Input value="12.345.678/0001-90" disabled />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Inscrição Estadual
                    </label>
                    <Input value="123.456.789.012" disabled />
                  </div>
                </div>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar Dados
                </Button>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Certificado Digital
              </h3>
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-text-secondary">Status</span>
                    <Badge variant="success">Válido</Badge>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-text-secondary">Titular</span>
                    <span className="text-text-primary">CONECTA PRO TECNOLOGIA LTDA</span>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-text-secondary">Validade</span>
                    <span className="text-text-primary">15/06/2025</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-text-secondary">Tipo</span>
                    <span className="text-text-primary">A1</span>
                  </div>
                </div>
                <Button variant="outline" className="w-full">
                  Atualizar Certificado
                </Button>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Configurações de Emissão
              </h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Série Padrão
                    </label>
                    <Input value="1" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Próximo Número
                    </label>
                    <Input value="1238" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">
                    Ambiente
                  </label>
                  <Select
                    options={[
                      { value: 'production', label: 'Produção' },
                      { value: 'homologation', label: 'Homologação' }
                    ]}
                    value="production"
                    onChange={() => {}}
                  />
                </div>
                <Button>Salvar Configurações</Button>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Configurações de Email
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-text-primary">Enviar XML automaticamente</p>
                    <p className="text-sm text-text-secondary">Envia XML para o destinatário após autorização</p>
                  </div>
                  <input type="checkbox" className="toggle" defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-text-primary">Enviar DANFE automaticamente</p>
                    <p className="text-sm text-text-secondary">Envia DANFE em PDF para o destinatário</p>
                  </div>
                  <input type="checkbox" className="toggle" defaultChecked />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">
                    Cópia para
                  </label>
                  <Input placeholder="email@empresa.com" />
                </div>
                <Button>Salvar Configurações</Button>
              </div>
            </Card>
          </div>
        )}

        {/* NF-e Detail Modal */}
        <Modal
          isOpen={!!selectedNFe}
          onClose={() => setSelectedNFe(null)}
          title="Detalhes da NF-e"
          size="lg"
        >
          {selectedNFe && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-text-primary font-mono">
                    NF-e {selectedNFe.number || 'Rascunho'}
                  </h3>
                  <p className="text-text-secondary">Série {selectedNFe.series}</p>
                </div>
                {getNFeStatusBadge(selectedNFe.status)}
              </div>

              {selectedNFe.accessKey && (
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-sm text-text-secondary mb-1">Chave de Acesso</p>
                  <p className="font-mono text-text-primary text-sm break-all">
                    {formatAccessKey(selectedNFe.accessKey)}
                  </p>
                </div>
              )}

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <p className="text-sm text-text-secondary mb-1">Destinatário</p>
                <p className="font-medium text-text-primary">{selectedNFe.recipientName}</p>
                <p className="text-sm text-text-secondary">{selectedNFe.recipientCnpj}</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-text-primary">
                    {formatCurrency(selectedNFe.totalValue)}
                  </p>
                  <p className="text-sm text-text-secondary">Valor Total</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-lg font-bold text-text-primary">
                    {formatCurrency(selectedNFe.icmsValue)}
                  </p>
                  <p className="text-sm text-text-secondary">ICMS</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-lg font-bold text-text-primary">
                    {formatCurrency(selectedNFe.ipiValue)}
                  </p>
                  <p className="text-sm text-text-secondary">IPI</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-lg font-bold text-text-primary">
                    {formatCurrency(selectedNFe.pisValue + selectedNFe.cofinsValue)}
                  </p>
                  <p className="text-sm text-text-secondary">PIS/COFINS</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Natureza da Operação</p>
                  <p className="text-text-primary">{selectedNFe.nature}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Emissão</p>
                  <p className="text-text-primary">
                    {selectedNFe.issueDate ? formatDateTime(selectedNFe.issueDate) : '-'}
                  </p>
                </div>
                {selectedNFe.protocol && (
                  <div>
                    <p className="text-sm text-text-secondary">Protocolo</p>
                    <p className="font-mono text-text-primary">{selectedNFe.protocol}</p>
                  </div>
                )}
                {selectedNFe.authorizationDate && (
                  <div>
                    <p className="text-sm text-text-secondary">Autorização</p>
                    <p className="text-text-primary">{formatDateTime(selectedNFe.authorizationDate)}</p>
                  </div>
                )}
              </div>

              {selectedNFe.status === 'cancelled' && selectedNFe.cancelReason && (
                <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <Ban className="h-5 w-5 text-red-400" />
                    <p className="font-medium text-red-400">NF-e Cancelada</p>
                  </div>
                  <p className="text-text-secondary">{selectedNFe.cancelReason}</p>
                  {selectedNFe.cancelProtocol && (
                    <p className="text-sm text-text-secondary mt-2">
                      Protocolo: {selectedNFe.cancelProtocol}
                    </p>
                  )}
                </div>
              )}

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedNFe(null)}>
                  Fechar
                </Button>
                {selectedNFe.status === 'authorized' && (
                  <>
                    <Button variant="outline">
                      <Printer className="h-4 w-4 mr-2" />
                      DANFE
                    </Button>
                    <Button variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      XML
                    </Button>
                    <Button variant="outline">
                      <Mail className="h-4 w-4 mr-2" />
                      Enviar Email
                    </Button>
                    <Button variant="outline" onClick={() => {
                      setSelectedNFe(null);
                      setShowCorrectionModal(true);
                    }}>
                      <Edit className="h-4 w-4 mr-2" />
                      CC-e
                    </Button>
                    <Button variant="danger" onClick={() => {
                      setSelectedNFe(null);
                      setShowCancelModal(true);
                    }}>
                      <Ban className="h-4 w-4 mr-2" />
                      Cancelar
                    </Button>
                  </>
                )}
                {selectedNFe.status === 'draft' && (
                  <Button>
                    <Send className="h-4 w-4 mr-2" />
                    Emitir NF-e
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* Recipient Detail Modal */}
        <Modal
          isOpen={!!selectedRecipient}
          onClose={() => setSelectedRecipient(null)}
          title="Detalhes do Destinatário"
          size="lg"
        >
          {selectedRecipient && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-full bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                  <Building2 className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedRecipient.name}</h3>
                  <p className="text-text-secondary">{selectedRecipient.document}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-text-secondary">Inscrição Estadual</p>
                  <p className="text-text-primary">{selectedRecipient.ie || 'Isento'}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Email</p>
                  <p className="text-text-primary">{selectedRecipient.email || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Telefone</p>
                  <p className="text-text-primary">{selectedRecipient.phone || '-'}</p>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <p className="text-sm text-text-secondary mb-2">Endereço</p>
                <p className="text-text-primary">
                  {selectedRecipient.address.street}, {selectedRecipient.address.number}
                  {selectedRecipient.address.complement && ` - ${selectedRecipient.address.complement}`}
                </p>
                <p className="text-text-secondary">
                  {selectedRecipient.address.neighborhood} - {selectedRecipient.address.city}/{selectedRecipient.address.state}
                </p>
                <p className="text-text-secondary">CEP: {selectedRecipient.address.zipCode}</p>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-2xl font-bold text-text-primary">{selectedRecipient.totalNFe}</p>
                  <p className="text-sm text-text-secondary">NF-e</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-xl font-bold text-text-primary">
                    {formatCurrency(selectedRecipient.totalValue)}
                  </p>
                  <p className="text-sm text-text-secondary">Valor Total</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary text-center">
                  <p className="text-text-primary">
                    {selectedRecipient.lastNFeDate ? formatDate(selectedRecipient.lastNFeDate) : '-'}
                  </p>
                  <p className="text-sm text-text-secondary">Última NF-e</p>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setSelectedRecipient(null)}>
                  Fechar
                </Button>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
                <Button>
                  <FileText className="h-4 w-4 mr-2" />
                  Nova NF-e
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New NF-e Modal */}
        <Modal
          isOpen={showNewNFeModal}
          onClose={() => setShowNewNFeModal(false)}
          title="Nova NF-e"
          size="lg"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Destinatário
              </label>
              <Select
                options={mockRecipients.map(r => ({
                  value: r.id,
                  label: `${r.name} - ${r.document}`
                }))}
                value=""
                onChange={() => {}}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Natureza da Operação
              </label>
              <Select
                options={[
                  { value: 'venda', label: 'Venda de mercadoria' },
                  { value: 'servico', label: 'Prestação de serviços' },
                  { value: 'devolucao', label: 'Devolução de mercadoria' },
                  { value: 'remessa', label: 'Remessa para demonstração' }
                ]}
                value="venda"
                onChange={() => {}}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Série
                </label>
                <Input value="1" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Data de Emissão
                </label>
                <Input type="date" />
              </div>
            </div>
            <div className="p-4 rounded-lg bg-bg-tertiary">
              <h4 className="font-medium text-text-primary mb-3">Itens da NF-e</h4>
              <p className="text-text-secondary text-sm">
                Adicione os produtos/serviços que serão incluídos na NF-e.
              </p>
              <Button variant="outline" className="mt-3">
                <Plus className="h-4 w-4 mr-2" />
                Adicionar Item
              </Button>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewNFeModal(false)}>
                Cancelar
              </Button>
              <Button variant="outline">
                Salvar Rascunho
              </Button>
              <Button>
                <Send className="h-4 w-4 mr-2" />
                Emitir NF-e
              </Button>
            </div>
          </div>
        </Modal>

        {/* Cancel NF-e Modal */}
        <Modal
          isOpen={showCancelModal}
          onClose={() => setShowCancelModal(false)}
          title="Cancelar NF-e"
        >
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                <p className="font-medium text-red-400">Atenção</p>
              </div>
              <p className="text-text-secondary text-sm">
                O cancelamento da NF-e é irreversível e deve ser realizado em até 24 horas após a autorização.
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Justificativa (mínimo 15 caracteres)
              </label>
              <textarea
                className="w-full h-24 px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary placeholder-text-muted resize-none focus:outline-none focus:border-accent-primary"
                placeholder="Informe o motivo do cancelamento..."
              />
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowCancelModal(false)}>
                Voltar
              </Button>
              <Button variant="danger">
                Confirmar Cancelamento
              </Button>
            </div>
          </div>
        </Modal>

        {/* Correction Letter Modal */}
        <Modal
          isOpen={showCorrectionModal}
          onClose={() => setShowCorrectionModal(false)}
          title="Carta de Correção (CC-e)"
        >
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-5 w-5 text-amber-400" />
                <p className="font-medium text-amber-400">Informação</p>
              </div>
              <p className="text-text-secondary text-sm">
                A Carta de Correção permite corrigir erros de preenchimento, exceto dados que alterem valores ou identificação do emitente/destinatário.
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Texto da Correção (mínimo 15 caracteres)
              </label>
              <textarea
                className="w-full h-32 px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary placeholder-text-muted resize-none focus:outline-none focus:border-accent-primary"
                placeholder='Exemplo: Onde se lê "10 unidades" leia-se "12 unidades"'
              />
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowCorrectionModal(false)}>
                Cancelar
              </Button>
              <Button>
                Enviar CC-e
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
