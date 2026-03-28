'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Loader2, User, FileText, Calendar, DollarSign, Building2, ChevronRight, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const API_BASE = '/api/v1/people-management/hr';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') || localStorage.getItem('token') : null;
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

const STATUS: Record<string, { label: string; color: string }> = {
  documents_pending: { label: 'Documentos Pendentes', color: 'bg-yellow-500 text-white' },
  medical_exam: { label: 'Exame Medico', color: 'bg-blue-500 text-white' },
  contract_signing: { label: 'Assinatura Contrato', color: 'bg-orange-500 text-white' },
  completed: { label: 'Concluida', color: 'bg-green-500 text-white' },
  cancelled: { label: 'Cancelada', color: 'bg-red-500 text-white' },
};

export default function AdmissaoDetalhePage() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [advancing, setAdvancing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/admissions/${params.id}`, { headers: getAuthHeaders() });
      if (res.ok) setData(await res.json());
    } catch { /* */ }
    finally { setLoading(false); }
  }, [params.id]);

  useEffect(() => { if (params.id) loadData(); }, [params.id, loadData]);

  const advanceStatus = async (newStatus: string, extraData?: Record<string, string>) => {
    setAdvancing(true);
    try {
      const res = await fetch(`${API_BASE}/admissions/${params.id}`, {
        method: 'PATCH', headers: getAuthHeaders(),
        body: JSON.stringify({ status: newStatus, ...extraData }),
      });
      if (res.ok) { toast.success(`Status atualizado para ${STATUS[newStatus]?.label || newStatus}`); await loadData(); }
      else { toast.error('Erro ao atualizar status'); }
    } catch { toast.error('Erro de conexao'); }
    finally { setAdvancing(false); }
  };

  if (loading) return <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>;
  if (!data) return <div className="text-center py-20 text-muted-foreground">Admissao nao encontrada</div>;

  const st = STATUS[String(data.status)] || { label: String(data.status), color: 'bg-gray-500 text-white' };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.push('/modulos/dp/admissao')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">{String(data.candidate_name || 'Candidato')}</h1>
          <p className="text-muted-foreground">Processo de admissao</p>
        </div>
        <Badge className={st.color}>{st.label}</Badge>
      </div>

      {/* Workflow Buttons */}
      {String(data.status) !== 'completed' && String(data.status) !== 'cancelled' && (
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-sm font-medium text-muted-foreground">Avancar para:</span>
              {String(data.status) === 'documents_pending' && (
                <Button size="sm" disabled={advancing} onClick={() => advanceStatus('medical_exam')}>
                  <ChevronRight className="h-4 w-4 mr-1" /> Exame Medico
                </Button>
              )}
              {String(data.status) === 'medical_exam' && (
                <Button size="sm" disabled={advancing} onClick={() => advanceStatus('contract_signing', { medical_exam_date: new Date().toISOString().slice(0, 10), medical_exam_result: 'apto' })}>
                  <ChevronRight className="h-4 w-4 mr-1" /> Assinatura Contrato
                </Button>
              )}
              {String(data.status) === 'contract_signing' && (
                <Button size="sm" disabled={advancing} onClick={() => advanceStatus('completed', { actual_start_date: String(data.expected_start_date || new Date().toISOString().slice(0, 10)) })}>
                  <CheckCircle2 className="h-4 w-4 mr-1" /> Concluir Admissao
                </Button>
              )}
              {advancing && <Loader2 className="h-4 w-4 animate-spin" />}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base flex items-center gap-2"><User className="h-4 w-4" /> Dados do Candidato</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div><span className="text-sm text-muted-foreground">Nome:</span><p className="font-medium">{String(data.candidate_name || '-')}</p></div>
            <div><span className="text-sm text-muted-foreground">CPF:</span><p className="font-medium">{String(data.cpf || '-')}</p></div>
            <div><span className="text-sm text-muted-foreground">Cargo:</span><p className="font-medium">{String(data.position || '-')}</p></div>
            <div><span className="text-sm text-muted-foreground">Departamento:</span><p className="font-medium">{String(data.department || '-')}</p></div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base flex items-center gap-2"><Calendar className="h-4 w-4" /> Informacoes</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div><span className="text-sm text-muted-foreground">Salario Proposto:</span><p className="font-medium">{data.salary_proposed ? `R$ ${Number(data.salary_proposed).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : '-'}</p></div>
            <div><span className="text-sm text-muted-foreground">Data Prevista:</span><p className="font-medium">{data.expected_start_date ? new Date(String(data.expected_start_date)).toLocaleDateString('pt-BR') : '-'}</p></div>
            <div><span className="text-sm text-muted-foreground">Criado em:</span><p className="font-medium">{data.created_at ? new Date(String(data.created_at)).toLocaleString('pt-BR') : '-'}</p></div>
            {data.notes ? <div><span className="text-sm text-muted-foreground">Observacoes:</span><p className="text-sm">{String(data.notes)}</p></div> : null}
          </CardContent>
        </Card>
      </div>

      {data.checklist && typeof data.checklist === 'object' ? (
        <Card>
          <CardHeader><CardTitle className="text-base flex items-center gap-2"><FileText className="h-4 w-4" /> Checklist de Documentos</CardTitle></CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(data.checklist as Record<string, Record<string, boolean>>).map(([cat, items]) => (
                <div key={cat}>
                  <h4 className="font-medium text-sm mb-2 capitalize">{cat.replace(/_/g, ' ')}</h4>
                  <div className="space-y-1">
                    {Object.entries(items).map(([doc, done]) => (
                      <div key={doc} className="flex items-center gap-2 text-sm">
                        <span className={done ? 'text-green-600' : 'text-muted-foreground'}>{done ? '✓' : '○'}</span>
                        <span className={done ? '' : 'text-muted-foreground'}>{doc.replace(/_/g, ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
