'use client';

import { Users, Search, RefreshCw, Plus, Eye, Edit, Trash2, AlertCircle, Lock, Unlock, CheckCircle, XCircle, ArrowLeft } from 'lucide-react';
import { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ConfirmModal } from '@/components/ui/modal';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { SupplierFormModal } from '@/components/financeiro/supplier-form-modal';
import { SupplierDetailModal } from '@/components/financeiro/supplier-detail-modal';
import { useCreateSupplier, useUpdateSupplier, useDeleteSupplier, useBlockSupplier, useUnblockSupplier } from '@/hooks/financial/useSuppliers';
import { cn } from '@/lib/utils';
import { customInstance } from '@/lib/api-client';

type TabFilter = 'todos' | 'ativos' | 'bloqueados';

interface Supplier {
  id: string;
  name?: string;
  company_name?: string;
  trade_name?: string;
  cnpj?: string;
  cpf?: string;
  email?: string;
  category?: string;
  supplier_type?: string;
  status?: string;
  is_blocked?: boolean;
  is_qualified?: boolean;
  rating?: number;
  phone?: string;
  city?: string;
  state?: string;
}

const formatCnpj = (cnpj?: string) => {
  if (!cnpj) return '-';
  const n = cnpj.replace(/\D/g, '');
  if (n.length === 14) return n.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
  if (n.length === 11) return n.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  return cnpj;
};

const getStatusBadge = (supplier: Supplier) => {
  if (supplier.is_blocked) return <Badge variant="destructive">Bloqueado</Badge>;
  const s = (supplier.status || '').toLowerCase();
  if (s === 'ativo' || s === 'active') return <Badge className="bg-green-100 text-green-800">Ativo</Badge>;
  if (s === 'inativo' || s === 'inactive') return <Badge variant="secondary">Inativo</Badge>;
  return <Badge variant="outline">{supplier.status || 'N/D'}</Badge>;
};

const getSupplierDisplayName = (s: Supplier) =>
  s.trade_name || s.company_name || s.name || '(sem nome)';

