'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Download,
  Upload,
  Eye,
  Search,
  Filter,
  Folder,
  File,
  Image,
  FileCheck,
  Clock,
  AlertTriangle,
  CheckCircle,
  Plus,
  Calendar,
  User,
  Shield
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../../design-system/components/Card';
import { Button } from '../../design-system/components/Button';
import { Input } from '../../design-system/components/Input';
import { Badge } from '../../design-system/components/Badge';
import { Modal } from '../../design-system/components/Modal';
import { StatCard, StatGrid } from '../../design-system/components/StatCard';
import { SimpleTabBar } from '../../design-system/components/Tabs';
import { MainLayout } from '../../layouts/MainLayout';

// Types
interface Document {
  id: string;
  name: string;
  category: 'personal' | 'contract' | 'payroll' | 'training' | 'other';
  type: 'pdf' | 'image' | 'doc' | 'other';
  size: string;
  uploadDate: string;
  expirationDate: string | null;
  status: 'valid' | 'expiring' | 'expired' | 'pending';
  required: boolean;
  downloadable: boolean;
}

// Mock Data
const mockDocuments: Document[] = [
  {
    id: '1',
    name: 'Contrato de Trabalho',
    category: 'contract',
    type: 'pdf',
    size: '245 KB',
    uploadDate: '2021-03-15',
    expirationDate: null,
    status: 'valid',
    required: true,
    downloadable: true
  },
  {
    id: '2',
    name: 'RG (Frente e Verso)',
    category: 'personal',
    type: 'image',
    size: '1.2 MB',
    uploadDate: '2021-03-15',
    expirationDate: null,
    status: 'valid',
    required: true,
    downloadable: false
  },
  {
    id: '3',
    name: 'CPF',
    category: 'personal',
    type: 'pdf',
    size: '156 KB',
    uploadDate: '2021-03-15',
    expirationDate: null,
    status: 'valid',
    required: true,
    downloadable: false
  },
  {
    id: '4',
    name: 'Comprovante de Residência',
    category: 'personal',
    type: 'pdf',
    size: '890 KB',
    uploadDate: '2024-01-10',
    expirationDate: '2024-04-10',
    status: 'expiring',
    required: true,
    downloadable: false
  },
  {
    id: '5',
    name: 'Certificado NR-10',
    category: 'training',
    type: 'pdf',
    size: '1.5 MB',
    uploadDate: '2023-06-15',
    expirationDate: '2025-06-15',
    status: 'valid',
    required: false,
    downloadable: true
  },
  {
    id: '6',
    name: 'Termo de Confidencialidade',
    category: 'contract',
    type: 'pdf',
    size: '320 KB',
    uploadDate: '2021-03-15',
    expirationDate: null,
    status: 'valid',
    required: true,
    downloadable: true
  },
  {
    id: '7',
    name: 'Carteira de Trabalho Digital',
    category: 'personal',
    type: 'pdf',
    size: '2.1 MB',
    uploadDate: '2024-01-20',
    expirationDate: null,
    status: 'valid',
    required: true,
    downloadable: true
  },
  {
    id: '8',
    name: 'Declaração de Dependentes IR',
    category: 'payroll',
    type: 'pdf',
    size: '180 KB',
    uploadDate: '2023-02-28',
    expirationDate: '2024-02-28',
    status: 'expired',
    required: true,
    downloadable: false
  }
];

const requiredDocuments = [
  { name: 'Comprovante de Residência Atualizado', dueDate: '2024-04-10', status: 'expiring' },
  { name: 'Declaração de Dependentes IR 2024', dueDate: '2024-02-28', status: 'expired' }
];

const tabs = [
  { value: 'all', label: 'Todos', icon: <FileText className="h-4 w-4" /> },
  { value: 'personal', label: 'Pessoais', icon: <User className="h-4 w-4" /> },
  { value: 'contract', label: 'Contratuais', icon: <FileCheck className="h-4 w-4" /> },
  { value: 'training', label: 'Treinamentos', icon: <Shield className="h-4 w-4" /> }
];

