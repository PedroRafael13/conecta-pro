'use client';

import { useState, useEffect } from 'react';
import { UserPlus, Filter, ArrowLeft, Inbox, Loader2, X, Save, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { validateCPF, formatCPF } from '@/utils/validators';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const API_BASE = '/api/v1/people-management/hr';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? (localStorage.getItem('access_token') || localStorage.getItem('access_token') || localStorage.getItem('token')) : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const statusConfig: Record<string, { label: string; className: string }> = {
  documents_pending: { label: 'Documentos Pendentes', className: 'bg-yellow-500 text-white' },
  medical_exam: { label: 'Exame Médico', className: 'bg-blue-500 text-white' },
  contract_signing: { label: 'Assinatura de Contrato', className: 'bg-orange-500 text-white' },
  in_progress: { label: 'Em Andamento', className: 'bg-cyan-500 text-white' },
  completed: { label: 'Concluída', className: 'bg-green-500 text-white' },
  cancelled: { label: 'Cancelada', className: 'bg-red-500 text-white' },
};

export default function AdmissaoPage() {
  const router = useRouter();
  const [filtroStatus, setFiltroStatus] = useState<string>('todos');
  const [admissoes, setAdmissoes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({ candidate_name: '', cpf: '', position: '', expected_date: '', department: '', salary: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const url = filtroStatus === 'todos'
          ? `${API_BASE}/admissions?page_size=50`
          : `${API_BASE}/admissions?status=${filtroStatus}&page_size=50`;
        const res = await fetch(url, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          setAdmissoes(data.items || data || []);
        }
      } catch { setAdmissoes([]); } finally { setLoading(false); }
    }
    load();
  }, [filtroStatus, refreshKey]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <UserPlus className="h-6 w-6" />
              Admissão de Colaboradores
            </h1>
            <p className="text-muted-foreground">Gerencie processos de admissão</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button type="button" variant="outline" size="sm" onClick={() => setFiltroStatus('todos')}>
            <Filter className="h-4 w-4 mr-1" /> Todos
          </Button>
          <Button type="button" size="sm" onClick={() => setShowForm(true)}><UserPlus className="h-4 w-4 mr-1" /> Nova Admissão</Button>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {Object.entries(statusConfig).map(([key, val]) => (
          <Badge
            key={key}
            className={`cursor-pointer ${filtroStatus === key ? val.className : 'bg-muted text-muted-foreground'}`}
            onClick={() => setFiltroStatus(key)}
          >
            {val.label}
          </Badge>
        ))}
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Nova Admissão</CardTitle>
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}><X className="h-4 w-4" /></Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Nome do Candidato *</label>
                <input type="text" value={formData.candidate_name} onChange={e => { setFormData(p => ({ ...p, candidate_name: e.target.value })); setFormErrors(p => ({ ...p, candidate_name: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.candidate_name ? 'border-red-500' : ''}`} placeholder="Nome completo" />
                {formErrors.candidate_name && <p className="text-red-500 text-xs mt-1">{formErrors.candidate_name}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">CPF *</label>
                <input type="text" value={formData.cpf} onChange={e => { const formatted = formatCPF(e.target.value); setFormData(p => ({ ...p, cpf: formatted })); setFormErrors(p => ({ ...p, cpf: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.cpf ? 'border-red-500' : ''}`} placeholder="000.000.000-00" maxLength={14} />
                {formErrors.cpf && <p className="text-red-500 text-xs mt-1">{formErrors.cpf}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Cargo *</label>
                <input type="text" value={formData.position} onChange={e => { setFormData(p => ({ ...p, position: e.target.value })); setFormErrors(p => ({ ...p, position: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.position ? 'border-red-500' : ''}`} placeholder="Ex: Vigilante" />
                {formErrors.position && <p className="text-red-500 text-xs mt-1">{formErrors.position}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Departamento</label>
                <input type="text" value={formData.department} onChange={e => setFormData(p => ({ ...p, department: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="Ex: Operações" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Data Prevista de Admissão *</label>
                <input type="date" value={formData.expected_date} onChange={e => { setFormData(p => ({ ...p, expected_date: e.target.value })); setFormErrors(p => ({ ...p, expected_date: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.expected_date ? 'border-red-500' : ''}`} />
                {formErrors.expected_date && <p className="text-red-500 text-xs mt-1">{formErrors.expected_date}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Salário Base</label>
                <input type="number" step="0.01" value={formData.salary} onChange={e => setFormData(p => ({ ...p, salary: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="0.00" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={async () => {
                const errors: Record<string, string> = {};
                if (!formData.candidate_name.trim()) errors.candidate_name = 'Nome é obrigatório';
                if (!formData.cpf.trim()) errors.cpf = 'CPF é obrigatório';
                else if (!validateCPF(formData.cpf)) errors.cpf = 'CPF inválido';
                if (!formData.position.trim()) errors.position = 'Cargo é obrigatório';
                if (!formData.expected_date) errors.expected_date = 'Data de admissão é obrigatória';
                if (Object.keys(errors).length > 0) { setFormErrors(errors); toast.error('Corrija os campos destacados'); return; }
                setSaving(true);
                try {
                  const payload = {
                    candidate_name: formData.candidate_name,
                    cpf: formData.cpf,
                    position: formData.position,
                    department: formData.department || undefined,
                    expected_start_date: formData.expected_date || undefined,
                    salary_proposed: formData.salary ? parseFloat(formData.salary) : undefined,
                  };
                  const res = await fetch(`${API_BASE}/admissions`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(payload) });
                  if (res.ok) { setShowForm(false); setFormData({ candidate_name: '', cpf: '', position: '', expected_date: '', department: '', salary: '' }); setFormErrors({}); setRefreshKey(k => k + 1); toast.success('Admissão criada com sucesso!'); }
                  else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao criar admissão'); }
                } catch { toast.error('Erro de conexão'); } finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Criar Admissão'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Processos de Admissão</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
          ) : admissoes.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p className="font-medium">Nenhum processo de admissão encontrado</p>
                  <p className="text-sm text-muted-foreground mt-1">Clique em "Nova Admissão" para iniciar um processo.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>CPF</TableHead>
                  <TableHead>Cargo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Data Prevista</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(filtroStatus === 'todos' ? admissoes : admissoes.filter(a => a.status === filtroStatus)).map((item, i) => {
                  const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                  return (
                    <TableRow key={item.id || i}>
                      <TableCell className="font-medium">{item.candidate_name || '-'}</TableCell>
                      <TableCell>{item.cpf || '-'}</TableCell>
                      <TableCell>{item.position || '-'}</TableCell>
                      <TableCell><Badge className={st.className}>{st.label}</Badge></TableCell>
                      <TableCell>{item.expected_start_date ? (() => { const p = String(item.expected_start_date).split('-'); return p.length === 3 ? `${p[2]}/${p[1]}/${p[0]}` : '-'; })() : '-'}</TableCell>
                      <TableCell><Button variant="outline" size="sm" onClick={() => router.push(`/modulos/dp/admissao/${item.id}`)}>Detalhes</Button></TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
