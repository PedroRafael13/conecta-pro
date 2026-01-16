'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Settings,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Zap,
  Building2,
  Mail,
  MessageSquare,
  CreditCard,
  FileText,
  Cloud,
  Link2,
  ExternalLink,
  Activity,
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
  SimpleTabBar,
  Modal,
} from '@/design-system/components';

// Types
interface Integration {
  id: string;
  name: string;
  description: string;
  category: 'banking' | 'communication' | 'government' | 'erp' | 'storage';
  icon: string;
  status: 'active' | 'inactive' | 'error' | 'configuring';
  lastSync: string | null;
  syncFrequency: string;
  eventsProcessed: number;
  errorCount: number;
}

// Mock Data
const integrations: Integration[] = [
  {
    id: '1',
    name: 'Open Banking',
    description: 'Conexão com bancos via API Open Finance',
    category: 'banking',
    icon: 'building',
    status: 'active',
    lastSync: '2026-01-15T14:30:00',
    syncFrequency: 'A cada 30 min',
    eventsProcessed: 1250,
    errorCount: 0,
  },
  {
    id: '2',
    name: 'WhatsApp Business',
    description: 'Envio de notificações e atendimento',
    category: 'communication',
    icon: 'message',
    status: 'active',
    lastSync: '2026-01-15T14:45:00',
    syncFrequency: 'Tempo real',
    eventsProcessed: 3420,
    errorCount: 2,
  },
  {
    id: '3',
    name: 'Email SMTP',
    description: 'Disparo de emails transacionais',
    category: 'communication',
    icon: 'mail',
    status: 'active',
    lastSync: '2026-01-15T14:50:00',
    syncFrequency: 'Tempo real',
    eventsProcessed: 890,
    errorCount: 0,
  },
  {
    id: '4',
    name: 'eSocial',
    description: 'Transmissão de eventos trabalhistas',
    category: 'government',
    icon: 'file',
    status: 'active',
    lastSync: '2026-01-15T08:00:00',
    syncFrequency: 'Diário',
    eventsProcessed: 605,
    errorCount: 0,
  },
  {
    id: '5',
    name: 'SPED Fiscal',
    description: 'Geração e transmissão de arquivos SPED',
    category: 'government',
    icon: 'file',
    status: 'error',
    lastSync: '2026-01-14T18:00:00',
    syncFrequency: 'Mensal',
    eventsProcessed: 12,
    errorCount: 1,
  },
  {
    id: '6',
    name: 'NF-e / NFS-e',
    description: 'Emissão de notas fiscais eletrônicas',
    category: 'government',
    icon: 'file',
    status: 'active',
    lastSync: '2026-01-15T14:00:00',
    syncFrequency: 'Tempo real',
    eventsProcessed: 156,
    errorCount: 0,
  },
  {
    id: '7',
    name: 'Google Drive',
    description: 'Backup e armazenamento de documentos',
    category: 'storage',
    icon: 'cloud',
    status: 'active',
    lastSync: '2026-01-15T12:00:00',
    syncFrequency: 'A cada hora',
    eventsProcessed: 2340,
    errorCount: 0,
  },
  {
    id: '8',
    name: 'Pix Automático',
    description: 'Recebimentos via PIX integrado',
    category: 'banking',
    icon: 'credit',
    status: 'configuring',
    lastSync: null,
    syncFrequency: 'Tempo real',
    eventsProcessed: 0,
    errorCount: 0,
  },
];

const categoryConfig = {
  banking: { label: 'Bancário', color: 'primary', icon: Building2 },
  communication: { label: 'Comunicação', color: 'info', icon: MessageSquare },
  government: { label: 'Governo', color: 'warning', icon: FileText },
  erp: { label: 'ERP', color: 'success', icon: Zap },
  storage: { label: 'Armazenamento', color: 'secondary', icon: Cloud },
};

const statusConfig = {
  active: { label: 'Ativo', color: 'success' as const, icon: CheckCircle2 },
  inactive: { label: 'Inativo', color: 'neutral' as const, icon: XCircle },
  error: { label: 'Erro', color: 'danger' as const, icon: AlertTriangle },
  configuring: { label: 'Configurando', color: 'warning' as const, icon: Settings },
};

