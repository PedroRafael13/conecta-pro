/**
 * Comodato Hooks
 * React Query hooks para gestão de comodatos
 */

import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { comodatoService } from '@/services/equipment/comodatoService';
import type {
  ComodatoCreate,
  ComodatoUpdate,
  ComodatoResponse,
  ComodatoListResponse,
  ListComodatosApiV1ComodatosGetParams,
  GetStatsApiV1ComodatosStatsGetParams,
  GetStatsApiV1ComodatosStatsGet200,
  GetActiveApiV1ComodatosActiveGetParams,
  GetExpiringApiV1ComodatosExpiringGetParams,
  SignComodatoApiV1ComodatosComodatoIdSignPostParams,
  DeliverComodatoApiV1ComodatosComodatoIdDeliverPostParams,
  BodyDeliverComodatoApiV1ComodatosComodatoIdDeliverPost,
  ScheduleReturnApiV1ComodatosComodatoIdScheduleReturnPostParams,
  RegisterReturnApiV1ComodatosComodatoIdReturnPostParams,
  BodyRegisterReturnApiV1ComodatosComodatoIdReturnPost,
  RegisterDamageApiV1ComodatosComodatoIdDamagePostParams,
  TerminateComodatoApiV1ComodatosComodatoIdTerminatePostParams,
  TransferComodatoApiV1ComodatosComodatoIdTransferPostParams
} from '@/types/generated/equipment/conectaPROEquipmentManagementAPI.schemas';

const COMODATO_KEYS = {
  all: ['comodato'] as const,
  lists: () => [...COMODATO_KEYS.all, 'list'] as const,
  list: (params?: ListComodatosApiV1ComodatosGetParams) => [...COMODATO_KEYS.lists(), params] as const,
  stats: (params?: GetStatsApiV1ComodatosStatsGetParams) => [...COMODATO_KEYS.all, 'stats', params] as const,
  active: (params?: GetActiveApiV1ComodatosActiveGetParams) => [...COMODATO_KEYS.all, 'active', params] as const,
  pendingSignature: () => [...COMODATO_KEYS.all, 'pending-signature'] as const,
  pendingDelivery: () => [...COMODATO_KEYS.all, 'pending-delivery'] as const,
  pendingReturn: () => [...COMODATO_KEYS.all, 'pending-return'] as const,
  expiring: (params?: GetExpiringApiV1ComodatosExpiringGetParams) => [...COMODATO_KEYS.all, 'expiring', params] as const,
  expired: () => [...COMODATO_KEYS.all, 'expired'] as const,
  byClient: (clientId: string) => [...COMODATO_KEYS.all, 'by-client', clientId] as const,
  byCode: (code: string) => [...COMODATO_KEYS.all, 'by-code', code] as const,
  detail: (id: string) => [...COMODATO_KEYS.all, 'detail', id] as const,
};

/**
 * Hook para listar comodatos
 */
export const useComodatoList = (
  params?: ListComodatosApiV1ComodatosGetParams,
  options?: UseQueryOptions<ComodatoListResponse>
) => {
  return useQuery({
    queryKey: COMODATO_KEYS.list(params),
    queryFn: () => comodatoService.list(params),
    ...options,
  });
};

/**
 * Hook para obter estatísticas de comodatos
 */
export const useComodatoStats = (
  params?: GetStatsApiV1ComodatosStatsGetParams,
  options?: UseQueryOptions<GetStatsApiV1ComodatosStatsGet200>
) => {
  return useQuery({
    queryKey: COMODATO_KEYS.stats(params),
    queryFn: () => comodatoService.getStats(params),
    ...options,
  });
};

/**
 * Hook para listar comodatos ativos
 */
export const useComodatoActive = (
  params?: GetActiveApiV1ComodatosActiveGetParams,
  options?: UseQueryOptions<ComodatoResponse[]>
) => {
  return useQuery({
    queryKey: COMODATO_KEYS.active(params),
    queryFn: () => comodatoService.getActive(params),
    ...options,
  });
};

/**
 * Hook para listar comodatos aguardando assinatura
 */
export const useComodatoPendingSignature = (options?: UseQueryOptions<ComodatoResponse[]>) => {
  return useQuery({
    queryKey: COMODATO_KEYS.pendingSignature(),
    queryFn: () => comodatoService.getPendingSignature(),
    ...options,
  });
};

/**
 * Hook para listar comodatos aguardando entrega
 */
export const useComodatoPendingDelivery = (options?: UseQueryOptions<ComodatoResponse[]>) => {
  return useQuery({
    queryKey: COMODATO_KEYS.pendingDelivery(),
    queryFn: () => comodatoService.getPendingDelivery(),
    ...options,
  });
};

/**
 * Hook para listar comodatos com devolução pendente
 */
export const useComodatoPendingReturn = (options?: UseQueryOptions<ComodatoResponse[]>) => {
  return useQuery({
    queryKey: COMODATO_KEYS.pendingReturn(),
    queryFn: () => comodatoService.getPendingReturn(),
    ...options,
  });
};

/**
 * Hook para listar comodatos expirando
 */
export const useComodatoExpiring = (
  params?: GetExpiringApiV1ComodatosExpiringGetParams,
  options?: UseQueryOptions<ComodatoResponse[]>
) => {
  return useQuery({
    queryKey: COMODATO_KEYS.expiring(params),
    queryFn: () => comodatoService.getExpiring(params),
    ...options,
  });
};

/**
 * Hook para listar comodatos expirados
 */
