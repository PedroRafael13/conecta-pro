/**
 * Maintenance Hooks
 * React Query hooks para gestão de manutenções
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { maintenanceService } from '@/services/equipment/maintenanceService';
import type {
  MaintenanceCreate,
  MaintenanceUpdate,
  MaintenanceResponse,
  MaintenanceListResponse,
  MaintenanceStats,
  ListMaintenancesApiV1MaintenancesGetParams,
  GetStatsApiV1MaintenancesStatsGetParams,
  GetByTechnicianApiV1MaintenancesByTechnicianTechnicianIdGetParams,
  CompleteMaintenanceApiV1MaintenancesMaintenanceIdCompletePostParams,
  BodyMarkWaitingPartsApiV1MaintenancesMaintenanceIdWaitingPartsPost,
  AddPartReplacedApiV1MaintenancesMaintenanceIdAddPartPostParams,
  SignMaintenanceApiV1MaintenancesMaintenanceIdSignPostParams,
  AssignTechnicianApiV1MaintenancesMaintenanceIdAssignTechnicianPostParams,
  SchedulePreventiveApiV1MaintenancesSchedulePreventiveEquipmentIdPostParams,
  RecommendScheduleApiV1MaintenancesAiRecommendScheduleGetParams,
  OptimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGetParams,
  AnalyzePatternsApiV1MaintenancesAiPatternsGetParams,
  EstimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGetParams
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

const MAINTENANCE_KEYS = {
  all: ['maintenance'] as const,
  lists: () => [...MAINTENANCE_KEYS.all, 'list'] as const,
  list: (params?: ListMaintenancesApiV1MaintenancesGetParams) => [...MAINTENANCE_KEYS.lists(), params] as const,
  stats: (params?: GetStatsApiV1MaintenancesStatsGetParams) => [...MAINTENANCE_KEYS.all, 'stats', params] as const,
  overdue: () => [...MAINTENANCE_KEYS.all, 'overdue'] as const,
  waitingParts: () => [...MAINTENANCE_KEYS.all, 'waiting-parts'] as const,
  needingFollowup: () => [...MAINTENANCE_KEYS.all, 'needing-followup'] as const,
  byDate: (date: string) => [...MAINTENANCE_KEYS.all, 'by-date', date] as const,
  byEquipment: (equipmentId: string) => [...MAINTENANCE_KEYS.all, 'by-equipment', equipmentId] as const,
  byClient: (clientId: string) => [...MAINTENANCE_KEYS.all, 'by-client', clientId] as const,
  byTechnician: (technicianId: string, params?: GetByTechnicianApiV1MaintenancesByTechnicianTechnicianIdGetParams) =>
    [...MAINTENANCE_KEYS.all, 'by-technician', technicianId, params] as const,
  byCode: (code: string) => [...MAINTENANCE_KEYS.all, 'by-code', code] as const,
  detail: (id: string) => [...MAINTENANCE_KEYS.all, 'detail', id] as const,
  aiHealth: (equipmentId: string) => [...MAINTENANCE_KEYS.all, 'ai', 'health', equipmentId] as const,
  aiFailure: (equipmentId: string) => [...MAINTENANCE_KEYS.all, 'ai', 'failure', equipmentId] as const,
  aiSchedule: (params?: RecommendScheduleApiV1MaintenancesAiRecommendScheduleGetParams) =>
    [...MAINTENANCE_KEYS.all, 'ai', 'schedule', params] as const,
  aiRoute: (technicianId: string, params: OptimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGetParams) =>
    [...MAINTENANCE_KEYS.all, 'ai', 'route', technicianId, params] as const,
  aiPatterns: (params?: AnalyzePatternsApiV1MaintenancesAiPatternsGetParams) =>
    [...MAINTENANCE_KEYS.all, 'ai', 'patterns', params] as const,
  aiCost: (equipmentId: string, params?: EstimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGetParams) =>
    [...MAINTENANCE_KEYS.all, 'ai', 'cost', equipmentId, params] as const,
};

/**
 * Hook para listar manutenções
 */
export const useMaintenanceList = (
  params?: ListMaintenancesApiV1MaintenancesGetParams,
  options?: UseQueryOptions<MaintenanceListResponse>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.list(params),
    queryFn: () => maintenanceService.list(params),
    ...options,
  });
};

/**
 * Hook para obter estatísticas de manutenções
 */
