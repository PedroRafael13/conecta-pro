'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Download,
  ClipboardCheck,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  Edit,
  MapPin,
  User,
  Calendar,
  Wrench,
  Phone,
  FileText,
  Camera,
  MessageSquare,
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
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
} from '@/design-system/components';

// Types
interface ServiceOrder {
  id: string;
  number: string;
  client: string;
  clientAddress: string;
  type: 'installation' | 'maintenance' | 'corrective' | 'inspection' | 'removal';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  technician: string | null;
  scheduledDate: string;
  startTime: string | null;
  endTime: string | null;
  description: string;
  equipment: string[];
  createdAt: string;
}

// Mock Data
const serviceOrders: ServiceOrder[] = [
  {
    id: '1',
    number: 'OS-2026-0150',
    client: 'Shopping Center Norte',
    clientAddress: 'Av. Cruzeiro do Sul, 1100 - Santana',
    type: 'maintenance',
    priority: 'high',
    status: 'in_progress',
    technician: 'Carlos Eduardo',
    scheduledDate: '2026-01-15',
    startTime: '09:30',
    endTime: null,
    description: 'Manutenção preventiva sistema CFTV - 32 câmeras',
    equipment: ['Câmeras IP', 'DVR', 'Switches'],
    createdAt: '2026-01-14',
  },
  {
    id: '2',
    number: 'OS-2026-0149',
    client: 'Hospital São Lucas',
    clientAddress: 'Rua Dr. Arnaldo, 500 - Pinheiros',
    type: 'corrective',
    priority: 'urgent',
    status: 'in_progress',
    technician: 'Ana Paula',
    scheduledDate: '2026-01-15',
    startTime: '08:00',
    endTime: null,
    description: 'Reparo emergencial controle de acesso UTI',
    equipment: ['Controladora', 'Leitor biométrico'],
    createdAt: '2026-01-15',
  },
  {
    id: '3',
    number: 'OS-2026-0148',
    client: 'Tech Park Empresarial',
    clientAddress: 'Av. Paulista, 1000 - Bela Vista',
    type: 'installation',
    priority: 'medium',
    status: 'scheduled',
    technician: 'Roberto Silva',
    scheduledDate: '2026-01-15',
    startTime: null,
    endTime: null,
    description: 'Instalação de 8 câmeras externas e 4 internas',
    equipment: ['Câmeras IP', 'Cabos', 'Conectores', 'NVR'],
    createdAt: '2026-01-13',
  },
  {
    id: '4',
    number: 'OS-2026-0147',
    client: 'Condomínio Aurora',
    clientAddress: 'Rua das Flores, 200 - Moema',
    type: 'inspection',
    priority: 'low',
    status: 'completed',
    technician: 'Pedro Santos',
    scheduledDate: '2026-01-15',
    startTime: '14:00',
    endTime: '16:30',
    description: 'Vistoria mensal sistema de segurança',
    equipment: [],
    createdAt: '2026-01-10',
  },
  {
    id: '5',
    number: 'OS-2026-0146',
    client: 'Edifício Corporate Tower',
    clientAddress: 'Av. Faria Lima, 3000 - Itaim',
    type: 'maintenance',
    priority: 'medium',
    status: 'pending',
    technician: null,
    scheduledDate: '2026-01-16',
    startTime: null,
    endTime: null,
    description: 'Manutenção preventiva elevadores e interfones',
    equipment: ['Interfones', 'Central telefônica'],
    createdAt: '2026-01-12',
  },
  {
    id: '6',
    number: 'OS-2026-0145',
    client: 'Banco Central',
    clientAddress: 'Av. Paulista, 500 - Consolação',
    type: 'removal',
    priority: 'low',
    status: 'cancelled',
    technician: null,
    scheduledDate: '2026-01-14',
    startTime: null,
    endTime: null,
    description: 'Remoção de equipamentos antigos',
    equipment: ['DVR antigo', 'Câmeras analógicas'],
    createdAt: '2026-01-08',
  },
];

const typeConfig = {
  installation: { label: 'Instalação', color: 'primary' as const, icon: Wrench },
  maintenance: { label: 'Manutenção', color: 'info' as const, icon: Wrench },
  corrective: { label: 'Corretiva', color: 'danger' as const, icon: AlertTriangle },
  inspection: { label: 'Vistoria', color: 'success' as const, icon: ClipboardCheck },
  removal: { label: 'Remoção', color: 'warning' as const, icon: XCircle },
};

const priorityConfig = {
  low: { label: 'Baixa', color: 'neutral' as const },
  medium: { label: 'Média', color: 'info' as const },
  high: { label: 'Alta', color: 'warning' as const },
  urgent: { label: 'Urgente', color: 'danger' as const },
};

