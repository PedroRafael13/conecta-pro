'use client';

import { Users, Search, RefreshCw, Plus, MoreHorizontal, Eye, Edit, Trash2, AlertCircle, Lock, Unlock, ArrowLeft, CheckCircle, XCircle } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ConfirmModal } from '@/components/ui/modal';
;
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  useSuppliers,
  useSupplierStats,
  useCreateSupplier,
  useUpdateSupplier,
  useDeleteSupplier,
  useBlockSupplier,
  useUnblockSupplier,
} from '@/hooks/financial/useSuppliers';
import { SupplierFormModal } from '@/components/financeiro/supplier-form-modal';
import { SupplierDetailModal } from '@/components/financeiro/supplier-detail-modal';
import { cn } from '@/lib/utils';

export default function FornecedoresPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [showFormModal, setShowFormModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<any>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Hooks de dados
  const {
    data: suppliersData,
    isLoading,
    isError,
    error,
    refetch,
  } = useSuppliers({
    ...(search && { search }),
    ...(statusFilter && { status: statusFilter }),
  });

  const { data: stats, refetch: refetchStats } = useSupplierStats();
  const createSupplier = useCreateSupplier();
  const updateSupplier = useUpdateSupplier();
  const deleteSupplierMutation = useDeleteSupplier();
  const blockSupplier = useBlockSupplier();
  const unblockSupplier = useUnblockSupplier();

  const suppliers = suppliersData?.data || suppliersData?.items || [];
  const total = suppliersData?.total || suppliers.length;

  // Stats
  const totalSuppliers = stats?.total || total;
  const activeSuppliers = stats?.active || suppliers.filter((s: any) => s.status === 'active').length;
  const blockedSuppliers = stats?.blocked || suppliers.filter((s: any) => s.status === 'blocked').length;

  const handleView = (supplier: any) => {
    setSelectedSupplier(supplier);
    setShowDetailModal(true);
  };

  const handleEdit = (supplier: any) => {
    setSelectedSupplier(supplier);
    setShowFormModal(true);
    setShowDetailModal(false);
  };

  const handleCreate = () => {
    setSelectedSupplier(null);
    setShowFormModal(true);
  };

  const handleDelete = (supplier: any) => {
    setSelectedSupplier(supplier);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedSupplier) return;
    setIsDeleting(true);

    try {
      await deleteSupplierMutation.mutateAsync({ supplierId: selectedSupplier.id });
      setShowDeleteModal(false);
      setSelectedSupplier(null);
      // refetch() removido - mutation já invalida queries automaticamente
    } catch (err) {
      console.error('Erro ao excluir fornecedor:', err);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleBlock = async (supplier: any) => {
    try {
      await blockSupplier.mutateAsync({ supplierId: supplier.id });
      // refetch() removido - mutation já invalida queries automaticamente
    } catch (err) {
      console.error('Erro ao bloquear fornecedor:', err);
    }
  };

  const handleUnblock = async (supplier: any) => {
    try {
      await unblockSupplier.mutateAsync({ supplierId: supplier.id });
      // refetch() removido - mutation já invalida queries automaticamente
    } catch (err) {
      console.error('Erro ao desbloquear fornecedor:', err);
    }
  };

  const handleFormSubmit = async (data: any) => {
    try {
      if (selectedSupplier) {
        await updateSupplier.mutateAsync({
          supplierId: selectedSupplier.id,
          data,
        });
      } else {
        await createSupplier.mutateAsync({ data });
      }
      setShowFormModal(false);
      setSelectedSupplier(null);
      // refetch() removido - mutation já invalida queries automaticamente
    } catch (err) {
      console.error('Erro ao salvar fornecedor:', err);
      throw err;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'blocked':
        return 'bg-red-500/10 text-red-500 border-red-500/30';
      case 'inactive':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Ativo';
      case 'blocked':
        return 'Bloqueado';
      case 'inactive':
        return 'Inativo';
      default:
        return status;
    }
  };

  // Filter localmente por search
  const filteredSuppliers = search
    ? suppliers.filter((s: any) =>
        s.name?.toLowerCase().includes(search.toLowerCase()) ||
        s.document?.toLowerCase().includes(search.toLowerCase()) ||
        s.email?.toLowerCase().includes(search.toLowerCase())
      )
    : suppliers;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link href="/modulos/financeiro">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Financeiro
            </Button>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-orange-500" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                Fornecedores
              </h1>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {total} fornecedores cadastrados
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => { refetch(); refetchStats(); }}
            disabled={isLoading}
          >
            <RefreshCw className={cn('w-4 h-4', isLoading && 'animate-spin')} />
          </Button>
          <Button variant="primary" size="sm" onClick={handleCreate}>
            <Plus className="w-4 h-4 mr-2" />
            Novo Fornecedor
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {isLoading ? '...' : totalSuppliers}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Total</p>
            </div>
          </div>
        </div>

        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {isLoading ? '...' : activeSuppliers}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Ativos</p>
            </div>
          </div>
        </div>

        <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {isLoading ? '...' : blockedSuppliers}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Bloqueados</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            type="search"
            placeholder="Buscar por nome, CNPJ/CPF ou email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            icon={<Search className="w-4 h-4" />}
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={statusFilter === undefined ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setStatusFilter(undefined)}
          >
            Todos
          </Button>
          <Button
            variant={statusFilter === 'active' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setStatusFilter('active')}
          >
            Ativos
          </Button>
          <Button
            variant={statusFilter === 'blocked' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setStatusFilter('blocked')}
          >
            Bloqueados
          </Button>
        </div>
      </div>

      {/* Error */}
      {isError && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-[hsl(var(--destructive))]/10 border border-[hsl(var(--destructive))]/30">
          <AlertCircle className="w-5 h-5 text-[hsl(var(--destructive))]" />
          <div>
            <p className="font-medium text-[hsl(var(--destructive))]">Erro ao carregar fornecedores</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {(error as Error)?.message || 'Tente novamente em alguns instantes'}
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => refetch()} className="ml-auto">
            Tentar novamente
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="divide-y divide-[hsl(var(--border))]">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="p-4 flex items-center gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-48 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                    <div className="h-3 w-32 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                  </div>
                  <div className="h-6 w-20 bg-[hsl(var(--secondary))] rounded animate-shimmer" />
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[hsl(var(--border))]">
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Nome
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                      CNPJ/CPF
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden lg:table-cell">
                      Email
                    </th>
                    <th className="text-left p-4 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                      Status
                    </th>
                    <th className="text-center p-4 text-sm font-medium text-[hsl(var(--muted-foreground))] hidden md:table-cell">
                      Qualificacao
                    </th>
                    <th className="w-12 p-4"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[hsl(var(--border))]">
                  {filteredSuppliers.map((supplier: any) => (
                    <tr
                      key={supplier.id}
                      className="hover:bg-[hsl(var(--secondary))]/50 transition-colors cursor-pointer"
                      onClick={() => handleView(supplier)}
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center flex-shrink-0">
                            <Users className="w-5 h-5 text-orange-500" />
                          </div>
                          <div>
                            <p className="font-medium text-[hsl(var(--foreground))]">
                              {supplier.name}
                            </p>
                            <p className="text-xs text-[hsl(var(--muted-foreground))] md:hidden">
                              {supplier.document || '-'}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="p-4 hidden md:table-cell">
                        <span className="text-sm text-[hsl(var(--muted-foreground))] font-mono">
                          {supplier.document || '-'}
                        </span>
                      </td>
                      <td className="p-4 hidden lg:table-cell">
                        <span className="text-sm text-[hsl(var(--muted-foreground))]">
                          {supplier.email || '-'}
                        </span>
                      </td>
                      <td className="p-4">
                        <span
                          className={cn(
                            'inline-flex px-2 py-1 text-xs font-medium rounded-full border',
                            getStatusColor(supplier.status)
                          )}
                        >
                          {getStatusLabel(supplier.status)}
                        </span>
                      </td>
                      <td className="p-4 hidden md:table-cell text-center">
                        {supplier.qualification_score != null ? (
                          <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                            {supplier.qualification_score}/10
                          </span>
                        ) : (
                          <span className="text-sm text-[hsl(var(--muted-foreground))]">-</span>
                        )}
                      </td>
                      <td className="p-4" onClick={(e) => e.stopPropagation()}>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleView(supplier)}>
                              <Eye className="w-4 h-4 mr-2" />
                              Visualizar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEdit(supplier)}>
                              <Edit className="w-4 h-4 mr-2" />
                              Editar
                            </DropdownMenuItem>
                            {supplier.status === 'active' ? (
                              <DropdownMenuItem onClick={() => handleBlock(supplier)}>
                                <Lock className="w-4 h-4 mr-2" />
                                Bloquear
                              </DropdownMenuItem>
                            ) : (
                              <DropdownMenuItem onClick={() => handleUnblock(supplier)}>
                                <Unlock className="w-4 h-4 mr-2" />
                                Desbloquear
                              </DropdownMenuItem>
                            )}
                            <DropdownMenuItem
                              onClick={() => handleDelete(supplier)}
                              className="text-red-500"
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Excluir
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !isError && filteredSuppliers.length === 0 && (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
              <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                Nenhum fornecedor encontrado
              </h3>
              <p className="text-[hsl(var(--muted-foreground))] mt-1">
                {search || statusFilter
                  ? 'Tente ajustar os filtros de busca'
                  : 'Cadastre seu primeiro fornecedor'}
              </p>
              {!search && !statusFilter && (
                <Button className="mt-4" onClick={handleCreate}>
                  <Plus className="w-4 h-4 mr-2" />
                  Novo Fornecedor
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination info */}
      {!isLoading && filteredSuppliers.length > 0 && (
        <div className="text-sm text-[hsl(var(--muted-foreground))] text-center">
          Mostrando {filteredSuppliers.length} de {total} fornecedores
        </div>
      )}

      {/* Modals */}
      <SupplierFormModal
        isOpen={showFormModal}
        onClose={() => {
          setShowFormModal(false);
          setSelectedSupplier(null);
        }}
        supplier={selectedSupplier}
        onSubmit={handleFormSubmit}
        isLoading={createSupplier.isPending || updateSupplier.isPending}
      />

      <SupplierDetailModal
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedSupplier(null);
        }}
        supplier={selectedSupplier}
      />

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedSupplier(null);
        }}
        onConfirm={confirmDelete}
        title="Excluir Fornecedor"
        message={`Tem certeza que deseja excluir o fornecedor "${selectedSupplier?.name}"? Esta acao nao pode ser desfeita.`}
        confirmText="Excluir"
        cancelText="Cancelar"
        variant="danger"
        isLoading={isDeleting}
      />
    </div>
  );
}
