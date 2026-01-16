'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  type Column,
  Modal
} from '@/design-system/components';
import {
  FileText,
  Upload,
  Brain,
  Search,
  CheckCircle,
  Clock,
  AlertTriangle,
  Eye,
  Download,
  Trash2,
  Filter,
  FileImage,
  File,
  FileSpreadsheet,
  Zap,
  Target,
  BarChart2,
  RefreshCw
} from 'lucide-react';
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
  Legend
} from 'recharts';

interface DocumentAnalysis {
  id: string;
  fileName: string;
  fileType: 'pdf' | 'image' | 'excel' | 'word';
  status: 'completed' | 'processing' | 'pending' | 'error';
  documentType: string;
  confidence: number;
  extractedData: number;
  uploadDate: string;
  processTime: string;
  size: string;
}

const mockDocuments: DocumentAnalysis[] = [
  {
    id: '1',
    fileName: 'contrato_servicos_2024.pdf',
    fileType: 'pdf',
    status: 'completed',
    documentType: 'Contrato de Serviços',
    confidence: 98.5,
    extractedData: 42,
    uploadDate: '2024-01-15 14:30',
    processTime: '2.3s',
    size: '2.4 MB'
  },
  {
    id: '2',
    fileName: 'nota_fiscal_000123.pdf',
    fileType: 'pdf',
    status: 'completed',
    documentType: 'Nota Fiscal',
    confidence: 99.2,
    extractedData: 28,
    uploadDate: '2024-01-15 14:25',
    processTime: '1.8s',
    size: '856 KB'
  },
  {
    id: '3',
    fileName: 'rg_colaborador.jpg',
    fileType: 'image',
    status: 'processing',
    documentType: 'RG',
    confidence: 0,
    extractedData: 0,
    uploadDate: '2024-01-15 14:35',
    processTime: '-',
    size: '1.2 MB'
  },
  {
    id: '4',
    fileName: 'planilha_custos.xlsx',
    fileType: 'excel',
    status: 'completed',
    documentType: 'Planilha Financeira',
    confidence: 95.8,
    extractedData: 156,
    uploadDate: '2024-01-15 14:20',
    processTime: '4.5s',
    size: '3.1 MB'
  },
  {
    id: '5',
    fileName: 'proposta_comercial.docx',
    fileType: 'word',
    status: 'error',
    documentType: 'Proposta Comercial',
    confidence: 0,
    extractedData: 0,
    uploadDate: '2024-01-15 14:15',
    processTime: '-',
    size: '1.8 MB'
  },
  {
    id: '6',
    fileName: 'ctps_funcionario.pdf',
    fileType: 'pdf',
    status: 'pending',
    documentType: 'CTPS',
    confidence: 0,
    extractedData: 0,
    uploadDate: '2024-01-15 14:40',
    processTime: '-',
    size: '950 KB'
  }
];

const mockStats = [
  { name: 'Contratos', value: 234 },
  { name: 'Notas Fiscais', value: 1256 },
  { name: 'Documentos RH', value: 892 },
  { name: 'Propostas', value: 156 },
  { name: 'Outros', value: 423 }
];

const COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#64748b'];

const mockAccuracyData = [
  { type: 'Contratos', accuracy: 98.2 },
  { type: 'NF-e', accuracy: 99.5 },
  { type: 'RG/CPF', accuracy: 97.8 },
  { type: 'CTPS', accuracy: 96.5 },
  { type: 'Planilhas', accuracy: 95.2 }
];

const tabs = [
  { value: 'upload', label: 'Upload & Análise', icon: <Upload className="h-4 w-4" /> },
  { value: 'history', label: 'Histórico', icon: <FileText className="h-4 w-4" /> },
  { value: 'templates', label: 'Templates', icon: <Target className="h-4 w-4" /> },
  { value: 'stats', label: 'Estatísticas', icon: <BarChart2 className="h-4 w-4" /> }
];

