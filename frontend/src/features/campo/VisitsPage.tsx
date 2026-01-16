'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Calendar,
  MapPin,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  Edit,
  Navigation,
  User,
  Phone,
  Building2,
  ChevronLeft,
  ChevronRight,
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
interface Visit {
  id: string;
  client: string;
  clientAddress: string;
  type: 'routine' | 'technical' | 'commercial' | 'emergency';
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  responsible: string;
  scheduledDate: string;
  scheduledTime: string;
  duration: number; // in minutes
  actualStart: string | null;
  actualEnd: string | null;
  notes: string;
  contactName: string;
  contactPhone: string;
}

// Mock Data
const visits: Visit[] = [
  {
    id: '1',
    client: 'Shopping Center Norte',
    clientAddress: 'Av. Cruzeiro do Sul, 1100 - Santana',
    type: 'routine',
    status: 'completed',
    responsible: 'Ana Paula',
    scheduledDate: '2026-01-15',
    scheduledTime: '09:00',
    duration: 120,
    actualStart: '09:05',
    actualEnd: '11:00',
    notes: 'Vistoria mensal de rotina',
    contactName: 'João Silva',
    contactPhone: '(11) 99999-1234',
  },
  {
    id: '2',
    client: 'Hospital São Lucas',
    clientAddress: 'Rua Dr. Arnaldo, 500 - Pinheiros',
    type: 'technical',
    status: 'in_progress',
    responsible: 'Carlos Eduardo',
    scheduledDate: '2026-01-15',
    scheduledTime: '14:00',
    duration: 180,
    actualStart: '14:10',
    actualEnd: null,
    notes: 'Revisão sistema de controle de acesso',
    contactName: 'Maria Santos',
    contactPhone: '(11) 98888-5678',
  },
  {
    id: '3',
    client: 'Tech Park Empresarial',
    clientAddress: 'Av. Paulista, 1000 - Bela Vista',
    type: 'commercial',
    status: 'scheduled',
    responsible: 'Roberto Silva',
    scheduledDate: '2026-01-15',
    scheduledTime: '16:00',
    duration: 60,
    actualStart: null,
    actualEnd: null,
    notes: 'Apresentação proposta ampliação CFTV',
    contactName: 'Pedro Costa',
    contactPhone: '(11) 97777-9012',
  },
  {
    id: '4',
    client: 'Condomínio Aurora',
    clientAddress: 'Rua das Flores, 200 - Moema',
    type: 'emergency',
    status: 'scheduled',
    responsible: 'Pedro Santos',
    scheduledDate: '2026-01-15',
    scheduledTime: '17:30',
    duration: 90,
    actualStart: null,
    actualEnd: null,
    notes: 'Chamado emergencial - portão não abre',
    contactName: 'Ana Oliveira',
    contactPhone: '(11) 96666-3456',
  },
  {
    id: '5',
    client: 'Banco Regional',
    clientAddress: 'Av. Brigadeiro, 800 - Jardins',
    type: 'routine',
    status: 'no_show',
    responsible: 'Ana Paula',
    scheduledDate: '2026-01-14',
    scheduledTime: '10:00',
    duration: 120,
    actualStart: null,
    actualEnd: null,
    notes: 'Cliente não estava no local',
    contactName: 'Carlos Mendes',
    contactPhone: '(11) 95555-7890',
  },
];

const typeConfig = {
  routine: { label: 'Rotina', color: 'info' as const },
  technical: { label: 'Técnica', color: 'primary' as const },
  commercial: { label: 'Comercial', color: 'success' as const },
  emergency: { label: 'Emergência', color: 'danger' as const },
};

const statusConfig = {
  scheduled: { label: 'Agendada', color: 'info' as const, icon: Calendar },
  in_progress: { label: 'Em Andamento', color: 'primary' as const, icon: Clock },
  completed: { label: 'Concluída', color: 'success' as const, icon: CheckCircle2 },
  cancelled: { label: 'Cancelada', color: 'neutral' as const, icon: XCircle },
  no_show: { label: 'Não Compareceu', color: 'danger' as const, icon: AlertTriangle },
};

const columns: Column<Visit>[] = [
  {
    key: 'time',
    header: 'Horário',
    render: (row) => (
      <div className="text-center">
        <p className="text-lg font-mono font-bold text-text-primary">{row.scheduledTime}</p>
        <p className="text-xs text-text-muted">{row.duration} min</p>
      </div>
    ),
  },
  {
    key: 'client',
    header: 'Cliente',
    render: (row) => (
      <div>
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-text-muted" />
          <p className="font-medium text-text-primary">{row.client}</p>
        </div>
        <div className="flex items-center gap-1 mt-1">
          <MapPin className="w-3 h-3 text-text-muted" />
          <p className="text-xs text-text-muted truncate max-w-[200px]">{row.clientAddress}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const config = typeConfig[row.type];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'contact',
    header: 'Contato',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.contactName}</p>
        <div className="flex items-center gap-1 mt-1">
          <Phone className="w-3 h-3 text-text-muted" />
          <p className="text-xs text-text-muted">{row.contactPhone}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'responsible',
    header: 'Responsável',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.responsible} size="xs" />
        <span className="text-sm">{row.responsible}</span>
      </div>
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
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Navegar">
          <Navigation className="w-4 h-4" />
        </Button>
        {row.status === 'scheduled' && (
          <Button variant="primary" size="sm">Iniciar</Button>
        )}
      </div>
    ),
  },
];

