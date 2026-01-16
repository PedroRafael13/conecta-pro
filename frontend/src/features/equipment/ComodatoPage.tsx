'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Edit2,
  Calendar,
  Clock,
  User,
  Package,
  FileText,
  CheckCircle,
  AlertTriangle,
  XCircle,
  RefreshCw,
  ArrowRight,
  ArrowLeft,
  History
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

// Types
interface Comodato {
  id: string;
  comodatoNumber: string;
  equipmentId: string;
  equipmentName: string;
  equipmentCode: string;
  equipmentValue: number;
  clientId: string;
  clientName: string;
  clientCnpj: string;
  responsibleName: string;
  responsibleContact: string;
  startDate: string;
  expectedEndDate: string;
  actualEndDate: string | null;
  status: 'active' | 'expired' | 'returned' | 'cancelled';
  contractUrl: string | null;
  notes: string;
}

// Mock Data
const mockComodatos: Comodato[] = [
  {
    id: '1',
    comodatoNumber: 'CMD-2024-00012',
    equipmentId: '6',
    equipmentName: 'Projetor Epson EB-X41',
    equipmentCode: 'PAT-2023-00156',
    equipmentValue: 2800,
    clientId: 'CLI-001',
    clientName: 'Tech Solutions Ltda',
    clientCnpj: '12.345.678/0001-90',
    responsibleName: 'Maria Santos',
    responsibleContact: '(11) 99999-1234',
    startDate: '2024-01-15',
    expectedEndDate: '2024-03-01',
    actualEndDate: null,
    status: 'active',
    contractUrl: '/contracts/cmd-2024-00012.pdf',
    notes: 'Empréstimo para eventos corporativos'
  },
  {
    id: '2',
    comodatoNumber: 'CMD-2024-00013',
    equipmentId: '7',
    equipmentName: 'Notebook Dell XPS 15',
    equipmentCode: 'PAT-2023-00189',
    equipmentValue: 8500,
    clientId: 'CLI-002',
    clientName: 'Consultoria ABC',
    clientCnpj: '23.456.789/0001-01',
    responsibleName: 'João Silva',
    responsibleContact: '(11) 99999-5678',
    startDate: '2024-01-20',
    expectedEndDate: '2024-02-28',
    actualEndDate: null,
    status: 'expired',
    contractUrl: '/contracts/cmd-2024-00013.pdf',
    notes: 'Uso temporário durante projeto'
  },
  {
    id: '3',
    comodatoNumber: 'CMD-2024-00014',
    equipmentId: '8',
    equipmentName: 'Kit Ferramentas Completo',
    equipmentCode: 'PAT-2023-00201',
    equipmentValue: 3500,
    clientId: 'CLI-003',
    clientName: 'Manutenção Express',
    clientCnpj: '34.567.890/0001-12',
    responsibleName: 'Pedro Oliveira',
    responsibleContact: '(11) 99999-9012',
    startDate: '2024-02-01',
    expectedEndDate: '2024-02-25',
    actualEndDate: null,
    status: 'active',
    contractUrl: '/contracts/cmd-2024-00014.pdf',
    notes: 'Serviço de manutenção em campo'
  },
  {
    id: '4',
    comodatoNumber: 'CMD-2024-00010',
    equipmentId: '9',
    equipmentName: 'Impressora Térmica Zebra',
    equipmentCode: 'PAT-2023-00145',
    equipmentValue: 1800,
    clientId: 'CLI-004',
    clientName: 'Logística Rápida',
    clientCnpj: '45.678.901/0001-23',
    responsibleName: 'Ana Costa',
    responsibleContact: '(11) 99999-3456',
    startDate: '2023-12-15',
    expectedEndDate: '2024-01-31',
    actualEndDate: '2024-01-28',
    status: 'returned',
    contractUrl: '/contracts/cmd-2024-00010.pdf',
    notes: 'Devolvido em perfeito estado'
  }
];

const tabs = [
  { value: 'all', label: 'Todos', icon: <Package className="h-4 w-4" /> },
  { value: 'active', label: 'Ativos', icon: <CheckCircle className="h-4 w-4" /> },
  { value: 'expired', label: 'Vencidos', icon: <AlertTriangle className="h-4 w-4" /> },
  { value: 'returned', label: 'Devolvidos', icon: <ArrowLeft className="h-4 w-4" /> }
];

