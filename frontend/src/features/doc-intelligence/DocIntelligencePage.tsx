'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Upload,
  Download,
  Eye,
  Search,
  Filter,
  Zap,
  CheckCircle,
  Clock,
  AlertTriangle,
  XCircle,
  FileImage,
  FileScan,
  Bot,
  Sparkles,
  BarChart3,
  TrendingUp,
  ChevronRight,
  Copy,
  Settings,
  Play,
  RefreshCw
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { SimpleTabBar } from '../../design-system/components/Tabs';
import { MainLayout } from '../../layouts/MainLayout';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts';

// Types
interface ProcessedDocument {
  id: string;
  fileName: string;
  fileType: 'pdf' | 'image' | 'scan';
  documentType: 'invoice' | 'contract' | 'id' | 'receipt' | 'report' | 'other';
  uploadDate: string;
  processedDate: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'review';
  confidence: number | null;
  extractedFields: number;
  fileSize: string;
  processingTime: number | null;
  extractedData: Record<string, unknown> | null;
}

// Mock Data
const mockDocuments: ProcessedDocument[] = [
  {
    id: '1',
    fileName: 'NF_2024_00145.pdf',
    fileType: 'pdf',
    documentType: 'invoice',
    uploadDate: '2024-02-16T14:30:00',
    processedDate: '2024-02-16T14:30:15',
    status: 'completed',
    confidence: 98.5,
    extractedFields: 12,
    fileSize: '245 KB',
    processingTime: 15,
    extractedData: {
      numero: '2024-00145',
      valor: 'R$ 15.850,00',
      emitente: 'Tech Solutions Ltda',
      cnpj: '12.345.678/0001-90',
      data: '16/02/2024'
    }
  },
  {
    id: '2',
    fileName: 'Contrato_Servicos_ABC.pdf',
    fileType: 'pdf',
    documentType: 'contract',
    uploadDate: '2024-02-16T11:20:00',
    processedDate: '2024-02-16T11:20:45',
    status: 'completed',
    confidence: 95.2,
    extractedFields: 18,
    fileSize: '1.2 MB',
    processingTime: 45,
    extractedData: {
      tipo: 'Prestação de Serviços',
      partes: ['Empresa ABC', 'Empresa XYZ'],
      valor: 'R$ 120.000,00/ano',
      vigencia: '01/03/2024 - 28/02/2025'
    }
  },
  {
    id: '3',
    fileName: 'RG_Funcionario_Scan.jpg',
    fileType: 'image',
    documentType: 'id',
    uploadDate: '2024-02-16T10:15:00',
    processedDate: '2024-02-16T10:15:08',
    status: 'review',
    confidence: 87.3,
    extractedFields: 8,
    fileSize: '890 KB',
    processingTime: 8,
    extractedData: {
      nome: 'João da Silva Santos',
      rg: '12.345.678-9',
      nascimento: '15/03/1985'
    }
  },
  {
    id: '4',
    fileName: 'Recibo_Pagamento.pdf',
    fileType: 'pdf',
    documentType: 'receipt',
    uploadDate: '2024-02-16T09:45:00',
    processedDate: null,
    status: 'processing',
    confidence: null,
    extractedFields: 0,
    fileSize: '156 KB',
    processingTime: null,
    extractedData: null
  },
  {
    id: '5',
    fileName: 'Documento_Ilegivel.pdf',
    fileType: 'scan',
    documentType: 'other',
    uploadDate: '2024-02-15T16:30:00',
    processedDate: '2024-02-15T16:31:20',
    status: 'failed',
    confidence: 32.1,
    extractedFields: 0,
    fileSize: '2.1 MB',
    processingTime: 80,
    extractedData: null
  }
];

