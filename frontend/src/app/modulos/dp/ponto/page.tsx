'use client';

import { useState, useEffect } from 'react';
import { Clock, ArrowLeft, Inbox, Loader2, AlertTriangle } from 'lucide-react';
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
  normal: { label: 'Normal', className: 'bg-green-500 text-white' },
  atraso: { label: 'Atraso', className: 'bg-yellow-500 text-white' },
  falta: { label: 'Falta', className: 'bg-red-500 text-white' },
  hora_extra: { label: 'Hora Extra', className: 'bg-blue-500 text-white' },
  late: { label: 'Atraso', className: 'bg-yellow-500 text-white' },
  absent: { label: 'Falta', className: 'bg-red-500 text-white' },
  overtime: { label: 'Hora Extra', className: 'bg-blue-500 text-white' },
};

export default function PontoPage() {
  const router = useRouter();
  const [periodo, setPeriodo] = useState('2026-03');
  const [registros, setRegistros] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const empRes = await fetch(`${API_BASE}/employees/?limit=100`, { headers: getAuthHeaders() });
        if (empRes.ok) {
          const empData = await empRes.json();
          const emps = empData.items || empData || [];
          const [year, month] = periodo.split('-');
          const startDate = `${year}-${month}-01`;
          const endDate = `${year}-${month}-28`;
          const allEntries: any[] = [];
          await Promise.all(
            emps.slice(0, 20).map(async (emp: any) => {
              try {
                const tRes = await fetch(
                  `${API_BASE}/time-tracking/employee/${emp.id}/entries?start_date=${startDate}&end_date=${endDate}`,
                  { headers: getAuthHeaders() }
                );
                if (tRes.ok) {
                  const entries = await tRes.json();
                  const items = entries.items || entries || [];
                  items.forEach((e: any) => {
                    allEntries.push({
                      colaborador: emp.nome || emp.name,
                      data: e.date || e.data,
                      entrada: e.clock_in || e.entrada || '--:--',
                      saida: e.clock_out || e.saida || '--:--',
                      total: e.total_hours || e.total || '00:00',
                      status: e.status || 'normal',
                    });
                  });
                }
              } catch { /* skip */ }
            })
          );
          setRegistros(allEntries);
        }
      } catch { setRegistros([]); } finally { setLoading(false); }
    }
    load();
  }, [periodo]);

  const totalHoras = registros.length * 8;
  const horasExtras = registros.filter(r => r.status === 'hora_extra' || r.status === 'overtime').length;
  const faltas = registros.filter(r => r.status === 'falta' || r.status === 'absent').length;
  const atrasos = registros.filter(r => r.status === 'atraso' || r.status === 'late').length;

  const summaryCards = [
    { title: 'Total Horas', value: `${totalHoras}h`, icon: Clock, color: 'text-blue-600', bgColor: 'bg-blue-50' },
    { title: 'Horas Extras', value: `${horasExtras}`, icon: Clock, color: 'text-green-600', bgColor: 'bg-green-50' },
    { title: 'Faltas', value: `${faltas}`, icon: AlertTriangle, color: 'text-red-600', bgColor: 'bg-red-50' },
    { title: 'Atrasos', value: `${atrasos}`, icon: AlertTriangle, color: 'text-yellow-600', bgColor: 'bg-yellow-50' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Clock className="h-6 w-6" />
              Ponto Eletrônico
            </h1>
            <p className="text-muted-foreground">Registro e controle de ponto dos colaboradores</p>
          </div>
        </div>
        <input
          type="month"
          value={periodo}
          onChange={(e) => setPeriodo(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm bg-background"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {summaryCards.map((card) => (
              <Card key={card.title}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">{card.title}</p>
                      <p className="text-2xl font-bold">{card.value}</p>
                    </div>
                    <div className={`h-10 w-10 rounded-lg ${card.bgColor} flex items-center justify-center`}>
                      <card.icon className={`h-5 w-5 ${card.color}`} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader><CardTitle>Registros de Ponto</CardTitle></CardHeader>
            <CardContent>
              {registros.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Inbox className="h-12 w-12 mb-3" />
                  <p className="font-medium">Nenhum registro de ponto encontrado</p>
                    <p className="text-sm text-muted-foreground mt-1">Os registros aparecerão conforme os colaboradores registram ponto.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Colaborador</TableHead>
                      <TableHead>Data</TableHead>
                      <TableHead>Entrada</TableHead>
                      <TableHead>Saída</TableHead>
                      <TableHead>Total Horas</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {registros.map((item, i) => {
                      const st = statusConfig[item.status] || { label: item.status, className: 'bg-gray-500 text-white' };
                      return (
                        <TableRow key={i}>
                          <TableCell className="font-medium">{item.colaborador}</TableCell>
                          <TableCell>{item.data ? new Date(item.data).toLocaleDateString('pt-BR') : '-'}</TableCell>
                          <TableCell>{item.entrada}</TableCell>
                          <TableCell>{item.saida}</TableCell>
                          <TableCell>{item.total}</TableCell>
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
