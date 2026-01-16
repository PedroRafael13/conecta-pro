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
  CreditCard,
  FileText,
  ArrowDownRight,
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
interface Payable {
  id: string;
  number: string;
  supplier: string;
  category: string;
  description: string;
  value: number;
  dueDate: string;
  paymentDate: string | null;
  status: 'pending' | 'overdue' | 'paid' | 'scheduled' | 'cancelled';
  paymentMethod: string;
  bankAccount: string;
  installment: string | null;
}

// Mock Data
const payables: Payable[] = [
  {
    id: '1',
    number: 'CP-2026-0125',
    supplier: 'Uniformes Brasil LTDA',
    category: 'Fornecedor',
    description: 'Lote de uniformes - Janeiro',
    value: 18500,
    dueDate: '2026-01-20',
    paymentDate: null,
    status: 'pending',
    paymentMethod: 'Boleto',
    bankAccount: 'Itaú Empresas',
    installment: '1/3',
  },
  {
    id: '2',
    number: 'CP-2026-0124',
    supplier: 'Receita Federal',
    category: 'Imposto',
    description: 'INSS Competência 12/2025',
    value: 42000,
    dueDate: '2026-01-20',
    paymentDate: null,
    status: 'scheduled',
    paymentMethod: 'DARF',
    bankAccount: 'Bradesco PJ',
    installment: null,
  },
  {
    id: '3',
    number: 'CP-2026-0123',
    supplier: 'Aluguel Sede Central',
    category: 'Administrativo',
    description: 'Aluguel Janeiro/2026',
    value: 15000,
    dueDate: '2026-01-10',
    paymentDate: '2026-01-09',
    status: 'paid',
    paymentMethod: 'Transferência',
    bankAccount: 'Itaú Empresas',
    installment: null,
  },
  {
    id: '4',
    number: 'CP-2026-0122',
    supplier: 'Seguradora XYZ',
    category: 'Seguro',
    description: 'Seguro de frota - Parcela',
    value: 8500,
    dueDate: '2026-01-05',
    paymentDate: null,
    status: 'overdue',
    paymentMethod: 'Débito Automático',
    bankAccount: 'Itaú Empresas',
    installment: '2/12',
  },
  {
    id: '5',
    number: 'CP-2026-0121',
    supplier: 'Telefonia Corp',
    category: 'Operacional',
    description: 'Internet e Telefonia - Janeiro',
    value: 3200,
    dueDate: '2026-01-15',
    paymentDate: '2026-01-14',
    status: 'paid',
    paymentMethod: 'Débito Automático',
    bankAccount: 'Bradesco PJ',
    installment: null,
  },
  {
    id: '6',
    number: 'CP-2026-0120',
    supplier: 'Energia Elétrica SA',
    category: 'Utilidades',
    description: 'Conta de luz - Sede',
    value: 4800,
    dueDate: '2026-01-25',
    paymentDate: null,
    status: 'pending',
    paymentMethod: 'Boleto',
    bankAccount: 'Itaú Empresas',
    installment: null,
  },
];

const statusConfig = {
  pending: { label: 'Pendente', color: 'warning' as const, icon: Clock },
  overdue: { label: 'Vencido', color: 'danger' as const, icon: AlertTriangle },
  paid: { label: 'Pago', color: 'success' as const, icon: CheckCircle2 },
  scheduled: { label: 'Agendado', color: 'info' as const, icon: Calendar },
  cancelled: { label: 'Cancelado', color: 'neutral' as const, icon: XCircle },
};

