'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Gavel,
  Calendar,
  Building2,
  Clock,
  FileText,
  Eye,
  Edit,
  Download,
  ExternalLink,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  DollarSign,
  Users,
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
interface Bidding {
  id: string;
  number: string;
  title: string;
  description: string;
  agency: string;
  agencyType: 'federal' | 'estadual' | 'municipal' | 'autarquia';
  modality: 'pregao_eletronico' | 'pregao_presencial' | 'concorrencia' | 'tomada_precos' | 'convite' | 'dispensa' | 'inexigibilidade';
  status: 'identificado' | 'em_analise' | 'proposta_elaboracao' | 'proposta_enviada' | 'aguardando_resultado' | 'recursos' | 'ganho' | 'perdido' | 'cancelado' | 'desistencia';
  estimatedValue: number;
  ourProposal: number | null;
  publicationDate: string;
  deadline: string;
  openingDate: string;
  portal: string;
  portalUrl: string;
  responsible: string;
  documentsCount: number;
  hasAlert: boolean;
  alertMessage: string | null;
}

// Mock Data
const biddings: Bidding[] = [
  {
    id: '1',
    number: 'PE-001/2026',
    title: 'Serviços de vigilância patrimonial armada e desarmada',
    description: 'Contratação de empresa especializada em vigilância patrimonial para as unidades administrativas',
    agency: 'Prefeitura Municipal de São Paulo',
    agencyType: 'municipal',
    modality: 'pregao_eletronico',
    status: 'identificado',
    estimatedValue: 2500000,
    ourProposal: null,
    publicationDate: '2026-01-10',
    deadline: '2026-01-20',
    openingDate: '2026-01-25',
    portal: 'ComprasNet',
    portalUrl: 'https://comprasnet.gov.br/xxx',
    responsible: 'Ana Paula',
    documentsCount: 8,
    hasAlert: true,
    alertMessage: 'Prazo para cadastro encerra em 5 dias',
  },
  {
    id: '2',
    number: 'PE-002/2026',
    title: 'Instalação e manutenção de sistema de CFTV',
    description: 'Fornecimento e instalação de câmeras de segurança com manutenção preventiva e corretiva',
    agency: 'Governo do Estado de SP',
    agencyType: 'estadual',
    modality: 'pregao_eletronico',
    status: 'proposta_enviada',
    estimatedValue: 850000,
    ourProposal: 780000,
    publicationDate: '2026-01-05',
    deadline: '2026-01-15',
    openingDate: '2026-01-18',
    portal: 'BEC/SP',
    portalUrl: 'https://bec.sp.gov.br/xxx',
    responsible: 'Carlos Eduardo',
    documentsCount: 12,
    hasAlert: false,
    alertMessage: null,
  },
  {
    id: '3',
    number: 'CC-003/2026',
    title: 'Segurança para eventos municipais',
    description: 'Serviços de segurança privada para eventos culturais e esportivos do município',
    agency: 'Câmara Municipal de Campinas',
    agencyType: 'municipal',
    modality: 'concorrencia',
    status: 'aguardando_resultado',
    estimatedValue: 180000,
    ourProposal: 165000,
    publicationDate: '2025-12-20',
    deadline: '2026-01-10',
    openingDate: '2026-01-12',
    portal: 'Portal de Compras',
    portalUrl: 'https://campinas.sp.gov.br/xxx',
    responsible: 'Roberto Silva',
    documentsCount: 6,
    hasAlert: true,
    alertMessage: 'Resultado previsto para amanhã',
  },
  {
    id: '4',
    number: 'PE-015/2025',
    title: 'Monitoramento eletrônico de frotas',
    description: 'Sistema de rastreamento e monitoramento GPS para frota municipal',
    agency: 'Secretaria de Transportes Metropolitanos',
    agencyType: 'estadual',
    modality: 'pregao_eletronico',
    status: 'ganho',
    estimatedValue: 420000,
    ourProposal: 385000,
    publicationDate: '2025-11-25',
    deadline: '2025-12-15',
    openingDate: '2025-12-20',
    portal: 'ComprasNet',
    portalUrl: 'https://comprasnet.gov.br/xxx',
    responsible: 'Ana Paula',
    documentsCount: 15,
    hasAlert: false,
    alertMessage: null,
  },
  {
    id: '5',
    number: 'TP-008/2025',
    title: 'Sistema de controle de acesso predial',
    description: 'Fornecimento e instalação de sistema biométrico de controle de acesso',
    agency: 'Tribunal de Justiça do Estado',
    agencyType: 'estadual',
    modality: 'tomada_precos',
    status: 'perdido',
    estimatedValue: 320000,
    ourProposal: 295000,
    publicationDate: '2025-11-10',
    deadline: '2025-12-01',
    openingDate: '2025-12-10',
    portal: 'Portal TJ',
    portalUrl: 'https://tj.sp.gov.br/xxx',
    responsible: 'Pedro Santos',
    documentsCount: 10,
    hasAlert: false,
    alertMessage: null,
  },
  {
    id: '6',
    number: 'PE-020/2025',
    title: 'Central de monitoramento 24h',
    description: 'Implantação de central de monitoramento com operação ininterrupta',
    agency: 'Ministério da Educação',
    agencyType: 'federal',
    modality: 'pregao_eletronico',
    status: 'em_analise',
    estimatedValue: 1200000,
    ourProposal: null,
    publicationDate: '2026-01-08',
    deadline: '2026-01-25',
    openingDate: '2026-01-30',
    portal: 'ComprasNet',
    portalUrl: 'https://comprasnet.gov.br/xxx',
    responsible: 'Carlos Eduardo',
    documentsCount: 5,
    hasAlert: false,
    alertMessage: null,
  },
];

