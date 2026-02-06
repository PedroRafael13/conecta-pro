/**
 * React Query Hooks - Módulo RECRUITMENT
 *
 * Hooks customizados com cache inteligente, invalidação automática
 * e otimizações de performance para o módulo de Recrutamento e Seleção.
 *
 * Estrutura:
 * - Job Positions: queries + mutations
 * - Candidates: queries + mutations
 * - Applications: queries + mutations
 * - Interviews: queries + mutations
 *
 * Gerado por: Claude Sonnet 4.5
 * Data: 28/01/2026
 */

import { useMutation, useQuery, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { recruitmentService } from '@/services/recruitment.service';
import type {
  // Job Positions
  JobPositionCreate,
  JobPositionUpdate,
  JobPositionResponse,
  JobPositionListResponse,
  JobPositionStats,
  JobPositionPublish,
  ListPositionsApiV1RecruitmentJobPositionsGetParams,
  ListOpenPositionsApiV1RecruitmentJobPositionsOpenGetParams,
  ListExpiringPositionsApiV1RecruitmentJobPositionsExpiringGetParams,
  GetPositionStatsApiV1RecruitmentJobPositionsStatsGetParams,
  PausePositionApiV1RecruitmentJobPositionsPositionIdPausePostParams,
  ClosePositionApiV1RecruitmentJobPositionsPositionIdClosePostParams,

  // Candidates
  CandidateCreate,
  CandidateUpdate,
  CandidateResponse,
  CandidateListResponse,
  CandidateStats,
  CandidateBlock,
  CandidateImport,
  ListCandidatesApiV1RecruitmentCandidatesGetParams,
  ListActiveCandidatesApiV1RecruitmentCandidatesActiveGetParams,
  ListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetParams,
  SearchBySkillsApiV1RecruitmentCandidatesSearchSkillsGetParams,
  ListRecentlyActiveApiV1RecruitmentCandidatesRecentlyActiveGetParams,
  GetCandidateStatsApiV1RecruitmentCandidatesStatsGetParams,
  AddCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePostParams,

  // Applications
  ApplicationCreate,
  ApplicationUpdate,
  ApplicationResponse,
  ApplicationListResponse,
  ApplicationStats,
  ApplicationAdvance,
  ApplicationReject,
  ApplicationProposal,
  ApplicationHire,
  ApplicationBulkAction,
  ListApplicationsApiV1RecruitmentApplicationsGetParams,
  ListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetParams,
  ListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetParams,
  ListActiveApiV1RecruitmentApplicationsActiveGetParams,
  ListShortlistedApiV1RecruitmentApplicationsShortlistedPositionIdGetParams,
  ListFavoritesApiV1RecruitmentApplicationsFavoritesGetParams,
  GetApplicationStatsApiV1RecruitmentApplicationsStatsGetParams,
  AcceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPostParams,
  RejectProposalApiV1RecruitmentApplicationsApplicationIdRejectProposalPostParams,
  UpdateScoresApiV1RecruitmentApplicationsApplicationIdScorePutParams,

  // Interviews
  InterviewCreate,
  InterviewUpdate,
  InterviewResponse,
  InterviewListResponse,
  InterviewStats,
  InterviewComplete,
  InterviewReschedule,
  InterviewCancel,
  InterviewEvaluation,
  InterviewSlot,
  InterviewCalendar,
  ListInterviewsApiV1RecruitmentInterviewsGetParams,
  ListTodayApiV1RecruitmentInterviewsTodayGetParams,
  ListUpcomingApiV1RecruitmentInterviewsUpcomingGetParams,
  ListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetParams,
  ListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetParams,
  GetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetParams,
  GetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetParams,
  GetInterviewStatsApiV1RecruitmentInterviewsStatsGetParams,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';

// ===================================================================
// QUERY KEYS - Chaves para cache do React Query
// ===================================================================

export const recruitmentKeys = {
  // Job Positions
  positions: {
    all: ['recruitment', 'positions'] as const,
    lists: () => [...recruitmentKeys.positions.all, 'list'] as const,
    list: (params?: ListPositionsApiV1RecruitmentJobPositionsGetParams) => [...recruitmentKeys.positions.lists(), params] as const,
    open: (params?: ListOpenPositionsApiV1RecruitmentJobPositionsOpenGetParams) => [...recruitmentKeys.positions.all, 'open', params] as const,
    expiring: (params?: ListExpiringPositionsApiV1RecruitmentJobPositionsExpiringGetParams) => [...recruitmentKeys.positions.all, 'expiring', params] as const,
    stats: (params?: GetPositionStatsApiV1RecruitmentJobPositionsStatsGetParams) => [...recruitmentKeys.positions.all, 'stats', params] as const,
    detail: (id: string) => [...recruitmentKeys.positions.all, 'detail', id] as const,
    byCode: (code: string) => [...recruitmentKeys.positions.all, 'code', code] as const,
  },

  // Candidates
  candidates: {
    all: ['recruitment', 'candidates'] as const,
    lists: () => [...recruitmentKeys.candidates.all, 'list'] as const,
    list: (params?: ListCandidatesApiV1RecruitmentCandidatesGetParams) => [...recruitmentKeys.candidates.lists(), params] as const,
    active: (params?: ListActiveCandidatesApiV1RecruitmentCandidatesActiveGetParams) => [...recruitmentKeys.candidates.all, 'active', params] as const,
    blocked: (params?: ListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetParams) => [...recruitmentKeys.candidates.all, 'blocked', params] as const,
    bySkills: (params: SearchBySkillsApiV1RecruitmentCandidatesSearchSkillsGetParams) => [...recruitmentKeys.candidates.all, 'skills', params] as const,
    recentlyActive: (params?: ListRecentlyActiveApiV1RecruitmentCandidatesRecentlyActiveGetParams) => [...recruitmentKeys.candidates.all, 'recently-active', params] as const,
    stats: (params?: GetCandidateStatsApiV1RecruitmentCandidatesStatsGetParams) => [...recruitmentKeys.candidates.all, 'stats', params] as const,
    detail: (id: string) => [...recruitmentKeys.candidates.all, 'detail', id] as const,
    byEmail: (email: string) => [...recruitmentKeys.candidates.all, 'email', email] as const,
  },

  // Applications
  applications: {
    all: ['recruitment', 'applications'] as const,
    lists: () => [...recruitmentKeys.applications.all, 'list'] as const,
    list: (params?: ListApplicationsApiV1RecruitmentApplicationsGetParams) => [...recruitmentKeys.applications.lists(), params] as const,
    byPosition: (positionId: string, params?: ListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetParams) => [...recruitmentKeys.applications.all, 'position', positionId, params] as const,
    byCandidate: (candidateId: string, params?: ListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetParams) => [...recruitmentKeys.applications.all, 'candidate', candidateId, params] as const,
    active: (params?: ListActiveApiV1RecruitmentApplicationsActiveGetParams) => [...recruitmentKeys.applications.all, 'active', params] as const,
    shortlisted: (positionId: string, params?: ListShortlistedApiV1RecruitmentApplicationsShortlistedPositionIdGetParams) => [...recruitmentKeys.applications.all, 'shortlisted', positionId, params] as const,
    favorites: (params?: ListFavoritesApiV1RecruitmentApplicationsFavoritesGetParams) => [...recruitmentKeys.applications.all, 'favorites', params] as const,
    stats: (params?: GetApplicationStatsApiV1RecruitmentApplicationsStatsGetParams) => [...recruitmentKeys.applications.all, 'stats', params] as const,
    detail: (id: string) => [...recruitmentKeys.applications.all, 'detail', id] as const,
  },

  // Interviews
  interviews: {
    all: ['recruitment', 'interviews'] as const,
    lists: () => [...recruitmentKeys.interviews.all, 'list'] as const,
    list: (params?: ListInterviewsApiV1RecruitmentInterviewsGetParams) => [...recruitmentKeys.interviews.lists(), params] as const,
    today: (params?: ListTodayApiV1RecruitmentInterviewsTodayGetParams) => [...recruitmentKeys.interviews.all, 'today', params] as const,
    upcoming: (params?: ListUpcomingApiV1RecruitmentInterviewsUpcomingGetParams) => [...recruitmentKeys.interviews.all, 'upcoming', params] as const,
    pendingConfirmation: () => [...recruitmentKeys.interviews.all, 'pending-confirmation'] as const,
    pendingResult: () => [...recruitmentKeys.interviews.all, 'pending-result'] as const,
    byDateRange: (params: ListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetParams) => [...recruitmentKeys.interviews.all, 'date-range', params] as const,
    byApplication: (applicationId: string, params?: ListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetParams) => [...recruitmentKeys.interviews.all, 'application', applicationId, params] as const,
    availableSlots: (params: GetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetParams) => [...recruitmentKeys.interviews.all, 'slots', params] as const,
    calendar: (interviewerId: string, params: GetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetParams) => [...recruitmentKeys.interviews.all, 'calendar', interviewerId, params] as const,
    stats: (params?: GetInterviewStatsApiV1RecruitmentInterviewsStatsGetParams) => [...recruitmentKeys.interviews.all, 'stats', params] as const,
    detail: (id: string) => [...recruitmentKeys.interviews.all, 'detail', id] as const,
    questions: (id: string) => [...recruitmentKeys.interviews.all, 'questions', id] as const,
  },
};

// ===================================================================
// JOB POSITIONS HOOKS - Vagas
// ===================================================================

/**
 * Lista vagas com filtros
 */
export const useJobPositions = (
  params?: ListPositionsApiV1RecruitmentJobPositionsGetParams,
  options?: Omit<UseQueryOptions<JobPositionListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.positions.list(params),
    queryFn: () => recruitmentService.jobPositions.list(params),
    staleTime: 5 * 60 * 1000, // 5 minutos
    ...options,
  });
};

