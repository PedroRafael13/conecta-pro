'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Users,
  Home,
  User,
  Phone,
  Mail,
  MapPin,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  MoreVertical,
  CheckCircle,
  XCircle,
  Clock,
  Key,
  Car,
  Shield,
  Calendar,
  FileText,
  Download,
  Upload,
  UserPlus,
  QrCode,
  Fingerprint,
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
interface Unit {
  id: string;
  number: string;
  block: string;
  floor: number;
  type: 'apartment' | 'house' | 'commercial' | 'storage';
  area: number;
  bedrooms?: number;
  status: 'occupied' | 'vacant' | 'maintenance';
  owner: {
    id: string;
    name: string;
    email: string;
    phone: string;
  } | null;
  tenant: {
    id: string;
    name: string;
    email: string;
    phone: string;
    leaseEnd: string;
  } | null;
  residents: number;
  vehicles: number;
  pets: number;
  createdAt: string;
}

interface Resident {
  id: string;
  name: string;
  cpf: string;
  email: string;
  phone: string;
  type: 'owner' | 'tenant' | 'dependent' | 'employee';
  unit: {
    id: string;
    number: string;
    block: string;
  };
  status: 'active' | 'inactive' | 'pending';
  accessMethods: string[];
  vehicles: {
    plate: string;
    model: string;
    color: string;
  }[];
  emergencyContact: {
    name: string;
    phone: string;
    relationship: string;
  } | null;
  createdAt: string;
  lastAccess: string | null;
}

// Mock data
const mockUnits: Unit[] = [
  {
    id: '1',
    number: '101',
    block: 'A',
    floor: 1,
    type: 'apartment',
    area: 85,
    bedrooms: 3,
    status: 'occupied',
    owner: { id: 'o1', name: 'José Silva', email: 'jose@email.com', phone: '(11) 99999-1234' },
    tenant: null,
    residents: 4,
    vehicles: 2,
    pets: 1,
    createdAt: '2024-01-15',
  },
  {
    id: '2',
    number: '102',
    block: 'A',
    floor: 1,
    type: 'apartment',
    area: 65,
    bedrooms: 2,
    status: 'occupied',
    owner: { id: 'o2', name: 'Maria Santos', email: 'maria@email.com', phone: '(11) 97777-4321' },
    tenant: { id: 't1', name: 'Carlos Mendes', email: 'carlos@email.com', phone: '(11) 98888-5678', leaseEnd: '2026-06-30' },
    residents: 2,
    vehicles: 1,
    pets: 0,
    createdAt: '2024-01-15',
  },
  {
    id: '3',
    number: '201',
    block: 'A',
    floor: 2,
    type: 'apartment',
    area: 120,
    bedrooms: 4,
    status: 'occupied',
    owner: { id: 'o3', name: 'Pedro Lima', email: 'pedro@email.com', phone: '(11) 95555-9876' },
    tenant: null,
    residents: 5,
    vehicles: 3,
    pets: 2,
    createdAt: '2024-01-15',
  },
  {
    id: '4',
    number: '202',
    block: 'A',
    floor: 2,
    type: 'apartment',
    area: 85,
    bedrooms: 3,
    status: 'vacant',
    owner: { id: 'o4', name: 'Ana Costa', email: 'ana@email.com', phone: '(11) 94444-3210' },
    tenant: null,
    residents: 0,
    vehicles: 0,
    pets: 0,
    createdAt: '2024-01-15',
  },
  {
    id: '5',
    number: '01',
    block: 'G',
    floor: 0,
    type: 'storage',
    area: 12,
    status: 'occupied',
    owner: { id: 'o1', name: 'José Silva', email: 'jose@email.com', phone: '(11) 99999-1234' },
    tenant: null,
    residents: 0,
    vehicles: 0,
    pets: 0,
    createdAt: '2024-01-15',
  },
];

