'use client';

import { useState } from 'react';
import { DollarSign, ArrowLeft, Inbox } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

const summaryCards = [
  { title: 'Total Bruto', value: fmt(187450.00), color: 'text-blue-600', bgColor: 'bg-blue-50' },
  { title: 'Total Descontos', value: fmt(42380.00), color: 'text-red-600', bgColor: 'bg-red-50' },
  { title: 'Total Liquido', value: fmt(145070.00), color: 'text-green-600', bgColor: 'bg-green-50' },
  { title: 'Total INSS', value: fmt(22494.00), color: 'text-purple-600', bgColor: 'bg-purple-50' },
  { title: 'Total IRRF', value: fmt(8920.00), color: 'text-orange-600', bgColor: 'bg-orange-50' },
];

const funcionarios = [
  { nome: 'Carlos Silva', salarioBase: 2500, horasExtras: 450, adicNoturno: 375, inss: 275, irrf: 0, liquido: 3050 },
  { nome: 'Ana Souza', salarioBase: 2800, horasExtras: 0, adicNoturno: 0, inss: 308, irrf: 42, liquido: 2450 },
  { nome: 'Pedro Lima', salarioBase: 3200, horasExtras: 320, adicNoturno: 480, inss: 440, irrf: 95, liquido: 3465 },
  { nome: 'Maria Oliveira', salarioBase: 2500, horasExtras: 200, adicNoturno: 375, inss: 275, irrf: 0, liquido: 2800 },
  { nome: 'Roberto Alves', salarioBase: 2600, horasExtras: 0, adicNoturno: 390, inss: 286, irrf: 15, liquido: 2689 },
];

export default function FolhaPage() {
  const router = useRouter();
  const [periodo, setPeriodo] = useState('2026-03');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
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
          {funcionarios.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum registro na folha para este periodo</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Salario Base</TableHead>
                  <TableHead>Horas Extras</TableHead>
                  <TableHead>Adic. Noturno</TableHead>
                  <TableHead>INSS</TableHead>
                  <TableHead>IRRF</TableHead>
                  <TableHead>Liquido</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {funcionarios.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.nome}</TableCell>
                    <TableCell>{fmt(item.salarioBase)}</TableCell>
                    <TableCell>{fmt(item.horasExtras)}</TableCell>
                    <TableCell>{fmt(item.adicNoturno)}</TableCell>
                    <TableCell className="text-red-500">{fmt(item.inss)}</TableCell>
                    <TableCell className="text-red-500">{fmt(item.irrf)}</TableCell>
                    <TableCell className="font-bold">{fmt(item.liquido)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