/**
 * Lista vagas abertas
 */
export const useOpenJobPositions = (
  params?: ListOpenPositionsApiV1RecruitmentJobPositionsOpenGetParams,
  options?: Omit<UseQueryOptions<JobPositionListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.positions.open(params),
    queryFn: () => recruitmentService.jobPositions.listOpen(params),
    staleTime: 3 * 60 * 1000,
    ...options,
  });
};

/**
 * Lista vagas próximas da expiração
 */
export const useExpiringJobPositions = (
  params?: ListExpiringPositionsApiV1RecruitmentJobPositionsExpiringGetParams,
  options?: Omit<UseQueryOptions<JobPositionListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.positions.expiring(params),
    queryFn: () => recruitmentService.jobPositions.listExpiring(params),
    staleTime: 10 * 60 * 1000,
    ...options,
  });
};

/**
 * Busca vaga por ID
 */
export const useJobPosition = (
  positionId: string,
  options?: Omit<UseQueryOptions<JobPositionResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.positions.detail(positionId),
    queryFn: () => recruitmentService.jobPositions.getById(positionId),
    staleTime: 5 * 60 * 1000,
    enabled: !!positionId,
    ...options,
  });
};

/**
 * Estatísticas de vagas
 */
export const useJobPositionStats = (
  params?: GetPositionStatsApiV1RecruitmentJobPositionsStatsGetParams,
  options?: Omit<UseQueryOptions<JobPositionStats>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.positions.stats(params),
    queryFn: () => recruitmentService.jobPositions.getStats(params),
    staleTime: 2 * 60 * 1000,
    ...options,
  });
};

