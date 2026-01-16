'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Users,
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Briefcase,
  Building2,
  Eye,
  Edit,
  Download,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  DollarSign,
  Award,
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
interface Employee {
  id: string;
  name: string;
  cpf: string;
  email: string;
  phone: string;
  photo: string | null;
  position: string;
  department: 'operations' | 'administrative' | 'commercial' | 'hr' | 'financial' | 'ti';
  type: 'clt' | 'pj' | 'temporary' | 'intern';
  status: 'active' | 'inactive' | 'vacation' | 'leave' | 'terminated';
  hireDate: string;
  terminationDate: string | null;
  salary: number;
  workSchedule: string;
  allocatedTo: string | null;
  manager: string | null;
  documents: {
    rg: boolean;
    cpf: boolean;
    ctps: boolean;
    comprovante: boolean;
  };
}

// Mock Data
const employees: Employee[] = [
  {
    id: '1',
    name: 'Carlos Eduardo Silva',
    cpf: '123.456.789-00',
    email: 'carlos.silva@conectaplus.com.br',
    phone: '(11) 99999-1234',
    photo: null,
    position: 'Supervisor de Operações',
    department: 'operations',
    type: 'clt',
    status: 'active',
    hireDate: '2022-03-15',
    terminationDate: null,
    salary: 4500,
    workSchedule: '44h semanais',
    allocatedTo: 'Shopping Center Norte',
    manager: 'Ana Paula Costa',
    documents: { rg: true, cpf: true, ctps: true, comprovante: true },
  },
  {
    id: '2',
    name: 'Ana Paula Costa',
    cpf: '234.567.890-01',
    email: 'ana.costa@conectaplus.com.br',
    phone: '(11) 98888-5678',
    photo: null,
    position: 'Gerente Operacional',
    department: 'operations',
    type: 'clt',
    status: 'active',
    hireDate: '2020-01-10',
    terminationDate: null,
    salary: 8500,
    workSchedule: '44h semanais',
    allocatedTo: null,
    manager: null,
    documents: { rg: true, cpf: true, ctps: true, comprovante: true },
  },
  {
    id: '3',
    name: 'Roberto Santos',
    cpf: '345.678.901-02',
    email: 'roberto.santos@conectaplus.com.br',
    phone: '(11) 97777-9012',
    photo: null,
    position: 'Vigilante',
    department: 'operations',
    type: 'clt',
    status: 'active',
    hireDate: '2023-06-01',
    terminationDate: null,
    salary: 2200,
    workSchedule: '12x36',
    allocatedTo: 'Hospital São Lucas',
    manager: 'Carlos Eduardo Silva',
    documents: { rg: true, cpf: true, ctps: true, comprovante: true },
  },
  {
    id: '4',
    name: 'Maria Oliveira',
    cpf: '456.789.012-03',
    email: 'maria.oliveira@conectaplus.com.br',
    phone: '(11) 96666-3456',
    photo: null,
    position: 'Analista Financeiro',
    department: 'financial',
    type: 'clt',
    status: 'active',
    hireDate: '2021-09-15',
    terminationDate: null,
    salary: 5200,
    workSchedule: '44h semanais',
    allocatedTo: null,
    manager: null,
    documents: { rg: true, cpf: true, ctps: true, comprovante: true },
  },
  {
    id: '5',
    name: 'Pedro Almeida',
    cpf: '567.890.123-04',
    email: 'pedro.almeida@conectaplus.com.br',
    phone: '(11) 95555-7890',
    photo: null,
    position: 'Vigilante',
    department: 'operations',
    type: 'clt',
    status: 'vacation',
    hireDate: '2022-11-20',
    terminationDate: null,
    salary: 2200,
    workSchedule: '12x36',
    allocatedTo: 'Tech Park Empresarial',
    manager: 'Carlos Eduardo Silva',
    documents: { rg: true, cpf: true, ctps: true, comprovante: false },
  },
  {
    id: '6',
    name: 'Fernanda Lima',
    cpf: '678.901.234-05',
    email: 'fernanda.lima@conectaplus.com.br',
    phone: '(11) 94444-1234',
    photo: null,
    position: 'Técnico de TI',
    department: 'ti',
    type: 'pj',
    status: 'active',
    hireDate: '2024-02-01',
    terminationDate: null,
    salary: 6000,
    workSchedule: 'Flexível',
    allocatedTo: null,
    manager: null,
    documents: { rg: true, cpf: true, ctps: false, comprovante: true },
  },
];

