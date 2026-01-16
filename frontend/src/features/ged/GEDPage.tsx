'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Upload,
  Download,
  FolderOpen,
  FileText,
  File,
  Image,
  FileSpreadsheet,
  FileArchive,
  MoreHorizontal,
  Eye,
  Share2,
  Trash2,
  Plus,
  Grid,
  List,
  Clock,
  User,
  HardDrive,
  Folder,
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
interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'doc' | 'xls' | 'img' | 'zip' | 'folder';
  size: number;
  folder: string;
  category: string;
  uploadedBy: string;
  uploadedAt: string;
  lastModified: string;
  tags: string[];
  shared: boolean;
}

// Mock Data
const documents: Document[] = [
  {
    id: '1',
    name: 'Contrato Shopping Center Norte',
    type: 'pdf',
    size: 2450000,
    folder: '/Contratos/2026',
    category: 'Contratos',
    uploadedBy: 'Ana Costa',
    uploadedAt: '2026-01-15',
    lastModified: '2026-01-15',
    tags: ['Contrato', 'Ativo'],
    shared: true,
  },
  {
    id: '2',
    name: 'Relatório Financeiro Janeiro',
    type: 'xls',
    size: 890000,
    folder: '/Financeiro/2026',
    category: 'Financeiro',
    uploadedBy: 'Carlos Lima',
    uploadedAt: '2026-01-14',
    lastModified: '2026-01-15',
    tags: ['Relatório', 'Mensal'],
    shared: false,
  },
  {
    id: '3',
    name: 'Proposta Hospital São Lucas',
    type: 'doc',
    size: 1200000,
    folder: '/Propostas/2026',
    category: 'Propostas',
    uploadedBy: 'Roberto Silva',
    uploadedAt: '2026-01-13',
    lastModified: '2026-01-14',
    tags: ['Proposta', 'Pendente'],
    shared: true,
  },
  {
    id: '4',
    name: 'Fotos Vistoria Condomínio',
    type: 'img',
    size: 15800000,
    folder: '/Operacional/Vistorias',
    category: 'Operacional',
    uploadedBy: 'Pedro Santos',
    uploadedAt: '2026-01-12',
    lastModified: '2026-01-12',
    tags: ['Vistoria', 'Fotos'],
    shared: false,
  },
  {
    id: '5',
    name: 'Backup Documentos RH',
    type: 'zip',
    size: 45000000,
    folder: '/RH/Backup',
    category: 'RH',
    uploadedBy: 'Maria Oliveira',
    uploadedAt: '2026-01-10',
    lastModified: '2026-01-10',
    tags: ['Backup', 'RH'],
    shared: false,
  },
];

const folders = [
  { id: '1', name: 'Contratos', icon: FileText, count: 45, color: 'primary' },
  { id: '2', name: 'Financeiro', icon: FileSpreadsheet, count: 128, color: 'success' },
  { id: '3', name: 'Propostas', icon: File, count: 32, color: 'warning' },
  { id: '4', name: 'RH', icon: User, count: 256, color: 'info' },
  { id: '5', name: 'Operacional', icon: FolderOpen, count: 89, color: 'secondary' },
];

