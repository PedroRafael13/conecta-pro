'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  ScanLine,
  Upload,
  FileText,
  Image,
  Download,
  Eye,
  Copy,
  Check,
  RefreshCw,
  Settings,
  Sparkles,
  Clock,
  CheckCircle2,
  AlertCircle,
  Trash2,
  Search,
  Filter,
  MoreVertical,
  FileImage,
  File,
  Zap,
  Target,
  BarChart3,
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
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  Modal,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Progress,
  Dropdown,
  EmptyState,
} from '@/design-system/components';

// Types
interface OCRDocument {
  id: string;
  filename: string;
  type: 'image' | 'pdf' | 'scan';
  status: 'pending' | 'processing' | 'completed' | 'error';
  uploadedAt: string;
  processedAt?: string;
  extractedText?: string;
  confidence: number;
  pages: number;
  fields: ExtractedField[];
}

interface ExtractedField {
  id: string;
  label: string;
  value: string;
  confidence: number;
  category: string;
}

// Mock Data
const mockDocuments: OCRDocument[] = [
  {
    id: '1',
    filename: 'nota_fiscal_001.pdf',
    type: 'pdf',
    status: 'completed',
    uploadedAt: '2026-01-16T10:30:00',
    processedAt: '2026-01-16T10:30:45',
    confidence: 98.5,
    pages: 2,
    extractedText: 'NOTA FISCAL ELETRÔNICA\nNúmero: 001234\nData: 15/01/2026\nValor Total: R$ 15.678,90\nCNPJ: 12.345.678/0001-90\nRazão Social: Empresa Exemplo LTDA',
    fields: [
      { id: '1', label: 'Número NF', value: '001234', confidence: 99, category: 'fiscal' },
      { id: '2', label: 'Data Emissão', value: '15/01/2026', confidence: 98, category: 'fiscal' },
      { id: '3', label: 'Valor Total', value: 'R$ 15.678,90', confidence: 97, category: 'financeiro' },
      { id: '4', label: 'CNPJ', value: '12.345.678/0001-90', confidence: 99, category: 'cadastro' },
    ],
  },
  {
    id: '2',
    filename: 'contrato_servicos.pdf',
    type: 'pdf',
    status: 'completed',
    uploadedAt: '2026-01-15T14:20:00',
    processedAt: '2026-01-15T14:22:30',
    confidence: 95.2,
    pages: 8,
    fields: [
      { id: '1', label: 'Contratante', value: 'Condomínio Aurora', confidence: 96, category: 'partes' },
      { id: '2', label: 'Valor Mensal', value: 'R$ 45.000,00', confidence: 94, category: 'financeiro' },
    ],
  },
  {
    id: '3',
    filename: 'rg_funcionario.jpg',
    type: 'image',
    status: 'completed',
    uploadedAt: '2026-01-15T09:15:00',
    processedAt: '2026-01-15T09:15:20',
    confidence: 92.8,
    pages: 1,
    fields: [
      { id: '1', label: 'Nome', value: 'João da Silva Santos', confidence: 95, category: 'pessoal' },
      { id: '2', label: 'RG', value: '12.345.678-9', confidence: 91, category: 'documento' },
      { id: '3', label: 'CPF', value: '123.456.789-00', confidence: 89, category: 'documento' },
    ],
  },
  {
    id: '4',
    filename: 'boleto_vencido.pdf',
    type: 'pdf',
    status: 'processing',
    uploadedAt: '2026-01-16T11:00:00',
    confidence: 0,
    pages: 1,
    fields: [],
  },
  {
    id: '5',
    filename: 'recibo_antigo.jpg',
    type: 'image',
    status: 'error',
    uploadedAt: '2026-01-14T16:30:00',
    confidence: 0,
    pages: 1,
    fields: [],
  },
];

const statusConfig = {
  pending: { label: 'Pendente', color: 'secondary' as const, icon: Clock },
  processing: { label: 'Processando', color: 'warning' as const, icon: RefreshCw },
  completed: { label: 'Concluído', color: 'success' as const, icon: CheckCircle2 },
  error: { label: 'Erro', color: 'danger' as const, icon: AlertCircle },
};

