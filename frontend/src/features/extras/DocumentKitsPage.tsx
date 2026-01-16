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
import {
  Package,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  FileText,
  FolderOpen,
  Copy,
  Trash2,
  Edit,
  Eye,
  CheckCircle,
  Clock,
  AlertTriangle,
  Users,
  Building,
  Calendar,
  Send,
  MoreVertical,
  File,
  FilePlus,
  Settings,
  Archive,
  Star,
  TrendingUp
} from 'lucide-react';
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
  Legend
} from 'recharts';

// ==================== TYPES ====================

interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'docx' | 'xlsx' | 'template';
  description: string;
  required: boolean;
  variables: string[];
  createdAt: string;
  updatedAt: string;
}

interface DocumentKit {
  id: string;
  name: string;
  description: string;
  category: 'admissao' | 'demissao' | 'ferias' | 'promocao' | 'cliente' | 'fornecedor' | 'operacional' | 'compliance';
  status: 'active' | 'inactive' | 'draft';
  documents: Document[];
  documentCount: number;
  downloads: number;
  lastUsed: string | null;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  tags: string[];
  isFavorite: boolean;
}

interface KitGeneration {
  id: string;
  kitId: string;
  kitName: string;
  targetType: 'employee' | 'client' | 'supplier' | 'contract';
  targetId: string;
  targetName: string;
  status: 'pending' | 'generating' | 'completed' | 'failed' | 'sent';
  documentsGenerated: number;
  totalDocuments: number;
  requestedBy: string;
  requestedAt: string;
  completedAt: string | null;
  sentAt: string | null;
  downloadUrl: string | null;
  errorMessage: string | null;
}

interface KitTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  documentCount: number;
  usageCount: number;
  isSystem: boolean;
}

interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
}

// ==================== CONSTANTS ====================

const CATEGORIES: Record<string, { label: string; color: string }> = {
  admissao: { label: 'Admissão', color: 'success' },
  demissao: { label: 'Demissão', color: 'danger' },
  ferias: { label: 'Férias', color: 'info' },
  promocao: { label: 'Promoção', color: 'primary' },
  cliente: { label: 'Cliente', color: 'warning' },
  fornecedor: { label: 'Fornecedor', color: 'neutral' },
  operacional: { label: 'Operacional', color: 'info' },
  compliance: { label: 'Compliance', color: 'primary' }
};

const DOCUMENT_TYPES: Record<string, { label: string; icon: string }> = {
  pdf: { label: 'PDF', icon: 'file-text' },
  docx: { label: 'Word', icon: 'file' },
  xlsx: { label: 'Excel', icon: 'file-spreadsheet' },
  template: { label: 'Template', icon: 'file-code' }
};

// ==================== MOCK DATA ====================