export default function FornecedoresPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [tab, setTab] = useState<TabFilter>('todos');
  const [showFormModal, setShowFormModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Busca principal — sem condominio_id obrigatório
  const {
    data: suppliersRaw = [],
    isLoading,
    isError,
    refetch,
  } = useQuery<Supplier[]>({
    queryKey: ['suppliers', search, tab],
    queryFn: () =>
      customInstance<Supplier[]>({
        url: '/api/v1/financial/suppliers',
        params: {
          ...(search ? { search } : {}),
          ...(tab === 'ativos' ? { status: 'ativo' } : {}),
          ...(tab === 'bloqueados' ? { is_blocked: true } : {}),
          limit: 200,
        },
      }),
  });

  // Stats — retry: 0 para não travar a página se falhar
  const { data: statsRaw } = useQuery({
    queryKey: ['suppliers-stats'],
    queryFn: () =>
      customInstance<Record<string, number>>({
        url: '/api/v1/financial/suppliers/stats',
      }),
    retry: 0,
  });

  const suppliers = Array.isArray(suppliersRaw) ? suppliersRaw : [];

  // Fallback: calcula stats localmente se o endpoint falhar
  const stats = useMemo(() => {
    if (statsRaw && typeof statsRaw === 'object' && 'total' in statsRaw) return statsRaw;
    return {
      total: suppliers.length,
      ativos: suppliers.filter((s) => !s.is_blocked && (s.status || '').toLowerCase() !== 'inativo').length,
      bloqueados: suppliers.filter((s) => s.is_blocked).length,
      qualificados: suppliers.filter((s) => s.is_qualified).length,
    };
  }, [statsRaw, suppliers]);

  const filtered = useMemo(() => {
    if (!search) return suppliers;
    const q = search.toLowerCase();
    return suppliers.filter(
      (s) =>
        getSupplierDisplayName(s).toLowerCase().includes(q) ||
        (s.cnpj || '').includes(q) ||
        (s.email || '').toLowerCase().includes(q),
    );
  }, [suppliers, search]);

  const createSupplier = useCreateSupplier();
  const updateSupplier = useUpdateSupplier();
  const deleteSupplierMutation = useDeleteSupplier();
  const blockSupplier = useBlockSupplier();
  const unblockSupplier = useUnblockSupplier();

  const handleDelete = async () => {
    if (!selectedSupplier) return;
    setIsDeleting(true);
    try {
      await deleteSupplierMutation.mutateAsync(selectedSupplier.id);
      await queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      setShowDeleteModal(false);
      setSelectedSupplier(null);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleBlock = async (supplier: Supplier) => {
    await blockSupplier.mutateAsync({ supplierId: supplier.id, data: { reason: 'Bloqueado manualmente' } });
    await queryClient.invalidateQueries({ queryKey: ['suppliers'] });
  };

  const handleUnblock = async (supplier: Supplier) => {
    await unblockSupplier.mutateAsync(supplier.id);
    await queryClient.invalidateQueries({ queryKey: ['suppliers'] });
  };

  const tabs: { key: TabFilter; label: string; count: number }[] = [
    { key: 'todos', label: 'Todos', count: Number(stats.total ?? 0) },
    { key: 'ativos', label: 'Ativos', count: Number(stats.ativos ?? 0) },
    { key: 'bloqueados', label: 'Bloqueados', count: Number(stats.bloqueados ?? 0) },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/modulos/financeiro">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Users className="h-6 w-6 text-blue-600" />
              Fornecedores
            </h1>
            <p className="text-sm text-muted-foreground">Gerencie seus fornecedores</p>
          </div>
        </div>
        <Button onClick={() => { setSelectedSupplier(null); setShowFormModal(true); }}>
          <Plus className="h-4 w-4 mr-2" />
          Novo Fornecedor
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total', value: stats.total ?? 0, color: 'text-blue-600' },
          { label: 'Ativos', value: stats.ativos ?? 0, color: 'text-green-600' },
          { label: 'Bloqueados', value: stats.bloqueados ?? 0, color: 'text-red-600' },
          { label: 'Qualificados', value: stats.qualificados ?? 0, color: 'text-purple-600' },
        ].map((kpi) => (
          <Card key={kpi.label}>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">{kpi.label}</p>
              <p className={cn('text-2xl font-bold mt-1', kpi.color)}>{kpi.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filtros e busca */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex gap-2">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                'px-4 py-1.5 rounded-full text-sm font-medium transition-colors',
                tab === t.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80',
              )}
            >
              {t.label} ({t.count})
            </button>
          ))}
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nome, CNPJ ou e-mail..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button variant="outline" size="icon" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Tabela */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-40 text-muted-foreground">
              <RefreshCw className="h-5 w-5 animate-spin mr-2" />
              Carregando fornecedores...
            </div>
          ) : isError ? (
            <div className="flex items-center justify-center h-40 text-destructive gap-2">
              <AlertCircle className="h-5 w-5" />
              Erro ao carregar fornecedores
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
              <Users className="h-8 w-8 mb-2 opacity-30" />
              <p>Nenhum fornecedor encontrado</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/30">
                    <th className="text-left px-4 py-3 font-medium">Nome / Razão Social</th>
                    <th className="text-left px-4 py-3 font-medium">CNPJ / CPF</th>
                    <th className="text-left px-4 py-3 font-medium hidden md:table-cell">E-mail</th>
                    <th className="text-left px-4 py-3 font-medium hidden lg:table-cell">Categoria</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-left px-4 py-3 font-medium hidden lg:table-cell">Rating</th>
                    <th className="text-right px-4 py-3 font-medium">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((supplier) => (
                    <tr key={supplier.id} className="border-b hover:bg-muted/20 transition-colors">
                      <td className="px-4 py-3 font-medium">
                        <div>{getSupplierDisplayName(supplier)}</div>
                        {supplier.trade_name && supplier.company_name && (
                          <div className="text-xs text-muted-foreground">{supplier.company_name}</div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground font-mono text-xs">
                        {formatCnpj(supplier.cnpj || supplier.cpf)}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">
                        {supplier.email || '-'}
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <Badge variant="outline" className="text-xs">
                          {supplier.category || supplier.supplier_type || 'Geral'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">{getStatusBadge(supplier)}</td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        {supplier.rating ? (
                          <span className="text-yellow-600 font-medium">
                            {'★'.repeat(Math.round(supplier.rating))}{'☆'.repeat(5 - Math.round(supplier.rating))}
                          </span>
                        ) : (
                          <span className="text-muted-foreground text-xs">N/A</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-7 w-7">
                              <span className="sr-only">Ações</span>
                              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                                <circle cx="12" cy="5" r="1.5" /><circle cx="12" cy="12" r="1.5" /><circle cx="12" cy="19" r="1.5" />
                              </svg>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => { setSelectedSupplier(supplier); setShowDetailModal(true); }}>
                              <Eye className="h-4 w-4 mr-2" /> Visualizar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => { setSelectedSupplier(supplier); setShowFormModal(true); }}>
                              <Edit className="h-4 w-4 mr-2" /> Editar
                            </DropdownMenuItem>
                            {supplier.is_blocked ? (
                              <DropdownMenuItem onClick={() => handleUnblock(supplier)}>
                                <Unlock className="h-4 w-4 mr-2" /> Desbloquear
                              </DropdownMenuItem>
                            ) : (
                              <DropdownMenuItem onClick={() => handleBlock(supplier)}>
                                <Lock className="h-4 w-4 mr-2" /> Bloquear
                              </DropdownMenuItem>
                            )}
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => { setSelectedSupplier(supplier); setShowDeleteModal(true); }}
                            >
                              <Trash2 className="h-4 w-4 mr-2" /> Excluir
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
        </CardContent>
      </Card>

      {/* Modais */}
      {showFormModal && (
        <SupplierFormModal
          open={showFormModal}
          onClose={() => { setShowFormModal(false); setSelectedSupplier(null); }}
          supplier={selectedSupplier as Parameters<typeof SupplierFormModal>[0]['supplier']}
          onSuccess={async () => {
            await queryClient.invalidateQueries({ queryKey: ['suppliers'] });
            setShowFormModal(false);
            setSelectedSupplier(null);
          }}
        />
      )}

      {showDetailModal && selectedSupplier && (
        <SupplierDetailModal
          open={showDetailModal}
          onClose={() => { setShowDetailModal(false); setSelectedSupplier(null); }}
          supplierId={selectedSupplier.id}
        />
      )}

      <ConfirmModal
        open={showDeleteModal}
        onClose={() => { setShowDeleteModal(false); setSelectedSupplier(null); }}
        onConfirm={handleDelete}
        title="Excluir fornecedor"
        description={`Tem certeza que deseja excluir "${selectedSupplier ? getSupplierDisplayName(selectedSupplier) : ''}"? Esta ação não pode ser desfeita.`}
        isLoading={isDeleting}
      />
    </div>
  );
}
