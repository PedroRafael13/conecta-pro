'use client';

import { UserPlus, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';

const onboardingMock = [
  { id: 1, colaborador: 'Lucas Ferreira', dataAdmissao: '2026-03-01', progresso: 75, etapasCompletas: 6, etapasTotal: 8, status: 'Em Andamento' },
  { id: 2, colaborador: 'Camila Rodrigues', dataAdmissao: '2026-03-05', progresso: 50, etapasCompletas: 4, etapasTotal: 8, status: 'Em Andamento' },
  { id: 3, colaborador: 'Pedro Almeida', dataAdmissao: '2026-02-15', progresso: 100, etapasCompletas: 8, etapasTotal: 8, status: 'Concluido' },
  { id: 4, colaborador: 'Julia Nascimento', dataAdmissao: '2026-03-10', progresso: 25, etapasCompletas: 2, etapasTotal: 8, status: 'Em Andamento' },
  { id: 5, colaborador: 'Thiago Barbosa', dataAdmissao: '2026-03-11', progresso: 12, etapasCompletas: 1, etapasTotal: 8, status: 'Iniciado' },
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

export default function OnboardingPage() {
  const [colaboradores] = useState(onboardingMock);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <UserPlus className="h-6 w-6" />
          Onboarding de Novos Colaboradores
        </h1>
        <p className="text-muted-foreground">Acompanhamento da integracao de novos colaboradores</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Em Onboarding</p>
            <p className="text-2xl font-bold">{colaboradores.filter(c => c.status !== 'Concluido').length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Concluidos (Mar/2026)</p>
            <p className="text-2xl font-bold">{colaboradores.filter(c => c.status === 'Concluido').length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Progresso Medio</p>
            <p className="text-2xl font-bold">{Math.round(colaboradores.reduce((a, c) => a + c.progresso, 0) / colaboradores.length)}%</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left p-4 text-muted-foreground font-medium">Colaborador</th>
                  <th className="text-left p-4 text-muted-foreground font-medium">Data Admissao</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Progresso</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Etapas</th>
                  <th className="text-center p-4 text-muted-foreground font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {colaboradores.map((c) => (
                  <tr key={c.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="p-4 font-medium">{c.colaborador}</td>
                    <td className="p-4 text-muted-foreground">{c.dataAdmissao}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-800 rounded-full h-2">
                          <div className={`${progressoCor(c.progresso)} h-2 rounded-full transition-all`} style={{ width: `${c.progresso}%` }} />
                        </div>
                        <span className="text-xs font-medium w-8 text-right">{c.progresso}%</span>
                      </div>
                    </td>
                    <td className="p-4 text-center">
                      <span className="flex items-center justify-center gap-1">
                        <CheckCircle className={`h-3 w-3 ${c.etapasCompletas === c.etapasTotal ? 'text-green-400' : 'text-muted-foreground'}`} />
                        {c.etapasCompletas}/{c.etapasTotal}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-1 rounded ${statusCores[c.status]}`}>{c.status}</span>
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
