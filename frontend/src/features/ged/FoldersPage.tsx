'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Plus,
  Folder,
  FolderOpen,
  FolderPlus,
  MoreHorizontal,
  Edit2,
  Trash2,
  Move,
  Lock,
  Users,
  FileText,
  ChevronRight,
  ChevronDown,
  Settings,
  Shield,
  Eye,
  Star,
  StarOff,
  Archive,
  Download,
  Upload,
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
  Textarea,
} from '@/design-system/components';

// Types
interface FolderItem {
  id: string;
  name: string;
  path: string;
  parentId: string | null;
  documentCount: number;
  size: number;
  owner: string;
  createdAt: string;
  modifiedAt: string;
  permissions: 'public' | 'private' | 'restricted';
  starred: boolean;
  children?: FolderItem[];
}

// Mock Data
const folderData: FolderItem[] = [
  {
    id: '1',
    name: 'Contratos',
    path: '/Contratos',
    parentId: null,
    documentCount: 145,
    size: 524288000,
    owner: 'Ana Costa',
    createdAt: '2024-01-15',
    modifiedAt: '2026-01-15',
    permissions: 'restricted',
    starred: true,
    children: [
      {
        id: '1.1',
        name: '2024',
        path: '/Contratos/2024',
        parentId: '1',
        documentCount: 78,
        size: 289000000,
        owner: 'Ana Costa',
        createdAt: '2024-01-15',
        modifiedAt: '2024-12-31',
        permissions: 'restricted',
        starred: false,
      },
      {
        id: '1.2',
        name: '2025',
        path: '/Contratos/2025',
        parentId: '1',
        documentCount: 52,
        size: 198000000,
        owner: 'Ana Costa',
        createdAt: '2025-01-02',
        modifiedAt: '2025-12-28',
        permissions: 'restricted',
        starred: false,
      },
      {
        id: '1.3',
        name: '2026',
        path: '/Contratos/2026',
        parentId: '1',
        documentCount: 15,
        size: 37288000,
        owner: 'Ana Costa',
        createdAt: '2026-01-02',
        modifiedAt: '2026-01-15',
        permissions: 'restricted',
        starred: true,
      },
    ],
  },
  {
    id: '2',
    name: 'Financeiro',
    path: '/Financeiro',
    parentId: null,
    documentCount: 328,
    size: 892000000,
    owner: 'Carlos Lima',
    createdAt: '2024-02-01',
    modifiedAt: '2026-01-14',
    permissions: 'private',
    starred: true,
  },
  {
    id: '3',
    name: 'Propostas',
    path: '/Propostas',
    parentId: null,
    documentCount: 89,
    size: 156000000,
    owner: 'Roberto Silva',
    createdAt: '2024-03-15',
    modifiedAt: '2026-01-13',
    permissions: 'restricted',
    starred: false,
  },
  {
    id: '4',
    name: 'RH',
    path: '/RH',
    parentId: null,
    documentCount: 456,
    size: 1240000000,
    owner: 'Maria Oliveira',
    createdAt: '2024-01-10',
    modifiedAt: '2026-01-12',
    permissions: 'private',
    starred: false,
  },
  {
    id: '5',
    name: 'Operacional',
    path: '/Operacional',
    parentId: null,
    documentCount: 234,
    size: 678000000,
    owner: 'Pedro Santos',
    createdAt: '2024-04-01',
    modifiedAt: '2026-01-10',
    permissions: 'public',
    starred: false,
  },
  {
    id: '6',
    name: 'Marketing',
    path: '/Marketing',
    parentId: null,
    documentCount: 112,
    size: 345000000,
    owner: 'Julia Ferreira',
    createdAt: '2024-05-15',
    modifiedAt: '2026-01-08',
    permissions: 'public',
    starred: false,
  },
];

const recentFolders = folderData.slice(0, 4);
const starredFolders = folderData.filter(f => f.starred);

const tabs = [
  { id: 'all', label: 'Todas as Pastas' },
  { id: 'starred', label: 'Favoritas' },
  { id: 'recent', label: 'Recentes' },
  { id: 'shared', label: 'Compartilhadas' },
];

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const permissionColors = {
  public: 'success',
  private: 'danger',
  restricted: 'warning',
} as const;