export function DocumentsPage() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);

  const getCategoryInfo = (category: Document['category']) => {
    const categories = {
      personal: { label: 'Pessoal', color: 'primary' as const },
      contract: { label: 'Contratual', color: 'info' as const },
      payroll: { label: 'Folha', color: 'success' as const },
      training: { label: 'Treinamento', color: 'warning' as const },
      other: { label: 'Outro', color: 'info' as const }
    };
    return categories[category];
  };

  const getStatusInfo = (status: Document['status']) => {
    const statuses = {
      valid: { label: 'Válido', color: 'success' as const, icon: CheckCircle },
      expiring: { label: 'Vencendo', color: 'warning' as const, icon: Clock },
      expired: { label: 'Vencido', color: 'danger' as const, icon: AlertTriangle },
      pending: { label: 'Pendente', color: 'info' as const, icon: Clock }
    };
    return statuses[status];
  };

  const getFileIcon = (type: Document['type']) => {
    const icons = {
      pdf: FileText,
      image: Image,
      doc: File,
      other: File
    };
    return icons[type];
  };

  const filteredDocuments = mockDocuments.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = activeTab === 'all' || doc.category === activeTab;
    return matchesSearch && matchesTab;
  });

  const validCount = mockDocuments.filter(d => d.status === 'valid').length;
  const expiringCount = mockDocuments.filter(d => d.status === 'expiring').length;
  const expiredCount = mockDocuments.filter(d => d.status === 'expired').length;

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Meus Documentos
            </h1>
            <p className="text-text-secondary mt-1">
              Documentos pessoais e contratuais
            </p>
          </div>
          <Button variant="primary" onClick={() => setShowUploadModal(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Enviar Documento
          </Button>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <StatCard
            title="Total de Documentos"
            value={mockDocuments.length.toString()}
            icon={<FileText className="h-5 w-5" />}
          />
          <StatCard
            title="Válidos"
            value={validCount.toString()}
            icon={<CheckCircle className="h-5 w-5" />}
            iconColor="success"
          />
          <StatCard
            title="Vencendo"
            value={expiringCount.toString()}
            changeLabel="próximos 30 dias"
            icon={<Clock className="h-5 w-5" />}
            iconColor="warning"
          />
          <StatCard
            title="Vencidos"
            value={expiredCount.toString()}
            changeLabel="necessitam atualização"
            icon={<AlertTriangle className="h-5 w-5" />}
            iconColor="danger"
          />
        </StatGrid>

        {/* Pending Documents Alert */}
        {requiredDocuments.filter(d => d.status === 'expired' || d.status === 'expiring').length > 0 && (
          <Card className="border-accent-warning/30 bg-accent-warning/5">
            <CardHeader>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-accent-warning" />
                <h3 className="text-lg font-semibold text-text-primary">
                  Documentos Pendentes
                </h3>
              </div>
            </CardHeader>
            <CardBody className="space-y-3">
              {requiredDocuments.map((doc, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${doc.status === 'expired' ? 'bg-accent-danger/20' : 'bg-accent-warning/20'}`}>
                      <FileText className={`h-4 w-4 ${doc.status === 'expired' ? 'text-accent-danger' : 'text-accent-warning'}`} />
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">{doc.name}</p>
                      <p className="text-xs text-text-secondary">
                        {doc.status === 'expired' ? 'Vencido em' : 'Vence em'} {new Date(doc.dueDate).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setShowUploadModal(true)}>
                    <Upload className="h-4 w-4 mr-2" />
                    Atualizar
                  </Button>
                </div>
              ))}
            </CardBody>
          </Card>
        )}

        {/* Tabs */}
        <SimpleTabBar
          tabs={tabs}
          value={activeTab}
          onChange={setActiveTab}
        />

        {/* Search */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
            <Input
              placeholder="Buscar documentos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Documents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map((doc, index) => {
            const categoryInfo = getCategoryInfo(doc.category);
            const statusInfo = getStatusInfo(doc.status);
            const FileIcon = getFileIcon(doc.type);
            const StatusIcon = statusInfo.icon;

            return (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                  <CardBody>
                    <div className="flex items-start gap-3">
                      <div className={`p-3 rounded-xl bg-accent-${categoryInfo.color}/20`}>
                        <FileIcon className={`h-6 w-6 text-accent-${categoryInfo.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-text-primary truncate">{doc.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant={categoryInfo.color} size="sm">
                            {categoryInfo.label}
                          </Badge>
                          <Badge variant={statusInfo.color} size="sm">
                            {statusInfo.label}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 mt-2 text-xs text-text-secondary">
                          <span>{doc.size}</span>
                          <span>•</span>
                          <span>Enviado em {new Date(doc.uploadDate).toLocaleDateString('pt-BR')}</span>
                        </div>
                        {doc.expirationDate && (
                          <p className={`text-xs mt-1 ${
                            doc.status === 'expired' ? 'text-accent-danger' :
                            doc.status === 'expiring' ? 'text-accent-warning' :
                            'text-text-secondary'
                          }`}>
                            {doc.status === 'expired' ? 'Venceu' : 'Vence'} em {new Date(doc.expirationDate).toLocaleDateString('pt-BR')}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border-subtle">
                      <Button variant="ghost" size="sm" className="flex-1">
                        <Eye className="h-4 w-4 mr-2" />
                        Visualizar
                      </Button>
                      {doc.downloadable && (
                        <Button variant="ghost" size="sm" className="flex-1">
                          <Download className="h-4 w-4 mr-2" />
                          Baixar
                        </Button>
                      )}
                    </div>
                  </CardBody>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Upload Modal */}
        <Modal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          title="Enviar Documento"
          size="md"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Tipo de Documento *
              </label>
              <select className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary">
                <option value="">Selecione...</option>
                <option value="personal">Documento Pessoal</option>
                <option value="address">Comprovante de Residência</option>
                <option value="training">Certificado de Treinamento</option>
                <option value="ir">Declaração IR</option>
                <option value="other">Outro</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nome do Documento *
              </label>
              <Input placeholder="Ex: Comprovante de Residência - Janeiro 2024" />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Arquivo *
              </label>
              <div className="border-2 border-dashed border-border-default rounded-lg p-8 text-center hover:border-accent-primary/50 transition-colors cursor-pointer">
                <Upload className="h-10 w-10 text-text-secondary mx-auto mb-3" />
                <p className="text-text-primary font-medium">
                  Clique para selecionar ou arraste o arquivo
                </p>
                <p className="text-sm text-text-secondary mt-1">
                  PDF, JPG, PNG (máx. 10MB)
                </p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Data de Validade (se aplicável)
              </label>
              <Input type="date" />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Observações
              </label>
              <textarea
                className="w-full px-3 py-2 bg-bg-secondary border border-border-default rounded-lg text-text-primary resize-none"
                rows={2}
                placeholder="Informações adicionais..."
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="ghost" onClick={() => setShowUploadModal(false)}>
                Cancelar
              </Button>
              <Button variant="primary">
                <Upload className="h-4 w-4 mr-2" />
                Enviar
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </MainLayout>
  );
}

export default DocumentsPage;
