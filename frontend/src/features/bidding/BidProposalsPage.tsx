'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  FileText,
  DollarSign,
  Calculator,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit,
  Download,
  Send,
  Copy,
  Percent,
  TrendingUp,
  TrendingDown,
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
  Avatar,
} from '@/design-system/components';

// Types
interface BidProposal {
  id: string;
  biddingNumber: string;
  biddingTitle: string;
  agency: string;
  status: 'draft' | 'review' | 'approved' | 'sent' | 'winner' | 'loser' | 'cancelled';
  estimatedValue: number;
  proposedValue: number;
  discount: number;
  margin: number;
  costs: {
    labor: number;
    materials: number;
    overhead: number;
    taxes: number;
  };
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  sentAt: string | null;
  deadline: string;
  version: number;
  notes: string;
}

// Mock Data
const proposals: BidProposal[] = [
  {
    id: '1',
    biddingNumber: 'PE-001/2026',
    biddingTitle: 'Serviços de vigilância patrimonial armada e desarmada',
    agency: 'Prefeitura Municipal de São Paulo',
    status: 'draft',
    estimatedValue: 2500000,
    proposedValue: 2350000,
    discount: 6,
    margin: 15,
    costs: { labor: 1600000, materials: 120000, overhead: 180000, taxes: 250000 },
    createdBy: 'Ana Paula',
    createdAt: '2026-01-12',
    updatedAt: '2026-01-15',
    sentAt: null,
    deadline: '2026-01-20',
    version: 3,
    notes: 'Aguardando aprovação do diretor financeiro',
  },
  {
    id: '2',
    biddingNumber: 'PE-002/2026',
    biddingTitle: 'Instalação e manutenção de sistema de CFTV',
    agency: 'Governo do Estado de SP',
    status: 'sent',
    estimatedValue: 850000,
    proposedValue: 780000,
    discount: 8.2,
    margin: 18,
    costs: { labor: 350000, materials: 200000, overhead: 80000, taxes: 78000 },
    createdBy: 'Carlos Eduardo',
    createdAt: '2026-01-08',
    updatedAt: '2026-01-14',
    sentAt: '2026-01-14 15:30',
    deadline: '2026-01-15',
    version: 5,
    notes: 'Proposta enviada dentro do prazo',
  },
  {
    id: '3',
    biddingNumber: 'CC-003/2026',
    biddingTitle: 'Segurança para eventos municipais',
    agency: 'Câmara Municipal de Campinas',
    status: 'winner',
    estimatedValue: 180000,
    proposedValue: 165000,
    discount: 8.3,
    margin: 20,
    costs: { labor: 95000, materials: 15000, overhead: 22000, taxes: 16500 },
    createdBy: 'Roberto Silva',
    createdAt: '2025-12-28',
    updatedAt: '2026-01-08',
    sentAt: '2026-01-09 10:00',
    deadline: '2026-01-10',
    version: 4,
    notes: 'Contrato em fase de assinatura',
  },
  {
    id: '4',
    biddingNumber: 'TP-008/2025',
    biddingTitle: 'Sistema de controle de acesso predial',
    agency: 'Tribunal de Justiça do Estado',
    status: 'loser',
    estimatedValue: 320000,
    proposedValue: 295000,
    discount: 7.8,
    margin: 16,
    costs: { labor: 150000, materials: 80000, overhead: 25000, taxes: 29500 },
    createdBy: 'Pedro Santos',
    createdAt: '2025-11-20',
    updatedAt: '2025-11-30',
    sentAt: '2025-11-30 14:00',
    deadline: '2025-12-01',
    version: 6,
    notes: 'Vencedor: R$ 278.000,00 - Margem muito apertada',
  },
  {
    id: '5',
    biddingNumber: 'PE-020/2025',
    biddingTitle: 'Central de monitoramento 24h',
    agency: 'Ministério da Educação',
    status: 'review',
    estimatedValue: 1200000,
    proposedValue: 1100000,
    discount: 8.3,
    margin: 17,
    costs: { labor: 650000, materials: 180000, overhead: 110000, taxes: 110000 },
    createdBy: 'Ana Paula',
    createdAt: '2026-01-10',
    updatedAt: '2026-01-14',
    sentAt: null,
    deadline: '2026-01-25',
    version: 2,
    notes: 'Em revisão pelo departamento técnico',
  },
];

