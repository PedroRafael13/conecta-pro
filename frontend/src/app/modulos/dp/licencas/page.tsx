'use client';

import { useState, useEffect } from 'react';
import { CalendarDays, ArrowLeft, Inbox, Loader2, Plus, X, Save } from 'lucide-react';
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
  ativa: { label: 'Ativa', className: 'bg-green-500 text-white' },
  encerrada: { label: 'Encerrada', className: 'bg-gray-500 text-white' },
  pendente: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
  active: { label: 'Ativa', className: 'bg-green-500 text-white' },
  ended: { label: 'Encerrada', className: 'bg-gray-500 text-white' },
  pending: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
};

const tipoConfig: Record<string, string> = {
  medica: 'Licença Médica',
  maternidade: 'Maternidade',
  paternidade: 'Paternidade',
  acidente: 'Acidente de Trabalho',
  obito: 'Nojo (Óbito)',
  casamento: 'Gala (Casamento)',
  medical: 'Licença Médica',
  maternity: 'Maternidade',
  paternity: 'Paternidade',
  work_accident: 'Acidente de Trabalho',
};

export default function LicencasPage() {
  const router = useRouter();
  const [licencas, setLicencas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [formData, setFormData] = useState({ employee_id: '', leave_type: 'medica', start_date: '', end_date: '', cid: '', notes: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    async function load() {
      try {
        // Fetch employees and their discipline/leave history
        const empRes = await fetch(`${API_BASE}/employees?page_size=100`, { headers: getAuthHeaders() });
        if (empRes.ok) {
          const empData = await empRes.json();
          const emps = empData.items || empData || [];
          setEmployees(emps);
          const allLeaves: any[] = [];
          await Promise.all(
            emps.map(async (emp: any) => {
              try {
                const lRes = await fetch(`${API_BASE}/discipline/employee/${emp.id}/history?page_size=50`, { headers: getAuthHeaders() });
                if (lRes.ok) {
                  const data = await lRes.json();
                  const items = data.items || data || [];
                  items.filter((item: any) => item.type === 'leave' || item.leave_type).forEach((l: any) => {
                    allLeaves.push({
                      colaborador: emp.nome || emp.name,
                      tipo: l.leave_type || l.tipo || 'medica',
                      inicio: l.start_date || l.inicio,
                      fim: l.end_date || l.fim,
                      dias: l.days || l.dias || 0,
                      status: l.status || 'active',
                    });
                  });
                }
              } catch { /* skip */ }
            })
          );
          setLicencas(allLeaves);
        }
      } catch { setLicencas([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <CalendarDays className="h-6 w-6" />
              Licenças e Afastamentos
            </h1>
            <p className="text-muted-foreground">Controle de licenças e afastamentos</p>
          </div>
        </div>
        <Button type="button" size="sm" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-1" /> Nova Licença</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Nova Licença</CardTitle>
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}><X className="h-4 w-4" /></Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Colaborador *</label>
                <select value={formData.employee_id} onChange={e => { setFormData(p => ({ ...p, employee_id: e.target.value })); setFormErrors(p => ({ ...p, employee_id: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.employee_id ? 'border-red-500' : ''}`}>
                  <option value="">Selecione o colaborador</option>
                  {employees.map((emp: any) => (
                    <option key={emp.id} value={emp.id}>{emp.nome || emp.name}</option>
                  ))}
                </select>
                {formErrors.employee_id && <p className="text-red-500 text-xs mt-1">{formErrors.employee_id}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Tipo de Licença</label>
                <select value={formData.leave_type} onChange={e => setFormData(p => ({ ...p, leave_type: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm">
                  <option value="medica">Licença Médica</option>
                  <option value="maternidade">Maternidade</option>
                  <option value="paternidade">Paternidade</option>
                  <option value="acidente">Acidente de Trabalho</option>
                  <option value="obito">Nojo (Óbito)</option>
                  <option value="casamento">Gala (Casamento)</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Data Início *</label>
                <input type="date" value={formData.start_date} onChange={e => { setFormData(p => ({ ...p, start_date: e.target.value })); setFormErrors(p => ({ ...p, start_date: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.start_date ? 'border-red-500' : ''}`} />
                {formErrors.start_date && <p className="text-red-500 text-xs mt-1">{formErrors.start_date}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Data Fim</label>
                <input type="date" value={formData.end_date} onChange={e => setFormData(p => ({ ...p, end_date: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" />
              </div>
              {formData.leave_type === 'medica' && (
                <div>
                  <label className="text-sm font-medium mb-1 block">CID</label>
                  <input type="text" value={formData.cid} onChange={e => setFormData(p => ({ ...p, cid: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="Ex: J11" />
                </div>
              )}
              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-1 block">Observações</label>
                <textarea value={formData.notes} onChange={e => setFormData(p => ({ ...p, notes: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" rows={3} placeholder="Observações adicionais" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={async () => {
                const errors: Record<string, string> = {};
                if (!formData.employee_id) errors.employee_id = 'Colaborador é obrigatório';
                if (!formData.start_date) errors.start_date = 'Data início é obrigatória';
                if (Object.keys(errors).length > 0) { setFormErrors(errors); toast.error('Corrija os campos destacados'); return; }
                setSaving(true);
                try {
                  const res = await fetch(`${API_BASE}/leaves/`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(formData) });
                  if (res.ok) { setShowForm(false); setFormData({ employee_id: '', leave_type: 'medica', start_date: '', end_date: '', cid: '', notes: '' }); setFormErrors({}); toast.success('Licença registrada com sucesso'); }
                  else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao registrar licença'); }
                } catch { toast.error('Erro de conexão'); } finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Registrar Licença'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Licenças Registradas</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
          ) : licencas.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p className="font-medium">Nenhuma licença registrada</p>
                  <p className="text-sm text-muted-foreground mt-1">As licenças aparecerão aqui quando solicitadas.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Início</TableHead>
                  <TableHead>Fim</TableHead>
                  <TableHead>Dias</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {licencas.map((item, i) => {
                  const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                  return (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{item.colaborador}</TableCell>
                      <TableCell>{tipoConfig[item.tipo] || item.tipo}</TableCell>
                      <TableCell>{item.inicio ? new Date(item.inicio).toLocaleDateString('pt-BR') : '-'}</TableCell>
                      <TableCell>{item.fim ? new Date(item.fim).toLocaleDateString('pt-BR') : '-'}</TableCell>
                      <TableCell>{item.dias}</TableCell>
                      <TableCell><Badge className={st.className}>{st.label}</Badge></TableCell>
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
