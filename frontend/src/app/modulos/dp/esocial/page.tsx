'use client';

import { ShieldCheck, ArrowLeft, Inbox } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const statusConfig: Record<string, { label: string; className: string }> = {
  pendente: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
  enviado: { label: 'Enviado', className: 'bg-blue-500 text-white' },
  aceito: { label: 'Aceito', className: 'bg-green-500 text-white' },
  rejeitado: { label: 'Rejeitado', className: 'bg-red-500 text-white' },
};

const eventos = [
  { evento: 'Admissao - Carlos Silva', tipo: 'S-2200', colaborador: 'Carlos Silva', status: 'aceito', data: '2026-03-10' },
  { evento: 'Alteracao Contratual - Ana Souza', tipo: 'S-2206', colaborador: 'Ana Souza', status: 'enviado', data: '2026-03-11' },
  { evento: 'Desligamento - Lucia Pereira', tipo: 'S-2299', colaborador: 'Lucia Pereira', status: 'pendente', data: '2026-03-12' },
  { evento: 'Afastamento - Maria Oliveira', tipo: 'S-2230', colaborador: 'Maria Oliveira', status: 'aceito', data: '2026-02-10' },
  { evento: 'Remuneracao - Folha Mar/2026', tipo: 'S-1200', colaborador: 'Todos', status: 'pendente', data: '2026-03-12' },
  { evento: 'Admissao - Pedro Lima', tipo: 'S-2200', colaborador: 'Pedro Lima', status: 'rejeitado', data: '2026-03-08' },
];

export default function ESocialPage() {
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
              <ShieldCheck className="h-6 w-6" />
              eSocial - Eventos
            </h1>
            <p className="text-muted-foreground">Gestao de eventos e obrigacoes do eSocial</p>
          </div>
        </div>
        <Button size="sm"><ShieldCheck className="h-4 w-4 mr-1" /> Enviar Pendentes</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {Object.entries(statusConfig).map(([key, val]) => {
          const count = eventos.filter((e) => e.status === key).length;
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
        <CardHeader><CardTitle>Eventos eSocial</CardTitle></CardHeader>
        <CardContent>
          {eventos.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum evento eSocial registrado</p>
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
                  <TableHead>Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {eventos.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.evento}</TableCell>
                    <TableCell><code className="text-xs bg-muted px-1.5 py-0.5 rounded">{item.tipo}</code></TableCell>
                    <TableCell>{item.colaborador}</TableCell>
                    <TableCell><Badge className={statusConfig[item.status].className}>{statusConfig[item.status].label}</Badge></TableCell>
                    <TableCell>{new Date(item.data).toLocaleDateString('pt-BR')}</TableCell>
                    <TableCell><Button variant="outline" size="sm">Detalhes</Button></TableCell>
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