const statusConfig = {
  pending: { label: 'Pendente', color: 'warning' as const, icon: Clock },
  scheduled: { label: 'Agendada', color: 'info' as const, icon: Calendar },
  in_progress: { label: 'Em Andamento', color: 'primary' as const, icon: Wrench },
  completed: { label: 'Concluída', color: 'success' as const, icon: CheckCircle2 },
  cancelled: { label: 'Cancelada', color: 'neutral' as const, icon: XCircle },
};

const columns: Column<ServiceOrder>[] = [
  {
    key: 'number',
    header: 'OS',
    render: (row) => {
      const type = typeConfig[row.type];
      const TypeIcon = type.icon;
      return (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-${type.color}/10`}>
            <TypeIcon className={`w-4 h-4 text-${type.color}`} />
          </div>
          <div>
            <p className="font-mono text-sm font-medium text-accent-primary">{row.number}</p>
            <Badge variant={type.color} size="sm">{type.label}</Badge>
          </div>
        </div>
      );
    },
  },
  {
    key: 'client',
    header: 'Cliente',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.client}</p>
        <div className="flex items-center gap-1 mt-1">
          <MapPin className="w-3 h-3 text-text-muted" />
          <p className="text-xs text-text-muted truncate max-w-[200px]">{row.clientAddress}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'description',
    header: 'Descrição',
    render: (row) => (
      <p className="text-sm text-text-secondary line-clamp-2 max-w-[250px]">{row.description}</p>
    ),
  },
  {
    key: 'priority',
    header: 'Prioridade',
    render: (row) => {
      const config = priorityConfig[row.priority];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      const StatusIcon = config.icon;
      return (
        <Badge variant={config.color} leftIcon={<StatusIcon className="w-3 h-3" />}>
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'technician',
    header: 'Técnico',
    render: (row) => (
      row.technician ? (
        <div className="flex items-center gap-2">
          <Avatar name={row.technician} size="xs" />
          <span className="text-sm">{row.technician}</span>
        </div>
      ) : (
        <Badge variant="warning" size="sm">Não atribuído</Badge>
      )
    ),
  },
  {
    key: 'scheduledDate',
    header: 'Agendamento',
    render: (row) => (
      <div className="text-sm">
        <p className="text-text-primary">{new Date(row.scheduledDate).toLocaleDateString('pt-BR')}</p>
        {row.startTime && (
          <p className="text-xs text-text-muted">
            {row.startTime} {row.endTime ? `- ${row.endTime}` : '(em andamento)'}
          </p>
        )}
      </div>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        {row.status === 'pending' && (
          <Button variant="primary" size="sm">Atribuir</Button>
        )}
      </div>
    ),
  },
];

export function ServiceOrdersPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredOrders = serviceOrders.filter((order) => {
    const matchesSearch =
      order.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || order.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  // Stats
  const pending = serviceOrders.filter((o) => o.status === 'pending').length;
  const inProgress = serviceOrders.filter((o) => o.status === 'in_progress').length;
  const completed = serviceOrders.filter((o) => o.status === 'completed').length;
  const urgent = serviceOrders.filter((o) => o.priority === 'urgent' && o.status !== 'completed').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Ordens de Serviço
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie todas as ordens de serviço de campo
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova OS
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Pendentes"
              value={pending}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Em Andamento"
              value={inProgress}
              icon={<Wrench className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Concluídas Hoje"
              value={completed}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Urgentes"
              value={urgent}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todas (${serviceOrders.length})` },
                  { value: 'pending', label: `Pendentes (${pending})` },
                  { value: 'in_progress', label: `Em Andamento (${inProgress})` },
                  { value: 'completed', label: `Concluídas (${completed})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar OS..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Service Orders Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredOrders}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => console.log('Order clicked:', row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New OS Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Ordem de Serviço"
          description="Cadastre uma nova OS"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar OS
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Cliente"
                options={[
                  { value: '1', label: 'Shopping Center Norte' },
                  { value: '2', label: 'Hospital São Lucas' },
                  { value: '3', label: 'Tech Park Empresarial' },
                  { value: '4', label: 'Condomínio Aurora' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Tipo"
                options={[
                  { value: 'installation', label: 'Instalação' },
                  { value: 'maintenance', label: 'Manutenção' },
                  { value: 'corrective', label: 'Corretiva' },
                  { value: 'inspection', label: 'Vistoria' },
                  { value: 'removal', label: 'Remoção' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <Input label="Descrição" placeholder="Descreva o serviço a ser realizado" required />
            <div className="grid grid-cols-3 gap-4">
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
                placeholder="Selecione..."
              />
              <Input label="Data" type="date" />
              <Input label="Horário" type="time" />
            </div>
            <Select
              label="Técnico Responsável"
              options={[
                { value: '1', label: 'Carlos Eduardo' },
                { value: '2', label: 'Roberto Silva' },
                { value: '3', label: 'Ana Paula' },
                { value: '4', label: 'Pedro Santos' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione (opcional)"
            />
            <Input label="Equipamentos" placeholder="Liste os equipamentos necessários" />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
