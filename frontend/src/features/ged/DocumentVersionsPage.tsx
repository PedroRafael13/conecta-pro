'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  FileText,
  Clock,
  GitBranch,
  GitCommit,
  RotateCcw,
  Download,
  Eye,
  Diff,
  ChevronDown,
  ChevronRight,
  User,
  Calendar,
  AlertCircle,
  CheckCircle2,
  History,
  ArrowLeftRight,
  Lock,
  MoreHorizontal,
  Filter,
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
interface DocumentVersion {
  id: string;
  documentId: string;
  documentName: string;
  version: string;
  author: string;
  createdAt: string;
  size: number;
  changeType: 'major' | 'minor' | 'patch';
  changeDescription: string;
  status: 'current' | 'archived' | 'draft';
  locked: boolean;
  downloads: number;
}

interface Document {
  id: string;
  name: string;
  currentVersion: string;
  totalVersions: number;
  lastModified: string;
  author: string;
  category: string;
}

// Mock Data
const documents: Document[] = [
  {
    id: '1',
    name: 'Contrato Shopping Center Norte',
    currentVersion: '3.2.0',
    totalVersions: 12,
    lastModified: '2026-01-15',
    author: 'Ana Costa',
    category: 'Contratos',
  },
  {
    id: '2',
    name: 'Manual de Procedimentos Operacionais',
    currentVersion: '2.5.1',
    totalVersions: 28,
    lastModified: '2026-01-14',
    author: 'Carlos Lima',
    category: 'Manuais',
  },
  {
    id: '3',
    name: 'Política de Segurança da Informação',
    currentVersion: '1.8.0',
    totalVersions: 8,
    lastModified: '2026-01-10',
    author: 'Roberto Silva',
    category: 'Políticas',
  },
  {
    id: '4',
    name: 'Relatório Anual 2025',
    currentVersion: '1.0.0',
    totalVersions: 5,
    lastModified: '2026-01-05',
    author: 'Maria Oliveira',
    category: 'Relatórios',
  },
];

const versions: DocumentVersion[] = [
  {
    id: 'v1',
    documentId: '1',
    documentName: 'Contrato Shopping Center Norte',
    version: '3.2.0',
    author: 'Ana Costa',
    createdAt: '2026-01-15T14:30:00',
    size: 2450000,
    changeType: 'minor',
    changeDescription: 'Atualização das cláusulas de pagamento',
    status: 'current',
    locked: false,
    downloads: 15,
  },
  {
    id: 'v2',
    documentId: '1',
    documentName: 'Contrato Shopping Center Norte',
    version: '3.1.0',
    author: 'Ana Costa',
    createdAt: '2026-01-10T09:15:00',
    size: 2380000,
    changeType: 'minor',
    changeDescription: 'Adição de anexo técnico',
    status: 'archived',
    locked: true,
    downloads: 8,
  },
  {
    id: 'v3',
    documentId: '1',
    documentName: 'Contrato Shopping Center Norte',
    version: '3.0.0',
    author: 'Roberto Silva',
    createdAt: '2025-12-20T16:45:00',
    size: 2200000,
    changeType: 'major',
    changeDescription: 'Nova versão do contrato com revisão completa',
    status: 'archived',
    locked: true,
    downloads: 45,
  },
  {
    id: 'v4',
    documentId: '2',
    documentName: 'Manual de Procedimentos Operacionais',
    version: '2.5.1',
    author: 'Carlos Lima',
    createdAt: '2026-01-14T11:20:00',
    size: 5800000,
    changeType: 'patch',
    changeDescription: 'Correção de erros de formatação',
    status: 'current',
    locked: false,
    downloads: 32,
  },
  {
    id: 'v5',
    documentId: '2',
    documentName: 'Manual de Procedimentos Operacionais',
    version: '2.5.0',
    author: 'Carlos Lima',
    createdAt: '2026-01-12T08:00:00',
    size: 5750000,
    changeType: 'minor',
    changeDescription: 'Novo capítulo sobre segurança',
    status: 'archived',
    locked: true,
    downloads: 18,
  },
];

