/**
 * Candidates Hooks - Gestão de Candidatos
 *
 * Re-exports dos hooks Orval do módulo recruitment
 */

import {
  useListCandidatesApiV1RecruitmentCandidatesGet,
  useCreateCandidateApiV1RecruitmentCandidatesPost,
  useGetCandidateApiV1RecruitmentCandidatesCandidateIdGet,
  useUpdateCandidateApiV1RecruitmentCandidatesCandidateIdPatch,
  useDeleteCandidateApiV1RecruitmentCandidatesCandidateIdDelete,
  useImportCandidatesApiV1RecruitmentCandidatesImportPost,
  useBlockCandidateApiV1RecruitmentCandidatesCandidateIdBlockPost,
  useUnblockCandidateApiV1RecruitmentCandidatesCandidateIdUnblockPost,
  useGetCandidateStatsApiV1RecruitmentCandidatesStatsGet,
  useListActiveCandidatesApiV1RecruitmentCandidatesActiveGet,
  useListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGet,
  useAddCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePost,
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';

// List & Read
export const useCandidates = useListCandidatesApiV1RecruitmentCandidatesGet;
export const useCandidate = useGetCandidateApiV1RecruitmentCandidatesCandidateIdGet;
export const useActiveCandidates = useListActiveCandidatesApiV1RecruitmentCandidatesActiveGet;
export const useBlockedCandidates = useListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGet;
export const useCandidateStats = useGetCandidateStatsApiV1RecruitmentCandidatesStatsGet;

// Mutations
export const useCreateCandidate = useCreateCandidateApiV1RecruitmentCandidatesPost;
export const useUpdateCandidate = useUpdateCandidateApiV1RecruitmentCandidatesCandidateIdPatch;
export const useDeleteCandidate = useDeleteCandidateApiV1RecruitmentCandidatesCandidateIdDelete;
export const useImportCandidates = useImportCandidatesApiV1RecruitmentCandidatesImportPost;
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
