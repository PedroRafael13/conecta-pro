/**
 * Hook: useSchedules
 *
 * Gerenciamento de agendamentos de diaristas.
 */

import { useQuery } from '@tanstack/react-query';
import { diaristCoreService } from '@/services/diarists';
import type { ScheduleStatus } from '@/api/diarists/generated/models';

/**
 * Hook para listar agendamentos
 */
export function useListSchedules(params?: {
  diaristId?: string;
  dataInicio?: string;
  dataFim?: string;
  status?: ScheduleStatus;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['diarists', 'schedules', 'list', params],
    queryFn: () => diaristCoreService.listSchedules(params),
  });
}

/**
 * Hook para buscar agendamento por ID
 */
export function useSchedule(scheduleId: string) {
  return useQuery({
    queryKey: ['diarists', 'schedules', 'detail', scheduleId],
    queryFn: () => diaristCoreService.getSchedule(scheduleId),
    enabled: !!scheduleId,
  });
}

/**
 * Hook para agendamentos de hoje
 */
export function useTodaySchedules() {
  return useQuery({
    queryKey: ['diarists', 'schedules', 'today'],
    queryFn: () => diaristCoreService.getTodaySchedules(),
    refetchInterval: 60000, // Atualiza a cada 1min
  });
}
