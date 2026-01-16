'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Briefcase,
  Search,
  Plus,
  Download,
  Edit,
  Eye,
  Trash2,
  DollarSign,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Tag,
  Settings,
  Copy,
  Archive,
  Filter,
  MoreVertical,
  Shield,
  Users,
  Building2,
  Wrench,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
} from '@/design-system/components';

// Types
interface Service {
  id: string;
  code: string;
  name: string;
  category: 'security' | 'cleaning' | 'reception' | 'facilities' | 'consulting';
  description: string;
  unit: 'hour' | 'month' | 'shift' | 'event' | 'project';
  basePrice: number;
  costComponents: {
    labor: number;
    materials: number;
    overhead: number;
    margin: number;
  };
  status: 'active' | 'inactive' | 'draft';
  contractsCount: number;
  revenue: number;
  createdAt: string;
}

interface PriceTable {
  id: string;
  name: string;
  validFrom: string;
  validTo: string | null;
  status: 'active' | 'expired' | 'scheduled';
  servicesCount: number;
  adjustment: number;
}

interface ServiceComponent {
  id: string;
  name: string;
  type: 'labor' | 'material' | 'equipment' | 'overhead';
  unit: string;
  unitCost: number;
  description: string;
}

// Mock Data
const services: Service[] = [
  {
    id: '1',
    code: 'SRV-001',
    name: 'Vigilância Patrimonial 24h',
    category: 'security',
    description: 'Serviço de vigilância armada com cobertura 24 horas',
    unit: 'month',
    basePrice: 18500.00,
    costComponents: { labor: 12000, materials: 500, overhead: 2000, margin: 4000 },
    status: 'active',
    contractsCount: 45,
    revenue: 832500.00,
    createdAt: '2024-01-15',
  },
  {
    id: '2',
    code: 'SRV-002',
    name: 'Portaria e Controle de Acesso',
    category: 'reception',
    description: 'Serviço de portaria com controle de acesso de pessoas e veículos',
    unit: 'month',
    basePrice: 12800.00,
    costComponents: { labor: 8500, materials: 300, overhead: 1500, margin: 2500 },
    status: 'active',
    contractsCount: 32,
    revenue: 409600.00,
    createdAt: '2024-02-20',
  },
  {
    id: '3',
    code: 'SRV-003',
    name: 'Monitoramento CFTV',
    category: 'security',
    description: 'Monitoramento remoto de câmeras com central 24h',
    unit: 'month',
    basePrice: 8500.00,
    costComponents: { labor: 5000, materials: 200, overhead: 1300, margin: 2000 },
    status: 'active',
    contractsCount: 28,
    revenue: 238000.00,
    createdAt: '2024-03-10',
  },
  {
    id: '4',
    code: 'SRV-004',
    name: 'Segurança para Eventos',
    category: 'security',
    description: 'Equipe de segurança para eventos corporativos e sociais',
    unit: 'event',
    basePrice: 4500.00,
    costComponents: { labor: 3000, materials: 200, overhead: 500, margin: 800 },
    status: 'active',
    contractsCount: 12,
    revenue: 54000.00,
    createdAt: '2024-04-05',
  },
  {
    id: '5',
    code: 'SRV-005',
    name: 'Limpeza e Conservação',
    category: 'cleaning',
    description: 'Serviço de limpeza profissional para áreas comuns',
    unit: 'month',
    basePrice: 9200.00,
    costComponents: { labor: 6000, materials: 800, overhead: 1200, margin: 1200 },
    status: 'active',
    contractsCount: 18,
    revenue: 165600.00,
    createdAt: '2024-05-12',
  },
  {
    id: '6',
    code: 'SRV-006',
    name: 'Consultoria em Segurança',
    category: 'consulting',
    description: 'Análise de riscos e elaboração de planos de segurança',
    unit: 'project',
    basePrice: 25000.00,
    costComponents: { labor: 15000, materials: 1000, overhead: 3000, margin: 6000 },
    status: 'draft',
    contractsCount: 0,
    revenue: 0,
    createdAt: '2026-01-10',
  },
];

const priceTables: PriceTable[] = [
  {
    id: '1',
    name: 'Tabela Padrão 2026',
    validFrom: '2026-01-01',
    validTo: null,
    status: 'active',
    servicesCount: 15,
    adjustment: 5.5,
  },
  {
    id: '2',
    name: 'Tabela Governo/Licitações',
    validFrom: '2026-01-01',
    validTo: null,
    status: 'active',
    servicesCount: 10,
    adjustment: -8.0,
  },
  {
    id: '3',
    name: 'Tabela Premium',
    validFrom: '2026-01-01',
    validTo: null,
    status: 'active',
    servicesCount: 12,
    adjustment: 15.0,
  },
  {
    id: '4',
    name: 'Tabela 2025 (Antiga)',
    validFrom: '2025-01-01',
    validTo: '2025-12-31',
    status: 'expired',
    servicesCount: 14,
    adjustment: 0,
  },
];

