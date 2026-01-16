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
  Box,
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  Package,
  MapPin,
  User,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownLeft,
  ArrowLeftRight,
  Eye,
  Edit,
  Trash2,
  History,
  QrCode,
  Barcode,
  Truck,
  HardHat,
  Wrench,
  Shirt,
  Smartphone,
  CheckCircle,
  Clock,
  XCircle,
  TrendingUp,
  TrendingDown,
  Building
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
  Legend,
  AreaChart,
  Area
} from 'recharts';

// ==================== TYPES ====================

interface InventoryItem {
  id: string;
  code: string;
  name: string;
  description: string;
  category: 'epi' | 'ferramenta' | 'uniforme' | 'eletronico' | 'material' | 'veiculo';
  status: 'available' | 'in_use' | 'maintenance' | 'lost' | 'damaged';
  quantity: number;
  minQuantity: number;
  unitValue: number;
  totalValue: number;
  location: string;
  assignedTo: string | null;
  assignedToId: string | null;
  postId: string | null;
  postName: string | null;
  serialNumber: string | null;
  brand: string | null;
  model: string | null;
  purchaseDate: string | null;
  warrantyExpiry: string | null;
  lastMovement: string;
  createdAt: string;
  updatedAt: string;
}

interface Movement {
  id: string;
  itemId: string;
  itemName: string;
  itemCode: string;
  type: 'entrada' | 'saida' | 'transferencia' | 'baixa' | 'devolucao';
  quantity: number;
  fromLocation: string | null;
  toLocation: string | null;
  fromEmployee: string | null;
  toEmployee: string | null;
  reason: string;
  notes: string | null;
  performedBy: string;
  performedAt: string;
  documentNumber: string | null;
}

interface Location {
  id: string;
  name: string;
  type: 'almoxarifado' | 'posto' | 'veiculo' | 'colaborador';
  address: string | null;
  responsible: string;
  itemCount: number;
  totalValue: number;
  status: 'active' | 'inactive';
}

interface Alert {
  id: string;
  type: 'low_stock' | 'expiring_warranty' | 'overdue_return' | 'maintenance_due' | 'lost_item';
  itemId: string;
  itemName: string;
  itemCode: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  acknowledged: boolean;
  acknowledgedBy: string | null;
  acknowledgedAt: string | null;
}

interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
}

// ==================== CONSTANTS ====================

const CATEGORIES: Record<string, { label: string; icon: any; color: string }> = {
  epi: { label: 'EPI', icon: HardHat, color: 'warning' },
  ferramenta: { label: 'Ferramenta', icon: Wrench, color: 'info' },
  uniforme: { label: 'Uniforme', icon: Shirt, color: 'primary' },
  eletronico: { label: 'Eletrônico', icon: Smartphone, color: 'success' },
  material: { label: 'Material', icon: Package, color: 'neutral' },
  veiculo: { label: 'Veículo', icon: Truck, color: 'danger' }
};

const STATUS_CONFIG: Record<string, { label: string; variant: string }> = {
  available: { label: 'Disponível', variant: 'success' },
  in_use: { label: 'Em Uso', variant: 'info' },
  maintenance: { label: 'Manutenção', variant: 'warning' },
  lost: { label: 'Perdido', variant: 'danger' },
  damaged: { label: 'Danificado', variant: 'danger' }
};

const MOVEMENT_TYPES: Record<string, { label: string; icon: any; color: string }> = {
  entrada: { label: 'Entrada', icon: ArrowDownLeft, color: 'success' },
  saida: { label: 'Saída', icon: ArrowUpRight, color: 'warning' },
  transferencia: { label: 'Transferência', icon: ArrowLeftRight, color: 'info' },
  baixa: { label: 'Baixa', icon: XCircle, color: 'danger' },
  devolucao: { label: 'Devolução', icon: ArrowDownLeft, color: 'primary' }
};

// ==================== MOCK DATA ====================

