'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Wrench,
  Calendar,
  MapPin,
  User,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  Download,
  FileText,
  Phone,
  Building2,
  Package,
  ClipboardCheck,
  UserCheck,
  Navigation,
  Camera,
  MessageSquare,
  MoreVertical,
  RefreshCw,
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
  Select,
  Textarea,
  StatCard,
  StatGrid,
  DataTable,
  Dropdown,
  EmptyState,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from '@/design-system/components';

// Types
interface Installation {
  id: string;
  code: string;
  equipment: {
    id: string;
    name: string;
    model: string;
    serialNumber: string;
  };
  client: {
    id: string;
    name: string;
    address: string;
    contact: string;
    phone: string;
  };
  technician: {
    id: string;
    name: string;
    phone: string;
  } | null;
  scheduledDate: string;
  scheduledTime: string;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'rescheduled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  type: 'new' | 'replacement' | 'upgrade' | 'relocation';
  notes: string;
  completedAt: string | null;
  acceptedAt: string | null;
  acceptedBy: string | null;
  photos: string[];
  checklist: {
    id: string;
    item: string;
    completed: boolean;
  }[];
  createdAt: string;
}

// Mock data
const mockInstallations: Installation[] = [
  {
    id: '1',
    code: 'INST-2026-0001',
    equipment: {
      id: 'eq1',
      name: 'Câmera IP HD',
      model: 'CAM-HD-2000',
      serialNumber: 'SN-2026-001234',
    },
    client: {
      id: 'c1',
      name: 'Condomínio Solar das Flores',
      address: 'Rua das Acácias, 150 - Jardim Primavera',
      contact: 'José Silva',
      phone: '(11) 99999-1234',
    },
    technician: {
      id: 't1',
      name: 'Carlos Mendes',
      phone: '(11) 98888-5678',
    },
    scheduledDate: '2026-01-17',
    scheduledTime: '09:00',
    status: 'scheduled',
    priority: 'high',
    type: 'new',
    notes: 'Instalação de 4 câmeras na área comum',
    completedAt: null,
    acceptedAt: null,
    acceptedBy: null,
    photos: [],
    checklist: [
      { id: '1', item: 'Verificar ponto de energia', completed: false },
      { id: '2', item: 'Instalar suporte', completed: false },
      { id: '3', item: 'Conectar cabeamento', completed: false },
      { id: '4', item: 'Configurar rede', completed: false },
      { id: '5', item: 'Testar funcionamento', completed: false },
    ],
    createdAt: '2026-01-10',
  },
  {
    id: '2',
    code: 'INST-2026-0002',
    equipment: {
      id: 'eq2',
      name: 'Controlador de Acesso',
      model: 'CTRL-BIO-500',
      serialNumber: 'SN-2026-002345',
    },
    client: {
      id: 'c2',
      name: 'Edifício Corporate Tower',
      address: 'Av. Paulista, 1000 - Bela Vista',
      contact: 'Maria Santos',
      phone: '(11) 97777-4321',
    },
    technician: {
      id: 't2',
      name: 'Roberto Alves',
      phone: '(11) 96666-8765',
    },
    scheduledDate: '2026-01-16',
    scheduledTime: '14:00',
    status: 'in_progress',
    priority: 'urgent',
    type: 'replacement',
    notes: 'Substituição do controlador com defeito',
    completedAt: null,
    acceptedAt: null,
    acceptedBy: null,
    photos: [],
    checklist: [
      { id: '1', item: 'Desativar equipamento antigo', completed: true },
      { id: '2', item: 'Remover equipamento', completed: true },
      { id: '3', item: 'Instalar novo equipamento', completed: true },
      { id: '4', item: 'Configurar biometria', completed: false },
      { id: '5', item: 'Cadastrar usuários', completed: false },
    ],
    createdAt: '2026-01-12',
  },
  {
    id: '3',
    code: 'INST-2026-0003',
    equipment: {
      id: 'eq3',
      name: 'DVR 16 Canais',
      model: 'DVR-16CH-4K',
      serialNumber: 'SN-2026-003456',
    },
    client: {
      id: 'c3',
      name: 'Shopping Center Norte',
      address: 'Av. Brasil, 500 - Centro',
      contact: 'Pedro Lima',
      phone: '(11) 95555-9876',
    },
    technician: null,
    scheduledDate: '2026-01-20',
    scheduledTime: '08:00',
    status: 'pending',
    priority: 'medium',
    type: 'upgrade',
    notes: 'Upgrade do sistema de gravação',
    completedAt: null,
    acceptedAt: null,
    acceptedBy: null,
    photos: [],
    checklist: [
      { id: '1', item: 'Backup do sistema atual', completed: false },
      { id: '2', item: 'Desinstalar DVR antigo', completed: false },
      { id: '3', item: 'Instalar novo DVR', completed: false },
      { id: '4', item: 'Migrar configurações', completed: false },
      { id: '5', item: 'Testar gravação', completed: false },
    ],
    createdAt: '2026-01-14',
  },
  {
    id: '4',
    code: 'INST-2025-0089',
    equipment: {
      id: 'eq4',
      name: 'Cerca Elétrica',
      model: 'CERCA-IND-3000',
      serialNumber: 'SN-2025-089123',
    },
    client: {
      id: 'c4',
      name: 'Indústria Metalúrgica ABC',
      address: 'Rod. Anhanguera, Km 45 - Industrial',
      contact: 'Ana Costa',
      phone: '(11) 94444-3210',
    },
    technician: {
      id: 't1',
      name: 'Carlos Mendes',
      phone: '(11) 98888-5678',
    },
    scheduledDate: '2026-01-15',
    scheduledTime: '07:00',
    status: 'completed',
    priority: 'high',
    type: 'new',
    notes: 'Instalação de 200m de cerca elétrica',
    completedAt: '2026-01-15T16:30:00',
    acceptedAt: '2026-01-15T17:00:00',
    acceptedBy: 'Ana Costa',
    photos: ['photo1.jpg', 'photo2.jpg', 'photo3.jpg'],
    checklist: [
      { id: '1', item: 'Preparar postes', completed: true },
      { id: '2', item: 'Instalar isoladores', completed: true },
      { id: '3', item: 'Passar fiação', completed: true },
      { id: '4', item: 'Instalar central', completed: true },
      { id: '5', item: 'Testar alarme', completed: true },
    ],
    createdAt: '2026-01-05',
  },
];

