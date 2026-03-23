'use client';

import { useState, useEffect } from 'react';
import { ShieldCheck, ArrowLeft, Inbox, Loader2, X, AlertTriangle } from 'lucide-react';
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
  pendente: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
  enviado: { label: 'Enviado', className: 'bg-blue-500 text-white' },
  aceito: { label: 'Aceito', className: 'bg-green-500 text-white' },
  rejeitado: { label: 'Rejeitado', className: 'bg-red-500 text-white' },
  pending: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
  sent: { label: 'Enviado', className: 'bg-blue-500 text-white' },
  accepted: { label: 'Aceito', className: 'bg-green-500 text-white' },
  rejected: { label: 'Rejeitado', className: 'bg-red-500 text-white' },
};

export default function ESocialPage() {
  const router = useRouter();
  const [eventos, setEventos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showConfirm, setShowConfirm] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        // eSocial events are generated from admissions and terminations
        const [admRes, termRes] = await Promise.all([
          fetch(`${API_BASE}/admissions?page_size=50`, { headers: getAuthHeaders() }),
          fetch(`${API_BASE}/terminations?page_size=50`, { headers: getAuthHeaders() }),
        ]);
        const evts: any[] = [];
        if (admRes.ok) {
          const admData = await admRes.json();
          (admData.items || admData || []).forEach((a: any) => {
            evts.push({
              evento: `Admissão - ${a.nome || a.candidate_name || 'N/A'}`,
              tipo: 'S-2200',
              colaborador: a.nome || a.candidate_name,
              status: a.status === 'completed' || a.status === 'concluida' ? 'aceito' : 'pendente',
              data: a.created_at || a.expected_date,
            });
          });
        }
        if (termRes.ok) {
          const termData = await termRes.json();
          (termData.items || termData || []).forEach((t: any) => {
            evts.push({
              evento: `Desligamento - ${t.nome || t.employee_name || 'N/A'}`,
              tipo: 'S-2299',
              colaborador: t.nome || t.employee_name,
              status: t.status === 'completed' || t.status === 'concluida' ? 'aceito' : 'pendente',
              data: t.created_at || t.last_day,
            });
          });
        }
        setEventos(evts);
      } catch { setEventos([]); } finally { setLoading(false); }
    }
    load();
  }, []);

  const countByStatus = (s: string) => eventos.filter(e => e.status === s).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <ShieldCheck className="h-6 w-6" />
              eSocial - Eventos
            </h1>
            <p className="text-muted-foreground">Gestão de eventos e obrigações do eSocial</p>
          </div>
        </div>
        <Button type="button" size="sm" onClick={() => setShowConfirm(true)}><ShieldCheck className="h-4 w-4 mr-1" /> Enviar Pendentes</Button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
          {showConfirm && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2"><AlertTriangle className="h-5 w-5 text-yellow-500" /> Confirmar Envio de Eventos Pendentes</CardTitle>
                  <Button type="button" variant="ghost" size="sm" onClick={() => setShowConfirm(false)}><X className="h-4 w-4" /></Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm font-medium mb-2">{countByStatus('pendente')} eventos pendentes</p>
                <p className="text-sm text-muted-foreground mb-4">Os eventos serão enviados ao governo. Confirme que os dados estão corretos.</p>
                <div className="flex gap-2">
                  <Button type="button" size="sm" disabled={sending} onClick={async () => {
                    setSending(true);
                    try {
                      const res = await fetch(`${API_BASE}/esocial/validar`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ events: eventos.filter(e => e.status === 'pendente') }) });
                      if (res.ok) { setShowConfirm(false); toast.success('Eventos enviados com sucesso'); }
                      else { const err = await res.json().catch(() => null); toast.error(err?.detail || 'Erro ao enviar eventos'); }
                    } catch { toast.error('Erro de conexão'); } finally { setSending(false); }
                  }}>
                    {sending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <ShieldCheck className="h-4 w-4 mr-1" />}
                    {sending ? 'Enviando...' : 'Enviar'}
                  </Button>
                  <Button type="button" variant="outline" size="sm" onClick={() => setShowConfirm(false)}>Cancelar</Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-4 md:grid-cols-4">
            {['pendente', 'enviado', 'aceito', 'rejeitado'].map((key) => (
              <Card key={key}>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">{statusConfig[key]?.label}</p>
                  <p className="text-2xl font-bold">{countByStatus(key)}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader><CardTitle>Eventos eSocial</CardTitle></CardHeader>
            <CardContent>
              {eventos.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Inbox className="h-12 w-12 mb-3" />
                  <p className="font-medium">Nenhum evento eSocial registrado</p>
                    <p className="text-sm text-muted-foreground mt-1">Os eventos serão gerados a partir de admissões e desligamentos.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Evento</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Colaborador</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Data</TableHead>
                      <TableHead>Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {eventos.map((item, i) => {
                      const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                      return (
                        <TableRow key={i}>
                          <TableCell className="font-medium">{item.evento}</TableCell>
                          <TableCell><code className="text-xs bg-muted px-1.5 py-0.5 rounded">{item.tipo}</code></TableCell>
                          <TableCell>{item.colaborador}</TableCell>
                          <TableCell><Badge className={st.className}>{st.label}</Badge></TableCell>
                          <TableCell>{item.data ? new Date(item.data).toLocaleDateString('pt-BR') : '-'}</TableCell>
                          <TableCell><Button type="button" variant="outline" size="sm" onClick={() => toast.info('Detalhes do evento sera implementado em breve')}>Detalhes</Button></TableCell>
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
