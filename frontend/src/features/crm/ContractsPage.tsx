'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  FileText,
  Calendar,
  DollarSign,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Download,
  Eye,
  Edit,
  TrendingUp,
  Building2,
  Users,
  FileSignature,
  History,
  Settings,
  BarChart3,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  X,
  Trash2,
  Copy,
  Send,
  Printer,
  Link,
  Paperclip,
  MessageSquare,
  Phone,
  Mail,
  MapPin,
  Shield,
  Briefcase,
  Target,
  Percent,
  ChevronRight,
  ExternalLink,
  AlertCircle,
  Info,
  MoreVertical,
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
  PieChart as RechartsPie,
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
interface ContractService {
  id: string;
  name: string;
  description: string;
  quantity: number;
  unitValue: number;
  totalValue: number;
}

interface ContractContact {
  id: string;
  name: string;
  role: string;
  email: string;
  phone: string;
  isPrimary: boolean;
}

interface ContractAmendment {
  id: string;
  number: string;
  type: 'additive' | 'amendment' | 'termination';
  description: string;
  valueChange: number;
  effectiveDate: string;
  status: 'draft' | 'pending' | 'signed';
  createdAt: string;
}

interface ContractActivity {
  id: string;
  type: 'created' | 'signed' | 'amended' | 'renewed' | 'suspended' | 'note' | 'payment';
  title: string;
  description: string;
  createdAt: string;
  createdBy: string;
}

interface Contract {
  id: string;
  number: string;
  client: string;
  clientLogo?: string;
  clientCnpj: string;
  type: string;
  category: 'security' | 'cleaning' | 'maintenance' | 'facilities' | 'mixed';
  value: number;
  status: 'draft' | 'pending_signature' | 'active' | 'suspended' | 'terminated' | 'expired';
  startDate: string;
  endDate: string | null;
  autoRenewal: boolean;
  renewalPeriod: number; // months
  adjustmentIndex: string;
  adjustmentPercentage: number;
  nextAdjustment: string | null;
  slaScore: number;
  paymentTerms: string;
  invoiceDay: number;
  address: string;
  manager: string;
  managerEmail: string;
  employeeCount: number;
  services: ContractService[];
  contacts: ContractContact[];
  amendments: ContractAmendment[];
  activities: ContractActivity[];
  notes: string;
  createdAt: string;
  updatedAt: string;
}

