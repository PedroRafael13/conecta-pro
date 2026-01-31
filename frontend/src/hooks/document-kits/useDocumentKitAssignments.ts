/**
 * React Query Hooks - Document Kit Assignments
 *
 * Hooks customizados para gerenciamento de atribuições de kits.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  documentKitAssignmentService,
  type ListAssignmentsParams,
  type RejectAssignmentParams,
} from '@/services/document-kits/documentKitAssignmentService';
import type {
  DocumentKitAssignmentCreate,
  DocumentKitAssignmentUpdate,
} from '@/types/generated/document-kits';

// Query Keys
export const documentKitAssignmentKeys = {
  all: ['document-kit-assignments'] as const,
  lists: () => [...documentKitAssignmentKeys.all, 'list'] as const,
  list: (params: ListAssignmentsParams) =>
    [...documentKitAssignmentKeys.lists(), params] as const,
  pending: (condominio_id: string) =>
    [...documentKitAssignmentKeys.all, 'pending', condominio_id] as const,
  overdue: (condominio_id: string) =>
    [...documentKitAssignmentKeys.all, 'overdue', condominio_id] as const,
  details: () => [...documentKitAssignmentKeys.all, 'detail'] as const,
  detail: (assignment_id: string, condominio_id: string) =>
    [
      ...documentKitAssignmentKeys.details(),
      assignment_id,
      condominio_id,
    ] as const,
};

/**
 * Hook para listar atribuições
 */
export function useListAssignments(params: ListAssignmentsParams) {
  return useQuery({
    queryKey: documentKitAssignmentKeys.list(params),
    queryFn: () => documentKitAssignmentService.listAssignments(params),
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
}

/**
 * Hook para listar atribuições pendentes
 */
export function usePendingAssignments(condominio_id: string) {
  return useQuery({
    queryKey: documentKitAssignmentKeys.pending(condominio_id),
    queryFn: () =>
      documentKitAssignmentService.listPendingAssignments(condominio_id),
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
}

/**
 * Hook para listar atribuições vencidas
 */
export function useOverdueAssignments(condominio_id: string) {
  return useQuery({
    queryKey: documentKitAssignmentKeys.overdue(condominio_id),
    queryFn: () =>
      documentKitAssignmentService.listOverdueAssignments(condominio_id),
    staleTime: 1 * 60 * 1000, // 1 minuto
  });
}

/**
 * Hook para buscar uma atribuição por ID
 */
export function useAssignment(assignment_id: string, condominio_id: string) {
  return useQuery({
    queryKey: documentKitAssignmentKeys.detail(assignment_id, condominio_id),
    queryFn: () =>
      documentKitAssignmentService.getAssignment(assignment_id, condominio_id),
    enabled: !!assignment_id && !!condominio_id,
  });
}

/**
 * Hook para criar atribuição
 */
export function useAssignKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DocumentKitAssignmentCreate) =>
      documentKitAssignmentService.assignKit(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      toast.success('Kit atribuído com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao atribuir kit: ${error.message}`);
    },
  });
}

/**
 * Hook para atualizar atribuição
 */
export function useUpdateAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assignment_id,
      data,
      condominio_id,
    }: {
      assignment_id: string;
      data: DocumentKitAssignmentUpdate;
      condominio_id: string;
    }) =>
      documentKitAssignmentService.updateAssignment(
        assignment_id,
        data,
        condominio_id
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.detail(
          variables.assignment_id,
          variables.condominio_id
        ),
      });
      toast.success('Atribuição atualizada com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao atualizar atribuição: ${error.message}`);
    },
  });
}

/**
 * Hook para iniciar atribuição
 */
export function useStartAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assignment_id,
      condominio_id,
    }: {
      assignment_id: string;
      condominio_id: string;
    }) =>
      documentKitAssignmentService.startAssignment(
        assignment_id,
        condominio_id
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.detail(
          variables.assignment_id,
          variables.condominio_id
        ),
      });
      toast.success('Atribuição iniciada com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao iniciar atribuição: ${error.message}`);
    },
  });
}

/**
 * Hook para aprovar atribuição
 */
export function useApproveAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assignment_id,
      condominio_id,
    }: {
      assignment_id: string;
      condominio_id: string;
    }) =>
      documentKitAssignmentService.approveAssignment(
        assignment_id,
        condominio_id
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.detail(
          variables.assignment_id,
          variables.condominio_id
        ),
      });
      toast.success('Atribuição aprovada com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao aprovar atribuição: ${error.message}`);
    },
  });
}

/**
 * Hook para rejeitar atribuição
 */
export function useRejectAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: RejectAssignmentParams) =>
      documentKitAssignmentService.rejectAssignment(params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.detail(
          variables.assignment_id,
          variables.condominio_id
        ),
      });
      toast.success('Atribuição reprovada!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao reprovar atribuição: ${error.message}`);
    },
  });
}

/**
 * Hook para completar atribuição
 */
export function useCompleteAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assignment_id,
      condominio_id,
    }: {
      assignment_id: string;
      condominio_id: string;
    }) =>
      documentKitAssignmentService.completeAssignment(
        assignment_id,
        condominio_id
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.detail(
          variables.assignment_id,
          variables.condominio_id
        ),
      });
      toast.success('Atribuição completada com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao completar atribuição: ${error.message}`);
    },
  });
}

/**
 * Hook para cancelar atribuição
 */
export function useCancelAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assignment_id,
      condominio_id,
    }: {
      assignment_id: string;
      condominio_id: string;
    }) =>
      documentKitAssignmentService.cancelAssignment(
        assignment_id,
        condominio_id
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.detail(
          variables.assignment_id,
          variables.condominio_id
        ),
      });
      toast.success('Atribuição cancelada com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao cancelar atribuição: ${error.message}`);
    },
  });
}

/**
 * Hook para enviar notificação
 */
export function useNotifyAssignment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      assignment_id,
      condominio_id,
    }: {
      assignment_id: string;
      condominio_id: string;
    }) =>
      documentKitAssignmentService.notifyAssignment(
        assignment_id,
        condominio_id
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: documentKitAssignmentKeys.detail(
          variables.assignment_id,
          variables.condominio_id
        ),
      });
      toast.success('Notificação enviada com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao enviar notificação: ${error.message}`);
    },
  });
}
