'use client';

import { useState, useEffect } from 'react';
import { UserMinus, ArrowLeft, Inbox, Loader2, Plus, X, Save, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
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
  em_andamento: { label: 'Em Andamento', className: 'bg-yellow-500 text-white' },
  calculo_pendente: { label: 'Cálculo Pendente', className: 'bg-orange-500 text-white' },
  homologacao: { label: 'Homologação', className: 'bg-blue-500 text-white' },
  concluida: { label: 'Concluída', className: 'bg-green-500 text-white' },
  in_progress: { label: 'Em Andamento', className: 'bg-yellow-500 text-white' },
  pending: { label: 'Pendente', className: 'bg-orange-500 text-white' },
  completed: { label: 'Concluída', className: 'bg-green-500 text-white' },
};

const tipoConfig: Record<string, string> = {
  voluntaria: 'Voluntária',
  involuntaria: 'Involuntária',
  justa_causa: 'Justa Causa',
  acordo: 'Acordo Mútuo',
  voluntary: 'Voluntária',
  involuntary: 'Involuntária',
  just_cause: 'Justa Causa',
  mutual_agreement: 'Acordo Mútuo',
};

export default function RescisaoPage() {
  const router = useRouter();
  const [rescisões, setRescisões] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [formData, setFormData] = useState({ employee_id: '', employee_name: '', termination_type: 'voluntary', last_day: '', reason: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/terminations?page_size=50`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          setRescisões(data.items || data || []);
        }
        const empRes = await fetch(`${API_BASE}/employees?page_size=100`, { headers: getAuthHeaders() });
        if (empRes.ok) { const d = await empRes.json(); setEmployees(d.items || d || []); }
      } catch { setRescisões([]); } finally { setLoading(false); }
    }
    load();
  }, [reloadKey]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <UserMinus className="h-6 w-6" />
              Processos de Rescisão
            </h1>
            <p className="text-muted-foreground">Gerencie desligamentos e rescisões</p>
          </div>
        </div>
        <Button type="button" size="sm" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-1" /> Iniciar Rescisão</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Nova Rescisão</CardTitle>
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}><X className="h-4 w-4" /></Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Colaborador *</label>
                <select value={formData.employee_id} onChange={e => { const emp = employees.find((em: any) => em.id === e.target.value); setFormData(p => ({ ...p, employee_id: e.target.value, employee_name: emp?.nome || emp?.name || '' })); setFormErrors(p => ({ ...p, employee_id: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.employee_id ? 'border-red-500' : ''}`}>
                  <option value="">Selecione um colaborador</option>
                  {employees.map((emp: any) => <option key={emp.id} value={emp.id}>{emp.nome}</option>)}
                </select>
                {formErrors.employee_id && <p className="text-red-500 text-xs mt-1">{formErrors.employee_id}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Tipo de Rescisão *</label>
                <select value={formData.termination_type} onChange={e => setFormData(p => ({ ...p, termination_type: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm">
                  <option value="voluntary">Voluntária</option>
                  <option value="involuntary">Involuntária</option>
                  <option value="just_cause">Justa Causa</option>
                  <option value="mutual_agreement">Acordo Mútuo</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Último Dia de Trabalho *</label>
                <input type="date" value={formData.last_day} onChange={e => { setFormData(p => ({ ...p, last_day: e.target.value })); setFormErrors(p => ({ ...p, last_day: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.last_day ? 'border-red-500' : ''}`} />
                {formErrors.last_day && <p className="text-red-500 text-xs mt-1">{formErrors.last_day}</p>}
              </div>
              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-1 block">Motivo</label>
                <textarea value={formData.reason} onChange={e => setFormData(p => ({ ...p, reason: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" rows={3} placeholder="Motivo da rescisão" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={async () => {
                const errors: Record<string, string> = {};
                if (!formData.employee_id) errors.employee_id = 'Selecione um colaborador';
                if (!formData.last_day) errors.last_day = 'Data é obrigatória';
                if (Object.keys(errors).length > 0) { setFormErrors(errors); toast.error('Corrija os campos destacados'); return; }
                setSaving(true);
                try {
                  const res = await fetch(`${API_BASE}/terminations`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(formData) });
                  if (res.ok) { setShowForm(false); setFormData({ employee_id: '', employee_name: '', termination_type: 'voluntary', last_day: '', reason: '' }); setFormErrors({}); setReloadKey(k => k + 1); toast.success('Rescisão criada com sucesso'); }
                  else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao criar rescisão'); }
                } catch { toast.error('Erro de conexão'); } finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Criar Rescisão'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Rescisões</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
          ) : rescisões.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p className="font-medium">Nenhum processo de rescisão encontrado</p>
                  <p className="text-sm text-muted-foreground mt-1">Os processos aparecerão aqui quando iniciados.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Último Dia</TableHead>
                  <TableHead>Valor Total</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rescisões.map((item, i) => {
                  const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                  return (
                    <TableRow key={item.id || i}>
                      <TableCell className="font-medium">{item.nome || item.employee_name}</TableCell>
                      <TableCell>{tipoConfig[item.tipo || item.termination_type] || item.tipo || item.termination_type}</TableCell>
                      <TableCell><Badge className={st.className}>{st.label}</Badge></TableCell>
                      <TableCell>{item.ultimoDia || item.last_day ? new Date(item.ultimoDia || item.last_day).toLocaleDateString('pt-BR') : '-'}</TableCell>
                      <TableCell>R$ {(item.valorTotal || item.total_amount || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</TableCell>
                      <TableCell><Button variant="outline" size="sm">Detalhes</Button></TableCell>
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
