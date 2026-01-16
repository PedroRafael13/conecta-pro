'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Search,
  RefreshCw,
  Download,
  Upload,
  Calendar,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileText,
  Send,
  Eye,
  Settings,
  Activity,
  Shield,
  Server,
  Wifi,
  WifiOff,
  ChevronRight,
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
  StatCard,
  StatGrid,
  DataTable,
  type Column,
  SimpleTabBar,
  Modal,
  Select,
} from '@/design-system/components';

// Types
interface ESocialEvent {
  id: string;
  code: string;
  name: string;
  category: 'initial' | 'periodic' | 'non_periodic';
  reference: string;
  deadline: string;
  status: 'pending' | 'processing' | 'sent' | 'accepted' | 'rejected' | 'overdue';
  protocol: string | null;
  employees: number;
  errorMessage: string | null;
}

interface GovernmentConnection {
  id: string;
  name: string;
  description: string;
  status: 'connected' | 'disconnected' | 'error';
  lastSync: string | null;
  certificateExpiry: string | null;
}

interface ProcessingLog {
  id: string;
  eventCode: string;
  eventName: string;
  timestamp: string;
  action: 'send' | 'receive' | 'error' | 'retry';
  message: string;
  status: 'success' | 'warning' | 'error';
}

// Mock Data
const esocialEvents: ESocialEvent[] = [
  {
    id: '1',
    code: 'S-1200',
    name: 'Remuneração de Trabalhador',
    category: 'periodic',
    reference: 'Janeiro/2026',
    deadline: '2026-02-07',
    status: 'pending',
    protocol: null,
    employees: 342,
    errorMessage: null,
  },
  {
    id: '2',
    code: 'S-1210',
    name: 'Pagamentos de Rendimentos',
    category: 'periodic',
    reference: 'Janeiro/2026',
    deadline: '2026-02-07',
    status: 'processing',
    protocol: null,
    employees: 342,
    errorMessage: null,
  },
  {
    id: '3',
    code: 'S-1299',
    name: 'Fechamento dos Eventos Periódicos',
    category: 'periodic',
    reference: 'Dezembro/2025',
    deadline: '2026-01-07',
    status: 'accepted',
    protocol: '1.2.202601071234567',
    employees: 340,
    errorMessage: null,
  },
  {
    id: '4',
    code: 'S-2200',
    name: 'Cadastramento Inicial',
    category: 'initial',
    reference: 'Janeiro/2026',
    deadline: '2026-01-15',
    status: 'sent',
    protocol: '1.2.202601151234568',
    employees: 5,
    errorMessage: null,
  },
  {
    id: '5',
    code: 'S-2206',
    name: 'Alteração Contratual',
    category: 'non_periodic',
    reference: 'Janeiro/2026',
    deadline: '2026-01-20',
    status: 'rejected',
    protocol: null,
    employees: 2,
    errorMessage: 'CPF do trabalhador inválido',
  },
];

const connections: GovernmentConnection[] = [
  {
    id: '1',
    name: 'eSocial',
    description: 'Sistema de Escrituração Fiscal Digital das Obrigações Trabalhistas',
    status: 'connected',
    lastSync: '2026-01-15 08:30',
    certificateExpiry: '2026-06-15',
  },
  {
    id: '2',
    name: 'EFD-Reinf',
    description: 'Escrituração Fiscal Digital de Retenções e Informações',
    status: 'connected',
    lastSync: '2026-01-15 08:30',
    certificateExpiry: '2026-06-15',
  },
  {
    id: '3',
    name: 'DCTFWeb',
    description: 'Declaração de Débitos e Créditos Tributários Web',
    status: 'connected',
    lastSync: '2026-01-14 18:00',
    certificateExpiry: '2026-06-15',
  },
  {
    id: '4',
    name: 'SEFIP/GFIP',
    description: 'Sistema Empresa de Recolhimento do FGTS',
    status: 'error',
    lastSync: '2026-01-10 10:00',
    certificateExpiry: '2026-06-15',
  },
  {
    id: '5',
    name: 'CAGED',
    description: 'Cadastro Geral de Empregados e Desempregados',
    status: 'disconnected',
    lastSync: null,
    certificateExpiry: null,
  },
];

