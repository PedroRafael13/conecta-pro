'use client';

import { useState, useEffect } from 'react';
import { Gift, ArrowLeft, Inbox, Loader2, Bus, UtensilsCrossed, Heart, Shield, Smile, Plus, X, Save } from 'lucide-react';
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
  inativo: { label: 'Inativo', className: 'bg-gray-500 text-white' },
  active: { label: 'Ativo', className: 'bg-green-500 text-white' },
  inactive: { label: 'Inativo', className: 'bg-gray-500 text-white' },
};

const fmt = (v: number) => `R$ ${(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

export default function BeneficiosPage() {
  const router = useRouter();
  const [beneficios, setBeneficios] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [formData, setFormData] = useState({ employee_id: '', benefit_type: 'VT', value: '', start_date: '', end_date: '', discount_payroll: false, discount_percentage: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    async function load() {
      try {
        const empRes = await fetch(`${API_BASE}/employees?page_size=100`, { headers: getAuthHeaders() });
        if (empRes.ok) {
          const empData = await empRes.json();
          const emps = empData.items || empData || [];
          setEmployees(emps);
          const allBenefits: any[] = [];
          await Promise.all(
            emps.map(async (emp: any) => {
              try {
                const benRes = await fetch(`${API_BASE}/benefits/employee/${emp.id}`, { headers: getAuthHeaders() });
                if (benRes.ok) {
                  const bens = await benRes.json();
                  const items = bens.items || bens || [];
                  items.forEach((b: any) => {
                    allBenefits.push({
                      colaborador: emp.nome || emp.name,
                      tipo: b.benefit_type || b.tipo,
                      plano: b.plan_name || b.plano || '-',
                      empresa: b.company_contribution || b.employer_cost || 0,
                      desconto: b.employee_discount || b.employee_cost || 0,
                      status: b.status || 'active',
                    });
                  });
                }
              } catch { /* skip */ }
            })
          );
          setBeneficios(allBenefits);
        }
      } catch { setBeneficios([]); } finally { setLoading(false); }
    }
    load();
  }, [reloadKey]);

  // Summary by type
  const tipoSummary = beneficios.reduce((acc, b) => {
    const tipo = b.tipo || 'Outro';
    if (!acc[tipo]) acc[tipo] = { count: 0, total: 0 };
    acc[tipo].count++;
    acc[tipo].total += (b.empresa || 0);
    return acc;
  }, {} as Record<string, { count: number; total: number }>);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Gift className="h-6 w-6" />
              Gestão de Benefícios
            </h1>
            <p className="text-muted-foreground">Benefícios oferecidos aos colaboradores</p>
          </div>
        </div>
        <Button type="button" size="sm" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-1" /> Novo Benefício</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Novo Benefício</CardTitle>
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
                <select value={formData.benefit_type} onChange={e => setFormData(p => ({ ...p, benefit_type: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm">
                  <option value="VT">Vale Transporte</option>
                  <option value="VR">Vale Refeição</option>
                  <option value="VA">Vale Alimentação</option>
                  <option value="Plano Saude">Plano de Saúde</option>
                  <option value="Plano Odonto">Plano Odontológico</option>
                  <option value="Seguro Vida">Seguro de Vida</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Valor *</label>
                <input type="number" step="0.01" value={formData.value} onChange={e => { setFormData(p => ({ ...p, value: e.target.value })); setFormErrors(p => ({ ...p, value: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.value ? 'border-red-500' : ''}`} placeholder="0.00" />
                {formErrors.value && <p className="text-red-500 text-xs mt-1">{formErrors.value}</p>}
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
                <label className="text-sm font-medium mb-1 block flex items-center gap-2">
                  <input type="checkbox" checked={formData.discount_payroll} onChange={e => setFormData(p => ({ ...p, discount_payroll: e.target.checked }))} />
                  Desconto em Folha
                </label>
              </div>
              {formData.discount_payroll && (
                <div>
                  <label className="text-sm font-medium mb-1 block">Percentual de Desconto (%)</label>
                  <input type="number" step="0.01" value={formData.discount_percentage} onChange={e => setFormData(p => ({ ...p, discount_percentage: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" placeholder="6.00" />
                </div>
              )}
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={async () => {
                const errors: Record<string, string> = {};
                if (!formData.employee_id) errors.employee_id = 'Selecione um colaborador';
                if (!formData.value) errors.value = 'Valor é obrigatório';
                if (!formData.start_date) errors.start_date = 'Data de início é obrigatória';
                if (Object.keys(errors).length > 0) { setFormErrors(errors); toast.error('Corrija os campos destacados'); return; }
                setSaving(true);
                try {
                  const res = await fetch(`${API_BASE}/benefits/`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(formData) });
                  if (res.ok) { setShowForm(false); setFormData({ employee_id: '', benefit_type: 'VT', value: '', start_date: '', end_date: '', discount_payroll: false, discount_percentage: '' }); setFormErrors({}); setReloadKey(k => k + 1); toast.success('Benefício criado com sucesso'); }
                  else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao criar benefício'); }
                } catch { toast.error('Erro de conexão'); } finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Criar Benefício'}
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
          {Object.keys(tipoSummary).length > 0 && (
            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
              {(Object.entries(tipoSummary) as [string, { count: number; total: number }][]).map(([tipo, data]) => (
                <Card key={tipo}>
                  <CardContent className="pt-4 pb-4">
                    <span className="text-sm font-medium">{tipo}</span>
                    <p className="text-lg font-bold">{data.count} colab.</p>
                    <p className="text-xs text-muted-foreground">{fmt(data.total)}/mes</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          <Card>
            <CardHeader><CardTitle>Benefícios por Colaborador</CardTitle></CardHeader>
            <CardContent>
              {beneficios.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Inbox className="h-12 w-12 mb-3" />
                  <p className="font-medium">Nenhum benefício cadastrado</p>
                    <p className="text-sm text-muted-foreground mt-1">Clique em "Novo Benefício" para adicionar.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Colaborador</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Plano</TableHead>
                      <TableHead>Contrib. Empresa</TableHead>
                      <TableHead>Desc. Funcionário</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {beneficios.map((item, i) => {
                      const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                      return (
                        <TableRow key={i}>
                          <TableCell className="font-medium">{item.colaborador}</TableCell>
                          <TableCell>{item.tipo}</TableCell>
                          <TableCell>{item.plano}</TableCell>
                          <TableCell>{fmt(item.empresa)}</TableCell>
                          <TableCell>{fmt(item.desconto)}</TableCell>
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
