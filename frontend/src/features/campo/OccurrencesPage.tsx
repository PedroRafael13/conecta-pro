'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  AlertTriangle,
  AlertOctagon,
  CheckCircle2,
  Clock,
  Eye,
  Edit,
  MapPin,
  User,
  Building2,
  Camera,
  FileText,
  MessageSquare,
  Shield,
  Siren,
  Car,
  Users,
  Flame,
  Zap,
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
interface Occurrence {
  id: string;
  type: 'intrusion' | 'fire' | 'medical' | 'vandalism' | 'theft' | 'vehicle' | 'visitor' | 'maintenance' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  title: string;
  description: string;
  location: string;
  client: string;
  reportedBy: string;
  assignedTo: string | null;
  reportedAt: string;
  resolvedAt: string | null;
  hasEvidence: boolean;
  evidenceCount: number;
  commentsCount: number;
}

// Mock Data
const occurrences: Occurrence[] = [
  {
    id: '1',
    type: 'intrusion',
    severity: 'critical',
    status: 'in_progress',
    title: 'Tentativa de invasão portaria lateral',
    description: 'Identificada tentativa de acesso não autorizado pela portaria lateral do bloco B',
    location: 'Portaria Lateral - Bloco B',
    client: 'Shopping Center Norte',
    reportedBy: 'Carlos Eduardo',
    assignedTo: 'Roberto Silva',
    reportedAt: '2026-01-15 02:34',
    resolvedAt: null,
    hasEvidence: true,
    evidenceCount: 5,
    commentsCount: 8,
  },
  {
    id: '2',
    type: 'vehicle',
    severity: 'low',
    status: 'resolved',
    title: 'Veículo estacionado em local proibido',
    description: 'Placa ABC-1234 estacionado em vaga de deficiente sem credencial',
    location: 'Estacionamento Subsolo 2',
    client: 'Tech Park Empresarial',
    reportedBy: 'Ana Paula',
    assignedTo: 'Pedro Santos',
    reportedAt: '2026-01-15 08:15',
    resolvedAt: '2026-01-15 09:30',
    hasEvidence: true,
    evidenceCount: 2,
    commentsCount: 3,
  },
  {
    id: '3',
    type: 'maintenance',
    severity: 'medium',
    status: 'open',
    title: 'Câmera 15 sem sinal',
    description: 'Câmera do corredor principal sem sinal desde 06:00',
    location: 'Corredor Principal - Térreo',
    client: 'Hospital São Lucas',
    reportedBy: 'Sistema',
    assignedTo: null,
    reportedAt: '2026-01-15 06:12',
    resolvedAt: null,
    hasEvidence: false,
    evidenceCount: 0,
    commentsCount: 1,
  },
  {
    id: '4',
    type: 'visitor',
    severity: 'low',
    status: 'closed',
    title: 'Visitante sem identificação',
    description: 'Pessoa sem crachá identificada no 3º andar',
    location: '3º Andar - Administrativo',
    client: 'Condomínio Aurora',
    reportedBy: 'Roberto Silva',
    assignedTo: 'Carlos Eduardo',
    reportedAt: '2026-01-14 14:45',
    resolvedAt: '2026-01-14 15:00',
    hasEvidence: true,
    evidenceCount: 1,
    commentsCount: 4,
  },
  {
    id: '5',
    type: 'fire',
    severity: 'high',
    status: 'resolved',
    title: 'Alarme de incêndio acionado',
    description: 'Alarme acionado na cozinha do restaurante - queima de alimento',
    location: 'Praça de Alimentação',
    client: 'Shopping Center Norte',
    reportedBy: 'Sistema',
    assignedTo: 'Ana Paula',
    reportedAt: '2026-01-14 12:30',
    resolvedAt: '2026-01-14 12:45',
    hasEvidence: true,
    evidenceCount: 3,
    commentsCount: 6,
  },
  {
    id: '6',
    type: 'medical',
    severity: 'high',
    status: 'closed',
    title: 'Funcionário passou mal',
    description: 'Vigilante sentiu mal estar durante ronda - SAMU acionado',
    location: 'Guarita Principal',
    client: 'Banco Regional',
    reportedBy: 'Pedro Santos',
    assignedTo: 'Carlos Eduardo',
    reportedAt: '2026-01-13 22:15',
    resolvedAt: '2026-01-13 23:30',
    hasEvidence: false,
    evidenceCount: 0,
    commentsCount: 12,
  },
];

