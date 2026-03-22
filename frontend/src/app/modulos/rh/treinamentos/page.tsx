'use client';

import { useState, useEffect } from 'react';
import { GraduationCap, Plus, MapPin, Loader2, X } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const API_BASE = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const statusCores: Record<string, string> = {
  scheduled: 'bg-blue-900/30 text-blue-400',
  in_progress: 'bg-yellow-900/30 text-yellow-400',
  completed: 'bg-green-900/30 text-green-400',
  cancelled: 'bg-red-900/30 text-red-400',
};

const statusLabels: Record<string, string> = {
  scheduled: 'Agendado', in_progress: 'Em Andamento', completed: 'Concluido', cancelled: 'Cancelado',
};

export default function TreinamentosPage() {
  const [treinamentos, setTreinamentos] = useState<any[]>([]);
  const [cursos, setCursos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    course_id: '', title: '', start_date: '', end_date: '',
    instructor_name: '', location: '', max_participants: 20,
  });

  async function loadData() {
    try {
      const [tRes, cRes] = await Promise.all([
        fetch(`${API_BASE}/training/?limit=50`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/training/courses/?limit=50`, { headers: getAuthHeaders() }),
      ]);
      if (tRes.ok) {
        const data = await tRes.json();
        setTreinamentos(data.items || data || []);
      }
      if (cRes.ok) {
        const data = await cRes.json();
        setCursos(data.items || data || []);
      }
    } catch { /* ignore */ } finally { setLoading(false); }
  }

  useEffect(() => { loadData(); }, []);

  async function handleSave() {
    if (!form.course_id || !form.title || !form.start_date) return;
    setSaving(true);
    try {
      const body: Record<string, unknown> = {
        course_id: form.course_id,
        title: form.title,
        start_date: form.start_date + 'T08:00:00Z',
        max_participants: form.max_participants,
      };
      if (form.end_date) body.end_date = form.end_date + 'T17:00:00Z';
      if (form.instructor_name) body.instructor_name = form.instructor_name;
      if (form.location) body.location = form.location;
      const res = await fetch(`${API_BASE}/training/`, {
        method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(body),
      });
      if (res.ok) {
        setShowModal(false);
        setForm({ course_id: '', title: '', start_date: '', end_date: '', instructor_name: '', location: '', max_participants: 20 });
        await loadData();
      }
    } catch { /* ignore */ } finally { setSaving(false); }
  }

  function formatDate(d: string | null) {
    if (!d) return '-';
    try { return new Date(d).toLocaleDateString('pt-BR'); } catch { return d; }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            Treinamentos
          </h1>
          <p className="text-muted-foreground">Agenda e gestao de treinamentos</p>
        </div>
        <Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4 mr-2" />Agendar Treinamento</Button>
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
                    <th className="text-left p-4 text-muted-foreground font-medium">Curso</th>
                    <th className="text-left p-4 text-muted-foreground font-medium">Data Inicio</th>
                    <th className="text-left p-4 text-muted-foreground font-medium">Data Fim</th>
                    <th className="text-left p-4 text-muted-foreground font-medium">Local</th>
                    <th className="text-left p-4 text-muted-foreground font-medium">Instrutor</th>
                    <th className="text-center p-4 text-muted-foreground font-medium">Participantes</th>
                    <th className="text-center p-4 text-muted-foreground font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {treinamentos.length === 0 ? (
                    <tr><td colSpan={7} className="p-8 text-center text-muted-foreground">Nenhum treinamento encontrado</td></tr>
                  ) : treinamentos.map((t, i) => {
                    const label = statusLabels[t.status] || t.status;
                    const cor = statusCores[t.status] || 'bg-gray-800 text-gray-400';
                    return (
                      <tr key={t.id || i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                        <td className="p-4 font-medium">{t.title || t.course_name}</td>
                        <td className="p-4 text-muted-foreground">{formatDate(t.start_date)}</td>
                        <td className="p-4 text-muted-foreground">{formatDate(t.end_date)}</td>
                        <td className="p-4 text-muted-foreground"><span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{t.location || '-'}</span></td>
                        <td className="p-4 text-muted-foreground">{t.instructor_name || '-'}</td>
                        <td className="p-4 text-center">{t.current_participants || 0}/{t.max_participants || '-'}</td>
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
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-lg p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Agendar Treinamento</h2>
              <button onClick={() => setShowModal(false)} type="button"><X className="h-5 w-5 text-gray-400 hover:text-white" /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-muted-foreground">Curso *</label>
                <select className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                  value={form.course_id} onChange={(e) => {
                    const c = cursos.find((c) => c.id === e.target.value);
                    setForm({
                      ...form,
                      course_id: e.target.value,
                      title: c ? `${c.name} - Turma ${new Date().toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })}` : form.title,
                    });
                  }}>
                  <option value="">Selecione um curso</option>
                  {cursos.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} ({c.duration_hours}h)</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Titulo da Turma *</label>
                <input className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                  value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="Ex: NR-1 - Turma Abril/2026" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm text-muted-foreground">Data Inicio *</label>
                  <input type="date" className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Data Fim</label>
                  <input type="date" className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm text-muted-foreground">Instrutor</label>
                  <input className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    value={form.instructor_name} onChange={(e) => setForm({ ...form, instructor_name: e.target.value })}
                    placeholder="Nome do instrutor" />
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Vagas</label>
                  <input type="number" min={1} className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    value={form.max_participants} onChange={(e) => setForm({ ...form, max_participants: Number(e.target.value) })} />
                </div>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Local</label>
                <input className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                  value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })}
                  placeholder="Ex: Sala de treinamento Conecta Mais" />
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="outline" onClick={() => setShowModal(false)}>Cancelar</Button>
              <Button onClick={handleSave} disabled={saving || !form.course_id || !form.title || !form.start_date}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
                Agendar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
