'use client';

import { LogIn, Monitor, Bell, RefreshCw, ArrowRight, Users, AlertTriangle, MapPin } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
;
import { useCampoDashboard, useMonitoringHealth } from '@/hooks/campo/useCampo';

export default function CampoPage() {
  const router = useRouter();
  const { data: dashboard, isLoading: dashLoading, refetch: refetchDash } = useCampoDashboard();
  const { data: health, isLoading: healthLoading } = useMonitoringHealth();
  const isLoading = dashLoading || healthLoading;

  const stats = {
    checkinsHoje: dashboard?.checkins_hoje ?? dashboard?.checkins ?? 0,
    agentesEmCampo: dashboard?.agentes_em_campo ?? dashboard?.agentes ?? 0,
    ocorrencias: dashboard?.ocorrencias ?? 0,
    alertas: health?.alertas ?? dashboard?.alertas ?? 0,
  };

  const modules = [
    {
      title: 'Check-in / Check-out',
      description: 'Registros de entrada e saida dos colaboradores nos postos de trabalho.',
      icon: LogIn,
      href: '/modulos/campo/checkin',
      color: 'cyan',
    },
    {
      title: 'Monitoramento',
      description: 'Acompanhamento em tempo real dos agentes em campo e status do sistema.',
      icon: Monitor,
      href: '/modulos/campo/monitoramento',
      color: 'violet',
    },
    {
      title: 'Comunicados',
      description: 'Envio e gestao de comunicados para equipes em campo.',
      icon: Bell,
      href: '/modulos/campo/comunicados',
      color: 'amber',
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                <MapPin className="w-5 h-5 text-cyan-500" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                  Campo
                </h1>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">
                  Gestao de operacoes em campo
                </p>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={() => refetchDash()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Atualizar
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                  <LogIn className="w-5 h-5 text-cyan-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                    {stats.checkinsHoje}
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Check-ins Hoje</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                  <Users className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                    {stats.agentesEmCampo}
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Agentes em Campo</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                  <Monitor className="w-5 h-5 text-violet-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                    {stats.ocorrencias}
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Ocorrencias</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                    {stats.alertas}
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Alertas</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Module Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {modules.map((mod) => {
            const Icon = mod.icon;
            return (
              <Card
                key={mod.href}
                className="cursor-pointer hover:border-[hsl(var(--primary))]/50 transition-all duration-200 hover:shadow-lg"
                onClick={() => router.push(mod.href)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className={`w-12 h-12 rounded-lg bg-${mod.color}-500/10 flex items-center justify-center`}>
                      <Icon className={`w-6 h-6 text-${mod.color}-500`} />
                    </div>
                    <ArrowRight className="w-5 h-5 text-[hsl(var(--muted-foreground))]" />
                  </div>
                  <CardTitle className="text-base mt-3">{mod.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-[hsl(var(--muted-foreground))]">
                    {mod.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </main>
    </div>
  );
}
