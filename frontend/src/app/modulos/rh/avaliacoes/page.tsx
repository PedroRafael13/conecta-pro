'use client';

import { ClipboardCheck, Plus, Star } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const cicloAtivo = { nome: 'Avaliacao Q1 2026', periodo: 'Jan-Mar 2026', total: 44, concluidas: 21, prazo: '2026-03-31' };

const avaliacoesMock = [
  { id: 1, colaborador: 'Joao Silva', avaliador: 'Carlos Mendes', tipo: 'Trimestral', score: 8.5, status: 'Concluida' },
  { id: 2, colaborador: 'Maria Santos', avaliador: 'Carlos Mendes', tipo: 'Trimestral', score: null, status: 'Revisao Gestor' },
  { id: 3, colaborador: 'Roberto Lima', avaliador: 'Ana Beatriz', tipo: 'Trimestral', score: null, status: 'Auto-Avaliacao' },
  { id: 4, colaborador: 'Patricia Costa', avaliador: 'Ana Beatriz', tipo: 'Trimestral', score: 7.2, status: 'Concluida' },
  { id: 5, colaborador: 'Marcos Silva', avaliador: 'Carlos Mendes', tipo: 'Trimestral', score: null, status: 'Rascunho' },
  { id: 6, colaborador: 'Fernanda Oliveira', avaliador: 'Ana Beatriz', tipo: 'Mensal', score: 9.0, status: 'Concluida' },
];

const statusCores: Record<string, string> = {
  'Rascunho': 'bg-gray-800 text-gray-400',
  'Auto-Avaliacao': 'bg-blue-900/30 text-blue-400',
  'Revisao Gestor': 'bg-yellow-900/30 text-yellow-400',
  'Concluida': 'bg-green-900/30 text-green-400',
};

export default function AvaliacoesPage() {
  const [avaliacoes] = useState(avaliacoesMock);
  const pct = Math.round((cicloAtivo.concluidas / cicloAtivo.total) * 100);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ClipboardCheck className="h-6 w-6" />
            Avaliacoes de Desempenho
          </h1>
          <p className="text-muted-foreground">Ciclos de avaliacao e acompanhamento</p>
        </div>
        <Button><Plus className="h-4 w-4 mr-2" />Iniciar Ciclo de Avaliacao</Button>
      </div>

      <Card className="border-primary/30 bg-primary/5">
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{cicloAtivo.nome}</p>
              <p className="text-sm text-muted-foreground">Periodo: {cicloAtivo.periodo} | Prazo: {cicloAtivo.prazo}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold">{pct}%</p>
              <p className="text-xs text-muted-foreground">{cicloAtivo.concluidas}/{cicloAtivo.total} concluidas</p>
            </div>
          </div>
          <div className="mt-3 w-full bg-gray-800 rounded-full h-2">
            <div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${pct}%` }} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left p-4 text-muted-foreground font-medium">Colaborador</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Avaliador</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Tipo</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Score</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {avaliacoes.map((a) => (
                  <tr key={a.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="p-4 font-medium">{a.colaborador}</td>
                    <td className="p-4 text-muted-foreground">{a.avaliador}</td>
                    <td className="p-4 text-center text-muted-foreground">{a.tipo}</td>
                    <td className="p-4 text-center">
                      {a.score ? (
                        <span className="flex items-center justify-center gap-1"><Star className="h-3 w-3 text-yellow-400" />{a.score.toFixed(1)}</span>
                      ) : <span className="text-muted-foreground">-</span>}
                    </td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-1 rounded ${statusCores[a.status]}`}>{a.status}</span>
                    </td>
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
