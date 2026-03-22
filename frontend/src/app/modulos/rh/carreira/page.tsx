'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, ArrowRight, Loader2 } from 'lucide-react';
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
  'Iniciado': 'bg-blue-900/30 text-blue-400',
  'Em Andamento': 'bg-yellow-900/30 text-yellow-400',
  'Concluido': 'bg-green-900/30 text-green-400',
  'in_progress': 'bg-yellow-900/30 text-yellow-400',
  'started': 'bg-blue-900/30 text-blue-400',
  'completed': 'bg-green-900/30 text-green-400',
};

const statusLabels: Record<string, string> = {
  in_progress: 'Em Andamento',
  started: 'Iniciado',
  completed: 'Concluido',
};

const progressoCor = (p: number) => {
  if (p >= 80) return 'bg-green-500';
  if (p >= 50) return 'bg-yellow-500';
  return 'bg-blue-500';
};

export default function CarreiraPage() {
  const [planos, setPlanos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/career/plans/?limit=50`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          setPlanos(data.items || data || []);
        }
      } catch { setPlanos([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <TrendingUp className="h-6 w-6" />
          Planos de Carreira
        </h1>
        <p className="text-muted-foreground">Desenvolvimento e progressao dos colaboradores</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
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
                  {planos.length === 0 ? (
                    <tr><td colSpan={7} className="p-8 text-center text-muted-foreground">Nenhum plano de carreira encontrado</td></tr>
                  ) : planos.map((p, i) => {
                    const status = statusLabels[p.status] || p.status;
                    const cor = statusCores[p.status] || statusCores[status] || 'bg-gray-800 text-gray-400';
                    const prog = p.progress || p.progresso || 0;
                    return (
                      <tr key={p.id || i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                        <td className="p-4 font-medium">{p.employee_name || p.colaborador}</td>
                        <td className="p-4 text-muted-foreground">{p.current_position || p.cargoAtual}</td>
                        <td className="p-4 text-muted-foreground">{p.target_position || p.cargoAlvo}</td>
                        <td className="p-4 text-center">
                          <span className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
                            {p.current_level || p.nivelAtual || '-'} <ArrowRight className="h-3 w-3" /> {p.target_level || p.nivelAlvo || '-'}
                          </span>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-800 rounded-full h-2">
                              <div className={`${progressoCor(prog)} h-2 rounded-full transition-all`} style={{ width: `${prog}%` }} />
                            </div>
                            <span className="text-xs font-medium w-8 text-right">{prog}%</span>
                          </div>
                        </td>
                        <td className="p-4 text-center">
                          <span className={`text-xs px-2 py-1 rounded ${cor}`}>{status}</span>
                        </td>
                        <td className="p-4 text-muted-foreground">{p.mentor_name || p.mentor || '-'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
