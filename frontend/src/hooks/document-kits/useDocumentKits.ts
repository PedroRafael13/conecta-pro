/**
 * React Query Hooks - Document Kits
 *
 * Hooks customizados para gerenciamento de kits documentais.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  documentKitService,
  type ListKitsParams,
  type DuplicateKitParams,
} from '@/services/document-kits/documentKitService';
import type {
  DocumentKitCreate,
  DocumentKitUpdate,
} from '@/types/generated/document-kits';

// Query Keys
export const documentKitKeys = {
  all: ['document-kits'] as const,
  lists: () => [...documentKitKeys.all, 'list'] as const,
  list: (params: ListKitsParams) =>
    [...documentKitKeys.lists(), params] as const,
  details: () => [...documentKitKeys.all, 'detail'] as const,
  detail: (id: string, condominio_id: string) =>
    [...documentKitKeys.details(), id, condominio_id] as const,
  stats: (condominio_id: string) =>
    [...documentKitKeys.all, 'stats', condominio_id] as const,
  templates: (condominio_id: string) =>
    [...documentKitKeys.all, 'templates', condominio_id] as const,
};

/**
 * Hook para listar kits documentais
 */
export function useListKits(params: ListKitsParams) {
  return useQuery({
    queryKey: documentKitKeys.list(params),
    queryFn: () => documentKitService.listKits(params),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para buscar estatísticas de kits
 */
export function useKitStats(condominio_id: string) {
  return useQuery({
    queryKey: documentKitKeys.stats(condominio_id),
    queryFn: () => documentKitService.getStats(condominio_id),
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
}

/**
 * Hook para listar templates de kits
 */
export function useKitTemplates(condominio_id: string, tipo?: string) {
  return useQuery({
    queryKey: documentKitKeys.templates(condominio_id),
    queryFn: () => documentKitService.listTemplates(condominio_id, tipo as any),
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para buscar um kit por ID
 */
export function useKit(kit_id: string, condominio_id: string) {
  return useQuery({
    queryKey: documentKitKeys.detail(kit_id, condominio_id),
    queryFn: () => documentKitService.getKit(kit_id, condominio_id),
    enabled: !!kit_id && !!condominio_id,
  });
}

/**
 * Hook para criar kit
 */
export function useCreateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DocumentKitCreate) =>
      documentKitService.createKit(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKitKeys.lists() });
      toast.success('Kit criado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao criar kit: ${error.message}`);
    },
  });
}

/**
 * Hook para atualizar kit
 */
export function useUpdateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kit_id,
      data,
      condominio_id,
    }: {
      kit_id: string;
      data: DocumentKitUpdate;
      condominio_id: string;
    }) => documentKitService.updateKit(kit_id, data, condominio_id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: documentKitKeys.detail(
          variables.kit_id,
          variables.condominio_id
        ),
      });
      toast.success('Kit atualizado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao atualizar kit: ${error.message}`);
    },
  });
}

/**
 * Hook para deletar kit
 */
export function useDeleteKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kit_id,
      condominio_id,
    }: {
      kit_id: string;
      condominio_id: string;
    }) => documentKitService.deleteKit(kit_id, condominio_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKitKeys.lists() });
      toast.success('Kit removido com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao remover kit: ${error.message}`);
    },
  });
}

/**
 * Hook para ativar kit
 */
export function useActivateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kit_id,
      condominio_id,
    }: {
      kit_id: string;
      condominio_id: string;
    }) => documentKitService.activateKit(kit_id, condominio_id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: documentKitKeys.detail(
          variables.kit_id,
          variables.condominio_id
        ),
      });
      toast.success('Kit ativado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao ativar kit: ${error.message}`);
    },
  });
}

/**
 * Hook para desativar kit
 */
export function useDeactivateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kit_id,
      condominio_id,
    }: {
      kit_id: string;
      condominio_id: string;
    }) => documentKitService.deactivateKit(kit_id, condominio_id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: documentKitKeys.detail(
          variables.kit_id,
          variables.condominio_id
        ),
      });
      toast.success('Kit desativado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao desativar kit: ${error.message}`);
    },
  });
}

/**
 * Hook para arquivar kit
 */
export function useArchiveKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      kit_id,
      condominio_id,
    }: {
      kit_id: string;
      condominio_id: string;
    }) => documentKitService.archiveKit(kit_id, condominio_id),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: documentKitKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: documentKitKeys.detail(
          variables.kit_id,
          variables.condominio_id
        ),
      });
      toast.success('Kit arquivado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao arquivar kit: ${error.message}`);
    },
  });
}

/**
 * Hook para duplicar kit
 */
export function useDuplicateKit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: DuplicateKitParams) =>
      documentKitService.duplicateKit(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKitKeys.lists() });
      toast.success('Kit duplicado com sucesso!');
    },
    onError: (error: Error) => {
      toast.error(`Erro ao duplicar kit: ${error.message}`);
    },
  });
}
