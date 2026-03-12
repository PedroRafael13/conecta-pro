'use client';

import { Users, AlertTriangle, AlertCircle, CheckCircle, XOctagon } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const distribuicao = [
  { nivel: 'Baixo', count: 28, cor: 'text-green-400', bgCor: 'bg-green-900/30', icon: CheckCircle },
  { nivel: 'Medio', count: 10, cor: 'text-yellow-400', bgCor: 'bg-yellow-900/30', icon: AlertCircle },
  { nivel: 'Alto', count: 4, cor: 'text-orange-400', bgCor: 'bg-orange-900/30', icon: AlertTriangle },
  { nivel: 'Critico', count: 2, cor: 'text-red-400', bgCor: 'bg-red-900/30', icon: XOctagon },
];

const colaboradoresMock = [
  { id: 1, colaborador: 'Marcos Silva', score: 0.92, nivel: 'Critico', fatores: 'Salario abaixo mercado, Insatisfacao gestor', acoes: 'Reajuste salarial, Transferencia de equipe' },
  { id: 2, colaborador: 'Fernanda Oliveira', score: 0.85, nivel: 'Critico', fatores: 'Sem promocao ha 3 anos, Sobrecarga', acoes: 'Plano de carreira, Redistribuicao de tarefas' },
  { id: 3, colaborador: 'Pedro Almeida', score: 0.72, nivel: 'Alto', fatores: 'Distancia residencia, Horario', acoes: 'Transferencia de posto, Ajuste de escala' },
  { id: 4, colaborador: 'Lucas Ferreira', score: 0.68, nivel: 'Alto', fatores: 'Falta de treinamento', acoes: 'Inscricao em cursos, Mentoria' },
  { id: 5, colaborador: 'Camila Rodrigues', score: 0.55, nivel: 'Medio', fatores: 'Clima da equipe', acoes: 'Mediacao de conflitos' },
  { id: 6, colaborador: 'Joao Silva', score: 0.15, nivel: 'Baixo', fatores: '-', acoes: '-' },
];

const nivelCores: Record<string, string> = {
  'Baixo': 'bg-green-900/30 text-green-400',
  'Medio': 'bg-yellow-900/30 text-yellow-400',
  'Alto': 'bg-orange-900/30 text-orange-400',
  'Critico': 'bg-red-900/30 text-red-400',
};

const scoreCor = (s: number) => {
  if (s >= 0.8) return 'text-red-400';
  if (s >= 0.6) return 'text-orange-400';
  if (s >= 0.4) return 'text-yellow-400';
  return 'text-green-400';
};

export default function TurnoverPage() {
  const [colaboradores] = useState(colaboradoresMock);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" />
          Previsao de Turnover
        </h1>
        <p className="text-muted-foreground">Analise preditiva de risco de desligamento</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {distribuicao.map((d) => (
          <Card key={d.nivel}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{d.nivel}</p>
                  <p className={`text-3xl font-bold ${d.cor}`}>{d.count}</p>
                  <p className="text-xs text-muted-foreground mt-1">colaboradores</p>
                </div>
                <div className={`h-10 w-10 rounded-lg ${d.bgCor} flex items-center justify-center`}>
                  <d.icon className={`h-5 w-5 ${d.cor}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left p-4 text-muted-foreground font-medium">Colaborador</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Score de Risco</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Nivel</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Fatores Principais</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Acoes Sugeridas</th>
                </tr>
              </thead>
              <tbody>
                {colaboradores.map((c) => (
                  <tr key={c.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="p-4 font-medium">{c.colaborador}</td>
                    <td className="p-4 text-center"><span className={`font-mono font-bold ${scoreCor(c.score)}`}>{(c.score * 100).toFixed(0)}%</span></td>
                    <td className="p-4 text-center"><span className={`text-xs px-2 py-1 rounded ${nivelCores[c.nivel]}`}>{c.nivel}</span></td>
                    <td className="p-4 text-muted-foreground text-xs">{c.fatores}</td>
                    <td className="p-4 text-muted-foreground text-xs">{c.acoes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
