import React, { useState } from 'react';
import {
  FileText,
  Plus,
  Search,
  Grid3X3,
  List,
  TrendingUp,
  Clock,
  CheckCircle,
  Send,
} from 'lucide-react';
import { ProposalCard, mockProposals } from './components';

type FilterStatus = 'all' | 'draft' | 'sent' | 'viewed' | 'accepted' | 'rejected' | 'expired';
type ViewMode = 'grid' | 'list';

export const ProposalsDashboard: React.FC = () => {
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');

  const stats = {
    total: 156,
    draft: 12,
    sent: 34,
    viewed: 18,
    accepted: 67,
    rejected: 15,
    expired: 10,
    acceptanceRate: 81.7,
    avgResponseTime: 3.2,
  };

  const statusFilters: { value: FilterStatus; label: string; count: number }[] = [
    { value: 'all', label: 'Todas', count: stats.total },
    { value: 'draft', label: 'Rascunho', count: stats.draft },
    { value: 'sent', label: 'Enviadas', count: stats.sent },
    { value: 'viewed', label: 'Visualizadas', count: stats.viewed },
    { value: 'accepted', label: 'Aceitas', count: stats.accepted },
    { value: 'rejected', label: 'Rejeitadas', count: stats.rejected },
    { value: 'expired', label: 'Expiradas', count: stats.expired },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FileText className="h-7 w-7 text-conecta-escuro" />
            Propostas Comerciais
          </h1>
          <p className="text-gray-600 mt-1">
            Gerencie e acompanhe suas propostas de servicos
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
          <Plus className="h-4 w-4" />
          Nova Proposta
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Send className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Enviadas (mes)</p>
              <p className="text-xl font-bold text-gray-900">{stats.sent}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Aceitas</p>
              <p className="text-xl font-bold text-gray-900">{stats.accepted}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Taxa de Aceitacao</p>
              <p className="text-xl font-bold text-gray-900">{stats.acceptanceRate}%</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Tempo Medio Resposta</p>
              <p className="text-xl font-bold text-gray-900">{stats.avgResponseTime} dias</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex-1 min-w-64 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar propostas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-conecta-escuro focus:border-conecta-escuro"
          />
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {statusFilters.map((filter) => (
            <button
              key={filter.value}
              onClick={() => setFilterStatus(filter.value)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                filterStatus === filter.value
                  ? 'bg-conecta-escuro text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {filter.label}
              <span className={`ml-1.5 px-1.5 py-0.5 rounded text-xs ${
                filterStatus === filter.value
                  ? 'bg-white/20'
                  : 'bg-gray-200'
              }`}>
                {filter.count}
              </span>
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1.5 rounded-md transition-colors ${
              viewMode === 'grid'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Grid3X3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-1.5 rounded-md transition-colors ${
              viewMode === 'list'
                ? 'bg-white text-conecta-escuro shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Proposals Grid */}
      <div className={`grid gap-4 ${
        viewMode === 'grid'
          ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
          : 'grid-cols-1'
      }`}>
        {mockProposals.map((proposal) => (
          <ProposalCard
            key={proposal.id}
            proposal={proposal}
            onView={() => console.log('View proposal:', proposal.id)}
          />
        ))}
      </div>

      {/* Empty State */}
      {mockProposals.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Nenhuma proposta encontrada
          </h3>
          <p className="text-gray-600 mb-4">
            Comece criando sua primeira proposta comercial
          </p>
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
            <Plus className="h-4 w-4" />
            Nova Proposta
          </button>
        </div>
      )}
    </div>
  );
};

export default ProposalsDashboard;
