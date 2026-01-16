'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  FileText,
  Upload,
  Download,
  Eye,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Calendar,
  RefreshCw,
  FolderOpen,
  File,
  FileCheck,
  FileWarning,
  Shield,
  Building2,
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
interface BidDocument {
  id: string;
  name: string;
  type: 'certidao' | 'contrato_social' | 'balanco' | 'atestado' | 'declaracao' | 'procuracao' | 'outros';
  category: 'habilitacao_juridica' | 'regularidade_fiscal' | 'qualificacao_tecnica' | 'qualificacao_economica' | 'outros';
  status: 'valid' | 'expiring' | 'expired' | 'pending' | 'rejected';
  expirationDate: string | null;
  issueDate: string;
  issuingAuthority: string;
  fileName: string;
  fileSize: string;
  uploadedAt: string;
  uploadedBy: string;
  usedIn: string[];
  notes: string;
}

// Mock Data
const documents: BidDocument[] = [
  {
    id: '1',
    name: 'Certidão Negativa de Débitos Federais',
    type: 'certidao',
    category: 'regularidade_fiscal',
    status: 'valid',
    expirationDate: '2026-04-15',
    issueDate: '2025-10-15',
    issuingAuthority: 'Receita Federal do Brasil',
    fileName: 'CND_Federal_2025.pdf',
    fileSize: '245 KB',
    uploadedAt: '2025-10-16',
    uploadedBy: 'Ana Paula',
    usedIn: ['PE-001/2026', 'PE-002/2026'],
    notes: '',
  },
  {
    id: '2',
    name: 'Certidão Negativa FGTS',
    type: 'certidao',
    category: 'regularidade_fiscal',
    status: 'expiring',
    expirationDate: '2026-01-25',
    issueDate: '2025-10-25',
    issuingAuthority: 'Caixa Econômica Federal',
    fileName: 'CRF_FGTS_2025.pdf',
    fileSize: '180 KB',
    uploadedAt: '2025-10-26',
    uploadedBy: 'Carlos Eduardo',
    usedIn: ['PE-001/2026'],
    notes: 'Renovar antes de 25/01',
  },
  {
    id: '3',
    name: 'Contrato Social Consolidado',
    type: 'contrato_social',
    category: 'habilitacao_juridica',
    status: 'valid',
    expirationDate: null,
    issueDate: '2024-05-10',
    issuingAuthority: 'Junta Comercial SP',
    fileName: 'Contrato_Social_Consolidado.pdf',
    fileSize: '1.2 MB',
    uploadedAt: '2024-05-12',
    uploadedBy: 'Admin',
    usedIn: ['PE-001/2026', 'PE-002/2026', 'CC-003/2026'],
    notes: '',
  },
  {
    id: '4',
    name: 'Balanço Patrimonial 2024',
    type: 'balanco',
    category: 'qualificacao_economica',
    status: 'valid',
    expirationDate: '2026-04-30',
    issueDate: '2025-04-30',
    issuingAuthority: 'Contador Responsável',
    fileName: 'Balanco_2024.pdf',
    fileSize: '3.5 MB',
    uploadedAt: '2025-05-02',
    uploadedBy: 'Roberto Silva',
    usedIn: ['PE-001/2026', 'CC-003/2026'],
    notes: '',
  },
  {
    id: '5',
    name: 'Atestado de Capacidade Técnica - Prefeitura Guarulhos',
    type: 'atestado',
    category: 'qualificacao_tecnica',
    status: 'valid',
    expirationDate: null,
    issueDate: '2025-08-15',
    issuingAuthority: 'Prefeitura de Guarulhos',
    fileName: 'ACT_Guarulhos_2025.pdf',
    fileSize: '450 KB',
    uploadedAt: '2025-08-20',
    uploadedBy: 'Pedro Santos',
    usedIn: ['PE-002/2026'],
    notes: 'Contrato de vigilância patrimonial',
  },
  {
    id: '6',
    name: 'Certidão Negativa Trabalhista',
    type: 'certidao',
    category: 'regularidade_fiscal',
    status: 'expired',
    expirationDate: '2026-01-10',
    issueDate: '2025-07-10',
    issuingAuthority: 'TST',
    fileName: 'CNDT_2025.pdf',
    fileSize: '120 KB',
    uploadedAt: '2025-07-11',
    uploadedBy: 'Ana Paula',
    usedIn: [],
    notes: 'URGENTE: Documento vencido - Renovar imediatamente',
  },
  {
    id: '7',
    name: 'Declaração de Inexistência de Fato Impeditivo',
    type: 'declaracao',
    category: 'habilitacao_juridica',
    status: 'pending',
    expirationDate: null,
    issueDate: '2026-01-15',
    issuingAuthority: 'Empresa',
    fileName: '',
    fileSize: '',
    uploadedAt: '',
    uploadedBy: '',
    usedIn: ['PE-001/2026'],
    notes: 'Aguardando assinatura do representante legal',
  },
];

