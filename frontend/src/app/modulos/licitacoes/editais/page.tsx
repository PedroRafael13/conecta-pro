'use client';

/**
 * Página de Lista de Editais
 * Gestão completa de editais de licitação
 */

import {
  FileText,
  Plus,
  RefreshCw,
  Search,
  Eye,
  Edit2,
  Trash2,
  Download,
  FileCheck,
  Calendar,
  DollarSign,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  CloudDownload,
  Database,
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ConfirmModal } from '@/components/ui/modal';
import {
  useListarEditais,
  useRemoverEdital,
  useMarcarParticipacao,
  useAlterarStatusEdital,
  useSincronizarPNCP,
  useBuscarPNCPMutation,
} from '@/hooks/bidding/useTenders';
import { TenderStatusBadge } from '@/components/licitacoes/TenderStatusBadge';
import { ModalityBadge } from '@/components/licitacoes/ModalityBadge';
import { TenderFilters } from '@/components/licitacoes/TenderFilters';
import { TenderFormModal } from '@/components/licitacoes/TenderFormModal';
import type { TenderResponse } from '@/types/generated/bidding';

export default function EditaisPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [filters, setFilters] = useState<any>({});
  const [selectedTender, setSelectedTender] = useState<TenderResponse | null>(null);
  const [showFormModal, setShowFormModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editTender, setEditTender] = useState<TenderResponse | null>(null);

  const { data, isLoading, refetch } = useListarEditais({
    ...filters,
    page,
    size: pageSize,
  });

  const removerMutation = useRemoverEdital();
  const marcarParticipacaoMutation = useMarcarParticipacao();
  const alterarStatusMutation = useAlterarStatusEdital();
  const sincronizarMutation = useSincronizarPNCP();
  const buscarPNCPMutation = useBuscarPNCPMutation();

  const tenders = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  const handleRefresh = () => {
    refetch();
  };

  const handleNew = () => {
    setEditTender(null);
    setShowFormModal(true);
  };

  const handleEdit = (tender: TenderResponse) => {
    setEditTender(tender);
    setShowFormModal(true);
  };

  const handleView = (tenderId: string) => {
    router.push(`/modulos/licitacoes/editais/${tenderId}`);
  };

  const handleDelete = async () => {
    if (!selectedTender) return;
    await removerMutation.mutateAsync(selectedTender.id);
    setShowDeleteModal(false);
    setSelectedTender(null);
    // handleRefresh() removido - mutation já invalida queries automaticamente
  };

  const confirmDelete = (tender: TenderResponse) => {
    setSelectedTender(tender);
    setShowDeleteModal(true);
  };

  const handleMarcarParticipacao = async (tender: TenderResponse) => {
    await marcarParticipacaoMutation.mutateAsync({
      tender_id: tender.id,
      participando: true,
      interesse: true,
    });
    // handleRefresh() removido - mutation já invalida queries automaticamente
  };

  const handleAlterarStatus = async (tender: TenderResponse, novoStatus: string) => {
    await alterarStatusMutation.mutateAsync({
      tender_id: tender.id,
      novo_status: novoStatus,
    });
    // handleRefresh() removido - mutation já invalida queries automaticamente
  };

  const handleSincronizarPNCP = async () => {
    await sincronizarMutation.mutateAsync({
      dias_retroativos: 30,
    });
    // handleRefresh() removido - mutation já invalida queries automaticamente
  };

  const handleBuscarPNCP = async () => {
    await buscarPNCPMutation.mutateAsync({
      uf: filters.uf,
      segmento: filters.segmento,
    });
    // handleRefresh() removido - mutation já invalida queries automaticamente
  };

  const formatCurrency = (value?: number) => {
    if (!value) return '-';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const clearFilters = () => {
    setFilters({});
    setPage(1);
  };

  return (
    <div className="min-h-screen bg-grid">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[hsl(var(--background))]/80 backdrop-blur-xl border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/modulos">
                <Button variant="ghost" size="sm">
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Módulos
                </Button>
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    Editais de Licitação
                  </h1>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    {total} registros
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleBuscarPNCP}
                disabled={buscarPNCPMutation.isPending}
              >
                <Search className="w-4 h-4 mr-2" />
                Buscar PNCP
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleSincronizarPNCP}
                disabled={sincronizarMutation.isPending}
              >
                <Database className="w-4 h-4 mr-2" />
                Sincronizar
              </Button>
              <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
                <RefreshCw
                  className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`}
                />
                Atualizar
              </Button>
              <Button variant="primary" onClick={handleNew}>
                <Plus className="w-4 h-4 mr-2" />
                Novo Edital
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filtros */}
        <div className="mb-6">
          <TenderFilters
            filters={filters}
            onFilterChange={setFilters}
            onClearFilters={clearFilters}
          />
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-pulse-slow text-[hsl(var(--primary))]">
              <FileText className="w-8 h-8" />
            </div>
          </div>
        )}

        {/* Table */}
        {!isLoading && (
          <>
            <div className="bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]">
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Número
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Órgão
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Modalidade
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Objeto
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Valor
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Data Abertura
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Status
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase">
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[hsl(var(--border))]">
                    {tenders.map((tender) => (
                      <tr
                        key={tender.id}
                        className="hover:bg-[hsl(var(--muted))]/50 transition-colors cursor-pointer"
                        onClick={() => handleView(tender.id)}
                      >
                        <td className="px-4 py-3">
                          <span className="text-sm font-mono text-[hsl(var(--foreground))]">
                            {(tender as any).number || tender.id.slice(0, 8)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div>
                            <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                              {(tender as any).entity || 'N/A'}
                            </p>
                            {(tender as any).uf && (
                              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                                {(tender as any).uf} - {(tender as any).city}
                              </p>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <ModalityBadge modality={tender.modality} />
                        </td>
                        <td className="px-4 py-3 max-w-xs">
                          <p className="text-sm text-[hsl(var(--foreground))] truncate">
                            {tender.title}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm font-medium text-[hsl(var(--foreground))]">
                            {formatCurrency(tender.estimated_value)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1 text-sm text-[hsl(var(--foreground))]">
                            <Calendar className="w-3 h-3 text-[hsl(var(--muted-foreground))]" />
                            {formatDate(tender.opening_date)}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <TenderStatusBadge status={tender.status} />
                        </td>
                        <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleView(tender.id)}
                              title="Ver Detalhes"
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleMarcarParticipacao(tender)}
                              title="Marcar Participação"
                              className="text-blue-500 hover:text-blue-600"
                            >
                              <FileCheck className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEdit(tender)}
                              title="Editar"
                            >
                              <Edit2 className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => confirmDelete(tender)}
                              className="text-red-500 hover:text-red-600"
                              title="Excluir"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Empty state */}
            {tenders.length === 0 && !isLoading && (
              <div className="text-center py-12 bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl mt-4">
                <FileText className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                <h3 className="text-lg font-medium text-[hsl(var(--foreground))]">
                  Nenhum edital encontrado
                </h3>
                <p className="text-[hsl(var(--muted-foreground))] mt-1">
                  Ajuste os filtros ou cadastre um novo edital
                </p>
                <Button variant="primary" className="mt-4" onClick={handleNew}>
                  <Plus className="w-4 h-4 mr-2" />
                  Novo Edital
                </Button>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  Mostrando {(page - 1) * pageSize + 1} a{' '}
                  {Math.min(page * pageSize, total)} de {total} registros
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-sm text-[hsl(var(--foreground))]">
                    Página {page} de {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page >= totalPages}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Form Modal */}
      <TenderFormModal
        isOpen={showFormModal}
        onClose={() => {
          setShowFormModal(false);
          setEditTender(null);
        }}
        onSuccess={() => {
          // TenderFormModal já invalida queries via mutations
          // Não precisa chamar handleRefresh() aqui
        }}
        editData={editTender}
      />

      {/* Delete Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedTender(null);
        }}
        onConfirm={handleDelete}
        title="Excluir Edital"
        message={`Tem certeza que deseja excluir o edital ${
          (selectedTender as any)?.number || selectedTender?.id
        }? Esta ação não pode ser desfeita.`}
        confirmText="Excluir"
        isLoading={removerMutation.isPending}
        variant="danger"
      />
    </div>
  );
}
