'use client';

import { Landmark, FileText, Users, Database, FileSpreadsheet, FileCode, Award, RefreshCw, ArrowRight, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
;
import { useObterDashboardMonitoramento, useHealthCheck } from '@/hooks/government';

export default function FiscalDashboardPage() {
  const router = useRouter();
  const {
    data: dashboardData,
    isLoading,
    isError,
    error,
    refetch,
  } = useObterDashboardMonitoramento();
  const { data: healthData } = useHealthCheck();

  const dashboard = dashboardData as any;
  const nfseEmitidas = dashboard?.nfse_emitidas ?? dashboard?.nfse?.total ?? 0;
  const esocialPendente = dashboard?.esocial_pendente ?? dashboard?.esocial?.pendentes ?? 0;
  const certidoesCount = dashboard?.certidoes ?? dashboard?.certificados?.total ?? 0;
  const syncStatus = healthData?.status ?? dashboard?.sync_status ?? 'offline';

  const statsCards = [
    {
      title: 'NFS-e Emitidas',
      value: nfseEmitidas,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'eSocial Pendente',
      value: esocialPendente,
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: 'Certidoes',
      value: certidoesCount,
      icon: Award,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Status Sync',
      value: syncStatus === 'ok' || syncStatus === 'healthy' ? 'Online' : 'Offline',
      icon: RefreshCw,
      color: syncStatus === 'ok' || syncStatus === 'healthy' ? 'text-emerald-600' : 'text-red-600',
      bgColor: syncStatus === 'ok' || syncStatus === 'healthy' ? 'bg-emerald-50' : 'bg-red-50',
    },
  ];

  const navigationCards = [
    {
      title: 'NFS-e',
      description: 'Emissao e gestao de Notas Fiscais de Servico Eletronica',
      icon: FileText,
      href: '/modulos/fiscal/nfse',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'eSocial',
      description: 'Eventos trabalhistas e previdenciarios',
      icon: Users,
      href: '/modulos/fiscal/esocial',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'SPED',
      description: 'Sistema Publico de Escrituracao Digital',
      icon: Database,
      href: '/modulos/fiscal/sped',
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
    {
      title: 'DCTFWeb',
      description: 'Declaracao de Debitos e Creditos Tributarios',
      icon: FileSpreadsheet,
      href: '/modulos/fiscal/dctfweb',
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
    },
    {
      title: 'EFD-Reinf',
      description: 'Escrituracao Fiscal Digital de Retencoes e Informacoes',
      icon: FileCode,
      href: '/modulos/fiscal/reinf',
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-50',
    },
    {
      title: 'Certidoes',
      description: 'Gestao de certidoes e certificados digitais',
      icon: Award,
      href: '/modulos/fiscal/certidoes',
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Landmark className="h-6 w-6" />
            Fiscal
          </h1>
          <p className="text-muted-foreground">
            Gestao fiscal, tributaria e obrigacoes acessorias
          </p>
        </div>
        <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/30">
          <AlertCircle className="w-5 h-5 text-[hsl(var(--destructive))]" />
          <div>
            <p className="font-medium text-[hsl(var(--destructive))]">Erro ao carregar dashboard</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {(error as Error)?.message || 'Tente novamente em alguns instantes'}
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => refetch()} className="ml-auto">
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <div className={`w-8 h-8 rounded-lg ${card.bgColor} flex items-center justify-center`}>
                <card.icon className={`h-4 w-4 ${card.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : card.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Navigation Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {navigationCards.map((card) => (
          <Card
            key={card.title}
            variant="interactive"
            className="cursor-pointer"
            onClick={() => router.push(card.href)}
          >
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-lg ${card.bgColor} flex items-center justify-center flex-shrink-0`}>
                  <card.icon className={`h-6 w-6 ${card.color}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-[hsl(var(--foreground))]">{card.title}</h3>
                  <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
                    {card.description}
                  </p>
                  <div className="flex items-center gap-1 mt-3 text-sm text-[hsl(var(--primary))]">
                    <span>Acessar</span>
                    <ArrowRight className="h-4 w-4" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