const tabs = [
  { id: 'all', label: 'Todos os Documentos' },
  { id: 'recent', label: 'Alterados Recentemente' },
  { id: 'draft', label: 'Rascunhos' },
  { id: 'locked', label: 'Bloqueados' },
];

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const changeTypeColors = {
  major: 'danger',
  minor: 'warning',
  patch: 'info',
} as const;

const changeTypeLabels = {
  major: 'Major',
  minor: 'Minor',
  patch: 'Patch',
};

const statusColors = {
  current: 'success',
  archived: 'secondary',
  draft: 'warning',
} as const;

const statusLabels = {
  current: 'Atual',
  archived: 'Arquivado',
  draft: 'Rascunho',
};

const documentColumns: Column<Document>[] = [
  {
    key: 'name',
    header: 'Documento',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <FileText className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.category}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'currentVersion',
    header: 'Versão Atual',
    render: (row) => (
      <div className="flex items-center gap-2">
        <GitBranch className="w-4 h-4 text-success" />
        <span className="font-mono font-medium text-success">v{row.currentVersion}</span>
      </div>
    ),
  },
  {
    key: 'totalVersions',
    header: 'Histórico',
    render: (row) => (
      <div className="flex items-center gap-2">
        <History className="w-4 h-4 text-text-muted" />
        <span>{row.totalVersions} versões</span>
      </div>
    ),
  },
  {
    key: 'author',
    header: 'Autor',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.author} size="xs" />
        <span className="text-sm">{row.author}</span>
      </div>
    ),
  },
  {
    key: 'lastModified',
    header: 'Última Modificação',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {new Date(row.lastModified).toLocaleDateString('pt-BR')}
      </span>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver Histórico">
          <History className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Comparar Versões">
          <ArrowLeftRight className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function DocumentVersionsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const documentVersions = selectedDocument
    ? versions.filter(v => v.documentId === selectedDocument.id)
    : [];

  // Stats
  const totalVersions = versions.length;
  const currentVersions = versions.filter(v => v.status === 'current').length;
  const lockedVersions = versions.filter(v => v.locked).length;
  const totalDownloads = versions.reduce((acc, v) => acc + v.downloads, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Controle de Versões
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie o histórico e versões dos documentos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<ArrowLeftRight className="w-4 h-4" />}>
              Comparar Versões
            </Button>
            <Button variant="primary" leftIcon={<GitCommit className="w-4 h-4" />}>
              Nova Versão
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Total de Versões"
              value={totalVersions}
              icon={<GitBranch className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Versões Atuais"
              value={currentVersions}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Versões Bloqueadas"
              value={lockedVersions}
              icon={<Lock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Total de Downloads"
              value={totalDownloads}
              icon={<Download className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Main Content - Split View */}
        <div className="grid grid-cols-5 gap-6">
          {/* Document List */}
          <div className="col-span-2">
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Documentos</h3>
                  <Input
                    placeholder="Buscar..."
                    leftIcon={<Search className="w-4 h-4" />}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-48"
                  />
                </div>
              </CardHeader>
              <CardBody className="p-0">
                <div className="divide-y divide-border">
                  {filteredDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className={`p-4 cursor-pointer transition-colors ${
                        selectedDocument?.id === doc.id
                          ? 'bg-primary/5 border-l-2 border-primary'
                          : 'hover:bg-bg-secondary/50'
                      }`}
                      onClick={() => setSelectedDocument(doc)}
                    >
                      <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <FileText className="w-4 h-4 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary truncate">{doc.name}</p>
                          <div className="flex items-center gap-3 mt-1">
                            <Badge variant="success" size="sm">v{doc.currentVersion}</Badge>
                            <span className="text-xs text-text-muted">{doc.totalVersions} versões</span>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-text-muted" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Version History */}
          <div className="col-span-3">
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">
                      {selectedDocument ? 'Histórico de Versões' : 'Selecione um Documento'}
                    </h3>
                    {selectedDocument && (
                      <p className="text-sm text-text-muted mt-1">{selectedDocument.name}</p>
                    )}
                  </div>
                  {selectedDocument && (
                    <Button
                      variant="outline"
                      size="sm"
                      leftIcon={<ArrowLeftRight className="w-4 h-4" />}
                      onClick={() => setIsCompareModalOpen(true)}
                    >
                      Comparar
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardBody>
                {selectedDocument ? (
                  <div className="space-y-4">
                    {/* Version Timeline */}
                    <div className="relative">
                      {documentVersions.map((version, index) => (
                        <div key={version.id} className="relative pl-8 pb-6 last:pb-0">
                          {/* Timeline line */}
                          {index < documentVersions.length - 1 && (
                            <div className="absolute left-[11px] top-8 bottom-0 w-0.5 bg-border" />
                          )}
                          {/* Timeline dot */}
                          <div className={`absolute left-0 top-1 w-6 h-6 rounded-full flex items-center justify-center ${
                            version.status === 'current'
                              ? 'bg-success text-white'
                              : 'bg-bg-secondary border-2 border-border'
                          }`}>
                            {version.status === 'current' ? (
                              <CheckCircle2 className="w-4 h-4" />
                            ) : (
                              <GitCommit className="w-3 h-3 text-text-muted" />
                            )}
                          </div>
                          {/* Version Card */}
                          <div className="bg-bg-secondary/50 rounded-lg p-4 border border-border hover:border-primary/30 transition-colors">
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <span className="font-mono font-bold text-lg">v{version.version}</span>
                                <Badge variant={changeTypeColors[version.changeType]} size="sm">
                                  {changeTypeLabels[version.changeType]}
                                </Badge>
                                <Badge variant={statusColors[version.status]} size="sm">
                                  {statusLabels[version.status]}
                                </Badge>
                                {version.locked && (
                                  <Lock className="w-4 h-4 text-warning" />
                                )}
                              </div>
                              <div className="flex items-center gap-1">
                                <Button variant="ghost" size="icon-sm" title="Visualizar">
                                  <Eye className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="icon-sm" title="Download">
                                  <Download className="w-4 h-4" />
                                </Button>
                                {!version.locked && version.status !== 'current' && (
                                  <Button variant="ghost" size="icon-sm" title="Restaurar">
                                    <RotateCcw className="w-4 h-4" />
                                  </Button>
                                )}
                                <Button variant="ghost" size="icon-sm">
                                  <MoreHorizontal className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                            <p className="text-text-secondary mb-3">{version.changeDescription}</p>
                            <div className="flex items-center gap-4 text-sm text-text-muted">
                              <div className="flex items-center gap-1">
                                <Avatar name={version.author} size="xs" />
                                <span>{version.author}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                <span>{new Date(version.createdAt).toLocaleString('pt-BR')}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Download className="w-4 h-4" />
                                <span>{version.downloads} downloads</span>
                              </div>
                              <span>{formatFileSize(version.size)}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-64 text-text-muted">
                    <History className="w-12 h-12 mb-4 opacity-50" />
                    <p>Selecione um documento para ver o histórico de versões</p>
                  </div>
                )}
              </CardBody>
            </Card>
          </div>
        </div>

        {/* Compare Modal */}
        <Modal
          isOpen={isCompareModalOpen}
          onClose={() => setIsCompareModalOpen(false)}
          title="Comparar Versões"
          description="Selecione duas versões para comparar"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCompareModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsCompareModalOpen(false)}>
                Comparar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Versão Original"
                options={documentVersions.map(v => ({
                  value: v.id,
                  label: `v${v.version} - ${new Date(v.createdAt).toLocaleDateString('pt-BR')}`
                }))}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Versão para Comparar"
                options={documentVersions.map(v => ({
                  value: v.id,
                  label: `v${v.version} - ${new Date(v.createdAt).toLocaleDateString('pt-BR')}`
                }))}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <div className="p-4 rounded-lg bg-info/10 border border-info/20">
              <div className="flex items-center gap-2 mb-2">
                <Diff className="w-5 h-5 text-info" />
                <span className="font-medium text-info">Visualização de Diferenças</span>
              </div>
              <p className="text-sm text-text-secondary">
                Após selecionar as versões, você poderá ver as diferenças lado a lado
                com destaque para adições, remoções e modificações.
              </p>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