export const useMaintenanceStats = (
  params?: GetStatsApiV1MaintenancesStatsGetParams,
  options?: UseQueryOptions<MaintenanceStats>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.stats(params),
    queryFn: () => maintenanceService.getStats(params),
    ...options,
  });
};

/**
 * Hook para listar manutenções atrasadas
 */
export const useMaintenanceOverdue = (options?: UseQueryOptions<MaintenanceResponse[]>) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.overdue(),
    queryFn: () => maintenanceService.getOverdue(),
    ...options,
  });
};

/**
 * Hook para listar manutenções aguardando peças
 */
export const useMaintenanceWaitingParts = (options?: UseQueryOptions<MaintenanceResponse[]>) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.waitingParts(),
    queryFn: () => maintenanceService.getWaitingParts(),
    ...options,
  });
};

/**
 * Hook para listar manutenções que precisam de follow-up
 */
export const useMaintenanceNeedingFollowup = (options?: UseQueryOptions<MaintenanceResponse[]>) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.needingFollowup(),
    queryFn: () => maintenanceService.getNeedingFollowup(),
    ...options,
  });
};

/**
 * Hook para listar manutenções por data
 */
export const useMaintenanceByDate = (
  date: string,
  options?: UseQueryOptions<MaintenanceResponse[]>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.byDate(date),
    queryFn: () => maintenanceService.getByDate(date),
    enabled: !!date,
    ...options,
  });
};

/**
 * Hook para listar manutenções por equipamento
 */
export const useMaintenanceByEquipment = (
  equipmentId: string,
  options?: UseQueryOptions<MaintenanceResponse[]>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.byEquipment(equipmentId),
    queryFn: () => maintenanceService.getByEquipment(equipmentId),
    enabled: !!equipmentId,
    ...options,
  });
};

/**
 * Hook para listar manutenções por cliente
 */
export const useMaintenanceByClient = (
  clientId: string,
  options?: UseQueryOptions<MaintenanceResponse[]>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.byClient(clientId),
    queryFn: () => maintenanceService.getByClient(clientId),
    enabled: !!clientId,
    ...options,
  });
};

/**
 * Hook para listar manutenções por técnico
 */
export const useMaintenanceByTechnician = (
  technicianId: string,
  params?: GetByTechnicianApiV1MaintenancesByTechnicianTechnicianIdGetParams,
  options?: UseQueryOptions<MaintenanceResponse[]>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.byTechnician(technicianId, params),
    queryFn: () => maintenanceService.getByTechnician(technicianId, params),
    enabled: !!technicianId,
    ...options,
  });
};

/**
 * Hook para buscar manutenção por código
 */
export const useMaintenanceByCode = (
  code: string,
  options?: UseQueryOptions<MaintenanceResponse>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.byCode(code),
    queryFn: () => maintenanceService.getByCode(code),
    enabled: !!code,
    ...options,
  });
};

/**
 * Hook para buscar manutenção por ID
 */
export const useMaintenance = (
  maintenanceId: string,
  options?: UseQueryOptions<MaintenanceResponse>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.detail(maintenanceId),
    queryFn: () => maintenanceService.getById(maintenanceId),
    enabled: !!maintenanceId,
    ...options,
  });
};

/**
 * Hook para criar manutenção
 */
export const useCreateMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: MaintenanceCreate) => maintenanceService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.stats() });
    },
  });
};

/**
 * Hook para atualizar manutenção
 */
export const useUpdateMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ maintenanceId, data }: { maintenanceId: string; data: MaintenanceUpdate }) =>
      maintenanceService.update(maintenanceId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(variables.maintenanceId) });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
    },
  });
};

/**
 * Hook para deletar manutenção
 */
export const useDeleteMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (maintenanceId: string) => maintenanceService.delete(maintenanceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.stats() });
    },
  });
};

/**
 * Hook para iniciar manutenção
 */
export const useStartMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (maintenanceId: string) => maintenanceService.start(maintenanceId),
    onSuccess: (_, maintenanceId) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(maintenanceId) });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
    },
  });
};

/**
 * Hook para completar manutenção
 */
export const useCompleteMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      maintenanceId,
      params,
    }: {
      maintenanceId: string;
      params?: CompleteMaintenanceApiV1MaintenancesMaintenanceIdCompletePostParams;
    }) => maintenanceService.complete(maintenanceId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(variables.maintenanceId) });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.stats() });
    },
  });
};