const permissionLabels = {
  public: 'Público',
  private: 'Privado',
  restricted: 'Restrito',
};

const columns: Column<FolderItem>[] = [
  {
    key: 'name',
    header: 'Nome da Pasta',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-warning/10">
          <FolderOpen className="w-5 h-5 text-warning" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <p className="font-medium text-text-primary">{row.name}</p>
            {row.starred && <Star className="w-4 h-4 text-warning fill-warning" />}
          </div>
          <p className="text-xs text-text-muted">{row.path}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'documentCount',
    header: 'Documentos',
    render: (row) => (
      <div className="flex items-center gap-2">
        <FileText className="w-4 h-4 text-text-muted" />
        <span className="font-medium">{row.documentCount}</span>
      </div>
    ),
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
    key: 'owner',
    header: 'Proprietário',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Avatar name={row.owner} size="xs" />
        <span className="text-sm">{row.owner}</span>
      </div>
    ),
  },
  {
    key: 'permissions',
    header: 'Permissões',
    render: (row) => (
      <Badge variant={permissionColors[row.permissions]}>
        {permissionLabels[row.permissions]}
      </Badge>
    ),
  },
  {
    key: 'modifiedAt',
    header: 'Modificado',
    render: (row) => (
      <span className="text-sm text-text-secondary">
        {new Date(row.modifiedAt).toLocaleDateString('pt-BR')}
      </span>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: () => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Abrir">
          <FolderOpen className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Compartilhar">
          <Users className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function FoldersPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState<string[]>(['1']);
  const [newParentFolder, setNewParentFolder] = useState('');
  const [newPermission, setNewPermission] = useState('restricted');

  const toggleFolder = (folderId: string) => {
    setExpandedFolders(prev =>
      prev.includes(folderId)
        ? prev.filter(id => id !== folderId)
        : [...prev, folderId]
    );
  };

  const filteredFolders = folderData.filter((folder) => {
    const matchesSearch = folder.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      folder.path.toLowerCase().includes(searchTerm.toLowerCase());

    if (activeTab === 'starred') return matchesSearch && folder.starred;
    if (activeTab === 'recent') return matchesSearch && recentFolders.includes(folder);
    if (activeTab === 'shared') return matchesSearch && folder.permissions !== 'private';
    return matchesSearch;
  });

  // Stats
  const totalFolders = folderData.length;
  const totalDocuments = folderData.reduce((acc, f) => acc + f.documentCount, 0);
  const totalSize = folderData.reduce((acc, f) => acc + f.size, 0);
  const sharedFolders = folderData.filter(f => f.permissions !== 'private').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Gerenciamento de Pastas
            </h1>
            <p className="text-text-secondary mt-1">
              Organize e gerencie a estrutura de pastas do sistema
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Upload className="w-4 h-4" />}>
              Importar Estrutura
            </Button>
            <Button
              variant="primary"
              leftIcon={<FolderPlus className="w-4 h-4" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Nova Pasta
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
              title="Total de Pastas"
              value={totalFolders}
              icon={<Folder className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Total de Documentos"
              value={totalDocuments.toLocaleString('pt-BR')}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Espaço Total"
              value={formatFileSize(totalSize)}
              icon={<Archive className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Pastas Compartilhadas"
              value={sharedFolders}
              icon={<Users className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Quick Access - Starred Folders */}
        {starredFolders.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5 text-warning" />
                <h3 className="font-semibold">Pastas Favoritas</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-4 gap-4">
                {starredFolders.map((folder) => (
                  <div
                    key={folder.id}
                    className="p-4 rounded-lg border border-border hover:border-warning/50 hover:bg-warning/5 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 rounded-lg bg-warning/10">
                        <FolderOpen className="w-5 h-5 text-warning" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-text-primary truncate">{folder.name}</p>
                        <p className="text-xs text-text-muted">{folder.documentCount} arquivos</p>
                      </div>
                      <Star className="w-4 h-4 text-warning fill-warning" />
                    </div>
                    <div className="flex items-center justify-between text-xs text-text-muted">
                      <span>{formatFileSize(folder.size)}</span>
                      <Badge variant={permissionColors[folder.permissions]} size="sm">
                        {permissionLabels[folder.permissions]}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
          <div className="flex items-center gap-3">
            <Input
              placeholder="Buscar pastas..."
              leftIcon={<Search className="w-4 h-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
          </div>
        </div>

        {/* Folder Tree View */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Estrutura de Pastas</h3>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" leftIcon={<Download className="w-4 h-4" />}>
                  Exportar
                </Button>
                <Button variant="ghost" size="sm" leftIcon={<Settings className="w-4 h-4" />}>
                  Configurar
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            {/* Tree View */}
            <div className="divide-y divide-border">
              {filteredFolders.map((folder) => (
                <div key={folder.id}>
                  <div
                    className="flex items-center gap-3 px-6 py-4 hover:bg-bg-secondary/50 cursor-pointer"
                    onClick={() => folder.children && toggleFolder(folder.id)}
                  >
                    <div className="flex items-center gap-2 w-8">
                      {folder.children && (
                        expandedFolders.includes(folder.id) ? (
                          <ChevronDown className="w-4 h-4 text-text-muted" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-text-muted" />
                        )
                      )}
                    </div>
                    <div className="p-2 rounded-lg bg-warning/10">
                      <FolderOpen className="w-5 h-5 text-warning" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-text-primary">{folder.name}</p>
                        {folder.starred && <Star className="w-4 h-4 text-warning fill-warning" />}
                      </div>
                      <p className="text-xs text-text-muted">{folder.path}</p>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <p className="text-sm font-medium">{folder.documentCount}</p>
                        <p className="text-xs text-text-muted">docs</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{formatFileSize(folder.size)}</p>
                        <p className="text-xs text-text-muted">tamanho</p>
                      </div>
                      <Badge variant={permissionColors[folder.permissions]}>
                        {permissionLabels[folder.permissions]}
                      </Badge>
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="icon-sm" title="Favoritar">
                          {folder.starred ? (
                            <Star className="w-4 h-4 text-warning fill-warning" />
                          ) : (
                            <StarOff className="w-4 h-4" />
                          )}
                        </Button>
                        <Button variant="ghost" size="icon-sm" title="Editar">
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="icon-sm">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  {/* Children */}
                  {folder.children && expandedFolders.includes(folder.id) && (
                    <div className="bg-bg-secondary/30">
                      {folder.children.map((child) => (
                        <div
                          key={child.id}
                          className="flex items-center gap-3 px-6 py-3 pl-16 hover:bg-bg-secondary/50 cursor-pointer border-l-2 border-warning/30 ml-9"
                        >
                          <div className="p-1.5 rounded-lg bg-warning/10">
                            <Folder className="w-4 h-4 text-warning" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-text-primary text-sm">{child.name}</p>
                          </div>
                          <div className="flex items-center gap-6">
                            <span className="text-sm text-text-muted">{child.documentCount} docs</span>
                            <span className="text-sm text-text-muted">{formatFileSize(child.size)}</span>
                            <div className="flex items-center gap-1">
                              <Button variant="ghost" size="icon-sm">
                                <MoreHorizontal className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Create Folder Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Nova Pasta"
          description="Crie uma nova pasta para organizar seus documentos"
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsCreateModalOpen(false)}>
                Criar Pasta
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Nome da Pasta"
              placeholder="Digite o nome da pasta"
              required
            />
            <Select
              label="Pasta Pai"
              options={[
                { value: '', label: '/ (Raiz)' },
                ...folderData.map(f => ({ value: f.id, label: f.path }))
              ]}
              value={newParentFolder}
              onChange={(value) => setNewParentFolder(value)}
              placeholder="Selecione a pasta pai"
            />
            <Textarea
              label="Descrição"
              placeholder="Descreva o propósito desta pasta"
              rows={3}
            />
            <Select
              label="Permissões"
              options={[
                { value: 'public', label: 'Público - Todos podem visualizar' },
                { value: 'restricted', label: 'Restrito - Apenas usuários autorizados' },
                { value: 'private', label: 'Privado - Apenas o proprietário' },
              ]}
              value={newPermission}
              onChange={(value) => setNewPermission(value)}
            />
            <div className="flex items-center gap-2 p-3 rounded-lg bg-info/10 border border-info/20">
              <Shield className="w-5 h-5 text-info" />
              <p className="text-sm text-text-secondary">
                Pastas herdam permissões da pasta pai por padrão
              </p>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