const departmentConfig = {
  operations: { label: 'Operações', color: 'primary' as const },
  administrative: { label: 'Administrativo', color: 'info' as const },
  commercial: { label: 'Comercial', color: 'success' as const },
  hr: { label: 'RH', color: 'warning' as const },
  financial: { label: 'Financeiro', color: 'success' as const },
  ti: { label: 'TI', color: 'info' as const },
};

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const, icon: CheckCircle2 },
  inactive: { label: 'Inativo', color: 'danger' as const, icon: XCircle },
  vacation: { label: 'Férias', color: 'warning' as const, icon: Clock },
  leave: { label: 'Afastado', color: 'warning' as const, icon: Clock },
  terminated: { label: 'Desligado', color: 'danger' as const, icon: XCircle },
};

const typeConfig = {
  clt: { label: 'CLT', color: 'primary' as const },
  pj: { label: 'PJ', color: 'info' as const },
  temporary: { label: 'Temporário', color: 'warning' as const },
  intern: { label: 'Estagiário', color: 'info' as const },
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const columns: Column<Employee>[] = [
  {
    key: 'employee',
    header: 'Colaborador',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.name} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.cpf}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'position',
    header: 'Cargo',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.position}</p>
        <Badge size="sm" variant={departmentConfig[row.department].color}>
          {departmentConfig[row.department].label}
        </Badge>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Vínculo',
    render: (row) => {
      const config = typeConfig[row.type];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'allocation',
    header: 'Alocação',
    render: (row) => (
      <div className="flex items-center gap-1">
        {row.allocatedTo ? (
          <>
            <Building2 className="w-3 h-3 text-text-muted" />
            <span className="text-sm">{row.allocatedTo}</span>
          </>
        ) : (
          <span className="text-sm text-text-muted">Sede</span>
        )}
      </div>
    ),
  },
  {
    key: 'hireDate',
    header: 'Admissão',
    render: (row) => (
      <span className="text-sm">{row.hireDate}</span>
    ),
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
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function EmployeesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Stats
  const totalEmployees = employees.length;
  const activeCount = employees.filter(e => e.status === 'active').length;
  const vacationCount = employees.filter(e => e.status === 'vacation').length;
  const cltCount = employees.filter(e => e.type === 'clt').length;
  const totalPayroll = employees.filter(e => e.status === 'active').reduce((acc, e) => acc + e.salary, 0);

  const filteredEmployees = employees.filter((emp) => {
    const matchesSearch =
      emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.cpf.includes(searchTerm) ||
      emp.position.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTab =
      selectedTab === 'all' ||
      emp.status === selectedTab ||
      emp.department === selectedTab;

    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Colaboradores
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie todos os funcionários da empresa
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
              Novo Colaborador
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total"
              value={totalEmployees}
              icon={<Users className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Ativos"
              value={activeCount}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Em Férias"
              value={vacationCount}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="CLT"
              value={cltCount}
              icon={<Briefcase className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Folha Mensal"
              value={formatCurrency(totalPayroll)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todos (${employees.length})` },
                  { value: 'active', label: `Ativos (${activeCount})` },
                  { value: 'operations', label: 'Operações' },
                  { value: 'administrative', label: 'Administrativo' },
                  { value: 'vacation', label: `Férias (${vacationCount})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar colaborador..."
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

        {/* Employees Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredEmployees}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => console.log('Employee clicked:', row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Employee Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Novo Colaborador"
          description="Cadastre um novo colaborador"
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
            <Input label="Nome Completo" placeholder="Nome do colaborador" required />
            <div className="grid grid-cols-2 gap-4">
              <Input label="CPF" placeholder="000.000.000-00" required />
              <Input label="RG" placeholder="00.000.000-0" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="E-mail" type="email" placeholder="email@empresa.com" />
              <Input label="Telefone" placeholder="(00) 00000-0000" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Cargo"
                options={[
                  { value: 'vigilante', label: 'Vigilante' },
                  { value: 'supervisor', label: 'Supervisor' },
                  { value: 'gerente', label: 'Gerente' },
                  { value: 'tecnico', label: 'Técnico' },
                  { value: 'analista', label: 'Analista' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Departamento"
                options={[
                  { value: 'operations', label: 'Operações' },
                  { value: 'administrative', label: 'Administrativo' },
                  { value: 'commercial', label: 'Comercial' },
                  { value: 'hr', label: 'RH' },
                  { value: 'financial', label: 'Financeiro' },
                  { value: 'ti', label: 'TI' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Select
                label="Tipo de Vínculo"
                options={[
                  { value: 'clt', label: 'CLT' },
                  { value: 'pj', label: 'PJ' },
                  { value: 'temporary', label: 'Temporário' },
                  { value: 'intern', label: 'Estagiário' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Input label="Data de Admissão" type="date" required />
              <Input label="Salário" type="number" placeholder="0,00" />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
