'use client';

import { useState, useEffect } from 'react';
import { FolderOpen, ArrowLeft, Inbox, Loader2, Eye, Download, X, Save, Upload } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
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
  valido: { label: 'Válido', className: 'bg-green-500 text-white' },
  vencido: { label: 'Vencido', className: 'bg-red-500 text-white' },
  pendente: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
  valid: { label: 'Válido', className: 'bg-green-500 text-white' },
  expired: { label: 'Vencido', className: 'bg-red-500 text-white' },
  pending: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
};

export default function DocumentosPage() {
  const router = useRouter();
  const [documentos, setDocumentos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [employees, setEmployees] = useState<any[]>([]);
  const [formData, setFormData] = useState({ employee_id: '', document_type: 'RG', file_name: '', expiry_date: '', notes: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    async function load() {
      try {
        // Fetch from admission checklist as document source
        const admRes = await fetch(`${API_BASE}/admissions/checklist`, { headers: getAuthHeaders() });
        const empRes = await fetch(`${API_BASE}/employees?page_size=100`, { headers: getAuthHeaders() });
        const docs: any[] = [];

        if (empRes.ok) {
          const empData = await empRes.json();
          const emps = empData.items || empData || [];
          setEmployees(emps);
          // Get employee profiles which include documents
          await Promise.all(
            emps.map(async (emp: any) => {
              try {
                const profRes = await fetch(`${API_BASE}/employees/${emp.id}/profile`, { headers: getAuthHeaders() });
                if (profRes.ok) {
                  const prof = await profRes.json();
                  const empDocs = prof.documents || [];
                  empDocs.forEach((d: any) => {
                    docs.push({
                      colaborador: emp.nome || emp.name,
                      documento: d.name || d.document_name || d.tipo,
                      tipo: d.type || d.document_type || 'Documento',
                      dataUpload: d.uploaded_at || d.created_at,
                      status: d.status || 'valid',
                    });
                  });
                }
              } catch { /* skip */ }
            })
          );
        }
        setDocumentos(docs);
      } catch { setDocumentos([]); } finally { setLoading(false); }
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
              <FolderOpen className="h-6 w-6" />
              Documentos de Colaboradores
            </h1>
            <p className="text-muted-foreground">Gestão de documentos dos colaboradores</p>
          </div>
        </div>
        <Button type="button" size="sm" onClick={() => setShowForm(true)}><Upload className="h-4 w-4 mr-1" /> Upload Documento</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Novo Documento</CardTitle>
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
                <label className="text-sm font-medium mb-1 block">Tipo de Documento</label>
                <select value={formData.document_type} onChange={e => setFormData(p => ({ ...p, document_type: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm">
                  <option value="RG">RG</option>
                  <option value="CPF">CPF</option>
                  <option value="CTPS">CTPS</option>
                  <option value="Comprovante_Residencia">Comprovante de Residência</option>
                  <option value="Certificado">Certificado</option>
                  <option value="Certidao">Certidão</option>
                  <option value="Outro">Outro</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Nome do Arquivo *</label>
                <input type="text" value={formData.file_name} onChange={e => { setFormData(p => ({ ...p, file_name: e.target.value })); setFormErrors(p => ({ ...p, file_name: '' })); }} className={`w-full px-3 py-2 border rounded-md text-sm ${formErrors.file_name ? 'border-red-500' : ''}`} placeholder="Ex: rg_joao_silva.pdf" />
                {formErrors.file_name && <p className="text-red-500 text-xs mt-1">{formErrors.file_name}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Data de Validade</label>
                <input type="date" value={formData.expiry_date} onChange={e => setFormData(p => ({ ...p, expiry_date: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" />
              </div>
              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-1 block">Observações</label>
                <textarea value={formData.notes} onChange={e => setFormData(p => ({ ...p, notes: e.target.value }))} className="w-full px-3 py-2 border rounded-md text-sm" rows={3} placeholder="Observações adicionais" />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button type="button" size="sm" disabled={saving} onClick={async () => {
                const errors: Record<string, string> = {};
                if (!formData.employee_id) errors.employee_id = 'Colaborador é obrigatório';
                if (!formData.file_name.trim()) errors.file_name = 'Nome do arquivo é obrigatório';
                if (Object.keys(errors).length > 0) { setFormErrors(errors); toast.error('Corrija os campos destacados'); return; }
                setSaving(true);
                try {
                  const res = await fetch('/api/v1/people-management/ged/documents', { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ title: formData.file_name, document_type: formData.document_type, employee_id: formData.employee_id, expiry_date: formData.expiry_date || null, notes: formData.notes }) });
                  if (res.ok) { setShowForm(false); setFormData({ employee_id: '', document_type: 'RG', file_name: '', expiry_date: '', notes: '' }); setFormErrors({}); toast.success('Documento registrado com sucesso'); }
                  else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao registrar documento'); }
                } catch { toast.error('Erro de conexão'); } finally { setSaving(false); }
              }}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Save className="h-4 w-4 mr-1" />}
                {saving ? 'Salvando...' : 'Registrar Documento'}
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Documentos</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
          ) : documentos.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p className="font-medium">Nenhum documento encontrado</p>
                  <p className="text-sm text-muted-foreground mt-1">Clique em "Upload Documento" para adicionar.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Documento</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Data Upload</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documentos.map((item, i) => {
                  const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                  return (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{item.colaborador}</TableCell>
                      <TableCell>{item.documento}</TableCell>
                      <TableCell>{item.tipo}</TableCell>
                      <TableCell>{item.dataUpload ? new Date(item.dataUpload).toLocaleDateString('pt-BR') : '-'}</TableCell>
                      <TableCell><Badge className={st.className}>{st.label}</Badge></TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button type="button" variant="outline" size="sm" onClick={() => toast.info('Visualizacao de documento sera implementada em breve')}><Eye className="h-3 w-3" /></Button>
                          <Button type="button" variant="outline" size="sm" onClick={() => toast.info('Download de documento sera implementado em breve')}><Download className="h-3 w-3" /></Button>
                        </div>
                      </TableCell>
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
