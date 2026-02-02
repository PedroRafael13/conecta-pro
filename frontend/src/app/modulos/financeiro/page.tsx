'use client';

import { DollarSign, TrendingUp, TrendingDown, Activity, ArrowRight, CreditCard, CheckCircle2, Users, ShoppingCart, Package, Landmark, Calculator, Receipt, Wallet } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
;
import { useRouter } from 'next/navigation';
import { useFinancialOverview } from '@/hooks/financial/useFinancial';

const formatCurrency = (value: number | undefined | null) => {
  if (value == null) return 'R$ 0,00';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const navigationCards = [
  {
    title: 'Contas a Pagar',
    description: 'Gerencie pagamentos, vencimentos e fornecedores',
    href: '/modulos/financeiro/contas-pagar',
    icon: TrendingDown,
  },
  {
    title: 'Contas a Receber',
    description: 'Controle cobranças, boletos e recebimentos',
    href: '/modulos/financeiro/contas-receber',
    icon: TrendingUp,
  },
  {
    title: 'Fluxo de Caixa',
    description: 'Acompanhe entradas, saídas e projeções',
    href: '/modulos/financeiro/fluxo-caixa',
    icon: Activity,
  },
  {
    title: 'Conciliação',
    description: 'Concilie extratos bancários e lançamentos',
    href: '/modulos/financeiro/conciliacao',
    icon: CheckCircle2,
  },
  {
    title: 'Fornecedores',
    description: 'Cadastro e gestão de fornecedores',
    href: '/modulos/financeiro/fornecedores',
    icon: Users,
  },
  {
    title: 'Clientes',
    description: 'Cadastro e gestão de clientes',
    href: '/modulos/financeiro/clientes',
    icon: Users,
  },
  {
    title: 'Compras',
    description: 'Requisições, cotações e pedidos de compra',
    href: '/modulos/financeiro/compras',
    icon: ShoppingCart,
  },
  {
    title: 'Estoque',
    description: 'Controle de materiais e movimentações',
    href: '/modulos/financeiro/estoque',
    icon: Package,
  },
  {
    title: 'Fiscal',
    description: 'Notas fiscais, impostos e obrigações',
    href: '/modulos/financeiro/fiscal',
    icon: Landmark,
  },
  {
    title: 'Contabilidade',
    description: 'Plano de contas, lançamentos e balancetes',
    href: '/modulos/financeiro/contabilidade',
    icon: Calculator,
  },
  {
    title: 'Faturamento',
    description: 'Emissão de faturas e controle de billing',
    href: '/modulos/financeiro/faturamento',
    icon: Receipt,
  },
  {
    title: 'Custeio ABC',
    description: 'Análise de custos por atividade',
    href: '/modulos/financeiro/custeio',
    icon: Wallet,
  },
];

export default function FinanceiroPage() {
  const router = useRouter();
  const { data: overview, isLoading } = useFinancialOverview();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
        <div className="animate-pulse-slow text-[hsl(var(--primary))]">
          <DollarSign className="w-12 h-12" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4 h-16">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                Financeiro
              </h1>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Gestão financeira completa
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Cards */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-4">
            Indicadores
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Receita */}
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-green-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Receita</p>
                    <p className="text-xl font-bold text-green-500 truncate">
                      {formatCurrency(overview?.receita_total)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Despesa */}
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                    <TrendingDown className="w-5 h-5 text-red-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Despesa</p>
                    <p className="text-xl font-bold text-red-500 truncate">
                      {formatCurrency(overview?.despesa_total)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Saldo */}
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <Activity className="w-5 h-5 text-blue-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Saldo</p>
                    <p className="text-xl font-bold text-blue-500 truncate">
                      {formatCurrency(overview?.saldo)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Inadimplência */}
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                    <CreditCard className="w-5 h-5 text-yellow-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">Inadimplência</p>
                    <p className="text-xl font-bold text-yellow-500 truncate">
                      {formatCurrency(overview?.inadimplencia)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Navigation Cards */}
        <div>
          <h2 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-4">
            Módulos Financeiros
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {navigationCards.map((card) => {
              const Icon = card.icon;
              return (
                <Card
                  key={card.href}
                  variant="interactive"
                  className="group"
                  onClick={() => router.push(card.href)}
                >
                  <CardContent className="pt-4">
                    <div className="flex flex-col gap-3">
                      <div className="flex items-center justify-between">
                        <div className="w-10 h-10 rounded-lg bg-[hsl(var(--primary))]/10 flex items-center justify-center">
                          <Icon className="w-5 h-5 text-[hsl(var(--primary))]" />
                        </div>
                        <ArrowRight className="w-4 h-4 text-[hsl(var(--muted-foreground))] transition-transform group-hover:translate-x-1" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
                          {card.title}
                        </h3>
                        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1 line-clamp-2">
                          {card.description}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
}