const processingTrendData = [
  { date: '10/02', documents: 45, success: 42 },
  { date: '11/02', documents: 52, success: 50 },
  { date: '12/02', documents: 38, success: 36 },
  { date: '13/02', documents: 65, success: 63 },
  { date: '14/02', documents: 48, success: 46 },
  { date: '15/02', documents: 55, success: 52 },
  { date: '16/02', documents: 35, success: 33 }
];

const documentTypeDistribution = [
  { name: 'Notas Fiscais', value: 40, color: '#6366f1' },
  { name: 'Contratos', value: 25, color: '#10b981' },
  { name: 'Documentos ID', value: 15, color: '#f59e0b' },
  { name: 'Recibos', value: 12, color: '#8b5cf6' },
  { name: 'Outros', value: 8, color: '#3b82f6' }
];

const confidenceDistribution = [
  { range: '90-100%', count: 145 },
  { range: '80-90%', count: 45 },
  { range: '70-80%', count: 18 },
  { range: '< 70%', count: 8 }
];

const tabs = [
  { value: 'all', label: 'Todos', icon: <FileText className="h-4 w-4" /> },
  { value: 'completed', label: 'Processados', icon: <CheckCircle className="h-4 w-4" /> },
  { value: 'processing', label: 'Em Processamento', icon: <Clock className="h-4 w-4" /> },
  { value: 'review', label: 'Revisão', icon: <AlertTriangle className="h-4 w-4" /> }
];

