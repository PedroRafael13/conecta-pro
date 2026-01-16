'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Eye,
  EyeOff,
  Database,
  Shield,
  Settings,
  Play,
  Pause,
  Plus,
  Edit2,
  Trash2,
  MoreHorizontal,
  CheckCircle2,
  AlertTriangle,
  Clock,
  FileText,
  User,
  CreditCard,
  Phone,
  Mail,
  MapPin,
  Hash,
  Calendar,
  RefreshCw,
  Download,
  Copy,
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
interface MaskingRule {
  id: string;
  name: string;
  fieldType: 'cpf' | 'email' | 'phone' | 'address' | 'name' | 'creditcard' | 'custom';
  maskPattern: string;
  description: string;
  status: 'active' | 'inactive' | 'testing';
  appliedTo: string[];
  createdAt: string;
  lastTriggered: string;
  triggerCount: number;
}

interface MaskedField {
  id: string;
  table: string;
  column: string;
  fieldType: string;
  maskingRule: string;
  sampleOriginal: string;
  sampleMasked: string;
  recordsAffected: number;
}

// Mock Data
const maskingRules: MaskingRule[] = [
  {
    id: '1',
    name: 'CPF Masking',
    fieldType: 'cpf',
    maskPattern: '***.***.***-XX',
    description: 'Oculta os primeiros 9 dígitos do CPF',
    status: 'active',
    appliedTo: ['clientes', 'funcionarios', 'fornecedores'],
    createdAt: '2025-06-15',
    lastTriggered: '2026-01-16T10:30:00',
    triggerCount: 15420,
  },
  {
    id: '2',
    name: 'Email Masking',
    fieldType: 'email',
    maskPattern: 'x***@***.com',
    description: 'Oculta parte do email mantendo domínio',
    status: 'active',
    appliedTo: ['clientes', 'leads', 'contatos'],
    createdAt: '2025-06-15',
    lastTriggered: '2026-01-16T10:25:00',
    triggerCount: 23150,
  },
  {
    id: '3',
    name: 'Phone Masking',
    fieldType: 'phone',
    maskPattern: '(**) ****-XXXX',
    description: 'Oculta os primeiros dígitos do telefone',
    status: 'active',
    appliedTo: ['clientes', 'funcionarios'],
    createdAt: '2025-07-01',
    lastTriggered: '2026-01-16T10:20:00',
    triggerCount: 18900,
  },
  {
    id: '4',
    name: 'Credit Card Masking',
    fieldType: 'creditcard',
    maskPattern: '**** **** **** XXXX',
    description: 'Exibe apenas os últimos 4 dígitos',
    status: 'active',
    appliedTo: ['pagamentos', 'cobrancas'],
    createdAt: '2025-06-20',
    lastTriggered: '2026-01-16T09:45:00',
    triggerCount: 8750,
  },
  {
    id: '5',
    name: 'Name Partial Masking',
    fieldType: 'name',
    maskPattern: 'Xx*** Xx***',
    description: 'Oculta parte do nome mantendo iniciais',
    status: 'testing',
    appliedTo: ['relatorios_externos'],
    createdAt: '2026-01-10',
    lastTriggered: '2026-01-15T14:00:00',
    triggerCount: 234,
  },
  {
    id: '6',
    name: 'Address Masking',
    fieldType: 'address',
    maskPattern: 'Rua ***, nº ***',
    description: 'Oculta detalhes do endereço',
    status: 'inactive',
    appliedTo: [],
    createdAt: '2025-08-01',
    lastTriggered: '',
    triggerCount: 0,
  },
];

const maskedFields: MaskedField[] = [
  { id: '1', table: 'clientes', column: 'cpf', fieldType: 'CPF', maskingRule: 'CPF Masking', sampleOriginal: '123.456.789-00', sampleMasked: '***.***.***.00', recordsAffected: 15420 },
  { id: '2', table: 'clientes', column: 'email', fieldType: 'Email', maskingRule: 'Email Masking', sampleOriginal: 'joao@email.com', sampleMasked: 'j***@***.com', recordsAffected: 15420 },
  { id: '3', table: 'clientes', column: 'telefone', fieldType: 'Telefone', maskingRule: 'Phone Masking', sampleOriginal: '(11) 98765-4321', sampleMasked: '(**) ****-4321', recordsAffected: 14890 },
  { id: '4', table: 'funcionarios', column: 'cpf', fieldType: 'CPF', maskingRule: 'CPF Masking', sampleOriginal: '987.654.321-00', sampleMasked: '***.***.***.00', recordsAffected: 245 },
  { id: '5', table: 'pagamentos', column: 'cartao', fieldType: 'Cartão', maskingRule: 'Credit Card Masking', sampleOriginal: '4532 1234 5678 9012', sampleMasked: '**** **** **** 9012', recordsAffected: 8750 },
];