const typeConfig = {
  certidao: { label: 'Certidão', color: 'primary' as const },
  contrato_social: { label: 'Contrato Social', color: 'info' as const },
  balanco: { label: 'Balanço', color: 'success' as const },
  atestado: { label: 'Atestado', color: 'warning' as const },
  declaracao: { label: 'Declaração', color: 'info' as const },
  procuracao: { label: 'Procuração', color: 'info' as const },
  outros: { label: 'Outros', color: 'info' as const },
};

const categoryConfig = {
  habilitacao_juridica: { label: 'Habilitação Jurídica', icon: Building2 },
  regularidade_fiscal: { label: 'Regularidade Fiscal', icon: Shield },
  qualificacao_tecnica: { label: 'Qualificação Técnica', icon: FileCheck },
  qualificacao_economica: { label: 'Qualificação Econômica', icon: FileText },
  outros: { label: 'Outros', icon: File },
};

const statusConfig = {
  valid: { label: 'Válido', color: 'success' as const, icon: CheckCircle2 },
  expiring: { label: 'Vencendo', color: 'warning' as const, icon: AlertTriangle },
  expired: { label: 'Vencido', color: 'danger' as const, icon: XCircle },
  pending: { label: 'Pendente', color: 'info' as const, icon: Clock },
  rejected: { label: 'Rejeitado', color: 'danger' as const, icon: XCircle },
};

