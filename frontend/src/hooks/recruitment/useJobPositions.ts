/**
 * Job Positions Hooks - Gestão de Vagas
 *
 * Re-exports dos hooks Orval do módulo recruitment
 */

import {
  useListJobPositionsApiV1RecruitmentJobPositionsGet,
  useCreateJobPositionApiV1RecruitmentJobPositionsPost,
  useGetJobPositionApiV1RecruitmentJobPositionsPositionIdGet,
  useUpdateJobPositionApiV1RecruitmentJobPositionsPositionIdPatch,
  useDeleteJobPositionApiV1RecruitmentJobPositionsPositionIdDelete,
  usePublishPositionApiV1RecruitmentJobPositionsPositionIdPublishPost,
  useClosePositionApiV1RecruitmentJobPositionsPositionIdClosePost,
  useGetPositionStatsApiV1RecruitmentJobPositionsStatsGet,
  useListActivePositionsApiV1RecruitmentJobPositionsActiveGet,
  useListOpenPositionsApiV1RecruitmentJobPositionsOpenGet,
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';

// List & Read
export const useJobPositions = useListJobPositionsApiV1RecruitmentJobPositionsGet;
export const useJobPosition = useGetJobPositionApiV1RecruitmentJobPositionsPositionIdGet;
export const useActivePositions = useListActivePositionsApiV1RecruitmentJobPositionsActiveGet;
export const useOpenPositions = useListOpenPositionsApiV1RecruitmentJobPositionsOpenGet;
export const usePositionStats = useGetPositionStatsApiV1RecruitmentJobPositionsStatsGet;

// Mutations
export const useCreateJobPosition = useCreateJobPositionApiV1RecruitmentJobPositionsPost;
export const useUpdateJobPosition = useUpdateJobPositionApiV1RecruitmentJobPositionsPositionIdPatch;
export const useDeleteJobPosition = useDeleteJobPositionApiV1RecruitmentJobPositionsPositionIdDelete;
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