function IntegrationCard({ integration }: { integration: Integration }) {
  const status = statusConfig[integration.status];
  const category = categoryConfig[integration.category];
  const CategoryIcon = category.icon;
  const StatusIcon = status.icon;

  const getIcon = () => {
    switch (integration.icon) {
      case 'building':
        return Building2;
      case 'message':
        return MessageSquare;
      case 'mail':
        return Mail;
      case 'file':
        return FileText;
      case 'cloud':
        return Cloud;
      case 'credit':
        return CreditCard;
      default:
        return Zap;
    }
  };

  const Icon = getIcon();

  return (
    <Card className="hover:border-accent-primary/50 transition-colors">
      <CardBody>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl bg-${category.color}/10`}>
              <Icon className={`w-6 h-6 text-${category.color}`} />
            </div>
            <div>
              <h3 className="font-medium text-text-primary">{integration.name}</h3>
              <Badge variant={category.color as any} size="sm">
                {category.label}
              </Badge>
            </div>
          </div>
          <Badge variant={status.color} leftIcon={<StatusIcon className="w-3 h-3" />}>
            {status.label}
          </Badge>
        </div>

        <p className="text-sm text-text-secondary mb-4">{integration.description}</p>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-text-muted mb-1">Última Sincronização</p>
            <p className="text-sm text-text-primary">
              {integration.lastSync
                ? new Date(integration.lastSync).toLocaleString('pt-BR')
                : 'Nunca'}
            </p>
          </div>
          <div>
            <p className="text-xs text-text-muted mb-1">Frequência</p>
            <p className="text-sm text-text-primary">{integration.syncFrequency}</p>
          </div>
        </div>

        <div className="flex items-center justify-between mb-4 p-3 bg-bg-tertiary rounded-lg">
          <div className="text-center">
            <p className="text-lg font-mono font-bold text-text-primary">
              {integration.eventsProcessed.toLocaleString()}
            </p>
            <p className="text-xs text-text-muted">Eventos</p>
          </div>
          <div className="text-center">
            <p className={`text-lg font-mono font-bold ${integration.errorCount > 0 ? 'text-danger' : 'text-success'}`}>
              {integration.errorCount}
            </p>
            <p className="text-xs text-text-muted">Erros</p>
          </div>
        </div>

        <div className="flex items-center gap-2 pt-4 border-t border-border-subtle">
          <Button variant="ghost" size="sm" leftIcon={<Settings className="w-4 h-4" />}>
            Configurar
          </Button>
          <Button variant="ghost" size="sm" leftIcon={<RefreshCw className="w-4 h-4" />}>
            Sincronizar
          </Button>
          <Button variant="ghost" size="sm" leftIcon={<Activity className="w-4 h-4" />}>
            Logs
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}

export function IntegrationsHubPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');

  const filteredIntegrations = integrations.filter((integration) => {
    const matchesSearch =
      integration.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      integration.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab =
      selectedTab === 'all' ||
      integration.category === selectedTab ||
      integration.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  // Stats
  const totalIntegrations = integrations.length;
  const activeIntegrations = integrations.filter((i) => i.status === 'active').length;
  const errorIntegrations = integrations.filter((i) => i.status === 'error').length;
  const totalEvents = integrations.reduce((acc, i) => acc + i.eventsProcessed, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Hub de Integrações
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie conexões com sistemas externos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Sincronizar Todas
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
              Nova Integração
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
              title="Total de Integrações"
              value={totalIntegrations}
              icon={<Link2 className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Ativas"
              value={activeIntegrations}
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
              title="Com Erro"
              value={errorIntegrations}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Eventos Processados"
              value={totalEvents.toLocaleString()}
              icon={<Activity className="w-6 h-6" />}
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
                  { value: 'all', label: `Todas (${integrations.length})` },
                  { value: 'banking', label: 'Bancário' },
                  { value: 'communication', label: 'Comunicação' },
                  { value: 'government', label: 'Governo' },
                  { value: 'storage', label: 'Armazenamento' },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <Input
                placeholder="Buscar integrações..."
                leftIcon={<Search className="w-4 h-4" />}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
            </div>
          </CardBody>
        </Card>

        {/* Integrations Grid */}
        <div className="grid grid-cols-3 gap-6">
          {filteredIntegrations.map((integration) => (
            <motion.div
              key={integration.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <IntegrationCard integration={integration} />
            </motion.div>
          ))}
        </div>

        {/* Alert for errors */}
        {errorIntegrations > 0 && (
          <Card className="border-danger/30 bg-danger/5">
            <CardBody>
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-danger/10">
                  <AlertTriangle className="w-6 h-6 text-danger" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-text-primary">
                    {errorIntegrations} integração(ões) com erro
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Verifique as configurações e corrija os problemas
                  </p>
                </div>
                <Button variant="danger" size="sm">
                  Ver Detalhes
                </Button>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