export function AIDocumentAnalysisPage() {
  const [activeTab, setActiveTab] = useState('upload');
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<DocumentAnalysis | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    // Handle file upload
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf': return <FileText className="h-5 w-5 text-red-400" />;
      case 'image': return <FileImage className="h-5 w-5 text-blue-400" />;
      case 'excel': return <FileSpreadsheet className="h-5 w-5 text-green-400" />;
      case 'word': return <File className="h-5 w-5 text-blue-400" />;
      default: return <File className="h-5 w-5 text-gray-400" />;
    }
  };

  const columns: Column<DocumentAnalysis>[] = [
    {
      key: 'fileName',
      header: 'Documento',
      render: (doc) => (
        <div className="flex items-center gap-3">
          {getFileIcon(doc.fileType)}
          <div>
            <span className="font-medium text-text-primary">{doc.fileName}</span>
            <p className="text-sm text-text-secondary">{doc.size}</p>
          </div>
        </div>
      )
    },
    {
      key: 'documentType',
      header: 'Tipo Detectado',
      render: (doc) => (
        <span className="text-text-primary">{doc.documentType || '-'}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (doc) => (
        <Badge variant={
          doc.status === 'completed' ? 'success' :
          doc.status === 'processing' ? 'primary' :
          doc.status === 'pending' ? 'info' : 'danger'
        }>
          <span className="flex items-center gap-1">
            {doc.status === 'completed' && <CheckCircle className="h-3 w-3" />}
            {doc.status === 'processing' && <RefreshCw className="h-3 w-3 animate-spin" />}
            {doc.status === 'pending' && <Clock className="h-3 w-3" />}
            {doc.status === 'error' && <AlertTriangle className="h-3 w-3" />}
            {doc.status === 'completed' ? 'Concluído' :
             doc.status === 'processing' ? 'Processando' :
             doc.status === 'pending' ? 'Pendente' : 'Erro'}
          </span>
        </Badge>
      )
    },
    {
      key: 'confidence',
      header: 'Confiança',
      render: (doc) => doc.confidence > 0 ? (
        <div className="flex items-center gap-2">
          <div className="w-16 bg-bg-primary rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                doc.confidence >= 95 ? 'bg-green-500' :
                doc.confidence >= 85 ? 'bg-amber-500' : 'bg-red-500'
              }`}
              style={{ width: `${doc.confidence}%` }}
            />
          </div>
          <span className="text-sm text-text-primary">{doc.confidence}%</span>
        </div>
      ) : <span className="text-text-secondary">-</span>
    },
    {
      key: 'extractedData',
      header: 'Dados Extraídos',
      render: (doc) => (
        <span className="text-text-primary">
          {doc.extractedData > 0 ? `${doc.extractedData} campos` : '-'}
        </span>
      )
    },
    {
      key: 'processTime',
      header: 'Tempo',
      render: (doc) => (
        <span className="text-text-secondary">{doc.processTime}</span>
      )
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (doc) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedDoc(doc);
              setShowPreviewModal(true);
            }}
            disabled={doc.status !== 'completed'}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" disabled={doc.status !== 'completed'}>
            <Download className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Trash2 className="h-4 w-4 text-red-400" />
          </Button>
        </div>
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">Análise de Documentos com IA</h1>
            <p className="text-text-secondary mt-1">OCR inteligente e extração automática de dados</p>
          </div>
          <div className="flex items-center gap-3">
            {
            <div className="flex items-center gap-3">
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtrar
              </Button>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload
              </Button>
            </div>
          }
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Documentos Processados"
            value="2.961"
            icon={<FileText className="h-5 w-5" />}
            iconColor="primary"
            change={156}
            changeLabel="este mês"
          />
          <StatCard
            title="Taxa de Precisão"
            value="97.8%"
            icon={<Target className="h-5 w-5" />}
            iconColor="success"
            change={1.2}
            changeLabel="vs mês anterior"
          />
          <StatCard
            title="Tempo Médio"
            value="2.8s"
            icon={<Zap className="h-5 w-5" />}
            iconColor="warning"
            change={-15}
            changeLabel="mais rápido"
          />
          <StatCard
            title="Dados Extraídos"
            value="48.2K"
            icon={<Brain className="h-5 w-5" />}
            iconColor="info"
            change={8.5}
            changeLabel="campos"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Content */}
        {activeTab === 'upload' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Upload Zone */}
            <Card className="lg:col-span-2 p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Upload de Documentos
              </h3>
              <div
                className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
                  dragActive
                    ? 'border-accent-primary bg-accent-primary/5'
                    : 'border-border-default hover:border-accent-primary/50'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className="flex flex-col items-center">
                  <div className="p-4 bg-accent-primary/10 rounded-full mb-4">
                    <Upload className="h-8 w-8 text-accent-primary" />
                  </div>
                  <h4 className="font-medium text-text-primary mb-2">
                    Arraste documentos aqui
                  </h4>
                  <p className="text-text-secondary text-sm mb-4">
                    ou clique para selecionar arquivos
                  </p>
                  <Button>
                    Selecionar Arquivos
                  </Button>
                  <p className="text-text-secondary text-xs mt-4">
                    Suporta: PDF, JPG, PNG, XLSX, DOCX (máx. 25MB)
                  </p>
                </div>
              </div>

              {/* Processing Queue */}
              <div className="mt-6">
                <h4 className="font-medium text-text-primary mb-3">
                  Fila de Processamento
                </h4>
                <div className="space-y-3">
                  {mockDocuments.filter(d => d.status !== 'completed').map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center gap-3">
                        {getFileIcon(doc.fileType)}
                        <div>
                          <span className="text-text-primary text-sm">{doc.fileName}</span>
                          <p className="text-xs text-text-secondary">{doc.size}</p>
                        </div>
                      </div>
                      <Badge variant={
                        doc.status === 'processing' ? 'primary' :
                        doc.status === 'pending' ? 'info' : 'danger'
                      }>
                        {doc.status === 'processing' ? 'Processando...' :
                         doc.status === 'pending' ? 'Na fila' : 'Erro'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            {/* Recent Results */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Últimas Análises
              </h3>
              <div className="space-y-4">
                {mockDocuments.filter(d => d.status === 'completed').slice(0, 4).map((doc) => (
                  <div key={doc.id} className="p-3 bg-bg-tertiary rounded-lg">
                    <div className="flex items-center gap-3 mb-2">
                      {getFileIcon(doc.fileType)}
                      <span className="text-text-primary text-sm font-medium truncate">
                        {doc.fileName}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-text-secondary">{doc.documentType}</span>
                      <span className="text-green-400">{doc.confidence}% precisão</span>
                    </div>
                    <div className="text-xs text-text-secondary mt-1">
                      {doc.extractedData} campos extraídos
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'history' && (
          <Card className="p-6">
            <DataTable<DocumentAnalysis>
              data={mockDocuments}
              columns={columns}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {activeTab === 'templates' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { name: 'Nota Fiscal Eletrônica', fields: 28, accuracy: 99.5, icon: FileText },
              { name: 'Contrato de Serviços', fields: 42, accuracy: 98.2, icon: File },
              { name: 'RG / CPF', fields: 12, accuracy: 97.8, icon: FileImage },
              { name: 'CTPS', fields: 18, accuracy: 96.5, icon: FileText },
              { name: 'Proposta Comercial', fields: 35, accuracy: 95.8, icon: File },
              { name: 'Planilha de Custos', fields: 50, accuracy: 95.2, icon: FileSpreadsheet }
            ].map((template, idx) => (
              <Card key={idx} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-accent-primary/10 rounded-lg">
                    <template.icon className="h-6 w-6 text-accent-primary" />
                  </div>
                  <Badge variant="success">{template.accuracy}%</Badge>
                </div>
                <h3 className="font-semibold text-text-primary">{template.name}</h3>
                <p className="text-sm text-text-secondary mt-1">
                  {template.fields} campos configurados
                </p>
                <div className="mt-4 pt-4 border-t border-border-subtle flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Editar
                  </Button>
                  <Button size="sm" className="flex-1">
                    Testar
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Documentos por Tipo
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={mockStats}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {mockStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Precisão por Tipo
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={mockAccuracyData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" />
                  <XAxis type="number" domain={[90, 100]} stroke="#64748b" />
                  <YAxis dataKey="type" type="category" stroke="#64748b" width={80} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#12121a',
                      border: '1px solid #2d2d3d',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="accuracy" fill="#6366f1" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )}

        {/* Preview Modal */}
        <Modal
          isOpen={showPreviewModal}
          onClose={() => setShowPreviewModal(false)}
          title="Dados Extraídos"
        >
          {selectedDoc && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-bg-tertiary rounded-lg">
                {getFileIcon(selectedDoc.fileType)}
                <div>
                  <span className="font-medium text-text-primary">{selectedDoc.fileName}</span>
                  <p className="text-sm text-text-secondary">{selectedDoc.documentType}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-secondary text-sm">Confiança</span>
                  <p className="text-lg font-semibold text-green-400">{selectedDoc.confidence}%</p>
                </div>
                <div className="p-3 bg-bg-tertiary rounded-lg">
                  <span className="text-text-secondary text-sm">Campos</span>
                  <p className="text-lg font-semibold text-text-primary">{selectedDoc.extractedData}</p>
                </div>
              </div>

              <div className="border border-border-default rounded-lg overflow-hidden">
                <div className="bg-bg-tertiary px-4 py-2 border-b border-border-default">
                  <span className="font-medium text-text-primary">Campos Extraídos</span>
                </div>
                <div className="divide-y divide-border-subtle">
                  {[
                    { label: 'CNPJ Emitente', value: '12.345.678/0001-90' },
                    { label: 'Razão Social', value: 'Empresa Exemplo LTDA' },
                    { label: 'Valor Total', value: 'R$ 15.890,00' },
                    { label: 'Data Emissão', value: '15/01/2024' },
                    { label: 'Número NF', value: '000123' }
                  ].map((field, idx) => (
                    <div key={idx} className="flex justify-between px-4 py-2">
                      <span className="text-text-secondary">{field.label}</span>
                      <span className="text-text-primary font-medium">{field.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowPreviewModal(false)}>
                  Fechar
                </Button>
                <Button>
                  <Download className="h-4 w-4 mr-2" />
                  Exportar JSON
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}