/**
 * Mutation: Criar vaga
 */
export const useCreateJobPosition = (
  options?: UseMutationOptions<JobPositionResponse, Error, JobPositionCreate>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: JobPositionCreate) => recruitmentService.jobPositions.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.positions.all });
    },
    ...options,
  });
};

/**
 * Mutation: Atualizar vaga
 */
export const useUpdateJobPosition = (
  options?: UseMutationOptions<JobPositionResponse, Error, { id: string; data: JobPositionUpdate }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.jobPositions.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.positions.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.positions.all });
    },
    ...options,
  });
};

/**
 * Mutation: Deletar vaga
 */
export const useDeleteJobPosition = (
  options?: UseMutationOptions<void, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => recruitmentService.jobPositions.delete(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.positions.all });
      queryClient.removeQueries({ queryKey: recruitmentKeys.positions.detail(id) });
    },
    ...options,
  });
};

/**
 * Mutation: Publicar vaga
 */
export const usePublishJobPosition = (
  options?: UseMutationOptions<JobPositionResponse, Error, { id: string; data: JobPositionPublish }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.jobPositions.publish(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.positions.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.positions.all });
    },
    ...options,
  });
};

/**
 * Mutation: Duplicar vaga
 */
export const useDuplicateJobPosition = (
  options?: UseMutationOptions<JobPositionResponse, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => recruitmentService.jobPositions.duplicate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.positions.all });
    },
    ...options,
  });
};

// ===================================================================
// CANDIDATES HOOKS - Candidatos
// ===================================================================

/**
 * Lista candidatos
 */
