import React from 'react';
import {
  Users,
  TrendingUp,
  DollarSign,
  Target,
  Plus,
  Filter,
} from 'lucide-react';

export function CRMPipelinePage() {
  const stages = [
    {
      id: 'prospecting',
      name: 'Prospecção',
      color: 'bg-blue-500',
      deals: [
        { id: '1', title: 'Condominio Parque Verde', value: 45000, contact: 'Ana Silva' },
        { id: '2', title: 'Residencial Sol Nascente', value: 32000, contact: 'Carlos Lima' },
      ],
    },
    {
      id: 'qualification',
      name: 'Qualificação',
      color: 'bg-purple-500',
      deals: [
        { id: '3', title: 'Edificio Corporate Tower', value: 120000, contact: 'Maria Santos' },
      ],
    },
    {
      id: 'proposal',
      name: 'Proposta',
      color: 'bg-yellow-500',
      deals: [
        { id: '4', title: 'Shopping Center Norte', value: 250000, contact: 'Pedro Costa' },
        { id: '5', title: 'Hospital Santa Casa', value: 180000, contact: 'Julia Mendes' },
      ],
    },
    {
      id: 'negotiation',
      name: 'Negociação',
      color: 'bg-orange-500',
      deals: [
        { id: '6', title: 'Universidade Federal', value: 350000, contact: 'Roberto Alves' },
      ],
    },
    {
      id: 'closed',
      name: 'Fechado',
      color: 'bg-green-500',
      deals: [
        { id: '7', title: 'Industria Metalurgica', value: 420000, contact: 'Fernando Souza' },
      ],
    },
  ];

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Target className="h-7 w-7 text-conecta-escuro" />
            Pipeline de Vendas
          </h1>
          <p className="text-gray-600 mt-1">
            Acompanhe o funil de vendas e oportunidades
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Filter className="h-4 w-4" />
            Filtros
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-conecta-escuro text-white rounded-lg hover:bg-conecta-claro transition-colors">
            <Plus className="h-4 w-4" />
            Nova Oportunidade
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Target className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Oportunidades</p>
              <p className="text-xl font-bold text-gray-900">24</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <DollarSign className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Valor Total</p>
              <p className="text-xl font-bold text-gray-900">R$ 1.4M</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Taxa Conversao</p>
              <p className="text-xl font-bold text-gray-900">32%</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Users className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Ticket Medio</p>
              <p className="text-xl font-bold text-gray-900">R$ 58K</p>
            </div>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {stages.map((stage) => (
          <div key={stage.id} className="flex-shrink-0 w-72">
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${stage.color}`} />
                  <h3 className="font-semibold text-gray-900">{stage.name}</h3>
                </div>
                <span className="text-sm text-gray-500">{stage.deals.length}</span>
              </div>
              <div className="space-y-3">
                {stage.deals.map((deal) => (
                  <div
                    key={deal.id}
                    className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
                  >
                    <h4 className="font-medium text-gray-900 mb-2">{deal.title}</h4>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">{deal.contact}</span>
                      <span className="font-semibold text-conecta-escuro">
                        {formatCurrency(deal.value)}
                      </span>
                    </div>
                  </div>
                ))}
                <button className="w-full py-2 text-sm text-gray-500 hover:text-conecta-escuro hover:bg-white rounded-lg transition-colors">
                  + Adicionar
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CRMPipelinePage;