const documentTemplates = [
  { id: 'nf', name: 'Nota Fiscal', fields: ['Número', 'Data', 'Valor', 'CNPJ', 'Razão Social'] },
  { id: 'contrato', name: 'Contrato', fields: ['Partes', 'Valor', 'Vigência', 'Objeto'] },
  { id: 'rg', name: 'RG', fields: ['Nome', 'RG', 'Data Nascimento', 'Filiação'] },
  { id: 'cpf', name: 'CPF', fields: ['Nome', 'CPF', 'Data Nascimento'] },
  { id: 'cnh', name: 'CNH', fields: ['Nome', 'CNH', 'Categoria', 'Validade'] },
  { id: 'boleto', name: 'Boleto', fields: ['Código de Barras', 'Valor', 'Vencimento', 'Beneficiário'] },
];

export function OCRPage() {
  const [documents, setDocuments] = useState(mockDocuments);
  const [selectedDoc, setSelectedDoc] = useState<OCRDocument | null>(null);
  const [activeTab, setActiveTab] = useState('documents');
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  const stats = {
    total: documents.length,
    completed: documents.filter((d) => d.status === 'completed').length,
    processing: documents.filter((d) => d.status === 'processing').length,
    avgConfidence: Math.round(
      documents
        .filter((d) => d.status === 'completed')
        .reduce((sum, d) => sum + d.confidence, 0) /
        documents.filter((d) => d.status === 'completed').length || 0
    ),
  };

  const handleCopyField = useCallback((id: string, value: string) => {
    navigator.clipboard.writeText(value);
    setCopiedField(id);
    setTimeout(() => setCopiedField(null), 2000);
  }, []);

  const handleReprocess = useCallback((id: string) => {
    setDocuments((prev) =>
      prev.map((doc) =>
        doc.id === id ? { ...doc, status: 'processing' as const } : doc
      )
    );
    setTimeout(() => {
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === id ? { ...doc, status: 'completed' as const, confidence: 95 } : doc
        )
      );
    }, 3000);
  }, []);

  const handleDelete = useCallback((id: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  }, []);

  const filteredDocuments = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'image':
        return <FileImage className="w-5 h-5" />;
      case 'pdf':
        return <FileText className="w-5 h-5" />;
      default:
        return <File className="w-5 h-5" />;
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <ScanLine className="w-8 h-8 text-accent-primary" />
              OCR - Reconhecimento Óptico
            </h1>
            <p className="text-text-secondary mt-1">
              Extração automática de dados de documentos com IA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button
              variant="primary"
              leftIcon={<Upload className="w-4 h-4" />}
              onClick={() => setUploadModalOpen(true)}
            >
              Upload Documento
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
              title="Total de Documentos"
              value={stats.total}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Processados"
              value={stats.completed}
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
              title="Em Processamento"
              value={stats.processing}
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
              title="Confiança Média"
              value={`${stats.avgConfidence}%`}
              icon={<Target className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="documents" label="Documentos" />
          <Tab value="templates" label="Templates" />
          <Tab value="history" label="Histórico" />
          <Tab value="settings" label="Configurações" />
        </Tabs>

        {activeTab === 'documents' && (
          <>
            {/* Filters */}
            <Card>
              <CardBody>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                      <Input
                        placeholder="Buscar documentos..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                    Filtros
                  </Button>
                </div>
              </CardBody>
            </Card>

            {/* Documents Table */}
            <Card>
              <CardHeader
                title="Documentos"
                subtitle={`${filteredDocuments.length} documentos`}
              />
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Documento</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Confiança</TableHead>
                    <TableHead>Campos Extraídos</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDocuments.map((doc) => {
                    const statusInfo = statusConfig[doc.status];
                    const StatusIcon = statusInfo.icon;
                    return (
                      <TableRow key={doc.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                              {getTypeIcon(doc.type)}
                            </div>
                            <div>
                              <p className="font-medium text-text-primary text-sm">
                                {doc.filename}
                              </p>
                              <p className="text-xs text-text-muted">
                                {doc.pages} página(s)
                              </p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">
                            {doc.type.toUpperCase()}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={statusInfo.color}
                            leftIcon={
                              <StatusIcon
                                className={`w-3 h-3 ${
                                  doc.status === 'processing' ? 'animate-spin' : ''
                                }`}
                              />
                            }
                          >
                            {statusInfo.label}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {doc.status === 'completed' ? (
                            <div className="flex items-center gap-2">
                              <div className="w-16">
                                <Progress
                                  value={doc.confidence}
                                  color={
                                    doc.confidence >= 90
                                      ? 'success'
                                      : doc.confidence >= 70
                                      ? 'warning'
                                      : 'danger'
                                  }
                                />
                              </div>
                              <span className="text-sm text-text-primary">
                                {doc.confidence}%
                              </span>
                            </div>
                          ) : (
                            <span className="text-sm text-text-muted">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-text-primary">
                            {doc.fields.length} campos
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-text-muted">
                            {new Date(doc.uploadedAt).toLocaleDateString('pt-BR')}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedDoc(doc);
                                setDetailsModalOpen(true);
                              }}
                              disabled={doc.status !== 'completed'}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Dropdown
                              trigger={
                                <Button variant="ghost" size="sm">
                                  <MoreVertical className="w-4 h-4" />
                                </Button>
                              }
                              items={[
                                {
                                  label: 'Reprocessar',
                                  icon: <RefreshCw className="w-4 h-4" />,
                                  onClick: () => handleReprocess(doc.id),
                                },
                                {
                                  label: 'Download',
                                  icon: <Download className="w-4 h-4" />,
                                },
                                {
                                  label: 'Excluir',
                                  icon: <Trash2 className="w-4 h-4" />,
                                  onClick: () => handleDelete(doc.id),
                                },
                              ]}
                            />
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </Card>
          </>
        )}

        {activeTab === 'templates' && (
          <div className="grid grid-cols-3 gap-6">
            {documentTemplates.map((template) => (
              <Card key={template.id} className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                <CardBody>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-text-primary">{template.name}</h3>
                    <Badge variant="secondary">{template.fields.length} campos</Badge>
                  </div>
                  <div className="space-y-2">
                    {template.fields.map((field, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-text-muted">
                        <div className="w-2 h-2 rounded-full bg-accent-primary" />
                        {field}
                      </div>
                    ))}
                  </div>
                  <Button variant="secondary" size="sm" className="w-full mt-4">
                    Usar Template
                  </Button>
                </CardBody>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'history' && (
          <Card>
            <CardHeader title="Histórico de Processamento" />
            <CardBody>
              <div className="space-y-4">
                {documents
                  .filter((d) => d.status === 'completed')
                  .map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 bg-bg-tertiary rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                          <CheckCircle2 className="w-5 h-5 text-green-500" />
                        </div>
                        <div>
                          <p className="font-medium text-text-primary">{doc.filename}</p>
                          <p className="text-sm text-text-muted">
                            {doc.fields.length} campos extraídos • Confiança: {doc.confidence}%
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-text-primary">
                          {new Date(doc.processedAt!).toLocaleDateString('pt-BR')}
                        </p>
                        <p className="text-xs text-text-muted">
                          {new Date(doc.processedAt!).toLocaleTimeString('pt-BR')}
                        </p>
                      </div>
                    </div>
                  ))}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'settings' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Configurações de OCR" />
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-text-primary">
                      Qualidade de Processamento
                    </label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>Alta (mais preciso, mais lento)</option>
                      <option>Média (balanceado)</option>
                      <option>Rápida (menos preciso)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-text-primary">
                      Idioma Principal
                    </label>
                    <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
                      <option>Português (Brasil)</option>
                      <option>English</option>
                      <option>Español</option>
                    </select>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Correção automática de texto</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Detectar campos automaticamente</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-text-primary">Melhorar imagem antes do OCR</span>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Estatísticas" />
              <CardBody>
                <div className="space-y-4">
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted">Documentos processados (mês)</p>
                    <p className="text-2xl font-bold text-text-primary">156</p>
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted">Campos extraídos (mês)</p>
                    <p className="text-2xl font-bold text-text-primary">892</p>
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted">Taxa de sucesso</p>
                    <p className="text-2xl font-bold text-green-500">98.2%</p>
                  </div>
                  <div className="p-4 bg-bg-tertiary rounded-lg">
                    <p className="text-sm text-text-muted">Tempo médio de processamento</p>
                    <p className="text-2xl font-bold text-text-primary">2.3s</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Upload de Documento para OCR"
        size="md"
      >
        <div className="space-y-4">
          <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent-primary transition-colors cursor-pointer">
            <Upload className="w-12 h-12 text-text-muted mx-auto mb-4" />
            <p className="text-text-primary font-medium">Arraste arquivos aqui</p>
            <p className="text-sm text-text-muted mt-1">ou clique para selecionar</p>
            <p className="text-xs text-text-muted mt-2">
              PDF, JPG, PNG (máx. 20MB)
            </p>
          </div>

          <div>
            <label className="text-sm font-medium text-text-primary">
              Template de Extração (opcional)
            </label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary"
            >
              <option value="">Detectar automaticamente</option>
              {documentTemplates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <input type="checkbox" id="enhance" className="rounded" defaultChecked />
            <label htmlFor="enhance" className="text-sm text-text-primary">
              Melhorar qualidade da imagem antes do processamento
            </label>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setUploadModalOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary" leftIcon={<Sparkles className="w-4 h-4" />}>
              Processar com IA
            </Button>
          </div>
        </div>
      </Modal>

      {/* Details Modal */}
      <Modal
        isOpen={detailsModalOpen}
        onClose={() => setDetailsModalOpen(false)}
        title="Dados Extraídos"
        size="lg"
      >
        {selectedDoc && (
          <div className="space-y-6">
            {/* Document Info */}
            <div className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-lg">
              <div className="w-12 h-12 rounded-lg bg-accent-primary/10 flex items-center justify-center">
                {getTypeIcon(selectedDoc.type)}
              </div>
              <div className="flex-1">
                <p className="font-medium text-text-primary">{selectedDoc.filename}</p>
                <p className="text-sm text-text-muted">
                  Processado em{' '}
                  {new Date(selectedDoc.processedAt!).toLocaleString('pt-BR')}
                </p>
              </div>
              <Badge variant="success">Confiança: {selectedDoc.confidence}%</Badge>
            </div>

            {/* Extracted Fields */}
            <div>
              <h4 className="font-medium text-text-primary mb-3">Campos Extraídos</h4>
              <div className="space-y-2">
                {selectedDoc.fields.map((field) => (
                  <div
                    key={field.id}
                    className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <Badge variant="secondary" size="sm">
                        {field.category}
                      </Badge>
                      <span className="text-sm text-text-muted">{field.label}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-text-primary">{field.value}</span>
                      <div className="flex items-center gap-1">
                        <span className="text-xs text-text-muted">{field.confidence}%</span>
                        <button
                          onClick={() => handleCopyField(field.id, field.value)}
                          className="p-1 hover:bg-bg-secondary rounded"
                        >
                          {copiedField === field.id ? (
                            <Check className="w-4 h-4 text-green-500" />
                          ) : (
                            <Copy className="w-4 h-4 text-text-muted" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Raw Text */}
            {selectedDoc.extractedText && (
              <div>
                <h4 className="font-medium text-text-primary mb-3">Texto Extraído</h4>
                <div className="p-4 bg-bg-tertiary rounded-lg">
                  <pre className="text-sm text-text-muted whitespace-pre-wrap font-mono">
                    {selectedDoc.extractedText}
                  </pre>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
                Exportar JSON
              </Button>
              <Button variant="secondary" leftIcon={<Copy className="w-4 h-4" />}>
                Copiar Tudo
              </Button>
              <Button variant="primary" leftIcon={<RefreshCw className="w-4 h-4" />}>
                Reprocessar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </MainLayout>
  );
}

export default OCRPage;
