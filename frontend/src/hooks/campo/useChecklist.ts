/**
 * React Query Hooks - Checklists (CAMPO)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { checklistService } from '@/services/campo';
import type {
  ChecklistTemplateCreate,
  ChecklistItemCreate,
  ChecklistItemUpdate,
  ChecklistPreenchidoCompleto,
} from '@/api/campo/generated/models';
import type { ChecklistPreenchimento } from '@/services/campo/types';

const QUERY_KEYS = {
  all: ['campo', 'checklists'] as const,
  templates: () => [...QUERY_KEYS.all, 'templates'] as const,
  template: (id: string) => [...QUERY_KEYS.templates(), id] as const,
  item: (id: string) => [...QUERY_KEYS.all, 'item', id] as const,
  porOS: (osId: string) => [...QUERY_KEYS.all, 'os', osId] as const,
  porVisita: (visitaId: string) => [...QUERY_KEYS.all, 'visita', visitaId] as const,
};

export const useTemplates = (params?: any) => {
  return useQuery({
    queryKey: [QUERY_KEYS.templates(), params],
    queryFn: () => checklistService.listarTemplates(params),
  });
};

export const useTemplate = (templateId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.template(templateId),
    queryFn: () => checklistService.buscarTemplate(templateId),
    enabled: !!templateId,
  });
};

export const useCriarTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ChecklistTemplateCreate) => checklistService.criarTemplate(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.templates() }),
  });
};

export const useAtualizarTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ templateId, data }: { templateId: string; data: Partial<ChecklistTemplateCreate> }) =>
      checklistService.atualizarTemplate(templateId, data),
    onSuccess: (_, { templateId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.template(templateId) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.templates() });
    },
  });
};

export const useDeletarTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (templateId: string) => checklistService.deletarTemplate(templateId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.templates() }),
  });
};

export const useChecklistPorOS = (ordemServicoId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.porOS(ordemServicoId),
    queryFn: () => checklistService.buscarPorOS(ordemServicoId),
    enabled: !!ordemServicoId,
  });
};

export const useChecklistPorVisita = (visitaId: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.porVisita(visitaId),
    queryFn: () => checklistService.buscarPorVisita(visitaId),
    enabled: !!visitaId,
  });
};

export const usePreencherItem = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ itemId, data }: { itemId: string; data: ChecklistPreenchidoCompleto }) =>
      checklistService.preencherItem(itemId, data),
    onSuccess: (_, { itemId }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.item(itemId) });
    },
  });
};

export const useValidarChecklist = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (checklistId: string) => checklistService.validarChecklist(checklistId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: QUERY_KEYS.all }),
  });
};