const typeConfig = {
  pdf: { icon: FileText, color: 'danger' },
  doc: { icon: File, color: 'primary' },
  xls: { icon: FileSpreadsheet, color: 'success' },
  img: { icon: Image, color: 'warning' },
  zip: { icon: FileArchive, color: 'secondary' },
  folder: { icon: Folder, color: 'info' },
};

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const columns: Column<Document>[] = [
  {
    key: 'name',
    header: 'Nome',
    render: (row) => {
      const config = typeConfig[row.type];
      const Icon = config.icon;
      return (
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-${config.color}/10`}>
            <Icon className={`w-5 h-5 text-${config.color}`} />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.folder}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => <Badge variant="secondary">{row.category}</Badge>,
  },
  {
    key: 'size',
    header: 'Tamanho',
    render: (row) => (
      <span className="font-mono text-sm text-text-secondary">
        {formatFileSize(row.size)}
      </span>
    ),
  },
  {
    key: 'uploadedBy',
    header: 'Enviado por',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.uploadedBy} size="xs" />
        <span className="text-sm text-text-secondary">{row.uploadedBy}</span>
      </div>
    ),
  },
  {
    key: 'lastModified',
    header: 'Modificado',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {new Date(row.lastModified).toLocaleDateString('pt-BR')}
      </span>
    ),
  },
  {
    key: 'tags',
    header: 'Tags',
    render: (row) => (
      <div className="flex flex-wrap gap-1">
        {row.tags.slice(0, 2).map((tag) => (
          <Badge key={tag} variant="neutral" size="sm">{tag}</Badge>
        ))}
      </div>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Visualizar">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Compartilhar">
          <Share2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Download">
          <Download className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function GEDPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [selectedFolder, setSelectedFolder] = useState('all');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFolder = selectedFolder === 'all' || doc.category === selectedFolder;
    return matchesSearch && matchesFolder;
  });

  // Stats
  const totalDocuments = documents.length;
  const totalSize = documents.reduce((acc, doc) => acc + doc.size, 0);
  const sharedDocuments = documents.filter((d) => d.shared).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gestão de Documentos
            </h1>
            <p className="text-text-secondary mt-1">
              Armazenamento e organização eletrônica de documentos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<FolderOpen className="w-4 h-4" />}>
              Nova Pasta
            </Button>
            <Button
              variant="primary"
              leftIcon={<Upload className="w-4 h-4" />}
              onClick={() => setIsUploadModalOpen(true)}
            >
              Upload
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
              title="Total de Documentos"
              value={totalDocuments}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Espaço Utilizado"
              value={formatFileSize(totalSize)}
              icon={<HardDrive className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Compartilhados"
              value={sharedDocuments}
              icon={<Share2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Pastas"
              value={folders.length}
              icon={<Folder className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Folders */}
        <div className="grid grid-cols-5 gap-4">
          {folders.map((folder) => {
            const Icon = folder.icon;
            return (
              <Card
                key={folder.id}
                className={`cursor-pointer transition-colors ${
                  selectedFolder === folder.name
                    ? 'border-accent-primary bg-accent-primary/5'
                    : 'hover:border-accent-primary/50'
                }`}
                onClick={() => setSelectedFolder(folder.name)}
              >
                <CardBody className="py-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-${folder.color}/10`}>
                      <Icon className={`w-5 h-5 text-${folder.color}`} />
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{folder.name}</p>
                      <p className="text-xs text-text-muted">{folder.count} arquivos</p>
                    </div>
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>

        {/* Search & View Toggle */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="flex items-center text-sm text-text-muted">
                  <Folder className="w-4 h-4 mr-2" />
                  <span>Documentos</span>
                  {selectedFolder !== 'all' && (
                    <>
                      <ChevronRight className="w-4 h-4 mx-1" />
                      <span className="text-text-primary">{selectedFolder}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar documentos..."
                  leftIcon={<Search className="w-4 h-4" />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
                <div className="flex items-center gap-1 bg-bg-secondary rounded-lg p-1">
                  <Button
                    variant={viewMode === 'list' ? 'primary' : 'ghost'}
                    size="icon-sm"
                    onClick={() => setViewMode('list')}
                  >
                    <List className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'grid' ? 'primary' : 'ghost'}
                    size="icon-sm"
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Documents */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {viewMode === 'list' ? (
            <Card>
              <CardBody className="p-0">
                <DataTable
                  columns={columns}
                  data={filteredDocuments}
                  keyExtractor={(row) => row.id}
                  onRowClick={(row) => { setSelectedDocument(row); setShowDetailModal(true); }}
                />
              </CardBody>
            </Card>
          ) : (
            <div className="grid grid-cols-4 gap-4">
              {filteredDocuments.map((doc) => {
                const config = typeConfig[doc.type];
                const Icon = config.icon;
                return (
                  <Card key={doc.id} className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                    <CardBody>
                      <div className="flex flex-col items-center text-center">
                        <div className={`p-4 rounded-xl bg-${config.color}/10 mb-3`}>
                          <Icon className={`w-8 h-8 text-${config.color}`} />
                        </div>
                        <p className="font-medium text-text-primary text-sm line-clamp-2 mb-2">
                          {doc.name}
                        </p>
                        <p className="text-xs text-text-muted mb-3">{formatFileSize(doc.size)}</p>
                        <div className="flex items-center gap-2 text-xs text-text-muted">
                          <Clock className="w-3 h-3" />
                          <span>{new Date(doc.lastModified).toLocaleDateString('pt-BR')}</span>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                );
              })}
            </div>
          )}
        </motion.div>

        {/* Upload Modal */}
        <Modal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          title="Upload de Documento"
          description="Envie novos arquivos para o sistema"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsUploadModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsUploadModalOpen(false)}>
                Enviar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-xl p-8 text-center">
              <Upload className="w-12 h-12 text-text-muted mx-auto mb-4" />
              <p className="text-text-primary font-medium mb-2">
                Arraste arquivos aqui ou clique para selecionar
              </p>
              <p className="text-sm text-text-muted">
                PDF, DOC, XLS, IMG até 50MB
              </p>
              <Button variant="outline" className="mt-4">
                Selecionar Arquivos
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Pasta"
                options={folders.map((f) => ({ value: f.name, label: f.name }))}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Input label="Tags" placeholder="Separadas por vírgula" />
            </div>
          </div>
        </Modal>

        {/* Document Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={selectedDocument?.name || 'Detalhes do Documento'}
          size="lg"
        >
          {selectedDocument && (
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-xl bg-accent-primary/20 flex items-center justify-center">
                  {selectedDocument.type === 'pdf' && <FileText className="w-8 h-8 text-danger" />}
                  {selectedDocument.type === 'doc' && <FileText className="w-8 h-8 text-info" />}
                  {selectedDocument.type === 'xls' && <FileSpreadsheet className="w-8 h-8 text-success" />}
                  {selectedDocument.type === 'img' && <Image className="w-8 h-8 text-warning" />}
                  {selectedDocument.type === 'zip' && <FileArchive className="w-8 h-8 text-secondary" />}
                  {selectedDocument.type === 'folder' && <Folder className="w-8 h-8 text-accent-primary" />}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">{selectedDocument.name}</h3>
                  <p className="text-text-secondary">{selectedDocument.folder}</p>
                  <div className="flex gap-2 mt-2">
                    {selectedDocument.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" size="sm">{tag}</Badge>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Tamanho</p>
                  <p className="font-semibold">{(selectedDocument.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Categoria</p>
                  <p className="font-semibold">{selectedDocument.category}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Enviado por</p>
                  <p className="font-semibold">{selectedDocument.uploadedBy}</p>
                </div>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <p className="text-sm text-text-muted mb-1">Data de Upload</p>
                  <p className="font-semibold">{new Date(selectedDocument.uploadedAt).toLocaleDateString('pt-BR')}</p>
                </div>
              </div>

              <div className="p-4 bg-bg-tertiary rounded-lg">
                <p className="text-sm text-text-muted mb-1">Última Modificação</p>
                <p className="font-semibold">{new Date(selectedDocument.lastModified).toLocaleDateString('pt-BR')}</p>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
                <Badge variant={selectedDocument.shared ? 'success' : 'secondary'}>
                  {selectedDocument.shared ? 'Compartilhado' : 'Privado'}
                </Badge>
                <div className="flex gap-3">
                  <Button variant="outline" onClick={() => setShowDetailModal(false)}>Fechar</Button>
                  <Button variant="outline" leftIcon={<Share2 className="w-4 h-4" />}>Compartilhar</Button>
                  <Button variant="primary" leftIcon={<Download className="w-4 h-4" />}>Download</Button>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
