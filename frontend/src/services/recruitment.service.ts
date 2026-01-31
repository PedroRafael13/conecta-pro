/**
 * Service Layer - Módulo RECRUITMENT (Recrutamento e Seleção)
 *
 * Wraps das funções geradas pelo Orval com interface limpa e organizada.
 *
 * Estrutura:
 * - Job Positions (Vagas): 11 endpoints
 * - Candidates (Candidatos): 16 endpoints
 * - Applications (Candidaturas): 20 endpoints
 * - Interviews (Entrevistas): 20 endpoints
 * - Total: 67 endpoints
 *
 * Gerado por: Claude Sonnet 4.5
 * Data: 28/01/2026
 */

import {
  // Funções da API geradas pelo Orval
  createPositionApiV1RecruitmentJobPositionsPost,
  listPositionsApiV1RecruitmentJobPositionsGet,
  listOpenPositionsApiV1RecruitmentJobPositionsOpenGet,
  listExpiringPositionsApiV1RecruitmentJobPositionsExpiringGet,
  getPositionStatsApiV1RecruitmentJobPositionsStatsGet,
  getPositionApiV1RecruitmentJobPositionsPositionIdGet,
  updatePositionApiV1RecruitmentJobPositionsPositionIdPut,
  deletePositionApiV1RecruitmentJobPositionsPositionIdDelete,
  getPositionByCodeApiV1RecruitmentJobPositionsCodeCodeGet,
  pausePositionApiV1RecruitmentJobPositionsPositionIdPausePost,
  closePositionApiV1RecruitmentJobPositionsPositionIdClosePost,
  publishPositionApiV1RecruitmentJobPositionsPositionIdPublishPost,
  reopenPositionApiV1RecruitmentJobPositionsPositionIdReopenPost,
  duplicatePositionApiV1RecruitmentJobPositionsPositionIdDuplicatePost,
  createCandidateApiV1RecruitmentCandidatesPost,
  listCandidatesApiV1RecruitmentCandidatesGet,
  listActiveCandidatesApiV1RecruitmentCandidatesActiveGet,
  listBlockedCandidatesApiV1RecruitmentCandidatesBlockedGet,
  listRecentlyActiveApiV1RecruitmentCandidatesRecentlyActiveGet,
  searchBySkillsApiV1RecruitmentCandidatesSearchSkillsGet,
  getCandidateStatsApiV1RecruitmentCandidatesStatsGet,
  getCandidateApiV1RecruitmentCandidatesCandidateIdGet,
  updateCandidateApiV1RecruitmentCandidatesCandidateIdPut,
  deleteCandidateApiV1RecruitmentCandidatesCandidateIdDelete,
  blockCandidateApiV1RecruitmentCandidatesCandidateIdBlockPost,
  unblockCandidateApiV1RecruitmentCandidatesCandidateIdUnblockPost,
  archiveCandidateApiV1RecruitmentCandidatesCandidateIdArchivePost,
  activateCandidateApiV1RecruitmentCandidatesCandidateIdActivatePost,
  getCandidateByEmailApiV1RecruitmentCandidatesEmailEmailGet,
  addCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePost,
  updateCandidateTagsApiV1RecruitmentCandidatesCandidateIdTagsPut,
  importCandidateApiV1RecruitmentCandidatesImportPost,
  mergeCandidatesApiV1RecruitmentCandidatesPrimaryIdMergeSecondaryIdPost,
  createApplicationApiV1RecruitmentApplicationsPost,
  listApplicationsApiV1RecruitmentApplicationsGet,
  listByPositionApiV1RecruitmentApplicationsPositionPositionIdGet,
  listByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGet,
  listActiveApiV1RecruitmentApplicationsActiveGet,
  listShortlistedApiV1RecruitmentApplicationsShortlistedPositionIdGet,
  listFavoritesApiV1RecruitmentApplicationsFavoritesGet,
  getApplicationStatsApiV1RecruitmentApplicationsStatsGet,
  getApplicationApiV1RecruitmentApplicationsApplicationIdGet,
  updateApplicationApiV1RecruitmentApplicationsApplicationIdPut,
  deleteApplicationApiV1RecruitmentApplicationsApplicationIdDelete,
  advanceStageApiV1RecruitmentApplicationsApplicationIdAdvancePost,
  rejectApplicationApiV1RecruitmentApplicationsApplicationIdRejectPost,
  sendProposalApiV1RecruitmentApplicationsApplicationIdProposalPost,
  acceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPost,
  rejectProposalApiV1RecruitmentApplicationsApplicationIdRejectProposalPost,
  hireCandidateApiV1RecruitmentApplicationsApplicationIdHirePost,
  toggleShortlistApiV1RecruitmentApplicationsApplicationIdToggleShortlistPost,
  toggleFavoriteApiV1RecruitmentApplicationsApplicationIdToggleFavoritePost,
  updateScoresApiV1RecruitmentApplicationsApplicationIdScorePut,
  updateRankingApiV1RecruitmentApplicationsPositionPositionIdUpdateRankingPost,
  bulkActionApiV1RecruitmentApplicationsBulkActionPost,
  recalculateMatchingApiV1RecruitmentApplicationsApplicationIdMatchingPost,
  createInterviewApiV1RecruitmentInterviewsPost,
  listInterviewsApiV1RecruitmentInterviewsGet,
  listTodayApiV1RecruitmentInterviewsTodayGet,
  listUpcomingApiV1RecruitmentInterviewsUpcomingGet,
  listByDateRangeApiV1RecruitmentInterviewsByDateRangeGet,
  listPendingConfirmationApiV1RecruitmentInterviewsPendingConfirmationGet,
  listPendingResultApiV1RecruitmentInterviewsPendingResultGet,
  getAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGet,
  listByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGet,
  getCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGet,
  getInterviewStatsApiV1RecruitmentInterviewsStatsGet,
  getInterviewApiV1RecruitmentInterviewsInterviewIdGet,
  updateInterviewApiV1RecruitmentInterviewsInterviewIdPut,
  deleteInterviewApiV1RecruitmentInterviewsInterviewIdDelete,
  rescheduleInterviewApiV1RecruitmentInterviewsInterviewIdReschedulePost,
  confirmInterviewerApiV1RecruitmentInterviewsInterviewIdConfirmInterviewerPost,
  confirmCandidateApiV1RecruitmentInterviewsInterviewIdConfirmCandidatePost,
  startInterviewApiV1RecruitmentInterviewsInterviewIdStartPost,
  completeInterviewApiV1RecruitmentInterviewsInterviewIdCompletePost,
  cancelInterviewApiV1RecruitmentInterviewsInterviewIdCancelPost,
  markNoShowApiV1RecruitmentInterviewsInterviewIdNoShowPost,
  addEvaluationApiV1RecruitmentInterviewsInterviewIdEvaluationPost,
  getSuggestedQuestionsApiV1RecruitmentInterviewsInterviewIdQuestionsGet,
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';
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
// JOB POSITIONS SERVICE - Vagas (11 endpoints)
// ===================================================================

export const jobPositionService = {
  /**
   * Cria uma nova vaga de emprego
   */
  create: async (data: JobPositionCreate): Promise<JobPositionResponse> => {
    return await createPositionApiV1RecruitmentJobPositionsPost(data);
  },

  /**
   * Lista vagas com filtros e paginação
   */
  list: async (params?: ListPositionsApiV1RecruitmentJobPositionsGetParams): Promise<JobPositionListResponse> => {
    return await listPositionsApiV1RecruitmentJobPositionsGet(params);
  },

  /**
   * Lista vagas abertas para candidaturas
   */
  listOpen: async (params?: ListOpenPositionsApiV1RecruitmentJobPositionsOpenGetParams): Promise<JobPositionListResponse> => {
    return await listOpenPositionsApiV1RecruitmentJobPositionsOpenGet(params);
  },

  /**
   * Lista vagas próximas da data limite
   */
  listExpiring: async (params?: ListExpiringPositionsApiV1RecruitmentJobPositionsExpiringGetParams): Promise<JobPositionListResponse> => {
    return await listExpiringPositionsApiV1RecruitmentJobPositionsExpiringGet(params);
  },

  /**
   * Retorna estatísticas das vagas
   */
  getStats: async (params?: GetPositionStatsApiV1RecruitmentJobPositionsStatsGetParams): Promise<JobPositionStats> => {
    return await getPositionStatsApiV1RecruitmentJobPositionsStatsGet(params);
  },

  /**
   * Busca vaga por ID
   */
  getById: async (positionId: string): Promise<JobPositionResponse> => {
    return await getPositionApiV1RecruitmentJobPositionsPositionIdGet(positionId);
  },

  /**
   * Busca vaga por código
   */
  getByCode: async (code: string): Promise<JobPositionResponse> => {
    return await getPositionByCodeApiV1RecruitmentJobPositionsCodeCodeGet(code);
  },

  /**
   * Atualiza uma vaga
   */
  update: async (positionId: string, data: JobPositionUpdate): Promise<JobPositionResponse> => {
    return await updatePositionApiV1RecruitmentJobPositionsPositionIdPut(positionId, data);
  },

  /**
   * Deleta uma vaga
   */
  delete: async (positionId: string): Promise<void> => {
    await deletePositionApiV1RecruitmentJobPositionsPositionIdDelete(positionId);
  },

  /**
   * Publica uma vaga
   */
  publish: async (positionId: string, data: JobPositionPublish): Promise<JobPositionResponse> => {
    return await publishPositionApiV1RecruitmentJobPositionsPositionIdPublishPost(positionId, data);
  },

  /**
   * Pausa uma vaga
   */
  pause: async (positionId: string, params?: PausePositionApiV1RecruitmentJobPositionsPositionIdPausePostParams): Promise<JobPositionResponse> => {
    return await pausePositionApiV1RecruitmentJobPositionsPositionIdPausePost(positionId, params);
  },

  /**
   * Reabre uma vaga pausada
   */
  reopen: async (positionId: string): Promise<JobPositionResponse> => {
    return await reopenPositionApiV1RecruitmentJobPositionsPositionIdReopenPost(positionId);
  },

  /**
   * Fecha uma vaga definitivamente
   */
  close: async (positionId: string, params?: ClosePositionApiV1RecruitmentJobPositionsPositionIdClosePostParams): Promise<JobPositionResponse> => {
    return await closePositionApiV1RecruitmentJobPositionsPositionIdClosePost(positionId, params);
  },

  /**
   * Duplica uma vaga
   */
  duplicate: async (positionId: string): Promise<JobPositionResponse> => {
    return await duplicatePositionApiV1RecruitmentJobPositionsPositionIdDuplicatePost(positionId);
  },
};

// ===================================================================
// CANDIDATES SERVICE - Candidatos (16 endpoints)
// ===================================================================

export const candidateService = {
  /**
   * Cria um novo candidato
   */
  create: async (data: CandidateCreate): Promise<CandidateResponse> => {
    return await createCandidateApiV1RecruitmentCandidatesPost(data);
  },

  /**
   * Importa candidato a partir de currículo
   */
  import: async (data: CandidateImport): Promise<CandidateResponse> => {
    return await importCandidateApiV1RecruitmentCandidatesImportPost(data);
  },

  /**
   * Lista candidatos com filtros
   */
  list: async (params?: ListCandidatesApiV1RecruitmentCandidatesGetParams): Promise<CandidateListResponse> => {
    return await listCandidatesApiV1RecruitmentCandidatesGet(params);
  },

  /**
   * Lista candidatos ativos
   */
  listActive: async (params?: ListActiveCandidatesApiV1RecruitmentCandidatesActiveGetParams): Promise<CandidateListResponse> => {
    return await listActiveCandidatesApiV1RecruitmentCandidatesActiveGet(params);
  },

  /**
   * Lista candidatos bloqueados
   */
  listBlocked: async (params?: ListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetParams): Promise<CandidateListResponse> => {
    return await listBlockedCandidatesApiV1RecruitmentCandidatesBlockedGet(params);
  },

  /**
   * Busca candidatos por skills
   */
  searchBySkills: async (params: SearchBySkillsApiV1RecruitmentCandidatesSearchSkillsGetParams): Promise<CandidateListResponse> => {
    return await searchBySkillsApiV1RecruitmentCandidatesSearchSkillsGet(params);
  },

  /**
   * Lista candidatos recentemente ativos
   */
  listRecentlyActive: async (params?: ListRecentlyActiveApiV1RecruitmentCandidatesRecentlyActiveGetParams): Promise<CandidateListResponse> => {
    return await listRecentlyActiveApiV1RecruitmentCandidatesRecentlyActiveGet(params);
  },

  /**
   * Retorna estatísticas dos candidatos
   */
  getStats: async (params?: GetCandidateStatsApiV1RecruitmentCandidatesStatsGetParams): Promise<CandidateStats> => {
    return await getCandidateStatsApiV1RecruitmentCandidatesStatsGet(params);
  },

  /**
   * Busca candidato por ID
   */
  getById: async (candidateId: string): Promise<CandidateResponse> => {
    return await getCandidateApiV1RecruitmentCandidatesCandidateIdGet(candidateId);
  },

  /**
   * Busca candidato por email
   */
  getByEmail: async (email: string): Promise<CandidateResponse> => {
    return await getCandidateByEmailApiV1RecruitmentCandidatesEmailEmailGet(email);
  },

  /**
   * Atualiza um candidato
   */
  update: async (candidateId: string, data: CandidateUpdate): Promise<CandidateResponse> => {
    return await updateCandidateApiV1RecruitmentCandidatesCandidateIdPut(candidateId, data);
  },

  /**
   * Deleta um candidato
   */
  delete: async (candidateId: string): Promise<void> => {
    await deleteCandidateApiV1RecruitmentCandidatesCandidateIdDelete(candidateId);
  },

  /**
   * Bloqueia um candidato
   */
  block: async (candidateId: string, data: CandidateBlock): Promise<CandidateResponse> => {
    return await blockCandidateApiV1RecruitmentCandidatesCandidateIdBlockPost(candidateId, data);
  },

  /**
   * Desbloqueia um candidato
   */
  unblock: async (candidateId: string): Promise<CandidateResponse> => {
    return await unblockCandidateApiV1RecruitmentCandidatesCandidateIdUnblockPost(candidateId);
  },

  /**
   * Arquiva um candidato
   */
  archive: async (candidateId: string): Promise<CandidateResponse> => {
    return await archiveCandidateApiV1RecruitmentCandidatesCandidateIdArchivePost(candidateId);
  },

  /**
   * Ativa um candidato arquivado
   */
  activate: async (candidateId: string): Promise<CandidateResponse> => {
    return await activateCandidateApiV1RecruitmentCandidatesCandidateIdActivatePost(candidateId);
  },

  /**
   * Atualiza tags de um candidato
   */
  updateTags: async (candidateId: string, tags: string[]): Promise<CandidateResponse> => {
    return await updateCandidateTagsApiV1RecruitmentCandidatesCandidateIdTagsPut(candidateId, tags);
  },

  /**
   * Adiciona nota a um candidato
   */
  addNote: async (candidateId: string, params: AddCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePostParams): Promise<CandidateResponse> => {
    return await addCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePost(candidateId, params);
  },

  /**
   * Mescla candidatos duplicados
   */
  merge: async (primaryId: string, secondaryId: string): Promise<CandidateResponse> => {
    return await mergeCandidatesApiV1RecruitmentCandidatesPrimaryIdMergeSecondaryIdPost(primaryId, secondaryId);
  },
};

// ===================================================================
// APPLICATIONS SERVICE - Candidaturas (20 endpoints)
// ===================================================================

export const applicationService = {
  /**
   * Cria uma nova candidatura
   */
  create: async (data: ApplicationCreate): Promise<ApplicationResponse> => {
    return await createApplicationApiV1RecruitmentApplicationsPost(data);
  },

  /**
   * Lista candidaturas com filtros
   */
  list: async (params?: ListApplicationsApiV1RecruitmentApplicationsGetParams): Promise<ApplicationListResponse> => {
    return await listApplicationsApiV1RecruitmentApplicationsGet(params);
  },

  /**
   * Lista candidaturas por vaga
   */
  listByPosition: async (positionId: string, params?: ListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetParams): Promise<ApplicationListResponse> => {
    return await listByPositionApiV1RecruitmentApplicationsPositionPositionIdGet(positionId, params);
  },

  /**
   * Lista candidaturas por candidato
   */
  listByCandidate: async (candidateId: string, params?: ListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetParams): Promise<ApplicationListResponse> => {
    return await listByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGet(candidateId, params);
  },

  /**
   * Lista candidaturas ativas
   */
  listActive: async (params?: ListActiveApiV1RecruitmentApplicationsActiveGetParams): Promise<ApplicationListResponse> => {
    return await listActiveApiV1RecruitmentApplicationsActiveGet(params);
  },

  /**
   * Lista candidaturas na shortlist
   */
  listShortlisted: async (positionId: string, params?: ListShortlistedApiV1RecruitmentApplicationsShortlistedPositionIdGetParams): Promise<ApplicationListResponse> => {
    return await listShortlistedApiV1RecruitmentApplicationsShortlistedPositionIdGet(positionId, params);
  },

  /**
   * Lista candidaturas favoritas
   */
  listFavorites: async (params?: ListFavoritesApiV1RecruitmentApplicationsFavoritesGetParams): Promise<ApplicationListResponse> => {
    return await listFavoritesApiV1RecruitmentApplicationsFavoritesGet(params);
  },

  /**
   * Retorna estatísticas das candidaturas
   */
  getStats: async (params?: GetApplicationStatsApiV1RecruitmentApplicationsStatsGetParams): Promise<ApplicationStats> => {
    return await getApplicationStatsApiV1RecruitmentApplicationsStatsGet(params);
  },

  /**
   * Busca candidatura por ID
   */
  getById: async (applicationId: string): Promise<ApplicationResponse> => {
    return await getApplicationApiV1RecruitmentApplicationsApplicationIdGet(applicationId);
  },

  /**
   * Atualiza uma candidatura
   */
  update: async (applicationId: string, data: ApplicationUpdate): Promise<ApplicationResponse> => {
    return await updateApplicationApiV1RecruitmentApplicationsApplicationIdPut(applicationId, data);
  },

  /**
   * Deleta uma candidatura
   */
  delete: async (applicationId: string): Promise<void> => {
    await deleteApplicationApiV1RecruitmentApplicationsApplicationIdDelete(applicationId);
  },

  /**
   * Avança candidatura para próxima etapa
   */
  advance: async (applicationId: string, data: ApplicationAdvance): Promise<ApplicationResponse> => {
    return await advanceStageApiV1RecruitmentApplicationsApplicationIdAdvancePost(applicationId, data);
  },

  /**
   * Rejeita uma candidatura
   */
  reject: async (applicationId: string, data: ApplicationReject): Promise<ApplicationResponse> => {
    return await rejectApplicationApiV1RecruitmentApplicationsApplicationIdRejectPost(applicationId, data);
  },

  /**
   * Envia proposta ao candidato
   */
  sendProposal: async (applicationId: string, data: ApplicationProposal): Promise<ApplicationResponse> => {
    return await sendProposalApiV1RecruitmentApplicationsApplicationIdProposalPost(applicationId, data);
  },

  /**
   * Aceita proposta
   */
  acceptProposal: async (applicationId: string, params?: AcceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPostParams): Promise<ApplicationResponse> => {
    return await acceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPost(applicationId, params);
  },

  /**
   * Rejeita proposta
   */
  rejectProposal: async (applicationId: string, params?: RejectProposalApiV1RecruitmentApplicationsApplicationIdRejectProposalPostParams): Promise<ApplicationResponse> => {
    return await rejectProposalApiV1RecruitmentApplicationsApplicationIdRejectProposalPost(applicationId, params);
  },

  /**
   * Contrata candidato
   */
  hire: async (applicationId: string, data: ApplicationHire): Promise<ApplicationResponse> => {
    return await hireCandidateApiV1RecruitmentApplicationsApplicationIdHirePost(applicationId, data);
  },

  /**
   * Alterna favorito
   */
  toggleFavorite: async (applicationId: string): Promise<ApplicationResponse> => {
    return await toggleFavoriteApiV1RecruitmentApplicationsApplicationIdToggleFavoritePost(applicationId);
  },

  /**
   * Alterna shortlist
   */
  toggleShortlist: async (applicationId: string): Promise<ApplicationResponse> => {
    return await toggleShortlistApiV1RecruitmentApplicationsApplicationIdToggleShortlistPost(applicationId);
  },

  /**
   * Atualiza scores da candidatura
   */
  updateScores: async (applicationId: string, params: UpdateScoresApiV1RecruitmentApplicationsApplicationIdScorePutParams): Promise<ApplicationResponse> => {
    return await updateScoresApiV1RecruitmentApplicationsApplicationIdScorePut(applicationId, params);
  },

  /**
   * Recalcula matching da candidatura
   */
  recalculateMatching: async (applicationId: string): Promise<unknown> => {
    return await recalculateMatchingApiV1RecruitmentApplicationsApplicationIdMatchingPost(applicationId);
  },

  /**
   * Atualiza ranking das candidaturas de uma vaga
   */
  updateRanking: async (positionId: string): Promise<void> => {
    await updateRankingApiV1RecruitmentApplicationsPositionPositionIdUpdateRankingPost(positionId);
  },

  /**
   * Executa ação em lote nas candidaturas
   */
  bulkAction: async (data: ApplicationBulkAction): Promise<unknown> => {
    return await bulkActionApiV1RecruitmentApplicationsBulkActionPost(data);
  },
};

// ===================================================================
// INTERVIEWS SERVICE - Entrevistas (20 endpoints)
// ===================================================================

export const interviewService = {
  /**
   * Cria uma nova entrevista
   */
  create: async (data: InterviewCreate): Promise<InterviewResponse> => {
    return await createInterviewApiV1RecruitmentInterviewsPost(data);
  },

  /**
   * Lista entrevistas com filtros
   */
  list: async (params?: ListInterviewsApiV1RecruitmentInterviewsGetParams): Promise<InterviewListResponse> => {
    return await listInterviewsApiV1RecruitmentInterviewsGet(params);
  },

  /**
   * Lista entrevistas de hoje
   */
  listToday: async (params?: ListTodayApiV1RecruitmentInterviewsTodayGetParams): Promise<InterviewListResponse> => {
    return await listTodayApiV1RecruitmentInterviewsTodayGet(params);
  },

  /**
   * Lista entrevistas próximas
   */
  listUpcoming: async (params?: ListUpcomingApiV1RecruitmentInterviewsUpcomingGetParams): Promise<InterviewListResponse> => {
    return await listUpcomingApiV1RecruitmentInterviewsUpcomingGet(params);
  },

  /**
   * Lista entrevistas pendentes de confirmação
   */
  listPendingConfirmation: async (): Promise<InterviewListResponse> => {
    return await listPendingConfirmationApiV1RecruitmentInterviewsPendingConfirmationGet();
  },

  /**
   * Lista entrevistas pendentes de resultado
   */
  listPendingResult: async (): Promise<InterviewListResponse> => {
    return await listPendingResultApiV1RecruitmentInterviewsPendingResultGet();
  },

  /**
   * Lista entrevistas por período
   */
  listByDateRange: async (params: ListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetParams): Promise<InterviewListResponse> => {
    return await listByDateRangeApiV1RecruitmentInterviewsByDateRangeGet(params);
  },

  /**
   * Lista entrevistas por candidatura
   */
  listByApplication: async (applicationId: string, params?: ListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetParams): Promise<InterviewListResponse> => {
    return await listByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGet(applicationId, params);
  },

  /**
   * Busca horários disponíveis para entrevistas
   */
  getAvailableSlots: async (params: GetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetParams): Promise<InterviewSlot[]> => {
    return await getAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGet(params);
  },

  /**
   * Busca calendário de entrevistas
   */
  getCalendar: async (interviewerId: string, params: GetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetParams): Promise<InterviewCalendar> => {
    return await getCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGet(interviewerId, params);
  },

  /**
   * Retorna estatísticas das entrevistas
   */
  getStats: async (params?: GetInterviewStatsApiV1RecruitmentInterviewsStatsGetParams): Promise<InterviewStats> => {
    return await getInterviewStatsApiV1RecruitmentInterviewsStatsGet(params);
  },

  /**
   * Busca entrevista por ID
   */
  getById: async (interviewId: string): Promise<InterviewResponse> => {
    return await getInterviewApiV1RecruitmentInterviewsInterviewIdGet(interviewId);
  },

  /**
   * Atualiza uma entrevista
   */
  update: async (interviewId: string, data: InterviewUpdate): Promise<InterviewResponse> => {
    return await updateInterviewApiV1RecruitmentInterviewsInterviewIdPut(interviewId, data);
  },

  /**
   * Deleta uma entrevista
   */
  delete: async (interviewId: string): Promise<void> => {
    await deleteInterviewApiV1RecruitmentInterviewsInterviewIdDelete(interviewId);
  },

  /**
   * Confirma presença do candidato
   */
  confirmCandidate: async (interviewId: string): Promise<InterviewResponse> => {
    return await confirmCandidateApiV1RecruitmentInterviewsInterviewIdConfirmCandidatePost(interviewId);
  },

  /**
   * Confirma presença do entrevistador
   */
  confirmInterviewer: async (interviewId: string): Promise<InterviewResponse> => {
    return await confirmInterviewerApiV1RecruitmentInterviewsInterviewIdConfirmInterviewerPost(interviewId);
  },

  /**
   * Inicia uma entrevista
   */
  start: async (interviewId: string): Promise<InterviewResponse> => {
    return await startInterviewApiV1RecruitmentInterviewsInterviewIdStartPost(interviewId);
  },

  /**
   * Completa uma entrevista
   */
  complete: async (interviewId: string, data: InterviewComplete): Promise<InterviewResponse> => {
    return await completeInterviewApiV1RecruitmentInterviewsInterviewIdCompletePost(interviewId, data);
  },

  /**
   * Cancela uma entrevista
   */
  cancel: async (interviewId: string, data: InterviewCancel): Promise<InterviewResponse> => {
    return await cancelInterviewApiV1RecruitmentInterviewsInterviewIdCancelPost(interviewId, data);
  },

  /**
   * Reagenda uma entrevista
   */
  reschedule: async (interviewId: string, data: InterviewReschedule): Promise<InterviewResponse> => {
    return await rescheduleInterviewApiV1RecruitmentInterviewsInterviewIdReschedulePost(interviewId, data);
  },

  /**
   * Marca candidato como ausente
   */
  markNoShow: async (interviewId: string): Promise<InterviewResponse> => {
    return await markNoShowApiV1RecruitmentInterviewsInterviewIdNoShowPost(interviewId);
  },

  /**
   * Adiciona avaliação à entrevista
   */
  addEvaluation: async (interviewId: string, data: InterviewEvaluation): Promise<InterviewResponse> => {
    return await addEvaluationApiV1RecruitmentInterviewsInterviewIdEvaluationPost(interviewId, data);
  },

  /**
   * Busca perguntas sugeridas por IA
   */
  getSuggestedQuestions: async (interviewId: string): Promise<unknown[]> => {
    return await getSuggestedQuestionsApiV1RecruitmentInterviewsInterviewIdQuestionsGet(interviewId);
  },
};

// ===================================================================
// EXPORT CONSOLIDADO
// ===================================================================

export const recruitmentService = {
  jobPositions: jobPositionService,
  candidates: candidateService,
  applications: applicationService,
  interviews: interviewService,
};

export default recruitmentService;