export const useCandidates = (
  params?: ListCandidatesApiV1RecruitmentCandidatesGetParams,
  options?: Omit<UseQueryOptions<CandidateListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.candidates.list(params),
    queryFn: () => recruitmentService.candidates.list(params),
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

/**
 * Lista candidatos ativos
 */
export const useActiveCandidates = (
  params?: ListActiveCandidatesApiV1RecruitmentCandidatesActiveGetParams,
  options?: Omit<UseQueryOptions<CandidateListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.candidates.active(params),
    queryFn: () => recruitmentService.candidates.listActive(params),
    staleTime: 3 * 60 * 1000,
    ...options,
  });
};

/**
 * Busca candidato por ID
 */
export const useCandidate = (
  candidateId: string,
  options?: Omit<UseQueryOptions<CandidateResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.candidates.detail(candidateId),
    queryFn: () => recruitmentService.candidates.getById(candidateId),
    staleTime: 5 * 60 * 1000,
    enabled: !!candidateId,
    ...options,
  });
};

/**
 * Estatísticas de candidatos
 */
export const useCandidateStats = (
  params?: GetCandidateStatsApiV1RecruitmentCandidatesStatsGetParams,
  options?: Omit<UseQueryOptions<CandidateStats>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.candidates.stats(params),
    queryFn: () => recruitmentService.candidates.getStats(params),
    staleTime: 2 * 60 * 1000,
    ...options,
  });
};

/**
 * Mutation: Criar candidato
 */
export const useCreateCandidate = (
  options?: UseMutationOptions<CandidateResponse, Error, CandidateCreate>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CandidateCreate) => recruitmentService.candidates.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.candidates.all });
    },
    ...options,
  });
};

/**
 * Mutation: Atualizar candidato
 */
export const useUpdateCandidate = (
  options?: UseMutationOptions<CandidateResponse, Error, { id: string; data: CandidateUpdate }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.candidates.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.candidates.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.candidates.all });
    },
    ...options,
  });
};

/**
 * Mutation: Bloquear candidato
 */
export const useBlockCandidate = (
  options?: UseMutationOptions<CandidateResponse, Error, { id: string; data: CandidateBlock }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.candidates.block(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.candidates.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.candidates.all });
    },
    ...options,
  });
};

// ===================================================================
// APPLICATIONS HOOKS - Candidaturas
// ===================================================================

/**
 * Lista candidaturas
 */
export const useApplications = (
  params?: ListApplicationsApiV1RecruitmentApplicationsGetParams,
  options?: Omit<UseQueryOptions<ApplicationListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.applications.list(params),
    queryFn: () => recruitmentService.applications.list(params),
    staleTime: 3 * 60 * 1000,
    ...options,
  });
};

/**
 * Lista candidaturas por vaga
 */
export const useApplicationsByPosition = (
  positionId: string,
  params?: ListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetParams,
  options?: Omit<UseQueryOptions<ApplicationListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.applications.byPosition(positionId, params),
    queryFn: () => recruitmentService.applications.listByPosition(positionId, params),
    staleTime: 2 * 60 * 1000,
    enabled: !!positionId,
    ...options,
  });
};

/**
 * Busca candidatura por ID
 */
export const useApplication = (
  applicationId: string,
  options?: Omit<UseQueryOptions<ApplicationResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.applications.detail(applicationId),
    queryFn: () => recruitmentService.applications.getById(applicationId),
    staleTime: 3 * 60 * 1000,
    enabled: !!applicationId,
    ...options,
  });
};

/**
 * Estatísticas de candidaturas
 */
export const useApplicationStats = (
  params?: GetApplicationStatsApiV1RecruitmentApplicationsStatsGetParams,
  options?: Omit<UseQueryOptions<ApplicationStats>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.applications.stats(params),
    queryFn: () => recruitmentService.applications.getStats(params),
    staleTime: 2 * 60 * 1000,
    ...options,
  });
};

/**
 * Mutation: Criar candidatura
 */
export const useCreateApplication = (
  options?: UseMutationOptions<ApplicationResponse, Error, ApplicationCreate>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ApplicationCreate) => recruitmentService.applications.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.all });
    },
    ...options,
  });
};

/**
 * Mutation: Atualizar candidatura
 */
export const useUpdateApplication = (
  options?: UseMutationOptions<ApplicationResponse, Error, { id: string; data: ApplicationUpdate }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.applications.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.all });
    },
    ...options,
  });
};

/**
 * Mutation: Avançar candidatura
 */
