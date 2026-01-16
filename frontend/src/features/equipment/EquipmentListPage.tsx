'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Eye,
  Edit2,
  Trash2,
  QrCode,
  MapPin,
  Calendar,
  DollarSign,
  Building,
  Tag,
  Printer,
  MoreVertical,
  CheckCircle,
  AlertTriangle,
  Wrench
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { DataTable, Column } from '../../design-system/components/Table';
import { MainLayout } from '../../layouts/MainLayout';

// Types
interface Equipment {
  id: string;
  patrimonyCode: string;
  name: string;
  description: string;
  category: 'ti' | 'veiculos' | 'moveis' | 'maquinas' | 'ferramentas' | 'outros';
  brand: string;
  model: string;
  serialNumber: string;
  purchaseDate: string;
  purchaseValue: number;
  currentValue: number;
  depreciationRate: number;
  location: string;
  responsible: string;
  status: 'active' | 'maintenance' | 'comodato' | 'baixado' | 'perdido';
  condition: 'excellent' | 'good' | 'regular' | 'poor';
  warrantyExpiration: string | null;
  lastMaintenance: string | null;
  nextMaintenance: string | null;
  qrCode: string;
}

// Mock Data
const mockEquipments: Equipment[] = [
  {
    id: '1',
    patrimonyCode: 'PAT-2024-00001',
    name: 'Notebook Dell Latitude 5520',
    description: 'Notebook corporativo para uso administrativo',
    category: 'ti',
    brand: 'Dell',
    model: 'Latitude 5520',
    serialNumber: 'SN123456789',
    purchaseDate: '2024-01-15',
    purchaseValue: 5500,
    currentValue: 5200,
    depreciationRate: 20,
    location: 'Matriz - TI',
    responsible: 'João Silva',
    status: 'active',
    condition: 'excellent',
    warrantyExpiration: '2027-01-15',
    lastMaintenance: '2024-02-01',
    nextMaintenance: '2024-08-01',
    qrCode: 'QR-PAT-2024-00001'
  },
  {
    id: '2',
    patrimonyCode: 'PAT-2024-00002',
    name: 'Veículo Ford Transit',
    description: 'Van para transporte de equipe',
    category: 'veiculos',
    brand: 'Ford',
    model: 'Transit 350L',
    serialNumber: '9BFZF5BN1P8000123',
    purchaseDate: '2023-06-20',
    purchaseValue: 180000,
    currentValue: 155000,
    depreciationRate: 15,
    location: 'Garagem Matriz',
    responsible: 'Frota',
    status: 'active',
    condition: 'good',
    warrantyExpiration: '2026-06-20',
    lastMaintenance: '2024-02-10',
    nextMaintenance: '2024-05-10',
    qrCode: 'QR-PAT-2024-00002'
  },
  {
    id: '3',
    patrimonyCode: 'PAT-2024-00003',
    name: 'Impressora HP LaserJet Pro',
    description: 'Impressora multifuncional laser',
    category: 'ti',
    brand: 'HP',
    model: 'LaserJet Pro M428fdw',
    serialNumber: 'CNBJ5P2K',
    purchaseDate: '2023-09-10',
    purchaseValue: 3200,
    currentValue: 2800,
    depreciationRate: 25,
    location: 'Matriz - Administrativo',
    responsible: 'Administrativo',
    status: 'maintenance',
    condition: 'regular',
    warrantyExpiration: '2025-09-10',
    lastMaintenance: '2024-02-15',
    nextMaintenance: null,
    qrCode: 'QR-PAT-2024-00003'
  },
  {
    id: '4',
    patrimonyCode: 'PAT-2024-00004',
    name: 'Mesa de Escritório L',
    description: 'Mesa em L com gaveteiro',
    category: 'moveis',
    brand: 'Flexform',
    model: 'Executive L',
    serialNumber: 'FF-2024-1234',
    purchaseDate: '2024-01-05',
    purchaseValue: 1800,
    currentValue: 1750,
    depreciationRate: 10,
    location: 'Matriz - Diretoria',
    responsible: 'Diretoria',
    status: 'active',
    condition: 'excellent',
    warrantyExpiration: '2029-01-05',
    lastMaintenance: null,
    nextMaintenance: null,
    qrCode: 'QR-PAT-2024-00004'
  },
  {
    id: '5',
    patrimonyCode: 'PAT-2024-00005',
    name: 'Servidor Dell PowerEdge R740',
    description: 'Servidor para datacenter',
    category: 'ti',
    brand: 'Dell',
    model: 'PowerEdge R740',
    serialNumber: 'SVRDL7409876',
    purchaseDate: '2022-03-15',
    purchaseValue: 45000,
    currentValue: 32000,
    depreciationRate: 20,
    location: 'Datacenter',
    responsible: 'TI',
    status: 'active',
    condition: 'good',
    warrantyExpiration: '2025-03-15',
    lastMaintenance: '2024-01-20',
    nextMaintenance: '2024-07-20',
    qrCode: 'QR-PAT-2024-00005'
  },
  {
    id: '6',
    patrimonyCode: 'PAT-2023-00156',
    name: 'Projetor Epson EB-X41',
    description: 'Projetor para apresentações',
    category: 'ti',
    brand: 'Epson',
    model: 'EB-X41',
    serialNumber: 'EPXB41-2023-001',
    purchaseDate: '2023-02-10',
    purchaseValue: 2800,
    currentValue: 2100,
    depreciationRate: 25,
    location: 'Cliente - Tech Solutions',
    responsible: 'Comercial',
    status: 'comodato',
    condition: 'good',
    warrantyExpiration: '2025-02-10',
    lastMaintenance: '2023-12-15',
    nextMaintenance: '2024-06-15',
    qrCode: 'QR-PAT-2023-00156'
  }
];