const columns: Column<Payable>[] = [
  {
    key: 'number',
    header: 'Título',
    render: (row) => (
      <div>
        <p className="font-mono text-sm font-medium text-accent-primary">{row.number}</p>
        <p className="text-xs text-text-muted">{row.category}</p>
      </div>
    ),
  },
  {
    key: 'supplier',
    header: 'Fornecedor',
    render: (row) => (
      <div className="flex items-center gap-3">
        <Avatar name={row.supplier} size="sm" />
        <div>
          <p className="font-medium text-text-primary">{row.supplier}</p>
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
      <div>
        <span className="font-mono font-medium text-danger">
          {row.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
        </span>
        {row.installment && (
          <p className="text-xs text-text-muted mt-0.5">Parcela {row.installment}</p>
        )}
      </div>
    ),
  },
  {
    key: 'dueDate',
    header: 'Vencimento',
    sortable: true,
    render: (row) => {
      const isOverdue = new Date(row.dueDate) < new Date() && row.status !== 'paid';
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
    key: 'paymentMethod',
    header: 'Pagamento',
    render: (row) => (
      <div className="flex items-center gap-2">
        <CreditCard className="w-4 h-4 text-text-muted" />
        <div>
          <p className="text-sm text-text-secondary">{row.paymentMethod}</p>
          <p className="text-xs text-text-muted">{row.bankAccount}</p>
        </div>
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
        <Button variant="ghost" size="icon-sm" title="Editar">
          <Edit className="w-4 h-4" />
        </Button>
        {row.status === 'pending' && (
          <Button variant="primary" size="sm">
            Pagar
          </Button>
        )}
      </div>
    ),
  },
];

export function PayablesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredPayables = payables.filter((payable) => {
    const matchesSearch =
      payable.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payable.supplier.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payable.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = selectedTab === 'all' || payable.status === selectedTab;
    return matchesSearch && matchesTab;
  });

  // Calculate stats
  const totalPending = payables
    .filter((p) => p.status === 'pending')
    .reduce((acc, p) => acc + p.value, 0);
  const totalOverdue = payables
    .filter((p) => p.status === 'overdue')
    .reduce((acc, p) => acc + p.value, 0);
  const totalScheduled = payables
    .filter((p) => p.status === 'scheduled')
    .reduce((acc, p) => acc + p.value, 0);
  const totalPaid = payables
    .filter((p) => p.status === 'paid')
    .reduce((acc, p) => acc + p.value, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Contas a Pagar
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie suas obrigações financeiras
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Upload className="w-4 h-4" />}>
              Importar
            </Button>
            <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
              Exportar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsModalOpen(true)}
            >
              Nova Conta
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
              title="Pendente"
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
              title="Agendado"
              value={totalScheduled.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Pago no Mês"
              value={totalPaid.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
              icon={<CheckCircle2 className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs & Search */}
        <Card>
          <CardBody className="py-4">
            <div className="flex items-center justify-between gap-4">
              <SimpleTabBar
                tabs={[
                  { value: 'all', label: `Todas (${payables.length})` },
                  { value: 'pending', label: `Pendentes (${payables.filter((p) => p.status === 'pending').length})` },
                  { value: 'overdue', label: `Vencidas (${payables.filter((p) => p.status === 'overdue').length})` },
                  { value: 'scheduled', label: `Agendadas (${payables.filter((p) => p.status === 'scheduled').length})` },
                  { value: 'paid', label: `Pagas (${payables.filter((p) => p.status === 'paid').length})` },
                ]}
                value={selectedTab}
                onChange={setSelectedTab}
                variant="pills"
              />
              <div className="flex items-center gap-3">
                <Input
                  placeholder="Buscar contas..."
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

        {/* Payables Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredPayables}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => console.log('Payable clicked:', row)}
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
                      Você possui contas vencidas
                    </p>
                    <p className="text-sm text-text-secondary mt-1">
                      {payables.filter((p) => p.status === 'overdue').length} título(s) vencido(s) totalizando{' '}
                      {totalOverdue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                    </p>
                  </div>
                  <Button variant="danger" size="sm">
                    Regularizar Agora
                  </Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* New Payable Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Nova Conta a Pagar"
          description="Cadastre uma nova obrigação"
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
                label="Categoria"
                options={[
                  { value: 'fornecedor', label: 'Fornecedor' },
                  { value: 'imposto', label: 'Imposto' },
                  { value: 'administrativo', label: 'Administrativo' },
                  { value: 'operacional', label: 'Operacional' },
                  { value: 'utilidades', label: 'Utilidades' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
            <Input label="Fornecedor" placeholder="Nome do fornecedor" required />
            <Input label="Descrição" placeholder="Descrição do pagamento" />
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
                  { value: 'debito', label: 'Débito Automático' },
                  { value: 'pix', label: 'PIX' },
                  { value: 'darf', label: 'DARF' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Conta Bancária"
                options={[
                  { value: 'itau', label: 'Itaú Empresas' },
                  { value: 'bradesco', label: 'Bradesco PJ' },
                  { value: 'santander', label: 'Santander' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
