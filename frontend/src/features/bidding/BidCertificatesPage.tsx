'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  Plus,
  Award,
  FileText,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  Edit2,
  Download,
  Upload,
  MoreHorizontal,
  Shield,
  Building2,
  RefreshCw,
  Bell,
  TrendingUp,
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
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Types
interface Certificate {
  id: string;
  name: string;
  type: 'cndt' | 'crf' | 'certidao_negativa' | 'atestado_capacidade' | 'alvara' | 'iso' | 'outros';
  issuer: string;
  issueDate: string;
  expirationDate: string;
  status: 'valid' | 'expiring' | 'expired' | 'pending';
  document: string | null;
  notes: string;
  alertDays: number;
  createdAt: string;
}

// Mock Data
const certificates: Certificate[] = [
  {
    id: '1',
    name: 'CNDT - Certidão Negativa de Débitos Trabalhistas',
    type: 'cndt',
    issuer: 'Tribunal Superior do Trabalho',
    issueDate: '2026-01-10',
    expirationDate: '2026-07-10',
    status: 'valid',
    document: '/docs/cndt-2026.pdf',
    notes: '',
    alertDays: 30,
    createdAt: '2026-01-10',
  },
  {
    id: '2',
    name: 'CRF - Certificado de Regularidade do FGTS',
    type: 'crf',
    issuer: 'Caixa Econômica Federal',
    issueDate: '2026-01-05',
    expirationDate: '2026-02-05',
    status: 'expiring',
    document: '/docs/crf-2026.pdf',
    notes: 'Vence em 20 dias - Renovar urgente',
    alertDays: 30,
    createdAt: '2026-01-05',
  },
  {
    id: '3',
    name: 'Certidão Negativa Federal - Receita Federal',
    type: 'certidao_negativa',
    issuer: 'Receita Federal do Brasil',
    issueDate: '2025-12-15',
    expirationDate: '2026-06-15',
    status: 'valid',
    document: '/docs/certidao-rf-2025.pdf',
    notes: '',
    alertDays: 30,
    createdAt: '2025-12-15',
  },
  {
    id: '4',
    name: 'Atestado de Capacidade Técnica - Shopping Center Norte',
    type: 'atestado_capacidade',
    issuer: 'Shopping Center Norte',
    issueDate: '2025-11-20',
    expirationDate: '2027-11-20',
    status: 'valid',
    document: '/docs/atestado-scn-2025.pdf',
    notes: 'Contrato de 500 vigilantes',
    alertDays: 60,
    createdAt: '2025-11-20',
  },
  {
    id: '5',
    name: 'Alvará de Funcionamento',
    type: 'alvara',
    issuer: 'Prefeitura de São Paulo',
    issueDate: '2025-01-01',
    expirationDate: '2025-12-31',
    status: 'expired',
    document: '/docs/alvara-2025.pdf',
    notes: 'Renovação em andamento',
    alertDays: 30,
    createdAt: '2025-01-01',
  },
  {
    id: '6',
    name: 'ISO 9001:2015 - Gestão da Qualidade',
    type: 'iso',
    issuer: 'Bureau Veritas',
    issueDate: '2024-06-15',
    expirationDate: '2027-06-15',
    status: 'valid',
    document: '/docs/iso9001-2024.pdf',
    notes: 'Auditoria de manutenção em Jun/2025',
    alertDays: 90,
    createdAt: '2024-06-15',
  },
];

const certificatesByType = [
  { name: 'Certidões Negativas', value: 35, color: '#3B82F6' },
  { name: 'Atestados Técnicos', value: 25, color: '#10B981' },
  { name: 'Alvarás/Licenças', value: 20, color: '#F59E0B' },
  { name: 'Certificações ISO', value: 15, color: '#8B5CF6' },
  { name: 'Outros', value: 5, color: '#6B7280' },
];

const expirationTimeline = [
  { month: 'Jan', expiring: 3 },
  { month: 'Fev', expiring: 5 },
  { month: 'Mar', expiring: 2 },
  { month: 'Abr', expiring: 4 },
  { month: 'Mai', expiring: 1 },
  { month: 'Jun', expiring: 6 },
];

const tabs = [
  { id: 'all', label: 'Todos' },
  { id: 'valid', label: 'Válidos' },
  { id: 'expiring', label: 'A Vencer' },
  { id: 'expired', label: 'Vencidos' },
];

const typeLabels = {
  cndt: 'CNDT',
  crf: 'CRF/FGTS',
  certidao_negativa: 'Certidão Negativa',
  atestado_capacidade: 'Atestado Técnico',
  alvara: 'Alvará',
  iso: 'Certificação ISO',
  outros: 'Outros',
};

const typeColors = {
  cndt: 'info',
  crf: 'success',
  certidao_negativa: 'primary',
  atestado_capacidade: 'warning',
  alvara: 'secondary',
  iso: 'danger',
  outros: 'neutral',
} as const;

const statusConfig = {
  valid: { label: 'Válido', color: 'success', icon: CheckCircle2 },
  expiring: { label: 'A Vencer', color: 'warning', icon: AlertTriangle },
  expired: { label: 'Vencido', color: 'danger', icon: XCircle },
  pending: { label: 'Pendente', color: 'secondary', icon: Clock },
} as const;

