'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  FileText,
  Share2,
  Users,
  Link,
  Mail,
  Copy,
  Eye,
  Download,
  Clock,
  Lock,
  Unlock,
  Globe,
  Building,
  User,
  Plus,
  MoreHorizontal,
  ExternalLink,
  Settings,
  Shield,
  Calendar,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Trash2,
  Edit2,
  RefreshCw,
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
interface SharedDocument {
  id: string;
  documentName: string;
  documentType: string;
  sharedBy: string;
  sharedAt: string;
  expiresAt: string | null;
  shareType: 'link' | 'email' | 'team' | 'public';
  permissions: 'view' | 'download' | 'edit';
  accessCount: number;
  recipients: Recipient[];
  status: 'active' | 'expired' | 'revoked';
  password: boolean;
}

interface Recipient {
  id: string;
  name: string;
  email: string;
  type: 'user' | 'team' | 'external';
  accessedAt?: string;
}

// Mock Data
const sharedDocuments: SharedDocument[] = [
  {
    id: '1',
    documentName: 'Relatório Financeiro Q4 2025',
    documentType: 'Relatório',
    sharedBy: 'Ana Costa',
    sharedAt: '2026-01-15T10:00:00',
    expiresAt: '2026-02-15',
    shareType: 'team',
    permissions: 'view',
    accessCount: 45,
    status: 'active',
    password: false,
    recipients: [
      { id: 'r1', name: 'Equipe Financeira', email: 'financeiro@empresa.com', type: 'team', accessedAt: '2026-01-15T14:30:00' },
      { id: 'r2', name: 'Diretoria', email: 'diretoria@empresa.com', type: 'team', accessedAt: '2026-01-15T11:00:00' },
    ],
  },
  {
    id: '2',
    documentName: 'Proposta Comercial - Cliente ABC',
    documentType: 'Proposta',
    sharedBy: 'Carlos Lima',
    sharedAt: '2026-01-14T09:00:00',
    expiresAt: '2026-01-21',
    shareType: 'link',
    permissions: 'download',
    accessCount: 12,
    status: 'active',
    password: true,
    recipients: [
      { id: 'r3', name: 'João Silva', email: 'joao@clienteabc.com', type: 'external', accessedAt: '2026-01-14T15:00:00' },
    ],
  },
  {
    id: '3',
    documentName: 'Manual de Procedimentos',
    documentType: 'Manual',
    sharedBy: 'Roberto Silva',
    sharedAt: '2026-01-10T14:00:00',
    expiresAt: null,
    shareType: 'public',
    permissions: 'view',
    accessCount: 234,
    status: 'active',
    password: false,
    recipients: [],
  },
  {
    id: '4',
    documentName: 'Contrato Antigo - Versão 2024',
    documentType: 'Contrato',
    sharedBy: 'Maria Oliveira',
    sharedAt: '2025-12-01T10:00:00',
    expiresAt: '2026-01-01',
    shareType: 'email',
    permissions: 'download',
    accessCount: 8,
    status: 'expired',
    password: false,
    recipients: [
      { id: 'r4', name: 'Cliente XYZ', email: 'contato@xyz.com', type: 'external' },
    ],
  },
  {
    id: '5',
    documentName: 'Dados Sensíveis - Projeto Beta',
    documentType: 'Confidencial',
    sharedBy: 'Pedro Santos',
    sharedAt: '2026-01-08T11:00:00',
    expiresAt: '2026-01-15',
    shareType: 'email',
    permissions: 'view',
    accessCount: 3,
    status: 'revoked',
    password: true,
    recipients: [
      { id: 'r5', name: 'Consultor Externo', email: 'consultor@email.com', type: 'external' },
    ],
  },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'active', label: 'Ativos' },
  { id: 'expired', label: 'Expirados' },
  { id: 'revoked', label: 'Revogados' },
];

const shareTypeIcons = {
  link: Link,
  email: Mail,
  team: Users,
  public: Globe,
};

const shareTypeLabels = {
  link: 'Link',
  email: 'E-mail',
  team: 'Equipe',
  public: 'Público',
};

const permissionLabels = {
  view: 'Visualizar',
  download: 'Download',
  edit: 'Editar',
};

const permissionColors = {
  view: 'info',
  download: 'warning',
  edit: 'danger',
} as const;

const statusColors = {
  active: 'success',
  expired: 'secondary',
  revoked: 'danger',
} as const;

const statusLabels = {
  active: 'Ativo',
  expired: 'Expirado',
  revoked: 'Revogado',
};