const components: ServiceComponent[] = [
  { id: '1', name: 'Vigilante (12x36)', type: 'labor', unit: 'mês', unitCost: 4200.00, description: 'Custo total por vigilante em escala 12x36' },
  { id: '2', name: 'Supervisor de Segurança', type: 'labor', unit: 'mês', unitCost: 6500.00, description: 'Custo total por supervisor' },
  { id: '3', name: 'Uniforme Completo', type: 'material', unit: 'conjunto', unitCost: 350.00, description: 'Kit uniforme padrão' },
  { id: '4', name: 'Rádio Comunicador', type: 'equipment', unit: 'mês', unitCost: 80.00, description: 'Aluguel de rádio comunicador' },
  { id: '5', name: 'Encargos Sociais', type: 'overhead', unit: '%', unitCost: 68.5, description: 'Percentual sobre mão de obra' },
];

const categoryConfig = {
  security: { label: 'Segurança', color: 'primary' as const, icon: Shield },
  cleaning: { label: 'Limpeza', color: 'success' as const, icon: Wrench },
  reception: { label: 'Recepção', color: 'info' as const, icon: Users },
  facilities: { label: 'Facilities', color: 'warning' as const, icon: Building2 },
  consulting: { label: 'Consultoria', color: 'primary' as const, icon: Briefcase },
};

const unitLabels = {
  hour: 'Hora',
  month: 'Mês',
  shift: 'Turno',
  event: 'Evento',
  project: 'Projeto',
};

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const },
  inactive: { label: 'Inativo', color: 'neutral' as const },
  draft: { label: 'Rascunho', color: 'warning' as const },
};

const tableStatusConfig = {
  active: { label: 'Vigente', color: 'success' as const },
  expired: { label: 'Expirada', color: 'neutral' as const },
  scheduled: { label: 'Agendada', color: 'info' as const },
};