const tabs = [
  { id: 'rules', label: 'Regras de Mascaramento' },
  { id: 'fields', label: 'Campos Mascarados' },
  { id: 'preview', label: 'Pré-visualização' },
  { id: 'logs', label: 'Logs' },
];

const fieldTypeIcons = {
  cpf: Hash,
  email: Mail,
  phone: Phone,
  address: MapPin,
  name: User,
  creditcard: CreditCard,
  custom: Settings,
};

const statusColors = {
  active: 'success',
  inactive: 'secondary',
  testing: 'warning',
} as const;

const statusLabels = {
  active: 'Ativo',
  inactive: 'Inativo',
  testing: 'Teste',
};

const ruleColumns: Column<MaskingRule>[] = [
  {
    key: 'name',
    header: 'Regra',
    render: (row) => {
      const Icon = fieldTypeIcons[row.fieldType];
      return (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-text-primary">{row.name}</p>
            <p className="text-xs text-text-muted">{row.description}</p>
          </div>
        </div>
      );
    },
  },
  {
    key: 'maskPattern',
    header: 'Padrão',
    render: (row) => (
      <code className="px-2 py-1 rounded bg-bg-secondary font-mono text-sm">
        {row.maskPattern}
      </code>
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
    key: 'appliedTo',
    header: 'Aplicado em',
    render: (row) => (
      <div className="flex flex-wrap gap-1">
        {row.appliedTo.slice(0, 2).map((table) => (
          <Badge key={table} variant="neutral" size="sm">{table}</Badge>
        ))}
        {row.appliedTo.length > 2 && (
          <Badge variant="neutral" size="sm">+{row.appliedTo.length - 2}</Badge>
        )}
      </div>
    ),
  },
  {
    key: 'triggerCount',
    header: 'Execuções',
    render: (row) => (
      <span className="font-medium">{row.triggerCount.toLocaleString('pt-BR')}</span>
    ),
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title={row.status === 'active' ? 'Desativar' : 'Ativar'}>
          {row.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </Button>
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon-sm">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    ),
  },
];

const fieldColumns: Column<MaskedField>[] = [
  {
    key: 'table',
    header: 'Tabela/Coluna',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Database className="w-4 h-4 text-text-muted" />
        <div>
          <p className="font-medium text-text-primary">{row.table}</p>
          <p className="text-xs text-text-muted">{row.column}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'fieldType',
    header: 'Tipo',
    render: (row) => <Badge variant="neutral">{row.fieldType}</Badge>,
  },
  {
    key: 'sampleOriginal',
    header: 'Original',
    render: (row) => (
      <div className="flex items-center gap-2">
        <Eye className="w-4 h-4 text-danger" />
        <code className="text-sm text-danger">{row.sampleOriginal}</code>
      </div>
    ),
  },
  {
    key: 'sampleMasked',
    header: 'Mascarado',
    render: (row) => (
      <div className="flex items-center gap-2">
        <EyeOff className="w-4 h-4 text-success" />
        <code className="text-sm text-success">{row.sampleMasked}</code>
      </div>
    ),
  },
  {
    key: 'recordsAffected',
    header: 'Registros',
    render: (row) => (
      <span className="font-medium">{row.recordsAffected.toLocaleString('pt-BR')}</span>
    ),
  },
];

export function DataMaskingPage() {
  const [activeTab, setActiveTab] = useState('rules');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [previewData, setPreviewData] = useState({
    cpf: '',
    email: '',
    phone: '',
  });

  const filteredRules = maskingRules.filter((rule) =>
    rule.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Stats
  const totalRules = maskingRules.length;
  const activeRules = maskingRules.filter(r => r.status === 'active').length;
  const totalExecutions = maskingRules.reduce((acc, r) => acc + r.triggerCount, 0);
  const protectedFields = maskedFields.length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Mascaramento de Dados
            </h1>
            <p className="text-text-secondary mt-1">
              Configure regras para ocultar dados sensíveis
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar Regras
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Nova Regra
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
              title="Regras de Mascaramento"
              value={totalRules}
              icon={<EyeOff className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Regras Ativas"
              value={activeRules}
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
              title="Campos Protegidos"
              value={protectedFields}
              icon={<Shield className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Total de Execuções"
              value={totalExecutions.toLocaleString('pt-BR')}
              icon={<Zap className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* How it Works */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-danger/10 flex items-center justify-center">
                  <Eye className="w-5 h-5 text-danger" />
                </div>
                <div>
                  <p className="text-sm text-text-muted">Dado Original</p>
                  <p className="font-mono font-medium">123.456.789-00</p>
                </div>
              </div>
              <div className="flex-1 border-t-2 border-dashed border-primary/30 relative">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-bg-primary px-3">
                  <RefreshCw className="w-5 h-5 text-primary" />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center">
                  <EyeOff className="w-5 h-5 text-success" />
                </div>
                <div>
                  <p className="text-sm text-text-muted">Dado Mascarado</p>
                  <p className="font-mono font-medium">***.***.***.00</p>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {activeTab === 'rules' && (
          <>
            <div className="flex items-center justify-end">
              <Input
                placeholder="Buscar regras..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
            </div>
            <Card>
              <CardBody className="p-0">
                <DataTable
                  columns={ruleColumns}
                  data={filteredRules}
                  keyExtractor={(row) => row.id}
                />
              </CardBody>
            </Card>
          </>
        )}

        {activeTab === 'fields' && (
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={fieldColumns}
                data={maskedFields}
                keyExtractor={(row) => row.id}
              />
            </CardBody>
          </Card>
        )}

        {activeTab === 'preview' && (
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Teste de Mascaramento</h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <Input
                    label="CPF"
                    placeholder="Digite um CPF"
                    value={previewData.cpf}
                    onChange={(e) => setPreviewData({ ...previewData, cpf: e.target.value })}
                    leftIcon={<Hash className="w-4 h-4" />}
                  />
                  <Input
                    label="E-mail"
                    placeholder="Digite um e-mail"
                    value={previewData.email}
                    onChange={(e) => setPreviewData({ ...previewData, email: e.target.value })}
                    leftIcon={<Mail className="w-4 h-4" />}
                  />
                  <Input
                    label="Telefone"
                    placeholder="Digite um telefone"
                    value={previewData.phone}
                    onChange={(e) => setPreviewData({ ...previewData, phone: e.target.value })}
                    leftIcon={<Phone className="w-4 h-4" />}
                  />
                </div>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-bg-secondary">
                    <p className="text-sm text-text-muted mb-2">CPF Mascarado</p>
                    <p className="font-mono text-lg text-success">
                      {previewData.cpf ? '***.***.***.XX' : '-'}
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-bg-secondary">
                    <p className="text-sm text-text-muted mb-2">E-mail Mascarado</p>
                    <p className="font-mono text-lg text-success">
                      {previewData.email ? 'x***@***.com' : '-'}
                    </p>
                  </div>
                  <div className="p-4 rounded-lg bg-bg-secondary">
                    <p className="text-sm text-text-muted mb-2">Telefone Mascarado</p>
                    <p className="font-mono text-lg text-success">
                      {previewData.phone ? '(**) ****-XXXX' : '-'}
                    </p>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'logs' && (
          <Card>
            <CardBody className="p-8 text-center">
              <Clock className="w-12 h-12 mx-auto mb-4 text-text-muted" />
              <h3 className="font-medium text-text-primary mb-2">Logs de Mascaramento</h3>
              <p className="text-text-muted mb-4">
                Visualize o histórico de operações de mascaramento
              </p>
              <Button variant="primary">Ver Logs Completos</Button>
            </CardBody>
          </Card>
        )}

        {/* Create Rule Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Nova Regra de Mascaramento"
          description="Configure uma nova regra para proteger dados sensíveis"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsCreateModalOpen(false)}>
                Criar Regra
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Nome da Regra"
              placeholder="Ex: CPF Masking"
              required
            />

            <Select
              label="Tipo de Campo"
              options={[
                { value: 'cpf', label: 'CPF' },
                { value: 'email', label: 'E-mail' },
                { value: 'phone', label: 'Telefone' },
                { value: 'creditcard', label: 'Cartão de Crédito' },
                { value: 'name', label: 'Nome' },
                { value: 'address', label: 'Endereço' },
                { value: 'custom', label: 'Personalizado' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />

            <Input
              label="Padrão de Máscara"
              placeholder="Ex: ***.***.***-XX"
              helperText="Use * para ocultar e X para manter caracteres"
            />

            <Textarea
              label="Descrição"
              placeholder="Descreva o propósito desta regra"
              rows={2}
            />

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">Aplicar em</label>
              <div className="grid grid-cols-3 gap-2">
                {['clientes', 'funcionarios', 'fornecedores', 'pagamentos', 'relatorios', 'exportacoes'].map((table) => (
                  <label key={table} className="flex items-center gap-2 p-2 rounded border border-border hover:bg-bg-secondary cursor-pointer">
                    <input type="checkbox" className="rounded" />
                    <span className="text-sm">{table}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-info/10 border border-info/20">
              <div className="flex items-center gap-2 mb-1">
                <Shield className="w-4 h-4 text-info" />
                <span className="text-sm font-medium text-info">Conformidade</span>
              </div>
              <p className="text-sm text-text-secondary">
                Esta regra ajuda a cumprir requisitos de proteção de dados da LGPD e GDPR.
              </p>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
