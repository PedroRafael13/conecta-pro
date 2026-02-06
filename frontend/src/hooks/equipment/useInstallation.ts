/**
 * Installation Hooks
 * React Query hooks para gestão de instalações
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { installationService } from '@/services/equipment/installationService';
import type {
  InstallationCreate,
  InstallationUpdate,
  InstallationResponse,
  InstallationListResponse,
  ListInstallationsApiV1InstallationsGetParams,
  GetStatsApiV1InstallationsStatsGetParams,
  GetStatsApiV1InstallationsStatsGet200,
  GetByTechnicianApiV1InstallationsByTechnicianTechnicianIdGetParams,
  GetTechnicianScheduleApiV1InstallationsTechnicianScheduleTechnicianIdGetParams,
  CompleteInstallationApiV1InstallationsInstallationIdCompletePostParams,
  CancelInstallationApiV1InstallationsInstallationIdCancelPostParams,
  RescheduleInstallationApiV1InstallationsInstallationIdReschedulePostParams,
  AcceptInstallationApiV1InstallationsInstallationIdAcceptPostParams,
  AddPhotoApiV1InstallationsInstallationIdPhotoPostParams,
  AssignTechnicianApiV1InstallationsInstallationIdAssignTechnicianPostParams
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

const INSTALLATION_KEYS = {
  all: ['installation'] as const,
  lists: () => [...INSTALLATION_KEYS.all, 'list'] as const,
  list: (params?: ListInstallationsApiV1InstallationsGetParams) => [...INSTALLATION_KEYS.lists(), params] as const,
  stats: (params: GetStatsApiV1InstallationsStatsGetParams) => [...INSTALLATION_KEYS.all, 'stats', params] as const,
  overdue: () => [...INSTALLATION_KEYS.all, 'overdue'] as const,
  pendingAcceptance: () => [...INSTALLATION_KEYS.all, 'pending-acceptance'] as const,
  byDate: (date: string) => [...INSTALLATION_KEYS.all, 'by-date', date] as const,
  byClient: (clientId: string) => [...INSTALLATION_KEYS.all, 'by-client', clientId] as const,
  byTechnician: (technicianId: string, params?: GetByTechnicianApiV1InstallationsByTechnicianTechnicianIdGetParams) =>
    [...INSTALLATION_KEYS.all, 'by-technician', technicianId, params] as const,
  technicianSchedule: (technicianId: string, params: GetTechnicianScheduleApiV1InstallationsTechnicianScheduleTechnicianIdGetParams) =>
    [...INSTALLATION_KEYS.all, 'technician-schedule', technicianId, params] as const,
  byCode: (code: string) => [...INSTALLATION_KEYS.all, 'by-code', code] as const,
  detail: (id: string) => [...INSTALLATION_KEYS.all, 'detail', id] as const,
};

/**
 * Hook para listar instalações
 */
export const useInstallationList = (
  params?: ListInstallationsApiV1InstallationsGetParams,
  options?: UseQueryOptions<InstallationListResponse>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.list(params),
    queryFn: () => installationService.list(params),
    ...options,
  });
};

/**
 * Hook para listar instalações atrasadas
 */
export const useInstallationOverdue = (options?: UseQueryOptions<InstallationResponse[]>) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.overdue(),
    queryFn: () => installationService.getOverdue(),
    ...options,
  });
};

/**
 * Hook para listar instalações aguardando aceite
 */
export const useInstallationPendingAcceptance = (options?: UseQueryOptions<InstallationResponse[]>) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.pendingAcceptance(),
    queryFn: () => installationService.getPendingAcceptance(),
    ...options,
  });
};

/**
 * Hook para listar instalações por data
 */
export const useInstallationByDate = (
  date: string,
  options?: UseQueryOptions<InstallationResponse[]>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.byDate(date),
    queryFn: () => installationService.getByDate(date),
    enabled: !!date,
    ...options,
  });
};

/**
 * Hook para listar instalações por cliente
 */
export const useInstallationByClient = (
  clientId: string,
  options?: UseQueryOptions<InstallationResponse[]>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.byClient(clientId),
    queryFn: () => installationService.getByClient(clientId),
    enabled: !!clientId,
    ...options,
  });
};

/**
 * Hook para listar instalações por técnico
 */
