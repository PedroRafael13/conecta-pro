'use client';

import { useState } from 'react';
import { UserPlus, Filter, ArrowLeft, Inbox } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

type Status = 'documentos_pendentes' | 'exame_medico' | 'assinatura_contrato' | 'concluida';

const statusConfig: Record<Status, { label: string; className: string }> = {
  documentos_pendentes: { label: 'Documentos Pendentes', className: 'bg-yellow-500 text-white' },
  exame_medico: { label: 'Exame Medico', className: 'bg-blue-500 text-white' },
  assinatura_contrato: { label: 'Assinatura Contrato', className: 'bg-orange-500 text-white' },
  concluida: { label: 'Concluida', className: 'bg-green-500 text-white' },
};

const admissoes = [
  { nome: 'Carlos Silva', cpf: '123.456.789-00', cargo: 'Vigilante', status: 'documentos_pendentes' as Status, dataPrevista: '2026-03-20' },
  { nome: 'Ana Souza', cpf: '987.654.321-00', cargo: 'Porteira', status: 'exame_medico' as Status, dataPrevista: '2026-03-18' },
  { nome: 'Pedro Lima', cpf: '456.789.123-00', cargo: 'Vigilante Lider', status: 'assinatura_contrato' as Status, dataPrevista: '2026-03-15' },
  { nome: 'Maria Oliveira', cpf: '321.654.987-00', cargo: 'Vigilante', status: 'concluida' as Status, dataPrevista: '2026-03-10' },
];

export default function AdmissaoPage() {
  const router = useRouter();
  const [filtroStatus, setFiltroStatus] = useState<Status | 'todos'>('todos');

  const filtered = filtroStatus === 'todos'
    ? admissoes
    : admissoes.filter((a) => a.status === filtroStatus);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => router.push('/modulos/dp')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <UserPlus className="h-6 w-6" />
              Admissao de Colaboradores
            </h1>
            <p className="text-muted-foreground">Gerencie processos de admissao</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setFiltroStatus('todos')}>
            <Filter className="h-4 w-4 mr-1" /> Todos
          </Button>
          <Button size="sm"><UserPlus className="h-4 w-4 mr-1" /> Nova Admissao</Button>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {Object.entries(statusConfig).map(([key, val]) => (
          <Badge
            key={key}
            className={`cursor-pointer ${filtroStatus === key ? val.className : 'bg-muted text-muted-foreground'}`}
            onClick={() => setFiltroStatus(key as Status)}
          >
            {val.label}
          </Badge>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Processos de Admissao</CardTitle></CardHeader>
        <CardContent>
          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum processo de admissao encontrado</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>CPF</TableHead>
                  <TableHead>Cargo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Data Prevista</TableHead>
                  <TableHead>Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.nome}</TableCell>
                    <TableCell>{item.cpf}</TableCell>
                    <TableCell>{item.cargo}</TableCell>
                    <TableCell><Badge className={statusConfig[item.status].className}>{statusConfig[item.status].label}</Badge></TableCell>
                    <TableCell>{new Date(item.dataPrevista).toLocaleDateString('pt-BR')}</TableCell>
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