export function EquipmentListPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [showEquipmentModal, setShowEquipmentModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);

  const getCategoryInfo = (category: Equipment['category']) => {
    const categories = {
      ti: { label: 'TI & Informática', color: 'primary' as const },
      veiculos: { label: 'Veículos', color: 'success' as const },
      moveis: { label: 'Móveis', color: 'warning' as const },
      maquinas: { label: 'Máquinas', color: 'danger' as const },
      ferramentas: { label: 'Ferramentas', color: 'info' as const },
      outros: { label: 'Outros', color: 'info' as const }
    };
    return categories[category];
  };

  const getStatusInfo = (status: Equipment['status']) => {
    const statuses = {
      active: { label: 'Ativo', color: 'success' as const },
      maintenance: { label: 'Em Manutenção', color: 'warning' as const },
      comodato: { label: 'Comodato', color: 'info' as const },
      baixado: { label: 'Baixado', color: 'info' as const },
      perdido: { label: 'Perdido', color: 'danger' as const }
    };
    return statuses[status];
  };

  const getConditionInfo = (condition: Equipment['condition']) => {
    const conditions = {
      excellent: { label: 'Excelente', color: 'success' as const },
      good: { label: 'Bom', color: 'info' as const },
      regular: { label: 'Regular', color: 'warning' as const },
      poor: { label: 'Ruim', color: 'danger' as const }
    };
    return conditions[condition];
  };

  const columns: Column<Equipment>[] = [
    {
      key: 'patrimonyCode',
      header: 'Patrimônio',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-accent-primary/20">
            <Package className="h-4 w-4 text-accent-primary" />
          </div>
          <div>
            <span className="font-mono text-text-primary text-sm">{row.patrimonyCode}</span>
            <button
              onClick={() => { setSelectedEquipment(row); setShowQRModal(true); }}
              className="ml-2 text-text-secondary hover:text-accent-primary transition-colors"
            >
              <QrCode className="h-3 w-3" />
            </button>
          </div>
        </div>
      )
    },
    {
      key: 'name',
      header: 'Equipamento',
      sortable: true,
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-secondary">{row.brand} - {row.model}</p>
        </div>
      )
    },
    {
      key: 'category',
      header: 'Categoria',
      sortable: true,
      render: (row) => {
        const info = getCategoryInfo(row.category);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
    },
    {
      key: 'location',
      header: 'Localização',
      sortable: true,
      render: (row) => (
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-text-secondary" />
          <span className="text-text-primary text-sm">{row.location}</span>
        </div>
      )
    },
    {
      key: 'currentValue',
      header: 'Valor Atual',
      sortable: true,
      render: (row) => (
        <div>
          <p className="font-medium text-text-primary">
            {row.currentValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </p>
          <p className="text-xs text-text-secondary">
            Compra: {row.purchaseValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </p>
        </div>
      )
    },
    {
      key: 'condition',
      header: 'Condição',
      sortable: true,
      render: (row) => {
        const info = getConditionInfo(row.condition);
        return <Badge variant={info.color} size="sm">{info.label}</Badge>;
      }
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
          <Button variant="ghost" size="sm" onClick={() => { setSelectedEquipment(row); }}>
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Printer className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const filteredEquipments = mockEquipments.filter(equipment => {
    const matchesSearch =
      equipment.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      equipment.patrimonyCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
      equipment.serialNumber.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || equipment.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || equipment.status === selectedStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const totalValue = mockEquipments.reduce((sum, eq) => sum + eq.currentValue, 0);
  const activeCount = mockEquipments.filter(eq => eq.status === 'active').length;
  const maintenanceCount = mockEquipments.filter(eq => eq.status === 'maintenance').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Inventário de Equipamentos
            </h1>
            <p className="text-text-secondary mt-1">
              Cadastro e controle de patrimônio
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Upload className="h-4 w-4 mr-2" />
              Importar
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button variant="primary" onClick={() => setShowEquipmentModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Equipamento
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <StatCard
            title="Total de Equipamentos"
            value={mockEquipments.length.toString()}
            icon={<Package className="h-5 w-5" />}
          />
          <StatCard
            title="Valor Total"
            value={totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<DollarSign className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Ativos"
            value={activeCount.toString()}
            changeLabel={`${((activeCount / mockEquipments.length) * 100).toFixed(0)}% do total`}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Em Manutenção"
            value={maintenanceCount.toString()}
            icon={<Wrench className="h-5 w-5" />}
            iconColor="warning"
          />
        </StatGrid>

        {/* Filters and Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Lista de Equipamentos
              </h3>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                  <Input
                    placeholder="Buscar por nome, patrimônio ou serial..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-80"
                  />
                </div>
                <select
                  className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary text-sm"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="all">Todas categorias</option>
                  <option value="ti">TI & Informática</option>
                  <option value="veiculos">Veículos</option>
                  <option value="moveis">Móveis</option>
                  <option value="maquinas">Máquinas</option>
                  <option value="ferramentas">Ferramentas</option>
                  <option value="outros">Outros</option>
                </select>
                <select
                  className="px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary text-sm"
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                >
                  <option value="all">Todos os status</option>
                  <option value="active">Ativo</option>
                  <option value="maintenance">Em Manutenção</option>
                  <option value="comodato">Comodato</option>
                  <option value="baixado">Baixado</option>
                </select>
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <DataTable<Equipment>
              data={filteredEquipments}
              columns={columns}
              keyExtractor={(row) => row.id}
            />
          </CardBody>
        </Card>

        {/* New Equipment Modal */}
        <Modal
          isOpen={showEquipmentModal}
          onClose={() => setShowEquipmentModal(false)}
          title="Novo Equipamento"
          size="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Código Patrimônio
                </label>
                <Input placeholder="Gerado automaticamente" disabled />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Categoria *
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="">Selecione...</option>
                  <option value="ti">TI & Informática</option>
                  <option value="veiculos">Veículos</option>
                  <option value="moveis">Móveis</option>
                  <option value="maquinas">Máquinas</option>
                  <option value="ferramentas">Ferramentas</option>
                  <option value="outros">Outros</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nome do Equipamento *
              </label>
              <Input placeholder="Ex: Notebook Dell Latitude 5520" />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Descrição
              </label>
              <textarea
                className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                rows={2}
                placeholder="Descrição detalhada do equipamento..."
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Marca *
                </label>
                <Input placeholder="Ex: Dell" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Modelo *
                </label>
                <Input placeholder="Ex: Latitude 5520" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Número de Série
                </label>
                <Input placeholder="Ex: SN123456789" />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Data de Aquisição *
                </label>
                <Input type="date" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Valor de Compra *
                </label>
                <Input type="number" step="0.01" placeholder="0,00" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Taxa Depreciação (% a.a.)
                </label>
                <Input type="number" placeholder="20" defaultValue={20} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Localização *
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="">Selecione...</option>
                  <option value="matriz">Matriz</option>
                  <option value="filial-sp">Filial SP</option>
                  <option value="filial-rj">Filial RJ</option>
                  <option value="cd">CD Logístico</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Responsável
                </label>
                <Input placeholder="Nome do responsável ou setor" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Condição
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="excellent">Excelente</option>
                  <option value="good">Bom</option>
                  <option value="regular">Regular</option>
                  <option value="poor">Ruim</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Vencimento Garantia
                </label>
                <Input type="date" />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="ghost" onClick={() => setShowEquipmentModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                Cadastrar Equipamento
              </Button>
            </div>
          </div>
        </Modal>

        {/* QR Code Modal */}
        <Modal
          isOpen={showQRModal}
          onClose={() => setShowQRModal(false)}
          title="QR Code do Equipamento"
          size="sm"
        >
          {selectedEquipment && (
            <div className="text-center space-y-4">
              <div className="bg-white p-6 rounded-lg inline-block">
                <div className="w-48 h-48 bg-gray-200 flex items-center justify-center">
                  <QrCode className="h-32 w-32 text-gray-800" />
                </div>
              </div>
              <div>
                <p className="font-mono text-lg text-text-primary">{selectedEquipment.patrimonyCode}</p>
                <p className="text-text-secondary">{selectedEquipment.name}</p>
              </div>
              <div className="flex justify-center gap-3">
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Baixar PNG
                </Button>
                <Button variant="primary">
                  <Printer className="h-4 w-4 mr-2" />
                  Imprimir Etiqueta
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}

export default EquipmentListPage;
