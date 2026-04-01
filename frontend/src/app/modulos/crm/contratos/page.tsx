'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { customInstance } from '@/lib/api-client';
import {
  FileSignature,
  Search,
  RefreshCw,
  Plus,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  AlertCircle,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
import { formatCurrency } from '@/lib/utils';
import { toast } from 'sonner';

const STATUS_BADGE: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  active: 'bg-green-100 text-green-800',
  suspended: 'bg-yellow-100 text-yellow-800',
  terminated: 'bg-red-100 text-red-800',
};

const STATUS_LABEL: Record<string, string> = {
  draft: 'Rascunho',
  active: 'Ativo',
  suspended: 'Suspenso',
  terminated: 'Encerrado',
};

export default function ContratosPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const {
    data: contractsData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['crm-contracts', search, statusFilter, page],
    queryFn: async () => {
      const params: Record<string, any> = {
        skip: page * pageSize,
        limit: pageSize,
      };
      if (search) params.search = search;
      if (statusFilter !== 'all') params.status = statusFilter;
      const res = await customInstance({
        url: '/api/v1/crm/contracts',
        method: 'GET',
        params,
      });
      return res;
    },
  });

  const { data: statsData } = useQuery({
    queryKey: ['crm-contracts-stats'],
    queryFn: async () => {
      const res = await customInstance({
        url: '/api/v1/crm/contracts/stats',
        method: 'GET',
      });
      return res;
    },
  });

  const { data: alertsData } = useQuery({
    queryKey: ['crm-contracts-alerts'],
    queryFn: async () => {
      try {
        const res = await customInstance({
          url: '/api/v1/crm/contracts/alerts',
          method: 'GET',
        });
        return res;
      } catch {
        return null;
      }
    },
  });

  const contracts = (contractsData as any)?.items || (Array.isArray(contractsData) ? contractsData : []);
  const total = (contractsData as any)?.total || contracts.length;

  const st = statsData as any;
  const alerts = alertsData as any;
  const alertCount = alerts?.total || alerts?.length || 0;

  const stats = {
    total: st?.total || total,
    ativos: st?.active || st?.ativos || contracts.filter((c: any) => c.status === 'active').length,
    mrr: st?.mrr || st?.valor_mrr || contracts.reduce((acc: number, c: any) => acc + (c.monthly_value || c.valor_mensal || 0), 0),
    alertas: alertCount,
  };

  const handleDelete = async (id: string) => {
    try {
      await customInstance({
        url: `/api/v1/crm/contracts/${id}`,
        method: 'DELETE',
      });
      toast.success('Contrato removido com sucesso');
      refetch();
    } catch {
      toast.error('Erro ao remover contrato');
    }
  };

  const getStatusBadge = (status: string) => (
    <Badge className={STATUS_BADGE[status] || 'bg-gray-100 text-gray-800'}>
      {STATUS_LABEL[status] || status}
    </Badge>
  );

  const formatDate = (date: string | null | undefined) => {
    if (!date) return '-';
    try {
      return new Date(date).toLocaleDateString('pt-BR');
    } catch {
      return date;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FileSignature className="h-6 w-6" />
            Contratos
          </h1>
          <p className="text-muted-foreground">Gestao de contratos comerciais</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button onClick={() => toast.info('Formulario de novo contrato em desenvolvimento')}>
            <Plus className="h-4 w-4 mr-2" />
            Novo Contrato
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <FileSignature className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ativos</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.ativos}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor MRR</CardTitle>
            <DollarSign className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{formatCurrency(stats.mrr)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.alertas}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(0); }}
                placeholder="Buscar por numero, cliente..."
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(0); }}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os status</SelectItem>
                <SelectItem value="draft">Rascunho</SelectItem>
                <SelectItem value="active">Ativo</SelectItem>
                <SelectItem value="suspended">Suspenso</SelectItem>
                <SelectItem value="terminated">Encerrado</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-sm text-destructive flex-1">Erro ao carregar contratos</p>
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
          ) : contracts.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <FileSignature className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium">Nenhum contrato encontrado</h3>
              <p className="mt-2">Tente ajustar os filtros ou crie um novo contrato</p>
              <Button
                className="mt-4"
                onClick={() => toast.info('Formulario de novo contrato em desenvolvimento')}
              >
                <Plus className="h-4 w-4 mr-2" />
                Novo Contrato
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Numero</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Valor Mensal</TableHead>
                  <TableHead>Inicio</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[80px]">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {contracts.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="font-medium">
                        {item.number || item.numero || item.contract_number || '-'}
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {item.client_name || item.cliente || item.client?.name || '-'}
                    </TableCell>
                    <TableCell className="text-sm">
                      {item.type || item.tipo || item.contract_type || '-'}
                    </TableCell>
                    <TableCell className="text-sm font-medium">
                      {formatCurrency(item.monthly_value || item.valor_mensal || 0)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {formatDate(item.start_date || item.data_inicio)}
                    </TableCell>
                    <TableCell>{getStatusBadge(item.status || 'draft')}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => toast.info('Detalhes do contrato em desenvolvimento')}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            Ver detalhes
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => toast.info('Edição de contrato em desenvolvimento')}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Editar
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => handleDelete(item.id)}
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
              Proximo
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
