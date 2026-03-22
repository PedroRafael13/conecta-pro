'use client';

import { useState, useEffect } from 'react';
import { DollarSign, ArrowLeft, Inbox, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const API_BASE = '/api/v1/people-management/hr';

function getAuthHeaders() {
  const token = typeof window !== 'undefined' ? (localStorage.getItem('access_token') || localStorage.getItem('access_token') || localStorage.getItem('token')) : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

const fmt = (v: number) => `R$ ${(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

export default function FolhaPage() {
  const router = useRouter();
  const [periodo, setPeriodo] = useState('2026-03');
  const [employees, setEmployees] = useState<any[]>([]);
  const [payrollData, setPayrollData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/employees/?page_size=100`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          const emps = data.items || data || [];
          setEmployees(emps);

          const [year, month] = periodo.split('-');
          const payrolls = await Promise.all(
            emps.map(async (emp: any) => {
              try {
                const pr = await fetch(
                  `${API_BASE}/payroll/employee/${emp.id}/calculate?month=${parseInt(month ?? '0')}&year=${parseInt(year ?? '0')}`,
                  { headers: getAuthHeaders() }
                );
                if (pr.ok) {
                  const d = await pr.json();
                  return { nome: emp.nome || emp.name, ...d };
                }
              } catch { /* skip */ }
              return null;
            })
          );
          setPayrollData(payrolls.filter(Boolean));
        }
      } catch { /* fallback */ } finally { setLoading(false); }
    }
    load();
  }, [periodo]);

  const totalBruto = payrollData.reduce((a, p) => a + (p.total_proventos || p.salario_base || 0), 0);
  const totalInss = payrollData.reduce((a, p) => {
    const inssItem = (p.descontos || []).find((d: any) => d.descricao?.includes('INSS'));
    return a + (inssItem?.valor || 0);
  }, 0);
  const totalIrrf = payrollData.reduce((a, p) => {
    const irrfItem = (p.descontos || []).find((d: any) => d.descricao?.includes('IRRF'));
    return a + (irrfItem?.valor || 0);
  }, 0);
  const totalDescontos = payrollData.reduce((a, p) => a + (p.total_descontos || 0), 0);
  const totalLiquido = payrollData.reduce((a, p) => a + (p.salario_liquido || 0), 0);
  const totalFgts = payrollData.reduce((a, p) => a + (p.fgts_8_pct || 0), 0);

  const summaryCards = [
    { title: 'Total Bruto', value: fmt(totalBruto), color: 'text-blue-600', bgColor: 'bg-blue-50' },
    { title: 'Total Descontos', value: fmt(totalDescontos), color: 'text-red-600', bgColor: 'bg-red-50' },
    { title: 'Total Líquido', value: fmt(totalLiquido), color: 'text-green-600', bgColor: 'bg-green-50' },
    { title: 'Total INSS', value: fmt(totalInss), color: 'text-purple-600', bgColor: 'bg-purple-50' },
    { title: 'Total FGTS 8%', value: fmt(totalFgts), color: 'text-cyan-600', bgColor: 'bg-cyan-50' },
    { title: 'Total IRRF', value: fmt(totalIrrf), color: 'text-orange-600', bgColor: 'bg-orange-50' },
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
              <DollarSign className="h-6 w-6" />
              Folha de Pagamento
            </h1>
            <p className="text-muted-foreground">Folha salarial e encargos trabalhistas</p>
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
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {summaryCards.map((card) => (
              <Card key={card.title}>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground">{card.title}</p>
                  <p className={`text-xl font-bold ${card.color}`}>{card.value}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader><CardTitle>Detalhamento por Colaborador</CardTitle></CardHeader>
            <CardContent>
              {payrollData.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Inbox className="h-12 w-12 mb-3" />
                  <p className="font-medium">Nenhum registro na folha para este período</p>
                    <p className="text-sm text-muted-foreground mt-1">Selecione outro período ou aguarde o processamento.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Colaborador</TableHead>
                      <TableHead>Salário Base</TableHead>
                      <TableHead>INSS</TableHead>
                      <TableHead>FGTS 8%</TableHead>
                      <TableHead>Descontos</TableHead>
                      <TableHead>Liquido</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {payrollData.map((item, i) => {
                      const inssVal = (item.descontos || []).find((d: any) => d.descricao?.includes('INSS'))?.valor || 0;
                      const irrfVal = (item.descontos || []).find((d: any) => d.descricao?.includes('IRRF'))?.valor || 0;
                      return (
                        <TableRow key={i}>
                          <TableCell className="font-medium">{item.nome || item.employee_name}</TableCell>
                          <TableCell>{fmt(item.salario_base)}</TableCell>
                          <TableCell className="text-red-500">{fmt(inssVal)}</TableCell>
                          <TableCell className="text-cyan-600">{fmt(item.fgts_8_pct || 0)}</TableCell>
                          <TableCell className="text-red-500">{fmt(item.total_descontos || 0)}</TableCell>
                          <TableCell className="font-bold">{fmt(item.salario_liquido)}</TableCell>
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
