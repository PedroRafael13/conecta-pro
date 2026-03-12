'use client';

import { Sun, ArrowLeft, Inbox } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const statusConfig: Record<string, { label: string; className: string }> = {
  programada: { label: 'Programada', className: 'bg-blue-500 text-white' },
  em_gozo: { label: 'Em Gozo', className: 'bg-green-500 text-white' },
  vencida: { label: 'Vencida', className: 'bg-red-500 text-white' },
  concluida: { label: 'Concluida', className: 'bg-gray-500 text-white' },
};

const ferias = [
  { colaborador: 'Carlos Silva', periodoAquisitivo: '06/2024 - 06/2025', diasDireito: 30, diasGozados: 0, saldo: 30, status: 'programada' },
  { colaborador: 'Ana Souza', periodoAquisitivo: '09/2024 - 09/2025', diasDireito: 30, diasGozados: 15, saldo: 15, status: 'em_gozo' },
  { colaborador: 'Pedro Lima', periodoAquisitivo: '01/2025 - 01/2026', diasDireito: 30, diasGozados: 0, saldo: 30, status: 'programada' },
  { colaborador: 'Maria Oliveira', periodoAquisitivo: '03/2024 - 03/2025', diasDireito: 30, diasGozados: 30, saldo: 0, status: 'concluida' },
  { colaborador: 'Roberto Alves', periodoAquisitivo: '01/2024 - 01/2025', diasDireito: 30, diasGozados: 0, saldo: 30, status: 'vencida' },
];

export default function FeriasPage() {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Sun className="h-6 w-6" />
              Gestao de Ferias
            </h1>
            <p className="text-muted-foreground">Programacao e controle de ferias dos colaboradores</p>
          </div>
        </div>
        <Button size="sm"><Sun className="h-4 w-4 mr-1" /> Programar Ferias</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {Object.entries(statusConfig).map(([key, val]) => {
          const count = ferias.filter((f) => f.status === key).length;
          return (
            <Card key={key}>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">{val.label}</p>
                <p className="text-2xl font-bold">{count}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader><CardTitle>Ferias dos Colaboradores</CardTitle></CardHeader>
        <CardContent>
          {ferias.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum registro de ferias encontrado</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Periodo Aquisitivo</TableHead>
                  <TableHead>Dias Direito</TableHead>
                  <TableHead>Dias Gozados</TableHead>
                  <TableHead>Saldo</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ferias.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.colaborador}</TableCell>
                    <TableCell>{item.periodoAquisitivo}</TableCell>
                    <TableCell>{item.diasDireito}</TableCell>
                    <TableCell>{item.diasGozados}</TableCell>
                    <TableCell className="font-bold">{item.saldo}</TableCell>
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