const statusConfig = {
  draft: { label: 'Rascunho', color: 'neutral' as const },
  review: { label: 'Em Revisão', color: 'warning' as const },
  approved: { label: 'Aprovada', color: 'info' as const },
  sent: { label: 'Enviada', color: 'primary' as const },
  winner: { label: 'Vencedora', color: 'success' as const },
  loser: { label: 'Não Venceu', color: 'danger' as const },
  cancelled: { label: 'Cancelada', color: 'danger' as const },
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

const columns: Column<BidProposal>[] = [
  {
    key: 'bidding',
    header: 'Licitação',
    render: (row) => (
      <div>
        <span className="font-mono text-sm font-bold text-accent-primary">{row.biddingNumber}</span>
        <p className="text-xs text-text-muted mt-1 truncate max-w-[200px]">{row.biddingTitle}</p>
      </div>
    ),
  },
  {
    key: 'values',
    header: 'Valores',
    render: (row) => (
      <div>
        <p className="text-sm text-text-muted">Est: {formatCurrency(row.estimatedValue)}</p>
        <p className="text-sm font-medium text-text-primary">Nossa: {formatCurrency(row.proposedValue)}</p>
      </div>
    ),
  },
  {
    key: 'discount',
    header: 'Desconto',
    render: (row) => (
      <div className="flex items-center gap-2">
        <TrendingDown className="w-4 h-4 text-accent-success" />
        <span className="font-medium text-accent-success">{row.discount.toFixed(1)}%</span>
      </div>
    ),
  },
  {
    key: 'margin',
    header: 'Margem',
    render: (row) => {
      const marginColor = row.margin >= 18 ? 'text-accent-success' : row.margin >= 12 ? 'text-accent-warning' : 'text-accent-danger';
      return (
        <div className="flex items-center gap-2">
          <Percent className={`w-4 h-4 ${marginColor}`} />
          <span className={`font-medium ${marginColor}`}>{row.margin}%</span>
        </div>
      );
    },
  },
  {
    key: 'createdBy',
    header: 'Responsável',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.createdBy} size="xs" />
        <div>
          <p className="text-sm">{row.createdBy}</p>
          <p className="text-xs text-text-muted">v{row.version}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'deadline',
    header: 'Prazo',
    render: (row) => {
      const deadlineDate = new Date(row.deadline);
      const today = new Date();
      const daysLeft = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
      const isUrgent = daysLeft <= 3 && daysLeft > 0;

      return (
        <div>
          <p className={`text-sm ${isUrgent ? 'text-accent-warning font-medium' : ''}`}>{row.deadline}</p>
          {isUrgent && <p className="text-xs text-accent-warning">{daysLeft} dias restantes</p>}
        </div>
      );
    },
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
        {(row.status === 'draft' || row.status === 'review') && (
          <>
            <Button variant="ghost" size="icon-sm" title="Editar">
              <Edit className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Duplicar">
              <Copy className="w-4 h-4" />
            </Button>
          </>
        )}
        {row.status === 'approved' && (
          <Button variant="primary" size="sm" leftIcon={<Send className="w-3 h-3" />}>
            Enviar
          </Button>
        )}
        <Button variant="ghost" size="icon-sm" title="Download PDF">
          <Download className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function BidProposalsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<BidProposal | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Stats
  const draftCount = proposals.filter(p => p.status === 'draft').length;
  const reviewCount = proposals.filter(p => p.status === 'review').length;
  const sentCount = proposals.filter(p => p.status === 'sent').length;
  const winnerCount = proposals.filter(p => p.status === 'winner').length;
  const totalProposed = proposals.reduce((acc, p) => acc + p.proposedValue, 0);
  const avgMargin = proposals.reduce((acc, p) => acc + p.margin, 0) / proposals.length;

  const filteredProposals = proposals.filter((proposal) => {
    const matchesSearch =
      proposal.biddingNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      proposal.biddingTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
      proposal.agency.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTab =
      selectedTab === 'all' ||
      proposal.status === selectedTab;

    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Propostas Comerciais
            </h1>
            <p className="text-text-secondary mt-1">
              Elabore e gerencie propostas para licitações
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Calculator className="w-4 h-4" />}>
              Simulador de Preços
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Proposta
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={3}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Rascunhos"
              value={draftCount}
              icon={<FileText className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Em Revisão"
              value={reviewCount}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Enviadas"
              value={sentCount}
              icon={<Send className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Vencedoras"
              value={winnerCount}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <StatCard
              title="Valor Total"
              value={formatCurrency(totalProposed)}
              icon={<DollarSign className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <StatCard
              title="Margem Média"
              value={`${avgMargin.toFixed(1)}%`}
              icon={<Percent className="w-6 h-6" />}
              iconColor={avgMargin >= 15 ? 'success' : 'warning'}
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: 'Todas' },
                  { value: 'draft', label: `Rascunhos (${draftCount})` },
                  { value: 'review', label: `Em Revisão (${reviewCount})` },
                  { value: 'sent', label: `Enviadas (${sentCount})` },
                  { value: 'winner', label: `Vencedoras (${winnerCount})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar proposta..."
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

        {/* Proposals Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredProposals}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => { setSelectedProposal(row); setShowDetailModal(true); }}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Proposal Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Proposta"
          description="Elabore uma nova proposta comercial"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Criar Proposta
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Licitação"
              options={[
                { value: '1', label: 'PE-001/2026 - Vigilância Patrimonial' },
                { value: '2', label: 'PE-020/2025 - Central de Monitoramento' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione a licitação..."
            />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Valor Proposto" type="number" placeholder="0,00" required />
              <Input label="Margem Desejada (%)" type="number" placeholder="15" />
            </div>
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="font-medium text-text-primary mb-3">Composição de Custos</h4>
              <div className="grid grid-cols-2 gap-4">
                <Input label="Mão de Obra" type="number" placeholder="0,00" />
                <Input label="Materiais" type="number" placeholder="0,00" />
                <Input label="Despesas Indiretas" type="number" placeholder="0,00" />
                <Input label="Impostos" type="number" placeholder="0,00" />
              </div>
            </div>
            <Input label="Observações" placeholder="Notas sobre a proposta" />
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Detalhes da Proposta"
          description={selectedProposal ? `${selectedProposal.biddingNumber} - v${selectedProposal.version}` : ''}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
                Fechar
              </Button>
              <Button variant="outline" leftIcon={<Download className="w-4 h-4" />}>
                Download PDF
              </Button>
              {selectedProposal?.status === 'approved' && (
                <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                  Enviar Proposta
                </Button>
              )}
            </>
          }
        >
          {selectedProposal && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl">
                <div className="p-3 rounded-lg bg-bg-primary">
                  <FileText className="w-6 h-6 text-text-muted" />
                </div>
                <div className="flex-1">
                  <p className="font-mono text-lg font-bold text-accent-primary">{selectedProposal.biddingNumber}</p>
                  <p className="text-sm text-text-muted">{selectedProposal.biddingTitle}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={statusConfig[selectedProposal.status].color}>{statusConfig[selectedProposal.status].label}</Badge>
                    <Badge variant="neutral">v{selectedProposal.version}</Badge>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-1">Órgão/Entidade</p>
                <p className="font-medium text-text-primary">{selectedProposal.agency}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Valor Estimado</p>
                  <p className="text-xl font-bold text-text-secondary">{formatCurrency(selectedProposal.estimatedValue)}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Valor Proposto</p>
                  <p className="text-xl font-bold text-accent-primary">{formatCurrency(selectedProposal.proposedValue)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <TrendingDown className="w-6 h-6 mx-auto mb-2 text-accent-success" />
                  <p className="text-2xl font-bold text-accent-success">{selectedProposal.discount.toFixed(1)}%</p>
                  <p className="text-sm text-text-muted">Desconto</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg text-center">
                  <Percent className={`w-6 h-6 mx-auto mb-2 ${
                    selectedProposal.margin >= 18 ? 'text-accent-success' :
                    selectedProposal.margin >= 12 ? 'text-accent-warning' : 'text-accent-danger'
                  }`} />
                  <p className={`text-2xl font-bold ${
                    selectedProposal.margin >= 18 ? 'text-accent-success' :
                    selectedProposal.margin >= 12 ? 'text-accent-warning' : 'text-accent-danger'
                  }`}>{selectedProposal.margin}%</p>
                  <p className="text-sm text-text-muted">Margem</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-3">Composição de Custos</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-text-muted">Mão de Obra</p>
                    <p className="font-medium text-text-primary">{formatCurrency(selectedProposal.costs.labor)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-text-muted">Materiais</p>
                    <p className="font-medium text-text-primary">{formatCurrency(selectedProposal.costs.materials)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-text-muted">Despesas Indiretas</p>
                    <p className="font-medium text-text-primary">{formatCurrency(selectedProposal.costs.overhead)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-text-muted">Impostos</p>
                    <p className="font-medium text-text-primary">{formatCurrency(selectedProposal.costs.taxes)}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Criado por</p>
                  <div className="flex items-center gap-2">
                    <Avatar name={selectedProposal.createdBy} size="sm" />
                    <span className="font-medium text-text-primary">{selectedProposal.createdBy}</span>
                  </div>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Prazo</p>
                  <p className="font-medium text-text-primary">{selectedProposal.deadline}</p>
                </div>
              </div>

              {selectedProposal.sentAt && (
                <div className="p-4 bg-accent-success/10 border border-accent-success/30 rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Enviada em</p>
                  <p className="font-medium text-accent-success">{selectedProposal.sentAt}</p>
                </div>
              )}

              {selectedProposal.notes && (
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Observações</p>
                  <p className="text-text-primary">{selectedProposal.notes}</p>
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