const mockItems: InventoryItem[] = [
  {
    id: 'INV001',
    code: 'EPI-001',
    name: 'Capacete de Segurança',
    description: 'Capacete classe A para proteção contra impactos',
    category: 'epi',
    status: 'in_use',
    quantity: 45,
    minQuantity: 20,
    unitValue: 85.00,
    totalValue: 3825.00,
    location: 'Almoxarifado Central',
    assignedTo: 'Carlos Silva',
    assignedToId: 'EMP001',
    postId: 'POST001',
    postName: 'Posto Shopping Norte',
    serialNumber: null,
    brand: 'MSA',
    model: 'V-Gard',
    purchaseDate: '2023-06-15',
    warrantyExpiry: '2025-06-15',
    lastMovement: '2024-01-15T10:30:00',
    createdAt: '2023-06-15T08:00:00',
    updatedAt: '2024-01-15T10:30:00'
  },
  {
    id: 'INV002',
    code: 'FER-001',
    name: 'Kit Ferramentas Manutenção',
    description: 'Kit completo com chaves, alicates e acessórios',
    category: 'ferramenta',
    status: 'available',
    quantity: 12,
    minQuantity: 5,
    unitValue: 450.00,
    totalValue: 5400.00,
    location: 'Almoxarifado Central',
    assignedTo: null,
    assignedToId: null,
    postId: null,
    postName: null,
    serialNumber: 'KIT-2023-001',
    brand: 'Stanley',
    model: 'Professional',
    purchaseDate: '2023-08-20',
    warrantyExpiry: '2024-08-20',
    lastMovement: '2024-01-10T14:00:00',
    createdAt: '2023-08-20T09:00:00',
    updatedAt: '2024-01-10T14:00:00'
  },
  {
    id: 'INV003',
    code: 'UNI-001',
    name: 'Uniforme Completo',
    description: 'Uniforme padrão com calça, camisa e jaqueta',
    category: 'uniforme',
    status: 'in_use',
    quantity: 156,
    minQuantity: 50,
    unitValue: 280.00,
    totalValue: 43680.00,
    location: 'Distribuído em Postos',
    assignedTo: 'Múltiplos',
    assignedToId: null,
    postId: null,
    postName: null,
    serialNumber: null,
    brand: 'Uniformes Pro',
    model: 'Padrão 2024',
    purchaseDate: '2024-01-05',
    warrantyExpiry: null,
    lastMovement: '2024-01-14T11:00:00',
    createdAt: '2024-01-05T08:00:00',
    updatedAt: '2024-01-14T11:00:00'
  },
  {
    id: 'INV004',
    code: 'ELE-001',
    name: 'Rádio Comunicador',
    description: 'Rádio HT para comunicação entre equipes',
    category: 'eletronico',
    status: 'in_use',
    quantity: 34,
    minQuantity: 15,
    unitValue: 890.00,
    totalValue: 30260.00,
    location: 'Distribuído em Postos',
    assignedTo: 'Múltiplos',
    assignedToId: null,
    postId: null,
    postName: null,
    serialNumber: 'RADIO-2023-034',
    brand: 'Motorola',
    model: 'T82',
    purchaseDate: '2023-05-10',
    warrantyExpiry: '2025-05-10',
    lastMovement: '2024-01-12T09:30:00',
    createdAt: '2023-05-10T10:00:00',
    updatedAt: '2024-01-12T09:30:00'
  },
  {
    id: 'INV005',
    code: 'MAT-001',
    name: 'Cone de Sinalização',
    description: 'Cone laranja para sinalização de áreas',
    category: 'material',
    status: 'available',
    quantity: 89,
    minQuantity: 30,
    unitValue: 45.00,
    totalValue: 4005.00,
    location: 'Almoxarifado Central',
    assignedTo: null,
    assignedToId: null,
    postId: null,
    postName: null,
    serialNumber: null,
    brand: 'Plasticor',
    model: '75cm',
    purchaseDate: '2023-09-01',
    warrantyExpiry: null,
    lastMovement: '2024-01-08T16:00:00',
    createdAt: '2023-09-01T08:00:00',
    updatedAt: '2024-01-08T16:00:00'
  },
  {
    id: 'INV006',
    code: 'VEI-001',
    name: 'Moto Honda CG 160',
    description: 'Motocicleta para rondas e deslocamentos',
    category: 'veiculo',
    status: 'in_use',
    quantity: 8,
    minQuantity: 5,
    unitValue: 15000.00,
    totalValue: 120000.00,
    location: 'Garagem Central',
    assignedTo: 'Equipe Ronda',
    assignedToId: 'TEAM001',
    postId: null,
    postName: null,
    serialNumber: 'ABC1234',
    brand: 'Honda',
    model: 'CG 160 Start',
    purchaseDate: '2023-03-15',
    warrantyExpiry: '2026-03-15',
    lastMovement: '2024-01-15T07:00:00',
    createdAt: '2023-03-15T10:00:00',
    updatedAt: '2024-01-15T07:00:00'
  },
  {
    id: 'INV007',
    code: 'EPI-002',
    name: 'Luvas de Proteção',
    description: 'Luvas para proteção em atividades gerais',
    category: 'epi',
    status: 'available',
    quantity: 15,
    minQuantity: 30,
    unitValue: 35.00,
    totalValue: 525.00,
    location: 'Almoxarifado Central',
    assignedTo: null,
    assignedToId: null,
    postId: null,
    postName: null,
    serialNumber: null,
    brand: 'Volk',
    model: 'Multiuso',
    purchaseDate: '2023-11-20',
    warrantyExpiry: null,
    lastMovement: '2024-01-05T10:00:00',
    createdAt: '2023-11-20T08:00:00',
    updatedAt: '2024-01-05T10:00:00'
  },
  {
    id: 'INV008',
    code: 'ELE-002',
    name: 'Lanterna Tática',
    description: 'Lanterna LED recarregável para rondas noturnas',
    category: 'eletronico',
    status: 'maintenance',
    quantity: 5,
    minQuantity: 10,
    unitValue: 180.00,
    totalValue: 900.00,
    location: 'Manutenção',
    assignedTo: null,
    assignedToId: null,
    postId: null,
    postName: null,
    serialNumber: 'LANT-2023-005',
    brand: 'Fenix',
    model: 'TK16',
    purchaseDate: '2023-07-10',
    warrantyExpiry: '2024-07-10',
    lastMovement: '2024-01-13T15:00:00',
    createdAt: '2023-07-10T09:00:00',
    updatedAt: '2024-01-13T15:00:00'
  }
];

