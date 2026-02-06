/**
 * React Query hooks for Operational AI
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { OperationalAIService } from '../operational.service';

// ========== DIARISTAS ==========

export function useCheckDiaristAvailability() {
  return useMutation({
    mutationFn: ({
      dataInicio,
      dataFim,
      tipo,
    }: {
      dataInicio: string;
      dataFim: string;
      tipo?: string;
    }) => OperationalAIService.checkDiaristAvailability(dataInicio, dataFim, tipo),
  });
}

export function useOptimizeDiaristAllocation() {
  return useMutation({
    mutationFn: ({
      dataInicio,
      dataFim,
      budget,
    }: {
      dataInicio: string;
      dataFim: string;
      budget?: number | string;
    }) => OperationalAIService.optimizeDiaristAllocation(dataInicio, dataFim, budget),
  });
}

export function useDiaristPerformance(diaristId: string) {
  return useQuery({
    queryKey: ['operational-ai', 'diarist', 'performance', diaristId],
    queryFn: () => OperationalAIService.analyzeDiaristPerformance(diaristId),
    enabled: !!diaristId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useSuggestDiarists() {
  return useMutation({
    mutationFn: ({
      data,
      tipo,
      hours,
    }: {
      data: string;
      tipo?: string;
      hours?: number;
    }) => OperationalAIService.suggestDiarists(data, tipo, hours),
  });
}

// ========== MANUTENÇÕES E EQUIPAMENTOS ==========

export function useEstimateMaintenanceCost(equipmentId: string) {
  return useQuery({
    queryKey: ['operational-ai', 'maintenance', 'estimate-cost', equipmentId],
    queryFn: () => OperationalAIService.estimateMaintenanceCost(equipmentId),
    enabled: !!equipmentId,
    staleTime: 30 * 60 * 1000,
  });
}

export function usePredictFailure(equipmentId: string) {
  return useQuery({
    queryKey: ['operational-ai', 'maintenance', 'predict-failure', equipmentId],
    queryFn: () => OperationalAIService.predictFailure(equipmentId),
    enabled: !!equipmentId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useEquipmentHealth(equipmentId: string) {
  return useQuery({
    queryKey: ['operational-ai', 'equipment', 'health', equipmentId],
    queryFn: () => OperationalAIService.analyzeEquipmentHealth(equipmentId),
    enabled: !!equipmentId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useMaintenancePatterns(clientId?: string) {
  return useQuery({
    queryKey: ['operational-ai', 'maintenance', 'patterns', clientId],
    queryFn: () => OperationalAIService.analyzeMaintenancePatterns(clientId),
    staleTime: 30 * 60 * 1000,
  });
}

export function useRecommendSchedule() {
  return useMutation({
    mutationFn: (clientId?: string) =>
      OperationalAIService.recommendSchedule(clientId),
  });
}

export function useOptimizeRoute() {
  return useMutation({
    mutationFn: ({ technicianId, date }: { technicianId: string; date: string }) =>
      OperationalAIService.optimizeRoute(technicianId, date),
  });
}
