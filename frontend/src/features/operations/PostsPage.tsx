'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  MapPin,
  Building2,
  Users,
  Clock,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Edit,
  MoreHorizontal,
  Shield,
  Sparkles,
  Wrench,
  DoorOpen,
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
interface Post {
  id: string;
  code: string;
  name: string;
  client: string;
  clientId: string;
  address: string;
  type: 'security' | 'cleaning' | 'maintenance' | 'reception';
  shift: string;
  requiredStaff: number;
  allocatedStaff: number;
  status: 'active' | 'inactive' | 'pending';
  coordinator: string;
  createdAt: string;
}

// Mock Data
const posts: Post[] = [
  {
    id: '1',
    code: 'PTO-001',
    name: 'Portaria Principal',
    client: 'Shopping Center Norte',
    clientId: 'CLI-001',
    address: 'Av. Cruzeiro do Sul, 1100',
    type: 'security',
    shift: '24h',
    requiredStaff: 6,
    allocatedStaff: 6,
    status: 'active',
    coordinator: 'Roberto Silva',
    createdAt: '2025-06-01',
  },
  {
    id: '2',
    code: 'PTO-002',
    name: 'Área de Alimentação',
    client: 'Shopping Center Norte',
    clientId: 'CLI-001',
    address: 'Av. Cruzeiro do Sul, 1100',
    type: 'cleaning',
    shift: '12x36',
    requiredStaff: 8,
    allocatedStaff: 7,
    status: 'active',
    coordinator: 'Maria Costa',
    createdAt: '2025-06-01',
  },
  {
    id: '3',
    code: 'PTO-003',
    name: 'Recepção Central',
    client: 'Hospital São Lucas',
    clientId: 'CLI-002',
    address: 'Rua Dr. Arnaldo, 500',
    type: 'reception',
    shift: '24h',
    requiredStaff: 4,
    allocatedStaff: 4,
    status: 'active',
    coordinator: 'Ana Oliveira',
    createdAt: '2025-03-15',
  },
  {
    id: '4',
    code: 'PTO-004',
    name: 'UTI Adulto',
    client: 'Hospital São Lucas',
    clientId: 'CLI-002',
    address: 'Rua Dr. Arnaldo, 500',
    type: 'cleaning',
    shift: '6x1',
    requiredStaff: 6,
    allocatedStaff: 6,
    status: 'active',
    coordinator: 'Carlos Lima',
    createdAt: '2025-03-15',
  },
  {
    id: '5',
    code: 'PTO-005',
    name: 'Guarita Condomínio',
    client: 'Condomínio Aurora',
    clientId: 'CLI-003',
    address: 'Rua das Flores, 200',
    type: 'security',
    shift: '12x36',
    requiredStaff: 4,
    allocatedStaff: 3,
    status: 'active',
    coordinator: 'Roberto Silva',
    createdAt: '2025-09-01',
  },
  {
    id: '6',
    code: 'PTO-006',
    name: 'Manutenção Predial',
    client: 'Tech Park',
    clientId: 'CLI-004',
    address: 'Av. Paulista, 1000',
    type: 'maintenance',
    shift: 'Comercial',
    requiredStaff: 3,
    allocatedStaff: 3,
    status: 'active',
    coordinator: 'Pedro Santos',
    createdAt: '2025-09-01',
  },
];

const typeConfig = {
  security: { label: 'Segurança', color: 'primary' as const, icon: Shield },
  cleaning: { label: 'Limpeza', color: 'info' as const, icon: Sparkles },
  maintenance: { label: 'Manutenção', color: 'warning' as const, icon: Wrench },
  reception: { label: 'Recepção', color: 'success' as const, icon: DoorOpen },
};

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  inactive: { label: 'Inativo', color: 'neutral' as const },
  pending: { label: 'Pendente', color: 'warning' as const },
};

