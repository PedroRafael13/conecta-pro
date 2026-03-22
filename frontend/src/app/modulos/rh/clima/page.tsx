'use client';

import { useState, useEffect } from 'react';
import { Heart, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const statusCores: Record<string, string> = {
  'Em Andamento': 'bg-yellow-900/30 text-yellow-400',
  'Concluida': 'bg-green-900/30 text-green-400',
  'in_progress': 'bg-yellow-900/30 text-yellow-400',
  'completed': 'bg-green-900/30 text-green-400',
  'active': 'bg-yellow-900/30 text-yellow-400',
};

const scoreCor = (s: number) => {
  if (s >= 80) return 'text-green-400';
  if (s >= 60) return 'text-yellow-400';
  return 'text-red-400';
};

export default function ClimaPage() {
  const [pesquisas, setPesquisas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        // Climate surveys from retention/climate module re-exported via human-resources
        const res = await fetch(`${API_BASE}/climate/?limit=50`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          setPesquisas(data.items || data || []);
        }
      } catch { setPesquisas([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  const scoreGeral = pesquisas.length > 0
    ? Math.round(pesquisas.reduce((a, p) => a + (p.score || p.overall_score || 0), 0) / pesquisas.length)
    : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Heart className="h-6 w-6" />
          Clima Organizacional
        </h1>
        <p className="text-muted-foreground">Pesquisas e indicadores de clima</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
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
              <CardHeader><CardTitle className="text-sm font-medium">Resumo</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>Total de pesquisas: <span className="font-bold text-white">{pesquisas.length}</span></p>
                  <p>Pesquisas ativas: <span className="font-bold text-white">{pesquisas.filter(p => p.status === 'active' || p.status === 'in_progress' || p.status === 'Em Andamento').length}</span></p>
                  <p>Concluidas: <span className="font-bold text-white">{pesquisas.filter(p => p.status === 'completed' || p.status === 'Concluida').length}</span></p>
                </div>
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
                    {pesquisas.length === 0 ? (
                      <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Nenhuma pesquisa de clima encontrada</td></tr>
                    ) : pesquisas.map((p, i) => {
                      const cor = statusCores[p.status] || 'bg-gray-800 text-gray-400';
                      const label = p.status === 'completed' ? 'Concluida' : p.status === 'in_progress' || p.status === 'active' ? 'Em Andamento' : p.status;
                      return (
                        <tr key={p.id || i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                          <td className="p-4 font-medium">{p.name || p.nome || p.title}</td>
                          <td className="p-4 text-muted-foreground">{p.period || p.periodo || '-'}</td>
                          <td className="p-4 text-center">{p.responses || p.respostas || 0}/{p.total_employees || p.total || '-'}</td>
                          <td className="p-4 text-center"><span className={scoreCor(p.score || p.overall_score || 0)}>{p.score || p.overall_score || 0}</span></td>
                          <td className="p-4 text-center"><span className={`text-xs px-2 py-1 rounded ${cor}`}>{label}</span></td>
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
