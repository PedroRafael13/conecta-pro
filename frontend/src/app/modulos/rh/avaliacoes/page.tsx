'use client';

import { useState, useEffect } from 'react';
import { ClipboardCheck, Plus, Star, Loader2, X, Save } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const API_BASE = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const statusCores: Record<string, string> = {
  'draft': 'bg-gray-800 text-gray-400',
  'Rascunho': 'bg-gray-800 text-gray-400',
  'self_assessment': 'bg-blue-900/30 text-blue-400',
  'Auto-Avaliacao': 'bg-blue-900/30 text-blue-400',
  'manager_review': 'bg-yellow-900/30 text-yellow-400',
  'Revisao Gestor': 'bg-yellow-900/30 text-yellow-400',
  'completed': 'bg-green-900/30 text-green-400',
  'Concluida': 'bg-green-900/30 text-green-400',
};

const statusLabels: Record<string, string> = {
  draft: 'Rascunho',
  self_assessment: 'Auto-Avaliacao',
  manager_review: 'Revisao Gestor',
  completed: 'Concluida',
};

export default function AvaliacoesPage() {
  const [avaliacoes, setAvaliacoes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({ employee_name: '', reviewer_name: '', review_type: 'quarterly', period_start: '', period_end: '' });

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/performance/reviews?limit=50`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          setAvaliacoes(data.items || data || []);
        }
      } catch { setAvaliacoes([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  const concluidas = avaliacoes.filter(a => a.status === 'completed' || a.status === 'Concluida').length;
  const total = avaliacoes.length;
  const pct = total > 0 ? Math.round((concluidas / total) * 100) : 0;

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
        <Button onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Iniciar Ciclo de Avaliacao</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Nova Avaliacao de Desempenho</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => setShowForm(false)}><X className="h-4 w-4" /></Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Colaborador *</label>
                <input type="text" value={formData.employee_name} onChange={e => setFormData(p => ({ ...p, employee_name: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm bg-background" placeholder="Nome do colaborador" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Avaliador *</label>
                <input type="text" value={formData.reviewer_name} onChange={e => setFormData(p => ({ ...p, reviewer_name: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm bg-background" placeholder="Nome do avaliador" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Tipo</label>
                <select value={formData.review_type} onChange={e => setFormData(p => ({ ...p, review_type: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm bg-background">
                  <option value="quarterly">Trimestral</option>
                  <option value="semi_annual">Semestral</option>
                  <option value="annual">Anual</option>
                  <option value="probation">Experiencia</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Periodo Inicio</label>
                <input type="date" value={formData.period_start} onChange={e => setFormData(p => ({ ...p, period_start: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm bg-background" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Periodo Fim</label>
                <input type="date" value={formData.period_end} onChange={e => setFormData(p => ({ ...p, period_end: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm bg-background" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button size="sm" disabled={saving || !formData.employee_name || !formData.reviewer_name} onClick={async () => {
                setSaving(true);
                try {
                  const res = await fetch(`${API_BASE}/performance/reviews`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(formData) });
                  if (res.ok) { const newReview = await res.json(); setAvaliacoes(prev => [newReview, ...prev]); setShowForm(false); setFormData({ employee_name: '', reviewer_name: '', review_type: 'quarterly', period_start: '', period_end: '' }); }
                } catch {} finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Criar Avaliacao'}
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
          <Card className="border-primary/30 bg-primary/5">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Ciclo de Avaliacoes</p>
                  <p className="text-sm text-muted-foreground">{total} avaliacoes registradas</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">{pct}%</p>
                  <p className="text-xs text-muted-foreground">{concluidas}/{total} concluidas</p>
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
                    {avaliacoes.length === 0 ? (
                      <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Nenhuma avaliacao encontrada</td></tr>
                    ) : avaliacoes.map((a, i) => {
                      const label = statusLabels[a.status] || a.status;
                      const cor = statusCores[a.status] || statusCores[label] || 'bg-gray-800 text-gray-400';
                      return (
                        <tr key={a.id || i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                          <td className="p-4 font-medium">{a.employee_name || a.colaborador}</td>
                          <td className="p-4 text-muted-foreground">{a.reviewer_name || a.avaliador}</td>
                          <td className="p-4 text-center text-muted-foreground">{a.review_type || a.tipo || 'Trimestral'}</td>
                          <td className="p-4 text-center">
                            {a.overall_score || a.score ? (
                              <span className="flex items-center justify-center gap-1"><Star className="h-3 w-3 text-yellow-400" />{(a.overall_score || a.score).toFixed?.(1) || a.overall_score || a.score}</span>
                            ) : <span className="text-muted-foreground">-</span>}
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
