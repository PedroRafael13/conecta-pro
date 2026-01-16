'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Calendar,
  DollarSign,
  Building2,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  Eye,
  Edit,
  Send,
  FileText,
  ArrowUpRight,
  Mail,
  Phone,
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
interface Receivable {
  id: string;
  number: string;
  client: string;
  clientEmail: string;
  contract: string;
  description: string;
  value: number;
  dueDate: string;
  receivedDate: string | null;
  status: 'pending' | 'overdue' | 'received' | 'partial' | 'cancelled';
  paymentMethod: string;
  nfNumber: string | null;
}

// Mock Data
const receivables: Receivable[] = [
  {
    id: '1',
    number: 'CR-2026-0089',
    client: 'Shopping Center Norte',
    clientEmail: 'financeiro@scn.com.br',
    contract: 'CONT-2026-0002',
    description: 'Facilities - Janeiro/2026',
    value: 128000,
    dueDate: '2026-01-20',
    receivedDate: null,
    status: 'pending',
    paymentMethod: 'Boleto',
    nfNumber: 'NF-2026-00123',
  },
  {
    id: '2',
    number: 'CR-2026-0088',
    client: 'Hospital São Lucas',
    clientEmail: 'pagamentos@hsl.com.br',
    contract: 'CONT-2026-0003',
    description: 'Limpeza Hospitalar - Janeiro/2026',
    value: 185000,
    dueDate: '2026-01-25',
    receivedDate: null,
    status: 'pending',
    paymentMethod: 'Depósito',
    nfNumber: 'NF-2026-00122',
  },
  {
    id: '3',
    number: 'CR-2026-0087',
    client: 'Condomínio Aurora',
    clientEmail: 'sindico@aurora.com',
    contract: 'CONT-2026-0001',
    description: 'Segurança 24h - Janeiro/2026',
    value: 45000,
    dueDate: '2026-01-15',
    receivedDate: '2026-01-15',
    status: 'received',
    paymentMethod: 'PIX',
    nfNumber: 'NF-2026-00121',
  },
  {
    id: '4',
    number: 'CR-2026-0086',
    client: 'Tech Park Empresarial',
    clientEmail: 'adm@techpark.io',
    contract: 'CONT-2026-0004',
    description: 'Manutenção - Janeiro/2026',
    value: 54000,
    dueDate: '2026-01-10',
    receivedDate: '2026-01-12',
    status: 'received',
    paymentMethod: 'Transferência',
    nfNumber: 'NF-2026-00120',
  },
  {
    id: '5',
    number: 'CR-2025-0412',
    client: 'Centro de Convenções',
    clientEmail: 'financeiro@centroconv.com.br',
    contract: 'CONT-2025-0089',
    description: 'Eventos - Dezembro/2025',
    value: 35000,
    dueDate: '2026-01-05',
    receivedDate: null,
    status: 'overdue',
    paymentMethod: 'Boleto',
    nfNumber: 'NF-2025-00890',
  },
  {
    id: '6',
    number: 'CR-2025-0411',
    client: 'Edifício Corporate Tower',
    clientEmail: 'adm@corporate.com',
    contract: 'CONT-2025-0078',
    description: 'Portaria - Dezembro/2025',
    value: 28000,
    dueDate: '2025-12-30',
    receivedDate: null,
    status: 'overdue',
    paymentMethod: 'Boleto',
    nfNumber: 'NF-2025-00889',
  },
];

const statusConfig = {
  pending: { label: 'A Receber', color: 'warning' as const, icon: Clock },
  overdue: { label: 'Vencido', color: 'danger' as const, icon: AlertTriangle },
  received: { label: 'Recebido', color: 'success' as const, icon: CheckCircle2 },
  partial: { label: 'Parcial', color: 'info' as const, icon: DollarSign },
  cancelled: { label: 'Cancelado', color: 'neutral' as const, icon: XCircle },
};

