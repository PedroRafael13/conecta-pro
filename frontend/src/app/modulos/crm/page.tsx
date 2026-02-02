'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Users, UserPlus, Target, Building2, FileText,
  RefreshCw, ArrowRight,
} from 'lucide-react';
import { useCRMDashboardKpis } from '@/hooks/crm';
import { formatCurrency } from '@/lib/utils';

export default function CRMDashboardPage() {
  const router = useRouter();
  const { data: kpis, isLoading, refetch } = useCRMDashboardKpis();

  const kpiData = kpis as any;

  const cards = [
    {
      title: 'Leads',
      description: 'Gerenciar leads e captacao',
      icon: UserPlus,
      href: '/modulos/crm/leads',
      value: kpiData?.leads_total || 0,
      subtitle: `${kpiData?.leads_new_month || 0} novos este mes`,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Oportunidades',
      description: 'Pipeline de vendas',
      icon: Target,
      href: '/modulos/crm/oportunidades',
      value: kpiData?.opportunities_total || 0,
      subtitle: kpiData?.pipeline_value ? formatCurrency(kpiData.pipeline_value) : 'Pipeline',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Clientes',
      description: 'Base de clientes ativos',
      icon: Building2,
      href: '/modulos/crm/clientes',
      value: kpiData?.leads_qualified || 0,
      subtitle: `${kpiData?.leads_conversion_rate ? (kpiData.leads_conversion_rate * 100).toFixed(1) : 0}% conversao`,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Propostas',
      description: 'Propostas comerciais',
      icon: FileText,
      href: '/modulos/crm/propostas',
      value: kpiData?.proposals_total || 0,
      subtitle: kpiData?.proposals_total_value ? formatCurrency(kpiData.proposals_total_value) : 'Valor total',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Users className="h-6 w-6" />
            CRM
          </h1>
          <p className="text-muted-foreground">Gestao de relacionamento com clientes</p>
        </div>
        <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* KPI Summary */}
      {kpiData && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground">Win Rate</div>
              <div className="text-2xl font-bold text-green-600">
                {kpiData.opportunities_win_rate ? `${(kpiData.opportunities_win_rate * 100).toFixed(1)}%` : '0%'}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground">Ticket Medio</div>
              <div className="text-2xl font-bold">
                {formatCurrency(kpiData.avg_deal_size || 0)}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-sm text-muted-foreground">Ciclo Medio</div>
              <div className="text-2xl font-bold">
                {kpiData.avg_sales_cycle_days || 0} dias
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Cards de navegacao */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <Card
            key={card.title}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => router.push(card.href)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{isLoading ? '...' : card.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{card.subtitle}</p>
              <div className="flex items-center gap-1 mt-2 text-xs text-primary">
                <span>Acessar</span>
                <ArrowRight className="h-3 w-3" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Contatos card */}
      <Card
        className="cursor-pointer hover:shadow-md transition-shadow"
        onClick={() => router.push('/modulos/crm/contatos')}
      >
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-cyan-50 flex items-center justify-center">
                <Users className="h-5 w-5 text-cyan-600" />
              </div>
              <div>
                <h3 className="font-medium">Contatos</h3>
                <p className="text-sm text-muted-foreground">Gerenciar contatos vinculados a clientes</p>
              </div>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