export const useComodatoExpired = (options?: UseQueryOptions<ComodatoResponse[]>) => {
  return useQuery({
    queryKey: COMODATO_KEYS.expired(),
    queryFn: () => comodatoService.getExpired(),
    ...options,
  });
};

/**
 * Hook para listar comodatos por cliente
 */
export const useComodatoByClient = (
  clientId: string,
  options?: UseQueryOptions<ComodatoResponse[]>
) => {
  return useQuery({
    queryKey: COMODATO_KEYS.byClient(clientId),
    queryFn: () => comodatoService.getByClient(clientId),
    enabled: !!clientId,
    ...options,
  });
};

/**
 * Hook para buscar comodato por código
 */
export const useComodatoByCode = (
  code: string,
  options?: UseQueryOptions<ComodatoResponse>
) => {
  return useQuery({
    queryKey: COMODATO_KEYS.byCode(code),
    queryFn: () => comodatoService.getByCode(code),
    enabled: !!code,
    ...options,
  });
};

/**
 * Hook para buscar comodato por ID
 */
export const useComodato = (
  comodatoId: string,
  options?: UseQueryOptions<ComodatoResponse>
) => {
  return useQuery({
    queryKey: COMODATO_KEYS.detail(comodatoId),
    queryFn: () => comodatoService.getById(comodatoId),
    enabled: !!comodatoId,
    ...options,
  });
};

/**
 * Hook para criar comodato
 */
export const useCreateComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ComodatoCreate) => comodatoService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.stats() });
    },
  });
};

/**
 * Hook para atualizar comodato
 */
export const useUpdateComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ comodatoId, data }: { comodatoId: string; data: ComodatoUpdate }) =>
      comodatoService.update(comodatoId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
    },
  });
};

/**
 * Hook para deletar comodato
 */
export const useDeleteComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (comodatoId: string) => comodatoService.delete(comodatoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.stats() });
    },
  });
};

/**
 * Hook para assinar comodato
 */
export const useSignComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comodatoId,
      params,
    }: {
      comodatoId: string;
      params: SignComodatoApiV1ComodatosComodatoIdSignPostParams;
    }) => comodatoService.sign(comodatoId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.pendingSignature() });
    },
  });
};

/**
 * Hook para entregar comodato
 */
export const useDeliverComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comodatoId,
      params,
      body,
    }: {
      comodatoId: string;
      params: DeliverComodatoApiV1ComodatosComodatoIdDeliverPostParams;
      body?: BodyDeliverComodatoApiV1ComodatosComodatoIdDeliverPost;
    }) => comodatoService.deliver(comodatoId, params, body),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.pendingDelivery() });
    },
  });
};

/**
 * Hook para solicitar devolução
 */
export const useRequestReturnComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (comodatoId: string) => comodatoService.requestReturn(comodatoId),
    onSuccess: (_, comodatoId) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.pendingReturn() });
    },
  });
};

/**
 * Hook para agendar devolução
 */
export const useScheduleReturnComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comodatoId,
      params,
    }: {
      comodatoId: string;
      params: ScheduleReturnApiV1ComodatosComodatoIdScheduleReturnPostParams;
    }) => comodatoService.scheduleReturn(comodatoId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
    },
  });
};

/**
 * Hook para registrar devolução
 */
export const useRegisterReturnComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comodatoId,
      params,
      body,
    }: {
      comodatoId: string;
      params: RegisterReturnApiV1ComodatosComodatoIdReturnPostParams;
      body?: BodyRegisterReturnApiV1ComodatosComodatoIdReturnPost;
    }) => comodatoService.registerReturn(comodatoId, params, body),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.pendingReturn() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.active() });
    },
  });
};

/**
 * Hook para registrar dano
 */
export const useRegisterDamageComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comodatoId,
      params,
    }: {
      comodatoId: string;
      params: RegisterDamageApiV1ComodatosComodatoIdDamagePostParams;
    }) => comodatoService.registerDamage(comodatoId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
    },
  });
};

/**
 * Hook para marcar como perdido
 */
export const useMarkAsLostComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (comodatoId: string) => comodatoService.markAsLost(comodatoId),
    onSuccess: (_, comodatoId) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
    },
  });
};

/**
 * Hook para encerrar comodato
 */
export const useTerminateComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comodatoId,
      params,
    }: {
      comodatoId: string;
      params: TerminateComodatoApiV1ComodatosComodatoIdTerminatePostParams;
    }) => comodatoService.terminate(comodatoId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.active() });
    },
  });
};

/**
 * Hook para transferir comodato
 */
export const useTransferComodato = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comodatoId,
      params,
    }: {
      comodatoId: string;
      params: TransferComodatoApiV1ComodatosComodatoIdTransferPostParams;
    }) => comodatoService.transfer(comodatoId, params),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.detail(variables.comodatoId) });
      queryClient.invalidateQueries({ queryKey: COMODATO_KEYS.lists() });
    },
  });
};

/**
 * Hook para gerar PDF do contrato
 */
export const useGenerateComodatoContractPdf = () => {
  return useMutation({
    mutationFn: (comodatoId: string) => comodatoService.generateContractPdf(comodatoId),
  });
};

/**
 * Hook para gerar termo de entrega
 */
export const useGenerateComodatoDeliveryTerm = () => {
  return useMutation({
    mutationFn: (comodatoId: string) => comodatoService.generateDeliveryTerm(comodatoId),
  });
};

/**
 * Hook para gerar termo de devolução
 */
export const useGenerateComodatoReturnTerm = () => {
  return useMutation({
    mutationFn: (comodatoId: string) => comodatoService.generateReturnTerm(comodatoId),
  });
};
