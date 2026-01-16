import React, { useState } from 'react';
import {
  Users,
  TrendingUp,
  DollarSign,
  FileText,
  Plus,
  Search,
  Filter,
  Grid3X3,
  List
} from 'lucide-react';
import { ContactCard } from './contacts/components/ContactCard';
import { DealKanban } from './deals/components/DealKanban';
import { useContacts } from './contacts/hooks';
import { useDeals } from './deals/hooks';
import type { CRMStats } from './types';

export const CRMDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'contacts' | 'deals' | 'proposals' | 'marketplace'>('deals');
  const [viewMode, setViewMode] = useState<'grid' | 'kanban'>('kanban');
  
  const { contacts, loading: contactsLoading } = useContacts();
  const {
    stages,
    dealsByStage,
    pipelineValue,
    loading: dealsLoading
  } = useDeals();

  // Mock stats - would be calculated from real data
  const [stats] = useState<CRMStats>({
    contacts: {
      total: 1247,
      leads: 342,
      customers: 789,
      active: 1156,
    },
    deals: {
      total: 89,
      value: 2840000,
      wonValue: 1250000,
      avgDealValue: 31910,
      conversionRate: 23.5,
      avgDealCycle: 45,
    },
    proposals: {
      total: 156,
      sent: 124,
      accepted: 89,
      acceptanceRate: 71.8,
      avgResponseTime: 4.2,
    },
    marketplace: {
      activeServices: 234,
      totalRequests: 67,
      completionRate: 94.2,
      avgRating: 4.7,
    },
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <Users className="w-8 h-8 mr-3 text-blue-600" />
                CRM 360°
              </h1>
              <p className="text-gray-600 mt-1">
                Gestão completa de relacionamento com clientes
              </p>
            </div>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Novo {activeTab === 'contacts' ? 'Contato' : activeTab === 'deals' ? 'Deal' : 'Item'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          
          {/* Contacts Stats */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Contatos Totais</p>
                <p className="text-3xl font-bold text-gray-900">{stats.contacts.total.toLocaleString()}</p>
                <p className="text-xs text-gray-500">
                  {stats.contacts.leads} leads • {stats.contacts.customers} clientes
                </p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          {/* Pipeline Value */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Valor Pipeline</p>
                <p className="text-3xl font-bold text-gray-900">{formatCurrency(stats.deals.value)}</p>
                <p className="text-xs text-gray-500">
                  {stats.deals.total} deals ativos
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>

          {/* Won Revenue */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Receita Fechada</p>
                <p className="text-3xl font-bold text-gray-900">{formatCurrency(stats.deals.wonValue)}</p>
                <p className="text-xs text-gray-500">
                  {stats.deals.conversionRate}% conversão
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-green-600" />
            </div>
          </div>

          {/* Proposals */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Propostas</p>
                <p className="text-3xl font-bold text-gray-900">{stats.proposals.total}</p>
                <p className="text-xs text-gray-500">
                  {stats.proposals.acceptanceRate}% aceitas
                </p>
              </div>
              <FileText className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'contacts', label: 'Contatos', count: stats.contacts.total },
                { id: 'deals', label: 'Pipeline', count: stats.deals.total },
                { id: 'proposals', label: 'Propostas', count: stats.proposals.total },
                { id: 'marketplace', label: 'Marketplace', count: stats.marketplace.activeServices },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label} ({tab.count})
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-lg border border-gray-200 min-h-96">
          
          {/* Deals Tab - Pipeline Kanban */}
          {activeTab === 'deals' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Pipeline de Vendas</h2>
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-600">
                    Pipeline: <span className="font-medium">{formatCurrency(pipelineValue)}</span>
                  </div>
                  <button
                    onClick={() => setViewMode(viewMode === 'kanban' ? 'grid' : 'kanban')}
                    className="flex items-center space-x-1 text-gray-500 hover:text-gray-700"
                  >
                    {viewMode === 'kanban' ? (
                      <>
                        <Grid3X3 className="w-4 h-4" />
                        <span>Grid</span>
                      </>
                    ) : (
                      <>
                        <List className="w-4 h-4" />
                        <span>Kanban</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {dealsLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Carregando pipeline...</p>
                  </div>
                </div>
              ) : (
                <DealKanban
                  dealsByStage={dealsByStage}
                  stages={stages}
                />
              )}
            </div>
          )}

          {/* Contacts Tab */}
          {activeTab === 'contacts' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Contatos</h2>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Buscar contatos..."
                      className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <button className="flex items-center space-x-1 text-gray-500 hover:text-gray-700">
                    <Filter className="w-4 h-4" />
                    <span>Filtrar</span>
                  </button>
                </div>
              </div>

              {contactsLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-gray-600">Carregando contatos...</p>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {contacts.slice(0, 12).map((contact) => (
                    <ContactCard
                      key={contact.id}
                      contact={contact}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Other tabs placeholder */}
          {(activeTab === 'proposals' || activeTab === 'marketplace') && (
            <div className="p-6 text-center">
              <div className="py-16">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {activeTab === 'proposals' ? 'Módulo de Propostas' : 'Marketplace B2B'}
                </h3>
                <p className="text-gray-500">
                  Em desenvolvimento...
                </p>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
