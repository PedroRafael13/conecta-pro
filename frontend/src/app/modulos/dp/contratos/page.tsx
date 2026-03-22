'use client';

import { useState, useEffect } from 'react';
import { FileText, ArrowLeft, Inbox, Loader2, Plus, X, Save } from 'lucide-react';
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
  ativo: { label: 'Ativo', className: 'bg-green-500 text-white' },
  vencido: { label: 'Vencido', className: 'bg-red-500 text-white' },
  suspenso: { label: 'Suspenso', className: 'bg-yellow-500 text-white' },
  encerrado: { label: 'Encerrado', className: 'bg-gray-500 text-white' },
  active: { label: 'Ativo', className: 'bg-green-500 text-white' },
  expired: { label: 'Vencido', className: 'bg-red-500 text-white' },
  suspended: { label: 'Suspenso', className: 'bg-yellow-500 text-white' },
  terminated: { label: 'Encerrado', className: 'bg-gray-500 text-white' },
};

export default function ContratosPage() {
  const router = useRouter();
  const [contratos, setContratos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [formData, setFormData] = useState({ employee_id: '', contract_type: 'CLT', start_date: '', end_date: '', salary: '', workload_hours: '44', department: '', position: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    async function load() {
      try {
        const empRes = await fetch(`${API_BASE}/employees/?limit=100`, { headers: getAuthHeaders() });
        if (empRes.ok) {
          const empData = await empRes.json();
          const emps = empData.items || empData || [];
          setEmployees(emps);
          const allContracts: any[] = [];
          await Promise.all(
            emps.slice(0, 30).map(async (emp: any) => {
              try {
                const cRes = await fetch(`${API_BASE}/contracts/employee/${emp.id}/current`, { headers: getAuthHeaders() });
                if (cRes.ok) {
                  const c = await cRes.json();
                  allContracts.push({
                    colaborador: emp.nome || emp.name,
                    tipo: c.contract_type || c.tipo || 'CLT',
                    inicio: c.start_date || c.inicio,
                    fim: c.end_date || c.fim,
                    salarioBase: c.salary || c.salario_base || emp.salario_base || 0,
                    status: c.status || 'active',
                  });
                }
              } catch { /* skip */ }
            })
          );
          setContratos(allContracts);
        }
      } catch { setContratos([]); } finally { setLoading(false); }
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
              <FileText className="h-6 w-6" />
              Contratos de Trabalho
            </h1>
            <p className="text-muted-foreground">Gerencie contratos de trabalho dos colaboradores</p>
          </div>
        </div>
        <Button type="button" size="sm" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-1" /> Novo Contrato</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Novo Contrato</CardTitle>
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
                <label className="text-sm font-medium mb-1 block">Tipo *</label>
                <select value={formData.contract_type} onChange={e => setFormData(p => ({ ...p, contract_type: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm">
                  <option value="CLT">CLT</option>
                  <option value="PJ">PJ</option>
                  <option value="Estagio">Estágio</option>
                  <option value="Temporario">Temporário</option>
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
              <div>
                <label className="text-sm font-medium mb-1 block">Salário Base</label>
                <input type="number" step="0.01" value={formData.salary} onChange={e => setFormData(p => ({ ...p, salary: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="0.00" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Carga Horária</label>
                <input type="number" value={formData.workload_hours} onChange={e => setFormData(p => ({ ...p, workload_hours: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="44" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Departamento</label>
                <input type="text" value={formData.department} onChange={e => setFormData(p => ({ ...p, department: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="Ex: Operações" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Cargo</label>
                <input type="text" value={formData.position} onChange={e => setFormData(p => ({ ...p, position: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="Ex: Vigilante" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={async () => {
                const errors: Record<string, string> = {};
                if (!formData.employee_id) errors.employee_id = 'Selecione um colaborador';
                if (!formData.start_date) errors.start_date = 'Data de início é obrigatória';
                if (Object.keys(errors).length > 0) { setFormErrors(errors); toast.error('Corrija os campos destacados'); return; }
                setSaving(true);
                try {
                  const res = await fetch(`${API_BASE}/contracts/`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(formData) });
                  if (res.ok) { setShowForm(false); setFormData({ employee_id: '', contract_type: 'CLT', start_date: '', end_date: '', salary: '', workload_hours: '44', department: '', position: '' }); setFormErrors({}); setReloadKey(k => k + 1); toast.success('Contrato criado com sucesso'); }
                  else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao criar contrato'); }
                } catch { toast.error('Erro de conexão'); } finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Criar Contrato'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Contratos</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
          ) : contratos.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p className="font-medium">Nenhum contrato encontrado</p>
                  <p className="text-sm text-muted-foreground mt-1">Clique em "Novo Contrato" para cadastrar.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Início</TableHead>
                  <TableHead>Fim</TableHead>
                  <TableHead>Salário Base</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {contratos.map((item, i) => {
                  const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                  return (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{item.colaborador}</TableCell>
                      <TableCell>{item.tipo}</TableCell>
                      <TableCell>{item.inicio ? new Date(item.inicio).toLocaleDateString('pt-BR') : '-'}</TableCell>
                      <TableCell>{item.fim ? new Date(item.fim).toLocaleDateString('pt-BR') : 'Indeterminado'}</TableCell>
                      <TableCell>R$ {(item.salarioBase || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</TableCell>
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
