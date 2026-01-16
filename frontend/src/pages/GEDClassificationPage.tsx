import React from 'react';
import {
  FolderTree,
  Tag,
  Plus,
  Search,
  Edit2,
  Trash2,
  ChevronRight,
} from 'lucide-react';

export function GEDClassificationPage() {
  const categories = [
    {
      id: '1',
      name: 'Contratos',
      count: 234,
      subcategories: ['Prestacao de Servicos', 'Fornecedores', 'Trabalho'],
    },
    {
      id: '2',
      name: 'Documentos Fiscais',
      count: 567,
      subcategories: ['Notas Fiscais', 'Guias de Impostos', 'Declaracoes'],
    },
    {
      id: '3',
      name: 'RH',
      count: 189,
      subcategories: ['Admissao', 'Demissao', 'Ferias', 'Beneficios'],
    },
    {
      id: '4',
      name: 'Compliance',
      count: 98,
      subcategories: ['Auditorias', 'Certificacoes', 'LGPD'],
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FolderTree className="h-7 w-7 text-conecta-escuro" />
            Classificacao de Documentos
          </h1>
          <p className="text-gray-600 mt-1">
            Organize e classifique documentos por categorias
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
          <Plus className="h-4 w-4" />
          Nova Categoria
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar categorias..."
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro"
        />
      </div>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {categories.map((category) => (
          <div key={category.id} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-conecta-escuro/10 rounded-lg">
                  <FolderTree className="h-5 w-5 text-conecta-escuro" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{category.name}</h3>
                  <p className="text-sm text-gray-600">{category.count} documentos</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="p-2 text-gray-500 hover:text-conecta-escuro hover:bg-gray-100 rounded-lg transition-colors">
                  <Edit2 className="h-4 w-4" />
                </button>
                <button className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="space-y-2">
              {category.subcategories.map((sub) => (
                <div
                  key={sub}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                >
                  <Tag className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-700">{sub}</span>
                  <ChevronRight className="h-4 w-4 text-gray-400 ml-auto" />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default GEDClassificationPage;