const mockKits: DocumentKit[] = [
  {
    id: 'KIT001',
    name: 'Kit Admissão CLT',
    description: 'Documentos completos para admissão de funcionários CLT',
    category: 'admissao',
    status: 'active',
    documents: [],
    documentCount: 12,
    downloads: 456,
    lastUsed: '2024-01-15T10:30:00',
    createdBy: 'Maria Santos',
    createdAt: '2023-06-01T08:00:00',
    updatedAt: '2024-01-10T14:20:00',
    tags: ['CLT', 'RH', 'Obrigatório'],
    isFavorite: true
  },
  {
    id: 'KIT002',
    name: 'Kit Demissão Padrão',
    description: 'Documentos para processo de desligamento',
    category: 'demissao',
    status: 'active',
    documents: [],
    documentCount: 8,
    downloads: 234,
    lastUsed: '2024-01-14T16:45:00',
    createdBy: 'João Silva',
    createdAt: '2023-07-15T09:30:00',
    updatedAt: '2024-01-08T11:00:00',
    tags: ['Desligamento', 'RH'],
    isFavorite: false
  },
  {
    id: 'KIT003',
    name: 'Kit Férias Anual',
    description: 'Documentos para solicitação e concessão de férias',
    category: 'ferias',
    status: 'active',
    documents: [],
    documentCount: 5,
    downloads: 789,
    lastUsed: '2024-01-15T09:00:00',
    createdBy: 'Ana Costa',
    createdAt: '2023-05-20T10:00:00',
    updatedAt: '2024-01-12T15:30:00',
    tags: ['Férias', 'RH', 'Anual'],
    isFavorite: true
  },
  {
    id: 'KIT004',
    name: 'Kit Onboarding Cliente',
    description: 'Documentos para cadastro de novos clientes',
    category: 'cliente',
    status: 'active',
    documents: [],
    documentCount: 7,
    downloads: 345,
    lastUsed: '2024-01-13T11:20:00',
    createdBy: 'Pedro Lima',
    createdAt: '2023-08-10T14:00:00',
    updatedAt: '2024-01-05T16:45:00',
    tags: ['Cliente', 'Comercial', 'Contrato'],
    isFavorite: false
  },
  {
    id: 'KIT005',
    name: 'Kit Promoção/Transferência',
    description: 'Documentos para promoção ou transferência de funcionários',
    category: 'promocao',
    status: 'active',
    documents: [],
    documentCount: 6,
    downloads: 123,
    lastUsed: '2024-01-10T14:30:00',
    createdBy: 'Maria Santos',
    createdAt: '2023-09-05T08:30:00',
    updatedAt: '2024-01-03T09:15:00',
    tags: ['Promoção', 'RH', 'Carreira'],
    isFavorite: false
  },
  {
    id: 'KIT006',
    name: 'Kit Compliance LGPD',
    description: 'Documentos de conformidade com LGPD',
    category: 'compliance',
    status: 'active',
    documents: [],
    documentCount: 10,
    downloads: 567,
    lastUsed: '2024-01-14T10:00:00',
    createdBy: 'Carlos Oliveira',
    createdAt: '2023-04-12T11:00:00',
    updatedAt: '2024-01-11T13:20:00',
    tags: ['LGPD', 'Compliance', 'Legal'],
    isFavorite: true
  },
  {
    id: 'KIT007',
    name: 'Kit Fornecedor Homologação',
    description: 'Documentos para homologação de fornecedores',
    category: 'fornecedor',
    status: 'active',
    documents: [],
    documentCount: 9,
    downloads: 189,
    lastUsed: '2024-01-12T15:00:00',
    createdBy: 'Ana Costa',
    createdAt: '2023-10-01T09:00:00',
    updatedAt: '2024-01-07T10:30:00',
    tags: ['Fornecedor', 'Compras', 'Homologação'],
    isFavorite: false
  },
  {
    id: 'KIT008',
    name: 'Kit Operacional Campo',
    description: 'Documentos operacionais para equipes de campo',
    category: 'operacional',
    status: 'draft',
    documents: [],
    documentCount: 4,
    downloads: 45,
    lastUsed: null,
    createdBy: 'João Silva',
    createdAt: '2024-01-05T14:00:00',
    updatedAt: '2024-01-15T08:00:00',
    tags: ['Operacional', 'Campo'],
    isFavorite: false
  }
];

const mockDocuments: Document[] = [
  {
    id: 'DOC001',
    name: 'Contrato de Trabalho CLT',
    type: 'template',
    description: 'Modelo de contrato de trabalho padrão CLT',
    required: true,
    variables: ['nome', 'cpf', 'cargo', 'salario', 'dataAdmissao'],
    createdAt: '2023-06-01T08:00:00',
    updatedAt: '2024-01-10T14:20:00'
  },
  {
    id: 'DOC002',
    name: 'Ficha de Registro',
    type: 'template',
    description: 'Ficha de registro do funcionário',
    required: true,
    variables: ['nome', 'cpf', 'rg', 'endereco', 'telefone'],
    createdAt: '2023-06-01T08:00:00',
    updatedAt: '2024-01-10T14:20:00'
  },
  {
    id: 'DOC003',
    name: 'Termo de Confidencialidade',
    type: 'template',
    description: 'Acordo de confidencialidade e sigilo',
    required: true,
    variables: ['nome', 'cpf', 'cargo'],
    createdAt: '2023-06-01T08:00:00',
    updatedAt: '2024-01-10T14:20:00'
  },
  {
    id: 'DOC004',
    name: 'Declaração de Dependentes',
    type: 'template',
    description: 'Declaração de dependentes para IR',
    required: false,
    variables: ['nome', 'dependentes'],
    createdAt: '2023-06-01T08:00:00',
    updatedAt: '2024-01-10T14:20:00'
  },
  {
    id: 'DOC005',
    name: 'Manual do Colaborador',
    type: 'pdf',
    description: 'Manual com políticas e procedimentos',
    required: false,
    variables: [],
    createdAt: '2023-06-01T08:00:00',
    updatedAt: '2024-01-10T14:20:00'
  }
];

