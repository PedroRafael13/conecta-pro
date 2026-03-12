'use client';

import { useState } from 'react';
import { Clock, ArrowLeft, Inbox, AlertTriangle, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const summaryCards = [
  { title: 'Total Horas', value: '1.760h', icon: Clock, color: 'text-blue-600', bgColor: 'bg-blue-50' },
  { title: 'Horas Extras', value: '48h', icon: Clock, color: 'text-green-600', bgColor: 'bg-green-50' },
  { title: 'Faltas', value: '3', icon: AlertTriangle, color: 'text-red-600', bgColor: 'bg-red-50' },
  { title: 'Atrasos', value: '7', icon: AlertTriangle, color: 'text-yellow-600', bgColor: 'bg-yellow-50' },
];

const statusConfig: Record<string, { label: string; className: string }> = {
  normal: { label: 'Normal', className: 'bg-green-500 text-white' },
  atraso: { label: 'Atraso', className: 'bg-yellow-500 text-white' },
  falta: { label: 'Falta', className: 'bg-red-500 text-white' },
  hora_extra: { label: 'Hora Extra', className: 'bg-blue-500 text-white' },
};

const registros = [
  { colaborador: 'Carlos Silva', data: '2026-03-12', entrada: '07:00', saida: '17:00', total: '10:00', status: 'hora_extra' },
  { colaborador: 'Ana Souza', data: '2026-03-12', entrada: '07:15', saida: '16:00', total: '08:45', status: 'atraso' },
  { colaborador: 'Pedro Lima', data: '2026-03-12', entrada: '07:00', saida: '16:00', total: '09:00', status: 'normal' },
  { colaborador: 'Maria Oliveira', data: '2026-03-12', entrada: '--:--', saida: '--:--', total: '00:00', status: 'falta' },
  { colaborador: 'Roberto Alves', data: '2026-03-12', entrada: '07:00', saida: '16:00', total: '09:00', status: 'normal' },
];

export default function PontoPage() {
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
              <Clock className="h-6 w-6" />
              Ponto Eletronico
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
              <p>Nenhum registro de ponto encontrado</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead>Entrada</TableHead>
                  <TableHead>Saida</TableHead>
                  <TableHead>Total Horas</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {registros.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.colaborador}</TableCell>
                    <TableCell>{new Date(item.data).toLocaleDateString('pt-BR')}</TableCell>
                    <TableCell>{item.entrada}</TableCell>
                    <TableCell>{item.saida}</TableCell>
                    <TableCell>{item.total}</TableCell>
                    <TableCell><Badge className={statusConfig[item.status].className}>{statusConfig[item.status].label}</Badge></TableCell>
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