const columns: Column<Post>[] = [
  {
    key: 'code',
    header: 'Código',
    render: (row) => (
      <span className="font-mono text-sm font-medium text-accent-primary">{row.code}</span>
    ),
  },
  {
    key: 'name',
    header: 'Posto',
    render: (row) => {
      const TypeIcon = typeConfig[row.type].icon;
      return (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-${typeConfig[row.type].color}/10`}>
            <TypeIcon className={`w-4 h-4 text-${typeConfig[row.type].color}`} />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <Badge variant={typeConfig[row.type].color} size="sm">
              {typeConfig[row.type].label}
            </Badge>
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
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-text-muted" />
          <span className="font-medium text-text-primary">{row.client}</span>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <MapPin className="w-3 h-3 text-text-muted" />
          <span className="text-xs text-text-muted">{row.address}</span>
        </div>
      </div>
    ),
  },
  {
    key: 'shift',
    header: 'Escala',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-text-muted" />
        <span className="text-sm text-text-secondary">{row.shift}</span>
      </div>
    ),
  },
  {
    key: 'staff',
    header: 'Efetivo',
    render: (row) => {
      const isFull = row.allocatedStaff >= row.requiredStaff;
      return (
        <div className="flex items-center gap-2">
          <Users className={`w-4 h-4 ${isFull ? 'text-success' : 'text-warning'}`} />
          <span className={`font-medium ${isFull ? 'text-success' : 'text-warning'}`}>
            {row.allocatedStaff}/{row.requiredStaff}
          </span>
        </div>
      );
    },
  },
  {
    key: 'coordinator',
    header: 'Coordenador',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.coordinator} size="xs" />
        <span className="text-sm text-text-secondary">{row.coordinator}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Visualizar">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function PostsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Form state for new post modal
  const [newPostClient, setNewPostClient] = useState('');
  const [newPostType, setNewPostType] = useState('');
  const [newPostScale, setNewPostScale] = useState('');
  const [newPostCoordinator, setNewPostCoordinator] = useState('');

  const filteredPosts = posts.filter((post) => {
    const matchesSearch =
      post.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.client.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab =
      selectedTab === 'all' || post.type === selectedTab || post.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  // Stats
  const totalPosts = posts.length;
  const activePosts = posts.filter((p) => p.status === 'active').length;
  const totalRequired = posts.reduce((acc, p) => acc + p.requiredStaff, 0);
  const totalAllocated = posts.reduce((acc, p) => acc + p.allocatedStaff, 0);
  const understaffed = posts.filter((p) => p.allocatedStaff < p.requiredStaff).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Postos de Trabalho
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie os postos e alocações de funcionários
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<MapPin className="w-4 h-4" />}>
              Mapa de Postos
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Novo Posto
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total de Postos"
              value={totalPosts}
              icon={<MapPin className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Postos Ativos"
              value={activePosts}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Efetivo Requerido"
              value={totalRequired}
              icon={<Users className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Efetivo Alocado"
              value={totalAllocated}
              icon={<Users className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <StatCard
              title="Postos Deficitários"
              value={understaffed}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todos (${posts.length})` },
                  { value: 'security', label: `Segurança (${posts.filter((p) => p.type === 'security').length})` },
                  { value: 'cleaning', label: `Limpeza (${posts.filter((p) => p.type === 'cleaning').length})` },
                  { value: 'maintenance', label: `Manutenção (${posts.filter((p) => p.type === 'maintenance').length})` },
                  { value: 'reception', label: `Recepção (${posts.filter((p) => p.type === 'reception').length})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar postos..."
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

        {/* Posts Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredPosts}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => { setSelectedPost(row); setShowDetailModal(true); }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Alert */}
        {understaffed > 0 && (
          <Card className="border-warning/30 bg-warning/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-warning/10">
                  <AlertTriangle className="w-6 h-6 text-warning" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    {understaffed} posto(s) com efetivo abaixo do necessário
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Faltam {totalRequired - totalAllocated} funcionário(s) para cobrir todos os postos
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Gerenciar Alocações
                </Button>
              </div>
            </CardBody>
          </Card>
        )}

        {/* New Post Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Novo Posto de Trabalho"
          description="Cadastre um novo posto"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Cadastrar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Código" placeholder="Auto-gerado" disabled />
              <Input label="Nome do Posto" placeholder="Ex: Portaria Principal" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Cliente"
                options={[
                  { value: '1', label: 'Shopping Center Norte' },
                  { value: '2', label: 'Hospital São Lucas' },
                  { value: '3', label: 'Condomínio Aurora' },
                  { value: '4', label: 'Tech Park' },
                ]}
                value={newPostClient}
                onChange={(value) => setNewPostClient(value)}
                placeholder="Selecione..."
              />
              <Select
                label="Tipo de Serviço"
                options={[
                  { value: 'security', label: 'Segurança' },
                  { value: 'cleaning', label: 'Limpeza' },
                  { value: 'maintenance', label: 'Manutenção' },
                  { value: 'reception', label: 'Recepção' },
                ]}
                value={newPostType}
                onChange={(value) => setNewPostType(value)}
                placeholder="Selecione..."
              />
            </div>
            <Input label="Endereço" placeholder="Endereço completo do posto" />
            <div className="grid grid-cols-3 gap-4">
              <Select
                label="Escala"
                options={[
                  { value: '24h', label: '24 horas' },
                  { value: '12x36', label: '12x36' },
                  { value: '6x1', label: '6x1' },
                  { value: 'comercial', label: 'Comercial' },
                ]}
                value={newPostScale}
                onChange={(value) => setNewPostScale(value)}
                placeholder="Selecione..."
              />
              <Input label="Efetivo Necessário" type="number" placeholder="0" />
              <Select
                label="Coordenador"
                options={[
                  { value: '1', label: 'Roberto Silva' },
                  { value: '2', label: 'Maria Costa' },
                  { value: '3', label: 'Ana Oliveira' },
                ]}
                value={newPostCoordinator}
                onChange={(value) => setNewPostCoordinator(value)}
                placeholder="Selecione..."
              />
            </div>
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes do Posto"
          description={selectedPost ? `${selectedPost.code} - ${selectedPost.name}` : ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              <Button variant="primary">Gerenciar Alocações</Button>
            </>
          }
        >
          {selectedPost && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className="p-3 rounded-lg bg-bg-primary">
                  {(() => {
                    const TypeIcon = typeConfig[selectedPost.type].icon;
                    return <TypeIcon className="w-6 h-6 text-text-muted" />;
                  })()}
                </div>
                <div className="flex-1">
                  <p className="font-mono text-sm text-accent-primary">{selectedPost.code}</p>
                  <p className="text-lg font-medium text-text-primary">{selectedPost.name}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={typeConfig[selectedPost.type].color}>{typeConfig[selectedPost.type].label}</Badge>
                    <Badge variant={statusConfig[selectedPost.status].color}>{statusConfig[selectedPost.status].label}</Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Cliente</p>
                  <p className="font-medium text-text-primary">{selectedPost.client}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Endereço</p>
                  <p className="font-medium text-text-primary">{selectedPost.address}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Escala</p>
                  <p className="font-medium text-text-primary">{selectedPost.shift}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Efetivo Necessário</p>
                  <p className="font-medium text-text-primary">{selectedPost.requiredStaff}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Efetivo Alocado</p>
                  <p className={`font-medium ${selectedPost.allocatedStaff >= selectedPost.requiredStaff ? 'text-accent-success' : 'text-accent-warning'}`}>
                    {selectedPost.allocatedStaff}
                  </p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-1">Coordenador</p>
                <div className="flex items-center gap-2">
                  <Avatar name={selectedPost.coordinator} size="sm" />
                  <p className="font-medium text-text-primary">{selectedPost.coordinator}</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-1">Criado em</p>
                <p className="font-medium text-text-primary">{selectedPost.createdAt}</p>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