const processingLogs: ProcessingLog[] = [
  {
    id: '1',
    eventCode: 'S-1210',
    eventName: 'Pagamentos de Rendimentos',
    timestamp: '2026-01-15 08:35',
    action: 'send',
    message: 'Evento enviado para processamento',
    status: 'success',
  },
  {
    id: '2',
    eventCode: 'S-1200',
    eventName: 'Remuneração de Trabalhador',
    timestamp: '2026-01-15 08:32',
    action: 'send',
    message: 'Iniciando envio do lote',
    status: 'success',
  },
  {
    id: '3',
    eventCode: 'S-2206',
    eventName: 'Alteração Contratual',
    timestamp: '2026-01-14 16:45',
    action: 'error',
    message: 'CPF do trabalhador inválido - Registro 2',
    status: 'error',
  },
  {
    id: '4',
    eventCode: 'S-2206',
    eventName: 'Alteração Contratual',
    timestamp: '2026-01-14 16:40',
    action: 'retry',
    message: 'Tentando reenvio automático (2/3)',
    status: 'warning',
  },
  {
    id: '5',
    eventCode: 'S-1299',
    eventName: 'Fechamento Periódicos',
    timestamp: '2026-01-07 08:00',
    action: 'receive',
    message: 'Protocolo de processamento recebido',
    status: 'success',
  },
];

const categoryLabels = {
  initial: 'Inicial',
  periodic: 'Periódico',
  non_periodic: 'Não Periódico',
};

const statusConfig = {
  pending: { label: 'Pendente', color: 'warning' as const },
  processing: { label: 'Processando', color: 'info' as const },
  sent: { label: 'Enviado', color: 'primary' as const },
  accepted: { label: 'Aceito', color: 'success' as const },
  rejected: { label: 'Rejeitado', color: 'danger' as const },
  overdue: { label: 'Atrasado', color: 'danger' as const },
};

const connectionStatusConfig = {
  connected: { label: 'Conectado', color: 'success' as const, icon: Wifi },
  disconnected: { label: 'Desconectado', color: 'neutral' as const, icon: WifiOff },
  error: { label: 'Erro', color: 'danger' as const, icon: AlertTriangle },
};

const logStatusConfig = {
  success: { color: 'success' as const },
  warning: { color: 'warning' as const },
  error: { color: 'danger' as const },
};

const actionLabels = {
  send: 'Envio',
  receive: 'Recebimento',
  error: 'Erro',
  retry: 'Tentativa',
};

const eventColumns: Column<ESocialEvent>[] = [
  {
    key: 'code',
    header: 'Evento',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.code}</p>
        <p className="text-xs text-text-muted truncate max-w-[200px]">{row.name}</p>
      </div>
    ),
  },
  {
    key: 'category',
    header: 'Categoria',
    render: (row) => <Badge variant="info">{categoryLabels[row.category]}</Badge>,
  },
  {
    key: 'reference',
    header: 'Referência',
    render: (row) => <span className="text-sm">{row.reference}</span>,
  },
  {
    key: 'employees',
    header: 'Registros',
    render: (row) => <span className="font-medium">{row.employees}</span>,
  },
  {
    key: 'deadline',
    header: 'Prazo',
    render: (row) => {
      const isOverdue = new Date(row.deadline) < new Date() && row.status !== 'accepted';
      return (
        <span className={`text-sm ${isOverdue ? 'text-accent-danger font-medium' : ''}`}>
          {new Date(row.deadline).toLocaleDateString('pt-BR')}
        </span>
      );
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return (
        <div className="flex items-center gap-2">
          <Badge variant={config.color}>{config.label}</Badge>
          {row.errorMessage && (
            <AlertTriangle className="w-4 h-4 text-accent-danger" />
          )}
        </div>
      );
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
        {row.status === 'pending' && (
          <Button variant="primary" size="sm" leftIcon={<Send className="w-3 h-3" />}>
            Enviar
          </Button>
        )}
        {row.status === 'rejected' && (
          <Button variant="danger" size="sm" leftIcon={<RefreshCw className="w-3 h-3" />}>
            Corrigir
          </Button>
        )}
      </div>
    ),
  },
];

