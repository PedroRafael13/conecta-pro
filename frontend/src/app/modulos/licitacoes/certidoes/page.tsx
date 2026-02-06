'use client';

import {
  Shield,
  Search,
  RefreshCw,
  Upload,
  MoreHorizontal,
  Download,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle,
  RefreshCcw,
} from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ConfirmModal } from '@/components/ui/modal';
import { toast } from 'sonner';
import {
  useListarCertidoes,
  useCriarCertidao,
  useRemoverCertidao,
  useRenovarCertidoes,
  useValidarCertidaoBidding,
  useDownloadCertidao,
} from '@/hooks/bidding/useCertificates';
import { CertificateUploadModal } from '@/components/licitacoes/CertificateUploadModal';
import { CertificateStatusBadge } from '@/components/licitacoes/CertificateStatusBadge';
import { CertificateTypeIcon } from '@/components/licitacoes/CertificateTypeIcon';
import { formatDate } from '@/lib/utils';

export default function CertidoesPage() {
  const [search, setSearch] = useState('');
  const [tipoFilter, setTipoFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const { data: certidoesData, isLoading, error, refetch } = useListarCertidoes({
    tipo: tipoFilter !== 'all' ? tipoFilter : undefined,
    status: statusFilter !== 'all' ? statusFilter : undefined,
    page,
    size: pageSize,
  });

  const criarMutation = useCriarCertidao();
  const removerMutation = useRemoverCertidao();
  const renovarMutation = useRenovarCertidoes();
  const validarMutation = useValidarCertidaoBidding();
  const downloadMutation = useDownloadCertidao();

  const [uploadOpen, setUploadOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{
    title: string;
    message: string;
    action: () => Promise<void>;
    variant: 'danger' | 'warning' | 'info';
  } | null>(null);

  const certidoes = (certidoesData as any)?.items || (Array.isArray(certidoesData) ? certidoesData : []);
  const total = (certidoesData as any)?.total || certidoes.length;

  // Calcular stats por tipo
  const statsPorTipo = {
    federal: certidoes.filter((c: any) => c.tipo_certidao?.includes('federal')),
    estadual: certidoes.filter((c: any) => c.tipo_certidao?.includes('estadual')),
    municipal: certidoes.filter((c: any) => c.tipo_certidao?.includes('municipal')),
    trabalhista: certidoes.filter((c: any) => c.tipo_certidao?.includes('trabalhista') || c.tipo_certidao?.includes('cndt')),
  };

  const getStatusForGroup = (group: any[]) => {
    const vencidas = group.filter((c: any) => c.status === 'vencida').length;
    const vencendo = group.filter((c: any) => c.status === 'vencendo').length;
    const validas = group.filter((c: any) => c.status === 'valida').length;

    if (vencidas > 0) return { status: 'vencida', count: vencidas };
    if (vencendo > 0) return { status: 'vencendo', count: vencendo };
    if (validas > 0) return { status: 'valida', count: validas };
    return { status: 'pendente', count: 0 };
  };

  const openConfirm = (
    title: string,
    message: string,
    action: () => Promise<void>,
    variant: 'danger' | 'warning' | 'info' = 'warning'
  ) => {
    setConfirmAction({ title, message, action, variant });
    setConfirmOpen(true);
  };

  const handleUploadSubmit = async (data: any) => {
    try {
      await criarMutation.mutateAsync(data);
      setUploadOpen(false);
    } catch (err) {
      // Error handled by mutation
    }
  };

  const handleRenovarTodas = async () => {
    try {
      await renovarMutation.mutateAsync({ cnpj: '' }); // Backend vai renovar todas
      toast.success('Renovação iniciada');
    } catch (err) {
      // Error handled by mutation
    }
  };

  const handleValidar = async (certificateId: string) => {
    try {
      await validarMutation.mutateAsync(certificateId);
    } catch (err) {
      // Error handled by mutation
    }
  };

  const handleDownload = async (certificateId: string) => {
    try {
      await downloadMutation.mutateAsync(certificateId);
    } catch (err) {
      // Error handled by mutation
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Certidões Negativas
          </h1>
          <p className="text-muted-foreground">Gestão de certidões e regularidade fiscal</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button variant="outline" onClick={handleRenovarTodas} disabled={renovarMutation.isPending}>
            <RefreshCcw className="h-4 w-4 mr-2" />
            Renovar Todas
          </Button>
          <Button onClick={() => setUploadOpen(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Upload Certidão
          </Button>
        </div>
      </div>

      {/* Stats Cards por Tipo */}
      <div className="grid gap-4 md:grid-cols-4">
        {[
          { key: 'federal', label: 'Federal', icon: Shield },
          { key: 'estadual', label: 'Estadual', icon: Shield },
          { key: 'municipal', label: 'Municipal', icon: Shield },
          { key: 'trabalhista', label: 'Trabalhista', icon: Shield },
        ].map(({ key, label, icon: Icon }) => {
          const group = statsPorTipo[key as keyof typeof statsPorTipo];
          const statusInfo = getStatusForGroup(group);

          return (
            <Card key={key}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{label}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-2xl font-bold">{group.length}</div>
                  <div>
                    {statusInfo.status === 'valida' && (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    )}
                    {statusInfo.status === 'vencendo' && (
                      <Clock className="h-5 w-5 text-yellow-600" />
                    )}
                    {statusInfo.status === 'vencida' && (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                    {statusInfo.status === 'pendente' && (
                      <AlertCircle className="h-5 w-5 text-gray-600" />
                    )}
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {statusInfo.status === 'valida' && 'Todas válidas'}
                  {statusInfo.status === 'vencendo' && `${statusInfo.count} vencendo`}
                  {statusInfo.status === 'vencida' && `${statusInfo.count} vencida(s)`}
                  {statusInfo.status === 'pendente' && 'Nenhuma cadastrada'}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(0);
                }}
                placeholder="Buscar por CNPJ, número..."
                className="pl-10"
              />
            </div>
            <Select
              value={tipoFilter}
              onValueChange={(v) => {
                setTipoFilter(v);
                setPage(0);
              }}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os tipos</SelectItem>
                <SelectItem value="federal">Federal</SelectItem>
                <SelectItem value="estadual">Estadual</SelectItem>
                <SelectItem value="municipal">Municipal</SelectItem>
                <SelectItem value="trabalhista">Trabalhista</SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={statusFilter}
              onValueChange={(v) => {
                setStatusFilter(v);
                setPage(0);
              }}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os status</SelectItem>
                <SelectItem value="valida">Válida</SelectItem>
                <SelectItem value="vencendo">Vencendo</SelectItem>
                <SelectItem value="vencida">Vencida</SelectItem>
                <SelectItem value="pendente">Pendente</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive flex-1">Erro ao carregar certidões</p>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : certidoes.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Shield className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium">Nenhuma certidão encontrada</h3>
              <p className="mt-2">Faça upload de uma certidão para começar</p>
              <Button className="mt-4" onClick={() => setUploadOpen(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Certidão
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Órgão Emissor</TableHead>
                  <TableHead>Número</TableHead>
                  <TableHead>Data Emissão</TableHead>
                  <TableHead>Validade</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[80px]">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {certidoes.map((certidao: any) => (
                  <TableRow key={certidao.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <CertificateTypeIcon tipo={certidao.tipo_certidao} className="h-4 w-4" />
                        <span className="text-sm">{certidao.tipo_certidao}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm">
                      {certidao.orgao_emissor || 'N/A'}
                    </TableCell>
                    <TableCell className="text-sm font-mono">
                      {certidao.numero_certidao}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(certidao.data_emissao)}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(certidao.data_validade)}
                    </TableCell>
                    <TableCell>
                      <CertificateStatusBadge status={certidao.status || 'pendente'} />
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleDownload(certidao.id)}>
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleValidar(certidao.id)}>
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Validar
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() =>
                              openConfirm(
                                'Renovar Certidão',
                                `Renovar automaticamente "${certidao.tipo_certidao}"?`,
                                async () => {
                                  await renovarMutation.mutateAsync({ cnpj: certidao.cnpj });
                                },
                                'info'
                              )
                            }
                          >
                            <RefreshCcw className="h-4 w-4 mr-2" />
                            Renovar
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() =>
                              openConfirm(
                                'Deletar Certidão',
                                `Deletar certidão "${certidao.numero_certidao}" permanentemente?`,
                                () => removerMutation.mutateAsync(certidao.id),
                                'danger'
                              )
                            }
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Deletar
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Mostrando {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} de {total}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * pageSize >= total}
            >
              Próximo
            </Button>
          </div>
        </div>
      )}

      {/* Modals */}
      <CertificateUploadModal
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onSubmit={handleUploadSubmit}
        isLoading={criarMutation.isPending}
      />

      {confirmAction && (
        <ConfirmModal
          isOpen={confirmOpen}
          onClose={() => setConfirmOpen(false)}
          onConfirm={async () => {
            await confirmAction.action();
            setConfirmOpen(false);
          }}
          title={confirmAction.title}
          message={confirmAction.message}
          variant={confirmAction.variant}
          isLoading={removerMutation.isPending || renovarMutation.isPending}
        />
      )}
    </div>
  );
}
