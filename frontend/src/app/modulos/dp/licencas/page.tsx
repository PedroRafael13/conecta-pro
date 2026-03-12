'use client';

import { CalendarDays, ArrowLeft, Inbox } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const statusConfig: Record<string, { label: string; className: string }> = {
  ativa: { label: 'Ativa', className: 'bg-green-500 text-white' },
  encerrada: { label: 'Encerrada', className: 'bg-gray-500 text-white' },
  pendente: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
};

const tipoConfig: Record<string, string> = {
  medica: 'Licenca Medica',
  maternidade: 'Maternidade',
  paternidade: 'Paternidade',
  acidente: 'Acidente de Trabalho',
  obito: 'Nojo (Obito)',
  casamento: 'Gala (Casamento)',
};

const licencas = [
  { colaborador: 'Ana Souza', tipo: 'medica', inicio: '2026-03-01', fim: '2026-03-15', dias: 15, status: 'ativa' },
  { colaborador: 'Maria Oliveira', tipo: 'maternidade', inicio: '2026-02-10', fim: '2026-06-10', dias: 120, status: 'ativa' },
  { colaborador: 'Pedro Lima', tipo: 'paternidade', inicio: '2026-03-05', fim: '2026-03-25', dias: 20, status: 'ativa' },
  { colaborador: 'Roberto Alves', tipo: 'acidente', inicio: '2026-01-10', fim: '2026-02-10', dias: 30, status: 'encerrada' },
  { colaborador: 'Carlos Silva', tipo: 'obito', inicio: '2026-03-10', fim: '2026-03-12', dias: 2, status: 'pendente' },
];

export default function LicencasPage() {
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
              <CalendarDays className="h-6 w-6" />
              Licencas e Afastamentos
            </h1>
            <p className="text-muted-foreground">Controle de licencas e afastamentos</p>
          </div>
        </div>
        <Button size="sm"><CalendarDays className="h-4 w-4 mr-1" /> Nova Licenca</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Licencas Registradas</CardTitle></CardHeader>
        <CardContent>
          {licencas.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhuma licenca registrada</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Inicio</TableHead>
                  <TableHead>Fim</TableHead>
                  <TableHead>Dias</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {licencas.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.colaborador}</TableCell>
                    <TableCell>{tipoConfig[item.tipo]}</TableCell>
                    <TableCell>{new Date(item.inicio).toLocaleDateString('pt-BR')}</TableCell>
                    <TableCell>{new Date(item.fim).toLocaleDateString('pt-BR')}</TableCell>
                    <TableCell>{item.dias}</TableCell>
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