const logColumns: Column<ProcessingLog>[] = [
  {
    key: 'timestamp',
    header: 'Data/Hora',
    render: (row) => <span className="text-sm font-mono">{row.timestamp}</span>,
  },
  {
    key: 'eventCode',
    header: 'Evento',
    render: (row) => (
      <div>
        <p className="font-medium text-text-primary">{row.eventCode}</p>
        <p className="text-xs text-text-muted">{row.eventName}</p>
      </div>
    ),
  },
  {
    key: 'action',
    header: 'Ação',
    render: (row) => <span className="text-sm">{actionLabels[row.action]}</span>,
  },
  {
    key: 'message',
    header: 'Mensagem',
    render: (row) => <span className="text-sm text-text-secondary">{row.message}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = logStatusConfig[row.status];
      return (
        <div className="flex items-center gap-2">
          {row.status === 'success' && <CheckCircle2 className="w-4 h-4 text-accent-success" />}
          {row.status === 'warning' && <AlertTriangle className="w-4 h-4 text-accent-warning" />}
          {row.status === 'error' && <XCircle className="w-4 h-4 text-accent-danger" />}
        </div>
      );
    },
  },
];

export function GovernmentPage() {
  const [selectedTab, setSelectedTab] = useState('events');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatusEvents, setFilterStatusEvents] = useState('all');
  const [modalEventType, setModalEventType] = useState('periodic');
  const [modalReference, setModalReference] = useState('2026-01');

  // Stats
  const pendingEvents = esocialEvents.filter(e => e.status === 'pending' || e.status === 'processing').length;
  const rejectedEvents = esocialEvents.filter(e => e.status === 'rejected').length;
  const connectedSystems = connections.filter(c => c.status === 'connected').length;
  const systemsWithError = connections.filter(c => c.status === 'error').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Integrações Governamentais
            </h1>
            <p className="text-text-secondary mt-1">
              eSocial, EFD-Reinf e demais obrigações
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Sincronizar
            </Button>
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button
              variant="primary"
              leftIcon={<Send className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Enviar Eventos
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Eventos Pendentes"
              value={pendingEvents}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Rejeitados"
              value={rejectedEvents}
              icon={<XCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Sistemas Conectados"
              value={`${connectedSystems}/${connections.length}`}
              icon={<Server className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Com Erro"
              value={systemsWithError}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Connection Status */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">Status das Conexões</h3>
            </CardHeader>
            <CardBody>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {connections.map((conn) => {
                  const config = connectionStatusConfig[conn.status];
                  const StatusIcon = config.icon;
                  return (
                    <div
                      key={conn.id}
                      className={`p-4 rounded-lg border ${
                        conn.status === 'connected' ? 'border-accent-success/30 bg-accent-success/5' :
                        conn.status === 'error' ? 'border-accent-danger/30 bg-accent-danger/5' :
                        'border-border-default bg-bg-tertiary'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-text-primary">{conn.name}</h4>
                          <p className="text-xs text-text-muted mt-1">{conn.description}</p>
                        </div>
                        <StatusIcon className={`w-5 h-5 ${
                          conn.status === 'connected' ? 'text-accent-success' :
                          conn.status === 'error' ? 'text-accent-danger' :
                          'text-text-muted'
                        }`} />
                      </div>
                      <div className="mt-3 pt-3 border-t border-border-subtle">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-text-muted">Última Sincronização</span>
                          <span className="text-text-secondary">{conn.lastSync || 'Nunca'}</span>
                        </div>
                        {conn.certificateExpiry && (
                          <div className="flex items-center justify-between text-xs mt-1">
                            <span className="text-text-muted">Certificado válido até</span>
                            <span className="text-text-secondary">
                              {new Date(conn.certificateExpiry).toLocaleDateString('pt-BR')}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>
        </motion.div>

        {/* Rejected Events Alert */}
        {rejectedEvents > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card className="border-accent-danger/30 bg-accent-danger/5">
              <CardBody>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent-danger/20 rounded-lg">
                      <XCircle className="w-5 h-5 text-accent-danger" />
                    </div>
                    <div>
                      <h4 className="font-medium text-text-primary">Eventos Rejeitados</h4>
                      <p className="text-sm text-text-secondary">
                        {rejectedEvents} {rejectedEvents === 1 ? 'evento precisa' : 'eventos precisam'} de correção
                      </p>
                    </div>
                  </div>
                  <Button variant="danger" size="sm">
                    Ver Erros
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* Tabs */}
        <Card>
          <CardBody className="py-4">
            <SimpleTabBar
              tabs={[
                { value: 'events', label: 'Eventos eSocial' },
                { value: 'logs', label: 'Log de Processamento' },
                { value: 'calendar', label: 'Calendário' },
              ]}
              value={selectedTab}
              onChange={setSelectedTab}
              variant="pills"
            />
          </CardBody>
        </Card>

        {/* Content */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
          <Card>
            {selectedTab !== 'calendar' && (
              <CardBody className="border-b border-border-subtle">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Input
                      placeholder="Buscar..."
                      leftIcon={<Search className="w-4 h-4" />}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  {selectedTab === 'events' && (
                    <>
                      <Select
                        options={[
                          { value: 'all', label: 'Todas Categorias' },
                          { value: 'initial', label: 'Inicial' },
                          { value: 'periodic', label: 'Periódico' },
                          { value: 'non_periodic', label: 'Não Periódico' },
                        ]}
                        value={filterCategory}
                        onChange={(value) => setFilterCategory(value)}
                        className="w-44"
                      />
                      <Select
                        options={[
                          { value: 'all', label: 'Todos Status' },
                          { value: 'pending', label: 'Pendentes' },
                          { value: 'processing', label: 'Processando' },
                          { value: 'accepted', label: 'Aceitos' },
                          { value: 'rejected', label: 'Rejeitados' },
                        ]}
                        value={filterStatusEvents}
                        onChange={(value) => setFilterStatusEvents(value)}
                        className="w-40"
                      />
                    </>
                  )}
                </div>
              </CardBody>
            )}
            <CardBody className={selectedTab === 'calendar' ? '' : 'p-0'}>
              {selectedTab === 'events' ? (
                <DataTable
                  columns={eventColumns}
                  data={esocialEvents}
                  keyExtractor={(row) => row.id}
                />
              ) : selectedTab === 'logs' ? (
                <DataTable
                  columns={logColumns}
                  data={processingLogs}
                  keyExtractor={(row) => row.id}
                />
              ) : (
                <div className="text-center py-12">
                  <Calendar className="w-12 h-12 text-text-muted mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-text-primary">Calendário de Obrigações</h3>
                  <p className="text-text-secondary mt-1">Visualize os prazos de entrega das obrigações</p>
                  <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
                    {[
                      { date: '07/02/2026', event: 'eSocial - Eventos Periódicos', status: 'warning' },
                      { date: '15/02/2026', event: 'EFD-Contribuições', status: 'info' },
                      { date: '28/02/2026', event: 'DIRF 2025', status: 'info' },
                    ].map((item, idx) => (
                      <Card key={idx}>
                        <CardBody className="text-center">
                          <p className="text-lg font-bold text-accent-primary">{item.date}</p>
                          <p className="text-sm text-text-secondary mt-1">{item.event}</p>
                        </CardBody>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardBody>
          </Card>
        </motion.div>

        {/* Send Events Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Enviar Eventos"
          description="Selecione os eventos para enviar ao eSocial"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Enviar Selecionados
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Select
              label="Tipo de Evento"
              options={[
                { value: 'all', label: 'Todos os Tipos' },
                { value: 'periodic', label: 'Eventos Periódicos' },
                { value: 'non_periodic', label: 'Eventos Não Periódicos' },
              ]}
              value={modalEventType}
              onChange={(value) => setModalEventType(value)}
            />
            <Select
              label="Referência"
              options={[
                { value: '2026-01', label: 'Janeiro/2026' },
                { value: '2025-12', label: 'Dezembro/2025' },
              ]}
              value={modalReference}
              onChange={(value) => setModalReference(value)}
            />
            <div className="p-4 bg-bg-tertiary rounded-lg">
              <h4 className="text-sm font-medium text-text-primary mb-3">Eventos Disponíveis</h4>
              <div className="space-y-2">
                {esocialEvents.filter(e => e.status === 'pending').map((event) => (
                  <label key={event.id} className="flex items-center gap-3 p-2 hover:bg-bg-hover rounded">
                    <input type="checkbox" className="rounded" />
                    <div className="flex-1">
                      <span className="font-medium">{event.code}</span>
                      <span className="text-text-muted ml-2">{event.name}</span>
                    </div>
                    <span className="text-sm text-text-muted">{event.employees} registros</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