const mockResidents: Resident[] = [
  {
    id: '1',
    name: 'José Silva',
    cpf: '123.456.789-00',
    email: 'jose@email.com',
    phone: '(11) 99999-1234',
    type: 'owner',
    unit: { id: '1', number: '101', block: 'A' },
    status: 'active',
    accessMethods: ['facial', 'fingerprint', 'card'],
    vehicles: [{ plate: 'ABC-1234', model: 'Honda Civic', color: 'Prata' }],
    emergencyContact: { name: 'Maria Silva', phone: '(11) 98888-1234', relationship: 'Esposa' },
    createdAt: '2024-01-15',
    lastAccess: '2026-01-16T08:30:00',
  },
  {
    id: '2',
    name: 'Maria Silva',
    cpf: '987.654.321-00',
    email: 'mariasilva@email.com',
    phone: '(11) 98888-1234',
    type: 'dependent',
    unit: { id: '1', number: '101', block: 'A' },
    status: 'active',
    accessMethods: ['facial', 'card'],
    vehicles: [{ plate: 'DEF-5678', model: 'Toyota Corolla', color: 'Branco' }],
    emergencyContact: { name: 'José Silva', phone: '(11) 99999-1234', relationship: 'Marido' },
    createdAt: '2024-01-15',
    lastAccess: '2026-01-16T09:15:00',
  },
  {
    id: '3',
    name: 'Carlos Mendes',
    cpf: '456.789.123-00',
    email: 'carlos@email.com',
    phone: '(11) 98888-5678',
    type: 'tenant',
    unit: { id: '2', number: '102', block: 'A' },
    status: 'active',
    accessMethods: ['fingerprint', 'card'],
    vehicles: [{ plate: 'GHI-9012', model: 'VW Golf', color: 'Preto' }],
    emergencyContact: { name: 'Ana Mendes', phone: '(11) 97777-5678', relationship: 'Irmã' },
    createdAt: '2024-03-01',
    lastAccess: '2026-01-15T22:45:00',
  },
  {
    id: '4',
    name: 'Pedro Lima',
    cpf: '789.123.456-00',
    email: 'pedro@email.com',
    phone: '(11) 95555-9876',
    type: 'owner',
    unit: { id: '3', number: '201', block: 'A' },
    status: 'active',
    accessMethods: ['facial', 'fingerprint', 'card', 'qrcode'],
    vehicles: [
      { plate: 'JKL-3456', model: 'BMW X5', color: 'Azul' },
      { plate: 'MNO-7890', model: 'Audi A4', color: 'Cinza' },
    ],
    emergencyContact: { name: 'Lucia Lima', phone: '(11) 94444-9876', relationship: 'Mãe' },
    createdAt: '2024-01-15',
    lastAccess: '2026-01-16T07:00:00',
  },
  {
    id: '5',
    name: 'Funcionário Teste',
    cpf: '111.222.333-00',
    email: 'funcionario@email.com',
    phone: '(11) 91111-2222',
    type: 'employee',
    unit: { id: '1', number: '101', block: 'A' },
    status: 'pending',
    accessMethods: ['card'],
    vehicles: [],
    emergencyContact: null,
    createdAt: '2026-01-10',
    lastAccess: null,
  },
];

const unitTypeLabels: Record<Unit['type'], string> = {
  apartment: 'Apartamento',
  house: 'Casa',
  commercial: 'Comercial',
  storage: 'Depósito',
};

const unitStatusConfig: Record<Unit['status'], { label: string; variant: 'success' | 'warning' | 'secondary' }> = {
  occupied: { label: 'Ocupado', variant: 'success' },
  vacant: { label: 'Vago', variant: 'warning' },
  maintenance: { label: 'Manutenção', variant: 'secondary' },
};

const residentTypeConfig: Record<Resident['type'], { label: string; variant: 'primary' | 'success' | 'info' | 'warning' }> = {
  owner: { label: 'Proprietário', variant: 'primary' },
  tenant: { label: 'Inquilino', variant: 'success' },
  dependent: { label: 'Dependente', variant: 'info' },
  employee: { label: 'Funcionário', variant: 'warning' },
};

const residentStatusConfig: Record<Resident['status'], { label: string; variant: 'success' | 'danger' | 'warning' }> = {
  active: { label: 'Ativo', variant: 'success' },
  inactive: { label: 'Inativo', variant: 'danger' },
  pending: { label: 'Pendente', variant: 'warning' },
};

