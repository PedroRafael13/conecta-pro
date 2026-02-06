/**
 * Hook: useDiarists
 *
 * Gerenciamento de diaristas (CRUD e consultas).
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { diaristCoreService } from '@/services/diarists';
import type {
  DiaristStatus,
  DiaristType,
  DiaristCreate,
  DiaristUpdate,
} from '@/api/diarists/generated/models';

/**
 * Hook para listar diaristas
 */
export function useListDiarists(params?: {
  skip?: number;
  limit?: number;
  status?: DiaristStatus;
  tipo?: DiaristType;
  search?: string;
}) {
  return useQuery({
    queryKey: ['diarists', 'list', params],
    queryFn: () => diaristCoreService.listDiarists(params),
  });
}

/**
 * Hook para buscar diarista por ID
 */
export function useDiarist(diaristId: string) {
  return useQuery({
    queryKey: ['diarists', 'detail', diaristId],
    queryFn: () => diaristCoreService.getDiarist(diaristId),
    enabled: !!diaristId,
  });
}

/**
 * Hook para buscar diaristas disponíveis
 */
export function useAvailableDiarists(data: string, tipo?: DiaristType) {
  return useQuery({
    queryKey: ['diarists', 'available', data, tipo],
    queryFn: () => diaristCoreService.getAvailableDiarists({ data, tipo }),
    enabled: !!data,
  });
}

/**
 * Hook para consultar CPF
 */
export function useConsultaCpf() {
  return useMutation({
    mutationFn: (cpf: string) => diaristCoreService.consultaCpf(cpf),
  });
}

/**
 * Hook para métricas de diarista
 */
export function useDiaristMetrics(
  diaristId: string,
  params?: {
    dataInicio?: string;
    dataFim?: string;
  }
) {
  return useQuery({
    queryKey: ['diarists', 'metrics', diaristId, params],
    queryFn: () => diaristCoreService.getDiaristMetrics(diaristId, params),
    enabled: !!diaristId,
  });
}