const componentTypeConfig = {
  labor: { label: 'Mão de Obra', color: 'primary' as const },
  material: { label: 'Material', color: 'info' as const },
  equipment: { label: 'Equipamento', color: 'warning' as const },
  overhead: { label: 'Encargo', color: 'neutral' as const },
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

const serviceColumns: Column<Service>[] = [
  {
    key: 'name',
    header: 'Serviço',
    render: (row) => {
      const config = categoryConfig[row.category];
      const CategoryIcon = config.icon;
      return (
        <div className="flex items-center gap-3">
          <div className="p-2 bg-bg-tertiary rounded-lg">
            <CategoryIcon className="w-5 h-5 text-text-muted" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.code}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => {
      const config = categoryConfig[row.category];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'unit',
    header: 'Unidade',
    render: (row) => <span className="text-sm">{unitLabels[row.unit]}</span>,
  },
  {
    key: 'basePrice',
    header: 'Preço Base',
    render: (row) => <span className="font-medium">{formatCurrency(row.basePrice)}</span>,
  },
  {
    key: 'contractsCount',
    header: 'Contratos',
    render: (row) => <span className="text-sm">{row.contractsCount}</span>,
  },
  {
    key: 'revenue',
    header: 'Receita Mensal',
    render: (row) => (
      <span className="font-medium text-accent-success">{formatCurrency(row.revenue)}</span>
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
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Duplicar">
          <Copy className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const tableColumns: Column<PriceTable>[] = [
  {
    key: 'name',
    header: 'Tabela',
    render: (row) => <span className="font-medium text-text-primary">{row.name}</span>,
  },
  {
    key: 'validFrom',
    header: 'Vigência',
    render: (row) => (
      <div className="text-sm">
        <p>{new Date(row.validFrom).toLocaleDateString('pt-BR')}</p>
        {row.validTo && (
          <p className="text-text-muted">até {new Date(row.validTo).toLocaleDateString('pt-BR')}</p>
        )}
      </div>
    ),
  },
  {
    key: 'servicesCount',
    header: 'Serviços',
    render: (row) => <span className="text-sm">{row.servicesCount}</span>,
  },
  {
    key: 'adjustment',
    header: 'Ajuste',
    render: (row) => (
      <span className={`font-medium ${row.adjustment > 0 ? 'text-accent-success' : row.adjustment < 0 ? 'text-accent-danger' : ''}`}>
        {row.adjustment > 0 ? '+' : ''}{row.adjustment}%
      </span>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = tableStatusConfig[row.status];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'active' && (
          <Button variant="ghost" size="icon-sm" title="Editar">
            <Edit className="w-4 h-4" />
          </Button>
        )}
      </div>
    ),
  },
];

const componentColumns: Column<ServiceComponent>[] = [
  {
    key: 'name',
    header: 'Componente',
    render: (row) => <span className="font-medium text-text-primary">{row.name}</span>,
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const config = componentTypeConfig[row.type];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'unit',
    header: 'Unidade',
    render: (row) => <span className="text-sm">{row.unit}</span>,
  },
  {
    key: 'unitCost',
    header: 'Custo Unitário',
    render: (row) => (
      <span className="font-medium">
        {row.type === 'overhead' ? `${row.unitCost}%` : formatCurrency(row.unitCost)}
      </span>
    ),
  },
  {
    key: 'description',
    header: 'Descrição',
    render: (row) => <span className="text-sm text-text-secondary">{row.description}</span>,
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function ServicesPage() {
  const [selectedTab, setSelectedTab] = useState('services');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Stats
  const totalServices = services.filter(s => s.status === 'active').length;
  const totalRevenue = services.reduce((acc, s) => acc + s.revenue, 0);
  const totalContracts = services.reduce((acc, s) => acc + s.contractsCount, 0);
  const activeTables = priceTables.filter(t => t.status === 'active').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Catálogo de Serviços
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão de serviços, preços e componentes
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
              Novo Serviço
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Serviços Ativos"
              value={totalServices}
              icon={<Briefcase className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Receita Mensal"
              value={formatCurrency(totalRevenue)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
              trend="up"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Contratos Ativos"
              value={totalContracts}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Tabelas Vigentes"
              value={activeTables}
              icon={<Tag className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Service Categories */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">Receita por Categoria</h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(categoryConfig).map(([key, config]) => {
                  const categoryServices = services.filter(s => s.category === key && s.status === 'active');
                  const categoryRevenue = categoryServices.reduce((acc, s) => acc + s.revenue, 0);
                  const CategoryIcon = config.icon;
                  return (
                    <div key={key} className="p-4 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <CategoryIcon className="w-5 h-5 text-text-muted" />
                        <span className="text-sm font-medium text-text-primary">{config.label}</span>
                      </div>
                      <p className="text-lg font-bold text-text-primary">{formatCurrency(categoryRevenue)}</p>
                      <p className="text-xs text-text-muted">{categoryServices.length} serviços</p>
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>
        </motion.div>

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'services', label: 'Serviços' },
                { value: 'tables', label: 'Tabelas de Preço' },
                { value: 'components', label: 'Componentes de Custo' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardBody className="border-b border-border-subtle">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Buscar..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                {selectedTab === 'services' && (
                  <>
                    <Select
                      options={[
                        { value: 'all', label: 'Todas Categorias' },
                        { value: 'security', label: 'Segurança' },
                        { value: 'cleaning', label: 'Limpeza' },
                        { value: 'reception', label: 'Recepção' },
                        { value: 'facilities', label: 'Facilities' },
                        { value: 'consulting', label: 'Consultoria' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-44"
                    />
                    <Select
                      options={[
                        { value: 'all', label: 'Todos Status' },
                        { value: 'active', label: 'Ativos' },
                        { value: 'inactive', label: 'Inativos' },
                        { value: 'draft', label: 'Rascunho' },
                      ]}
                      value="all"
                      onChange={() => {}}
                      className="w-40"
                    />
                  </>
                )}
              </div>
            </CardBody>
            <CardBody className="p-0">
              {selectedTab === 'services' ? (
                <DataTable
                  columns={serviceColumns}
                  data={services}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'tables' ? (
                <DataTable
                  columns={tableColumns}
                  data={priceTables}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <DataTable
                  columns={componentColumns}
                  data={components}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* New Service Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Novo Serviço"
          description="Cadastre um novo serviço no catálogo"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar Serviço
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <Input label="Código" placeholder="SRV-XXX" />
              <div className="col-span-2">
                <Input label="Nome do Serviço" placeholder="Nome do serviço..." />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Categoria"
                options={[
                  { value: 'security', label: 'Segurança' },
                  { value: 'cleaning', label: 'Limpeza' },
                  { value: 'reception', label: 'Recepção' },
                  { value: 'facilities', label: 'Facilities' },
                  { value: 'consulting', label: 'Consultoria' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Unidade de Cobrança"
                options={[
                  { value: 'hour', label: 'Por Hora' },
                  { value: 'month', label: 'Mensal' },
                  { value: 'shift', label: 'Por Turno' },
                  { value: 'event', label: 'Por Evento' },
                  { value: 'project', label: 'Por Projeto' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Descrição</label>
              <textarea
                className="w-full h-20 px-3 py-2 bg-bg-tertiary border border-border-default rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent"
                placeholder="Descreva o serviço..."
              />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="text-sm font-medium text-text-primary mb-3">Composição de Custo</h4>
              <div className="grid grid-cols-2 gap-4">
                <Input label="Mão de Obra" type="number" placeholder="R$ 0,00" />
                <Input label="Materiais" type="number" placeholder="R$ 0,00" />
                <Input label="Encargos" type="number" placeholder="R$ 0,00" />
                <Input label="Margem (%)" type="number" placeholder="0%" />
              </div>
            </div>
            <Input label="Preço Base" type="number" placeholder="R$ 0,00" />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