// Mock Data - Comprehensive contracts
const contracts: Contract[] = [
  {
    id: '1',
    number: 'CONT-2026-0001',
    client: 'Condomínio Aurora',
    clientCnpj: '12.345.678/0001-90',
    type: 'Segurança 24h',
    category: 'security',
    value: 45000,
    status: 'active',
    startDate: '2025-06-01',
    endDate: '2026-06-01',
    autoRenewal: true,
    renewalPeriod: 12,
    adjustmentIndex: 'IGPM',
    adjustmentPercentage: 4.5,
    nextAdjustment: '2026-06-01',
    slaScore: 98,
    paymentTerms: 'Boleto 30 dias',
    invoiceDay: 5,
    address: 'Av. Paulista, 1000 - São Paulo/SP',
    manager: 'Carlos Silva',
    managerEmail: 'carlos.silva@conectaplus.com.br',
    employeeCount: 12,
    services: [
      { id: '1', name: 'Vigilância Armada', description: 'Posto 24h com vigilante armado', quantity: 4, unitValue: 8500, totalValue: 34000 },
      { id: '2', name: 'Ronda Motorizada', description: 'Rondas a cada 2h', quantity: 1, unitValue: 5000, totalValue: 5000 },
      { id: '3', name: 'Monitoramento CFTV', description: '24 câmeras monitoradas', quantity: 1, unitValue: 6000, totalValue: 6000 },
    ],
    contacts: [
      { id: '1', name: 'João Mendes', role: 'Síndico', email: 'joao@aurora.com.br', phone: '(11) 99999-1111', isPrimary: true },
      { id: '2', name: 'Maria Santos', role: 'Subsíndica', email: 'maria@aurora.com.br', phone: '(11) 99999-2222', isPrimary: false },
    ],
    amendments: [
      { id: '1', number: 'ADIT-2025-0001', type: 'additive', description: 'Inclusão de posto adicional', valueChange: 8500, effectiveDate: '2025-09-01', status: 'signed', createdAt: '2025-08-15' },
    ],
    activities: [
      { id: '1', type: 'created', title: 'Contrato criado', description: 'Contrato inicial criado e enviado para assinatura', createdAt: '2025-05-15T10:00:00', createdBy: 'Admin' },
      { id: '2', type: 'signed', title: 'Contrato assinado', description: 'Assinatura digital realizada por ambas as partes', createdAt: '2025-05-28T14:30:00', createdBy: 'Sistema' },
      { id: '3', type: 'amended', title: 'Aditivo aprovado', description: 'Aditivo ADIT-2025-0001 assinado', createdAt: '2025-08-20T09:15:00', createdBy: 'Carlos Silva' },
    ],
    notes: 'Cliente prioritário. Atenção especial em eventos no salão de festas.',
    createdAt: '2025-05-15',
    updatedAt: '2025-12-10',
  },
  {
    id: '2',
    number: 'CONT-2026-0002',
    client: 'Shopping Center Norte',
    clientCnpj: '23.456.789/0001-01',
    type: 'Facilities',
    category: 'facilities',
    value: 128000,
    status: 'active',
    startDate: '2025-03-15',
    endDate: '2027-03-15',
    autoRenewal: true,
    renewalPeriod: 24,
    adjustmentIndex: 'IPCA',
    adjustmentPercentage: 4.2,
    nextAdjustment: '2026-03-15',
    slaScore: 95,
    paymentTerms: 'Boleto 45 dias',
    invoiceDay: 10,
    address: 'Av. Brasil, 500 - São Paulo/SP',
    manager: 'Ana Costa',
    managerEmail: 'ana.costa@conectaplus.com.br',
    employeeCount: 45,
    services: [
      { id: '1', name: 'Limpeza Geral', description: 'Limpeza de áreas comuns', quantity: 20, unitValue: 3000, totalValue: 60000 },
      { id: '2', name: 'Segurança', description: 'Postos de vigilância', quantity: 8, unitValue: 5500, totalValue: 44000 },
      { id: '3', name: 'Manutenção Predial', description: 'Equipe técnica', quantity: 4, unitValue: 6000, totalValue: 24000 },
    ],
    contacts: [
      { id: '1', name: 'Roberto Lima', role: 'Gerente Operacional', email: 'roberto@scn.com.br', phone: '(11) 99888-3333', isPrimary: true },
    ],
    amendments: [],
    activities: [
      { id: '1', type: 'created', title: 'Contrato criado', description: 'Novo contrato de facilities', createdAt: '2025-03-01T10:00:00', createdBy: 'Admin' },
      { id: '2', type: 'signed', title: 'Contrato assinado', description: 'Assinatura concluída', createdAt: '2025-03-10T16:00:00', createdBy: 'Sistema' },
    ],
    notes: 'Contrato estratégico. Reunião mensal obrigatória.',
    createdAt: '2025-03-01',
    updatedAt: '2025-12-01',
  },
  {
    id: '3',
    number: 'CONT-2026-0003',
    client: 'Hospital São Lucas',
    clientCnpj: '34.567.890/0001-12',
    type: 'Segurança + Limpeza',
    category: 'mixed',
    value: 185000,
    status: 'pending_signature',
    startDate: '2026-02-01',
    endDate: '2028-02-01',
    autoRenewal: false,
    renewalPeriod: 0,
    adjustmentIndex: 'IGPM',
    adjustmentPercentage: 0,
    nextAdjustment: null,
    slaScore: 0,
    paymentTerms: 'Boleto 30 dias',
    invoiceDay: 15,
    address: 'Rua das Flores, 200 - São Paulo/SP',
    manager: 'Pedro Alves',
    managerEmail: 'pedro.alves@conectaplus.com.br',
    employeeCount: 0,
    services: [
      { id: '1', name: 'Segurança Hospitalar', description: 'Equipe especializada', quantity: 10, unitValue: 9500, totalValue: 95000 },
      { id: '2', name: 'Limpeza Hospitalar', description: 'Equipe técnica com treinamento', quantity: 15, unitValue: 6000, totalValue: 90000 },
    ],
    contacts: [
      { id: '1', name: 'Dr. Fernando Melo', role: 'Diretor Administrativo', email: 'fernando@hsl.com.br', phone: '(11) 99777-4444', isPrimary: true },
    ],
    amendments: [],
    activities: [
      { id: '1', type: 'created', title: 'Proposta enviada', description: 'Proposta comercial convertida em contrato', createdAt: '2026-01-10T10:00:00', createdBy: 'Admin' },
    ],
    notes: 'Aguardando análise jurídica do cliente.',
    createdAt: '2026-01-10',
    updatedAt: '2026-01-15',
  },
  {
    id: '4',
    number: 'CONT-2025-0089',
    client: 'Universidade Federal',
    clientCnpj: '45.678.901/0001-23',
    type: 'Portaria',
    category: 'security',
    value: 67000,
    status: 'expired',
    startDate: '2024-01-01',
    endDate: '2025-12-31',
    autoRenewal: false,
    renewalPeriod: 0,
    adjustmentIndex: 'IPCA',
    adjustmentPercentage: 5.8,
    nextAdjustment: null,
    slaScore: 92,
    paymentTerms: 'Empenho',
    invoiceDay: 1,
    address: 'Campus Universitário - São Paulo/SP',
    manager: 'Marcos Souza',
    managerEmail: 'marcos.souza@conectaplus.com.br',
    employeeCount: 18,
    services: [
      { id: '1', name: 'Portaria', description: 'Controle de acesso', quantity: 6, unitValue: 7500, totalValue: 45000 },
      { id: '2', name: 'Vigilância', description: 'Rondas no campus', quantity: 4, unitValue: 5500, totalValue: 22000 },
    ],
    contacts: [
      { id: '1', name: 'Prof. Ricardo Gomes', role: 'Pró-Reitor', email: 'ricardo@uf.edu.br', phone: '(11) 99666-5555', isPrimary: true },
    ],
    amendments: [],
    activities: [
      { id: '1', type: 'created', title: 'Licitação vencida', description: 'Contrato assinado após pregão', createdAt: '2023-12-15T10:00:00', createdBy: 'Admin' },
      { id: '2', type: 'note', title: 'Renovação não prevista', description: 'Cliente informou nova licitação', createdAt: '2025-11-01T09:00:00', createdBy: 'Marcos Souza' },
    ],
    notes: 'Contrato público via licitação. Não renovável automaticamente.',
    createdAt: '2023-12-15',
    updatedAt: '2025-12-31',
  },
  {
    id: '5',
    number: 'CONT-2026-0004',
    client: 'Tech Park Empresarial',
    clientCnpj: '56.789.012/0001-34',
    type: 'Manutenção Predial',
    category: 'maintenance',
    value: 54000,
    status: 'active',
    startDate: '2025-09-01',
    endDate: null,
    autoRenewal: true,
    renewalPeriod: 12,
    adjustmentIndex: 'IGPM',
    adjustmentPercentage: 4.8,
    nextAdjustment: '2026-09-01',
    slaScore: 100,
    paymentTerms: 'Boleto 30 dias',
    invoiceDay: 20,
    address: 'Av. das Nações, 1500 - São Paulo/SP',
    manager: 'Julia Ferreira',
    managerEmail: 'julia.ferreira@conectaplus.com.br',
    employeeCount: 8,
    services: [
      { id: '1', name: 'Manutenção Elétrica', description: 'Equipe eletricista', quantity: 2, unitValue: 12000, totalValue: 24000 },
      { id: '2', name: 'Manutenção Hidráulica', description: 'Equipe hidráulica', quantity: 2, unitValue: 10000, totalValue: 20000 },
      { id: '3', name: 'Manutenção Geral', description: 'Serviços diversos', quantity: 2, unitValue: 5000, totalValue: 10000 },
    ],
    contacts: [
      { id: '1', name: 'Eduardo Ramos', role: 'Facilities Manager', email: 'eduardo@techpark.com.br', phone: '(11) 99555-6666', isPrimary: true },
    ],
    amendments: [],
    activities: [
      { id: '1', type: 'created', title: 'Contrato criado', description: 'Novo contrato de manutenção', createdAt: '2025-08-20T10:00:00', createdBy: 'Admin' },
      { id: '2', type: 'signed', title: 'Contrato assinado', description: 'Assinatura digital concluída', createdAt: '2025-08-25T11:30:00', createdBy: 'Sistema' },
    ],
    notes: 'Contrato por prazo indeterminado com rescisão mediante aviso de 90 dias.',
    createdAt: '2025-08-20',
    updatedAt: '2025-12-01',
  },
  {
    id: '6',
    number: 'CONT-2026-0005',
    client: 'Banco Metropolitano',
    clientCnpj: '67.890.123/0001-45',
    type: 'Segurança Bancária',
    category: 'security',
    value: 220000,
    status: 'active',
    startDate: '2025-01-01',
    endDate: '2027-12-31',
    autoRenewal: true,
    renewalPeriod: 36,
    adjustmentIndex: 'IPCA',
    adjustmentPercentage: 4.5,
    nextAdjustment: '2026-01-01',
    slaScore: 99,
    paymentTerms: 'Boleto 45 dias',
    invoiceDay: 1,
    address: 'Av. Faria Lima, 2000 - São Paulo/SP',
    manager: 'Ricardo Nunes',
    managerEmail: 'ricardo.nunes@conectaplus.com.br',
    employeeCount: 32,
    services: [
      { id: '1', name: 'Vigilância Armada', description: 'Agências e matriz', quantity: 15, unitValue: 9000, totalValue: 135000 },
      { id: '2', name: 'Escolta de Valores', description: 'Transporte de numerário', quantity: 5, unitValue: 12000, totalValue: 60000 },
      { id: '3', name: 'Monitoramento', description: 'Central 24h', quantity: 1, unitValue: 25000, totalValue: 25000 },
    ],
    contacts: [
      { id: '1', name: 'André Machado', role: 'Gerente de Segurança', email: 'andre@bancometro.com.br', phone: '(11) 99444-7777', isPrimary: true },
    ],
    amendments: [],
    activities: [
      { id: '1', type: 'created', title: 'Contrato criado', description: 'Contrato bancário premium', createdAt: '2024-12-01T10:00:00', createdBy: 'Admin' },
      { id: '2', type: 'signed', title: 'Contrato assinado', description: 'Assinatura em cartório', createdAt: '2024-12-20T14:00:00', createdBy: 'Sistema' },
    ],
    notes: 'Cliente VIP. Atendimento prioritário. Reuniões quinzenais.',
    createdAt: '2024-12-01',
    updatedAt: '2026-01-10',
  },
  {
    id: '7',
    number: 'CONT-2026-0006',
    client: 'Indústria Metalúrgica ABC',
    clientCnpj: '78.901.234/0001-56',
    type: 'Limpeza Industrial',
    category: 'cleaning',
    value: 89000,
    status: 'suspended',
    startDate: '2024-06-01',
    endDate: '2026-06-01',
    autoRenewal: true,
    renewalPeriod: 12,
    adjustmentIndex: 'IGPM',
    adjustmentPercentage: 5.2,
    nextAdjustment: null,
    slaScore: 78,
    paymentTerms: 'Boleto 30 dias',
    invoiceDay: 10,
    address: 'Rod. Anhanguera, Km 45 - São Paulo/SP',
    manager: 'Fernanda Lima',
    managerEmail: 'fernanda.lima@conectaplus.com.br',
    employeeCount: 22,
    services: [
      { id: '1', name: 'Limpeza Industrial', description: 'Área fabril', quantity: 15, unitValue: 4500, totalValue: 67500 },
      { id: '2', name: 'Limpeza Administrativa', description: 'Escritórios', quantity: 5, unitValue: 3500, totalValue: 17500 },
      { id: '3', name: 'Tratamento de Piso', description: 'Piso industrial', quantity: 1, unitValue: 4000, totalValue: 4000 },
    ],
    contacts: [
      { id: '1', name: 'Paulo César', role: 'Gerente de Produção', email: 'paulo@metalabc.com.br', phone: '(11) 99333-8888', isPrimary: true },
    ],
    amendments: [],
    activities: [
      { id: '1', type: 'created', title: 'Contrato criado', description: 'Novo contrato industrial', createdAt: '2024-05-15T10:00:00', createdBy: 'Admin' },
      { id: '2', type: 'suspended', title: 'Contrato suspenso', description: 'Cliente solicitou suspensão por 60 dias devido a parada de produção', createdAt: '2025-12-01T09:00:00', createdBy: 'Fernanda Lima' },
    ],
    notes: 'ATENÇÃO: Contrato suspenso desde 01/12/2025. Retorno previsto para 01/02/2026.',
    createdAt: '2024-05-15',
    updatedAt: '2025-12-01',
  },
];

