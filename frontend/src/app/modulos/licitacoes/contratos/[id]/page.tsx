'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import {
  FileSignature,
  ArrowLeft,
  Edit,
  Plus,
  RefreshCw,
  FileText,
  Calendar,
  DollarSign,
  Building2,
  AlertCircle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useBuscarContrato, useAditivar } from '@/hooks/bidding/useContracts';
import { ContractStatusBadge } from '@/components/licitacoes/ContractStatusBadge';
import { ContractAddendumModal } from '@/components/licitacoes/ContractAddendumModal';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function ContratoDetalhePage() {
  const params = useParams();
  const router = useRouter();
  const contractId = params.id as string;

  const { data: contrato, isLoading, error, refetch } = useBuscarContrato(contractId);
  const aditivarMutation = useAditivar();

  const [addendumOpen, setAddendumOpen] = useState(false);

  const handleAddendumSubmit = async (data: any) => {
    try {
      await aditivarMutation.mutateAsync(data);
      setAddendumOpen(false);
      refetch();
    } catch (err) {
      // Error handled by mutation
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (error || !contrato) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </Button>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive flex-1">Erro ao carregar contrato</p>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Tentar novamente
          </Button>
        </div>
      </div>
    );
  }

  const c = contrato as any;
  const aditivos = c.aditivos || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Button variant="ghost" onClick={() => router.back()} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FileSignature className="h-6 w-6" />
            Contrato {c.numero_contrato}
          </h1>
          <p className="text-muted-foreground">{c.orgao_contratante}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button variant="outline" onClick={() => router.push(`/modulos/licitacoes/contratos/${contractId}/editar`)}>
            <Edit className="h-4 w-4 mr-2" />
            Editar
          </Button>
        </div>
      </div>

      <Tabs defaultValue="dados" className="space-y-4">
        <TabsList>
          <TabsTrigger value="dados">Dados Gerais</TabsTrigger>
          <TabsTrigger value="aditivos">
            Aditivos
            {aditivos.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {aditivos.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="medicoes">Medições</TabsTrigger>
          <TabsTrigger value="documentos">Documentos</TabsTrigger>
        </TabsList>

        {/* Dados Gerais */}
        <TabsContent value="dados" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Informações do Contrato</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Número do Contrato</p>
                <p className="font-medium">{c.numero_contrato}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <div className="mt-1">
                  <ContractStatusBadge status={c.status || 'vigente'} />
                </div>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-muted-foreground">Órgão Contratante</p>
                <p className="font-medium flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  {c.orgao_contratante}
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-muted-foreground">Objeto</p>
                <p className="font-medium">{c.objeto}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Valor Total</p>
                <p className="font-medium text-lg flex items-center gap-2">
                  <DollarSign className="h-5 w-5 text-green-600" />
                  {formatCurrency(c.valor_total || 0)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">ID da Proposta</p>
                <p className="font-medium text-xs">{c.proposta_id || 'N/A'}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Datas e Vigência</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Data de Assinatura</p>
                <p className="font-medium flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  {formatDate(c.data_assinatura)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Data de Início</p>
                <p className="font-medium flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-green-600" />
                  {formatDate(c.data_inicio)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Data de Término</p>
                <p className="font-medium flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-red-600" />
                  {formatDate(c.data_fim)}
                </p>
              </div>
            </CardContent>
          </Card>

          {c.observacoes && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Observações</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{c.observacoes}</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Aditivos */}
        <TabsContent value="aditivos" className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {aditivos.length} aditivo(s) cadastrado(s)
            </p>
            <Button onClick={() => setAddendumOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Aditivo
            </Button>
          </div>

          <Card>
            <CardContent className="p-0">
              {aditivos.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-medium">Nenhum aditivo cadastrado</h3>
                  <p className="mt-2">Crie um aditivo para registrar alterações no contrato</p>
                  <Button className="mt-4" onClick={() => setAddendumOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Novo Aditivo
                  </Button>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Data</TableHead>
                      <TableHead>Valor/Prazo</TableHead>
                      <TableHead>Justificativa</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {aditivos.map((aditivo: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Badge variant="outline">
                            {aditivo.tipo_aditivo === 'prazo' && 'Prazo'}
                            {aditivo.tipo_aditivo === 'valor' && 'Valor'}
                            {aditivo.tipo_aditivo === 'escopo' && 'Escopo'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">
                          {formatDate(aditivo.data_aditivo)}
                        </TableCell>
                        <TableCell className="text-sm font-medium">
                          {aditivo.tipo_aditivo === 'valor' && formatCurrency(aditivo.novo_valor || 0)}
                          {aditivo.tipo_aditivo === 'prazo' && formatDate(aditivo.nova_data_fim)}
                          {aditivo.tipo_aditivo === 'escopo' && '-'}
                        </TableCell>
                        <TableCell className="text-sm max-w-md truncate">
                          {aditivo.justificativa}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Medições */}
        <TabsContent value="medicoes" className="space-y-4">
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-muted-foreground">
                <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium">Funcionalidade em Desenvolvimento</h3>
                <p className="mt-2">O módulo de medições será implementado em breve</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Documentos */}
        <TabsContent value="documentos" className="space-y-4">
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-muted-foreground">
                <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium">Documentos do Contrato</h3>
                <p className="mt-2">Documentos relacionados ao contrato aparecerão aqui</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal de Aditivo */}
      <ContractAddendumModal
        isOpen={addendumOpen}
        onClose={() => setAddendumOpen(false)}
        onSubmit={handleAddendumSubmit}
        contractId={contractId}
        isLoading={aditivarMutation.isPending}
      />
    </div>
  );
}
