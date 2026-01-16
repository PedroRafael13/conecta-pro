import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  Eye, 
  MoreVertical, 
  Edit, 
  Trash2,
  Tag,
  Calendar,
  User,
  AlertCircle
} from 'lucide-react';
import type { Document } from '../types';

interface DocumentCardProps {
  document: Document;
  onView?: (document: Document) => void;
  onEdit?: (document: Document) => void;
  onDelete?: (document: Document) => void;
  onDownload?: (document: Document) => void;
  isSelected?: boolean;
  onSelect?: (document: Document) => void;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({
  document,
  onView,
  onEdit,
  onDelete,
  onDownload,
  isSelected,
  onSelect,
}) => {
  const [showMenu, setShowMenu] = useState(false);

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <FileText className="w-8 h-8 text-red-500" />;
      case 'doc':
      case 'docx':
        return <FileText className="w-8 h-8 text-blue-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
        return <FileText className="w-8 h-8 text-green-500" />;
      default:
        return <FileText className="w-8 h-8 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('pt-BR');
  };

  const getStatusBadge = (status: Document['status']) => {
    switch (status) {
      case 'processing':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1 animate-pulse" />
            Processando
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Completo
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <AlertCircle className="w-3 h-3 mr-1" />
            Erro
          </span>
        );
      default:
        return null;
    }
  };

  const getConfidenceBadge = (confidence?: number) => {
    if (!confidence) return null;

    const color = confidence > 0.8 
      ? 'bg-green-100 text-green-800' 
      : confidence > 0.6 
      ? 'bg-yellow-100 text-yellow-800'
      : 'bg-red-100 text-red-800';

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${color}`}>
        IA: {Math.round(confidence * 100)}%
      </span>
    );
  };

  return (
    <div 
      className={`bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 ${
        isSelected ? 'ring-2 ring-blue-500 border-blue-500' : ''
      }`}
      onClick={() => onSelect?.(document)}
    >
      {/* Thumbnail */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center space-x-3">
          {document.thumbnail ? (
            <img
              src={document.thumbnail}
              alt={document.name}
              className="w-12 h-12 object-cover rounded"
            />
          ) : (
            getFileIcon(document.type)
          )}
          
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-medium text-gray-900 truncate">
              {document.name}
            </h3>
            <p className="text-xs text-gray-500">
              {formatFileSize(document.size)} • {document.type.toUpperCase()}
            </p>
          </div>

          {/* Menu */}
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="text-gray-400 hover:text-gray-600 p-1"
            >
              <MoreVertical className="w-4 h-4" />
            </button>

            {showMenu && (
              <div className="absolute right-0 top-8 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                <div className="py-1">
                  {onView && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onView(document);
                        setShowMenu(false);
                      }}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Visualizar
                    </button>
                  )}
                  {onDownload && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDownload(document);
                        setShowMenu(false);
                      }}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </button>
                  )}
                  {onEdit && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onEdit(document);
                        setShowMenu(false);
                      }}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Editar
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(document);
                        setShowMenu(false);
                      }}
                      className="flex items-center px-4 py-2 text-sm text-red-600 hover:bg-gray-100 w-full text-left"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Excluir
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="p-4 space-y-2">
        {/* Status & Classification */}
        <div className="flex items-center space-x-2">
          {getStatusBadge(document.status)}
          {document.classification && getConfidenceBadge(document.classification.confidence)}
        </div>

        {/* Category */}
        <div className="flex items-center space-x-1 text-xs text-gray-500">
          <Tag className="w-3 h-3" />
          <span>{document.category}</span>
        </div>

        {/* Tags */}
        {document.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {document.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tag}
              </span>
            ))}
            {document.tags.length > 3 && (
              <span className="text-xs text-gray-500">
                +{document.tags.length - 3} mais
              </span>
            )}
          </div>
        )}

        {/* Upload Info */}
        <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-100">
          <div className="flex items-center space-x-1">
            <User className="w-3 h-3" />
            <span>{document.uploadedBy}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Calendar className="w-3 h-3" />
            <span>{formatDate(document.uploadDate)}</span>
          </div>
        </div>
      </div>

      {/* Click overlay for card selection */}
      {onSelect && (
        <div className="absolute inset-0 cursor-pointer" onClick={() => onSelect(document)} />
      )}
    </div>
  );
};
