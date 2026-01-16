import React from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  FileText,
  PiggyBank,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';

export function FinancePage() {
  const stats = {
    revenue: 2450000,
    expenses: 1890000,
    profit: 560000,
    profitMargin: 22.9,
    accountsReceivable: 456000,
    accountsPayable: 234000,
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <DollarSign className="h-7 w-7 text-conecta-escuro" />
            Financeiro
          </h1>
          <p className="text-gray-600 mt-1">
            Visao geral financeira e controle de fluxo de caixa
          </p>
        </div>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Receita Total</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(stats.revenue)}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="flex items-center gap-1 mt-3 text-sm text-green-600">
            <ArrowUpRight className="h-4 w-4" />
            <span>+12.5% vs mes anterior</span>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Despesas</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(stats.expenses)}
              </p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <TrendingDown className="h-6 w-6 text-red-600" />
            </div>
          </div>
          <div className="flex items-center gap-1 mt-3 text-sm text-red-600">
            <ArrowDownRight className="h-4 w-4" />
            <span>+5.2% vs mes anterior</span>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Lucro Liquido</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {formatCurrency(stats.profit)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <PiggyBank className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="flex items-center gap-1 mt-3 text-sm text-blue-600">
            <span>Margem: {stats.profitMargin}%</span>
          </div>
        </div>
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-orange-100 rounded-lg">
              <FileText className="h-5 w-5 text-orange-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Contas a Receber</h2>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {formatCurrency(stats.accountsReceivable)}
          </p>
          <p className="text-sm text-gray-600 mt-2">45 titulos em aberto</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <CreditCard className="h-5 w-5 text-purple-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Contas a Pagar</h2>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {formatCurrency(stats.accountsPayable)}
          </p>
          <p className="text-sm text-gray-600 mt-2">28 titulos em aberto</p>
        </div>
      </div>

      {/* Placeholder for charts */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Fluxo de Caixa</h2>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <p className="text-gray-500">Grafico de fluxo de caixa</p>
        </div>
      </div>
    </div>
  );
}

export default FinancePage;