const mockMovements: Movement[] = [
  {
    id: 'MOV001',
    itemId: 'INV001',
    itemName: 'Capacete de Segurança',
    itemCode: 'EPI-001',
    type: 'saida',
    quantity: 5,
    fromLocation: 'Almoxarifado Central',
    toLocation: 'Posto Shopping Norte',
    fromEmployee: null,
    toEmployee: 'Carlos Silva',
    reason: 'Distribuição para novos funcionários',
    notes: 'Entregue no turno da manhã',
    performedBy: 'Maria Santos',
    performedAt: '2024-01-15T10:30:00',
    documentNumber: 'MOV-2024-001'
  },
  {
    id: 'MOV002',
    itemId: 'INV003',
    itemName: 'Uniforme Completo',
    itemCode: 'UNI-001',
    type: 'saida',
    quantity: 10,
    fromLocation: 'Almoxarifado Central',
    toLocation: 'Posto Centro',
    fromEmployee: null,
    toEmployee: 'Equipe Centro',
    reason: 'Reposição de uniformes',
    notes: null,
    performedBy: 'João Lima',
    performedAt: '2024-01-14T11:00:00',
    documentNumber: 'MOV-2024-002'
  },
  {
    id: 'MOV003',
    itemId: 'INV008',
    itemName: 'Lanterna Tática',
    itemCode: 'ELE-002',
    type: 'transferencia',
    quantity: 5,
    fromLocation: 'Posto Sul',
    toLocation: 'Manutenção',
    fromEmployee: 'Pedro Alves',
    toEmployee: null,
    reason: 'Defeito na bateria',
    notes: 'Aguardando peças para reparo',
    performedBy: 'Ana Costa',
    performedAt: '2024-01-13T15:00:00',
    documentNumber: 'MOV-2024-003'
  },
  {
    id: 'MOV004',
    itemId: 'INV004',
    itemName: 'Rádio Comunicador',
    itemCode: 'ELE-001',
    type: 'devolucao',
    quantity: 2,
    fromLocation: 'Posto Norte',
    toLocation: 'Almoxarifado Central',
    fromEmployee: 'Roberto Dias',
    toEmployee: null,
    reason: 'Desligamento de funcionário',
    notes: 'Equipamentos em bom estado',
    performedBy: 'Maria Santos',
    performedAt: '2024-01-12T09:30:00',
    documentNumber: 'MOV-2024-004'
  },
  {
    id: 'MOV005',
    itemId: 'INV002',
    itemName: 'Kit Ferramentas Manutenção',
    itemCode: 'FER-001',
    type: 'entrada',
    quantity: 3,
    fromLocation: null,
    toLocation: 'Almoxarifado Central',
    fromEmployee: null,
    toEmployee: null,
    reason: 'Compra NF 12345',
    notes: 'Fornecedor: Ferramentas Brasil',
    performedBy: 'João Lima',
    performedAt: '2024-01-10T14:00:00',
    documentNumber: 'NF-12345'
  },
  {
    id: 'MOV006',
    itemId: 'INV007',
    itemName: 'Luvas de Proteção',
    itemCode: 'EPI-002',
    type: 'baixa',
    quantity: 20,
    fromLocation: 'Almoxarifado Central',
    toLocation: null,
    fromEmployee: null,
    toEmployee: null,
    reason: 'Vencimento do prazo de validade',
    notes: 'Descarte conforme normas',
    performedBy: 'Ana Costa',
    performedAt: '2024-01-05T10:00:00',
    documentNumber: 'BAIXA-2024-001'
  }
];

const mockLocations: Location[] = [
  {
    id: 'LOC001',
    name: 'Almoxarifado Central',
    type: 'almoxarifado',
    address: 'Rua Principal, 100 - Centro',
    responsible: 'Maria Santos',
    itemCount: 234,
    totalValue: 125000.00,
    status: 'active'
  },
  {
    id: 'LOC002',
    name: 'Posto Shopping Norte',
    type: 'posto',
    address: 'Av. Shopping Norte, 500',
    responsible: 'Carlos Silva',
    itemCount: 45,
    totalValue: 28500.00,
    status: 'active'
  },
  {
    id: 'LOC003',
    name: 'Posto Centro',
    type: 'posto',
    address: 'Praça Central, 10',
    responsible: 'Ana Costa',
    itemCount: 38,
    totalValue: 22000.00,
    status: 'active'
  },
  {
    id: 'LOC004',
    name: 'Garagem Central',
    type: 'almoxarifado',
    address: 'Rua das Garagens, 50',
    responsible: 'Pedro Lima',
    itemCount: 12,
    totalValue: 180000.00,
    status: 'active'
  },
  {
    id: 'LOC005',
    name: 'Veículo Ronda 01',
    type: 'veiculo',
    address: null,
    responsible: 'Roberto Dias',
    itemCount: 8,
    totalValue: 4500.00,
    status: 'active'
  }
];

const mockAlerts: Alert[] = [
  {
    id: 'ALT001',
    type: 'low_stock',
    itemId: 'INV007',
    itemName: 'Luvas de Proteção',
    itemCode: 'EPI-002',
    message: 'Estoque abaixo do mínimo: 15/30 unidades',
    severity: 'high',
    createdAt: '2024-01-15T08:00:00',
    acknowledged: false,
    acknowledgedBy: null,
    acknowledgedAt: null
  },
  {
    id: 'ALT002',
    type: 'low_stock',
    itemId: 'INV008',
    itemName: 'Lanterna Tática',
    itemCode: 'ELE-002',
    message: 'Estoque abaixo do mínimo: 5/10 unidades',
    severity: 'medium',
    createdAt: '2024-01-14T10:00:00',
    acknowledged: false,
    acknowledgedBy: null,
    acknowledgedAt: null
  },
  {
    id: 'ALT003',
    type: 'expiring_warranty',
    itemId: 'INV002',
    itemName: 'Kit Ferramentas Manutenção',
    itemCode: 'FER-001',
    message: 'Garantia expira em 30 dias: 20/08/2024',
    severity: 'low',
    createdAt: '2024-01-10T09:00:00',
    acknowledged: true,
    acknowledgedBy: 'Maria Santos',
    acknowledgedAt: '2024-01-10T11:00:00'
  },
  {
    id: 'ALT004',
    type: 'maintenance_due',
    itemId: 'INV006',
    itemName: 'Moto Honda CG 160',
    itemCode: 'VEI-001',
    message: 'Manutenção preventiva pendente: 5000km',
    severity: 'medium',
    createdAt: '2024-01-13T14:00:00',
    acknowledged: false,
    acknowledgedBy: null,
    acknowledgedAt: null
  }
];

// ==================== CHART DATA ====================

const categoryDistributionData = [
  { name: 'EPI', value: 60, color: '#f59e0b' },
  { name: 'Ferramenta', value: 12, color: '#3b82f6' },
  { name: 'Uniforme', value: 156, color: '#6366f1' },
  { name: 'Eletrônico', value: 39, color: '#10b981' },
  { name: 'Material', value: 89, color: '#64748b' },
  { name: 'Veículo', value: 8, color: '#ef4444' }
];