/**
 * Hook para cancelar manutenção
 */
export const useCancelMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (maintenanceId: string) => maintenanceService.cancel(maintenanceId),
    onSuccess: (_, maintenanceId) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(maintenanceId) });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
    },
  });
};

/**
 * Hook para marcar como aguardando peças
 */
export const useMarkMaintenanceWaitingParts = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      maintenanceId,
      body,
    }: {
      maintenanceId: string;
      body: BodyMarkWaitingPartsApiV1MaintenancesMaintenanceIdWaitingPartsPost;
    }) => maintenanceService.markWaitingParts(maintenanceId, body),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(variables.maintenanceId) });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.waitingParts() });
    },
  });
};

/**
 * Hook para adicionar peça substituída
 */
export const useAddMaintenancePartReplaced = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      maintenanceId,
      params,
    }: {
      maintenanceId: string;
      params: AddPartReplacedApiV1MaintenancesMaintenanceIdAddPartPostParams;
    }) => maintenanceService.addPartReplaced(maintenanceId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(variables.maintenanceId) });
    },
  });
};

/**
 * Hook para assinar manutenção
 */
export const useSignMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      maintenanceId,
      params,
    }: {
      maintenanceId: string;
      params: SignMaintenanceApiV1MaintenancesMaintenanceIdSignPostParams;
    }) => maintenanceService.sign(maintenanceId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(variables.maintenanceId) });
    },
  });
};

/**
 * Hook para atribuir técnico
 */
export const useAssignMaintenanceTechnician = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      maintenanceId,
      params,
    }: {
      maintenanceId: string;
      params: AssignTechnicianApiV1MaintenancesMaintenanceIdAssignTechnicianPostParams;
    }) => maintenanceService.assignTechnician(maintenanceId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.detail(variables.maintenanceId) });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
    },
  });
};

/**
 * Hook para agendar manutenção preventiva
 */
export const useSchedulePreventiveMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      equipmentId,
      params,
    }: {
      equipmentId: string;
      params?: SchedulePreventiveApiV1MaintenancesSchedulePreventiveEquipmentIdPostParams;
    }) => maintenanceService.schedulePreventive(equipmentId, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.stats() });
    },
  });
};

// AI Hooks

/**
 * Hook para análise de saúde do equipamento
 */
export const useMaintenanceAIHealth = (
  equipmentId: string,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.aiHealth(equipmentId),
    queryFn: () => maintenanceService.analyzeHealth(equipmentId),
    enabled: !!equipmentId,
    ...options,
  });
};

/**
 * Hook para previsão de falha
 */
export const useMaintenanceAIFailure = (
  equipmentId: string,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.aiFailure(equipmentId),
    queryFn: () => maintenanceService.predictFailure(equipmentId),
    enabled: !!equipmentId,
    ...options,
  });
};

/**
 * Hook para recomendação de agenda
 */
export const useMaintenanceAISchedule = (
  params?: RecommendScheduleApiV1MaintenancesAiRecommendScheduleGetParams,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.aiSchedule(params),
    queryFn: () => maintenanceService.recommendSchedule(params),
    ...options,
  });
};

/**
 * Hook para otimização de rota
 */
export const useMaintenanceAIRoute = (
  technicianId: string,
  params: OptimizeRouteApiV1MaintenancesAiOptimizeRouteTechnicianIdGetParams,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.aiRoute(technicianId, params),
    queryFn: () => maintenanceService.optimizeRoute(technicianId, params),
    enabled: !!technicianId,
    ...options,
  });
};

/**
 * Hook para análise de padrões
 */
export const useMaintenanceAIPatterns = (
  params?: AnalyzePatternsApiV1MaintenancesAiPatternsGetParams,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.aiPatterns(params),
    queryFn: () => maintenanceService.analyzePatterns(params),
    ...options,
  });
};

/**
 * Hook para estimativa de custo
 */
export const useMaintenanceAICost = (
  equipmentId: string,
  params?: EstimateCostApiV1MaintenancesAiEstimateCostEquipmentIdGetParams,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: MAINTENANCE_KEYS.aiCost(equipmentId, params),
    queryFn: () => maintenanceService.estimateCost(equipmentId, params),
    enabled: !!equipmentId,
    ...options,
  });
};
