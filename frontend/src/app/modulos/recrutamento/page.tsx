'use client';

import { Users, Briefcase, UserPlus, FileText, Calendar, RefreshCw, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  usePositionStats,
  useCandidateStats,
  useApplicationStats,
  useInterviewStats,
} from '@/hooks/recruitment';

export default function RecrutamentoDashboardPage() {
  const router = useRouter();

  const { data: positionStats, isLoading: loadingPositions, error: errPositions, refetch: refetchPositions } = usePositionStats();
  const { data: candidateStats, isLoading: loadingCandidates, error: errCandidates, refetch: refetchCandidates } = useCandidateStats();
  const { data: applicationStats, isLoading: loadingApplications, error: errApplications, refetch: refetchApplications } = useApplicationStats();
  const { data: interviewStats, isLoading: loadingInterviews, error: errInterviews, refetch: refetchInterviews } = useInterviewStats();

  const isLoading = loadingPositions || loadingCandidates || loadingApplications || loadingInterviews;
  const hasError = errPositions || errCandidates || errApplications || errInterviews;

  const posStats = positionStats as any;
  const candStats = candidateStats as any;
  const appStats = applicationStats as any;
  const intStats = interviewStats as any;

  const handleRefresh = () => {
    refetchPositions();
    refetchCandidates();
    refetchApplications();
    refetchInterviews();
  };

  const statCards = [
    {
      title: 'Vagas Abertas',
      value: posStats?.open_positions ?? posStats?.abertas ?? 0,
      subtitle: `${posStats?.total ?? 0} vagas no total`,
      icon: Briefcase,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Candidatos Ativos',
      value: candStats?.active_candidates ?? candStats?.ativos ?? 0,
      subtitle: `${candStats?.total ?? 0} candidatos cadastrados`,
      icon: UserPlus,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Candidaturas',
      value: appStats?.active_applications ?? appStats?.ativas ?? 0,
      subtitle: `${appStats?.total ?? 0} candidaturas no total`,
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Entrevistas Hoje',
      value: intStats?.today ?? intStats?.hoje ?? 0,
      subtitle: `${intStats?.scheduled ?? intStats?.agendadas ?? 0} agendadas`,
      icon: Calendar,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  const navCards = [
    {
      title: 'Vagas',
      description: 'Gerenciar vagas e posicoes abertas',
      icon: Briefcase,
      href: '/modulos/recrutamento/vagas',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Candidatos',
      description: 'Base de candidatos cadastrados',
      icon: UserPlus,
      href: '/modulos/recrutamento/candidatos',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Candidaturas',
      description: 'Acompanhar candidaturas e etapas',
      icon: FileText,
      href: '/modulos/recrutamento/candidaturas',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Entrevistas',
      description: 'Agenda de entrevistas e avaliacoes',
      icon: Calendar,
      href: '/modulos/recrutamento/entrevistas',
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
            Recrutamento e Selecao
          </h1>
          <p className="text-muted-foreground">
            Gerencie vagas, candidatos, candidaturas e entrevistas
          </p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Error Banner */}
      {hasError && !isLoading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-800/30 dark:bg-red-900/20 dark:text-red-400">
          <p className="font-medium">Erro ao carregar dados do recrutamento</p>
          <p className="mt-1 text-red-600 dark:text-red-500">
            Alguns serviços estão temporariamente indisponíveis. Os dados exibidos podem estar incompletos.
          </p>
          <Button variant="outline" size="sm" className="mt-2" onClick={handleRefresh}>
            <RefreshCw className="h-3 w-3 mr-1" /> Tentar novamente
          </Button>
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.title}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{card.title}</p>
                  <p className="text-2xl font-bold">
                    {isLoading ? '...' : card.value}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">{card.subtitle}</p>
                </div>
                <div className={`h-10 w-10 rounded-lg ${card.bgColor} flex items-center justify-center`}>
                  <card.icon className={`h-5 w-5 ${card.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Navigation Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {navCards.map((card) => (
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
              <p className="text-sm text-muted-foreground">{card.description}</p>
              <div className="flex items-center gap-1 mt-3 text-xs text-primary">
                <span>Acessar</span>
                <ArrowRight className="h-3 w-3" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
