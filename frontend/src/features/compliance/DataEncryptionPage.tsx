'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Shield,
  Lock,
  Key,
  Database,
  FileText,
  Server,
  HardDrive,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Settings,
  Eye,
  EyeOff,
  Download,
  Upload,
  Plus,
  MoreHorizontal,
  Activity,
  Zap,
  ShieldCheck,
  KeyRound,
  Fingerprint,
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
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

// Types
interface EncryptionKey {
  id: string;
  name: string;
  algorithm: string;
  keySize: number;
  status: 'active' | 'rotating' | 'expired' | 'revoked';
  createdAt: string;
  expiresAt: string;
  lastUsed: string;
  usage: string;
  rotationPeriod: string;
}

interface EncryptedResource {
  id: string;
  name: string;
  type: 'database' | 'file' | 'api' | 'backup';
  encryptionType: 'AES-256' | 'RSA-2048' | 'RSA-4096' | 'ChaCha20';
  keyId: string;
  status: 'encrypted' | 'decrypting' | 'error';
  lastEncrypted: string;
  size: number;
}

// Mock Data
const encryptionKeys: EncryptionKey[] = [
  {
    id: 'key-1',
    name: 'Master Key - Produção',
    algorithm: 'AES-256-GCM',
    keySize: 256,
    status: 'active',
    createdAt: '2025-01-15',
    expiresAt: '2026-01-15',
    lastUsed: '2026-01-16T10:30:00',
    usage: 'Dados sensíveis',
    rotationPeriod: '90 dias',
  },
  {
    id: 'key-2',
    name: 'Database Encryption Key',
    algorithm: 'AES-256-CBC',
    keySize: 256,
    status: 'active',
    createdAt: '2025-06-01',
    expiresAt: '2026-06-01',
    lastUsed: '2026-01-16T09:45:00',
    usage: 'Banco de dados',
    rotationPeriod: '180 dias',
  },
  {
    id: 'key-3',
    name: 'API Token Key',
    algorithm: 'RSA-2048',
    keySize: 2048,
    status: 'rotating',
    createdAt: '2025-10-01',
    expiresAt: '2026-01-20',
    lastUsed: '2026-01-16T10:00:00',
    usage: 'Tokens de API',
    rotationPeriod: '30 dias',
  },
  {
    id: 'key-4',
    name: 'Backup Encryption Key',
    algorithm: 'AES-256-GCM',
    keySize: 256,
    status: 'active',
    createdAt: '2025-08-15',
    expiresAt: '2026-08-15',
    lastUsed: '2026-01-15T23:00:00',
    usage: 'Backups',
    rotationPeriod: '365 dias',
  },
  {
    id: 'key-5',
    name: 'Legacy Key - Deprecated',
    algorithm: 'AES-128-CBC',
    keySize: 128,
    status: 'expired',
    createdAt: '2024-01-01',
    expiresAt: '2025-01-01',
    lastUsed: '2025-01-01T00:00:00',
    usage: 'Dados legados',
    rotationPeriod: '-',
  },
];

const encryptedResources: EncryptedResource[] = [
  { id: 'r1', name: 'PostgreSQL - Produção', type: 'database', encryptionType: 'AES-256', keyId: 'key-2', status: 'encrypted', lastEncrypted: '2026-01-16', size: 45000000000 },
  { id: 'r2', name: 'Documentos GED', type: 'file', encryptionType: 'AES-256', keyId: 'key-1', status: 'encrypted', lastEncrypted: '2026-01-16', size: 125000000000 },
  { id: 'r3', name: 'API Gateway', type: 'api', encryptionType: 'RSA-2048', keyId: 'key-3', status: 'encrypted', lastEncrypted: '2026-01-16', size: 0 },
  { id: 'r4', name: 'Backup Diário', type: 'backup', encryptionType: 'AES-256', keyId: 'key-4', status: 'encrypted', lastEncrypted: '2026-01-16', size: 78000000000 },
];

const encryptionDistribution = [
  { name: 'AES-256', value: 65, color: '#10B981' },
  { name: 'RSA-2048', value: 20, color: '#3B82F6' },
  { name: 'RSA-4096', value: 10, color: '#8B5CF6' },
  { name: 'Outros', value: 5, color: '#6B7280' },
];