const statusConfig = {
  draft: { label: 'Rascunho', color: 'neutral' as const, icon: FileText },
  pending_signature: { label: 'Aguard. Assinatura', color: 'warning' as const, icon: Clock },
  active: { label: 'Ativo', color: 'success' as const, icon: CheckCircle2 },
  suspended: { label: 'Suspenso', color: 'danger' as const, icon: AlertTriangle },
  terminated: { label: 'Encerrado', color: 'neutral' as const, icon: XCircle },
  expired: { label: 'Expirado', color: 'warning' as const, icon: RefreshCw },
};

const categoryConfig = {
  security: { label: 'Segurança', color: 'primary' as const },
  cleaning: { label: 'Limpeza', color: 'info' as const },
  maintenance: { label: 'Manutenção', color: 'warning' as const },
  facilities: { label: 'Facilities', color: 'success' as const },
  mixed: { label: 'Misto', color: 'secondary' as const },
};

// Chart data
const contractsByCategory = [
  { name: 'Segurança', value: 3, total: 332000, color: '#6366f1' },
  { name: 'Facilities', value: 1, total: 128000, color: '#10b981' },
  { name: 'Limpeza', value: 1, total: 89000, color: '#3b82f6' },
  { name: 'Manutenção', value: 1, total: 54000, color: '#f59e0b' },
  { name: 'Misto', value: 1, total: 185000, color: '#8b5cf6' },
];

