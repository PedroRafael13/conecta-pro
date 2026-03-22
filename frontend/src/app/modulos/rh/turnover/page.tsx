'use client';

import { useState, useEffect } from 'react';
import { Users, AlertTriangle, AlertCircle, CheckCircle, XOctagon, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

const API_BASE = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const nivelCores: Record<string, string> = {
  'Baixo': 'bg-green-900/30 text-green-400', 'low': 'bg-green-900/30 text-green-400',
  'Medio': 'bg-yellow-900/30 text-yellow-400', 'medium': 'bg-yellow-900/30 text-yellow-400',
  'Alto': 'bg-orange-900/30 text-orange-400', 'high': 'bg-orange-900/30 text-orange-400',
  'Critico': 'bg-red-900/30 text-red-400', 'critical': 'bg-red-900/30 text-red-400',
};

const nivelLabels: Record<string, string> = { low: 'Baixo', medium: 'Medio', high: 'Alto', critical: 'Critico' };

const scoreCor = (s: number) => {
  if (s >= 0.8) return 'text-red-400';
  if (s >= 0.6) return 'text-orange-400';
  if (s >= 0.4) return 'text-yellow-400';
  return 'text-green-400';
};

export default function TurnoverPage() {
  const [colaboradores, setColaboradores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/turnover/?limit=50`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          setColaboradores(data.items || data.predictions || data || []);
        }
      } catch { setColaboradores([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  const distribuicao = [
    { nivel: 'Baixo', key: ['Baixo', 'low'], cor: 'text-green-400', bgCor: 'bg-green-900/30', icon: CheckCircle },
    { nivel: 'Medio', key: ['Medio', 'medium'], cor: 'text-yellow-400', bgCor: 'bg-yellow-900/30', icon: AlertCircle },
    { nivel: 'Alto', key: ['Alto', 'high'], cor: 'text-orange-400', bgCor: 'bg-orange-900/30', icon: AlertTriangle },
    { nivel: 'Critico', key: ['Critico', 'critical'], cor: 'text-red-400', bgCor: 'bg-red-900/30', icon: XOctagon },
  ].map(d => ({ ...d, count: colaboradores.filter(c => d.key.includes(c.nivel || c.risk_level)).length }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" />
          Previsao de Turnover
        </h1>
        <p className="text-muted-foreground">Analise preditiva de risco de desligamento</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
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
                    {colaboradores.length === 0 ? (
                      <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Nenhuma previsao de turnover disponivel</td></tr>
                    ) : colaboradores.map((c, i) => {
                      const nivel = nivelLabels[c.risk_level] || c.nivel || c.risk_level;
                      const cor = nivelCores[c.risk_level || c.nivel] || 'bg-gray-800 text-gray-400';
                      const score = c.score || c.risk_score || 0;
                      return (
                        <tr key={c.id || i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                          <td className="p-4 font-medium">{c.employee_name || c.colaborador}</td>
                          <td className="p-4 text-center"><span className={`font-mono font-bold ${scoreCor(score)}`}>{(score * 100).toFixed(0)}%</span></td>
                          <td className="p-4 text-center"><span className={`text-xs px-2 py-1 rounded ${cor}`}>{nivel}</span></td>
                          <td className="p-4 text-muted-foreground text-xs">{c.factors || c.fatores || '-'}</td>
                          <td className="p-4 text-muted-foreground text-xs">{c.suggested_actions || c.acoes || '-'}</td>
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