const columns: Column<Certificate>[] = [
  {
    key: 'name',
    header: 'Certificado',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${row.status === 'expired' ? 'bg-danger/10' : row.status === 'expiring' ? 'bg-warning/10' : 'bg-success/10'}`}>
          <Award className={`w-5 h-5 ${row.status === 'expired' ? 'text-danger' : row.status === 'expiring' ? 'text-warning' : 'text-success'}`} />
        </div>
        <div>
          <p className="font-medium text-text-primary">{row.name}</p>
          <p className="text-xs text-text-muted">{row.issuer}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'type',
    header: 'Tipo',
    render: (row) => <Badge variant={typeColors[row.type]}>{typeLabels[row.type]}</Badge>,
  },
  {
    key: 'issueDate',
    header: 'Emissão',
    render: (row) => <span className="text-sm">{new Date(row.issueDate).toLocaleDateString('pt-BR')}</span>,
  },
  {
    key: 'expirationDate',
    header: 'Validade',
    render: (row) => {
      const daysToExpire = Math.ceil((new Date(row.expirationDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
      return (
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-text-muted" />
          <span className={`text-sm ${daysToExpire < 0 ? 'text-danger' : daysToExpire < 30 ? 'text-warning' : ''}`}>
            {new Date(row.expirationDate).toLocaleDateString('pt-BR')}
          </span>
          {daysToExpire > 0 && daysToExpire <= 30 && (
            <Badge variant="warning" size="sm">{daysToExpire}d</Badge>
          )}
        </div>
      );
    },
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const config = statusConfig[row.status];
      const Icon = config.icon;
      return (
        <Badge variant={config.color as any}>
          <Icon className="w-3 h-3 mr-1" />
          {config.label}
        </Badge>
      );
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Ver">
          <Eye className="w-4 h-4" />
        </Button>
        {row.document && (
          <Button variant="ghost" size="icon-sm" title="Download">
            <Download className="w-4 h-4" />
          </Button>
        )}
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

export function BidCertificatesPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const filteredCertificates = certificates.filter((cert) => {
    const matchesSearch = cert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cert.issuer.toLowerCase().includes(searchTerm.toLowerCase());
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && cert.status === activeTab;
  });

  // Stats
  const totalCertificates = certificates.length;
  const validCertificates = certificates.filter((c) => c.status === 'valid').length;
  const expiringCertificates = certificates.filter((c) => c.status === 'expiring').length;
  const expiredCertificates = certificates.filter((c) => c.status === 'expired').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Certificados e Qualificações</h1>
            <p className="text-text-secondary mt-1">Gestão de documentos de habilitação para licitações</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Verificar Validades
            </Button>
            <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />} onClick={() => setIsCreateModalOpen(true)}>
              Novo Certificado
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard title="Total de Certificados" value={totalCertificates} icon={<FileText className="w-6 h-6" />} iconColor="primary" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard title="Válidos" value={validCertificates} icon={<CheckCircle2 className="w-6 h-6" />} iconColor="success" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard title="A Vencer (30 dias)" value={expiringCertificates} icon={<AlertTriangle className="w-6 h-6" />} iconColor="warning" />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard title="Vencidos" value={expiredCertificates} icon={<XCircle className="w-6 h-6" />} iconColor="danger" />
          </motion.div>
        </StatGrid>

        {/* Alert for expiring certificates */}
        {expiringCertificates > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="border-warning/50 bg-warning/5">
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-warning/20">
                    <Bell className="w-6 h-6 text-warning" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-warning">Atenção: Certificados a vencer</h4>
                    <p className="text-sm text-text-secondary mt-1">
                      Você tem {expiringCertificates} certificado(s) próximo(s) ao vencimento. Verifique a lista e providencie a renovação.
                    </p>
                  </div>
                  <Button variant="warning">Ver Detalhes</Button>
                </div>
              </CardBody>
            </Card>
          </motion.div>
        )}

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Certificados por Tipo</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={certificatesByType} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                      {certificatesByType.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {certificatesByType.map((item) => (
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
                <TrendingUp className="w-5 h-5 text-warning" />
                <h3 className="font-semibold">Vencimentos por Mês</h3>
              </div>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={expirationTimeline}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="month" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip />
                    <Bar dataKey="expiring" fill="#F59E0B" radius={[4, 4, 0, 0]} name="Vencimentos" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Tabs & Search */}
        <div className="flex items-center justify-between">
          <SimpleTabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
          <div className="flex items-center gap-3">
            <Input
              placeholder="Buscar certificados..."
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

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardBody className="p-0">
              <DataTable columns={columns} data={filteredCertificates} keyExtractor={(row) => row.id} />
            </CardBody>
          </Card>
        </motion.div>

        {/* Create Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          title="Novo Certificado"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary">Salvar Certificado</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Nome do Certificado" placeholder="Ex: CNDT - Certidão Negativa de Débitos" required />
            <Select
              label="Tipo"
              options={[
                { value: 'cndt', label: 'CNDT' },
                { value: 'crf', label: 'CRF/FGTS' },
                { value: 'certidao_negativa', label: 'Certidão Negativa' },
                { value: 'atestado_capacidade', label: 'Atestado de Capacidade Técnica' },
                { value: 'alvara', label: 'Alvará/Licença' },
                { value: 'iso', label: 'Certificação ISO' },
                { value: 'outros', label: 'Outros' },
              ]}
              value=""
              onChange={() => {}}
              placeholder="Selecione..."
            />
            <Input label="Órgão Emissor" placeholder="Ex: Tribunal Superior do Trabalho" />
            <div className="grid grid-cols-2 gap-4">
              <Input label="Data de Emissão" type="date" required />
              <Input label="Data de Validade" type="date" required />
            </div>
            <Input label="Alerta (dias antes do vencimento)" type="number" placeholder="30" />
            <div className="p-4 rounded-lg border border-dashed border-border">
              <div className="flex items-center justify-center gap-2 text-text-muted">
                <Upload className="w-5 h-5" />
                <span>Arraste o documento ou clique para fazer upload</span>
              </div>
            </div>
            <Textarea label="Observações" placeholder="Informações adicionais..." rows={3} />
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}
