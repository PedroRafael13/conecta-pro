'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import {
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Upload,
  Download,
  Eye,
  Trash2,
  ChevronDown,
  ChevronUp,
  Calendar,
  Shield,
  FileWarning,
} from 'lucide-react';

type DocumentStatus = 'pending' | 'uploaded' | 'verified' | 'rejected' | 'expired';
type DocumentCategory = 'habilitacao' | 'tecnica' | 'economica' | 'fiscal' | 'outros';
type DocumentPriority = 'required' | 'optional' | 'conditional';

interface DocumentItem {
  id: string;
  name: string;
  description?: string;
  category: DocumentCategory;
  priority: DocumentPriority;
  status: DocumentStatus;
  uploadedAt?: Date;
  verifiedAt?: Date;
  expiresAt?: Date;
  fileName?: string;
  fileSize?: number; // bytes
  rejectionReason?: string;
  templateUrl?: string;
  notes?: string;
}

interface DocumentChecklistProps {
  documents: DocumentItem[];
  title?: string;
  showCategories?: boolean;
  allowUpload?: boolean;
  allowDelete?: boolean;
  onUpload?: (documentId: string, file: File) => void;
  onDownload?: (documentId: string) => void;
  onView?: (documentId: string) => void;
  onDelete?: (documentId: string) => void;
  onDownloadTemplate?: (documentId: string) => void;
  className?: string;
}

const categoryLabels: Record<DocumentCategory, string> = {
  habilitacao: 'Habilitacao Juridica',
  tecnica: 'Qualificacao Tecnica',
  economica: 'Qualificacao Economica',
  fiscal: 'Regularidade Fiscal',
  outros: 'Outros Documentos',
};

const statusConfig: Record<
  DocumentStatus,
  { icon: typeof FileText; color: string; bgColor: string; label: string }
> = {
  pending: {
    icon: Clock,
    color: 'text-gray-500',
    bgColor: 'bg-gray-100',
    label: 'Pendente',
  },
  uploaded: {
    icon: FileText,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    label: 'Enviado',
  },
  verified: {
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    label: 'Verificado',
  },
  rejected: {
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    label: 'Rejeitado',
  },
  expired: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    label: 'Expirado',
  },
};

const priorityConfig: Record<DocumentPriority, { label: string; color: string }> = {
  required: { label: 'Obrigatorio', color: 'text-red-600' },
  optional: { label: 'Opcional', color: 'text-gray-500' },
  conditional: { label: 'Condicional', color: 'text-yellow-600' },
};