export function DocIntelligencePage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<ProcessedDocument | null>(null);

  const getDocumentTypeInfo = (type: ProcessedDocument['documentType']) => {
    const types = {
      invoice: { label: 'Nota Fiscal', color: 'primary' as const },
      contract: { label: 'Contrato', color: 'success' as const },
      id: { label: 'Documento ID', color: 'warning' as const },
      receipt: { label: 'Recibo', color: 'info' as const },
      report: { label: 'Relatório', color: 'info' as const },
      other: { label: 'Outro', color: 'info' as const }
    };
    return types[type];
  };

  const getStatusInfo = (status: ProcessedDocument['status']) => {
    const statuses = {
      pending: { label: 'Pendente', color: 'info' as const, icon: Clock },
      processing: { label: 'Processando', color: 'info' as const, icon: RefreshCw },
      completed: { label: 'Concluído', color: 'success' as const, icon: CheckCircle },
      failed: { label: 'Falhou', color: 'danger' as const, icon: XCircle },
      review: { label: 'Revisão', color: 'warning' as const, icon: AlertTriangle }
    };
    return statuses[status];
  };

  const getFileIcon = (type: ProcessedDocument['fileType']) => {
    const icons = {
      pdf: FileText,
      image: FileImage,
      scan: FileScan
    };
    return icons[type];
  };

  const getConfidenceColor = (confidence: number | null) => {
    if (confidence === null) return 'text-text-secondary';
    if (confidence >= 90) return 'text-accent-success';
    if (confidence >= 75) return 'text-accent-warning';
    return 'text-accent-danger';
  };

  const handleViewDetails = (doc: ProcessedDocument) => {
    setSelectedDocument(doc);
    setShowDetailModal(true);
  };

  const filteredDocuments = mockDocuments.filter(doc => {
    const matchesSearch = doc.fileName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === 'all' || doc.status === activeTab;
    return matchesSearch && matchesTab;
  });

  const completedDocs = mockDocuments.filter(d => d.status === 'completed').length;
  const avgConfidence = mockDocuments
    .filter(d => d.confidence !== null)
    .reduce((sum, d) => sum + (d.confidence || 0), 0) / mockDocuments.filter(d => d.confidence !== null).length;
  const totalFields = mockDocuments.reduce((sum, d) => sum + d.extractedFields, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-accent-primary" />
              Document Intelligence
            </h1>
            <p className="text-text-secondary mt-1">
              OCR e extração inteligente de dados de documentos
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Templates
            </Button>
            <Button variant="primary" onClick={() => setShowUploadModal(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Processar Documento
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={5}>
          <StatCard
            title="Documentos Processados"
            value={completedDocs.toString()}
            change={12}
            changeLabel="esta semana"
            icon={<FileText className="h-5 w-5" />}
          />
          <StatCard
            title="Taxa de Sucesso"
            value="94.8%"
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Confiança Média"
            value={`${avgConfidence.toFixed(1)}%`}
            icon={<Bot className="h-5 w-5" />}
            iconColor="primary"
          />
          <StatCard
            title="Campos Extraídos"
            value={totalFields.toString()}
            changeLabel="esta semana"
            icon={<Zap className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Tempo Médio"
            value="18s"
            changeLabel="por documento"
            icon={<Clock className="h-5 w-5" />}
          />
        </StatGrid>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Processing Trend */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Documentos Processados (7 dias)
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={processingTrendData}>
                    <defs>
                      <linearGradient id="colorDocs" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="documents"
                      name="Total"
                      stroke="#6366f1"
                      fillOpacity={1}
                      fill="url(#colorDocs)"
                    />
                    <Area
                      type="monotone"
                      dataKey="success"
                      name="Sucesso"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* Document Type Distribution */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-text-primary">
                Por Tipo
              </h3>
            </CardHeader>
            <CardBody>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={documentTypeDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={60}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {documentTypeDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a2e',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-2">
                {documentTypeDistribution.map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-text-secondary">{item.name}</span>
                    </div>
                    <span className="text-text-primary font-medium">{item.value}%</span>
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Confidence Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-text-primary">
              Distribuição de Confiança
            </h3>
          </CardHeader>
          <CardBody>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={confidenceDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                  <XAxis dataKey="range" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a1a2e',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="count" name="Documentos" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardBody>
        </Card>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Documents List */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">
                Documentos
              </h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
                <Input
                  placeholder="Buscar documentos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </CardHeader>
          <CardBody className="space-y-3">
            {filteredDocuments.map((doc, index) => {
              const statusInfo = getStatusInfo(doc.status);
              const typeInfo = getDocumentTypeInfo(doc.documentType);
              const FileIcon = getFileIcon(doc.fileType);
              const StatusIcon = statusInfo.icon;
              return (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 bg-bg-tertiary rounded-xl hover:bg-bg-hover transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-xl bg-accent-${statusInfo.color}/20`}>
                        <FileIcon className={`h-6 w-6 text-accent-${statusInfo.color}`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-text-primary">{doc.fileName}</h4>
                          <Badge variant={statusInfo.color} size="sm">
                            {statusInfo.label}
                          </Badge>
                          <Badge variant={typeInfo.color} size="sm">
                            {typeInfo.label}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-xs text-text-secondary">
                          <span>{doc.fileSize}</span>
                          <span>Upload: {new Date(doc.uploadDate).toLocaleString('pt-BR')}</span>
                          {doc.processingTime && <span>Tempo: {doc.processingTime}s</span>}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      {doc.confidence !== null && (
                        <div className="text-right">
                          <p className="text-sm text-text-secondary">Confiança</p>
                          <p className={`text-xl font-bold ${getConfidenceColor(doc.confidence)}`}>
                            {doc.confidence.toFixed(1)}%
                          </p>
                        </div>
                      )}
                      <div className="text-right">
                        <p className="text-sm text-text-secondary">Campos</p>
                        <p className="text-xl font-bold text-text-primary">
                          {doc.extractedFields}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => handleViewDetails(doc)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        {doc.status === 'completed' && (
                          <>
                            <Button variant="ghost" size="sm">
                              <Copy className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                        {doc.status === 'failed' && (
                          <Button variant="ghost" size="sm">
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Extracted Data Preview */}
                  {doc.status === 'completed' && doc.extractedData && (
                    <div className="mt-4 p-3 bg-bg-secondary rounded-lg">
                      <p className="text-xs text-text-secondary mb-2">Dados Extraídos (prévia)</p>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        {Object.entries(doc.extractedData).slice(0, 4).map(([key, value]) => (
                          <div key={key}>
                            <p className="text-text-secondary capitalize">{key}</p>
                            <p className="text-text-primary font-medium truncate">{String(value)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              );
            })}
          </CardBody>
        </Card>

        {/* Upload Modal */}
        <Modal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          title="Processar Documento"
          size="md"
        >
          <div className="space-y-4">
            <div className="border-2 border-dashed border-border-default rounded-xl p-8 text-center hover:border-accent-primary/50 transition-colors cursor-pointer">
              <Upload className="h-12 w-12 text-text-secondary mx-auto mb-3" />
              <p className="text-text-primary font-medium">
                Clique para selecionar ou arraste o documento
              </p>
              <p className="text-sm text-text-secondary mt-1">
                PDF, JPG, PNG (máx. 25MB)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Tipo de Documento
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Detectar automaticamente</option>
                <option value="invoice">Nota Fiscal</option>
                <option value="contract">Contrato</option>
                <option value="id">Documento de Identificação</option>
                <option value="receipt">Recibo</option>
                <option value="other">Outro</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Template de Extração
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Usar IA para extração</option>
                <option value="nfe">Nota Fiscal Eletrônica</option>
                <option value="contract_services">Contrato de Serviços</option>
                <option value="rg">RG</option>
                <option value="cnpj">Cartão CNPJ</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input type="checkbox" id="autoValidate" className="rounded border-border-default" />
              <label htmlFor="autoValidate" className="text-sm text-text-primary">
                Validar dados automaticamente
              </label>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="ghost" onClick={() => setShowUploadModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                <Play className="h-4 w-4 mr-2" />
                Processar
              </Button>
            </div>
          </div>
        </Modal>

        {/* Detail Modal */}
        <Modal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title={`Detalhes: ${selectedDocument?.fileName}`}
          size="lg"
        >
          {selectedDocument && (
            <div className="space-y-6">
              {/* Document Info */}
              <div className="grid grid-cols-3 gap-4 p-4 bg-bg-tertiary rounded-lg">
                <div>
                  <p className="text-sm text-text-secondary">Status</p>
                  <Badge variant={getStatusInfo(selectedDocument.status).color}>
                    {getStatusInfo(selectedDocument.status).label}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Confiança</p>
                  <p className={`font-bold ${getConfidenceColor(selectedDocument.confidence)}`}>
                    {selectedDocument.confidence?.toFixed(1) || '-'}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-text-secondary">Tempo de Processamento</p>
                  <p className="font-semibold text-text-primary">
                    {selectedDocument.processingTime || '-'}s
                  </p>
                </div>
              </div>

              {/* Extracted Data */}
              {selectedDocument.extractedData && (
                <div>
                  <h4 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-accent-primary" />
                    Dados Extraídos
                  </h4>
                  <div className="bg-bg-tertiary rounded-lg overflow-hidden">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-border-subtle">
                          <th className="text-left p-3 text-sm text-text-secondary">Campo</th>
                          <th className="text-left p-3 text-sm text-text-secondary">Valor</th>
                          <th className="text-right p-3 text-sm text-text-secondary">Ações</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(selectedDocument.extractedData).map(([key, value]) => (
                          <tr key={key} className="border-b border-border-subtle last:border-0">
                            <td className="p-3 text-text-secondary capitalize">{key}</td>
                            <td className="p-3 text-text-primary font-medium">{String(value)}</td>
                            <td className="p-3 text-right">
                              <Button variant="ghost" size="sm">
                                <Copy className="h-3 w-3" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3">
                <Button variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reprocessar
                </Button>
                <Button variant="outline">
                  <Copy className="h-4 w-4 mr-2" />
                  Copiar JSON
                </Button>
                <Button variant="primary">
                  <Download className="h-4 w-4 mr-2" />
                  Exportar Dados
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}

export default DocIntelligencePage;
