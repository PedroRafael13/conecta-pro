/**
 * Hooks React Query - Contract Templates
 * Gestão de Templates de Contrato
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractTemplateService } from '@/services/contracts';
import type {
  ContractTemplateCreate,
  ContractTemplateUpdate,
  ContractTemplateResponse,
  ContractTemplateListResponse,
} from '@/types/generated/contracts/cRMContractsAPI.schemas';

/**
 * Query keys para templates
 */
export const templateKeys = {
  all: ['contract-templates'] as const,
  lists: () => [...templateKeys.all, 'list'] as const,
  list: (filters?: any) => [...templateKeys.lists(), filters] as const,
  details: () => [...templateKeys.all, 'detail'] as const,
  detail: (id: string) => [...templateKeys.details(), id] as const,
};

/**
 * Hook para listar templates
 */
export function useContractTemplates(params?: {
  service_type?: string;
  approved_only?: boolean;
}) {
  return useQuery({
    queryKey: templateKeys.list(params),
    queryFn: () => contractTemplateService.list(params),
  });
}

/**
 * Hook para obter template por ID
 */
export function useContractTemplate(templateId: string, enabled = true) {
  return useQuery({
    queryKey: templateKeys.detail(templateId),
    queryFn: () => contractTemplateService.getById(templateId),
    enabled: enabled && !!templateId,
  });
}

/**
 * Hook para criar template
 */
export function useCreateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ContractTemplateCreate) =>
      contractTemplateService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
  });
}

/**
 * Hook para atualizar template
 */
export function useUpdateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      templateId,
      data,
    }: {
      templateId: string;
      data: ContractTemplateUpdate;
    }) => contractTemplateService.update(templateId, data),
    onSuccess: (_, { templateId }) => {
      queryClient.invalidateQueries({ queryKey: templateKeys.detail(templateId) });
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
  });
}

/**
 * Hook para aprovar template
 */
export function useApproveTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (templateId: string) => contractTemplateService.approve(templateId),
    onSuccess: (_, templateId) => {
      queryClient.invalidateQueries({ queryKey: templateKeys.detail(templateId) });
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
  });
}

/**
 * Hook para deletar template
 */
export function useDeleteTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (templateId: string) => contractTemplateService.delete(templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
  });
}
