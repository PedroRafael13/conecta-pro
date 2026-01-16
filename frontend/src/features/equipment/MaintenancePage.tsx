'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Wrench,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Edit2,
  Calendar,
  Clock,
  DollarSign,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Package,
  User,
  FileText,
  ClipboardCheck,
  Settings,
  BarChart3,
  TrendingUp
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { DataTable, Column } from '../../design-system/components/Table';
import { SimpleTabBar } from '../../design-system/components/Tabs';
import { MainLayout } from '../../layouts/MainLayout';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';

// Types
interface Maintenance {
  id: string;
  maintenanceNumber: string;
  equipmentId: string;
  equipmentName: string;
  equipmentCode: string;
  type: 'preventiva' | 'corretiva' | 'preditiva';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'scheduled' | 'in_progress' | 'waiting_parts' | 'completed' | 'cancelled';
  description: string;
  scheduledDate: string;
  startDate: string | null;
  completedDate: string | null;
  estimatedCost: number;
  actualCost: number | null;
  technician: string;
  vendor: string | null;
  notes: string;
}

// Mock Data
const mockMaintenances: Maintenance[] = [
  {
    id: '1',
    maintenanceNumber: 'MNT-2024-00145',
    equipmentId: '1',
    equipmentName: 'Servidor Dell PowerEdge R740',
    equipmentCode: 'PAT-2024-00005',
    type: 'preventiva',
    priority: 'high',
    status: 'completed',
    description: 'Manutenção preventiva semestral - limpeza, verificação de hardware e atualização de firmware',
    scheduledDate: '2024-02-15',
    startDate: '2024-02-15',
    completedDate: '2024-02-15',
    estimatedCost: 1500,
    actualCost: 1200,
    technician: 'Carlos Técnico',
    vendor: 'Dell Services',
    notes: 'Substituído 2 módulos de memória preventivamente'
  },
  {
    id: '2',
    maintenanceNumber: 'MNT-2024-00146',
    equipmentId: '2',
    equipmentName: 'Veículo Ford Transit ABC-1234',
    equipmentCode: 'PAT-2024-00002',
    type: 'corretiva',
    priority: 'critical',
    status: 'in_progress',
    description: 'Problema no sistema de freio - troca de pastilhas e discos',
    scheduledDate: '2024-02-16',
    startDate: '2024-02-16',
    completedDate: null,
    estimatedCost: 3500,
    actualCost: null,
    technician: 'Oficina AutoService',
    vendor: 'AutoService LTDA',
    notes: 'Aguardando conclusão - previsão para amanhã'
  },
  {
    id: '3',
    maintenanceNumber: 'MNT-2024-00147',
    equipmentId: '3',
    equipmentName: 'Impressora HP LaserJet Pro',
    equipmentCode: 'PAT-2024-00003',
    type: 'corretiva',
    priority: 'medium',
    status: 'waiting_parts',
    description: 'Substituição do fusor - aquecimento insuficiente',
    scheduledDate: '2024-02-17',
    startDate: '2024-02-17',
    completedDate: null,
    estimatedCost: 450,
    actualCost: null,
    technician: 'João TI',
    vendor: null,
    notes: 'Peça encomendada - prazo 3 dias úteis'
  },
  {
    id: '4',
    maintenanceNumber: 'MNT-2024-00148',
    equipmentId: '5',
    equipmentName: 'Ar Condicionado Split 12000 BTU',
    equipmentCode: 'PAT-2023-00089',
    type: 'preventiva',
    priority: 'low',
    status: 'scheduled',
    description: 'Limpeza e higienização semestral',
    scheduledDate: '2024-02-20',
    startDate: null,
    completedDate: null,
    estimatedCost: 200,
    actualCost: null,
    technician: 'Empresa Clima Bom',
    vendor: 'Clima Bom LTDA',
    notes: ''
  },
  {
    id: '5',
    maintenanceNumber: 'MNT-2024-00149',
    equipmentId: '6',
    equipmentName: 'Notebook Dell Latitude 5520',
    equipmentCode: 'PAT-2024-00001',
    type: 'preventiva',
    priority: 'medium',
    status: 'scheduled',
    description: 'Troca de pasta térmica e limpeza interna',
    scheduledDate: '2024-02-22',
    startDate: null,
    completedDate: null,
    estimatedCost: 150,
    actualCost: null,
    technician: 'Carlos TI',
    vendor: null,
    notes: ''
  }
];