export function VisitsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [selectedDate, setSelectedDate] = useState('2026-01-15');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedVisit, setSelectedVisit] = useState<Visit | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const filteredVisits = visits.filter((visit) => {
    const matchesSearch =
      visit.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
      visit.contactName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || visit.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  // Stats
  const scheduled = visits.filter((v) => v.status === 'scheduled').length;
  const inProgress = visits.filter((v) => v.status === 'in_progress').length;
  const completed = visits.filter((v) => v.status === 'completed').length;
  const totalToday = visits.filter((v) => v.scheduledDate === selectedDate).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Agenda de Visitas
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie visitas técnicas e comerciais
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Calendar className="w-4 h-4" />}>
              Ver Calendário
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Visita
            </Button>
          </div>
        </div>

        {/* Date Navigation */}
        <Card>
          <CardBody className="py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon-sm">
                  <ChevronLeft className="w-5 h-5" />
                </Button>
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-accent-primary" />
                  <Input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="w-40"
                  />
                </div>
                <Button variant="ghost" size="icon-sm">
                  <ChevronRight className="w-5 h-5" />
                </Button>
                <Button variant="outline" size="sm">Hoje</Button>
              </div>
              <p className="text-sm text-text-secondary">
                {totalToday} visitas agendadas para este dia
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Agendadas"
              value={scheduled}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Em Andamento"
              value={inProgress}
              icon={<Clock className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Concluídas"
              value={completed}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Taxa de Conclusão"
              value={`${Math.round((completed / (completed + scheduled + inProgress)) * 100)}%`}
              icon={<CheckCircle2 className="w-6 h-6" />}
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
                  { value: 'all', label: `Todas (${visits.length})` },
                  { value: 'scheduled', label: `Agendadas (${scheduled})` },
                  { value: 'in_progress', label: `Em Andamento (${inProgress})` },
                  { value: 'completed', label: `Concluídas (${completed})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar visitas..."
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

        {/* Visits Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredVisits}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => { setSelectedVisit(row); setShowDetailModal(true); }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Visit Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Visita"
          description="Agende uma nova visita"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Agendar
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
                label="Tipo de Visita"
                options={[
                  { value: 'routine', label: 'Rotina' },
                  { value: 'technical', label: 'Técnica' },
                  { value: 'commercial', label: 'Comercial' },
                  { value: 'emergency', label: 'Emergência' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Input label="Data" type="date" required />
              <Input label="Horário" type="time" required />
              <Input label="Duração (min)" type="number" placeholder="60" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Nome do Contato" placeholder="Nome do responsável no local" />
              <Input label="Telefone" placeholder="(00) 00000-0000" />
            </div>
            <Select
              label="Responsável"
              options={[
                { value: '1', label: 'Ana Paula' },
                { value: '2', label: 'Carlos Eduardo' },
                { value: '3', label: 'Roberto Silva' },
                { value: '4', label: 'Pedro Santos' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />
            <Input label="Observações" placeholder="Notas sobre a visita" />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes da Visita"
          description={selectedVisit ? `${selectedVisit.client} - ${selectedVisit.scheduledTime}` : ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              {selectedVisit?.status === 'scheduled' && (
                <Button variant="primary">Iniciar Visita</Button>
              )}
              {selectedVisit?.status === 'in_progress' && (
                <Button variant="success">Finalizar Visita</Button>
              )}
            </>
          }
        >
          {selectedVisit && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className="p-3 rounded-lg bg-bg-primary">
                  <Calendar className="w-6 h-6 text-text-muted" />
                </div>
                <div className="flex-1">
                  <p className="text-lg font-medium text-text-primary">{selectedVisit.client}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={typeConfig[selectedVisit.type].color}>{typeConfig[selectedVisit.type].label}</Badge>
                    <Badge variant={statusConfig[selectedVisit.status].color}>{statusConfig[selectedVisit.status].label}</Badge>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-text-primary">{selectedVisit.scheduledTime}</p>
                  <p className="text-sm text-text-muted">{selectedVisit.duration} min</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-1">Endereço</p>
                <p className="font-medium text-text-primary">{selectedVisit.clientAddress}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Contato</p>
                  <p className="font-medium text-text-primary">{selectedVisit.contactName}</p>
                  <p className="text-sm text-text-muted">{selectedVisit.contactPhone}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Responsável</p>
                  <p className="font-medium text-text-primary">{selectedVisit.responsible}</p>
                </div>
              </div>

              {(selectedVisit.actualStart || selectedVisit.actualEnd) && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted mb-1">Início Real</p>
                    <p className="font-medium text-text-primary">{selectedVisit.actualStart || '-'}</p>
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted mb-1">Término Real</p>
                    <p className="font-medium text-text-primary">{selectedVisit.actualEnd || '-'}</p>
                  </div>
                </div>
              )}

              {selectedVisit.notes && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Observações</p>
                  <p className="text-text-primary">{selectedVisit.notes}</p>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