export const useAdvanceApplication = (
  options?: UseMutationOptions<ApplicationResponse, Error, { id: string; data: ApplicationAdvance }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.applications.advance(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.all });
    },
    ...options,
  });
};

/**
 * Mutation: Rejeitar candidatura
 */
export const useRejectApplication = (
  options?: UseMutationOptions<ApplicationResponse, Error, { id: string; data: ApplicationReject }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.applications.reject(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.all });
    },
    ...options,
  });
};

/**
 * Mutation: Toggle favorito
 */
export const useToggleFavoriteApplication = (
  options?: UseMutationOptions<ApplicationResponse, Error, string>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => recruitmentService.applications.toggleFavorite(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.detail(id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.applications.all });
    },
    ...options,
  });
};

// ===================================================================
// INTERVIEWS HOOKS - Entrevistas
// ===================================================================

/**
 * Lista entrevistas
 */
export const useInterviews = (
  params?: ListInterviewsApiV1RecruitmentInterviewsGetParams,
  options?: Omit<UseQueryOptions<InterviewListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.interviews.list(params),
    queryFn: () => recruitmentService.interviews.list(params),
    staleTime: 3 * 60 * 1000,
    ...options,
  });
};

/**
 * Lista entrevistas de hoje
 */
export const useTodayInterviews = (
  params?: ListTodayApiV1RecruitmentInterviewsTodayGetParams,
  options?: Omit<UseQueryOptions<InterviewListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.interviews.today(params),
    queryFn: () => recruitmentService.interviews.listToday(params),
    staleTime: 1 * 60 * 1000, // 1 minuto - dados mais frescos
    ...options,
  });
};

/**
 * Lista entrevistas próximas
 */
export const useUpcomingInterviews = (
  params?: ListUpcomingApiV1RecruitmentInterviewsUpcomingGetParams,
  options?: Omit<UseQueryOptions<InterviewListResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.interviews.upcoming(params),
    queryFn: () => recruitmentService.interviews.listUpcoming(params),
    staleTime: 2 * 60 * 1000,
    ...options,
  });
};

/**
 * Busca entrevista por ID
 */
export const useInterview = (
  interviewId: string,
  options?: Omit<UseQueryOptions<InterviewResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.interviews.detail(interviewId),
    queryFn: () => recruitmentService.interviews.getById(interviewId),
    staleTime: 3 * 60 * 1000,
    enabled: !!interviewId,
    ...options,
  });
};

/**
 * Busca horários disponíveis
 */
export const useAvailableSlots = (
  params: GetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetParams,
  options?: Omit<UseQueryOptions<InterviewSlot[]>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.interviews.availableSlots(params),
    queryFn: () => recruitmentService.interviews.getAvailableSlots(params),
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

/**
 * Estatísticas de entrevistas
 */
export const useInterviewStats = (
  params?: GetInterviewStatsApiV1RecruitmentInterviewsStatsGetParams,
  options?: Omit<UseQueryOptions<InterviewStats>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recruitmentKeys.interviews.stats(params),
    queryFn: () => recruitmentService.interviews.getStats(params),
    staleTime: 2 * 60 * 1000,
    ...options,
  });
};

/**
 * Mutation: Criar entrevista
 */
export const useCreateInterview = (
  options?: UseMutationOptions<InterviewResponse, Error, InterviewCreate>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: InterviewCreate) => recruitmentService.interviews.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.all });
    },
    ...options,
  });
};

/**
 * Mutation: Atualizar entrevista
 */
export const useUpdateInterview = (
  options?: UseMutationOptions<InterviewResponse, Error, { id: string; data: InterviewUpdate }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.interviews.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.all });
    },
    ...options,
  });
};

/**
 * Mutation: Completar entrevista
 */
export const useCompleteInterview = (
  options?: UseMutationOptions<InterviewResponse, Error, { id: string; data: InterviewComplete }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.interviews.complete(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.all });
    },
    ...options,
  });
};

/**
 * Mutation: Cancelar entrevista
 */
export const useCancelInterview = (
  options?: UseMutationOptions<InterviewResponse, Error, { id: string; data: InterviewCancel }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.interviews.cancel(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.all });
    },
    ...options,
  });
};

/**
 * Mutation: Reagendar entrevista
 */
export const useRescheduleInterview = (
  options?: UseMutationOptions<InterviewResponse, Error, { id: string; data: InterviewReschedule }>
) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => recruitmentService.interviews.reschedule(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: recruitmentKeys.interviews.all });
    },
    ...options,
  });
};