const modalityConfig = {
  pregao_eletronico: { label: 'Pregão Eletrônico', color: 'primary' as const },
  pregao_presencial: { label: 'Pregão Presencial', color: 'info' as const },
  concorrencia: { label: 'Concorrência', color: 'warning' as const },
  tomada_precos: { label: 'Tomada de Preços', color: 'success' as const },
  convite: { label: 'Convite', color: 'info' as const },
  dispensa: { label: 'Dispensa', color: 'info' as const },
  inexigibilidade: { label: 'Inexigibilidade', color: 'info' as const },
};

const statusConfig = {
  identificado: { label: 'Identificado', color: 'info' as const },
  em_analise: { label: 'Em Análise', color: 'warning' as const },
  proposta_elaboracao: { label: 'Elaborando Proposta', color: 'primary' as const },
  proposta_enviada: { label: 'Proposta Enviada', color: 'primary' as const },
  aguardando_resultado: { label: 'Aguardando Resultado', color: 'warning' as const },
  recursos: { label: 'Em Recurso', color: 'warning' as const },
  ganho: { label: 'Ganho', color: 'success' as const },
  perdido: { label: 'Perdido', color: 'danger' as const },
  cancelado: { label: 'Cancelado', color: 'danger' as const },
  desistencia: { label: 'Desistência', color: 'danger' as const },
};