const mockGenerations: KitGeneration[] = [
  {
    id: 'GEN001',
    kitId: 'KIT001',
    kitName: 'Kit Admissão CLT',
    targetType: 'employee',
    targetId: 'EMP001',
    targetName: 'Ana Paula Silva',
    status: 'completed',
    documentsGenerated: 12,
    totalDocuments: 12,
    requestedBy: 'Maria Santos',
    requestedAt: '2024-01-15T10:00:00',
    completedAt: '2024-01-15T10:05:00',
    sentAt: '2024-01-15T10:10:00',
    downloadUrl: '/downloads/kit-admissao-ana-silva.zip',
    errorMessage: null
  },
  {
    id: 'GEN002',
    kitId: 'KIT003',
    kitName: 'Kit Férias Anual',
    targetType: 'employee',
    targetId: 'EMP045',
    targetName: 'Carlos Mendes',
    status: 'generating',
    documentsGenerated: 3,
    totalDocuments: 5,
    requestedBy: 'Ana Costa',
    requestedAt: '2024-01-15T09:30:00',
    completedAt: null,
    sentAt: null,
    downloadUrl: null,
    errorMessage: null
  },
  {
    id: 'GEN003',
    kitId: 'KIT004',
    kitName: 'Kit Onboarding Cliente',
    targetType: 'client',
    targetId: 'CLI023',
    targetName: 'Empresa ABC Ltda',
    status: 'pending',
    documentsGenerated: 0,
    totalDocuments: 7,
    requestedBy: 'Pedro Lima',
    requestedAt: '2024-01-15T11:00:00',
    completedAt: null,
    sentAt: null,
    downloadUrl: null,
    errorMessage: null
  },
  {
    id: 'GEN004',
    kitId: 'KIT002',
    kitName: 'Kit Demissão Padrão',
    targetType: 'employee',
    targetId: 'EMP089',
    targetName: 'Roberto Alves',
    status: 'failed',
    documentsGenerated: 5,
    totalDocuments: 8,
    requestedBy: 'João Silva',
    requestedAt: '2024-01-14T16:00:00',
    completedAt: null,
    sentAt: null,
    downloadUrl: null,
    errorMessage: 'Erro ao gerar documento: Dados incompletos do funcionário'
  },
  {
    id: 'GEN005',
    kitId: 'KIT006',
    kitName: 'Kit Compliance LGPD',
    targetType: 'client',
    targetId: 'CLI045',
    targetName: 'Tech Solutions SA',
    status: 'sent',
    documentsGenerated: 10,
    totalDocuments: 10,
    requestedBy: 'Carlos Oliveira',
    requestedAt: '2024-01-14T14:00:00',
    completedAt: '2024-01-14T14:08:00',
    sentAt: '2024-01-14T14:15:00',
    downloadUrl: '/downloads/kit-lgpd-tech-solutions.zip',
    errorMessage: null
  }
];

const mockTemplates: KitTemplate[] = [
  {
    id: 'TPL001',
    name: 'Admissão CLT Padrão',
    category: 'admissao',
    description: 'Template padrão para admissão CLT com todos os documentos obrigatórios',
    documentCount: 12,
    usageCount: 156,
    isSystem: true
  },
  {
    id: 'TPL002',
    name: 'Admissão PJ',
    category: 'admissao',
    description: 'Template para contratação de prestadores de serviço PJ',
    documentCount: 6,
    usageCount: 78,
    isSystem: true
  },
  {
    id: 'TPL003',
    name: 'Desligamento Sem Justa Causa',
    category: 'demissao',
    description: 'Template completo para desligamento sem justa causa',
    documentCount: 10,
    usageCount: 89,
    isSystem: true
  },
  {
    id: 'TPL004',
    name: 'Desligamento Por Acordo',
    category: 'demissao',
    description: 'Template para rescisão por acordo mútuo',
    documentCount: 8,
    usageCount: 34,
    isSystem: true
  },
  {
    id: 'TPL005',
    name: 'Onboarding Cliente Premium',
    category: 'cliente',
    description: 'Kit completo para clientes premium',
    documentCount: 15,
    usageCount: 45,
    isSystem: false
  }
];

// ==================== CHART DATA ====================

const categoryDistributionData = [
  { name: 'Admissão', value: 8, color: '#10b981' },
  { name: 'Demissão', value: 4, color: '#ef4444' },
  { name: 'Férias', value: 3, color: '#3b82f6' },
  { name: 'Compliance', value: 5, color: '#6366f1' },
  { name: 'Cliente', value: 4, color: '#f59e0b' }
];

const downloadsWeeklyData = [
  { day: 'Seg', downloads: 45 },
  { day: 'Ter', downloads: 67 },
  { day: 'Qua', downloads: 52 },
  { day: 'Qui', downloads: 89 },
  { day: 'Sex', downloads: 78 },
  { day: 'Sáb', downloads: 23 },
  { day: 'Dom', downloads: 12 }
];

const monthlyUsageData = [
  { month: 'Jul', kits: 120, docs: 890 },
  { month: 'Ago', kits: 145, docs: 1020 },
  { month: 'Set', kits: 134, docs: 956 },
  { month: 'Out', kits: 167, docs: 1234 },
  { month: 'Nov', kits: 189, docs: 1456 },
  { month: 'Dez', kits: 156, docs: 1123 },
  { month: 'Jan', kits: 178, docs: 1345 }
];