const mockTechnicians = [
  { value: 't1', label: 'Carlos Mendes' },
  { value: 't2', label: 'Roberto Alves' },
  { value: 't3', label: 'Fernando Santos' },
  { value: 't4', label: 'Lucas Oliveira' },
];

const statusConfig: Record<Installation['status'], { label: string; variant: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'secondary' }> = {
  pending: { label: 'Pendente', variant: 'secondary' },
  scheduled: { label: 'Agendada', variant: 'info' },
  in_progress: { label: 'Em Andamento', variant: 'warning' },
  completed: { label: 'Concluída', variant: 'success' },
  cancelled: { label: 'Cancelada', variant: 'danger' },
  rescheduled: { label: 'Reagendada', variant: 'primary' },
};

const priorityConfig: Record<Installation['priority'], { label: string; variant: 'primary' | 'success' | 'warning' | 'danger' }> = {
  low: { label: 'Baixa', variant: 'success' },
  medium: { label: 'Média', variant: 'primary' },
  high: { label: 'Alta', variant: 'warning' },
  urgent: { label: 'Urgente', variant: 'danger' },
};

const typeLabels: Record<Installation['type'], string> = {
  new: 'Nova Instalação',
  replacement: 'Substituição',
  upgrade: 'Upgrade',
  relocation: 'Relocação',
};