export const useInstallationByTechnician = (
  technicianId: string,
  params?: GetByTechnicianApiV1InstallationsByTechnicianTechnicianIdGetParams,
  options?: UseQueryOptions<InstallationResponse[]>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.byTechnician(technicianId, params),
    queryFn: () => installationService.getByTechnician(technicianId, params),
    enabled: !!technicianId,
    ...options,
  });
};

/**
 * Hook para obter agenda do técnico
 */
export const useInstallationTechnicianSchedule = (
  technicianId: string,
  params: GetTechnicianScheduleApiV1InstallationsTechnicianScheduleTechnicianIdGetParams,
  options?: UseQueryOptions<InstallationResponse[]>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.technicianSchedule(technicianId, params),
    queryFn: () => installationService.getTechnicianSchedule(technicianId, params),
    enabled: !!technicianId,
    ...options,
  });
};

/**
 * Hook para obter estatísticas de instalações
 */
export const useInstallationStats = (
  params: GetStatsApiV1InstallationsStatsGetParams,
  options?: UseQueryOptions<GetStatsApiV1InstallationsStatsGet200>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.stats(params),
    queryFn: () => installationService.getStats(params),
    ...options,
  });
};

/**
 * Hook para buscar instalação por código
 */
export const useInstallationByCode = (
  code: string,
  options?: UseQueryOptions<InstallationResponse>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.byCode(code),
    queryFn: () => installationService.getByCode(code),
    enabled: !!code,
    ...options,
  });
};

/**
 * Hook para buscar instalação por ID
 */
export const useInstallation = (
  installationId: string,
  options?: UseQueryOptions<InstallationResponse>
) => {
  return useQuery({
    queryKey: INSTALLATION_KEYS.detail(installationId),
    queryFn: () => installationService.getById(installationId),
    enabled: !!installationId,
    ...options,
  });
};

/**
 * Hook para criar instalação
 */
export const useCreateInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: InstallationCreate) => installationService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
    },
  });
};

/**
 * Hook para atualizar instalação
 */
export const useUpdateInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ installationId, data }: { installationId: string; data: InstallationUpdate }) =>
      installationService.update(installationId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(variables.installationId) });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
    },
  });
};

/**
 * Hook para deletar instalação
 */
export const useDeleteInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (installationId: string) => installationService.delete(installationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
    },
  });
};

/**
 * Hook para iniciar instalação
 */
export const useStartInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (installationId: string) => installationService.start(installationId),
    onSuccess: (_, installationId) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(installationId) });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
    },
  });
};

/**
 * Hook para completar instalação
 */
export const useCompleteInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      installationId,
      params,
    }: {
      installationId: string;
      params?: CompleteInstallationApiV1InstallationsInstallationIdCompletePostParams;
    }) => installationService.complete(installationId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(variables.installationId) });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.pendingAcceptance() });
    },
  });
};

/**
 * Hook para cancelar instalação
 */
export const useCancelInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      installationId,
      params,
    }: {
      installationId: string;
      params: CancelInstallationApiV1InstallationsInstallationIdCancelPostParams;
    }) => installationService.cancel(installationId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(variables.installationId) });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
    },
  });
};

/**
 * Hook para reagendar instalação
 */
export const useRescheduleInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      installationId,
      params,
    }: {
      installationId: string;
      params: RescheduleInstallationApiV1InstallationsInstallationIdReschedulePostParams;
    }) => installationService.reschedule(installationId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(variables.installationId) });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
    },
  });
};

/**
 * Hook para aceitar instalação
 */
export const useAcceptInstallation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      installationId,
      params,
    }: {
      installationId: string;
      params: AcceptInstallationApiV1InstallationsInstallationIdAcceptPostParams;
    }) => installationService.accept(installationId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(variables.installationId) });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.pendingAcceptance() });
    },
  });
};

/**
 * Hook para adicionar foto
 */
export const useAddInstallationPhoto = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      installationId,
      params,
    }: {
      installationId: string;
      params: AddPhotoApiV1InstallationsInstallationIdPhotoPostParams;
    }) => installationService.addPhoto(installationId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(variables.installationId) });
    },
  });
};

/**
 * Hook para atribuir técnico
 */
export const useAssignInstallationTechnician = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      installationId,
      params,
    }: {
      installationId: string;
      params: AssignTechnicianApiV1InstallationsInstallationIdAssignTechnicianPostParams;
    }) => installationService.assignTechnician(installationId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.detail(variables.installationId) });
      queryClient.invalidateQueries({ queryKey: INSTALLATION_KEYS.lists() });
    },
  });
};