const topKitsData = [
  { name: 'Kit Férias', downloads: 789 },
  { name: 'Kit Compliance LGPD', downloads: 567 },
  { name: 'Kit Admissão CLT', downloads: 456 },
  { name: 'Kit Onboarding', downloads: 345 },
  { name: 'Kit Demissão', downloads: 234 }
];

// ==================== HELPERS ====================

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR');
};

const formatDateTime = (dateString: string | null) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('pt-BR');
};

const getStatusBadge = (status: DocumentKit['status']) => {
  const config: Record<string, { variant: any; label: string }> = {
    active: { variant: 'success', label: 'Ativo' },
    inactive: { variant: 'neutral', label: 'Inativo' },
    draft: { variant: 'warning', label: 'Rascunho' }
  };
  const { variant, label } = config[status] || { variant: 'neutral', label: status };
  return <Badge variant={variant}>{label}</Badge>;
};

const getGenerationStatusBadge = (status: KitGeneration['status']) => {
  const config: Record<string, { variant: any; label: string }> = {
    pending: { variant: 'warning', label: 'Pendente' },
    generating: { variant: 'info', label: 'Gerando...' },
    completed: { variant: 'success', label: 'Concluído' },
    failed: { variant: 'danger', label: 'Falhou' },
    sent: { variant: 'primary', label: 'Enviado' }
  };
  const { variant, label } = config[status] || { variant: 'neutral', label: status };
  return <Badge variant={variant}>{label}</Badge>;
};

const getCategoryBadge = (category: string) => {
  const config = CATEGORIES[category];
  if (!config) return <Badge variant="neutral">{category}</Badge>;
  return <Badge variant={config.color as any}>{config.label}</Badge>;
};

// ==================== COMPONENT ====================

