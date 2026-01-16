'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  FileText,
  PenTool,
  CheckCircle2,
  Clock,
  XCircle,
  AlertTriangle,
  Users,
  Send,
  Download,
  Eye,
  Plus,
  MoreHorizontal,
  Shield,
  Fingerprint,
  FileSignature,
  Mail,
  Calendar,
  User,
  Building,
  Stamp,
  RefreshCw,
  History,
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
interface SignatureRequest {
  id: string;
  documentName: string;
  documentType: string;
  requestedBy: string;
  requestedAt: string;
  deadline: string;
  status: 'pending' | 'signed' | 'rejected' | 'expired';
  signers: Signer[];
  signatureType: 'simple' | 'advanced' | 'qualified';
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

interface Signer {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'pending' | 'signed' | 'rejected';
  signedAt?: string;
  order: number;
}

// Mock Data
const signatureRequests: SignatureRequest[] = [
  {
    id: '1',
    documentName: 'Contrato de Prestação de Serviços - Shopping Center Norte',
    documentType: 'Contrato',
    requestedBy: 'Ana Costa',
    requestedAt: '2026-01-14T10:00:00',
    deadline: '2026-01-20',
    status: 'pending',
    signatureType: 'qualified',
    priority: 'high',
    signers: [
      { id: 's1', name: 'Carlos Lima', email: 'carlos@empresa.com', role: 'Diretor', status: 'signed', signedAt: '2026-01-14T14:30:00', order: 1 },
      { id: 's2', name: 'Roberto Silva', email: 'roberto@empresa.com', role: 'Gerente Jurídico', status: 'pending', order: 2 },
      { id: 's3', name: 'Maria Oliveira', email: 'maria@cliente.com', role: 'Representante Legal', status: 'pending', order: 3 },
    ],
  },
  {
    id: '2',
    documentName: 'Aditivo Contratual - Hospital São Lucas',
    documentType: 'Aditivo',
    requestedBy: 'Roberto Silva',
    requestedAt: '2026-01-13T15:00:00',
    deadline: '2026-01-18',
    status: 'signed',
    signatureType: 'advanced',
    priority: 'medium',
    signers: [
      { id: 's4', name: 'Ana Costa', email: 'ana@empresa.com', role: 'Gerente Comercial', status: 'signed', signedAt: '2026-01-14T09:00:00', order: 1 },
      { id: 's5', name: 'Pedro Santos', email: 'pedro@hospital.com', role: 'Administrador', status: 'signed', signedAt: '2026-01-14T16:00:00', order: 2 },
    ],
  },
  {
    id: '3',
    documentName: 'Termo de Confidencialidade - Projeto Alpha',
    documentType: 'NDA',
    requestedBy: 'Carlos Lima',
    requestedAt: '2026-01-12T08:00:00',
    deadline: '2026-01-15',
    status: 'expired',
    signatureType: 'simple',
    priority: 'low',
    signers: [
      { id: 's6', name: 'João Ferreira', email: 'joao@parceiro.com', role: 'Consultor', status: 'pending', order: 1 },
    ],
  },
  {
    id: '4',
    documentName: 'Proposta Comercial - Condomínio Residencial',
    documentType: 'Proposta',
    requestedBy: 'Ana Costa',
    requestedAt: '2026-01-15T09:00:00',
    deadline: '2026-01-22',
    status: 'pending',
    signatureType: 'advanced',
    priority: 'urgent',
    signers: [
      { id: 's7', name: 'Roberto Silva', email: 'roberto@empresa.com', role: 'Diretor Comercial', status: 'pending', order: 1 },
      { id: 's8', name: 'Cliente Teste', email: 'cliente@condominio.com', role: 'Síndico', status: 'pending', order: 2 },
    ],
  },
  {
    id: '5',
    documentName: 'Distrato - Contrato Antigo',
    documentType: 'Distrato',
    requestedBy: 'Maria Oliveira',
    requestedAt: '2026-01-10T11:00:00',
    deadline: '2026-01-17',
    status: 'rejected',
    signatureType: 'qualified',
    priority: 'medium',
    signers: [
      { id: 's9', name: 'Carlos Lima', email: 'carlos@empresa.com', role: 'Diretor', status: 'signed', signedAt: '2026-01-11T10:00:00', order: 1 },
      { id: 's10', name: 'Ex-Cliente', email: 'excliente@email.com', role: 'Contratante', status: 'rejected', order: 2 },
    ],
  },
];

const tabs = [
  { id: 'all', label: 'Todas' },
  { id: 'pending', label: 'Pendentes' },
  { id: 'signed', label: 'Assinadas' },
  { id: 'rejected', label: 'Rejeitadas' },
  { id: 'expired', label: 'Expiradas' },
];

const statusColors = {
  pending: 'warning',
  signed: 'success',
  rejected: 'danger',
  expired: 'secondary',
} as const;

const statusLabels = {
  pending: 'Pendente',
  signed: 'Assinado',
  rejected: 'Rejeitado',
  expired: 'Expirado',
};

const statusIcons = {
  pending: Clock,
  signed: CheckCircle2,
  rejected: XCircle,
  expired: AlertTriangle,
};

const priorityColors = {
  low: 'secondary',
  medium: 'info',
  high: 'warning',
  urgent: 'danger',
} as const;

const priorityLabels = {
  low: 'Baixa',
  medium: 'Média',
  high: 'Alta',
  urgent: 'Urgente',
};

const signatureTypeLabels = {
  simple: 'Simples',
  advanced: 'Avançada',
  qualified: 'Qualificada (ICP-Brasil)',
};

const columns: Column<SignatureRequest>[] = [
  {
    key: 'documentName',
    header: 'Documento',
    render: (row) => (
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-primary/10">
          <FileSignature className="w-5 h-5 text-primary" />
        </div>
        <div>
          <p className="font-medium text-text-primary line-clamp-1">{row.documentName}</p>
          <p className="text-xs text-text-muted">{row.documentType}</p>
        </div>
      </div>
    ),
  },
  {
    key: 'status',
    header: 'Status',
    render: (row) => {
      const Icon = statusIcons[row.status];
      return (
        <Badge variant={statusColors[row.status]}>
          <Icon className="w-3 h-3 mr-1" />
          {statusLabels[row.status]}
        </Badge>
      );
    },
  },
  {
    key: 'signers',
    header: 'Signatários',
    render: (row) => {
      const signed = row.signers.filter(s => s.status === 'signed').length;
      return (
        <div className="flex items-center gap-2">
          <div className="flex -space-x-2">
            {row.signers.slice(0, 3).map((signer) => (
              <Avatar
                key={signer.id}
                name={signer.name}
                size="xs"
                className={`ring-2 ring-bg-primary ${
                  signer.status === 'signed' ? 'ring-success' :
                  signer.status === 'rejected' ? 'ring-danger' : 'ring-border'
                }`}
              />
            ))}
          </div>
          <span className="text-sm text-text-muted">
            {signed}/{row.signers.length}
          </span>
        </div>
      );
    },
  },
  {
    key: 'priority',
    header: 'Prioridade',
    render: (row) => (
      <Badge variant={priorityColors[row.priority]} size="sm">
        {priorityLabels[row.priority]}
      </Badge>
    ),
  },
  {
    key: 'deadline',
    header: 'Prazo',
    render: (row) => {
      const deadline = new Date(row.deadline);
      const today = new Date();
      const isOverdue = deadline < today && row.status === 'pending';
      return (
        <div className={`flex items-center gap-2 ${isOverdue ? 'text-danger' : 'text-text-secondary'}`}>
          <Calendar className="w-4 h-4" />
          <span className="text-sm">{deadline.toLocaleDateString('pt-BR')}</span>
        </div>
      );
    },
  },
  {
    key: 'actions',
    header: '',
    render: (row) => (
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon-sm" title="Visualizar">
          <Eye className="w-4 h-4" />
        </Button>
        {row.status === 'pending' && (
          <Button variant="ghost" size="icon-sm" title="Reenviar">
            <RefreshCw className="w-4 h-4" />
          </Button>
        )}
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

export function DocumentSignaturesPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isNewRequestModalOpen, setIsNewRequestModalOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<SignatureRequest | null>(null);

  const filteredRequests = signatureRequests.filter((request) => {
    const matchesSearch = request.documentName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === 'all' || request.status === activeTab;
    return matchesSearch && matchesTab;
  });

  // Stats
  const totalRequests = signatureRequests.length;
  const pendingRequests = signatureRequests.filter(r => r.status === 'pending').length;
  const signedRequests = signatureRequests.filter(r => r.status === 'signed').length;
  const urgentRequests = signatureRequests.filter(r => r.priority === 'urgent' && r.status === 'pending').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Assinaturas Digitais
            </h1>
            <p className="text-text-secondary mt-1">
              Gerencie solicitações de assinatura eletrônica de documentos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<History className="w-4 h-4" />}>
              Histórico
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setIsNewRequestModalOpen(true)}
            >
              Nova Solicitação
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
              title="Total de Solicitações"
              value={totalRequests}
              icon={<FileSignature className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Pendentes"
              value={pendingRequests}
              icon={<Clock className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Assinadas"
              value={signedRequests}
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
              title="Urgentes"
              value={urgentRequests}
              icon={<AlertTriangle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
        </StatGrid>

        {/* Signature Types Info */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-info">
            <CardBody className="py-4">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-info/10">
                  <PenTool className="w-5 h-5 text-info" />
                </div>
                <div>
                  <h4 className="font-medium text-text-primary">Assinatura Simples</h4>
                  <p className="text-sm text-text-muted mt-1">
                    Aceite digital básico, ideal para documentos internos
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
          <Card className="border-l-4 border-l-warning">
            <CardBody className="py-4">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-warning/10">
                  <Fingerprint className="w-5 h-5 text-warning" />
                </div>
                <div>
                  <h4 className="font-medium text-text-primary">Assinatura Avançada</h4>
                  <p className="text-sm text-text-muted mt-1">
                    Verificação de identidade, validade jurídica ampliada
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
          <Card className="border-l-4 border-l-success">
            <CardBody className="py-4">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-success/10">
                  <Shield className="w-5 h-5 text-success" />
                </div>
                <div>
                  <h4 className="font-medium text-text-primary">Assinatura Qualificada</h4>
                  <p className="text-sm text-text-muted mt-1">
                    Certificado ICP-Brasil, máxima segurança jurídica
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
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
              placeholder="Buscar documentos..."
              leftIcon={<Search className="w-4 h-4" />}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
          </div>
        </div>

        {/* Requests Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardBody className="p-0">
              <DataTable
                columns={columns}
                data={filteredRequests}
                keyExtractor={(row) => row.id}
                onRowClick={(row) => setSelectedRequest(row)}
              />
            </CardBody>
          </Card>
        </motion.div>

        {/* New Request Modal */}
        <Modal
          isOpen={isNewRequestModalOpen}
          onClose={() => setIsNewRequestModalOpen(false)}
          title="Nova Solicitação de Assinatura"
          description="Configure os detalhes da solicitação"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setIsNewRequestModalOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                Enviar Solicitação
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-xl p-6 text-center">
              <FileText className="w-10 h-10 text-text-muted mx-auto mb-3" />
              <p className="text-text-primary font-medium mb-1">
                Arraste o documento ou clique para selecionar
              </p>
              <p className="text-sm text-text-muted">PDF, DOC até 25MB</p>
              <Button variant="outline" className="mt-3">
                Selecionar Arquivo
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Select
                label="Tipo de Assinatura"
                options={[
                  { value: 'simple', label: 'Simples - Aceite Digital' },
                  { value: 'advanced', label: 'Avançada - Verificação de Identidade' },
                  { value: 'qualified', label: 'Qualificada - Certificado ICP-Brasil' },
                ]}
                value=""
                onChange={() => {}}
                placeholder="Selecione..."
              />
              <Select
                label="Prioridade"
                options={[
                  { value: 'low', label: 'Baixa' },
                  { value: 'medium', label: 'Média' },
                  { value: 'high', label: 'Alta' },
                  { value: 'urgent', label: 'Urgente' },
                ]}
                value="medium"
                onChange={() => {}}
              />
            </div>

            <Input
              label="Prazo para Assinatura"
              type="date"
            />

            <div className="space-y-3">
              <label className="text-sm font-medium text-text-primary">Signatários</label>
              <div className="border border-border rounded-lg divide-y divide-border">
                <div className="p-3 flex items-center gap-3">
                  <div className="flex-1 grid grid-cols-3 gap-3">
                    <Input placeholder="Nome" />
                    <Input placeholder="Email" type="email" />
                    <Input placeholder="Função" />
                  </div>
                  <Button variant="ghost" size="icon-sm">
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <Button variant="outline" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                Adicionar Signatário
              </Button>
            </div>

            <Textarea
              label="Mensagem (opcional)"
              placeholder="Mensagem que será enviada junto com a solicitação"
              rows={3}
            />

            <div className="flex items-center gap-2 p-3 rounded-lg bg-info/10 border border-info/20">
              <Mail className="w-5 h-5 text-info" />
              <p className="text-sm text-text-secondary">
                Os signatários receberão um email com o link para assinatura
              </p>
            </div>
          </div>
        </Modal>

        {/* Request Details Modal */}
        <Modal
          isOpen={!!selectedRequest}
          onClose={() => setSelectedRequest(null)}
          title="Detalhes da Solicitação"
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedRequest(null)}>
                Fechar
              </Button>
              {selectedRequest?.status === 'pending' && (
                <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />}>
                  Reenviar
                </Button>
              )}
            </>
          }
        >
          {selectedRequest && (
            <div className="space-y-6">
              {/* Document Info */}
              <div className="flex items-start gap-4 p-4 rounded-lg bg-bg-secondary">
                <div className="p-3 rounded-lg bg-primary/10">
                  <FileSignature className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-text-primary">{selectedRequest.documentName}</h4>
                  <div className="flex items-center gap-4 mt-2 text-sm text-text-muted">
                    <span>{selectedRequest.documentType}</span>
                    <Badge variant={statusColors[selectedRequest.status]}>
                      {statusLabels[selectedRequest.status]}
                    </Badge>
                    <Badge variant={priorityColors[selectedRequest.priority]} size="sm">
                      {priorityLabels[selectedRequest.priority]}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div>
                <h5 className="font-medium text-text-primary mb-3">Signatários</h5>
                <div className="space-y-3">
                  {selectedRequest.signers.map((signer, index) => (
                    <div
                      key={signer.id}
                      className={`flex items-center gap-4 p-3 rounded-lg border ${
                        signer.status === 'signed' ? 'border-success/30 bg-success/5' :
                        signer.status === 'rejected' ? 'border-danger/30 bg-danger/5' :
                        'border-border'
                      }`}
                    >
                      <div className="w-8 h-8 rounded-full bg-bg-secondary flex items-center justify-center font-medium">
                        {signer.order}
                      </div>
                      <Avatar name={signer.name} size="sm" />
                      <div className="flex-1">
                        <p className="font-medium text-text-primary">{signer.name}</p>
                        <p className="text-sm text-text-muted">{signer.email} • {signer.role}</p>
                      </div>
                      <div className="text-right">
                        <Badge variant={statusColors[signer.status]}>
                          {statusLabels[signer.status]}
                        </Badge>
                        {signer.signedAt && (
                          <p className="text-xs text-text-muted mt-1">
                            {new Date(signer.signedAt).toLocaleString('pt-BR')}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Info */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Solicitado por</p>
                  <p className="font-medium">{selectedRequest.requestedBy}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Tipo de Assinatura</p>
                  <p className="font-medium">{signatureTypeLabels[selectedRequest.signatureType]}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Data da Solicitação</p>
                  <p className="font-medium">{new Date(selectedRequest.requestedAt).toLocaleString('pt-BR')}</p>
                </div>
                <div className="p-3 rounded-lg bg-bg-secondary">
                  <p className="text-text-muted mb-1">Prazo</p>
                  <p className="font-medium">{new Date(selectedRequest.deadline).toLocaleDateString('pt-BR')}</p>
                </div>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