function formatDate(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isExpiringSoon(date: Date, daysThreshold: number = 30): boolean {
  const now = new Date();
  const diffTime = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays > 0 && diffDays <= daysThreshold;
}

export function DocumentChecklist({
  documents,
  title = 'Documentos Necessarios',
  showCategories = true,
  allowUpload = true,
  allowDelete = true,
  onUpload,
  onDownload,
  onView,
  onDelete,
  onDownloadTemplate,
  className,
}: DocumentChecklistProps) {
  const [expandedCategories, setExpandedCategories] = useState<Set<DocumentCategory>>(
    new Set(Object.keys(categoryLabels) as DocumentCategory[])
  );

  const toggleCategory = (category: DocumentCategory) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  // Group documents by category
  const groupedDocuments = documents.reduce((acc, doc) => {
    if (!acc[doc.category]) {
      acc[doc.category] = [];
    }
    acc[doc.category].push(doc);
    return acc;
  }, {} as Record<DocumentCategory, DocumentItem[]>);

  // Calculate stats
  const stats = {
    total: documents.length,
    completed: documents.filter((d) => d.status === 'verified').length,
    pending: documents.filter((d) => d.status === 'pending').length,
    issues: documents.filter((d) => d.status === 'rejected' || d.status === 'expired').length,
  };

  const completionPercentage = stats.total > 0 ? (stats.completed / stats.total) * 100 : 0;

  return (
    <div
      className={clsx(
        'bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-[#0A2540]">{title}</h3>
          <div className="flex items-center gap-2">
            {stats.issues > 0 && (
              <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-red-100 text-red-600 rounded-full">
                <AlertTriangle className="w-3 h-3" />
                {stats.issues} pendencias
              </span>
            )}
          </div>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Progresso</span>
            <span className="font-semibold text-[#0A2540]">
              {stats.completed} de {stats.total} ({Math.round(completionPercentage)}%)
            </span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${completionPercentage}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={clsx(
                'h-full rounded-full',
                completionPercentage === 100 ? 'bg-green-500' : 'bg-[#FF6B35]'
              )}
            />
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 mt-2">
            <div className="flex items-center gap-1 text-xs">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span className="text-gray-600">{stats.completed} verificados</span>
            </div>
            <div className="flex items-center gap-1 text-xs">
              <Clock className="w-3 h-3 text-gray-400" />
              <span className="text-gray-600">{stats.pending} pendentes</span>
            </div>
            {stats.issues > 0 && (
              <div className="flex items-center gap-1 text-xs">
                <AlertTriangle className="w-3 h-3 text-red-500" />
                <span className="text-gray-600">{stats.issues} problemas</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Document List */}
      <div className="divide-y divide-gray-100">
        {showCategories ? (
          // Grouped by category
          Object.entries(groupedDocuments).map(([category, docs]) => {
            const isExpanded = expandedCategories.has(category as DocumentCategory);
            const categoryStats = {
              total: docs.length,
              completed: docs.filter((d) => d.status === 'verified').length,
            };

            return (
              <div key={category}>
                {/* Category Header */}
                <button
                  onClick={() => toggleCategory(category as DocumentCategory)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-[#0A2540]" />
                    <span className="font-medium text-[#0A2540]">
                      {categoryLabels[category as DocumentCategory]}
                    </span>
                    <span className="text-sm text-gray-500">
                      ({categoryStats.completed}/{categoryStats.total})
                    </span>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>

                {/* Category Documents */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      {docs.map((doc) => (
                        <DocumentItemRow
                          key={doc.id}
                          document={doc}
                          allowUpload={allowUpload}
                          allowDelete={allowDelete}
                          onUpload={onUpload}
                          onDownload={onDownload}
                          onView={onView}
                          onDelete={onDelete}
                          onDownloadTemplate={onDownloadTemplate}
                        />
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })
        ) : (
          // Flat list
          documents.map((doc) => (
            <DocumentItemRow
              key={doc.id}
              document={doc}
              allowUpload={allowUpload}
              allowDelete={allowDelete}
              onUpload={onUpload}
              onDownload={onDownload}
              onView={onView}
              onDelete={onDelete}
              onDownloadTemplate={onDownloadTemplate}
            />
          ))
        )}
      </div>
    </div>
  );
}

// Individual document row component
interface DocumentItemRowProps {
  document: DocumentItem;
  allowUpload?: boolean;
  allowDelete?: boolean;
  onUpload?: (documentId: string, file: File) => void;
  onDownload?: (documentId: string) => void;
  onView?: (documentId: string) => void;
  onDelete?: (documentId: string) => void;
  onDownloadTemplate?: (documentId: string) => void;
}

function DocumentItemRow({
  document: doc,
  allowUpload,
  allowDelete,
  onUpload,
  onDownload,
  onView,
  onDelete,
  onDownloadTemplate,
}: DocumentItemRowProps) {
  const status = statusConfig[doc.status];
  const StatusIcon = status.icon;
  const isExpiring = doc.expiresAt && isExpiringSoon(doc.expiresAt);
  const isExpired = doc.expiresAt && new Date() > doc.expiresAt;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUpload) {
      onUpload(doc.id, file);
    }
  };

  return (
    <div
      className={clsx(
        'px-4 py-3 hover:bg-gray-50 transition-colors',
        doc.status === 'rejected' && 'bg-red-50/50',
        isExpiring && !isExpired && 'bg-yellow-50/50'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Status Icon */}
        <div
          className={clsx(
            'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center',
            status.bgColor
          )}
        >
          <StatusIcon className={clsx('w-4 h-4', status.color)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h4 className="font-medium text-[#0A2540] truncate">{doc.name}</h4>
                <span className={clsx('text-xs', priorityConfig[doc.priority].color)}>
                  {priorityConfig[doc.priority].label}
                </span>
              </div>
              {doc.description && (
                <p className="text-sm text-gray-500 mt-0.5 line-clamp-1">{doc.description}</p>
              )}
            </div>

            {/* Status Badge */}
            <span
              className={clsx(
                'flex-shrink-0 px-2 py-0.5 text-xs font-medium rounded-full',
                status.bgColor,
                status.color
              )}
            >
              {status.label}
            </span>
          </div>

          {/* File Info */}
          {doc.fileName && (
            <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
              <span className="truncate max-w-[200px]">{doc.fileName}</span>
              {doc.fileSize && <span>{formatFileSize(doc.fileSize)}</span>}
              {doc.uploadedAt && <span>Enviado em {formatDate(doc.uploadedAt)}</span>}
            </div>
          )}

          {/* Expiration Warning */}
          {doc.expiresAt && (
            <div
              className={clsx(
                'flex items-center gap-1 mt-2 text-xs',
                isExpired ? 'text-red-600' : isExpiring ? 'text-yellow-600' : 'text-gray-500'
              )}
            >
              <Calendar className="w-3 h-3" />
              <span>
                {isExpired
                  ? `Expirado em ${formatDate(doc.expiresAt)}`
                  : `Valido ate ${formatDate(doc.expiresAt)}`}
                {isExpiring && !isExpired && ' (expirando)'}
              </span>
            </div>
          )}

          {/* Rejection Reason */}
          {doc.status === 'rejected' && doc.rejectionReason && (
            <div className="flex items-start gap-1 mt-2 p-2 bg-red-100 rounded text-xs text-red-700">
              <FileWarning className="w-3 h-3 mt-0.5 flex-shrink-0" />
              <span>{doc.rejectionReason}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 mt-2">
            {/* Upload */}
            {allowUpload && (doc.status === 'pending' || doc.status === 'rejected' || doc.status === 'expired') && onUpload && (
              <label className="cursor-pointer">
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                />
                <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-[#FF6B35] hover:bg-orange-50 rounded transition-colors">
                  <Upload className="w-3 h-3" />
                  Enviar
                </span>
              </label>
            )}

            {/* View */}
            {doc.status !== 'pending' && onView && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onView(doc.id)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 rounded transition-colors"
              >
                <Eye className="w-3 h-3" />
                Ver
              </motion.button>
            )}

            {/* Download */}
            {doc.status !== 'pending' && onDownload && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onDownload(doc.id)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 rounded transition-colors"
              >
                <Download className="w-3 h-3" />
                Baixar
              </motion.button>
            )}

            {/* Template */}
            {doc.templateUrl && onDownloadTemplate && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onDownloadTemplate(doc.id)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded transition-colors"
              >
                <FileText className="w-3 h-3" />
                Modelo
              </motion.button>
            )}

            {/* Delete */}
            {allowDelete && doc.status !== 'pending' && onDelete && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onDelete(doc.id)}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 rounded transition-colors"
              >
                <Trash2 className="w-3 h-3" />
                Remover
              </motion.button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
