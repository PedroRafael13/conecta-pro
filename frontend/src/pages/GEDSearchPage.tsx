import React, { useState } from 'react';
import {
  Search,
  FileText,
  Calendar,
  Tag,
  User,
  Clock,
  Download,
  Eye,
} from 'lucide-react';

export function GEDSearchPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const results = [
    {
      id: '1',
      name: 'Contrato_Prestacao_Servicos_2024.pdf',
      type: 'PDF',
      category: 'Contratos',
      size: '2.4 MB',
      author: 'Maria Silva',
      date: '2024-01-10',
    },
    {
      id: '2',
      name: 'NF_Janeiro_2024_001.pdf',
      type: 'PDF',
      category: 'Documentos Fiscais',
      size: '156 KB',
      author: 'Sistema',
      date: '2024-01-08',
    },
    {
      id: '3',
      name: 'Relatorio_Auditoria_Q4_2023.xlsx',
      type: 'Excel',
      category: 'Compliance',
      size: '1.8 MB',
      author: 'Carlos Santos',
      date: '2024-01-05',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Search className="h-7 w-7 text-conecta-escuro" />
          Busca de Documentos
        </h1>
        <p className="text-gray-600 mt-1">
          Encontre documentos por nome, conteudo ou metadados
        </p>
      </div>

      {/* Search Box */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Digite sua busca..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro text-lg"
            />
          </div>
          <button className="px-6 py-3 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
            Buscar
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mt-4">
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Calendar className="h-4 w-4" />
            Data
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Tag className="h-4 w-4" />
            Categoria
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <User className="h-4 w-4" />
            Autor
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <FileText className="h-4 w-4" />
            Tipo
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Resultados ({results.length})
          </h2>
        </div>
        <div className="divide-y divide-gray-200">
          {results.map((doc) => (
            <div key={doc.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <FileText className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{doc.name}</h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Tag className="h-3 w-3" />
                        {doc.category}
                      </span>
                      <span className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {doc.author}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(doc.date).toLocaleDateString('pt-BR')}
                      </span>
                      <span>{doc.size}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 text-gray-500 hover:text-conecta-escuro hover:bg-gray-100 rounded-lg transition-colors">
                    <Eye className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-500 hover:text-conecta-escuro hover:bg-gray-100 rounded-lg transition-colors">
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default GEDSearchPage;
