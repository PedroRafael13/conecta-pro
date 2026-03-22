'use client';

import { useState, useEffect } from 'react';
import { BookOpen, Plus, Clock, Users, CheckCircle, XCircle, Loader2, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const API_BASE = '/api/v1/people-management/human-resources';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const categoriaCores: Record<string, string> = {
  mandatory_security: 'bg-red-900/30 text-red-400',
  mandatory_safety: 'bg-orange-900/30 text-orange-400',
  technical: 'bg-blue-900/30 text-blue-400',
  behavioral: 'bg-green-900/30 text-green-400',
  leadership: 'bg-purple-900/30 text-purple-400',
  compliance: 'bg-yellow-900/30 text-yellow-400',
  onboarding: 'bg-cyan-900/30 text-cyan-400',
  other: 'bg-gray-800 text-gray-400',
};

const categoriaLabels: Record<string, string> = {
  mandatory_security: 'Obrigatorio Seguranca',
  mandatory_safety: 'Obrigatorio SST',
  technical: 'Tecnico',
  behavioral: 'Comportamental',
  leadership: 'Lideranca',
  compliance: 'Compliance',
  onboarding: 'Integracao',
  other: 'Outros',
};

export default function CursosPage() {
  const [cursos, setCursos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: '', category: 'technical', duration_hours: 8,
    is_mandatory: false, description: '', validity_months: '' as string,
  });

  async function loadCursos() {
    try {
      const res = await fetch(`${API_BASE}/training/courses/?limit=50`, { headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        setCursos(data.items || data || []);
      }
    } catch { setCursos([]); } finally { setLoading(false); }
  }

  useEffect(() => { loadCursos(); }, []);

  async function handleSave() {
    if (!form.name.trim()) return;
    setSaving(true);
    try {
      const body: Record<string, unknown> = {
        name: form.name,
        category: form.category,
        duration_hours: form.duration_hours,
        is_mandatory: form.is_mandatory,
      };
      if (form.description) body.description = form.description;
      if (form.validity_months) body.validity_months = Number(form.validity_months);
      const res = await fetch(`${API_BASE}/training/courses`, {
        method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(body),
      });
      if (res.ok) {
        setShowModal(false);
        setForm({ name: '', category: 'technical', duration_hours: 8, is_mandatory: false, description: '', validity_months: '' });
        await loadCursos();
      }
    } catch { /* ignore */ } finally { setSaving(false); }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            Catalogo de Cursos
          </h1>
          <p className="text-muted-foreground">Cursos disponiveis para treinamento</p>
        </div>
        <Button onClick={() => setShowModal(true)}><Plus className="h-4 w-4 mr-2" />Novo Curso</Button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : cursos.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">Nenhum curso encontrado</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cursos.map((curso, i) => {
            const cat = curso.category || 'other';
            return (
              <Card key={curso.id || i} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{curso.name || curso.nome}</CardTitle>
                    {curso.is_mandatory && (
                      <span className="text-xs bg-red-900/30 text-red-400 px-2 py-0.5 rounded">Obrigatorio</span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <span className={`text-xs px-2 py-0.5 rounded ${categoriaCores[cat] || 'bg-gray-800 text-gray-400'}`}>
                    {categoriaLabels[cat] || cat}
                  </span>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{curso.duration_hours || '-'}h</span>
                    <span className="flex items-center gap-1"><Users className="h-3 w-3" />{curso.participants_count || 0}</span>
                  </div>
                  <div className="flex items-center gap-1 text-sm">
                    {curso.is_active !== false ? (
                      <><CheckCircle className="h-4 w-4 text-green-500" /><span className="text-green-500">Ativo</span></>
                    ) : (
                      <><XCircle className="h-4 w-4 text-gray-500" /><span className="text-gray-500">Inativo</span></>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-lg p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Novo Curso</h2>
              <button onClick={() => setShowModal(false)} type="button"><X className="h-5 w-5 text-gray-400 hover:text-white" /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-muted-foreground">Titulo *</label>
                <input className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                  value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Ex: Tecnicas de Portaria" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm text-muted-foreground">Categoria</label>
                  <select className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                    {Object.entries(categoriaLabels).map(([k, v]) => (
                      <option key={k} value={k}>{v}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Carga Horaria (h)</label>
                  <input type="number" min={1} className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    value={form.duration_hours} onChange={(e) => setForm({ ...form, duration_hours: Number(e.target.value) })} />
                </div>
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Descricao</label>
                <textarea className="w-full mt-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                  rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={form.is_mandatory} onChange={(e) => setForm({ ...form, is_mandatory: e.target.checked })} />
                  Obrigatorio
                </label>
                {form.is_mandatory && (
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-muted-foreground">Validade (meses):</label>
                    <input type="number" min={1} className="w-20 px-2 py-1 bg-gray-800 border border-gray-700 rounded text-sm"
                      value={form.validity_months} onChange={(e) => setForm({ ...form, validity_months: e.target.value })} />
                  </div>
                )}
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="outline" onClick={() => setShowModal(false)}>Cancelar</Button>
              <Button onClick={handleSave} disabled={saving || !form.name.trim()}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
                Salvar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
