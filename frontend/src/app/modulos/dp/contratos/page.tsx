'use client';

import { FileText, ArrowLeft, Inbox } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const statusConfig: Record<string, { label: string; className: string }> = {
  ativo: { label: 'Ativo', className: 'bg-green-500 text-white' },
  vencido: { label: 'Vencido', className: 'bg-red-500 text-white' },
  suspenso: { label: 'Suspenso', className: 'bg-yellow-500 text-white' },
  encerrado: { label: 'Encerrado', className: 'bg-gray-500 text-white' },
};

const contratos = [
  { colaborador: 'Carlos Silva', tipo: 'CLT Indeterminado', inicio: '2024-06-01', fim: null, salarioBase: 2500.00, status: 'ativo' },
  { colaborador: 'Ana Souza', tipo: 'CLT Determinado', inicio: '2025-09-01', fim: '2026-09-01', salarioBase: 2800.00, status: 'ativo' },
  { colaborador: 'Pedro Lima', tipo: 'Temporario', inicio: '2026-01-15', fim: '2026-07-15', salarioBase: 2200.00, status: 'ativo' },
  { colaborador: 'Lucia Pereira', tipo: 'CLT Indeterminado', inicio: '2023-03-10', fim: null, salarioBase: 3100.00, status: 'encerrado' },
  { colaborador: 'Roberto Alves', tipo: 'CLT Determinado', inicio: '2025-01-01', fim: '2026-01-01', salarioBase: 2600.00, status: 'vencido' },
];

export default function ContratosPage() {
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
              <FileText className="h-6 w-6" />
              Contratos de Trabalho
            </h1>
            <p className="text-muted-foreground">Gerencie contratos de trabalho dos colaboradores</p>
          </div>
        </div>
        <Button size="sm"><FileText className="h-4 w-4 mr-1" /> Novo Contrato</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Contratos</CardTitle></CardHeader>
        <CardContent>
          {contratos.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum contrato encontrado</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Inicio</TableHead>
                  <TableHead>Fim</TableHead>
                  <TableHead>Salario Base</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {contratos.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.colaborador}</TableCell>
                    <TableCell>{item.tipo}</TableCell>
                    <TableCell>{new Date(item.inicio).toLocaleDateString('pt-BR')}</TableCell>
                    <TableCell>{item.fim ? new Date(item.fim).toLocaleDateString('pt-BR') : 'Indeterminado'}</TableCell>
                    <TableCell>R$ {item.salarioBase.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</TableCell>
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
