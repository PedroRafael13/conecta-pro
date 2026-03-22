'use client';

import { useState, useEffect } from 'react';
import { UserPlus, CheckCircle, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const statusCores: Record<string, string> = {
  'Iniciado': 'bg-blue-900/30 text-blue-400', 'started': 'bg-blue-900/30 text-blue-400',
  'Em Andamento': 'bg-yellow-900/30 text-yellow-400', 'in_progress': 'bg-yellow-900/30 text-yellow-400',
  'Concluido': 'bg-green-900/30 text-green-400', 'completed': 'bg-green-900/30 text-green-400',
};

const statusLabels: Record<string, string> = { started: 'Iniciado', in_progress: 'Em Andamento', completed: 'Concluido' };

const progressoCor = (p: number) => {
  if (p >= 80) return 'bg-green-500';
  if (p >= 50) return 'bg-yellow-500';
  return 'bg-blue-500';
};

export default function OnboardingPage() {
  const [colaboradores, setColaboradores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/onboarding/?limit=50`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          setColaboradores(data.items || data || []);
        }
      } catch { setColaboradores([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  const inProgress = colaboradores.filter(c => c.status !== 'completed' && c.status !== 'Concluido').length;
  const completed = colaboradores.filter(c => c.status === 'completed' || c.status === 'Concluido').length;
  const avgProgress = colaboradores.length > 0
    ? Math.round(colaboradores.reduce((a, c) => a + (c.progress || c.progresso || 0), 0) / colaboradores.length)
    : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <UserPlus className="h-6 w-6" />
          Onboarding de Novos Colaboradores
        </h1>
        <p className="text-muted-foreground">Acompanhamento da integracao de novos colaboradores</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Em Onboarding</p>
                <p className="text-2xl font-bold">{inProgress}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Concluidos</p>
                <p className="text-2xl font-bold">{completed}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">Progresso Medio</p>
                <p className="text-2xl font-bold">{avgProgress}%</p>
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
                    {colaboradores.length === 0 ? (
                      <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Nenhum onboarding em andamento</td></tr>
                    ) : colaboradores.map((c, i) => {
                      const prog = c.progress || c.progresso || 0;
                      const label = statusLabels[c.status] || c.status;
                      const cor = statusCores[c.status] || statusCores[label] || 'bg-gray-800 text-gray-400';
                      const steps = c.completed_steps || c.etapasCompletas || 0;
                      const total = c.total_steps || c.etapasTotal || 8;
                      return (
                        <tr key={c.id || i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                          <td className="p-4 font-medium">{c.employee_name || c.colaborador}</td>
                          <td className="p-4 text-muted-foreground">{c.admission_date || c.dataAdmissao}</td>
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-800 rounded-full h-2">
                                <div className={`${progressoCor(prog)} h-2 rounded-full transition-all`} style={{ width: `${prog}%` }} />
                              </div>
                              <span className="text-xs font-medium w-8 text-right">{prog}%</span>
                            </div>
                          </td>
                          <td className="p-4 text-center">
                            <span className="flex items-center justify-center gap-1">
                              <CheckCircle className={`h-3 w-3 ${steps === total ? 'text-green-400' : 'text-muted-foreground'}`} />
                              {steps}/{total}
                            </span>
                          </td>
                          <td className="p-4 text-center">
                            <span className={`text-xs px-2 py-1 rounded ${cor}`}>{label}</span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