const typeConfig = {
  intrusion: { label: 'Invasão', color: 'danger' as const, icon: AlertOctagon },
  fire: { label: 'Incêndio', color: 'danger' as const, icon: Flame },
  medical: { label: 'Médico', color: 'warning' as const, icon: Plus },
  vandalism: { label: 'Vandalismo', color: 'danger' as const, icon: AlertTriangle },
  theft: { label: 'Furto', color: 'danger' as const, icon: Shield },
  vehicle: { label: 'Veículo', color: 'info' as const, icon: Car },
  visitor: { label: 'Visitante', color: 'neutral' as const, icon: Users },
  maintenance: { label: 'Manutenção', color: 'warning' as const, icon: Zap },
  other: { label: 'Outro', color: 'neutral' as const, icon: FileText },
};

const severityConfig = {
  low: { label: 'Baixa', color: 'success' as const },
  medium: { label: 'Média', color: 'warning' as const },
  high: { label: 'Alta', color: 'danger' as const },
  critical: { label: 'Crítica', color: 'danger' as const },
};

const statusConfig = {
  open: { label: 'Aberta', color: 'danger' as const },
  in_progress: { label: 'Em Andamento', color: 'primary' as const },
  resolved: { label: 'Resolvida', color: 'success' as const },
  closed: { label: 'Fechada', color: 'neutral' as const },
};