export function DocumentKitsPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Modals
  const [showKitModal, setShowKitModal] = useState(false);
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showNewKitModal, setShowNewKitModal] = useState(false);
  const [showNewDocumentModal, setShowNewDocumentModal] = useState(false);

  const [selectedKit, setSelectedKit] = useState<DocumentKit | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [selectedGeneration, setSelectedGeneration] = useState<KitGeneration | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<KitTemplate | null>(null);

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Package className="h-4 w-4" /> },
    { value: 'kits', label: 'Kits', icon: <FolderOpen className="h-4 w-4" /> },
    { value: 'documents', label: 'Documentos', icon: <FileText className="h-4 w-4" /> },
    { value: 'generations', label: 'Gerações', icon: <Copy className="h-4 w-4" /> },
    { value: 'templates', label: 'Templates', icon: <File className="h-4 w-4" /> }
  ];

  // Filter kits
  const filteredKits = mockKits.filter(kit => {
    const matchesSearch = kit.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         kit.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || kit.category === categoryFilter;
    const matchesStatus = statusFilter === 'all' || kit.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Filter documents
  const filteredDocuments = mockDocuments.filter(doc => {
    return doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           doc.description.toLowerCase().includes(searchTerm.toLowerCase());
  });

  // Columns
  const kitColumns: Column<DocumentKit>[] = [
    {
      key: 'name',
      header: 'Kit',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${row.isFavorite ? 'bg-yellow-500/20' : 'bg-bg-tertiary'}`}>
            {row.isFavorite ? (
              <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
            ) : (
              <Package className="h-5 w-5 text-accent-primary" />
            )}
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.description.substring(0, 50)}...</p>
          </div>
        </div>
      )
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => getCategoryBadge(row.category)
    },
    {
      key: 'documents',
      header: 'Documentos',
      render: (row) => (
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-text-secondary" />
          <span>{row.documentCount}</span>
        </div>
      )
    },
    {
      key: 'downloads',
      header: 'Downloads',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Download className="h-4 w-4 text-text-secondary" />
          <span>{row.downloads}</span>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
    },
    {
      key: 'lastUsed',
      header: 'Último Uso',
      render: (row) => (
        <span className="text-text-secondary">
          {row.lastUsed ? formatDateTime(row.lastUsed) : 'Nunca'}
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
            onClick={() => {
              setSelectedKit(row);
              setShowKitModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedKit(row);
              setShowGenerateModal(true);
            }}
          >
            <Copy className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const documentColumns: Column<Document>[] = [
    {
      key: 'name',
      header: 'Documento',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-bg-tertiary">
            <FileText className="h-5 w-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.description.substring(0, 40)}...</p>
          </div>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        <Badge variant="outline">{DOCUMENT_TYPES[row.type]?.label || row.type}</Badge>
      )
    },
    {
      key: 'required',
      header: 'Obrigatório',
      render: (row) => (
        row.required ? (
          <Badge variant="danger">Sim</Badge>
        ) : (
          <Badge variant="neutral">Não</Badge>
        )
      )
    },
    {
      key: 'variables',
      header: 'Variáveis',
      render: (row) => (
        <span className="text-text-secondary">
          {row.variables.length > 0 ? row.variables.length + ' variáveis' : 'Estático'}
        </span>
      )
    },
    {
      key: 'updatedAt',
      header: 'Atualizado',
      render: (row) => (
        <span className="text-text-secondary">{formatDate(row.updatedAt)}</span>
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
            onClick={() => {
              setSelectedDocument(row);
              setShowDocumentModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const generationColumns: Column<KitGeneration>[] = [
    {
      key: 'kit',
      header: 'Kit',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.kitName}</p>
          <p className="text-sm text-text-secondary">ID: {row.id}</p>
        </div>
      )
    },
    {
      key: 'target',
      header: 'Destinatário',
      render: (row) => (
        <div className="flex items-center gap-2">
          {row.targetType === 'employee' ? (
            <Users className="h-4 w-4 text-text-secondary" />
          ) : (
            <Building className="h-4 w-4 text-text-secondary" />
          )}
          <div>
            <p className="text-text-primary">{row.targetName}</p>
            <p className="text-xs text-text-secondary capitalize">{row.targetType}</p>
          </div>
        </div>
      )
    },
    {
      key: 'progress',
      header: 'Progresso',
      render: (row) => (
        <div className="w-32">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-text-secondary">{row.documentsGenerated}/{row.totalDocuments}</span>
            <span className="text-text-secondary">
              {Math.round((row.documentsGenerated / row.totalDocuments) * 100)}%
            </span>
          </div>
          <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                row.status === 'failed' ? 'bg-accent-danger' :
                row.status === 'completed' || row.status === 'sent' ? 'bg-accent-success' :
                'bg-accent-primary'
              }`}
              style={{ width: `${(row.documentsGenerated / row.totalDocuments) * 100}%` }}
            />
          </div>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getGenerationStatusBadge(row.status)
    },
    {
      key: 'requestedAt',
      header: 'Solicitado',
      render: (row) => (
        <div>
          <p className="text-text-primary">{formatDateTime(row.requestedAt)}</p>
          <p className="text-xs text-text-secondary">por {row.requestedBy}</p>
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-2">
          {row.status === 'completed' && row.downloadUrl && (
            <Button variant="ghost" size="sm">
              <Download className="h-4 w-4" />
            </Button>
          )}
          {row.status === 'completed' && !row.sentAt && (
            <Button variant="ghost" size="sm">
              <Send className="h-4 w-4" />
            </Button>
          )}
          {row.status === 'failed' && (
            <Button variant="ghost" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  const templateColumns: Column<KitTemplate>[] = [
    {
      key: 'name',
      header: 'Template',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${row.isSystem ? 'bg-accent-primary/20' : 'bg-bg-tertiary'}`}>
            <File className="h-5 w-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary">{row.description.substring(0, 40)}...</p>
          </div>
        </div>
      )
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => getCategoryBadge(row.category)
    },
    {
      key: 'documents',
      header: 'Documentos',
      render: (row) => (
        <span>{row.documentCount} documentos</span>
      )
    },
    {
      key: 'usage',
      header: 'Uso',
      render: (row) => (
        <span>{row.usageCount} vezes</span>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => (
        row.isSystem ? (
          <Badge variant="primary">Sistema</Badge>
        ) : (
          <Badge variant="outline">Customizado</Badge>
        )
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
            onClick={() => {
              setSelectedTemplate(row);
              setShowTemplateModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Copy className="h-4 w-4" />
          </Button>
          {!row.isSystem && (
            <Button variant="ghost" size="sm">
              <Edit className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Kits de Documentos
            </h1>
            <p className="text-text-secondary mt-1">
              Pacotes de documentos pré-configurados para processos empresariais
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => setShowNewDocumentModal(true)}>
              <FilePlus className="h-4 w-4 mr-2" />
              Novo Documento
            </Button>
            <Button onClick={() => setShowNewKitModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Kit
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Kits Ativos"
            value={mockKits.filter(k => k.status === 'active').length.toString()}
            icon={<Package className="h-5 w-5" />}
            iconColor="primary"
            change="+3"
            changeLabel="este mês"
          />
          <StatCard
            title="Documentos"
            value={mockDocuments.length.toString()}
            icon={<FileText className="h-5 w-5" />}
            iconColor="info"
            change="+12"
            changeLabel="novos"
          />
          <StatCard
            title="Downloads Hoje"
            value="89"
            icon={<Download className="h-5 w-5" />}
            iconColor="success"
            change="+15%"
            changeLabel="vs ontem"
          />
          <StatCard
            title="Gerações Pendentes"
            value={mockGenerations.filter(g => g.status === 'pending' || g.status === 'generating').length.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Category Distribution */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Distribuição por Categoria
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={categoryDistributionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {categoryDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Card>

              {/* Weekly Downloads */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Downloads da Semana
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={downloadsWeeklyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Bar dataKey="downloads" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Second Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Monthly Usage Trend */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Tendência de Uso Mensal
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={monthlyUsageData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="kits"
                      name="Kits Gerados"
                      stroke="#6366f1"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="docs"
                      name="Documentos"
                      stroke="#10b981"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>

              {/* Top Kits */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Kits Mais Utilizados
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={topKitsData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" width={120} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Bar dataKey="downloads" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Atividade Recente
                </h3>
                <Button variant="ghost" size="sm">
                  Ver Todas
                </Button>
              </div>
              <div className="space-y-4">
                {mockGenerations.slice(0, 4).map((gen) => (
                  <div
                    key={gen.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-bg-tertiary"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${
                        gen.status === 'completed' || gen.status === 'sent' ? 'bg-accent-success/20' :
                        gen.status === 'failed' ? 'bg-accent-danger/20' :
                        'bg-accent-primary/20'
                      }`}>
                        {gen.status === 'completed' || gen.status === 'sent' ? (
                          <CheckCircle className="h-5 w-5 text-accent-success" />
                        ) : gen.status === 'failed' ? (
                          <AlertTriangle className="h-5 w-5 text-accent-danger" />
                        ) : (
                          <Clock className="h-5 w-5 text-accent-primary" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{gen.kitName}</p>
                        <p className="text-sm text-text-secondary">
                          Para: {gen.targetName} • {formatDateTime(gen.requestedAt)}
                        </p>
                      </div>
                    </div>
                    {getGenerationStatusBadge(gen.status)}
                  </div>
                ))}
              </div>
            </Card>

            {/* Favorite Kits */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Kits Favoritos
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {mockKits.filter(k => k.isFavorite).map((kit) => (
                  <div
                    key={kit.id}
                    className="p-4 rounded-lg bg-bg-tertiary border border-border-subtle hover:border-accent-primary transition-colors cursor-pointer"
                    onClick={() => {
                      setSelectedKit(kit);
                      setShowKitModal(true);
                    }}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-2 rounded-lg bg-yellow-500/20">
                        <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                      </div>
                      {getCategoryBadge(kit.category)}
                    </div>
                    <h4 className="font-semibold text-text-primary mb-1">{kit.name}</h4>
                    <p className="text-sm text-text-secondary mb-3">
                      {kit.description.substring(0, 60)}...
                    </p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-text-secondary">
                        <FileText className="h-4 w-4 inline mr-1" />
                        {kit.documentCount} docs
                      </span>
                      <span className="text-text-secondary">
                        <Download className="h-4 w-4 inline mr-1" />
                        {kit.downloads}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'kits' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar kits..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                options={[
                  { value: 'all', label: 'Todas Categorias' },
                  ...Object.entries(CATEGORIES).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))
                ]}
                value={categoryFilter}
                onChange={setCategoryFilter}
              />
              <Select
                options={[
                  { value: 'all', label: 'Todos Status' },
                  { value: 'active', label: 'Ativo' },
                  { value: 'inactive', label: 'Inativo' },
                  { value: 'draft', label: 'Rascunho' }
                ]}
                value={statusFilter}
                onChange={setStatusFilter}
              />
            </div>

            <DataTable
              data={filteredKits}
              columns={kitColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'documents' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar documentos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>

            <DataTable
              data={filteredDocuments}
              columns={documentColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'generations' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-text-primary">
                Histórico de Gerações
              </h3>
              <Button variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Atualizar
              </Button>
            </div>

            <DataTable
              data={mockGenerations}
              columns={generationColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'templates' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4 flex-1">
                <Input
                  placeholder="Buscar templates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-md"
                />
              </div>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Novo Template
              </Button>
            </div>

            <DataTable
              data={mockTemplates}
              columns={templateColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Kit Detail Modal */}
        <Modal
          isOpen={showKitModal}
          onClose={() => setShowKitModal(false)}
          title="Detalhes do Kit"
          size="lg"
        >
          {selectedKit && (
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-lg ${selectedKit.isFavorite ? 'bg-yellow-500/20' : 'bg-accent-primary/20'}`}>
                    {selectedKit.isFavorite ? (
                      <Star className="h-8 w-8 text-yellow-500 fill-yellow-500" />
                    ) : (
                      <Package className="h-8 w-8 text-accent-primary" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedKit.name}</h3>
                    <p className="text-text-secondary">{selectedKit.description}</p>
                  </div>
                </div>
                {getStatusBadge(selectedKit.status)}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Categoria</p>
                  <div className="mt-1">{getCategoryBadge(selectedKit.category)}</div>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Documentos</p>
                  <p className="text-xl font-semibold text-text-primary mt-1">{selectedKit.documentCount}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Downloads</p>
                  <p className="text-xl font-semibold text-text-primary mt-1">{selectedKit.downloads}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Último Uso</p>
                  <p className="text-sm font-medium text-text-primary mt-1">
                    {selectedKit.lastUsed ? formatDateTime(selectedKit.lastUsed) : 'Nunca'}
                  </p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-text-primary mb-3">Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedKit.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">{tag}</Badge>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-text-primary mb-3">Documentos Incluídos</h4>
                <div className="space-y-2">
                  {mockDocuments.slice(0, selectedKit.documentCount).map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-bg-tertiary"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-accent-primary" />
                        <div>
                          <p className="font-medium text-text-primary">{doc.name}</p>
                          <p className="text-sm text-text-secondary">{doc.type.toUpperCase()}</p>
                        </div>
                      </div>
                      {doc.required && <Badge variant="danger">Obrigatório</Badge>}
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-text-secondary">Criado por</p>
                  <p className="text-text-primary">{selectedKit.createdBy}</p>
                </div>
                <div>
                  <p className="text-text-secondary">Criado em</p>
                  <p className="text-text-primary">{formatDate(selectedKit.createdAt)}</p>
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button className="flex-1" onClick={() => {
                  setShowKitModal(false);
                  setShowGenerateModal(true);
                }}>
                  <Copy className="h-4 w-4 mr-2" />
                  Gerar Kit
                </Button>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Exportar
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Document Detail Modal */}
        <Modal
          isOpen={showDocumentModal}
          onClose={() => setShowDocumentModal(false)}
          title="Detalhes do Documento"
          size="md"
        >
          {selectedDocument && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-accent-primary/20">
                  <FileText className="h-8 w-8 text-accent-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedDocument.name}</h3>
                  <p className="text-text-secondary">{selectedDocument.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Tipo</p>
                  <p className="text-lg font-semibold text-text-primary mt-1">
                    {DOCUMENT_TYPES[selectedDocument.type]?.label}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Obrigatório</p>
                  <p className="mt-1">
                    {selectedDocument.required ? (
                      <Badge variant="danger">Sim</Badge>
                    ) : (
                      <Badge variant="neutral">Não</Badge>
                    )}
                  </p>
                </div>
              </div>

              {selectedDocument.variables.length > 0 && (
                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Variáveis do Template</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedDocument.variables.map((variable, index) => (
                      <code
                        key={index}
                        className="px-2 py-1 rounded bg-bg-tertiary text-accent-primary text-sm"
                      >
                        {`{{${variable}}}`}
                      </code>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-text-secondary">Criado em</p>
                  <p className="text-text-primary">{formatDate(selectedDocument.createdAt)}</p>
                </div>
                <div>
                  <p className="text-text-secondary">Atualizado em</p>
                  <p className="text-text-primary">{formatDate(selectedDocument.updatedAt)}</p>
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" className="flex-1">
                  <Eye className="h-4 w-4 mr-2" />
                  Visualizar
                </Button>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Generate Kit Modal */}
        <Modal
          isOpen={showGenerateModal}
          onClose={() => setShowGenerateModal(false)}
          title="Gerar Kit de Documentos"
          size="md"
        >
          {selectedKit && (
            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-bg-tertiary">
                <div className="flex items-center gap-3 mb-2">
                  <Package className="h-5 w-5 text-accent-primary" />
                  <span className="font-semibold text-text-primary">{selectedKit.name}</span>
                </div>
                <p className="text-sm text-text-secondary">
                  {selectedKit.documentCount} documentos serão gerados
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Tipo de Destinatário
                  </label>
                  <Select
                    options={[
                      { value: 'employee', label: 'Funcionário' },
                      { value: 'client', label: 'Cliente' },
                      { value: 'supplier', label: 'Fornecedor' },
                      { value: 'contract', label: 'Contrato' }
                    ]}
                    value="employee"
                    onChange={() => {}}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Selecionar Destinatário
                  </label>
                  <Select
                    options={[
                      { value: 'emp1', label: 'Ana Paula Silva' },
                      { value: 'emp2', label: 'Carlos Mendes' },
                      { value: 'emp3', label: 'Maria Santos' }
                    ]}
                    value=""
                    onChange={() => {}}
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input type="checkbox" id="sendEmail" className="rounded" />
                  <label htmlFor="sendEmail" className="text-sm text-text-primary">
                    Enviar por email após geração
                  </label>
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button className="flex-1">
                  <Copy className="h-4 w-4 mr-2" />
                  Gerar Kit
                </Button>
                <Button variant="outline" onClick={() => setShowGenerateModal(false)}>
                  Cancelar
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New Kit Modal */}
        <Modal
          isOpen={showNewKitModal}
          onClose={() => setShowNewKitModal(false)}
          title="Criar Novo Kit"
          size="lg"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Nome do Kit
                </label>
                <Input placeholder="Ex: Kit Admissão Temporário" />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Descrição
                </label>
                <textarea
                  className="w-full px-4 py-2 rounded-lg bg-bg-tertiary border border-border-default text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-primary"
                  rows={3}
                  placeholder="Descreva o propósito deste kit..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Categoria
                </label>
                <Select
                  options={Object.entries(CATEGORIES).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))}
                  value="admissao"
                  onChange={() => {}}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Baseado em Template
                </label>
                <Select
                  options={[
                    { value: '', label: 'Nenhum (criar do zero)' },
                    ...mockTemplates.map(t => ({ value: t.id, label: t.name }))
                  ]}
                  value=""
                  onChange={() => {}}
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Tags
                </label>
                <Input placeholder="Separe tags por vírgula..." />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Adicionar Documentos
              </label>
              <div className="border-2 border-dashed border-border-default rounded-lg p-8 text-center">
                <FilePlus className="h-12 w-12 text-text-secondary mx-auto mb-3" />
                <p className="text-text-secondary mb-2">
                  Arraste documentos aqui ou clique para selecionar
                </p>
                <Button variant="outline" size="sm">
                  Selecionar Documentos
                </Button>
              </div>
            </div>

            <div className="flex gap-3 pt-4 border-t border-border-subtle">
              <Button className="flex-1">
                <Plus className="h-4 w-4 mr-2" />
                Criar Kit
              </Button>
              <Button variant="outline" onClick={() => setShowNewKitModal(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>

        {/* New Document Modal */}
        <Modal
          isOpen={showNewDocumentModal}
          onClose={() => setShowNewDocumentModal(false)}
          title="Adicionar Documento"
          size="md"
        >
          <div className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Nome do Documento
                </label>
                <Input placeholder="Ex: Termo de Responsabilidade" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Descrição
                </label>
                <textarea
                  className="w-full px-4 py-2 rounded-lg bg-bg-tertiary border border-border-default text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-primary"
                  rows={2}
                  placeholder="Descreva o documento..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Tipo
                </label>
                <Select
                  options={[
                    { value: 'template', label: 'Template (com variáveis)' },
                    { value: 'pdf', label: 'PDF Estático' },
                    { value: 'docx', label: 'Documento Word' },
                    { value: 'xlsx', label: 'Planilha Excel' }
                  ]}
                  value="template"
                  onChange={() => {}}
                />
              </div>

              <div className="flex items-center gap-2">
                <input type="checkbox" id="required" className="rounded" />
                <label htmlFor="required" className="text-sm text-text-primary">
                  Documento obrigatório
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Arquivo
                </label>
                <div className="border-2 border-dashed border-border-default rounded-lg p-6 text-center">
                  <File className="h-10 w-10 text-text-secondary mx-auto mb-2" />
                  <p className="text-text-secondary text-sm mb-2">
                    Arraste o arquivo ou clique para selecionar
                  </p>
                  <Button variant="outline" size="sm">
                    Selecionar Arquivo
                  </Button>
                </div>
              </div>
            </div>

            <div className="flex gap-3 pt-4 border-t border-border-subtle">
              <Button className="flex-1">
                <Plus className="h-4 w-4 mr-2" />
                Adicionar
              </Button>
              <Button variant="outline" onClick={() => setShowNewDocumentModal(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>

        {/* Template Detail Modal */}
        <Modal
          isOpen={showTemplateModal}
          onClose={() => setShowTemplateModal(false)}
          title="Detalhes do Template"
          size="md"
        >
          {selectedTemplate && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${selectedTemplate.isSystem ? 'bg-accent-primary/20' : 'bg-bg-tertiary'}`}>
                  <File className="h-8 w-8 text-accent-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedTemplate.name}</h3>
                  <p className="text-text-secondary">{selectedTemplate.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Categoria</p>
                  <div className="mt-1">{getCategoryBadge(selectedTemplate.category)}</div>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Tipo</p>
                  <p className="mt-1">
                    {selectedTemplate.isSystem ? (
                      <Badge variant="primary">Sistema</Badge>
                    ) : (
                      <Badge variant="outline">Customizado</Badge>
                    )}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Documentos</p>
                  <p className="text-xl font-semibold text-text-primary mt-1">{selectedTemplate.documentCount}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Vezes Usado</p>
                  <p className="text-xl font-semibold text-text-primary mt-1">{selectedTemplate.usageCount}</p>
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button className="flex-1">
                  <Copy className="h-4 w-4 mr-2" />
                  Usar Template
                </Button>
                {!selectedTemplate.isSystem && (
                  <Button variant="outline">
                    <Edit className="h-4 w-4 mr-2" />
                    Editar
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