const monthlyRevenue = [
  { month: 'Jul', recorrente: 580000, avulso: 45000 },
  { month: 'Ago', recorrente: 634000, avulso: 38000 },
  { month: 'Set', recorrente: 688000, avulso: 52000 },
  { month: 'Out', recorrente: 699000, avulso: 41000 },
  { month: 'Nov', recorrente: 699000, avulso: 48000 },
  { month: 'Dez', recorrente: 610000, avulso: 55000 },
  { month: 'Jan', recorrente: 699000, avulso: 42000 },
];

const slaHistory = [
  { month: 'Jul', sla: 94 },
  { month: 'Ago', sla: 95 },
  { month: 'Set', sla: 96 },
  { month: 'Out', sla: 97 },
  { month: 'Nov', sla: 96 },
  { month: 'Dez', sla: 95 },
  { month: 'Jan', sla: 97 },
];

const renewalSchedule = [
  { month: 'Fev', count: 1, value: 45000 },
  { month: 'Mar', count: 1, value: 128000 },
  { month: 'Abr', count: 0, value: 0 },
  { month: 'Mai', count: 0, value: 0 },
  { month: 'Jun', count: 1, value: 45000 },
  { month: 'Jul', count: 0, value: 0 },
];

export function ContractsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [mainTab, setMainTab] = useState('contracts');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [showRenewalModal, setShowRenewalModal] = useState(false);
  const [showAmendmentModal, setShowAmendmentModal] = useState(false);
  const [detailTab, setDetailTab] = useState('overview');

  // Filtered contracts
  const filteredContracts = useMemo(() => {
    return contracts.filter((contract) => {
      const matchesSearch =
        contract.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contract.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contract.type.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTab = selectedTab === 'all' || contract.status === selectedTab;
      const matchesStatus = !statusFilter || contract.status === statusFilter;
      const matchesCategory = !categoryFilter || contract.category === categoryFilter;
      return matchesSearch && matchesTab && matchesStatus && matchesCategory;
    });
  }, [searchTerm, selectedTab, statusFilter, categoryFilter]);

  // Statistics
  const stats = useMemo(() => {
    const activeContracts = contracts.filter((c) => c.status === 'active');
    const totalValue = activeContracts.reduce((acc, c) => acc + c.value, 0);
    const avgSla = activeContracts.length > 0
      ? Math.round(activeContracts.reduce((acc, c) => acc + c.slaScore, 0) / activeContracts.length)
      : 0;
    const expiringCount = contracts.filter(
      (c) => c.status === 'active' && c.endDate && new Date(c.endDate) < new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
    ).length;
    const pendingCount = contracts.filter((c) => c.status === 'pending_signature').length;
    const suspendedCount = contracts.filter((c) => c.status === 'suspended').length;
    const employeeTotal = activeContracts.reduce((acc, c) => acc + c.employeeCount, 0);

    return { activeContracts, totalValue, avgSla, expiringCount, pendingCount, suspendedCount, employeeTotal };
  }, []);

  // Table columns
  const columns: Column<Contract>[] = [
    {
      key: 'number',
      header: 'Contrato',
      render: (row) => (
        <div>
          <p className="font-mono text-sm font-medium text-accent-primary">{row.number}</p>
          <p className="text-xs text-text-muted">{row.type}</p>
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
            <p className="text-xs text-text-muted">{row.clientCnpj}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => {
        const config = categoryConfig[row.category];
        return <Badge variant={config.color} size="sm">{config.label}</Badge>;
      },
    },
    {
      key: 'value',
      header: 'Valor Mensal',
      sortable: true,
      render: (row) => (
        <span className="font-mono text-text-primary">
          {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
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
      key: 'period',
      header: 'Vigência',
      render: (row) => (
        <div className="text-sm">
          <p className="text-text-primary">
            {new Date(row.startDate).toLocaleDateString('pt-BR')}
          </p>
          <p className="text-text-muted">
            até {row.endDate ? new Date(row.endDate).toLocaleDateString('pt-BR') : 'Indeterminado'}
          </p>
        </div>
      ),
    },
    {
      key: 'slaScore',
      header: 'SLA',
      sortable: true,
      render: (row) => (
        row.slaScore > 0 ? (
          <div className="flex items-center gap-2">
            <div className="w-12 h-2 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  row.slaScore >= 95 ? 'bg-success' : row.slaScore >= 80 ? 'bg-warning' : 'bg-danger'
                }`}
                style={{ width: `${row.slaScore}%` }}
              />
            </div>
            <span className="text-sm font-medium">{row.slaScore}%</span>
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
            onClick={(e) => {
              e.stopPropagation();
              setSelectedContract(row);
              setShowDetailModal(true);
            }}
          >
            <Eye className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon-sm">
            <Edit className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon-sm">
            <Download className="w-4 h-4" />
          </Button>
        </div>
      ),
    },
  ];

  // Open contract detail
  const openContractDetail = (contract: Contract) => {
    setSelectedContract(contract);
    setDetailTab('overview');
    setShowDetailModal(true);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Contratos
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão completa de contratos com renovação automática e SLA
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
              Novo Contrato
            </Button>
          </div>
        </div>

        {/* Main Tabs */}
        <SimpleTabBar
          tabs={[
            { value: 'contracts', label: 'Contratos', icon: <FileText className="w-4 h-4" /> },
            { value: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
            { value: 'renewals', label: 'Renovações', icon: <RefreshCw className="w-4 h-4" /> },
          ]}
          value={mainTab}
          onChange={setMainTab}
        />

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Contratos Ativos"
              value={stats.activeContracts.length}
              change={8}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <StatCard
              title="Receita Mensal"
              value={stats.totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              change={12.5}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="SLA Médio"
              value={`${stats.avgSla}%`}
              change={2.1}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <StatCard
              title="Colaboradores Alocados"
              value={stats.employeeTotal}
              icon={<Users className="w-6 h-6" />}
              iconColor="secondary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Renovação em 90 dias"
              value={stats.expiringCount}
              icon={<RefreshCw className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
          >
            <StatCard
              title="Aguard. Assinatura"
              value={stats.pendingCount}
              icon={<FileSignature className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </div>

        {/* Contracts Tab */}
        {mainTab === 'contracts' && (
          <>
            {/* Filters */}
            <Card>
              <CardBody className="py-4">
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <SimpleTabBar
                    tabs={[
                      { value: 'all', label: `Todos (${contracts.length})` },
                      { value: 'active', label: `Ativos (${contracts.filter(c => c.status === 'active').length})` },
                      { value: 'pending_signature', label: `Pendentes (${contracts.filter(c => c.status === 'pending_signature').length})` },
                      { value: 'suspended', label: `Suspensos (${contracts.filter(c => c.status === 'suspended').length})` },
                      { value: 'expired', label: `Expirados (${contracts.filter(c => c.status === 'expired').length})` },
                    ]}
                    value={selectedTab}
                    onChange={setSelectedTab}
                    variant="pills"
                  />
                  <div className="flex items-center gap-3">
                    <Input
                      placeholder="Buscar contratos..."
                      leftIcon={<Search className="w-4 h-4" />}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-64"
                    />
                    <Select
                      options={[
                        { value: '', label: 'Todas categorias' },
                        { value: 'security', label: 'Segurança' },
                        { value: 'cleaning', label: 'Limpeza' },
                        { value: 'maintenance', label: 'Manutenção' },
                        { value: 'facilities', label: 'Facilities' },
                        { value: 'mixed', label: 'Misto' },
                      ]}
                      value={categoryFilter}
                      onChange={setCategoryFilter}
                      className="w-40"
                    />
                    <Button variant="outline" leftIcon={<Filter className="w-4 h-4" />}>
                      Mais Filtros
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Contracts Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card>
                <CardBody className="p-0">
                  <DataTable
                    columns={columns}
                    data={filteredContracts}
                    keyExtractor={(row) => row.id}
                    onRowClick={openContractDetail}
                  />
                </CardBody>
              </Card>
            </motion.div>

            {/* Alerts */}
            {(stats.expiringCount > 0 || stats.suspendedCount > 0) && (
              <div className="space-y-4">
                {stats.expiringCount > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Card className="border-warning/30 bg-warning/5">
                      <CardBody>
                        <div className="flex items-center gap-4">
                          <div className="p-3 rounded-xl bg-warning/10">
                            <AlertTriangle className="w-6 h-6 text-warning" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-text-primary">
                              {stats.expiringCount} contrato(s) vencem nos próximos 90 dias
                            </p>
                            <p className="text-sm text-text-secondary mt-1">
                              Revise os contratos e inicie o processo de renovação
                            </p>
                          </div>
                          <Button variant="outline" size="sm" onClick={() => setMainTab('renewals')}>
                            Ver Renovações
                          </Button>
                        </div>
                      </CardBody>
                    </Card>
                  </motion.div>
                )}

                {stats.suspendedCount > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Card className="border-danger/30 bg-danger/5">
                      <CardBody>
                        <div className="flex items-center gap-4">
                          <div className="p-3 rounded-xl bg-danger/10">
                            <AlertCircle className="w-6 h-6 text-danger" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-text-primary">
                              {stats.suspendedCount} contrato(s) suspenso(s)
                            </p>
                            <p className="text-sm text-text-secondary mt-1">
                              Verifique a situação e tome as providências necessárias
                            </p>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedTab('suspended')}
                          >
                            Ver Suspensos
                          </Button>
                        </div>
                      </CardBody>
                    </Card>
                  </motion.div>
                )}
              </div>
            )}
          </>
        )}

        {/* Analytics Tab */}
        {mainTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Chart */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Receita Mensal</h3>
                    <p className="text-sm text-text-secondary">Recorrente vs Avulso</p>
                  </div>
                  <Badge variant="success">+12.5%</Badge>
                </div>
              </CardHeader>
              <CardBody>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={monthlyRevenue}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${(v/1000)}K`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      formatter={(value: number) => [value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }), '']}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="recorrente"
                      name="Recorrente"
                      stackId="1"
                      stroke="#6366f1"
                      fill="#6366f1"
                      fillOpacity={0.6}
                    />
                    <Area
                      type="monotone"
                      dataKey="avulso"
                      name="Avulso"
                      stackId="1"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>

            {/* Contracts by Category */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Contratos por Categoria</h3>
                    <p className="text-sm text-text-secondary">Distribuição atual</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="flex items-center gap-6">
                  <div className="w-48 h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPie>
                        <Pie
                          data={contractsByCategory}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          dataKey="value"
                        >
                          {contractsByCategory.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                        />
                      </RechartsPie>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex-1 space-y-3">
                    {contractsByCategory.map((cat) => (
                      <div key={cat.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                          <span className="text-sm text-text-secondary">{cat.name}</span>
                        </div>
                        <div className="text-right">
                          <span className="text-sm font-medium text-text-primary">{cat.value}</span>
                          <span className="text-xs text-text-muted ml-2">
                            {cat.total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* SLA History */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Histórico de SLA</h3>
                    <p className="text-sm text-text-secondary">Últimos 7 meses</p>
                  </div>
                  <Badge variant="success">97% atual</Badge>
                </div>
              </CardHeader>
              <CardBody>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={slaHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} domain={[80, 100]} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="sla"
                      name="SLA %"
                      stroke="#6366f1"
                      strokeWidth={2}
                      dot={{ fill: '#6366f1', strokeWidth: 2 }}
                    />
                    {/* Target line */}
                    <Line
                      type="monotone"
                      dataKey={() => 95}
                      name="Meta"
                      stroke="#f59e0b"
                      strokeDasharray="5 5"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>

            {/* Top Contracts */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Maiores Contratos</h3>
                    <p className="text-sm text-text-secondary">Por valor mensal</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {contracts
                    .filter(c => c.status === 'active')
                    .sort((a, b) => b.value - a.value)
                    .slice(0, 5)
                    .map((contract, index) => (
                      <div
                        key={contract.id}
                        className="flex items-center gap-4 p-3 rounded-lg bg-bg-tertiary hover:bg-bg-hover transition-colors cursor-pointer"
                        onClick={() => openContractDetail(contract)}
                      >
                        <div className="w-8 h-8 rounded-full bg-accent-primary/10 flex items-center justify-center">
                          <span className="text-sm font-bold text-accent-primary">{index + 1}</span>
                        </div>
                        <Avatar name={contract.client} size="sm" />
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{contract.client}</p>
                          <p className="text-xs text-text-muted">{contract.type}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono font-medium text-text-primary">
                            {contract.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                          <p className="text-xs text-text-muted">/mês</p>
                        </div>
                      </div>
                    ))}
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Renewals Tab */}
        {mainTab === 'renewals' && (
          <div className="space-y-6">
            {/* Renewal Schedule Chart */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Calendário de Renovações</h3>
                    <p className="text-sm text-text-secondary">Próximos 6 meses</p>
                  </div>
                  <Button variant="outline" size="sm" leftIcon={<Download className="w-4 h-4" />}>
                    Exportar
                  </Button>
                </div>
              </CardHeader>
              <CardBody>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={renewalSchedule}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis yAxisId="left" stroke="#64748b" fontSize={12} />
                    <YAxis yAxisId="right" orientation="right" stroke="#64748b" fontSize={12} tickFormatter={(v) => `${(v/1000)}K`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      formatter={(value: number, name: string) => [
                        name === 'value'
                          ? value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                          : value,
                        name === 'value' ? 'Valor' : 'Contratos'
                      ]}
                    />
                    <Bar yAxisId="left" dataKey="count" name="Contratos" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar yAxisId="right" dataKey="value" name="Valor" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>

            {/* Upcoming Renewals */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Próximas Renovações</h3>
                    <p className="text-sm text-text-secondary">Contratos que vencem em até 90 dias</p>
                  </div>
                </div>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  {contracts
                    .filter(c => c.status === 'active' && c.endDate)
                    .sort((a, b) => new Date(a.endDate!).getTime() - new Date(b.endDate!).getTime())
                    .slice(0, 5)
                    .map((contract) => {
                      const daysLeft = Math.ceil((new Date(contract.endDate!).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
                      const urgency = daysLeft <= 30 ? 'danger' : daysLeft <= 60 ? 'warning' : 'info';

                      return (
                        <div
                          key={contract.id}
                          className="flex items-center gap-4 p-4 rounded-lg bg-bg-tertiary hover:bg-bg-hover transition-colors cursor-pointer"
                          onClick={() => openContractDetail(contract)}
                        >
                          <Avatar name={contract.client} size="md" />
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-text-primary">{contract.client}</p>
                              <Badge variant={urgency} size="sm">
                                {daysLeft} dias
                              </Badge>
                            </div>
                            <p className="text-sm text-text-secondary">{contract.number} • {contract.type}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-mono font-medium text-text-primary">
                              {contract.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </p>
                            <p className="text-xs text-text-muted">
                              Vence em {new Date(contract.endDate!).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {contract.autoRenewal ? (
                              <Badge variant="success" size="sm">
                                <RefreshCw className="w-3 h-3 mr-1" />
                                Auto
                              </Badge>
                            ) : (
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedContract(contract);
                                  setShowRenewalModal(true);
                                }}
                              >
                                Renovar
                              </Button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                </div>
              </CardBody>
            </Card>

            {/* Auto-Renewal Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-success/5 border-success/20">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-success/10">
                      <RefreshCw className="w-6 h-6 text-success" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-text-primary">
                        {contracts.filter(c => c.status === 'active' && c.autoRenewal).length}
                      </p>
                      <p className="text-sm text-text-secondary">Renovação Automática</p>
                    </div>
                  </div>
                </CardBody>
              </Card>

              <Card className="bg-warning/5 border-warning/20">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-warning/10">
                      <Clock className="w-6 h-6 text-warning" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-text-primary">
                        {contracts.filter(c => c.status === 'active' && !c.autoRenewal).length}
                      </p>
                      <p className="text-sm text-text-secondary">Renovação Manual</p>
                    </div>
                  </div>
                </CardBody>
              </Card>

              <Card className="bg-info/5 border-info/20">
                <CardBody>
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-info/10">
                      <Calendar className="w-6 h-6 text-info" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-text-primary">
                        {contracts.filter(c => c.status === 'active' && !c.endDate).length}
                      </p>
                      <p className="text-sm text-text-secondary">Prazo Indeterminado</p>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
          </div>
        )}

        {/* Contract Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedContract?.number || 'Detalhes do Contrato'}
          size="xl"
        >
          {selectedContract && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedContract.client} size="lg" />
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedContract.client}</h3>
                    <p className="text-sm text-text-secondary">{selectedContract.clientCnpj}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={statusConfig[selectedContract.status].color}>
                        {statusConfig[selectedContract.status].label}
                      </Badge>
                      <Badge variant={categoryConfig[selectedContract.category].color}>
                        {categoryConfig[selectedContract.category].label}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-accent-primary">
                    {selectedContract.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </p>
                  <p className="text-sm text-text-muted">/mês</p>
                </div>
              </div>

              {/* Detail Tabs */}
              <SimpleTabBar
                tabs={[
                  { value: 'overview', label: 'Visão Geral', icon: <FileText className="w-4 h-4" /> },
                  { value: 'services', label: 'Serviços', icon: <Briefcase className="w-4 h-4" /> },
                  { value: 'contacts', label: 'Contatos', icon: <Users className="w-4 h-4" /> },
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
                        <Calendar className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Vigência</span>
                      </div>
                      <p className="text-text-primary">
                        {new Date(selectedContract.startDate).toLocaleDateString('pt-BR')} até{' '}
                        {selectedContract.endDate
                          ? new Date(selectedContract.endDate).toLocaleDateString('pt-BR')
                          : 'Indeterminado'}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <RefreshCw className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Renovação</span>
                      </div>
                      <p className="text-text-primary">
                        {selectedContract.autoRenewal
                          ? `Automática a cada ${selectedContract.renewalPeriod} meses`
                          : 'Manual'}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Percent className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Reajuste</span>
                      </div>
                      <p className="text-text-primary">
                        Índice: {selectedContract.adjustmentIndex}
                        {selectedContract.nextAdjustment && (
                          <span className="text-text-muted ml-2">
                            (Próximo: {new Date(selectedContract.nextAdjustment).toLocaleDateString('pt-BR')})
                          </span>
                        )}
                      </p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <DollarSign className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Pagamento</span>
                      </div>
                      <p className="text-text-primary">
                        {selectedContract.paymentTerms} • Fatura dia {selectedContract.invoiceDay}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <MapPin className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Endereço</span>
                      </div>
                      <p className="text-text-primary">{selectedContract.address}</p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Colaboradores</span>
                      </div>
                      <p className="text-text-primary">{selectedContract.employeeCount} funcionários alocados</p>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Target className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">SLA</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-3 bg-bg-primary rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              selectedContract.slaScore >= 95 ? 'bg-success' :
                              selectedContract.slaScore >= 80 ? 'bg-warning' : 'bg-danger'
                            }`}
                            style={{ width: `${selectedContract.slaScore}%` }}
                          />
                        </div>
                        <span className="font-bold text-text-primary">{selectedContract.slaScore}%</span>
                      </div>
                    </div>

                    <div className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-center gap-2 mb-3">
                        <Shield className="w-4 h-4 text-text-muted" />
                        <span className="text-sm font-medium text-text-secondary">Gestor</span>
                      </div>
                      <p className="text-text-primary">{selectedContract.manager}</p>
                      <p className="text-sm text-text-muted">{selectedContract.managerEmail}</p>
                    </div>
                  </div>

                  {selectedContract.notes && (
                    <div className="col-span-2 p-4 rounded-lg bg-warning/5 border border-warning/20">
                      <div className="flex items-center gap-2 mb-2">
                        <Info className="w-4 h-4 text-warning" />
                        <span className="text-sm font-medium text-warning">Observações</span>
                      </div>
                      <p className="text-text-primary">{selectedContract.notes}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Services Tab */}
              {detailTab === 'services' && (
                <div className="space-y-4">
                  {selectedContract.services.map((service) => (
                    <div key={service.id} className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-text-primary">{service.name}</h4>
                          <p className="text-sm text-text-secondary mt-1">{service.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono font-bold text-accent-primary">
                            {service.totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                          <p className="text-xs text-text-muted">
                            {service.quantity}x {service.unitValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}

                  <div className="p-4 rounded-lg bg-accent-primary/10 border border-accent-primary/20">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-text-primary">Total Mensal</span>
                      <span className="text-xl font-bold text-accent-primary">
                        {selectedContract.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Contacts Tab */}
              {detailTab === 'contacts' && (
                <div className="space-y-4">
                  {selectedContract.contacts.map((contact) => (
                    <div key={contact.id} className="p-4 rounded-lg bg-bg-tertiary">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-4">
                          <Avatar name={contact.name} size="md" />
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium text-text-primary">{contact.name}</h4>
                              {contact.isPrimary && (
                                <Badge variant="primary" size="sm">Principal</Badge>
                              )}
                            </div>
                            <p className="text-sm text-text-secondary">{contact.role}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="icon-sm">
                            <Phone className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="icon-sm">
                            <Mail className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="mt-3 flex items-center gap-4 text-sm text-text-secondary">
                        <span className="flex items-center gap-1">
                          <Mail className="w-4 h-4" />
                          {contact.email}
                        </span>
                        <span className="flex items-center gap-1">
                          <Phone className="w-4 h-4" />
                          {contact.phone}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* History Tab */}
              {detailTab === 'history' && (
                <div className="space-y-4">
                  {selectedContract.activities.map((activity, index) => (
                    <div key={activity.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          activity.type === 'created' ? 'bg-info/10 text-info' :
                          activity.type === 'signed' ? 'bg-success/10 text-success' :
                          activity.type === 'amended' ? 'bg-warning/10 text-warning' :
                          activity.type === 'suspended' ? 'bg-danger/10 text-danger' :
                          'bg-bg-tertiary text-text-muted'
                        }`}>
                          {activity.type === 'created' && <Plus className="w-5 h-5" />}
                          {activity.type === 'signed' && <FileSignature className="w-5 h-5" />}
                          {activity.type === 'amended' && <Edit className="w-5 h-5" />}
                          {activity.type === 'suspended' && <AlertTriangle className="w-5 h-5" />}
                          {activity.type === 'note' && <MessageSquare className="w-5 h-5" />}
                          {activity.type === 'payment' && <DollarSign className="w-5 h-5" />}
                        </div>
                        {index < selectedContract.activities.length - 1 && (
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
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
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
                  {selectedContract.status === 'active' && (
                    <>
                      <Button
                        variant="outline"
                        leftIcon={<Plus className="w-4 h-4" />}
                        onClick={() => {
                          setShowDetailModal(false);
                          setShowAmendmentModal(true);
                        }}
                      >
                        Aditivo
                      </Button>
                      <Button
                        variant="primary"
                        leftIcon={<RefreshCw className="w-4 h-4" />}
                        onClick={() => {
                          setShowDetailModal(false);
                          setShowRenewalModal(true);
                        }}
                      >
                        Renovar
                      </Button>
                    </>
                  )}
                  {selectedContract.status === 'pending_signature' && (
                    <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                      Enviar para Assinatura
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}
        </Modal>

        {/* New Contract Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Novo Contrato"
          size="lg"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Cliente
                </label>
                <Select
                  options={[
                    { value: '', label: 'Selecione um cliente' },
                    { value: '1', label: 'Condomínio Aurora' },
                    { value: '2', label: 'Shopping Center Norte' },
                    { value: '3', label: 'Hospital São Lucas' },
                  ]}
                  value=""
                  onChange={() => {}}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Tipo de Contrato
                </label>
                <Select
                  options={[
                    { value: '', label: 'Selecione o tipo' },
                    { value: 'security', label: 'Segurança' },
                    { value: 'cleaning', label: 'Limpeza' },
                    { value: 'maintenance', label: 'Manutenção' },
                    { value: 'facilities', label: 'Facilities' },
                    { value: 'mixed', label: 'Misto' },
                  ]}
                  value=""
                  onChange={() => {}}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Data de Início
                </label>
                <Input type="date" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Data de Término
                </label>
                <Input type="date" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Valor Mensal
                </label>
                <Input placeholder="R$ 0,00" leftIcon={<DollarSign className="w-4 h-4" />} />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Índice de Reajuste
                </label>
                <Select
                  options={[
                    { value: 'IGPM', label: 'IGPM' },
                    { value: 'IPCA', label: 'IPCA' },
                    { value: 'INPC', label: 'INPC' },
                  ]}
                  value="IGPM"
                  onChange={() => {}}
                />
              </div>
            </div>

            <div className="p-4 rounded-lg bg-bg-tertiary">
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" className="w-5 h-5 rounded border-border-default bg-bg-primary text-accent-primary focus:ring-accent-primary" />
                <div>
                  <span className="text-text-primary font-medium">Renovação Automática</span>
                  <p className="text-sm text-text-muted">O contrato será renovado automaticamente ao final da vigência</p>
                </div>
              </label>
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
                Criar Contrato
              </Button>
            </div>
          </div>
        </Modal>

        {/* Renewal Modal */}
        <Modal
          isOpen={showRenewalModal}
          onClose={() => setShowRenewalModal(false)}
          title="Renovar Contrato"
          size="md"
        >
          {selectedContract && (
            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-bg-tertiary">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedContract.client} size="lg" />
                  <div>
                    <h4 className="font-medium text-text-primary">{selectedContract.client}</h4>
                    <p className="text-sm text-text-muted">{selectedContract.number}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    Nova Data de Término
                  </label>
                  <Input type="date" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    Período de Renovação
                  </label>
                  <Select
                    options={[
                      { value: '12', label: '12 meses' },
                      { value: '24', label: '24 meses' },
                      { value: '36', label: '36 meses' },
                    ]}
                    value="12"
                    onChange={() => {}}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Reajuste (%)
                </label>
                <div className="flex items-center gap-4">
                  <Input
                    placeholder="4.5"
                    leftIcon={<Percent className="w-4 h-4" />}
                    className="flex-1"
                  />
                  <Badge variant="info">
                    {selectedContract.adjustmentIndex}: +{selectedContract.adjustmentPercentage}%
                  </Badge>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-success/5 border border-success/20">
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">Novo Valor Mensal</span>
                  <span className="text-xl font-bold text-success">
                    {(selectedContract.value * 1.045).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                  </span>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowRenewalModal(false)}>
                  Cancelar
                </Button>
                <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />}>
                  Confirmar Renovação
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Amendment Modal */}
        <Modal
          isOpen={showAmendmentModal}
          onClose={() => setShowAmendmentModal(false)}
          title="Novo Aditivo"
          size="md"
        >
          {selectedContract && (
            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-bg-tertiary">
                <div className="flex items-center gap-4">
                  <Avatar name={selectedContract.client} size="lg" />
                  <div>
                    <h4 className="font-medium text-text-primary">{selectedContract.client}</h4>
                    <p className="text-sm text-text-muted">{selectedContract.number}</p>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Tipo de Aditivo
                </label>
                <Select
                  options={[
                    { value: 'additive', label: 'Aditivo de Serviços' },
                    { value: 'amendment', label: 'Alteração Contratual' },
                    { value: 'termination', label: 'Distrato' },
                  ]}
                  value="additive"
                  onChange={() => {}}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Descrição
                </label>
                <textarea
                  className="w-full px-4 py-3 bg-bg-tertiary border border-border-default rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary"
                  rows={3}
                  placeholder="Descreva as alterações do aditivo..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    Alteração no Valor
                  </label>
                  <Input placeholder="R$ 0,00" leftIcon={<DollarSign className="w-4 h-4" />} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    Data de Vigência
                  </label>
                  <Input type="date" />
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowAmendmentModal(false)}>
                  Cancelar
                </Button>
                <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
                  Criar Aditivo
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
