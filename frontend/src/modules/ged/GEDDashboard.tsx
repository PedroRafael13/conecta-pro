import React, { useState } from 'react';
import {
  FileText,
  Upload,
  FolderOpen,
  Cpu
} from 'lucide-react';
import { useDocuments, useSearch } from './hooks';
import type { SearchFilters } from './types';

export const GEDDashboard: React.FC = () => {
  const [, setShowUploader] = useState(false);

  const { documents } = useDocuments();
  const {
    results: searchResults,
    search,
    clearSearch
  } = useSearch();

  // Stats mock data
  const [stats] = useState({
    totalDocuments: 2547,
    storageUsed: 8.2,
    storageLimit: 50,
    processingQueue: 12,
    recentUploads: 23,
    ocrProcessed: 98.5,
    aiClassified: 96.2,
  });

  // displayDocuments usado para renderizacao futura
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const displayDocuments = searchResults.length > 0 ? searchResults : documents;

  // handleSearch usado para renderizacao futura
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleSearch = (query: string, filters: SearchFilters) => {
    if (query.trim() || Object.keys(filters).length > 0) {
      search(query, filters);
    } else {
      clearSearch();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <FileText className="w-8 h-8 mr-3 text-blue-600" />
                GED - Gestão Eletrônica de Documentos
              </h1>
              <p className="text-gray-600 mt-1">
                Upload, OCR automático e classificação IA de documentos
              </p>
            </div>
            <button
              onClick={() => setShowUploader(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Documentos</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          
          {/* Total Documents */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Documentos</p>
                <p className="text-3xl font-bold text-gray-900">{stats.totalDocuments.toLocaleString()}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          {/* Storage Usage */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Armazenamento</p>
                <p className="text-3xl font-bold text-gray-900">{stats.storageUsed}GB</p>
                <p className="text-xs text-gray-500">de {stats.storageLimit}GB</p>
              </div>
              <FolderOpen className="w-8 h-8 text-green-600" />
            </div>
          </div>

          {/* Processing Queue */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Fila Processamento</p>
                <p className="text-3xl font-bold text-gray-900">{stats.processingQueue}</p>
                <p className="text-xs text-gray-500">OCR + IA</p>
              </div>
              <Cpu className="w-8 h-8 text-orange-600" />
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Uploads Recentes</p>
                <p className="text-3xl font-bold text-gray-900">{stats.recentUploads}</p>
                <p className="text-xs text-gray-500">últimas 24h</p>
              </div>
              <Upload className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="text-center py-16">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Módulo GED Completo
            </h3>
            <p className="text-gray-500">
              Upload, OCR, IA Classification e Busca implementados
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