const agencyTypeConfig = {
  federal: { label: 'Federal', color: 'primary' as const },
  estadual: { label: 'Estadual', color: 'info' as const },
  municipal: { label: 'Municipal', color: 'success' as const },
  autarquia: { label: 'Autarquia', color: 'warning' as const },
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const columns: Column<Bidding>[] = [
  {
    key: 'number',
    header: 'Processo',
    render: (row) => (
      <div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-bold text-accent-primary">{row.number}</span>
          {row.hasAlert && (
            <AlertTriangle className="w-4 h-4 text-accent-warning" />
          )}
        </div>
        <Badge size="sm" variant={modalityConfig[row.modality].color}>
          {modalityConfig[row.modality].label}
        </Badge>
      </div>
    ),
  },
  {
    key: 'title',
    header: 'Objeto',
    render: (row) => (
      <div className="max-w-[300px]">
        <p className="text-sm font-medium text-text-primary truncate">{row.title}</p>
        <div className="flex items-center gap-1 mt-1">
          <Building2 className="w-3 h-3 text-text-muted" />
          <p className="text-xs text-text-muted truncate">{row.agency}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'agencyType',
    header: 'Esfera',
    render: (row) => {
      const config = agencyTypeConfig[row.agencyType];
      return <Badge variant={config.color}>{config.label}</Badge>;
    },
  },
  {
    key: 'value',
    header: 'Valor',
    render: (row) => (
      <div>
        <p className="text-sm font-medium text-text-primary">{formatCurrency(row.estimatedValue)}</p>
        {row.ourProposal && (
          <p className="text-xs text-accent-primary">Nossa: {formatCurrency(row.ourProposal)}</p>
        )}
      </div>
    ),
  },
  {
    key: 'dates',
    header: 'Prazos',
    render: (row) => {
      const deadlineDate = new Date(row.deadline);
      const today = new Date();
      const daysLeft = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
      const isUrgent = daysLeft <= 5 && daysLeft > 0;
      const isPast = daysLeft < 0;

      return (
        <div>
          <div className="flex items-center gap-1">
            <Clock className={`w-3 h-3 ${isUrgent ? 'text-accent-warning' : isPast ? 'text-text-muted' : 'text-text-muted'}`} />
            <p className={`text-xs ${isUrgent ? 'text-accent-warning font-medium' : ''}`}>
              Prazo: {row.deadline}
            </p>
          </div>
          <div className="flex items-center gap-1 mt-1">
            <Calendar className="w-3 h-3 text-text-muted" />
            <p className="text-xs text-text-muted">Abertura: {row.openingDate}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'documents',
    header: 'Docs',
    render: (row) => (
      <div className="flex items-center gap-1">
        <FileText className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.documentsCount}</span>
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
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Abrir portal">
          <ExternalLink className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function BiddingsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedBidding, setSelectedBidding] = useState<Bidding | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Form state for new bidding modal
  const [newBiddingModality, setNewBiddingModality] = useState('');
  const [newBiddingSphere, setNewBiddingSphere] = useState('');
  const [newBiddingResponsible, setNewBiddingResponsible] = useState('');

  // Stats
  const openCount = biddings.filter(b =>
    ['identificado', 'em_analise', 'proposta_elaboracao'].includes(b.status)
  ).length;
  const inProgressCount = biddings.filter(b =>
    ['proposta_enviada', 'aguardando_resultado', 'recursos'].includes(b.status)
  ).length;
  const wonCount = biddings.filter(b => b.status === 'ganho').length;
  const lostCount = biddings.filter(b => b.status === 'perdido').length;

  const filteredBiddings = biddings.filter((bidding) => {
    const matchesSearch =
      bidding.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bidding.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bidding.agency.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTab =
      selectedTab === 'all' ||
      (selectedTab === 'open' && ['identificado', 'em_analise', 'proposta_elaboracao'].includes(bidding.status)) ||
      (selectedTab === 'in_progress' && ['proposta_enviada', 'aguardando_resultado', 'recursos'].includes(bidding.status)) ||
      (selectedTab === 'won' && bidding.status === 'ganho') ||
      (selectedTab === 'lost' && bidding.status === 'perdido');

    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Processos Licitatórios
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie e acompanhe todas as licitações
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
              Nova Licitação
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Em Aberto"
              value={openCount}
              icon={<Gavel className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Em Andamento"
              value={inProgressCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Ganhas"
              value={wonCount}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Perdidas"
              value={lostCount}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Alerts */}
        {biddings.some(b => b.hasAlert) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card variant="outline" className="border-accent-warning/30 bg-accent-warning/5">
              <CardBody className="py-3">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-accent-warning" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-text-primary">
                      {biddings.filter(b => b.hasAlert).length} licitação(ões) requerem atenção
                    </p>
                    <p className="text-xs text-text-muted">
                      {biddings.filter(b => b.hasAlert).map(b => b.alertMessage).join(' | ')}
                    </p>
                  </div>
                  <Button variant="secondary" size="sm">
                    Ver Alertas
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todas (${biddings.length})` },
                  { value: 'open', label: `Em Aberto (${openCount})` },
                  { value: 'in_progress', label: `Em Andamento (${inProgressCount})` },
                  { value: 'won', label: `Ganhas (${wonCount})` },
                  { value: 'lost', label: `Perdidas (${lostCount})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar licitação..."
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

        {/* Biddings Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredBiddings}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => { setSelectedBidding(row); setShowDetailModal(true); }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Bidding Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Licitação"
          description="Cadastre um novo processo licitatório"
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
              <Input label="Número do Processo" placeholder="Ex: PE-001/2026" required />
              <Select
                label="Modalidade"
                options={[
                  { value: 'pregao_eletronico', label: 'Pregão Eletrônico' },
                  { value: 'pregao_presencial', label: 'Pregão Presencial' },
                  { value: 'concorrencia', label: 'Concorrência' },
                  { value: 'tomada_precos', label: 'Tomada de Preços' },
                  { value: 'convite', label: 'Convite' },
                  { value: 'dispensa', label: 'Dispensa' },
                  { value: 'inexigibilidade', label: 'Inexigibilidade' },
                ]}
                value={newBiddingModality}
                onChange={(value) => setNewBiddingModality(value)}
                placeholder="Selecione..."
              />
            </div>
            <Input label="Objeto" placeholder="Descrição do objeto da licitação" required />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Órgão/Entidade" placeholder="Nome do órgão licitante" required />
              <Select
                label="Esfera"
                options={[
                  { value: 'federal', label: 'Federal' },
                  { value: 'estadual', label: 'Estadual' },
                  { value: 'municipal', label: 'Municipal' },
                  { value: 'autarquia', label: 'Autarquia' },
                ]}
                value={newBiddingSphere}
                onChange={(value) => setNewBiddingSphere(value)}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Input label="Valor Estimado" type="number" placeholder="0,00" />
              <Input label="Prazo de Proposta" type="date" required />
              <Input label="Data de Abertura" type="date" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Portal" placeholder="Ex: ComprasNet, BEC/SP" />
              <Input label="URL do Edital" placeholder="https://..." />
            </div>
            <Select
              label="Responsável"
              options={[
                { value: '1', label: 'Ana Paula' },
                { value: '2', label: 'Carlos Eduardo' },
                { value: '3', label: 'Roberto Silva' },
                { value: '4', label: 'Pedro Santos' },
              ]}
              value={newBiddingResponsible}
              onChange={(value) => setNewBiddingResponsible(value)}
              placeholder="Selecione..."
            />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes da Licitação"
          description={selectedBidding ? selectedBidding.number : ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              <Button variant="outline" leftIcon={<ExternalLink className="w-4 h-4" />}>
                Abrir Portal
              </Button>
              <Button variant="primary">Elaborar Proposta</Button>
            </>
          }
        >
          {selectedBidding && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className="p-3 rounded-lg bg-bg-primary">
                  <Gavel className="w-6 h-6 text-text-muted" />
                </div>
                <div className="flex-1">
                  <p className="font-mono text-lg font-bold text-accent-primary">{selectedBidding.number}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={modalityConfig[selectedBidding.modality].color}>{modalityConfig[selectedBidding.modality].label}</Badge>
                    <Badge variant={agencyTypeConfig[selectedBidding.agencyType].color}>{agencyTypeConfig[selectedBidding.agencyType].label}</Badge>
                    <Badge variant={statusConfig[selectedBidding.status].color}>{statusConfig[selectedBidding.status].label}</Badge>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-text-muted mb-2">Objeto</p>
                <p className="font-medium text-text-primary">{selectedBidding.title}</p>
                <p className="text-sm text-text-secondary mt-1">{selectedBidding.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Órgão/Entidade</p>
                  <p className="font-medium text-text-primary">{selectedBidding.agency}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Responsável</p>
                  <p className="font-medium text-text-primary">{selectedBidding.responsible}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Valor Estimado</p>
                  <p className="text-xl font-bold text-text-primary">{formatCurrency(selectedBidding.estimatedValue)}</p>
                </div>
                {selectedBidding.ourProposal && (
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted mb-1">Nossa Proposta</p>
                    <p className="text-xl font-bold text-accent-primary">{formatCurrency(selectedBidding.ourProposal)}</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Publicação</p>
                  <p className="font-medium text-text-primary">{selectedBidding.publicationDate}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Prazo de Proposta</p>
                  <p className="font-medium text-text-primary">{selectedBidding.deadline}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Data de Abertura</p>
                  <p className="font-medium text-text-primary">{selectedBidding.openingDate}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Portal</p>
                  <p className="font-medium text-text-primary">{selectedBidding.portal}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Documentos</p>
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-text-muted" />
                    <p className="font-medium text-text-primary">{selectedBidding.documentsCount} documento(s)</p>
                  </div>
                </div>
              </div>

              {selectedBidding.hasAlert && selectedBidding.alertMessage && (
                <div className="p-4 bg-accent-warning/10 border border-accent-warning/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-accent-warning" />
                    <p className="font-medium text-accent-warning">{selectedBidding.alertMessage}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
