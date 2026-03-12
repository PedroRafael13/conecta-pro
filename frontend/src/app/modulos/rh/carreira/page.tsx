'use client';

import { TrendingUp, ArrowRight } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';

const planosMock = [
  { id: 1, colaborador: 'Joao Silva', cargoAtual: 'Vigilante', cargoAlvo: 'Supervisor de Seguranca', nivelAtual: 'Junior', nivelAlvo: 'Pleno', progresso: 65, status: 'Em Andamento', mentor: 'Carlos Mendes' },
  { id: 2, colaborador: 'Maria Santos', cargoAtual: 'Recepcionista', cargoAlvo: 'Coord. Portaria', nivelAtual: 'Pleno', nivelAlvo: 'Senior', progresso: 40, status: 'Em Andamento', mentor: 'Ana Beatriz' },
  { id: 3, colaborador: 'Roberto Lima', cargoAtual: 'Tecnico CFTV', cargoAlvo: 'Coord. Tecnico', nivelAtual: 'Pleno', nivelAlvo: 'Senior', progresso: 85, status: 'Em Andamento', mentor: 'Patricia Costa' },
  { id: 4, colaborador: 'Fernanda Oliveira', cargoAtual: 'Aux. Administrativo', cargoAlvo: 'Analista RH', nivelAtual: 'Junior', nivelAlvo: 'Pleno', progresso: 100, status: 'Concluido', mentor: 'Ana Beatriz' },
  { id: 5, colaborador: 'Marcos Silva', cargoAtual: 'Vigilante', cargoAlvo: 'Lider de Equipe', nivelAtual: 'Junior', nivelAlvo: 'Pleno', progresso: 20, status: 'Iniciado', mentor: 'Carlos Mendes' },
];

const statusCores: Record<string, string> = {
  'Iniciado': 'bg-blue-900/30 text-blue-400',
  'Em Andamento': 'bg-yellow-900/30 text-yellow-400',
  'Concluido': 'bg-green-900/30 text-green-400',
};

const progressoCor = (p: number) => {
  if (p >= 80) return 'bg-green-500';
  if (p >= 50) return 'bg-yellow-500';
  return 'bg-blue-500';
};

export default function CarreiraPage() {
  const [planos] = useState(planosMock);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <TrendingUp className="h-6 w-6" />
          Planos de Carreira
        </h1>
        <p className="text-muted-foreground">Desenvolvimento e progressao dos colaboradores</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left p-4 text-muted-foreground font-medium">Colaborador</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Cargo Atual</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Cargo Alvo</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Nivel</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Progresso</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Status</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Mentor</th>
                </tr>
              </thead>
              <tbody>
                {planos.map((p) => (
                  <tr key={p.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="p-4 font-medium">{p.colaborador}</td>
                    <td className="p-4 text-muted-foreground">{p.cargoAtual}</td>
                    <td className="p-4 text-muted-foreground">{p.cargoAlvo}</td>
                    <td className="p-4 text-center">
                      <span className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
                        {p.nivelAtual} <ArrowRight className="h-3 w-3" /> {p.nivelAlvo}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-800 rounded-full h-2">
                          <div className={`${progressoCor(p.progresso)} h-2 rounded-full transition-all`} style={{ width: `${p.progresso}%` }} />
                        </div>
                        <span className="text-xs font-medium w-8 text-right">{p.progresso}%</span>
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-1 rounded ${statusCores[p.status]}`}>{p.status}</span>
                    </td>
                    <td className="p-4 text-muted-foreground">{p.mentor}</td>
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