const encryptionActivity = [
  { day: 'Seg', operations: 12450 },
  { day: 'Ter', operations: 14230 },
  { day: 'Qua', operations: 13890 },
  { day: 'Qui', operations: 15670 },
  { day: 'Sex', operations: 11234 },
  { day: 'Sáb', operations: 4560 },
  { day: 'Dom', operations: 3210 },
];

const tabs = [
  { id: 'overview', label: 'Visão Geral' },
  { id: 'keys', label: 'Chaves' },
  { id: 'resources', label: 'Recursos' },
  { id: 'audit', label: 'Auditoria' },
];

const statusColors = {
  active: 'success',
  rotating: 'warning',
  expired: 'secondary',
  revoked: 'danger',
} as const;

const statusLabels = {
  active: 'Ativa',
  rotating: 'Rotacionando',
  expired: 'Expirada',
  revoked: 'Revogada',
};

const resourceTypeIcons = {
  database: Database,
  file: FileText,
  api: Zap,
  backup: HardDrive,
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '-';
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(0)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const keyColumns: Column<EncryptionKey>[] = [
  {
    key: 'name',
    header: 'Nome da Chave',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <Key className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted font-mono">{row.id}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'algorithm',
    header: 'Algoritmo',
    render: (row) => (
      <div>
        <p className="font-medium">{row.algorithm}</p>
        <p className="text-xs text-text-muted">{row.keySize} bits</p>
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
    key: 'usage',
    header: 'Uso',
    render: (row) => <span className="text-sm text-text-secondary">{row.usage}</span>,
  },
  {
    key: 'expiresAt',
    header: 'Expira em',
    render: (row) => {
      const expires = new Date(row.expiresAt);
      const isExpiring = expires < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
      return (
        <span className={`text-sm ${isExpiring ? 'text-warning' : 'text-text-secondary'}`}>
          {expires.toLocaleDateString('pt-BR')}
        </span>
      );
    },
  },
  {
    key: 'rotationPeriod',
    header: 'Rotação',
    render: (row) => <span className="text-sm text-text-muted">{row.rotationPeriod}</span>,
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Rotacionar">
          <RefreshCw className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm" title="Detalhes">
          <Eye className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#6B7280'];

export function DataEncryptionPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateKeyModalOpen, setIsCreateKeyModalOpen] = useState(false);

  const filteredKeys = encryptionKeys.filter((key) =>
    key.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Stats
  const totalKeys = encryptionKeys.length;
  const activeKeys = encryptionKeys.filter(k => k.status === 'active').length;
  const rotatingKeys = encryptionKeys.filter(k => k.status === 'rotating').length;
  const encryptedData = encryptedResources.reduce((acc, r) => acc + r.size, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Criptografia de Dados
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie chaves de criptografia e proteção de dados
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsCreateKeyModalOpen(true)}
            >
              Nova Chave
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
              title="Chaves de Criptografia"
              value={totalKeys}
              icon={<Key className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Chaves Ativas"
              value={activeKeys}
              icon={<ShieldCheck className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Em Rotação"
              value={rotatingKeys}
              icon={<RefreshCw className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Dados Criptografados"
              value={formatFileSize(encryptedData)}
              icon={<Lock className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Security Status */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-success">
            <CardBody className="py-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/10">
                  <CheckCircle2 className="w-5 h-5 text-success" />
                </div>
                <div>
                  <p className="font-medium text-text-primary">Criptografia em Repouso</p>
                  <p className="text-sm text-text-muted">AES-256-GCM ativo</p>
                </div>
              </div>
            </CardBody>
          </Card>
          <Card className="border-l-4 border-l-success">
            <CardBody className="py-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/10">
                  <CheckCircle2 className="w-5 h-5 text-success" />
                </div>
                <div>
                  <p className="font-medium text-text-primary">Criptografia em Trânsito</p>
                  <p className="text-sm text-text-muted">TLS 1.3 ativo</p>
                </div>
              </div>
            </CardBody>
          </Card>
          <Card className="border-l-4 border-l-warning">
            <CardBody className="py-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-warning/10">
                  <AlertTriangle className="w-5 h-5 text-warning" />
                </div>
                <div>
                  <p className="font-medium text-text-primary">Rotação de Chave</p>
                  <p className="text-sm text-text-muted">1 chave expirando em 4 dias</p>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {activeTab === 'overview' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold">Distribuição de Algoritmos</h3>
                </div>
              </CardHeader>
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={encryptionDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {encryptionDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex justify-center gap-4 mt-4">
                  {encryptionDistribution.map((item) => (
                    <div key={item.name} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm text-text-muted">{item.name}</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-success" />
                  <h3 className="font-semibold">Operações de Criptografia</h3>
                </div>
              </CardHeader>
              <CardBody>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={encryptionActivity}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                      <XAxis dataKey="day" stroke="var(--color-text-muted)" />
                      <YAxis stroke="var(--color-text-muted)" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'var(--color-bg-secondary)',
                          border: '1px solid var(--color-border)',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="operations" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {activeTab === 'keys' && (
          <>
            <div className="flex items-center justify-end">
              <Input
                placeholder="Buscar chaves..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable
                  columns={keyColumns}
                  data={filteredKeys}
                  keyExtractor={(row) => row.id}
                />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'resources' && (
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Recursos Criptografados</h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-2 gap-4">
                {encryptedResources.map((resource) => {
                  const Icon = resourceTypeIcons[resource.type];
                  return (
                    <div
                      key={resource.id}
                      className="p-4 rounded-lg border border-border hover:border-primary/50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-lg bg-primary/10">
                            <Icon className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium text-text-primary">{resource.name}</p>
                            <p className="text-sm text-text-muted capitalize">{resource.type}</p>
                          </div>
                        </div>
                        <Badge variant="success">Criptografado</Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-text-muted">Algoritmo</p>
                          <p className="font-medium">{resource.encryptionType}</p>
                        </div>
                        <div>
                          <p className="text-text-muted">Tamanho</p>
                          <p className="font-medium">{formatFileSize(resource.size)}</p>
                        </div>
                        <div>
                          <p className="text-text-muted">Última Atualização</p>
                          <p className="font-medium">{new Date(resource.lastEncrypted).toLocaleDateString('pt-BR')}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'audit' && (
          <Card>
            <CardBody className="p-8 text-center">
              <Activity className="w-12 h-12 mx-auto mb-4 text-text-muted" />
              <h3 className="font-medium text-text-primary mb-2">Log de Auditoria de Criptografia</h3>
              <p className="text-text-muted mb-4">
                Visualize todas as operações de criptografia realizadas
              </p>
              <Button variant="primary">Ver Logs de Auditoria</Button>
            </CardBody>
          </Card>
        )}

        {/* Create Key Modal */}
        <Modal
          isOpen={isCreateKeyModalOpen}
          onClose={() => setIsCreateKeyModalOpen(false)}
          title="Nova Chave de Criptografia"
          description="Crie uma nova chave para proteção de dados"
          size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateKeyModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Key className="w-4 h-4" />}>
                Criar Chave
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Nome da Chave"
              placeholder="Ex: Chave de Produção"
              required
            />

            <Select
              label="Algoritmo"
              options={[
                { value: 'AES-256-GCM', label: 'AES-256-GCM (Recomendado)' },
                { value: 'AES-256-CBC', label: 'AES-256-CBC' },
                { value: 'RSA-2048', label: 'RSA-2048' },
                { value: 'RSA-4096', label: 'RSA-4096' },
              ]}
              value="AES-256-GCM"
              onChange={() => {}}
            />

            <Select
              label="Uso"
              options={[
                { value: 'general', label: 'Uso Geral' },
                { value: 'database', label: 'Banco de Dados' },
                { value: 'files', label: 'Arquivos' },
                { value: 'api', label: 'Tokens de API' },
                { value: 'backup', label: 'Backups' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o uso..."
            />

            <Select
              label="Período de Rotação"
              options={[
                { value: '30', label: '30 dias' },
                { value: '90', label: '90 dias' },
                { value: '180', label: '180 dias' },
                { value: '365', label: '365 dias' },
              ]}
              value="90"
              onChange={() => {}}
            />

            <div className="p-3 rounded-lg bg-info/10 border border-info/20">
              <div className="flex items-center gap-2 mb-1">
                <Shield className="w-4 h-4 text-info" />
                <span className="text-sm font-medium text-info">Segurança</span>
              </div>
              <p className="text-sm text-text-secondary">
                A chave será armazenada de forma segura usando HSM (Hardware Security Module)
                e rotacionada automaticamente conforme o período definido.
              </p>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
