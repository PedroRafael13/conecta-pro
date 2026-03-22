'use client';

import { useState, useEffect } from 'react';
import { Sun, ArrowLeft, Inbox, Loader2, Plus, X, Save } from 'lucide-react';
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
  programada: { label: 'Programada', className: 'bg-blue-500 text-white' },
  em_gozo: { label: 'Em Gozo', className: 'bg-green-500 text-white' },
  vencida: { label: 'Vencida', className: 'bg-red-500 text-white' },
  concluida: { label: 'Concluída', className: 'bg-gray-500 text-white' },
  scheduled: { label: 'Programada', className: 'bg-blue-500 text-white' },
  in_progress: { label: 'Em Gozo', className: 'bg-green-500 text-white' },
  overdue: { label: 'Vencida', className: 'bg-red-500 text-white' },
  completed: { label: 'Concluída', className: 'bg-gray-500 text-white' },
};

export default function FeriasPage() {
  const router = useRouter();
  const [ferias, setFerias] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [formData, setFormData] = useState({ employee_id: '', start_date: '', end_date: '', days_count: '30', sell_days: false, sell_days_count: '0', notes: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    async function load() {
      try {
        // Fetch employees and their vacation balances
        const empRes = await fetch(`${API_BASE}/employees?limit=100`, { headers: getAuthHeaders() });
        if (empRes.ok) {
          const empData = await empRes.json();
          const emps = empData.items || empData || [];
          setEmployees(emps);
          const balances = await Promise.all(
            emps.slice(0, 30).map(async (emp: any) => {
              try {
                const balRes = await fetch(`${API_BASE}/vacations/employee/${emp.id}/balance`, { headers: getAuthHeaders() });
                if (balRes.ok) {
                  const bal = await balRes.json();
                  return {
                    colaborador: emp.nome || emp.name,
                    periodoAquisitivo: bal.periodo_aquisitivo || '-',
                    diasDireito: bal.dias_direito || 30,
                    diasGozados: bal.dias_gozados || 0,
                    saldo: bal.dias_saldo || bal.saldo || 0,
                    status: bal.status || (bal.dias_saldo > 0 ? 'programada' : 'concluida'),
                  };
                }
              } catch { /* skip */ }
              return null;
            })
          );
          setFerias(balances.filter(Boolean));
        }
      } catch { setFerias([]); } finally { setLoading(false); }
    }
    load();
  }, [reloadKey]);

  const statusCounts = Object.entries(statusConfig).reduce((acc, [key]) => {
    acc[key] = ferias.filter(f => f.status === key).length;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Sun className="h-6 w-6" />
              Gestão de Férias
            </h1>
            <p className="text-muted-foreground">Programação e controle de férias dos colaboradores</p>
          </div>
        </div>
        <Button type="button" size="sm" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-1" /> Programar Férias</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Programar Férias</CardTitle>
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}><X className="h-4 w-4" /></Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Colaborador *</label>
                <select value={formData.employee_id} onChange={e => { setFormData(p => ({ ...p, employee_id: e.target.value })); setFormErrors(p => ({ ...p, employee_id: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.employee_id ? 'border-red-500' : ''}`}>
                  <option value="">Selecione um colaborador</option>
                  {employees.map((emp: any) => <option key={emp.id} value={emp.id}>{emp.nome}</option>)}
                </select>
                {formErrors.employee_id && <p className="text-red-500 text-xs mt-1">{formErrors.employee_id}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Data Início *</label>
                <input type="date" value={formData.start_date} onChange={e => { setFormData(p => ({ ...p, start_date: e.target.value })); setFormErrors(p => ({ ...p, start_date: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.start_date ? 'border-red-500' : ''}`} />
                {formErrors.start_date && <p className="text-red-500 text-xs mt-1">{formErrors.start_date}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Data Fim *</label>
                <input type="date" value={formData.end_date} onChange={e => { setFormData(p => ({ ...p, end_date: e.target.value })); setFormErrors(p => ({ ...p, end_date: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.end_date ? 'border-red-500' : ''}`} />
                {formErrors.end_date && <p className="text-red-500 text-xs mt-1">{formErrors.end_date}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Dias de Férias</label>
                <input type="number" value={formData.days_count} onChange={e => setFormData(p => ({ ...p, days_count: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="30" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 flex items-center gap-2">
                  <input type="checkbox" checked={formData.sell_days} onChange={e => setFormData(p => ({ ...p, sell_days: e.target.checked, sell_days_count: e.target.checked ? p.sell_days_count : '0' }))} />
                  <div>
                    <span className="block">Abono Pecuniário</span>
                    <span className="text-xs text-muted-foreground font-normal">Converter até 1/3 dos dias de férias em pagamento</span>
                  </div>
                </label>
              </div>
              {formData.sell_days && (
                <div>
                  <label className="text-sm font-medium mb-1 block">Dias de Abono</label>
                  <input type="number" value={formData.sell_days_count} onChange={e => setFormData(p => ({ ...p, sell_days_count: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="10" />
                </div>
              )}
              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-1 block">Observações</label>
                <textarea value={formData.notes} onChange={e => setFormData(p => ({ ...p, notes: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" rows={3} placeholder="Observações sobre as férias" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={async () => {
                const errors: Record<string, string> = {};
                if (!formData.employee_id) errors.employee_id = 'Selecione um colaborador';
                if (!formData.start_date) errors.start_date = 'Data de início é obrigatória';
                if (!formData.end_date) errors.end_date = 'Data de fim é obrigatória';
                if (Object.keys(errors).length > 0) { setFormErrors(errors); toast.error('Corrija os campos destacados'); return; }
                setSaving(true);
                try {
                  const res = await fetch(`${API_BASE}/vacations/vacations/`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(formData) });
                  if (res.ok) { setShowForm(false); setFormData({ employee_id: '', start_date: '', end_date: '', days_count: '30', sell_days: false, sell_days_count: '0', notes: '' }); setFormErrors({}); setReloadKey(k => k + 1); toast.success('Férias programadas com sucesso'); }
                  else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao programar férias'); }
                } catch { toast.error('Erro de conexão'); } finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Programar Férias'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            {['programada', 'em_gozo', 'vencida', 'concluida'].map((key) => {
              const cfg = statusConfig[key];
              return (
                <Card key={key}>
                  <CardContent className="pt-6">
                    <p className="text-sm text-muted-foreground">{cfg?.label}</p>
                    <p className="text-2xl font-bold">{statusCounts[key] || 0}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card>
            <CardHeader><CardTitle>Férias dos Colaboradores</CardTitle></CardHeader>
            <CardContent>
              {ferias.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Inbox className="h-12 w-12 mb-3" />
                  <p className="font-medium">Nenhum registro de férias encontrado</p>
                    <p className="text-sm text-muted-foreground mt-1">Clique em "Programar Férias" para agendar.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Colaborador</TableHead>
                      <TableHead>Período Aquisitivo</TableHead>
                      <TableHead>Dias Direito</TableHead>
                      <TableHead>Dias Gozados</TableHead>
                      <TableHead>Saldo</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ferias.map((item, i) => {
                      const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                      return (
                        <TableRow key={i}>
                          <TableCell className="font-medium">{item.colaborador}</TableCell>
                          <TableCell>{item.periodoAquisitivo}</TableCell>
                          <TableCell>{item.diasDireito}</TableCell>
                          <TableCell>{item.diasGozados}</TableCell>
                          <TableCell className="font-bold">{item.saldo}</TableCell>
                          <TableCell><Badge className={st.className}>{st.label}</Badge></TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