const movementsTrendData = [
  { day: 'Seg', entradas: 12, saidas: 18 },
  { day: 'Ter', entradas: 8, saidas: 15 },
  { day: 'Qua', entradas: 15, saidas: 22 },
  { day: 'Qui', entradas: 10, saidas: 14 },
  { day: 'Sex', entradas: 20, saidas: 25 },
  { day: 'Sáb', entradas: 5, saidas: 8 },
  { day: 'Dom', entradas: 2, saidas: 3 }
];

const valueByLocationData = [
  { name: 'Almoxarifado Central', value: 125000 },
  { name: 'Garagem Central', value: 180000 },
  { name: 'Posto Shopping Norte', value: 28500 },
  { name: 'Posto Centro', value: 22000 },
  { name: 'Veículos', value: 4500 }
];

const monthlyValueData = [
  { month: 'Ago', valor: 320000 },
  { month: 'Set', valor: 335000 },
  { month: 'Out', valor: 345000 },
  { month: 'Nov', valor: 360000 },
  { month: 'Dez', valor: 375000 },
  { month: 'Jan', valor: 385000 }
];

// ==================== HELPERS ====================

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR');
};

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('pt-BR');
};

const getStatusBadge = (status: InventoryItem['status']) => {
  const config = STATUS_CONFIG[status];
  if (!config) return <Badge variant="neutral">{status}</Badge>;
  return <Badge variant={config.variant as any}>{config.label}</Badge>;
};