export default function InstallationPage() {
  const [installations] = useState<Installation[]>(mockInstallations);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedInstallation, setSelectedInstallation] = useState<Installation | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  // Stats
  const stats = {
    total: installations.length,
    pending: installations.filter(i => i.status === 'pending').length,
    scheduled: installations.filter(i => i.status === 'scheduled').length,
    inProgress: installations.filter(i => i.status === 'in_progress').length,
    completed: installations.filter(i => i.status === 'completed').length,
    todayScheduled: installations.filter(i => i.scheduledDate === '2026-01-16').length,
  };

  // Filter
  const filteredInstallations = installations.filter(inst => {
    const matchesSearch =
      inst.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inst.client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inst.equipment.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || inst.status === statusFilter;
    const matchesTab = activeTab === 'all' || inst.status === activeTab;
    return matchesSearch && matchesStatus && matchesTab;
  });

  const columns = [
    {
      key: 'code',
      header: 'Código',
      render: (row: Installation) => (
        <span className="font-mono text-accent-primary">{row.code}</span>
      ),
    },
    {
      key: 'equipment',
      header: 'Equipamento',
      render: (row: Installation) => (
        <div>
          <p className="font-medium">{row.equipment.name}</p>
          <p className="text-xs text-text-secondary">{row.equipment.model}</p>
        </div>
      ),
    },
    {
      key: 'client',
      header: 'Cliente',
      render: (row: Installation) => (
        <div>
          <p className="font-medium">{row.client.name}</p>
          <p className="text-xs text-text-secondary flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {row.client.address.substring(0, 30)}...
          </p>
        </div>
      ),
    },
    {
      key: 'technician',
      header: 'Técnico',
      render: (row: Installation) => (
        row.technician ? (
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-text-secondary" />
            <span>{row.technician.name}</span>
          </div>
        ) : (
          <Badge variant="secondary">Não atribuído</Badge>
        )
      ),
    },
    {
      key: 'schedule',
      header: 'Agendamento',
      render: (row: Installation) => (
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-text-secondary" />
          <div>
            <p>{new Date(row.scheduledDate).toLocaleDateString('pt-BR')}</p>
            <p className="text-xs text-text-secondary">{row.scheduledTime}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'priority',
      header: 'Prioridade',
      render: (row: Installation) => (
        <Badge variant={priorityConfig[row.priority].variant}>
          {priorityConfig[row.priority].label}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: Installation) => (
        <Badge variant={statusConfig[row.status].variant}>
          {statusConfig[row.status].label}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row: Installation) => (
        <Dropdown
          trigger={
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          }
          items={[
            { label: 'Ver Detalhes', icon: <Eye className="w-4 h-4" />, onClick: () => { setSelectedInstallation(row); setShowDetailModal(true); } },
            { label: 'Editar', icon: <Edit className="w-4 h-4" />, onClick: () => {} },
            { label: 'Atribuir Técnico', icon: <UserCheck className="w-4 h-4" />, onClick: () => {} },
            { label: 'Reagendar', icon: <Calendar className="w-4 h-4" />, onClick: () => {} },
            { label: 'Cancelar', icon: <XCircle className="w-4 h-4" />, danger: true, onClick: () => {} },
          ]}
        />
      ),
    },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Instalações
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie agendamentos e execução de instalações de equipamentos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setShowNewModal(true)}>
              Nova Instalação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Instalações"
              value={stats.total}
              icon={<Package className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <StatCard
              title="Pendentes"
              value={stats.pending}
              icon={<Clock className="w-6 h-6" />}
              iconColor="secondary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Agendadas"
              value={stats.scheduled}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <StatCard
              title="Em Andamento"
              value={stats.inProgress}
              icon={<Wrench className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Concluídas"
              value={stats.completed}
              icon={<CheckCircle className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">Todas</TabsTrigger>
            <TabsTrigger value="pending">Pendentes</TabsTrigger>
            <TabsTrigger value="scheduled">Agendadas</TabsTrigger>
            <TabsTrigger value="in_progress">Em Andamento</TabsTrigger>
            <TabsTrigger value="completed">Concluídas</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Filters & Table */}
        <Card>
          <CardHeader
            title="Lista de Instalações"
            action={
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar instalações..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todos os Status' },
                    { value: 'pending', label: 'Pendente' },
                    { value: 'scheduled', label: 'Agendada' },
                    { value: 'in_progress', label: 'Em Andamento' },
                    { value: 'completed', label: 'Concluída' },
                  ]}
                  value={statusFilter}
                  onChange={setStatusFilter}
                  className="w-40"
                />
                <Button variant="outline" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            }
          />
          <CardBody className="p-0">
            {filteredInstallations.length > 0 ? (
              <DataTable
                columns={columns}
                data={filteredInstallations}
                onRowClick={(row) => { setSelectedInstallation(row); setShowDetailModal(true); }}
              />
            ) : (
              <EmptyState
                icon={<Wrench className="w-12 h-12" />}
                title="Nenhuma instalação encontrada"
                description="Não há instalações que correspondam aos filtros selecionados."
                action={{
                  label: 'Nova Instalação',
                  onClick: () => setShowNewModal(true),
                }}
              />
            )}
          </CardBody>
        </Card>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={`Instalação ${selectedInstallation?.code}`}
          size="lg"
        >
          {selectedInstallation && (
            <div className="space-y-6">
              {/* Status e Info */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge variant={statusConfig[selectedInstallation.status].variant} size="lg">
                    {statusConfig[selectedInstallation.status].label}
                  </Badge>
                  <Badge variant={priorityConfig[selectedInstallation.priority].variant}>
                    {priorityConfig[selectedInstallation.priority].label}
                  </Badge>
                  <Badge variant="secondary">{typeLabels[selectedInstallation.type]}</Badge>
                </div>
              </div>

              {/* Equipamento */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-2">Equipamento</h4>
                <div className="flex items-center gap-4">
                  <Package className="w-10 h-10 text-accent-primary" />
                  <div>
                    <p className="font-semibold text-text-primary">{selectedInstallation.equipment.name}</p>
                    <p className="text-sm text-text-secondary">Modelo: {selectedInstallation.equipment.model}</p>
                    <p className="text-sm text-text-secondary">S/N: {selectedInstallation.equipment.serialNumber}</p>
                  </div>
                </div>
              </div>

              {/* Cliente e Técnico */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Cliente</h4>
                  <div className="space-y-2">
                    <p className="font-semibold">{selectedInstallation.client.name}</p>
                    <p className="text-sm text-text-secondary flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      {selectedInstallation.client.address}
                    </p>
                    <p className="text-sm text-text-secondary flex items-center gap-2">
                      <User className="w-4 h-4" />
                      {selectedInstallation.client.contact}
                    </p>
                    <p className="text-sm text-text-secondary flex items-center gap-2">
                      <Phone className="w-4 h-4" />
                      {selectedInstallation.client.phone}
                    </p>
                  </div>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Técnico Responsável</h4>
                  {selectedInstallation.technician ? (
                    <div className="space-y-2">
                      <p className="font-semibold">{selectedInstallation.technician.name}</p>
                      <p className="text-sm text-text-secondary flex items-center gap-2">
                        <Phone className="w-4 h-4" />
                        {selectedInstallation.technician.phone}
                      </p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-4">
                      <UserCheck className="w-8 h-8 text-text-muted mb-2" />
                      <p className="text-text-secondary">Não atribuído</p>
                      <Button variant="outline" size="sm" className="mt-2">
                        Atribuir Técnico
                      </Button>
                    </div>
                  )}
                </div>
              </div>

              {/* Checklist */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Checklist de Instalação</h4>
                <div className="space-y-2">
                  {selectedInstallation.checklist.map((item) => (
                    <div key={item.id} className="flex items-center gap-3">
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center ${item.completed ? 'bg-success' : 'bg-bg-elevated border border-border-default'}`}>
                        {item.completed && <CheckCircle className="w-3 h-3 text-white" />}
                      </div>
                      <span className={item.completed ? 'text-text-secondary line-through' : 'text-text-primary'}>
                        {item.item}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="mt-3 pt-3 border-t border-border-subtle">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary">Progresso</span>
                    <span className="font-medium">
                      {selectedInstallation.checklist.filter(i => i.completed).length} / {selectedInstallation.checklist.length}
                    </span>
                  </div>
                </div>
              </div>

              {/* Notas */}
              {selectedInstallation.notes && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-2">Observações</h4>
                  <p className="text-text-primary">{selectedInstallation.notes}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                  Fechar
                </Button>
                {selectedInstallation.status === 'completed' && !selectedInstallation.acceptedAt && (
                  <Button variant="success" leftIcon={<CheckCircle className="w-4 h-4" />}>
                    Aceitar Instalação
                  </Button>
                )}
                {selectedInstallation.status === 'in_progress' && (
                  <Button variant="primary" leftIcon={<CheckCircle className="w-4 h-4" />}>
                    Marcar como Concluída
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* New Installation Modal */}
        <Modal
          isOpen={showNewModal}
          onClose={() => setShowNewModal(false)}
          title="Nova Instalação"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Equipamento"
                options={[
                  { value: 'eq1', label: 'Câmera IP HD - CAM-HD-2000' },
                  { value: 'eq2', label: 'Controlador de Acesso - CTRL-BIO-500' },
                  { value: 'eq3', label: 'DVR 16 Canais - DVR-16CH-4K' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione o equipamento"
                required
              />
              <Select
                label="Cliente"
                options={[
                  { value: 'c1', label: 'Condomínio Solar das Flores' },
                  { value: 'c2', label: 'Edifício Corporate Tower' },
                  { value: 'c3', label: 'Shopping Center Norte' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione o cliente"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Instalação"
                options={[
                  { value: 'new', label: 'Nova Instalação' },
                  { value: 'replacement', label: 'Substituição' },
                  { value: 'upgrade', label: 'Upgrade' },
                  { value: 'relocation', label: 'Relocação' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
              <Select
                label="Prioridade"
                options={[
                  { value: 'low', label: 'Baixa' },
                  { value: 'medium', label: 'Média' },
                  { value: 'high', label: 'Alta' },
                  { value: 'urgent', label: 'Urgente' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Data Agendada"
                type="date"
                required
              />
              <Input
                label="Horário"
                type="time"
                required
              />
            </div>
            <Select
              label="Técnico Responsável"
              options={mockTechnicians}
              value=""
              onChange={() => {}}
              placeholder="Selecione o técnico (opcional)"
            />
            <Textarea
              label="Observações"
              placeholder="Informações adicionais sobre a instalação..."
              rows={3}
            />
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                Criar Instalação
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
