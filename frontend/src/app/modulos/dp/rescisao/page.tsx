'use client';

import { UserMinus, ArrowLeft, Inbox } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const statusConfig: Record<string, { label: string; className: string }> = {
  em_andamento: { label: 'Em Andamento', className: 'bg-yellow-500 text-white' },
  calculo_pendente: { label: 'Calculo Pendente', className: 'bg-orange-500 text-white' },
  homologacao: { label: 'Homologacao', className: 'bg-blue-500 text-white' },
  concluida: { label: 'Concluida', className: 'bg-green-500 text-white' },
};

const tipoConfig: Record<string, string> = {
  voluntaria: 'Voluntaria',
  involuntaria: 'Involuntaria',
  justa_causa: 'Justa Causa',
  acordo: 'Acordo Mutuo',
};

const rescisoes = [
  { nome: 'Roberto Alves', tipo: 'voluntaria', status: 'em_andamento', ultimoDia: '2026-03-31', valorTotal: 8450.00 },
  { nome: 'Fernanda Costa', tipo: 'involuntaria', status: 'calculo_pendente', ultimoDia: '2026-03-25', valorTotal: 12300.00 },
  { nome: 'Marcos Santos', tipo: 'acordo', status: 'homologacao', ultimoDia: '2026-03-20', valorTotal: 9875.50 },
  { nome: 'Lucia Pereira', tipo: 'justa_causa', status: 'concluida', ultimoDia: '2026-03-05', valorTotal: 3200.00 },
];

export default function RescisaoPage() {
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
              <UserMinus className="h-6 w-6" />
              Processos de Rescisao
            </h1>
            <p className="text-muted-foreground">Gerencie desligamentos e rescisoes</p>
          </div>
        </div>
        <Button size="sm"><UserMinus className="h-4 w-4 mr-1" /> Iniciar Rescisao</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Rescisoes</CardTitle></CardHeader>
        <CardContent>
          {rescisoes.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum processo de rescisao encontrado</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ultimo Dia</TableHead>
                  <TableHead>Valor Total</TableHead>
                  <TableHead>Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rescisoes.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.nome}</TableCell>
                    <TableCell>{tipoConfig[item.tipo]}</TableCell>
                    <TableCell><Badge className={statusConfig[item.status].className}>{statusConfig[item.status].label}</Badge></TableCell>
                    <TableCell>{new Date(item.ultimoDia).toLocaleDateString('pt-BR')}</TableCell>
                    <TableCell>R$ {item.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</TableCell>
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
