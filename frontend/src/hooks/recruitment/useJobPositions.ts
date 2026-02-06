/**
 * Job Positions Hooks - Gestão de Vagas
 *
 * Re-exports dos hooks Orval do módulo recruitment
 */

import { useQuery } from '@tanstack/react-query';
import {
  getListPositionsApiV1RecruitmentJobPositionsGetQueryOptions,
  getGetPositionApiV1RecruitmentJobPositionsPositionIdGetQueryOptions,
  getGetPositionStatsApiV1RecruitmentJobPositionsStatsGetQueryOptions,
  getListOpenPositionsApiV1RecruitmentJobPositionsOpenGetQueryOptions,
  useCreatePositionApiV1RecruitmentJobPositionsPost,
  useUpdatePositionApiV1RecruitmentJobPositionsPositionIdPut,
  useDeletePositionApiV1RecruitmentJobPositionsPositionIdDelete,
  usePublishPositionApiV1RecruitmentJobPositionsPositionIdPublishPost,
  useClosePositionApiV1RecruitmentJobPositionsPositionIdClosePost,
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';
import type {
  ListPositionsApiV1RecruitmentJobPositionsGetParams,
  GetPositionStatsApiV1RecruitmentJobPositionsStatsGetParams,
  ListOpenPositionsApiV1RecruitmentJobPositionsOpenGetParams,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';

// List & Read
export const useJobPositions = (params?: ListPositionsApiV1RecruitmentJobPositionsGetParams) =>
  useQuery(getListPositionsApiV1RecruitmentJobPositionsGetQueryOptions(params));

export const useJobPosition = (positionId: string) =>
  useQuery(getGetPositionApiV1RecruitmentJobPositionsPositionIdGetQueryOptions(positionId));

export const useActivePositions = (params?: ListPositionsApiV1RecruitmentJobPositionsGetParams) =>
  useQuery(getListPositionsApiV1RecruitmentJobPositionsGetQueryOptions({ ...params, status: 'aberta' as const }));

export const useOpenPositions = (params?: ListOpenPositionsApiV1RecruitmentJobPositionsOpenGetParams) =>
  useQuery(getListOpenPositionsApiV1RecruitmentJobPositionsOpenGetQueryOptions(params));

export const usePositionStats = (params?: GetPositionStatsApiV1RecruitmentJobPositionsStatsGetParams) =>
  useQuery(getGetPositionStatsApiV1RecruitmentJobPositionsStatsGetQueryOptions(params));

// Mutations
export const useCreateJobPosition = useCreatePositionApiV1RecruitmentJobPositionsPost;
export const useUpdateJobPosition = useUpdatePositionApiV1RecruitmentJobPositionsPositionIdPut;
export const useDeleteJobPosition = useDeletePositionApiV1RecruitmentJobPositionsPositionIdDelete;
export const usePublishPosition = usePublishPositionApiV1RecruitmentJobPositionsPositionIdPublishPost;
export const useClosePosition = useClosePositionApiV1RecruitmentJobPositionsPositionIdClosePost;

// Re-export types
export type {
  JobPositionCreate,
  JobPositionUpdate,
  JobPositionResponse,
  JobPositionPublish,
  JobPositionStats,
  JobPositionListResponse,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';