const maintenanceTrendData = [
  { month: 'Set', preventiva: 45, corretiva: 12, custo: 15000 },
  { month: 'Out', preventiva: 52, corretiva: 8, custo: 12000 },
  { month: 'Nov', preventiva: 48, corretiva: 15, custo: 18000 },
  { month: 'Dez', preventiva: 55, corretiva: 6, custo: 9500 },
  { month: 'Jan', preventiva: 60, corretiva: 10, custo: 14000 },
  { month: 'Fev', preventiva: 58, corretiva: 7, custo: 11500 }
];

const typeDistributionData = [
  { name: 'Preventiva', value: 65, color: '#10b981' },
  { name: 'Corretiva', value: 28, color: '#ef4444' },
  { name: 'Preditiva', value: 7, color: '#6366f1' }
];

const statusDistributionData = [
  { status: 'Agendada', count: 12 },
  { status: 'Em Andamento', count: 5 },
  { status: 'Aguardando Peças', count: 3 },
  { status: 'Concluída', count: 45 },
  { status: 'Cancelada', count: 2 }
];

const tabs = [
  { value: 'all', label: 'Todas', icon: <ClipboardCheck className="h-4 w-4" /> },
  { value: 'scheduled', label: 'Agendadas', icon: <Calendar className="h-4 w-4" /> },
  { value: 'in_progress', label: 'Em Andamento', icon: <Clock className="h-4 w-4" /> },
  { value: 'completed', label: 'Concluídas', icon: <CheckCircle className="h-4 w-4" /> }
];

