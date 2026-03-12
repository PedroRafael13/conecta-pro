'use client';

import { FolderOpen, ArrowLeft, Inbox, Eye, Download } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

const statusConfig: Record<string, { label: string; className: string }> = {
  valido: { label: 'Valido', className: 'bg-green-500 text-white' },
  vencido: { label: 'Vencido', className: 'bg-red-500 text-white' },
  pendente: { label: 'Pendente', className: 'bg-yellow-500 text-white' },
};

const documentos = [
  { colaborador: 'Carlos Silva', documento: 'RG', tipo: 'Identidade', dataUpload: '2024-06-01', status: 'valido' },
  { colaborador: 'Carlos Silva', documento: 'ASO Admissional', tipo: 'Saude', dataUpload: '2024-06-01', status: 'valido' },
  { colaborador: 'Ana Souza', documento: 'CNH', tipo: 'Habilitacao', dataUpload: '2025-09-01', status: 'vencido' },
  { colaborador: 'Ana Souza', documento: 'Certidao Nascimento', tipo: 'Civil', dataUpload: '2025-09-01', status: 'valido' },
  { colaborador: 'Pedro Lima', documento: 'ASO Periodico', tipo: 'Saude', dataUpload: null, status: 'pendente' },
  { colaborador: 'Maria Oliveira', documento: 'Certificado Vigilante', tipo: 'Profissional', dataUpload: '2023-03-10', status: 'vencido' },
];

export default function DocumentosPage() {
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
              <FolderOpen className="h-6 w-6" />
              Documentos de Colaboradores
            </h1>
            <p className="text-muted-foreground">Gestao de documentos dos colaboradores</p>
          </div>
        </div>
        <Button size="sm"><FolderOpen className="h-4 w-4 mr-1" /> Upload Documento</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Documentos</CardTitle></CardHeader>
        <CardContent>
          {documentos.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-12 w-12 mb-3" />
              <p>Nenhum documento encontrado</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Documento</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Data Upload</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Acoes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documentos.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.colaborador}</TableCell>
                    <TableCell>{item.documento}</TableCell>
                    <TableCell>{item.tipo}</TableCell>
                    <TableCell>{item.dataUpload ? new Date(item.dataUpload).toLocaleDateString('pt-BR') : '-'}</TableCell>
                    <TableCell><Badge className={statusConfig[item.status].className}>{statusConfig[item.status].label}</Badge></TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="outline" size="sm"><Eye className="h-3 w-3" /></Button>
                        <Button variant="outline" size="sm"><Download className="h-3 w-3" /></Button>
                      </div>
                    </TableCell>
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