const accessMethodIcons: Record<string, typeof Fingerprint> = {
  facial: User,
  fingerprint: Fingerprint,
  card: Key,
  qrcode: QrCode,
};

export default function UnitsResidentsPage() {
  const [units] = useState<Unit[]>(mockUnits);
  const [residents] = useState<Resident[]>(mockResidents);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('units');
  const [selectedUnit, setSelectedUnit] = useState<Unit | null>(null);
  const [selectedResident, setSelectedResident] = useState<Resident | null>(null);
  const [showUnitModal, setShowUnitModal] = useState(false);
  const [showResidentModal, setShowResidentModal] = useState(false);
  const [showNewUnitModal, setShowNewUnitModal] = useState(false);
  const [showNewResidentModal, setShowNewResidentModal] = useState(false);

  // Stats
  const unitStats = {
    total: units.length,
    occupied: units.filter(u => u.status === 'occupied').length,
    vacant: units.filter(u => u.status === 'vacant').length,
    totalResidents: units.reduce((acc, u) => acc + u.residents, 0),
  };

  const residentStats = {
    total: residents.length,
    active: residents.filter(r => r.status === 'active').length,
    owners: residents.filter(r => r.type === 'owner').length,
    tenants: residents.filter(r => r.type === 'tenant').length,
  };

  // Filter
  const filteredUnits = units.filter(unit =>
    unit.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    unit.block.toLowerCase().includes(searchTerm.toLowerCase()) ||
    unit.owner?.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredResidents = residents.filter(resident =>
    resident.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    resident.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    resident.unit.number.includes(searchTerm)
  );

  const unitColumns = [
    {
      key: 'unit',
      header: 'Unidade',
      render: (row: Unit) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
            <Home className="w-5 h-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium">Bloco {row.block} - {row.number}</p>
            <p className="text-xs text-text-secondary">{unitTypeLabels[row.type]} • {row.area}m²</p>
          </div>
        </div>
      ),
    },
    {
      key: 'owner',
      header: 'Proprietário',
      render: (row: Unit) => (
        row.owner ? (
          <div>
            <p className="font-medium">{row.owner.name}</p>
            <p className="text-xs text-text-secondary">{row.owner.phone}</p>
          </div>
        ) : (
          <span className="text-text-muted">-</span>
        )
      ),
    },
    {
      key: 'tenant',
      header: 'Inquilino',
      render: (row: Unit) => (
        row.tenant ? (
          <div>
            <p className="font-medium">{row.tenant.name}</p>
            <p className="text-xs text-text-secondary">Até {new Date(row.tenant.leaseEnd).toLocaleDateString('pt-BR')}</p>
          </div>
        ) : (
          <span className="text-text-muted">-</span>
        )
      ),
    },
    {
      key: 'residents',
      header: 'Moradores',
      render: (row: Unit) => (
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4 text-text-secondary" />
            <span>{row.residents}</span>
          </div>
          <div className="flex items-center gap-1">
            <Car className="w-4 h-4 text-text-secondary" />
            <span>{row.vehicles}</span>
          </div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: Unit) => (
        <Badge variant={unitStatusConfig[row.status].variant}>
          {unitStatusConfig[row.status].label}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row: Unit) => (
        <Dropdown
          trigger={
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          }
          items={[
            { label: 'Ver Detalhes', icon: <Eye className="w-4 h-4" />, onClick: () => { setSelectedUnit(row); setShowUnitModal(true); } },
            { label: 'Editar', icon: <Edit className="w-4 h-4" />, onClick: () => {} },
            { label: 'Adicionar Morador', icon: <UserPlus className="w-4 h-4" />, onClick: () => {} },
            { label: 'Excluir', icon: <Trash2 className="w-4 h-4" />, danger: true, onClick: () => {} },
          ]}
        />
      ),
    },
  ];

  const residentColumns = [
    {
      key: 'resident',
      header: 'Morador',
      render: (row: Resident) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-accent-primary/20 flex items-center justify-center">
            <User className="w-5 h-5 text-accent-primary" />
          </div>
          <div>
            <p className="font-medium">{row.name}</p>
            <p className="text-xs text-text-secondary">{row.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'unit',
      header: 'Unidade',
      render: (row: Resident) => (
        <span>Bloco {row.unit.block} - {row.unit.number}</span>
      ),
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (row: Resident) => (
        <Badge variant={residentTypeConfig[row.type].variant}>
          {residentTypeConfig[row.type].label}
        </Badge>
      ),
    },
    {
      key: 'access',
      header: 'Acesso',
      render: (row: Resident) => (
        <div className="flex items-center gap-1">
          {row.accessMethods.map((method) => {
            const Icon = accessMethodIcons[method] || Key;
            return (
              <div key={method} className="w-6 h-6 rounded bg-bg-tertiary flex items-center justify-center" title={method}>
                <Icon className="w-3 h-3 text-text-secondary" />
              </div>
            );
          })}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: Resident) => (
        <Badge variant={residentStatusConfig[row.status].variant}>
          {residentStatusConfig[row.status].label}
        </Badge>
      ),
    },
    {
      key: 'lastAccess',
      header: 'Último Acesso',
      render: (row: Resident) => (
        row.lastAccess ? (
          <span className="text-text-secondary text-sm">
            {new Date(row.lastAccess).toLocaleString('pt-BR')}
          </span>
        ) : (
          <span className="text-text-muted">Nunca</span>
        )
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (row: Resident) => (
        <Dropdown
          trigger={
            <Button variant="ghost" size="sm">
              <MoreVertical className="w-4 h-4" />
            </Button>
          }
          items={[
            { label: 'Ver Detalhes', icon: <Eye className="w-4 h-4" />, onClick: () => { setSelectedResident(row); setShowResidentModal(true); } },
            { label: 'Editar', icon: <Edit className="w-4 h-4" />, onClick: () => {} },
            { label: 'Gerar QR Code', icon: <QrCode className="w-4 h-4" />, onClick: () => {} },
            { label: row.status === 'active' ? 'Desativar' : 'Ativar', icon: row.status === 'active' ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />, onClick: () => {} },
            { label: 'Excluir', icon: <Trash2 className="w-4 h-4" />, danger: true, onClick: () => {} },
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
              Unidades e Moradores
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie unidades, proprietários, inquilinos e moradores do condomínio
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => activeTab === 'units' ? setShowNewUnitModal(true) : setShowNewResidentModal(true)}
            >
              {activeTab === 'units' ? 'Nova Unidade' : 'Novo Morador'}
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="units">Unidades</TabsTrigger>
            <TabsTrigger value="residents">Moradores</TabsTrigger>
          </TabsList>

          <TabsContent value="units">
            {/* Unit Stats */}
            <StatGrid columns={4}>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <StatCard
                  title="Total de Unidades"
                  value={unitStats.total}
                  icon={<Building2 className="w-6 h-6" />}
                  iconColor="primary"
                />
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                <StatCard
                  title="Ocupadas"
                  value={unitStats.occupied}
                  icon={<CheckCircle className="w-6 h-6" />}
                  iconColor="success"
                />
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                <StatCard
                  title="Vagas"
                  value={unitStats.vacant}
                  icon={<Home className="w-6 h-6" />}
                  iconColor="warning"
                />
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                <StatCard
                  title="Total Moradores"
                  value={unitStats.totalResidents}
                  icon={<Users className="w-6 h-6" />}
                  iconColor="info"
                />
              </motion.div>
            </StatGrid>

            {/* Units Table */}
            <Card className="mt-6">
              <CardHeader
                title="Lista de Unidades"
                action={
                  <Input
                    placeholder="Buscar unidades..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-64"
                  />
                }
              />
              <CardBody className="p-0">
                <DataTable
                  columns={unitColumns}
                  data={filteredUnits}
                  onRowClick={(row) => { setSelectedUnit(row); setShowUnitModal(true); }}
                />
              </CardBody>
            </Card>
          </TabsContent>

          <TabsContent value="residents">
            {/* Resident Stats */}
            <StatGrid columns={4}>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <StatCard
                  title="Total de Moradores"
                  value={residentStats.total}
                  icon={<Users className="w-6 h-6" />}
                  iconColor="primary"
                />
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                <StatCard
                  title="Ativos"
                  value={residentStats.active}
                  icon={<CheckCircle className="w-6 h-6" />}
                  iconColor="success"
                />
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                <StatCard
                  title="Proprietários"
                  value={residentStats.owners}
                  icon={<Key className="w-6 h-6" />}
                  iconColor="info"
                />
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                <StatCard
                  title="Inquilinos"
                  value={residentStats.tenants}
                  icon={<User className="w-6 h-6" />}
                  iconColor="warning"
                />
              </motion.div>
            </StatGrid>

            {/* Residents Table */}
            <Card className="mt-6">
              <CardHeader
                title="Lista de Moradores"
                action={
                  <Input
                    placeholder="Buscar moradores..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-64"
                  />
                }
              />
              <CardBody className="p-0">
                <DataTable
                  columns={residentColumns}
                  data={filteredResidents}
                  onRowClick={(row) => { setSelectedResident(row); setShowResidentModal(true); }}
                />
              </CardBody>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Unit Detail Modal */}
        <Modal
          isOpen={showUnitModal}
          onClose={() => setShowUnitModal(false)}
          title={selectedUnit ? `Bloco ${selectedUnit.block} - ${selectedUnit.number}` : ''}
          size="lg"
        >
          {selectedUnit && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <Badge variant={unitStatusConfig[selectedUnit.status].variant} size="lg">
                  {unitStatusConfig[selectedUnit.status].label}
                </Badge>
                <Badge variant="secondary">{unitTypeLabels[selectedUnit.type]}</Badge>
                <span className="text-text-secondary">{selectedUnit.area}m²</span>
                {selectedUnit.bedrooms && <span className="text-text-secondary">{selectedUnit.bedrooms} quartos</span>}
              </div>

              {selectedUnit.owner && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-3">Proprietário</h4>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-accent-primary/20 flex items-center justify-center">
                      <User className="w-6 h-6 text-accent-primary" />
                    </div>
                    <div>
                      <p className="font-semibold">{selectedUnit.owner.name}</p>
                      <p className="text-sm text-text-secondary">{selectedUnit.owner.email}</p>
                      <p className="text-sm text-text-secondary">{selectedUnit.owner.phone}</p>
                    </div>
                  </div>
                </div>
              )}

              {selectedUnit.tenant && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-3">Inquilino</h4>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center">
                      <User className="w-6 h-6 text-success" />
                    </div>
                    <div>
                      <p className="font-semibold">{selectedUnit.tenant.name}</p>
                      <p className="text-sm text-text-secondary">{selectedUnit.tenant.email}</p>
                      <p className="text-sm text-text-secondary">Contrato até: {new Date(selectedUnit.tenant.leaseEnd).toLocaleDateString('pt-BR')}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <Users className="w-6 h-6 text-accent-primary mx-auto mb-2" />
                  <p className="text-2xl font-bold">{selectedUnit.residents}</p>
                  <p className="text-xs text-text-secondary">Moradores</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <Car className="w-6 h-6 text-info mx-auto mb-2" />
                  <p className="text-2xl font-bold">{selectedUnit.vehicles}</p>
                  <p className="text-xs text-text-secondary">Veículos</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <Shield className="w-6 h-6 text-warning mx-auto mb-2" />
                  <p className="text-2xl font-bold">{selectedUnit.pets}</p>
                  <p className="text-xs text-text-secondary">Pets</p>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" onClick={() => setShowUnitModal(false)}>Fechar</Button>
                <Button variant="primary" leftIcon={<UserPlus className="w-4 h-4" />}>Adicionar Morador</Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Resident Detail Modal */}
        <Modal
          isOpen={showResidentModal}
          onClose={() => setShowResidentModal(false)}
          title={selectedResident?.name || ''}
          size="lg"
        >
          {selectedResident && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <Badge variant={residentStatusConfig[selectedResident.status].variant} size="lg">
                  {residentStatusConfig[selectedResident.status].label}
                </Badge>
                <Badge variant={residentTypeConfig[selectedResident.type].variant}>
                  {residentTypeConfig[selectedResident.type].label}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-3">Dados Pessoais</h4>
                  <div className="space-y-2">
                    <p className="flex items-center gap-2"><Mail className="w-4 h-4 text-text-muted" /> {selectedResident.email}</p>
                    <p className="flex items-center gap-2"><Phone className="w-4 h-4 text-text-muted" /> {selectedResident.phone}</p>
                    <p className="flex items-center gap-2"><FileText className="w-4 h-4 text-text-muted" /> {selectedResident.cpf}</p>
                  </div>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-3">Unidade</h4>
                  <p className="text-xl font-bold">Bloco {selectedResident.unit.block} - {selectedResident.unit.number}</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <h4 className="text-sm font-medium text-text-secondary mb-3">Métodos de Acesso</h4>
                <div className="flex gap-2">
                  {selectedResident.accessMethods.map((method) => {
                    const Icon = accessMethodIcons[method] || Key;
                    return (
                      <div key={method} className="flex items-center gap-2 px-3 py-2 bg-bg-elevated rounded-lg">
                        <Icon className="w-4 h-4 text-accent-primary" />
                        <span className="text-sm capitalize">{method}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {selectedResident.vehicles.length > 0 && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <h4 className="text-sm font-medium text-text-secondary mb-3">Veículos</h4>
                  <div className="space-y-2">
                    {selectedResident.vehicles.map((vehicle, index) => (
                      <div key={index} className="flex items-center gap-4 p-2 bg-bg-elevated rounded">
                        <Car className="w-5 h-5 text-text-muted" />
                        <div>
                          <p className="font-medium">{vehicle.plate}</p>
                          <p className="text-xs text-text-secondary">{vehicle.model} - {vehicle.color}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
                <Button variant="outline" onClick={() => setShowResidentModal(false)}>Fechar</Button>
                <Button variant="outline" leftIcon={<QrCode className="w-4 h-4" />}>Gerar QR Code</Button>
                <Button variant="primary" leftIcon={<Edit className="w-4 h-4" />}>Editar</Button>
              </div>
            </div>
          )}
        </Modal>

        {/* New Unit Modal */}
        <Modal isOpen={showNewUnitModal} onClose={() => setShowNewUnitModal(false)} title="Nova Unidade">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Número" placeholder="Ex: 101" required />
              <Input label="Bloco" placeholder="Ex: A" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo"
                options={[
                  { value: 'apartment', label: 'Apartamento' },
                  { value: 'house', label: 'Casa' },
                  { value: 'commercial', label: 'Comercial' },
                  { value: 'storage', label: 'Depósito' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
              <Input label="Área (m²)" type="number" placeholder="Ex: 85" required />
            </div>
            <Input label="Quartos" type="number" placeholder="Ex: 3" />
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewUnitModal(false)}>Cancelar</Button>
              <Button variant="primary">Criar Unidade</Button>
            </div>
          </div>
        </Modal>

        {/* New Resident Modal */}
        <Modal isOpen={showNewResidentModal} onClose={() => setShowNewResidentModal(false)} title="Novo Morador">
          <div className="space-y-4">
            <Input label="Nome Completo" placeholder="Nome do morador" required />
            <div className="grid grid-cols-2 gap-4">
              <Input label="CPF" placeholder="000.000.000-00" required />
              <Input label="Telefone" placeholder="(11) 99999-9999" required />
            </div>
            <Input label="Email" type="email" placeholder="email@exemplo.com" required />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Unidade"
                options={units.map(u => ({ value: u.id, label: `Bloco ${u.block} - ${u.number}` }))}
                value=""
                onChange={() => {}}
                required
              />
              <Select
                label="Tipo"
                options={[
                  { value: 'owner', label: 'Proprietário' },
                  { value: 'tenant', label: 'Inquilino' },
                  { value: 'dependent', label: 'Dependente' },
                  { value: 'employee', label: 'Funcionário' },
                ]}
                value=""
                onChange={() => {}}
                required
              />
            </div>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setShowNewResidentModal(false)}>Cancelar</Button>
              <Button variant="primary">Criar Morador</Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