export function MaintenancePage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);

  const getTypeInfo = (type: Maintenance['type']) => {
    const types = {
      preventiva: { label: 'Preventiva', color: 'success' as const },
      corretiva: { label: 'Corretiva', color: 'danger' as const },
      preditiva: { label: 'Preditiva', color: 'primary' as const }
    };
    return types[type];
  };

  const getPriorityInfo = (priority: Maintenance['priority']) => {
    const priorities = {
      low: { label: 'Baixa', color: 'success' as const },
      medium: { label: 'Média', color: 'warning' as const },
      high: { label: 'Alta', color: 'danger' as const },
      critical: { label: 'Crítica', color: 'danger' as const }
    };
    return priorities[priority];
  };

  const getStatusInfo = (status: Maintenance['status']) => {
    const statuses = {
      scheduled: { label: 'Agendada', color: 'info' as const },
      in_progress: { label: 'Em Andamento', color: 'warning' as const },
      waiting_parts: { label: 'Aguardando Peças', color: 'info' as const },
      completed: { label: 'Concluída', color: 'success' as const },
      cancelled: { label: 'Cancelada', color: 'danger' as const }
    };
    return statuses[status];
  };

  const columns: Column<Maintenance>[] = [
    {
      key: 'maintenanceNumber',
      header: 'Número',
      sortable: true,
      render: (row) => (
        <span className="font-mono text-text-primary">{row.maintenanceNumber}</span>
      )
    },
    {
      key: 'equipmentName',
      header: 'Equipamento',
      sortable: true,
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.equipmentName}</p>
          <p className="text-xs text-text-secondary">{row.equipmentCode}</p>
        </div>
      )
    },
    {
      key: 'type',
      header: 'Tipo',
      sortable: true,
      render: (row) => {
        const info = getTypeInfo(row.type);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'priority',
      header: 'Prioridade',
      sortable: true,
      render: (row) => {
        const info = getPriorityInfo(row.priority);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'scheduledDate',
      header: 'Data Agendada',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary">
            {new Date(row.scheduledDate).toLocaleDateString('pt-BR')}
          </span>
        </div>
      )
    },
    {
      key: 'technician',
      header: 'Técnico',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary text-sm">{row.technician}</span>
        </div>
      )
    },
    {
      key: 'estimatedCost',
      header: 'Custo Est.',
      sortable: true,
      render: (row) => (
        <div>
          <p className="text-text-primary">
            {row.estimatedCost.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </p>
          {row.actualCost && (
            <p className={`text-xs ${row.actualCost <= row.estimatedCost ? 'text-accent-success' : 'text-accent-danger'}`}>
              Real: {row.actualCost.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            </p>
          )}
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row) => {
        const info = getStatusInfo(row.status);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <FileText className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const filteredMaintenances = mockMaintenances.filter(maintenance => {
    const matchesSearch =
      maintenance.maintenanceNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      maintenance.equipmentName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || maintenance.type === selectedType;
    const matchesTab = activeTab === 'all' || maintenance.status === activeTab;
    return matchesSearch && matchesType && matchesTab;
  });

  const totalCost = mockMaintenances
    .filter(m => m.status === 'completed')
    .reduce((sum, m) => sum + (m.actualCost || m.estimatedCost), 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Manutenções
            </h1>
            <p className="text-text-secondary mt-1">
              Manutenções preventivas, corretivas e preditivas
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button variant="primary" onClick={() => setShowMaintenanceModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Manutenção
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <StatCard
            title="Total de Manutenções"
            value={mockMaintenances.length.toString()}
            icon={<Wrench className="h-5 w-5" />}
          />
          <StatCard
            title="Agendadas"
            value={mockMaintenances.filter(m => m.status === 'scheduled').length.toString()}
            icon={<Calendar className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Em Andamento"
            value={mockMaintenances.filter(m => m.status === 'in_progress' || m.status === 'waiting_parts').length.toString()}
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Concluídas (Mês)"
            value={mockMaintenances.filter(m => m.status === 'completed').length.toString()}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Custo Total (Mês)"
            value={totalCost.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<DollarSign className="h-5 w-5" />}
          />
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trend Chart */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Histórico de Manutenções
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={maintenanceTrendData}>
                    <defs>
                      <linearGradient id="colorPrev" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorCorr" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="month" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="preventiva"
                      name="Preventiva"
                      stroke="#10b981"
                      fillOpacity={1}
                      fill="url(#colorPrev)"
                    />
                    <Area
                      type="monotone"
                      dataKey="corretiva"
                      name="Corretiva"
                      stroke="#ef4444"
                      fillOpacity={1}
                      fill="url(#colorCorr)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Type Distribution */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Por Tipo
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={typeDistributionData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={60}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {typeDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-4 mt-2">
                {typeDistributionData.map((item) => (
                  <div key={item.name} className="flex items-center gap-2 text-sm">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-text-secondary">{item.name}</span>
                    <span className="text-text-primary font-medium">{item.value}%</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Lista de Manutenções
              </h3>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                  <Input
                    placeholder="Buscar manutenções..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <select
                  className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary text-sm"
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                >
                  <option value="all">Todos os tipos</option>
                  <option value="preventiva">Preventiva</option>
                  <option value="corretiva">Corretiva</option>
                  <option value="preditiva">Preditiva</option>
                </select>
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <DataTable<Maintenance>
              data={filteredMaintenances}
              columns={columns}
              keyExtractor={(row) => row.id}
            />
          </CardBody>
        </Card>

        {/* Maintenance Modal */}
        <Modal
          isOpen={showMaintenanceModal}
          onClose={() => setShowMaintenanceModal(false)}
          title="Nova Manutenção"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Equipamento *
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="">Selecione o equipamento...</option>
                  <option value="1">PAT-2024-00001 - Notebook Dell</option>
                  <option value="2">PAT-2024-00002 - Veículo Ford Transit</option>
                  <option value="3">PAT-2024-00003 - Impressora HP</option>
                  <option value="5">PAT-2024-00005 - Servidor Dell</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Tipo de Manutenção *
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="preventiva">Preventiva</option>
                  <option value="corretiva">Corretiva</option>
                  <option value="preditiva">Preditiva</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Descrição *
              </label>
              <textarea
                className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                rows={3}
                placeholder="Descreva a manutenção a ser realizada..."
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Prioridade *
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="low">Baixa</option>
                  <option value="medium">Média</option>
                  <option value="high">Alta</option>
                  <option value="critical">Crítica</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Data Agendada *
                </label>
                <Input type="date" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Custo Estimado
                </label>
                <Input type="number" step="0.01" placeholder="0,00" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Técnico/Responsável *
                </label>
                <Input placeholder="Nome do técnico ou empresa" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Fornecedor (se externo)
                </label>
                <Input placeholder="Nome do fornecedor" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Observações
              </label>
              <textarea
                className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                rows={2}
                placeholder="Observações adicionais..."
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="ghost" onClick={() => setShowMaintenanceModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                Agendar Manutenção
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}

export default MaintenancePage;
