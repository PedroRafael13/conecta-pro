/**
 * useTemplates Hook
 *
 * Hook para gerenciamento de templates de notificação
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { templateService } from '@/services/notifications';
import type {
  TemplateCreate,
  TemplateUpdate,
  TemplateResponse,
} from '@/types/generated/notifications';

// Query Keys
export const templateKeys = {
  all: ['notification-templates'] as const,
  lists: () => [...templateKeys.all, 'list'] as const,
  list: (filters: string) => [...templateKeys.lists(), { filters }] as const,
  details: () => [...templateKeys.all, 'detail'] as const,
  detail: (id: string) => [...templateKeys.details(), id] as const,
  bySlug: (slug: string) => [...templateKeys.all, 'slug', slug] as const,
  byCategory: (category: string) => [...templateKeys.all, 'category', category] as const,
};

/**
 * Hook para listar templates
 */
export function useTemplates(params?: {
  category?: string;
  template_status?: string;
  active?: boolean;
  skip?: number;
  limit?: number;
}) {
  const filters = JSON.stringify(params);

  return useQuery({
    queryKey: templateKeys.list(filters),
    queryFn: () => templateService.list(params),
    staleTime: 300000, // 5 minutos
  });
}

/**
 * Hook para obter template específico
 */
export function useTemplate(templateId: string) {
  return useQuery({
    queryKey: templateKeys.detail(templateId),
    queryFn: () => templateService.get(templateId),
    enabled: !!templateId,
    staleTime: 300000,
  });
}

/**
 * Hook para buscar template por slug
 */
export function useTemplateBySlug(slug: string) {
  return useQuery({
    queryKey: templateKeys.bySlug(slug),
    queryFn: () => templateService.getBySlug(slug),
    enabled: !!slug,
    staleTime: 300000,
  });
}

/**
 * Hook para templates por categoria
 */
export function useTemplatesByCategory(category: string) {
  return useQuery({
    queryKey: templateKeys.byCategory(category),
    queryFn: () => templateService.listByCategory(category),
    enabled: !!category,
    staleTime: 300000,
  });
}

/**
 * Hook para criar template
 */
export function useCreateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TemplateCreate) => templateService.create(data),
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
    mutationFn: ({ templateId, data }: { templateId: string; data: TemplateUpdate }) =>
      templateService.update(templateId, data),
    onSuccess: (_, { templateId }) => {
      queryClient.invalidateQueries({ queryKey: templateKeys.detail(templateId) });
      queryClient.invalidateQueries({ queryKey: templateKeys.lists() });
    },
  });
}

/**
 * Hook para validar variáveis do template
 */
export function useValidateTemplateVariables() {
  return (template: TemplateResponse, variables: Record<string, unknown>) => {
    return templateService.validateVariables(template, variables);
  };
}

/**
 * Hook para renderizar template
 */
export function useRenderTemplate() {
  return (content: string, variables: Record<string, unknown>) => {
    return templateService.renderTemplate(content, variables);
  };
}