const columns: Column<Occurrence>[] = [
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => {
      const config = typeConfig[row.type];
      const TypeIcon = config.icon;
      return (
        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-lg ${
            row.severity === 'critical' ? 'bg-accent-danger/20' :
            row.severity === 'high' ? 'bg-accent-danger/10' :
            'bg-bg-tertiary'
          }`}>
            <TypeIcon className={`w-4 h-4 ${
              row.severity === 'critical' || row.severity === 'high' ? 'text-accent-danger' : 'text-text-muted'
            }`} />
          </div>
          <div>
            <p className="font-medium text-text-primary">{config.label}</p>
            <Badge size="sm" variant={severityConfig[row.severity].color}>
              {severityConfig[row.severity].label}
            </Badge>
          </div>
        </div>
      );
    },
  },
  {
    key: 'title',
    header: 'Ocorrência',
    render: (row) => (
      <div className="max-w-[300px]">
        <p className="font-medium text-text-primary truncate">{row.title}</p>
        <p className="text-xs text-text-muted mt-1 truncate">{row.description}</p>
      </div>
    ),
  },
  {
    key: 'location',
    header: 'Local',
    render: (row) => (
      <div>
        <div className="flex items-center gap-1">
          <Building2 className="w-3 h-3 text-text-muted" />
          <p className="text-sm text-text-primary">{row.client}</p>
        </div>
        <div className="flex items-center gap-1 mt-1">
          <MapPin className="w-3 h-3 text-text-muted" />
          <p className="text-xs text-text-muted truncate max-w-[150px]">{row.location}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'reportedBy',
    header: 'Reportado por',
    render: (row) => (
      <div className="flex items-center gap-2">
        {row.reportedBy === 'Sistema' ? (
          <>
            <div className="w-6 h-6 rounded-full bg-accent-primary/20 flex items-center justify-center">
              <Siren className="w-3 h-3 text-accent-primary" />
            </div>
            <span className="text-sm text-text-secondary">Sistema</span>
          </>
        ) : (
          <>
            <Avatar name={row.reportedBy} size="xs" />
            <span className="text-sm">{row.reportedBy}</span>
          </>
        )}
      </div>
    ),
  },
  {
    key: 'reportedAt',
    header: 'Data/Hora',
    render: (row) => (
      <div>
        <p className="text-sm text-text-primary">{row.reportedAt.split(' ')[0]}</p>
        <p className="text-xs text-text-muted">{row.reportedAt.split(' ')[1]}</p>
      </div>
    ),
  },
  {
    key: 'evidence',
    header: 'Evidências',
    render: (row) => (
      <div className="flex items-center gap-3">
        {row.hasEvidence && (
          <div className="flex items-center gap-1 text-text-muted">
            <Camera className="w-4 h-4" />
            <span className="text-xs">{row.evidenceCount}</span>
          </div>
        )}
        <div className="flex items-center gap-1 text-text-muted">
          <MessageSquare className="w-4 h-4" />
          <span className="text-xs">{row.commentsCount}</span>
        </div>
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
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        {(row.status === 'open' || row.status === 'in_progress') && (
          <Button variant="ghost" size="icon-sm" title="Editar">
            <Edit className="w-4 h-4" />
          </Button>
        )}
      </div>
    ),
  },
];

export function OccurrencesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedOccurrence, setSelectedOccurrence] = useState<Occurrence | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Stats
  const openCount = occurrences.filter(o => o.status === 'open').length;
  const inProgressCount = occurrences.filter(o => o.status === 'in_progress').length;
  const resolvedToday = occurrences.filter(o =>
    o.status === 'resolved' && o.resolvedAt?.startsWith('2026-01-15')
  ).length;
  const criticalCount = occurrences.filter(o =>
    o.severity === 'critical' && o.status !== 'closed'
  ).length;

  const filteredOccurrences = occurrences.filter((occ) => {
    const matchesSearch =
      occ.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      occ.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
      occ.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || occ.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Central de Ocorrências
            </h1>
            <p className="text-text-secondary mt-1">
              Registre e acompanhe ocorrências de segurança
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Ocorrência
            </Button>
          </div>
        </div>

        {/* Critical Alert */}
        {criticalCount > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-accent-danger/10 border border-accent-danger/30 rounded-xl p-4"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent-danger/20 rounded-lg">
                <Siren className="w-5 h-5 text-accent-danger" />
              </div>
              <div>
                <p className="font-medium text-accent-danger">
                  {criticalCount} ocorrência{criticalCount > 1 ? 's' : ''} crítica{criticalCount > 1 ? 's' : ''} em aberto
                </p>
                <p className="text-sm text-text-secondary">
                  Requer atenção imediata da equipe de segurança
                </p>
              </div>
              <Button variant="danger" size="sm" className="ml-auto">
                Ver Críticas
              </Button>
            </div>
          </motion.div>
        )}

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Abertas"
              value={openCount}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Em Andamento"
              value={inProgressCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Resolvidas Hoje"
              value={resolvedToday}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Total do Mês"
              value={occurrences.length}
              icon={<Shield className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todas (${occurrences.length})` },
                  { value: 'open', label: `Abertas (${openCount})` },
                  { value: 'in_progress', label: `Em Andamento (${inProgressCount})` },
                  { value: 'resolved', label: 'Resolvidas' },
                  { value: 'closed', label: 'Fechadas' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar ocorrências..."
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

        {/* Occurrences Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredOccurrences}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => { setSelectedOccurrence(row); setShowDetailModal(true); }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Occurrence Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Ocorrência"
          description="Registre uma nova ocorrência de segurança"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Registrar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Ocorrência"
                options={[
                  { value: 'intrusion', label: 'Invasão' },
                  { value: 'fire', label: 'Incêndio' },
                  { value: 'medical', label: 'Emergência Médica' },
                  { value: 'vandalism', label: 'Vandalismo' },
                  { value: 'theft', label: 'Furto/Roubo' },
                  { value: 'vehicle', label: 'Veículo' },
                  { value: 'visitor', label: 'Visitante' },
                  { value: 'maintenance', label: 'Manutenção' },
                  { value: 'other', label: 'Outro' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Severidade"
                options={[
                  { value: 'low', label: 'Baixa' },
                  { value: 'medium', label: 'Média' },
                  { value: 'high', label: 'Alta' },
                  { value: 'critical', label: 'Crítica' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <Input label="Título" placeholder="Descreva brevemente a ocorrência" required />
            <Input label="Descrição Detalhada" placeholder="Forneça todos os detalhes relevantes" />
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
              <Input label="Local Específico" placeholder="Ex: Portaria Principal" />
            </div>
            <Select
              label="Atribuir para"
              options={[
                { value: '1', label: 'Ana Paula' },
                { value: '2', label: 'Carlos Eduardo' },
                { value: '3', label: 'Roberto Silva' },
                { value: '4', label: 'Pedro Santos' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione um responsável (opcional)"
            />
            <div className="pt-4 border-t border-border-subtle">
              <Button variant="outline" leftIcon={<Camera className="w-4 h-4" />}>
                Anexar Evidências
              </Button>
              <p className="text-xs text-text-muted mt-2">
                Adicione fotos, vídeos ou documentos relacionados
              </p>
            </div>
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes da Ocorrência"
          description={selectedOccurrence ? `#${selectedOccurrence.id} - ${selectedOccurrence.title}` : ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              {selectedOccurrence && (selectedOccurrence.status === 'open' || selectedOccurrence.status === 'in_progress') && (
                <Button variant="primary">Atualizar Status</Button>
              )}
            </>
          }
        >
          {selectedOccurrence && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className={`p-3 rounded-lg ${
                  selectedOccurrence.severity === 'critical' ? 'bg-accent-danger/20' :
                  selectedOccurrence.severity === 'high' ? 'bg-accent-danger/10' : 'bg-bg-primary'
                }`}>
                  {(() => {
                    const TypeIcon = typeConfig[selectedOccurrence.type].icon;
                    return <TypeIcon className={`w-6 h-6 ${
                      selectedOccurrence.severity === 'critical' || selectedOccurrence.severity === 'high' ? 'text-accent-danger' : 'text-text-muted'
                    }`} />;
                  })()}
                </div>
                <div className="flex-1">
                  <p className="text-lg font-medium text-text-primary">{selectedOccurrence.title}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={typeConfig[selectedOccurrence.type].color}>{typeConfig[selectedOccurrence.type].label}</Badge>
                    <Badge variant={severityConfig[selectedOccurrence.severity].color}>{severityConfig[selectedOccurrence.severity].label}</Badge>
                    <Badge variant={statusConfig[selectedOccurrence.status].color}>{statusConfig[selectedOccurrence.status].label}</Badge>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-text-muted mb-2">Descrição</p>
                <p className="text-text-primary">{selectedOccurrence.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Cliente</p>
                  <p className="font-medium text-text-primary">{selectedOccurrence.client}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Local</p>
                  <p className="font-medium text-text-primary">{selectedOccurrence.location}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Reportado por</p>
                  <p className="font-medium text-text-primary">{selectedOccurrence.reportedBy}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Atribuído para</p>
                  <p className="font-medium text-text-primary">{selectedOccurrence.assignedTo || 'Não atribuído'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Data/Hora do Registro</p>
                  <p className="font-medium text-text-primary">{selectedOccurrence.reportedAt}</p>
                </div>
                {selectedOccurrence.resolvedAt && (
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted mb-1">Data/Hora da Resolução</p>
                    <p className="font-medium text-text-primary">{selectedOccurrence.resolvedAt}</p>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center gap-2">
                  <Camera className="w-5 h-5 text-text-muted" />
                  <span className="text-text-primary">{selectedOccurrence.evidenceCount} evidências</span>
                </div>
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-text-muted" />
                  <span className="text-text-primary">{selectedOccurrence.commentsCount} comentários</span>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
