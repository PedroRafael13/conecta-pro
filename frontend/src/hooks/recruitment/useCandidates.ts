/**
 * Candidates Hooks - Gestão de Candidatos
 *
 * Re-exports dos hooks Orval do módulo recruitment
 */

import { useQuery } from '@tanstack/react-query';
import {
  getListCandidatesApiV1RecruitmentCandidatesGetQueryOptions,
  getGetCandidateApiV1RecruitmentCandidatesCandidateIdGetQueryOptions,
  getListActiveCandidatesApiV1RecruitmentCandidatesActiveGetQueryOptions,
  getListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetQueryOptions,
  getGetCandidateStatsApiV1RecruitmentCandidatesStatsGetQueryOptions,
  useCreateCandidateApiV1RecruitmentCandidatesPost,
  useUpdateCandidateApiV1RecruitmentCandidatesCandidateIdPut,
  useDeleteCandidateApiV1RecruitmentCandidatesCandidateIdDelete,
  useImportCandidateApiV1RecruitmentCandidatesImportPost,
  useBlockCandidateApiV1RecruitmentCandidatesCandidateIdBlockPost,
  useUnblockCandidateApiV1RecruitmentCandidatesCandidateIdUnblockPost,
  useAddCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePost,
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';
import type {
  ListCandidatesApiV1RecruitmentCandidatesGetParams,
  ListActiveCandidatesApiV1RecruitmentCandidatesActiveGetParams,
  ListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetParams,
  GetCandidateStatsApiV1RecruitmentCandidatesStatsGetParams,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';

// List & Read
export const useCandidates = (params?: ListCandidatesApiV1RecruitmentCandidatesGetParams) =>
  useQuery(getListCandidatesApiV1RecruitmentCandidatesGetQueryOptions(params));

export const useCandidate = (candidateId: string) =>
  useQuery(getGetCandidateApiV1RecruitmentCandidatesCandidateIdGetQueryOptions(candidateId));

export const useActiveCandidates = (params?: ListActiveCandidatesApiV1RecruitmentCandidatesActiveGetParams) =>
  useQuery(getListActiveCandidatesApiV1RecruitmentCandidatesActiveGetQueryOptions(params));

export const useBlockedCandidates = (params?: ListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetParams) =>
  useQuery(getListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetQueryOptions(params));

export const useCandidateStats = (params?: GetCandidateStatsApiV1RecruitmentCandidatesStatsGetParams) =>
  useQuery(getGetCandidateStatsApiV1RecruitmentCandidatesStatsGetQueryOptions(params));

// Mutations
export const useCreateCandidate = useCreateCandidateApiV1RecruitmentCandidatesPost;
export const useUpdateCandidate = useUpdateCandidateApiV1RecruitmentCandidatesCandidateIdPut;
export const useDeleteCandidate = useDeleteCandidateApiV1RecruitmentCandidatesCandidateIdDelete;
export const useImportCandidates = useImportCandidateApiV1RecruitmentCandidatesImportPost;
export const useBlockCandidate = useBlockCandidateApiV1RecruitmentCandidatesCandidateIdBlockPost;
export const useUnblockCandidate = useUnblockCandidateApiV1RecruitmentCandidatesCandidateIdUnblockPost;
export const useAddCandidateNote = useAddCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePost;

// Re-export types
export type {
  CandidateCreate,
  CandidateUpdate,
  CandidateResponse,
  CandidateImport,
  CandidateBlock,
  CandidateStats,
  CandidateListResponse,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';