const columns: Column<SharedDocument>[] = [
  {
    key: 'documentName',
    header: 'Documento',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <FileText className="w-5 h-5 text-primary" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <p className="font-medium text-text-primary">{row.documentName}</p>
            {row.password && <Lock className="w-3 h-3 text-warning" />}
          </div>
          <p className="text-xs text-text-muted">{row.documentType}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'shareType',
    header: 'Tipo',
    render: (row) => {
      const Icon = shareTypeIcons[row.shareType];
      return (
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-text-muted" />
          <span>{shareTypeLabels[row.shareType]}</span>
        </div>
      );
    },
  },
  {
    key: 'permissions',
    header: 'Permissão',
    render: (row) => (
      <Badge variant={permissionColors[row.permissions]} size="sm">
        {permissionLabels[row.permissions]}
      </Badge>
    ),
  },
  {
    key: 'recipients',
    header: 'Destinatários',
    render: (row) => {
      if (row.shareType === 'public') {
        return <span className="text-sm text-text-muted">Público</span>;
      }
      return (
        <div className="flex items-center gap-2">
          {row.recipients.length > 0 ? (
            <>
              <div className="flex -space-x-2">
                {row.recipients.slice(0, 3).map((r) => (
                  <Avatar key={r.id} name={r.name} size="xs" className="ring-2 ring-bg-primary" />
                ))}
              </div>
              {row.recipients.length > 3 && (
                <span className="text-xs text-text-muted">+{row.recipients.length - 3}</span>
              )}
            </>
          ) : (
            <span className="text-sm text-text-muted">-</span>
          )}
        </div>
      );
    },
  },
  {
    key: 'accessCount',
    header: 'Acessos',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Eye className="w-4 h-4 text-text-muted" />
        <span className="font-medium">{row.accessCount}</span>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => (
      <Badge variant={statusColors[row.status]}>
        {statusLabels[row.status]}
      </Badge>
    ),
  },
  {
    key: 'expiresAt',
    header: 'Expira em',
    render: (row) => {
      if (!row.expiresAt) return <span className="text-sm text-text-muted">Sem prazo</span>;
      const expires = new Date(row.expiresAt);
      const isExpired = expires < new Date();
      return (
        <span className={`text-sm ${isExpired ? 'text-danger' : 'text-text-secondary'}`}>
          {expires.toLocaleDateString('pt-BR')}
        </span>
      );
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Copiar Link">
          <Copy className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit2 className="w-4 h-4" />
        </Button>
        {row.status === 'active' && (
          <Button variant="ghost" size="icon-sm" title="Revogar">
            <XCircle className="w-4 h-4" />
          </Button>
        )}
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

export function DocumentSharePage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [selectedShare, setSelectedShare] = useState<SharedDocument | null>(null);

  const filteredShares = sharedDocuments.filter((share) => {
    const matchesSearch = share.documentName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === 'all' || share.status === activeTab;
    return matchesSearch && matchesTab;
  });

  // Stats
  const totalShares = sharedDocuments.length;
  const activeShares = sharedDocuments.filter(s => s.status === 'active').length;
  const totalAccess = sharedDocuments.reduce((acc, s) => acc + s.accessCount, 0);
  const protectedShares = sharedDocuments.filter(s => s.password).length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Compartilhamento de Documentos
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie links e permissões de compartilhamento
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button
              variant="primary"
              leftIcon={<Share2 className="w-4 h-4" />}
              onClick={() => setIsShareModalOpen(true)}
            >
              Compartilhar
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
              title="Total Compartilhados"
              value={totalShares}
              icon={<Share2 className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Links Ativos"
              value={activeShares}
              icon={<Link className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Total de Acessos"
              value={totalAccess}
              icon={<Eye className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Protegidos por Senha"
              value={protectedShares}
              icon={<Lock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Share Types Overview */}
        <div className="grid grid-cols-4 gap-4">
          {Object.entries(shareTypeIcons).map(([type, Icon]) => {
            const count = sharedDocuments.filter(s => s.shareType === type && s.status === 'active').length;
            return (
              <Card key={type} className="hover:border-primary/50 transition-colors cursor-pointer">
                <CardBody className="py-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{shareTypeLabels[type as keyof typeof shareTypeLabels]}</p>
                      <p className="text-sm text-text-muted">{count} ativos</p>
                    </div>
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
          <div className="flex items-center gap-3">
            <Input
              placeholder="Buscar compartilhamentos..."
              leftIcon={<Search className="w-4 h-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
          </div>
        </div>

        {/* Shares Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredShares}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedShare(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Share Modal */}
        <Modal
          isOpen={isShareModalOpen}
          onClose={() => setIsShareModalOpen(false)}
          title="Compartilhar Documento"
          description="Configure as opções de compartilhamento"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsShareModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Share2 className="w-4 h-4" />}>
                Compartilhar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Documento"
              options={sharedDocuments.map(d => ({ value: d.id, label: d.documentName }))}
              value=""
              onChange={() => {}}
              placeholder="Selecione o documento..."
            />

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Tipo de Compartilhamento</label>
              <div className="grid grid-cols-4 gap-3">
                {Object.entries(shareTypeIcons).map(([type, Icon]) => (
                  <button
                    key={type}
                    className="p-3 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors text-center"
                  >
                    <Icon className="w-5 h-5 mx-auto mb-2 text-text-muted" />
                    <span className="text-sm font-medium">{shareTypeLabels[type as keyof typeof shareTypeLabels]}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium text-text-primary">Destinatários</label>
              <Input
                placeholder="Digite email ou nome..."
                leftIcon={<User className="w-4 h-4" />}
              />
              <div className="flex flex-wrap gap-2">
                <Badge variant="primary" className="flex items-center gap-1">
                  Ana Costa
                  <button className="ml-1 hover:text-danger">×</button>
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Permissão"
                options={[
                  { value: 'view', label: 'Apenas Visualizar' },
                  { value: 'download', label: 'Visualizar e Download' },
                  { value: 'edit', label: 'Editar' },
                ]}
                value="view"
                onChange={() => {}}
              />
              <Input
                label="Data de Expiração"
                type="date"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-text-muted" />
                <span className="text-sm">Proteger com senha</span>
              </div>
              <input type="checkbox" className="toggle" />
            </div>

            <Textarea
              label="Mensagem (opcional)"
              placeholder="Adicione uma mensagem para os destinatários..."
              rows={2}
            />

            <div className="p-3 rounded-lg bg-info/10 border border-info/20">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-info" />
                <span className="text-sm font-medium text-info">Segurança</span>
              </div>
              <p className="text-sm text-text-secondary">
                Os acessos serão registrados para auditoria. Você poderá revogar o compartilhamento a qualquer momento.
              </p>
            </div>
          </div>
        </Modal>

        {/* Share Details Modal */}
        <Modal
          isOpen={!!selectedShare}
          onClose={() => setSelectedShare(null)}
          title="Detalhes do Compartilhamento"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedShare(null)}>
                Fechar
              </Button>
              {selectedShare?.status === 'active' && (
                <>
                  <Button variant="outline" leftIcon={<Copy className="w-4 h-4" />}>
                    Copiar Link
                  </Button>
                  <Button variant="danger" leftIcon={<XCircle className="w-4 h-4" />}>
                    Revogar
                  </Button>
                </>
              )}
            </>
          }
        >
          {selectedShare && (
            <div className="space-y-6">
              {/* Document Info */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                <div className="p-3 rounded-lg bg-primary/10">
                  <FileText className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-text-primary">{selectedShare.documentName}</h4>
                  <div className="flex items-center gap-3 mt-2">
                    <Badge variant={statusColors[selectedShare.status]}>
                      {statusLabels[selectedShare.status]}
                    </Badge>
                    <Badge variant={permissionColors[selectedShare.permissions]} size="sm">
                      {permissionLabels[selectedShare.permissions]}
                    </Badge>
                    {selectedShare.password && (
                      <div className="flex items-center gap-1 text-warning">
                        <Lock className="w-3 h-3" />
                        <span className="text-xs">Protegido</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Link */}
              {selectedShare.shareType === 'link' && (
                <div className="flex items-center gap-2">
                  <Input
                    value={`https://app.conectaplus.com.br/share/${selectedShare.id}`}
                    readOnly
                    className="flex-1 font-mono text-sm"
                  />
                  <Button variant="secondary" leftIcon={<Copy className="w-4 h-4" />}>
                    Copiar
                  </Button>
                </div>
              )}

              {/* Recipients */}
              {selectedShare.recipients.length > 0 && (
                <div>
                  <h5 className="font-medium text-text-primary mb-3">Destinatários</h5>
                  <div className="space-y-2">
                    {selectedShare.recipients.map((recipient) => (
                      <div
                        key={recipient.id}
                        className="flex items-center gap-3 p-3 rounded-lg border border-border"
                      >
                        <Avatar name={recipient.name} size="sm" />
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{recipient.name}</p>
                          <p className="text-sm text-text-muted">{recipient.email}</p>
                        </div>
                        <div className="text-right">
                          <Badge variant={recipient.type === 'external' ? 'warning' : 'info'} size="sm">
                            {recipient.type === 'external' ? 'Externo' : recipient.type === 'team' ? 'Equipe' : 'Usuário'}
                          </Badge>
                          {recipient.accessedAt && (
                            <p className="text-xs text-text-muted mt-1">
                              Acessou: {new Date(recipient.accessedAt).toLocaleString('pt-BR')}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 rounded-lg bg-bg-secondary text-center">
                  <Eye className="w-5 h-5 mx-auto mb-2 text-info" />
                  <p className="text-2xl font-bold">{selectedShare.accessCount}</p>
                  <p className="text-sm text-text-muted">Acessos</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary text-center">
                  <Calendar className="w-5 h-5 mx-auto mb-2 text-primary" />
                  <p className="text-sm font-medium">{new Date(selectedShare.sharedAt).toLocaleDateString('pt-BR')}</p>
                  <p className="text-sm text-text-muted">Criado em</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary text-center">
                  <Clock className="w-5 h-5 mx-auto mb-2 text-warning" />
                  <p className="text-sm font-medium">
                    {selectedShare.expiresAt ? new Date(selectedShare.expiresAt).toLocaleDateString('pt-BR') : 'Sem prazo'}
                  </p>
                  <p className="text-sm text-text-muted">Expira em</p>
                </div>
              </div>

              {/* Shared By */}
              <div className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                <Avatar name={selectedShare.sharedBy} size="sm" />
                <div>
                  <p className="text-sm text-text-muted">Compartilhado por</p>
                  <p className="font-medium">{selectedShare.sharedBy}</p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