const getCategoryBadge = (category: string) => {
  const config = CATEGORIES[category];
  if (!config) return <Badge variant="neutral">{category}</Badge>;
  const Icon = config.icon;
  return (
    <Badge variant={config.color as any}>
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
};

const getMovementTypeBadge = (type: string) => {
  const config = MOVEMENT_TYPES[type];
  if (!config) return <Badge variant="neutral">{type}</Badge>;
  const Icon = config.icon;
  return (
    <Badge variant={config.color as any}>
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
};

const getSeverityBadge = (severity: Alert['severity']) => {
  const config: Record<string, { variant: any; label: string }> = {
    low: { variant: 'neutral', label: 'Baixa' },
    medium: { variant: 'warning', label: 'Média' },
    high: { variant: 'danger', label: 'Alta' },
    critical: { variant: 'danger', label: 'Crítica' }
  };
  const { variant, label } = config[severity] || { variant: 'neutral', label: severity };
  return <Badge variant={variant}>{label}</Badge>;
};

// ==================== COMPONENT ====================

export function FieldInventoryPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Modals
  const [showItemModal, setShowItemModal] = useState(false);
  const [showMovementModal, setShowMovementModal] = useState(false);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [showNewItemModal, setShowNewItemModal] = useState(false);
  const [showNewMovementModal, setShowNewMovementModal] = useState(false);
  const [showAlertModal, setShowAlertModal] = useState(false);

  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [selectedMovement, setSelectedMovement] = useState<Movement | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Box className="h-4 w-4" /> },
    { value: 'items', label: 'Itens', icon: <Package className="h-4 w-4" /> },
    { value: 'movements', label: 'Movimentações', icon: <ArrowLeftRight className="h-4 w-4" /> },
    { value: 'locations', label: 'Locais', icon: <MapPin className="h-4 w-4" /> },
    { value: 'alerts', label: 'Alertas', icon: <AlertTriangle className="h-4 w-4" /> }
  ];

  // Calculations
  const totalItems = mockItems.reduce((sum, item) => sum + item.quantity, 0);
  const totalValue = mockItems.reduce((sum, item) => sum + item.totalValue, 0);
  const lowStockItems = mockItems.filter(item => item.quantity < item.minQuantity).length;
  const pendingAlerts = mockAlerts.filter(alert => !alert.acknowledged).length;

  // Filters
  const filteredItems = mockItems.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Columns
  const itemColumns: Column<InventoryItem>[] = [
    {
      key: 'item',
      header: 'Item',
      render: (row) => {
        const CategoryIcon = CATEGORIES[row.category]?.icon || Package;
        return (
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-bg-tertiary">
              <CategoryIcon className="h-5 w-5 text-accent-primary" />
            </div>
            <div>
              <p className="font-medium text-text-primary">{row.name}</p>
              <p className="text-sm text-text-secondary">{row.code}</p>
            </div>
          </div>
        );
      }
    },
    {
      key: 'category',
      header: 'Categoria',
      render: (row) => getCategoryBadge(row.category)
    },
    {
      key: 'quantity',
      header: 'Quantidade',
      render: (row) => (
        <div className="flex items-center gap-2">
          <span className={row.quantity < row.minQuantity ? 'text-accent-danger font-semibold' : 'text-text-primary'}>
            {row.quantity}
          </span>
          <span className="text-text-secondary text-sm">/ {row.minQuantity} mín</span>
          {row.quantity < row.minQuantity && (
            <AlertTriangle className="h-4 w-4 text-accent-danger" />
          )}
        </div>
      )
    },
    {
      key: 'value',
      header: 'Valor Total',
      render: (row) => (
        <span className="text-text-primary">{formatCurrency(row.totalValue)}</span>
      )
    },
    {
      key: 'location',
      header: 'Local',
      render: (row) => (
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-text-secondary" />
          <span className="text-text-secondary">{row.location}</span>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => getStatusBadge(row.status)
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
              setSelectedItem(row);
              setShowItemModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedItem(row);
              setShowNewMovementModal(true);
            }}
          >
            <ArrowLeftRight className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const movementColumns: Column<Movement>[] = [
    {
      key: 'type',
      header: 'Tipo',
      render: (row) => getMovementTypeBadge(row.type)
    },
    {
      key: 'item',
      header: 'Item',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.itemName}</p>
          <p className="text-sm text-text-secondary">{row.itemCode}</p>
        </div>
      )
    },
    {
      key: 'quantity',
      header: 'Qtd',
      render: (row) => (
        <span className="font-semibold text-text-primary">{row.quantity}</span>
      )
    },
    {
      key: 'from',
      header: 'Origem',
      render: (row) => (
        <span className="text-text-secondary">
          {row.fromLocation || row.fromEmployee || '-'}
        </span>
      )
    },
    {
      key: 'to',
      header: 'Destino',
      render: (row) => (
        <span className="text-text-secondary">
          {row.toLocation || row.toEmployee || '-'}
        </span>
      )
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <div>
          <p className="text-text-primary">{formatDateTime(row.performedAt)}</p>
          <p className="text-xs text-text-secondary">por {row.performedBy}</p>
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setSelectedMovement(row);
            setShowMovementModal(true);
          }}
        >
          <Eye className="h-4 w-4" />
        </Button>
      )
    }
  ];

  const locationColumns: Column<Location>[] = [
    {
      key: 'name',
      header: 'Local',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-bg-tertiary">
            <MapPin className="h-5 w-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-sm text-text-secondary capitalize">{row.type}</p>
          </div>
        </div>
      )
    },
    {
      key: 'responsible',
      header: 'Responsável',
      render: (row) => (
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-text-secondary" />
          <span>{row.responsible}</span>
        </div>
      )
    },
    {
      key: 'items',
      header: 'Itens',
      render: (row) => (
        <span className="font-semibold text-text-primary">{row.itemCount}</span>
      )
    },
    {
      key: 'value',
      header: 'Valor Total',
      render: (row) => (
        <span className="text-text-primary">{formatCurrency(row.totalValue)}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        row.status === 'active' ? (
          <Badge variant="success">Ativo</Badge>
        ) : (
          <Badge variant="neutral">Inativo</Badge>
        )
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setSelectedLocation(row);
            setShowLocationModal(true);
          }}
        >
          <Eye className="h-4 w-4" />
        </Button>
      )
    }
  ];

  const alertColumns: Column<Alert>[] = [
    {
      key: 'severity',
      header: 'Severidade',
      render: (row) => getSeverityBadge(row.severity)
    },
    {
      key: 'item',
      header: 'Item',
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.itemName}</p>
          <p className="text-sm text-text-secondary">{row.itemCode}</p>
        </div>
      )
    },
    {
      key: 'message',
      header: 'Mensagem',
      render: (row) => (
        <span className="text-text-secondary">{row.message}</span>
      )
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <span className="text-text-secondary">{formatDateTime(row.createdAt)}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        row.acknowledged ? (
          <Badge variant="success">Reconhecido</Badge>
        ) : (
          <Badge variant="warning">Pendente</Badge>
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
              setSelectedAlert(row);
              setShowAlertModal(true);
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>
          {!row.acknowledged && (
            <Button variant="ghost" size="sm">
              <CheckCircle className="h-4 w-4" />
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
              Estoque de Campo
            </h1>
            <p className="text-text-secondary mt-1">
              Controle de materiais e equipamentos em campo
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => setShowNewMovementModal(true)}>
              <ArrowLeftRight className="h-4 w-4 mr-2" />
              Nova Movimentação
            </Button>
            <Button onClick={() => setShowNewItemModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Item
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Itens em Campo"
            value={totalItems.toLocaleString('pt-BR')}
            icon={<Package className="h-5 w-5" />}
            iconColor="primary"
            change={45}
            changeLabel="este mês"
          />
          <StatCard
            title="Valor Total"
            value={formatCurrency(totalValue)}
            icon={<TrendingUp className="h-5 w-5" />}
            iconColor="success"
            change={8}
            changeLabel="vs mês anterior"
          />
          <StatCard
            title="Estoque Baixo"
            value={lowStockItems.toString()}
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Alertas Pendentes"
            value={pendingAlerts.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="danger"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Charts Row 1 */}
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

              {/* Movements Trend */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Movimentações da Semana
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={movementsTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="day" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                    />
                    <Legend />
                    <Bar dataKey="entradas" name="Entradas" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="saidas" name="Saídas" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Value by Location */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Valor por Local
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={valueByLocationData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis type="number" stroke="#94a3b8" tickFormatter={(v) => `R$ ${(v/1000).toFixed(0)}k`} />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" width={140} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>

              {/* Monthly Value Evolution */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Evolução do Valor Total
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={monthlyValueData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" tickFormatter={(v) => `R$ ${(v/1000).toFixed(0)}k`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid #2d2d3d' }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Area
                      type="monotone"
                      dataKey="valor"
                      name="Valor"
                      stroke="#8b5cf6"
                      fill="#8b5cf6"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Recent Activity & Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Movements */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Movimentações Recentes
                  </h3>
                  <Button variant="ghost" size="sm" onClick={() => setActiveTab('movements')}>
                    Ver Todas
                  </Button>
                </div>
                <div className="space-y-3">
                  {mockMovements.slice(0, 4).map((mov) => {
                    const Icon = MOVEMENT_TYPES[mov.type]?.icon || ArrowLeftRight;
                    return (
                      <div
                        key={mov.id}
                        className="flex items-center justify-between p-3 rounded-lg bg-bg-tertiary"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${
                            mov.type === 'entrada' || mov.type === 'devolucao' ? 'bg-accent-success/20' :
                            mov.type === 'saida' ? 'bg-accent-warning/20' :
                            mov.type === 'baixa' ? 'bg-accent-danger/20' :
                            'bg-accent-info/20'
                          }`}>
                            <Icon className={`h-4 w-4 ${
                              mov.type === 'entrada' || mov.type === 'devolucao' ? 'text-accent-success' :
                              mov.type === 'saida' ? 'text-accent-warning' :
                              mov.type === 'baixa' ? 'text-accent-danger' :
                              'text-accent-info'
                            }`} />
                          </div>
                          <div>
                            <p className="font-medium text-text-primary">{mov.itemName}</p>
                            <p className="text-sm text-text-secondary">
                              {mov.quantity} unid. • {formatDateTime(mov.performedAt)}
                            </p>
                          </div>
                        </div>
                        {getMovementTypeBadge(mov.type)}
                      </div>
                    );
                  })}
                </div>
              </Card>

              {/* Pending Alerts */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-text-primary">
                    Alertas Pendentes
                  </h3>
                  <Button variant="ghost" size="sm" onClick={() => setActiveTab('alerts')}>
                    Ver Todos
                  </Button>
                </div>
                <div className="space-y-3">
                  {mockAlerts.filter(a => !a.acknowledged).map((alert) => (
                    <div
                      key={alert.id}
                      className={`flex items-center justify-between p-3 rounded-lg ${
                        alert.severity === 'critical' || alert.severity === 'high' ? 'bg-accent-danger/10 border border-accent-danger/30' :
                        alert.severity === 'medium' ? 'bg-accent-warning/10 border border-accent-warning/30' :
                        'bg-bg-tertiary'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <AlertTriangle className={`h-5 w-5 ${
                          alert.severity === 'critical' || alert.severity === 'high' ? 'text-accent-danger' :
                          alert.severity === 'medium' ? 'text-accent-warning' :
                          'text-text-secondary'
                        }`} />
                        <div>
                          <p className="font-medium text-text-primary">{alert.itemName}</p>
                          <p className="text-sm text-text-secondary">{alert.message}</p>
                        </div>
                      </div>
                      {getSeverityBadge(alert.severity)}
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Low Stock Items */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-primary">
                  Itens com Estoque Baixo
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {mockItems.filter(item => item.quantity < item.minQuantity).map((item) => {
                  const CategoryIcon = CATEGORIES[item.category]?.icon || Package;
                  const percentage = (item.quantity / item.minQuantity) * 100;
                  return (
                    <div
                      key={item.id}
                      className="p-4 rounded-lg bg-bg-tertiary border border-accent-danger/30"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 rounded-lg bg-accent-danger/20">
                          <CategoryIcon className="h-5 w-5 text-accent-danger" />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{item.name}</p>
                          <p className="text-sm text-text-secondary">{item.code}</p>
                        </div>
                      </div>
                      <div className="mb-2">
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-text-secondary">Estoque</span>
                          <span className="text-accent-danger font-semibold">
                            {item.quantity} / {item.minQuantity}
                          </span>
                        </div>
                        <div className="h-2 bg-bg-primary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-accent-danger transition-all"
                            style={{ width: `${Math.min(percentage, 100)}%` }}
                          />
                        </div>
                      </div>
                      <Button size="sm" className="w-full mt-2">
                        Solicitar Reposição
                      </Button>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'items' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <Input
                  placeholder="Buscar por nome ou código..."
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
                  ...Object.entries(STATUS_CONFIG).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))
                ]}
                value={statusFilter}
                onChange={setStatusFilter}
              />
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>

            <DataTable
              data={filteredItems}
              columns={itemColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'movements' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <Input
                  placeholder="Buscar movimentações..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todos Tipos' },
                    ...Object.entries(MOVEMENT_TYPES).map(([key, val]) => ({
                      value: key,
                      label: val.label
                    }))
                  ]}
                  value="all"
                  onChange={() => {}}
                />
              </div>
              <Button onClick={() => setShowNewMovementModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Movimentação
              </Button>
            </div>

            <DataTable
              data={mockMovements}
              columns={movementColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'locations' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <Input
                placeholder="Buscar locais..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Novo Local
              </Button>
            </div>

            <DataTable
              data={mockLocations}
              columns={locationColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'alerts' && (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-text-primary">
                Central de Alertas
              </h3>
              <div className="flex items-center gap-3">
                <Select
                  options={[
                    { value: 'all', label: 'Todos' },
                    { value: 'pending', label: 'Pendentes' },
                    { value: 'acknowledged', label: 'Reconhecidos' }
                  ]}
                  value="all"
                  onChange={() => {}}
                />
                <Button variant="outline">
                  Reconhecer Todos
                </Button>
              </div>
            </div>

            <DataTable
              data={mockAlerts}
              columns={alertColumns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Item Detail Modal */}
        <Modal
          isOpen={showItemModal}
          onClose={() => setShowItemModal(false)}
          title="Detalhes do Item"
          size="lg"
        >
          {selectedItem && (
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-accent-primary/20">
                    {(() => {
                      const CategoryIcon = CATEGORIES[selectedItem.category]?.icon || Package;
                      return <CategoryIcon className="h-8 w-8 text-accent-primary" />;
                    })()}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-text-primary">{selectedItem.name}</h3>
                    <p className="text-text-secondary">{selectedItem.code}</p>
                  </div>
                </div>
                {getStatusBadge(selectedItem.status)}
              </div>

              <p className="text-text-secondary">{selectedItem.description}</p>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Categoria</p>
                  <div className="mt-1">{getCategoryBadge(selectedItem.category)}</div>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Quantidade</p>
                  <p className="text-xl font-semibold text-text-primary mt-1">
                    {selectedItem.quantity}
                    <span className="text-sm text-text-secondary font-normal"> / {selectedItem.minQuantity} mín</span>
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Valor Unitário</p>
                  <p className="text-xl font-semibold text-text-primary mt-1">
                    {formatCurrency(selectedItem.unitValue)}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Valor Total</p>
                  <p className="text-xl font-semibold text-accent-success mt-1">
                    {formatCurrency(selectedItem.totalValue)}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Localização</h4>
                  <div className="p-4 rounded-lg bg-bg-tertiary">
                    <div className="flex items-center gap-2 mb-2">
                      <MapPin className="h-4 w-4 text-text-secondary" />
                      <span className="text-text-primary">{selectedItem.location}</span>
                    </div>
                    {selectedItem.assignedTo && (
                      <div className="flex items-center gap-2 mb-2">
                        <User className="h-4 w-4 text-text-secondary" />
                        <span className="text-text-primary">{selectedItem.assignedTo}</span>
                      </div>
                    )}
                    {selectedItem.postName && (
                      <div className="flex items-center gap-2">
                        <Building className="h-4 w-4 text-text-secondary" />
                        <span className="text-text-primary">{selectedItem.postName}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-text-primary mb-3">Informações do Produto</h4>
                  <div className="p-4 rounded-lg bg-bg-tertiary space-y-2">
                    {selectedItem.brand && (
                      <div className="flex justify-between">
                        <span className="text-text-secondary">Marca</span>
                        <span className="text-text-primary">{selectedItem.brand}</span>
                      </div>
                    )}
                    {selectedItem.model && (
                      <div className="flex justify-between">
                        <span className="text-text-secondary">Modelo</span>
                        <span className="text-text-primary">{selectedItem.model}</span>
                      </div>
                    )}
                    {selectedItem.serialNumber && (
                      <div className="flex justify-between">
                        <span className="text-text-secondary">Nº Série</span>
                        <span className="text-text-primary">{selectedItem.serialNumber}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-text-secondary">Data de Compra</p>
                  <p className="text-text-primary">
                    {selectedItem.purchaseDate ? formatDate(selectedItem.purchaseDate) : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-text-secondary">Garantia até</p>
                  <p className="text-text-primary">
                    {selectedItem.warrantyExpiry ? formatDate(selectedItem.warrantyExpiry) : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-text-secondary">Última Movimentação</p>
                  <p className="text-text-primary">{formatDateTime(selectedItem.lastMovement)}</p>
                </div>
                <div>
                  <p className="text-text-secondary">Cadastrado em</p>
                  <p className="text-text-primary">{formatDate(selectedItem.createdAt)}</p>
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button className="flex-1" onClick={() => {
                  setShowItemModal(false);
                  setShowNewMovementModal(true);
                }}>
                  <ArrowLeftRight className="h-4 w-4 mr-2" />
                  Nova Movimentação
                </Button>
                <Button variant="outline">
                  <History className="h-4 w-4 mr-2" />
                  Histórico
                </Button>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
                <Button variant="outline">
                  <QrCode className="h-4 w-4 mr-2" />
                  QR Code
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Movement Detail Modal */}
        <Modal
          isOpen={showMovementModal}
          onClose={() => setShowMovementModal(false)}
          title="Detalhes da Movimentação"
          size="md"
        >
          {selectedMovement && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getMovementTypeBadge(selectedMovement.type)}
                  <span className="text-text-secondary">{selectedMovement.documentNumber}</span>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <p className="text-text-secondary text-sm">Item</p>
                <p className="font-semibold text-text-primary">{selectedMovement.itemName}</p>
                <p className="text-text-secondary">{selectedMovement.itemCode}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Quantidade</p>
                  <p className="text-2xl font-semibold text-text-primary">{selectedMovement.quantity}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Data/Hora</p>
                  <p className="text-text-primary">{formatDateTime(selectedMovement.performedAt)}</p>
                </div>
              </div>

              {(selectedMovement.fromLocation || selectedMovement.fromEmployee) && (
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm mb-2">Origem</p>
                  {selectedMovement.fromLocation && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-text-secondary" />
                      <span className="text-text-primary">{selectedMovement.fromLocation}</span>
                    </div>
                  )}
                  {selectedMovement.fromEmployee && (
                    <div className="flex items-center gap-2 mt-1">
                      <User className="h-4 w-4 text-text-secondary" />
                      <span className="text-text-primary">{selectedMovement.fromEmployee}</span>
                    </div>
                  )}
                </div>
              )}

              {(selectedMovement.toLocation || selectedMovement.toEmployee) && (
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm mb-2">Destino</p>
                  {selectedMovement.toLocation && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-text-secondary" />
                      <span className="text-text-primary">{selectedMovement.toLocation}</span>
                    </div>
                  )}
                  {selectedMovement.toEmployee && (
                    <div className="flex items-center gap-2 mt-1">
                      <User className="h-4 w-4 text-text-secondary" />
                      <span className="text-text-primary">{selectedMovement.toEmployee}</span>
                    </div>
                  )}
                </div>
              )}

              <div>
                <p className="text-text-secondary text-sm mb-1">Motivo</p>
                <p className="text-text-primary">{selectedMovement.reason}</p>
              </div>

              {selectedMovement.notes && (
                <div>
                  <p className="text-text-secondary text-sm mb-1">Observações</p>
                  <p className="text-text-primary">{selectedMovement.notes}</p>
                </div>
              )}

              <div className="pt-4 border-t border-border-subtle">
                <p className="text-text-secondary text-sm">
                  Realizado por <span className="text-text-primary">{selectedMovement.performedBy}</span>
                </p>
              </div>
            </div>
          )}
        </Modal>

        {/* Location Detail Modal */}
        <Modal
          isOpen={showLocationModal}
          onClose={() => setShowLocationModal(false)}
          title="Detalhes do Local"
          size="md"
        >
          {selectedLocation && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-accent-primary/20">
                  <MapPin className="h-8 w-8 text-accent-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedLocation.name}</h3>
                  <p className="text-text-secondary capitalize">{selectedLocation.type}</p>
                </div>
              </div>

              {selectedLocation.address && (
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Endereço</p>
                  <p className="text-text-primary">{selectedLocation.address}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Itens</p>
                  <p className="text-2xl font-semibold text-text-primary">{selectedLocation.itemCount}</p>
                </div>
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Valor Total</p>
                  <p className="text-2xl font-semibold text-accent-success">
                    {formatCurrency(selectedLocation.totalValue)}
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <p className="text-text-secondary text-sm">Responsável</p>
                <div className="flex items-center gap-2 mt-1">
                  <User className="h-4 w-4 text-text-secondary" />
                  <span className="text-text-primary">{selectedLocation.responsible}</span>
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-border-subtle">
                <Button className="flex-1">
                  Ver Itens
                </Button>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New Item Modal */}
        <Modal
          isOpen={showNewItemModal}
          onClose={() => setShowNewItemModal(false)}
          title="Cadastrar Novo Item"
          size="lg"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Nome do Item
                </label>
                <Input placeholder="Ex: Capacete de Segurança" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Código
                </label>
                <Input placeholder="Ex: EPI-001" />
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
                  value="epi"
                  onChange={() => {}}
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Descrição
                </label>
                <textarea
                  className="w-full px-4 py-2 rounded-lg bg-bg-tertiary border border-border-default text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-primary"
                  rows={2}
                  placeholder="Descreva o item..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Quantidade Inicial
                </label>
                <Input type="number" placeholder="0" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Quantidade Mínima
                </label>
                <Input type="number" placeholder="0" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Valor Unitário (R$)
                </label>
                <Input type="number" placeholder="0.00" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Local de Armazenamento
                </label>
                <Select
                  options={mockLocations.map(loc => ({
                    value: loc.id,
                    label: loc.name
                  }))}
                  value=""
                  onChange={() => {}}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Marca
                </label>
                <Input placeholder="Ex: MSA" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Modelo
                </label>
                <Input placeholder="Ex: V-Gard" />
              </div>
            </div>

            <div className="flex gap-3 pt-4 border-t border-border-subtle">
              <Button className="flex-1">
                <Plus className="h-4 w-4 mr-2" />
                Cadastrar Item
              </Button>
              <Button variant="outline" onClick={() => setShowNewItemModal(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>

        {/* New Movement Modal */}
        <Modal
          isOpen={showNewMovementModal}
          onClose={() => setShowNewMovementModal(false)}
          title="Nova Movimentação"
          size="md"
        >
          <div className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Tipo de Movimentação
                </label>
                <Select
                  options={Object.entries(MOVEMENT_TYPES).map(([key, val]) => ({
                    value: key,
                    label: val.label
                  }))}
                  value="saida"
                  onChange={() => {}}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Item
                </label>
                <Select
                  options={mockItems.map(item => ({
                    value: item.id,
                    label: `${item.code} - ${item.name}`
                  }))}
                  value={selectedItem?.id || ''}
                  onChange={() => {}}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Quantidade
                </label>
                <Input type="number" placeholder="0" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Local de Destino
                </label>
                <Select
                  options={mockLocations.map(loc => ({
                    value: loc.id,
                    label: loc.name
                  }))}
                  value=""
                  onChange={() => {}}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Colaborador (opcional)
                </label>
                <Input placeholder="Nome do colaborador" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Motivo
                </label>
                <Input placeholder="Ex: Distribuição para novos funcionários" />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Observações
                </label>
                <textarea
                  className="w-full px-4 py-2 rounded-lg bg-bg-tertiary border border-border-default text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-primary"
                  rows={2}
                  placeholder="Observações adicionais..."
                />
              </div>
            </div>

            <div className="flex gap-3 pt-4 border-t border-border-subtle">
              <Button className="flex-1">
                <CheckCircle className="h-4 w-4 mr-2" />
                Confirmar Movimentação
              </Button>
              <Button variant="outline" onClick={() => setShowNewMovementModal(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>

        {/* Alert Detail Modal */}
        <Modal
          isOpen={showAlertModal}
          onClose={() => setShowAlertModal(false)}
          title="Detalhes do Alerta"
          size="md"
        >
          {selectedAlert && (
            <div className="space-y-6">
              <div className={`p-4 rounded-lg ${
                selectedAlert.severity === 'critical' || selectedAlert.severity === 'high' ? 'bg-accent-danger/10 border border-accent-danger/30' :
                selectedAlert.severity === 'medium' ? 'bg-accent-warning/10 border border-accent-warning/30' :
                'bg-bg-tertiary'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <AlertTriangle className={`h-6 w-6 ${
                    selectedAlert.severity === 'critical' || selectedAlert.severity === 'high' ? 'text-accent-danger' :
                    selectedAlert.severity === 'medium' ? 'text-accent-warning' :
                    'text-text-secondary'
                  }`} />
                  {getSeverityBadge(selectedAlert.severity)}
                </div>
                <p className="text-text-primary font-medium">{selectedAlert.message}</p>
              </div>

              <div className="p-4 rounded-lg bg-bg-tertiary">
                <p className="text-text-secondary text-sm">Item Relacionado</p>
                <p className="font-semibold text-text-primary">{selectedAlert.itemName}</p>
                <p className="text-text-secondary">{selectedAlert.itemCode}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-text-secondary">Criado em</p>
                  <p className="text-text-primary">{formatDateTime(selectedAlert.createdAt)}</p>
                </div>
                <div>
                  <p className="text-text-secondary">Status</p>
                  <p className="text-text-primary">
                    {selectedAlert.acknowledged ? 'Reconhecido' : 'Pendente'}
                  </p>
                </div>
              </div>

              {selectedAlert.acknowledged && (
                <div className="p-4 rounded-lg bg-bg-tertiary">
                  <p className="text-text-secondary text-sm">Reconhecido por</p>
                  <p className="text-text-primary">{selectedAlert.acknowledgedBy}</p>
                  <p className="text-text-secondary text-sm mt-1">
                    em {selectedAlert.acknowledgedAt ? formatDateTime(selectedAlert.acknowledgedAt) : '-'}
                  </p>
                </div>
              )}

              {!selectedAlert.acknowledged && (
                <div className="flex gap-3 pt-4 border-t border-border-subtle">
                  <Button className="flex-1">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Reconhecer Alerta
                  </Button>
                  <Button variant="outline">
                    Ver Item
                  </Button>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
