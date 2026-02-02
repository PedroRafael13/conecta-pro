/**
 * Applications Hooks - Gestão de Candidaturas
 *
 * Re-exports dos hooks Orval do módulo recruitment
 */

import { useQuery } from '@tanstack/react-query';
import {
  getListApplicationsApiV1RecruitmentApplicationsGetQueryOptions,
  getGetApplicationApiV1RecruitmentApplicationsApplicationIdGetQueryOptions,
  getListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetQueryOptions,
  getListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetQueryOptions,
  getListActiveApiV1RecruitmentApplicationsActiveGetQueryOptions,
  getGetApplicationStatsApiV1RecruitmentApplicationsStatsGetQueryOptions,
  useCreateApplicationApiV1RecruitmentApplicationsPost,
  useUpdateApplicationApiV1RecruitmentApplicationsApplicationIdPut,
  useDeleteApplicationApiV1RecruitmentApplicationsApplicationIdDelete,
  useAdvanceStageApiV1RecruitmentApplicationsApplicationIdAdvancePost,
  useRejectApplicationApiV1RecruitmentApplicationsApplicationIdRejectPost,
  useSendProposalApiV1RecruitmentApplicationsApplicationIdProposalPost,
  useAcceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPost,
  useBulkActionApiV1RecruitmentApplicationsBulkActionPost,
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';
import type {
  ListApplicationsApiV1RecruitmentApplicationsGetParams,
  ListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetParams,
  ListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetParams,
  ListActiveApiV1RecruitmentApplicationsActiveGetParams,
  GetApplicationStatsApiV1RecruitmentApplicationsStatsGetParams,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';

// List & Read
export const useApplications = (params?: ListApplicationsApiV1RecruitmentApplicationsGetParams) =>
  useQuery(getListApplicationsApiV1RecruitmentApplicationsGetQueryOptions(params));

export const useApplication = (applicationId: string) =>
  useQuery(getGetApplicationApiV1RecruitmentApplicationsApplicationIdGetQueryOptions(applicationId));

export const useApplicationsByCandidate = (candidateId: string, params?: ListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetParams) =>
  useQuery(getListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetQueryOptions(candidateId, params));

export const useApplicationsByPosition = (positionId: string, params?: ListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetParams) =>
  useQuery(getListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetQueryOptions(positionId, params));

export const useActiveApplications = (params?: ListActiveApiV1RecruitmentApplicationsActiveGetParams) =>
  useQuery(getListActiveApiV1RecruitmentApplicationsActiveGetQueryOptions(params));

export const useApplicationStats = (params?: GetApplicationStatsApiV1RecruitmentApplicationsStatsGetParams) =>
  useQuery(getGetApplicationStatsApiV1RecruitmentApplicationsStatsGetQueryOptions(params));

// Mutations
export const useCreateApplication = useCreateApplicationApiV1RecruitmentApplicationsPost;
export const useUpdateApplication = useUpdateApplicationApiV1RecruitmentApplicationsApplicationIdPut;
export const useDeleteApplication = useDeleteApplicationApiV1RecruitmentApplicationsApplicationIdDelete;
export const useAdvanceApplication = useAdvanceStageApiV1RecruitmentApplicationsApplicationIdAdvancePost;
export const useRejectApplication = useRejectApplicationApiV1RecruitmentApplicationsApplicationIdRejectPost;
export const useSendProposal = useSendProposalApiV1RecruitmentApplicationsApplicationIdProposalPost;
export const useAcceptProposal = useAcceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPost;
export const useBulkAction = useBulkActionApiV1RecruitmentApplicationsBulkActionPost;

// Re-export types
export type {
  ApplicationCreate,
  ApplicationUpdate,
  ApplicationResponse,
  ApplicationAdvance,
  ApplicationReject,
  ApplicationProposal,
  ApplicationHire,
  ApplicationBulkAction,
  ApplicationStats,
  ApplicationListResponse,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';