export function ComodatoPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showComodatoModal, setShowComodatoModal] = useState(false);
  const [showReturnModal, setShowReturnModal] = useState(false);
  const [selectedComodato, setSelectedComodato] = useState<Comodato | null>(null);

  const getStatusInfo = (status: Comodato['status']) => {
    const statuses = {
      active: { label: 'Ativo', color: 'success' as const },
      expired: { label: 'Vencido', color: 'danger' as const },
      returned: { label: 'Devolvido', color: 'info' as const },
      cancelled: { label: 'Cancelado', color: 'info' as const }
    };
    return statuses[status];
  };

  const calculateDaysRemaining = (endDate: string) => {
    const end = new Date(endDate);
    const today = new Date();
    const diff = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const columns: Column<Comodato>[] = [
    {
      key: 'comodatoNumber',
      header: 'Número',
      sortable: true,
      render: (row) => (
        <span className="font-mono text-text-primary">{row.comodatoNumber}</span>
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
      key: 'clientName',
      header: 'Cliente',
      sortable: true,
      render: (row) => (
        <div>
          <div className="flex items-center gap-2">
            <Building className="h-4 w-4 text-text-secondary" />
            <span className="font-medium text-text-primary">{row.clientName}</span>
          </div>
          <p className="text-xs text-text-secondary ml-6">{row.clientCnpj}</p>
        </div>
      )
    },
    {
      key: 'responsibleName',
      header: 'Responsável',
      sortable: true,
      render: (row) => (
        <div>
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-text-secondary" />
            <span className="text-text-primary">{row.responsibleName}</span>
          </div>
          <p className="text-xs text-text-secondary ml-6">{row.responsibleContact}</p>
        </div>
      )
    },
    {
      key: 'startDate',
      header: 'Período',
      sortable: true,
      render: (row) => (
        <div className="text-sm">
          <div className="flex items-center gap-1 text-text-primary">
            <Calendar className="h-3 w-3" />
            {new Date(row.startDate).toLocaleDateString('pt-BR')}
          </div>
          <div className="flex items-center gap-1 text-text-secondary">
            <ArrowRight className="h-3 w-3" />
            {new Date(row.expectedEndDate).toLocaleDateString('pt-BR')}
          </div>
        </div>
      )
    },
    {
      key: 'daysRemaining',
      header: 'Situação',
      render: (row) => {
        if (row.status === 'returned') {
          return (
            <span className="text-text-secondary text-sm">
              Devolvido em {new Date(row.actualEndDate!).toLocaleDateString('pt-BR')}
            </span>
          );
        }
        const days = calculateDaysRemaining(row.expectedEndDate);
        if (days < 0) {
          return (
            <Badge variant="danger" size="sm">
              {Math.abs(days)} dias atrasado
            </Badge>
          );
        } else if (days <= 7) {
          return (
            <Badge variant="warning" size="sm">
              {days} dias restantes
            </Badge>
          );
        } else {
          return (
            <Badge variant="success" size="sm">
              {days} dias restantes
            </Badge>
          );
        }
      }
    },
    {
      key: 'equipmentValue',
      header: 'Valor',
      sortable: true,
      render: (row) => (
        <span className="text-text-primary font-medium">
          {row.equipmentValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
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
          {row.status === 'active' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => { setSelectedComodato(row); setShowReturnModal(true); }}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
          )}
          {row.status === 'expired' && (
            <Button variant="ghost" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
          <Button variant="ghost" size="sm">
            <FileText className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];

  const filteredComodatos = mockComodatos.filter(comodato => {
    const matchesSearch =
      comodato.comodatoNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      comodato.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      comodato.equipmentName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === 'all' || comodato.status === activeTab;
    return matchesSearch && matchesTab;
  });

  const activeComodatos = mockComodatos.filter(c => c.status === 'active');
  const expiredComodatos = mockComodatos.filter(c => c.status === 'expired');
  const totalValue = activeComodatos.reduce((sum, c) => sum + c.equipmentValue, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Comodatos
            </h1>
            <p className="text-text-secondary mt-1">
              Controle de empréstimos de equipamentos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
            <Button variant="primary" onClick={() => setShowComodatoModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Comodato
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <StatCard
            title="Comodatos Ativos"
            value={activeComodatos.length.toString()}
            icon={<Package className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Vencidos"
            value={expiredComodatos.length.toString()}
            changeLabel="necessitam ação"
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
          />
          <StatCard
            title="Valor em Comodato"
            value={totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            icon={<Building className="h-5 w-5" />}
            iconColor="info"
          />
          <StatCard
            title="Devoluções (Mês)"
            value={mockComodatos.filter(c => c.status === 'returned').length.toString()}
            icon={<ArrowLeft className="h-5 w-5" />}
          />
        </StatGrid>

        {/* Alert for expired */}
        {expiredComodatos.length > 0 && (
          <Card className="border-accent-danger/30 bg-accent-danger/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-accent-danger/20">
                  <AlertTriangle className="h-6 w-6 text-accent-danger" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-text-primary">
                    Atenção: {expiredComodatos.length} comodato(s) vencido(s)
                  </h4>
                  <p className="text-text-secondary text-sm">
                    É necessário entrar em contato com os clientes para devolução ou renovação
                  </p>
                </div>
                <Button variant="danger">
                  Ver Vencidos
                </Button>
              </div>
            </CardBody>
          </Card>
        )}

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
                Lista de Comodatos
              </h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                <Input
                  placeholder="Buscar comodatos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <DataTable<Comodato>
              data={filteredComodatos}
              columns={columns}
              keyExtractor={(row) => row.id}
            />
          </CardBody>
        </Card>

        {/* New Comodato Modal */}
        <Modal
          isOpen={showComodatoModal}
          onClose={() => setShowComodatoModal(false)}
          title="Novo Comodato"
          size="lg"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Equipamento *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Selecione o equipamento disponível...</option>
                <option value="10">PAT-2024-00010 - Monitor Dell 27" (R$ 1.500)</option>
                <option value="11">PAT-2024-00011 - Webcam Logitech (R$ 450)</option>
                <option value="12">PAT-2024-00012 - Tablet iPad Pro (R$ 6.500)</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Cliente *
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="">Selecione o cliente...</option>
                  <option value="1">Tech Solutions Ltda</option>
                  <option value="2">Consultoria ABC</option>
                  <option value="3">Manutenção Express</option>
                  <option value="4">Logística Rápida</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Responsável (Cliente) *
                </label>
                <Input placeholder="Nome do responsável no cliente" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Contato do Responsável
              </label>
              <Input placeholder="Telefone ou email" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Data de Início *
                </label>
                <Input type="date" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Data Prevista de Devolução *
                </label>
                <Input type="date" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Motivo / Observações
              </label>
              <textarea
                className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                rows={3}
                placeholder="Descreva o motivo do empréstimo..."
              />
            </div>

            <div className="p-4 bg-bg-tertiary rounded-lg">
              <p className="text-sm text-text-secondary mb-2">
                Termo de Responsabilidade
              </p>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" className="rounded border-border-default" />
                <span className="text-text-primary">
                  Cliente ciente das condições de uso e responsabilidade pelo equipamento
                </span>
              </label>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="ghost" onClick={() => setShowComodatoModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                <FileText className="h-4 w-4 mr-2" />
                Gerar Contrato
              </Button>
            </div>
          </div>
        </Modal>

        {/* Return Modal */}
        <Modal
          isOpen={showReturnModal}
          onClose={() => setShowReturnModal(false)}
          title="Registrar Devolução"
          size="md"
        >
          {selectedComodato && (
            <div className="space-y-4">
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-secondary">Equipamento</p>
                <p className="font-medium text-text-primary">{selectedComodato.equipmentName}</p>
                <p className="text-xs text-text-secondary">{selectedComodato.equipmentCode}</p>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-secondary">Cliente</p>
                <p className="font-medium text-text-primary">{selectedComodato.clientName}</p>
                <p className="text-xs text-text-secondary">{selectedComodato.responsibleName}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Data de Devolução
                </label>
                <Input type="date" defaultValue={new Date().toISOString().split('T')[0]} />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Condição do Equipamento
                </label>
                <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                  <option value="excellent">Excelente - Sem alterações</option>
                  <option value="good">Bom - Desgaste normal de uso</option>
                  <option value="regular">Regular - Pequenos danos</option>
                  <option value="poor">Ruim - Danos significativos</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">
                  Observações da Devolução
                </label>
                <textarea
                  className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                  rows={3}
                  placeholder="Descreva o estado do equipamento na devolução..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="ghost" onClick={() => setShowReturnModal(false)}>
                  Cancelar
                </Button>
                <Button variant="primary">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Confirmar Devolução
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}

export default ComodatoPage;
