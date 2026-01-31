'use client';

/**
 * Página do Assistente Bartolo
 * Interface completa de chat com estatísticas e insights
 */

import { useState } from 'react';
import { MessageSquare, Brain, TrendingUp, Book, Sparkles } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { BartoloChatWidget } from '@/components/ai/BartoloChatWidget';
import {
  useBartoloStats,
  useBartoloLearningStats,
  useBartoloModules,
  useBartoloWizards,
} from '@/hooks/ai/useBartolo';

export default function AssistentePage() {
  return (
    <div className="container mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bartolo - Assistente Inteligente</h1>
          <p className="text-muted-foreground">
            Seu assistente IA para o Conecta PRO
          </p>
        </div>
        <Badge variant="default" className="gap-2">
          <Brain className="h-4 w-4" />
          GPT-4 Turbo
        </Badge>
      </div>

      <Tabs defaultValue="chat" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chat" className="gap-2">
            <MessageSquare className="h-4 w-4" />
            Chat
          </TabsTrigger>
          <TabsTrigger value="stats" className="gap-2">
            <TrendingUp className="h-4 w-4" />
            Estatísticas
          </TabsTrigger>
          <TabsTrigger value="modules" className="gap-2">
            <Book className="h-4 w-4" />
            Módulos
          </TabsTrigger>
          <TabsTrigger value="wizards" className="gap-2">
            <Sparkles className="h-4 w-4" />
            Assistentes Guiados
          </TabsTrigger>
        </TabsList>

        {/* Chat Tab */}
        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Conversar com Bartolo</CardTitle>
              <CardDescription>
                Faça perguntas sobre o sistema, solicite relatórios ou peça ajuda
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex h-[600px] items-center justify-center">
                <BartoloChatWidget initialOpen />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Stats Tab */}
        <TabsContent value="stats" className="space-y-4">
          <StatsView />
        </TabsContent>

        {/* Modules Tab */}
        <TabsContent value="modules" className="space-y-4">
          <ModulesView />
        </TabsContent>

        {/* Wizards Tab */}
        <TabsContent value="wizards" className="space-y-4">
          <WizardsView />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ==========================================
// Sub-components
// ==========================================

function StatsView() {
  const { data: stats, isLoading } = useBartoloStats();
  const { data: learningStats } = useBartoloLearningStats();

  if (isLoading) {
    return <div>Carregando estatísticas...</div>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Interações Totais</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats?.total_interactions || 0}</div>
          <p className="text-xs text-muted-foreground">
            +{stats?.interactions_today || 0} hoje
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Taxa de Satisfação</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats?.satisfaction_rate || 0}%</div>
          <p className="text-xs text-muted-foreground">
            Baseado em {stats?.total_feedback || 0} feedbacks
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Padrões Aprendidos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {learningStats?.patterns_count || 0}
          </div>
          <p className="text-xs text-muted-foreground">Últimos 30 dias</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Tempo Médio Resposta</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats?.avg_response_time_ms || 0}ms
          </div>
          <p className="text-xs text-muted-foreground">Processamento</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Wizards Completados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats?.wizards_completed || 0}
          </div>
          <p className="text-xs text-muted-foreground">Este mês</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Consultas de Dados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats?.data_queries_count || 0}
          </div>
          <p className="text-xs text-muted-foreground">Acessos ao banco</p>
        </CardContent>
      </Card>
    </div>
  );
}

function ModulesView() {
  const { data: modules, isLoading } = useBartoloModules();

  if (isLoading) {
    return <div>Carregando módulos...</div>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {modules?.map((module: any) => (
        <Card key={module.id}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {module.icon && <span>{module.icon}</span>}
              {module.name}
            </CardTitle>
            <CardDescription>{module.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">Comandos:</span>{' '}
                {module.commands_count || 0}
              </div>
              <div className="flex flex-wrap gap-1">
                {module.capabilities?.slice(0, 3).map((cap: string, idx: number) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {cap}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function WizardsView() {
  const { data: wizards, isLoading } = useBartoloWizards();

  if (isLoading) {
    return <div>Carregando assistentes...</div>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {wizards?.map((wizard: any) => (
        <Card key={wizard.id}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              {wizard.name}
            </CardTitle>
            <CardDescription>{wizard.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="text-sm text-muted-foreground">
                {wizard.steps_count} passos · ~{wizard.estimated_time} minutos
              </div>
              <div className="flex flex-wrap gap-2">
                {wizard.tags?.map((tag: string, idx: number) => (
                  <Badge key={idx} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