const columns: Column<BidDocument>[] = [
  {
    key: 'document',
    header: 'Documento',
    render: (row) => {
      const StatusIcon = statusConfig[row.status].icon;
      return (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            row.status === 'valid' ? 'bg-accent-success/20' :
            row.status === 'expiring' ? 'bg-accent-warning/20' :
            row.status === 'expired' ? 'bg-accent-danger/20' :
            'bg-bg-tertiary'
          }`}>
            <StatusIcon className={`w-5 h-5 ${
              row.status === 'valid' ? 'text-accent-success' :
              row.status === 'expiring' ? 'text-accent-warning' :
              row.status === 'expired' ? 'text-accent-danger' :
              'text-text-muted'
            }`} />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <Badge size="sm" variant={typeConfig[row.type].color}>
              {typeConfig[row.type].label}
            </Badge>
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
      const CategoryIcon = config.icon;
      return (
        <div className="flex items-center gap-2">
          <CategoryIcon className="w-4 h-4 text-text-muted" />
          <span className="text-sm">{config.label}</span>
        </div>
      );
    },
  },
  {
    key: 'validity',
    header: 'Validade',
    render: (row) => {
      if (!row.expirationDate) {
        return <span className="text-text-muted">Sem validade</span>;
      }

      const expDate = new Date(row.expirationDate);
      const today = new Date();
      const daysLeft = Math.ceil((expDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
      const isExpiring = daysLeft <= 30 && daysLeft > 0;
      const isExpired = daysLeft < 0;

      return (
        <div>
          <p className={`text-sm ${isExpiring ? 'text-accent-warning' : isExpired ? 'text-accent-danger' : ''}`}>
            {row.expirationDate}
          </p>
          {isExpiring && <p className="text-xs text-accent-warning">{daysLeft} dias restantes</p>}
          {isExpired && <p className="text-xs text-accent-danger">Vencido há {Math.abs(daysLeft)} dias</p>}
        </div>
      );
    },
  },
  {
    key: 'issuingAuthority',
    header: 'Emissor',
    render: (row) => (
      <p className="text-sm text-text-secondary truncate max-w-[150px]">{row.issuingAuthority}</p>
    ),
  },
  {
    key: 'usedIn',
    header: 'Usado em',
    render: (row) => (
      <div className="flex items-center gap-1">
        <FolderOpen className="w-4 h-4 text-text-muted" />
        <span className="text-sm">{row.usedIn.length} licitação(ões)</span>
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
        {row.fileName && (
          <>
            <Button variant="ghost" size="icon-sm" title="Visualizar">
              <Eye className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon-sm" title="Download">
              <Download className="w-4 h-4" />
            </Button>
          </>
        )}
        {row.status === 'expired' && (
          <Button variant="danger" size="sm" leftIcon={<RefreshCw className="w-3 h-3" />}>
            Renovar
          </Button>
        )}
        {row.status === 'pending' && (
          <Button variant="primary" size="sm" leftIcon={<Upload className="w-3 h-3" />}>
            Upload
          </Button>
        )}
      </div>
    ),
  },
];

export function BidDocumentsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Stats
  const validCount = documents.filter(d => d.status === 'valid').length;
  const expiringCount = documents.filter(d => d.status === 'expiring').length;
  const expiredCount = documents.filter(d => d.status === 'expired').length;
  const pendingCount = documents.filter(d => d.status === 'pending').length;

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.issuingAuthority.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTab =
      selectedTab === 'all' ||
      doc.status === selectedTab ||
      doc.category === selectedTab;

    return matchesSearch && matchesTab;
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Documentação para Licitações
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie documentos de habilitação e qualificação
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Verificar Validades
            </Button>
            <Button
              variant="primary"
              leftIcon={<Upload className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Upload Documento
            </Button>
          </div>
        </div>

        {/* Alert for expired/expiring documents */}
        {(expiredCount > 0 || expiringCount > 0) && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-xl border ${
              expiredCount > 0
                ? 'bg-accent-danger/10 border-accent-danger/30'
                : 'bg-accent-warning/10 border-accent-warning/30'
            }`}
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className={`w-5 h-5 ${expiredCount > 0 ? 'text-accent-danger' : 'text-accent-warning'}`} />
              <div className="flex-1">
                <p className={`font-medium ${expiredCount > 0 ? 'text-accent-danger' : 'text-accent-warning'}`}>
                  {expiredCount > 0
                    ? `${expiredCount} documento(s) vencido(s) - Ação imediata necessária`
                    : `${expiringCount} documento(s) vencendo nos próximos 30 dias`}
                </p>
                <p className="text-sm text-text-secondary">
                  {expiredCount > 0
                    ? 'Documentos vencidos impossibilitam participação em licitações'
                    : 'Agende a renovação para evitar problemas'}
                </p>
              </div>
              <Button variant={expiredCount > 0 ? 'danger' : 'secondary'} size="sm">
                Ver Documentos
              </Button>
            </div>
          </motion.div>
        )}

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Válidos"
              value={validCount}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Vencendo"
              value={expiringCount}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Vencidos"
              value={expiredCount}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Pendentes"
              value={pendingCount}
              icon={<Clock className="w-6 h-6" />}
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
                  { value: 'all', label: `Todos (${documents.length})` },
                  { value: 'valid', label: `Válidos (${validCount})` },
                  { value: 'expiring', label: `Vencendo (${expiringCount})` },
                  { value: 'expired', label: `Vencidos (${expiredCount})` },
                  { value: 'pending', label: `Pendentes (${pendingCount})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar documento..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Select
                  options={[
                    { value: 'all', label: 'Todas as Categorias' },
                    { value: 'habilitacao_juridica', label: 'Habilitação Jurídica' },
                    { value: 'regularidade_fiscal', label: 'Regularidade Fiscal' },
                    { value: 'qualificacao_tecnica', label: 'Qualificação Técnica' },
                    { value: 'qualificacao_economica', label: 'Qualificação Econômica' },
                  ]}
                  value="all"
                  onChange={() => {}}
                  className="w-48"
                />
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Documents Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredDocuments}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => console.log('Document clicked:', row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Upload Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Upload de Documento"
          description="Adicione um novo documento ao acervo"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Fazer Upload
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome do Documento" placeholder="Ex: Certidão Negativa de Débitos" required />
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo"
                options={[
                  { value: 'certidao', label: 'Certidão' },
                  { value: 'contrato_social', label: 'Contrato Social' },
                  { value: 'balanco', label: 'Balanço' },
                  { value: 'atestado', label: 'Atestado' },
                  { value: 'declaracao', label: 'Declaração' },
                  { value: 'procuracao', label: 'Procuração' },
                  { value: 'outros', label: 'Outros' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Categoria"
                options={[
                  { value: 'habilitacao_juridica', label: 'Habilitação Jurídica' },
                  { value: 'regularidade_fiscal', label: 'Regularidade Fiscal' },
                  { value: 'qualificacao_tecnica', label: 'Qualificação Técnica' },
                  { value: 'qualificacao_economica', label: 'Qualificação Econômica' },
                  { value: 'outros', label: 'Outros' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data de Emissão" type="date" required />
              <Input label="Data de Validade" type="date" />
            </div>
            <Input label="Órgão Emissor" placeholder="Ex: Receita Federal do Brasil" />
            <div className="p-8 border-2 border-dashed border-border-default rounded-xl text-center">
              <Upload className="w-8 h-8 text-text-muted mx-auto mb-2" />
              <p className="text-sm text-text-secondary">
                Arraste um arquivo ou clique para selecionar
              </p>
              <p className="text-xs text-text-muted mt-1">
                PDF, JPG ou PNG até 10MB
              </p>
            </div>
            <Input label="Observações" placeholder="Notas sobre o documento" />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
