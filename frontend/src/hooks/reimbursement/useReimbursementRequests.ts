/**
 * React Query Hooks - Reimbursement Requests
 *
 * Hooks customizados para gerenciamento de solicitações de reembolso
 * Inclui cache, invalidação automática e otimização de queries
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { reimbursementRequestService } from '@/services/reimbursement';
import type {
  ReimbursementRequestCreate,
  ReimbursementRequestUpdate,
  ReimbursementRequestResponse,
  PaginatedReimbursementResponse,
  ReimbursementRequestStats,
} from '@/types/generated/reimbursement/models';

// Query Keys
export const reimbursementKeys = {
  all: ['reimbursements'] as const,
  lists: () => [...reimbursementKeys.all, 'list'] as const,
  list: (filters?: object) => [...reimbursementKeys.lists(), filters] as const,
  myLists: () => [...reimbursementKeys.all, 'my'] as const,
  myList: (filters?: object) => [...reimbursementKeys.myLists(), filters] as const,
  details: () => [...reimbursementKeys.all, 'detail'] as const,
  detail: (id: string) => [...reimbursementKeys.details(), id] as const,
  stats: (myOnly?: boolean) => [...reimbursementKeys.all, 'stats', myOnly] as const,
  categories: () => [...reimbursementKeys.all, 'categories'] as const,
  expenseTypes: () => [...reimbursementKeys.all, 'expense-types'] as const,
  attachmentTypes: () => [...reimbursementKeys.all, 'attachment-types'] as const,
};

/**
 * Lista solicitações de reembolso com filtros
 */
export function useReimbursementRequests(
  params?: Parameters<typeof reimbursementRequestService.list>[0],
  options?: Omit<UseQueryOptions<PaginatedReimbursementResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reimbursementKeys.list(params),
    queryFn: () => reimbursementRequestService.list(params),
    ...options,
  });
}

/**
 * Lista solicitações do usuário autenticado
 */
export function useMyReimbursementRequests(
  params?: Parameters<typeof reimbursementRequestService.listMy>[0],
  options?: Omit<UseQueryOptions<PaginatedReimbursementResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reimbursementKeys.myList(params),
    queryFn: () => reimbursementRequestService.listMy(params),
    ...options,
  });
}

/**
 * Busca solicitação por ID
 */
export function useReimbursementRequest(
  requestId: string,
  options?: Omit<UseQueryOptions<ReimbursementRequestResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reimbursementKeys.detail(requestId),
    queryFn: () => reimbursementRequestService.getById(requestId),
    enabled: !!requestId,
    ...options,
  });
}

/**
 * Estatísticas de reembolsos
 */
export function useReimbursementStats(
  myOnly: boolean = false,
  options?: Omit<UseQueryOptions<ReimbursementRequestStats>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reimbursementKeys.stats(myOnly),
    queryFn: () => reimbursementRequestService.getStats(myOnly),
    ...options,
  });
}

/**
 * Categorias de despesa
 */
export function useExpenseCategories(
  options?: Omit<UseQueryOptions<Array<{ code: string; name: string }>>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reimbursementKeys.categories(),
    queryFn: () => reimbursementRequestService.getCategories(),
    staleTime: 1000 * 60 * 30, // 30 minutos
    ...options,
  });
}

/**
 * Tipos de despesa (enum)
 */
export function useExpenseTypes(
  options?: Omit<UseQueryOptions<Array<{ value: string; label: string }>>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reimbursementKeys.expenseTypes(),
    queryFn: () => reimbursementRequestService.getExpenseTypes(),
    staleTime: Infinity, // Enum não muda
    ...options,
  });
}

/**
 * Tipos de anexo (enum)
 */
export function useAttachmentTypes(
  options?: Omit<UseQueryOptions<Array<{ value: string; label: string }>>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: reimbursementKeys.attachmentTypes(),
    queryFn: () => reimbursementRequestService.getAttachmentTypes(),
    staleTime: Infinity, // Enum não muda
    ...options,
  });
}

/**
 * Cria nova solicitação de reembolso
 */
export function useCreateReimbursementRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReimbursementRequestCreate) =>
      reimbursementRequestService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.stats() });
    },
  });
}

/**
 * Atualiza solicitação de reembolso
 */
export function useUpdateReimbursementRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, data }: { requestId: string; data: ReimbursementRequestUpdate }) =>
      reimbursementRequestService.update(requestId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
    },
  });
}

/**
 * Exclui solicitação de reembolso
 */
export function useDeleteReimbursementRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (requestId: string) => reimbursementRequestService.delete(requestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.stats() });
    },
  });
}

/**
 * Submete solicitação para aprovação
 */
export function useSubmitReimbursementRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, notes }: { requestId: string; notes?: string }) =>
      reimbursementRequestService.submit(requestId, notes),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.stats() });
    },
  });
}

/**
 * Cancela solicitação
 */
export function useCancelReimbursementRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, reason }: { requestId: string; reason?: string }) =>
      reimbursementRequestService.cancel(requestId, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.detail(variables.requestId) });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.myLists() });
      queryClient.invalidateQueries({ queryKey: reimbursementKeys.stats() });
    },
  });
}