const columns: Column<Receivable>[] = [
  {
    key: 'number',
    header: 'Título',
    render: (row) => (
      <div>
        <p className="font-mono text-sm font-medium text-accent-primary">{row.number}</p>
        <p className="text-xs text-text-muted">{row.contract}</p>
      </div>
    ),
  },
  {
    key: 'client',
    header: 'Cliente',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.client} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.client}</p>
          <p className="text-xs text-text-muted line-clamp-1">{row.description}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'value',
    header: 'Valor',
    sortable: true,
    render: (row) => (
      <span className="font-mono font-medium text-success">
        {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
      </span>
    ),
  },
  {
    key: 'dueDate',
    header: 'Vencimento',
    sortable: true,
    render: (row) => {
      const isOverdue = new Date(row.dueDate) < new Date() && row.status !== 'received';
      return (
        <div className="flex items-center gap-2">
          <Calendar className={`w-4 h-4 ${isOverdue ? 'text-danger' : 'text-text-muted'}`} />
          <span className={`text-sm ${isOverdue ? 'text-danger font-medium' : 'text-text-secondary'}`}>
            {new Date(row.dueDate).toLocaleDateString('pt-BR')}
          </span>
        </div>
      );
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      return (
        <Badge variant={config.color} leftIcon={<config.icon className="w-3 h-3" />}>
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'nfNumber',
    header: 'NF',
    render: (row) => (
      <div className="flex items-center gap-2">
        <FileText className="w-4 h-4 text-text-muted" />
        <span className="text-sm font-mono text-text-secondary">{row.nfNumber || '-'}</span>
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
        {row.status === 'overdue' && (
          <Button variant="ghost" size="icon-sm" title="Cobrar">
            <Send className="w-4 h-4" />
          </Button>
        )}
        {['pending', 'overdue'].includes(row.status) && (
          <Button variant="success" size="sm">
            Baixar
          </Button>
        )}
      </div>
    ),
  },
];

export function ReceivablesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredReceivables = receivables.filter((receivable) => {
    const matchesSearch =
      receivable.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      receivable.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
      receivable.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || receivable.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  // Calculate stats
  const totalPending = receivables
    .filter((r) => r.status === 'pending')
    .reduce((acc, r) => acc + r.value, 0);
  const totalOverdue = receivables
    .filter((r) => r.status === 'overdue')
    .reduce((acc, r) => acc + r.value, 0);
  const totalReceived = receivables
    .filter((r) => r.status === 'received')
    .reduce((acc, r) => acc + r.value, 0);
  const avgDaysOverdue = 15; // Mock

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Contas a Receber
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie os recebimentos dos clientes
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Send className="w-4 h-4" />}>
              Cobrar Vencidos
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Novo Título
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
              title="A Receber"
              value={totalPending.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Vencido"
              value={totalOverdue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Recebido no Mês"
              value={totalReceived.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Dias Médio Atraso"
              value={`${avgDaysOverdue} dias`}
              icon={<Calendar className="w-6 h-6" />}
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
                  { value: 'all', label: `Todos (${receivables.length})` },
                  { value: 'pending', label: `A Receber (${receivables.filter((r) => r.status === 'pending').length})` },
                  { value: 'overdue', label: `Vencidos (${receivables.filter((r) => r.status === 'overdue').length})` },
                  { value: 'received', label: `Recebidos (${receivables.filter((r) => r.status === 'received').length})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar títulos..."
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

        {/* Receivables Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredReceivables}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => console.log('Receivable clicked:', row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* Alert for overdue */}
        {totalOverdue > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card className="border-danger/30 bg-danger/5">
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-danger/10">
                    <AlertTriangle className="w-6 h-6 text-danger" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-text-primary">
                      Títulos vencidos precisam de cobrança
                    </p>
                    <p className="text-sm text-text-secondary mt-1">
                      {receivables.filter((r) => r.status === 'overdue').length} título(s) vencido(s) totalizando{' '}
                      {totalOverdue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                  </div>
                  <Button variant="danger" size="sm" leftIcon={<Send className="w-4 h-4" />}>
                    Enviar Cobrança
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* New Receivable Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Novo Título a Receber"
          description="Cadastre um novo título"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Cadastrar
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input label="Número" placeholder="Auto-gerado" disabled />
              <Select
                label="Cliente"
                options={[
                  { value: '1', label: 'Shopping Center Norte' },
                  { value: '2', label: 'Hospital São Lucas' },
                  { value: '3', label: 'Condomínio Aurora' },
                  { value: '4', label: 'Tech Park' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <Select
              label="Contrato"
              options={[
                { value: '1', label: 'CONT-2026-0001 - Segurança' },
                { value: '2', label: 'CONT-2026-0002 - Facilities' },
                { value: '3', label: 'CONT-2026-0003 - Limpeza' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione o contrato..."
            />
            <Input label="Descrição" placeholder="Descrição do recebimento" />
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Valor"
                placeholder="R$ 0,00"
                leftIcon={<span className="text-text-muted">R$</span>}
                required
              />
              <Input label="Vencimento" type="date" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Forma de Pagamento"
                options={[
                  { value: 'boleto', label: 'Boleto' },
                  { value: 'transferencia', label: 'Transferência' },
                  { value: 'pix', label: 'PIX' },
                  { value: 'deposito', label: 'Depósito' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Input label="Número NF" placeholder="NF-2026-XXXXX" />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
