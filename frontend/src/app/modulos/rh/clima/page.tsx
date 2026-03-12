'use client';

import { Heart } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const scoreGeral = 78;

const dimensoes = [
  { nome: 'Carreira', score: 72, cor: 'bg-blue-500' },
  { nome: 'Lideranca', score: 81, cor: 'bg-green-500' },
  { nome: 'Ambiente', score: 85, cor: 'bg-teal-500' },
  { nome: 'Comunicacao', score: 74, cor: 'bg-yellow-500' },
  { nome: 'Beneficios', score: 68, cor: 'bg-purple-500' },
];

const pesquisasMock = [
  { id: 1, nome: 'Pesquisa Clima Q1 2026', periodo: 'Jan-Mar 2026', respostas: 38, total: 44, score: 78, status: 'Em Andamento' },
  { id: 2, nome: 'Pesquisa Clima Q4 2025', periodo: 'Out-Dez 2025', respostas: 42, total: 44, score: 75, status: 'Concluida' },
  { id: 3, nome: 'Pesquisa Clima Q3 2025', periodo: 'Jul-Set 2025', respostas: 40, total: 42, score: 72, status: 'Concluida' },
];

const statusCores: Record<string, string> = {
  'Em Andamento': 'bg-yellow-900/30 text-yellow-400',
  'Concluida': 'bg-green-900/30 text-green-400',
};

const scoreCor = (s: number) => {
  if (s >= 80) return 'text-green-400';
  if (s >= 60) return 'text-yellow-400';
  return 'text-red-400';
};

export default function ClimaPage() {
  const [pesquisas] = useState(pesquisasMock);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Heart className="h-6 w-6" />
          Clima Organizacional
        </h1>
        <p className="text-muted-foreground">Pesquisas e indicadores de clima</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-sm font-medium">Score Geral</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-col items-center">
              <span className={`text-6xl font-bold ${scoreCor(scoreGeral)}`}>{scoreGeral}</span>
              <span className="text-muted-foreground text-sm mt-1">de 100 pontos</span>
              <div className="w-full mt-4 bg-gray-800 rounded-full h-3">
                <div className={`h-3 rounded-full transition-all ${scoreGeral >= 80 ? 'bg-green-500' : 'bg-yellow-500'}`} style={{ width: `${scoreGeral}%` }} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-sm font-medium">Dimensoes</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {dimensoes.map((d) => (
              <div key={d.nome} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>{d.nome}</span>
                  <span className={scoreCor(d.score)}>{d.score}</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div className={`${d.cor} h-2 rounded-full transition-all`} style={{ width: `${d.score}%` }} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left p-4 text-muted-foreground font-medium">Pesquisa</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Periodo</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Respostas</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Score Medio</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {pesquisas.map((p) => (
                  <tr key={p.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="p-4 font-medium">{p.nome}</td>
                    <td className="p-4 text-muted-foreground">{p.periodo}</td>
                    <td className="p-4 text-center">{p.respostas}/{p.total}</td>
                    <td className="p-4 text-center"><span className={scoreCor(p.score)}>{p.score}</span></td>
                    <td className="p-4 text-center"><span className={`text-xs px-2 py-1 rounded ${statusCores[p.status]}`}>{p.status}</span></td>
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
