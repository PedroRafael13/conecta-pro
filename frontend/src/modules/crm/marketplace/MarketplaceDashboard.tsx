import React, { useState } from 'react';
import {
  Store,
  Search,
  Filter,
  Grid3X3,
  List,
  Star,
  ShoppingCart,
  Package,
} from 'lucide-react';
import { ServiceCard, FilterSidebar, ProviderCard, mockServices, mockProviders } from './components';

type ViewMode = 'services' | 'providers';
type LayoutMode = 'grid' | 'list';

export const MarketplaceDashboard: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('services');
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const stats = {
    totalServices: 156,
    activeProviders: 89,
    requestsThisMonth: 234,
    avgRating: 4.6,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Store className="h-7 w-7 text-conecta-escuro" />
            Marketplace B2B
          </h1>
          <p className="text-gray-600 mt-1">
            Encontre fornecedores e servicos para seu condominio
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
              showFilters
                ? 'bg-conecta-escuro text-white border-conecta-escuro'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Filter className="h-4 w-4" />
            Filtros
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Servicos</p>
              <p className="text-xl font-bold text-gray-900">{stats.totalServices}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Store className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Fornecedores</p>
              <p className="text-xl font-bold text-gray-900">{stats.activeProviders}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ShoppingCart className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Solicitacoes</p>
              <p className="text-xl font-bold text-gray-900">{stats.requestsThisMonth}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Star className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Avaliacao Media</p>
              <p className="text-xl font-bold text-gray-900">{stats.avgRating}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and View Toggle */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar servicos ou fornecedores..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro"
          />
        </div>
        <div className="flex items-center bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('services')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'services'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Servicos
          </button>
          <button
            onClick={() => setViewMode('providers')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'providers'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Fornecedores
          </button>
        </div>
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setLayoutMode('grid')}
            className={`p-1.5 rounded-md transition-colors ${
              layoutMode === 'grid'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Grid3X3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setLayoutMode('list')}
            className={`p-1.5 rounded-md transition-colors ${
              layoutMode === 'list'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex gap-6">
        {/* Filters Sidebar */}
        {showFilters && (
          <div className="w-64 flex-shrink-0">
            <FilterSidebar
              filters={{}}
              onFiltersChange={() => {}}
              onClear={() => {}}
            />
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1">
          {viewMode === 'services' ? (
            <div className={`grid gap-4 ${
              layoutMode === 'grid'
                ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                : 'grid-cols-1'
            }`}>
              {mockServices.map((service) => (
                <ServiceCard
                  key={service.id}
                  service={service}
                  variant={layoutMode === 'grid' ? 'default' : 'horizontal'}
                />
              ))}
            </div>
          ) : (
            <div className={`grid gap-4 ${
              layoutMode === 'grid'
                ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                : 'grid-cols-1'
            }`}>
              {mockProviders.map((provider) => (
                <ProviderCard
                  key={provider.id}
                  provider={provider}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketplaceDashboard;
