'use client';

import { Brain, UserCheck, Users, Heart, CalendarClock, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const features = [
  {
    title: 'Scoring de Candidatos',
    description: 'Analise automatica de curriculos e ranking de candidatos com base em competencias e requisitos da vaga.',
    icon: UserCheck,
    color: 'text-blue-400',
    bgColor: 'bg-blue-900/30',
    lastRun: '2026-03-12 08:30',
    status: 'Ativo',
  },
  {
    title: 'Previsao de Turnover',
    description: 'Modelo preditivo que identifica colaboradores com risco de desligamento baseado em multiplos fatores.',
    icon: Users,
    color: 'text-red-400',
    bgColor: 'bg-red-900/30',
    lastRun: '2026-03-11 22:00',
    status: 'Ativo',
  },
  {
    title: 'Analise de Clima',
    description: 'Processamento de linguagem natural em respostas abertas de pesquisas de clima organizacional.',
    icon: Heart,
    color: 'text-green-400',
    bgColor: 'bg-green-900/30',
    lastRun: '2026-03-10 14:15',
    status: 'Ativo',
  },
  {
    title: 'Otimizacao de Escalas',
    description: 'Algoritmo de otimizacao para alocacao de colaboradores em postos considerando competencias e custos.',
    icon: CalendarClock,
    color: 'text-purple-400',
    bgColor: 'bg-purple-900/30',
    lastRun: '-',
    status: 'Em Desenvolvimento',
  },
];

const StatusBadge = ({ status }: { status: string }) => {
  if (status === 'Ativo') return (
    <span className="flex items-center gap-1 text-xs text-green-400">
      <CheckCircle className="h-3 w-3" />Ativo
    </span>
  );
  if (status === 'Em Desenvolvimento') return (
    <span className="flex items-center gap-1 text-xs text-yellow-400">
      <AlertCircle className="h-3 w-3" />Em Desenvolvimento
    </span>
  );
  return <span className="text-xs text-muted-foreground">{status}</span>;
};

export default function IAPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Brain className="h-6 w-6" />
          Inteligencia Artificial de Pessoas
        </h1>
        <p className="text-muted-foreground">Modelos de IA aplicados a gestao de pessoas</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {features.map((f) => (
          <Card key={f.title} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-start gap-4 space-y-0">
              <div className={`h-12 w-12 rounded-lg ${f.bgColor} flex items-center justify-center shrink-0`}>
                <f.icon className={`h-6 w-6 ${f.color}`} />
              </div>
              <div className="flex-1">
                <CardTitle className="text-sm font-medium">{f.title}</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">{f.description}</p>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-gray-800 pt-3">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Ultima execucao: {f.lastRun}
                </span>
                <StatusBadge status={f.status} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
