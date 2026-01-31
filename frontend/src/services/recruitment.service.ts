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

import { getRecruitmentRecrutamentoESelecao } from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';
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

// Inicializar funções geradas
const api = getRecruitmentRecrutamentoESelecao();

// ===================================================================
// JOB POSITIONS SERVICE - Vagas (11 endpoints)
// ===================================================================

export const jobPositionService = {
  /**
   * Cria uma nova vaga de emprego
   */
  create: async (data: JobPositionCreate): Promise<JobPositionResponse> => {
    return await api.createPositionApiV1RecruitmentJobPositionsPost(data);
  },

  /**
   * Lista vagas com filtros e paginação
   */
  list: async (params?: ListPositionsApiV1RecruitmentJobPositionsGetParams): Promise<JobPositionListResponse> => {
    return await api.listPositionsApiV1RecruitmentJobPositionsGet(params);
  },

  /**
   * Lista vagas abertas para candidaturas
   */
  listOpen: async (params?: ListOpenPositionsApiV1RecruitmentJobPositionsOpenGetParams): Promise<JobPositionListResponse> => {
    return await api.listOpenPositionsApiV1RecruitmentJobPositionsOpenGet(params);
  },

  /**
   * Lista vagas próximas da data limite
   */
  listExpiring: async (params?: ListExpiringPositionsApiV1RecruitmentJobPositionsExpiringGetParams): Promise<JobPositionListResponse> => {
    return await api.listExpiringPositionsApiV1RecruitmentJobPositionsExpiringGet(params);
  },

  /**
   * Retorna estatísticas das vagas
   */
  getStats: async (params?: GetPositionStatsApiV1RecruitmentJobPositionsStatsGetParams): Promise<JobPositionStats> => {
    return await api.getPositionStatsApiV1RecruitmentJobPositionsStatsGet(params);
  },

  /**
   * Busca vaga por ID
   */
  getById: async (positionId: string): Promise<JobPositionResponse> => {
    return await api.getPositionApiV1RecruitmentJobPositionsPositionIdGet(positionId);
  },

  /**
   * Busca vaga por código
   */
  getByCode: async (code: string): Promise<JobPositionResponse> => {
    return await api.getPositionByCodeApiV1RecruitmentJobPositionsCodeCodeGet(code);
  },

  /**
   * Atualiza uma vaga
   */
  update: async (positionId: string, data: JobPositionUpdate): Promise<JobPositionResponse> => {
    return await api.updatePositionApiV1RecruitmentJobPositionsPositionIdPut(positionId, data);
  },

  /**
   * Deleta uma vaga
   */
  delete: async (positionId: string): Promise<void> => {
    await api.deletePositionApiV1RecruitmentJobPositionsPositionIdDelete(positionId);
  },

  /**
   * Publica uma vaga
   */
  publish: async (positionId: string, data: JobPositionPublish): Promise<JobPositionResponse> => {
    return await api.publishPositionApiV1RecruitmentJobPositionsPositionIdPublishPost(positionId, data);
  },

  /**
   * Pausa uma vaga
   */
  pause: async (positionId: string, params?: PausePositionApiV1RecruitmentJobPositionsPositionIdPausePostParams): Promise<JobPositionResponse> => {
    return await api.pausePositionApiV1RecruitmentJobPositionsPositionIdPausePost(positionId, params);
  },

  /**
   * Reabre uma vaga pausada
   */
  reopen: async (positionId: string): Promise<JobPositionResponse> => {
    return await api.reopenPositionApiV1RecruitmentJobPositionsPositionIdReopenPost(positionId);
  },

  /**
   * Fecha uma vaga definitivamente
   */
  close: async (positionId: string, params?: ClosePositionApiV1RecruitmentJobPositionsPositionIdClosePostParams): Promise<JobPositionResponse> => {
    return await api.closePositionApiV1RecruitmentJobPositionsPositionIdClosePost(positionId, params);
  },

  /**
   * Duplica uma vaga
   */
  duplicate: async (positionId: string): Promise<JobPositionResponse> => {
    return await api.duplicatePositionApiV1RecruitmentJobPositionsPositionIdDuplicatePost(positionId);
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
    return await api.createCandidateApiV1RecruitmentCandidatesPost(data);
  },

  /**
   * Importa candidato a partir de currículo
   */
  import: async (data: CandidateImport): Promise<CandidateResponse> => {
    return await api.importCandidateApiV1RecruitmentCandidatesImportPost(data);
  },

  /**
   * Lista candidatos com filtros
   */
  list: async (params?: ListCandidatesApiV1RecruitmentCandidatesGetParams): Promise<CandidateListResponse> => {
    return await api.listCandidatesApiV1RecruitmentCandidatesGet(params);
  },

  /**
   * Lista candidatos ativos
   */
  listActive: async (params?: ListActiveCandidatesApiV1RecruitmentCandidatesActiveGetParams): Promise<CandidateListResponse> => {
    return await api.listActiveCandidatesApiV1RecruitmentCandidatesActiveGet(params);
  },

  /**
   * Lista candidatos bloqueados
   */
  listBlocked: async (params?: ListBlockedCandidatesApiV1RecruitmentCandidatesBlockedGetParams): Promise<CandidateListResponse> => {
    return await api.listBlockedCandidatesApiV1RecruitmentCandidatesBlockedGet(params);
  },

  /**
   * Busca candidatos por skills
   */
  searchBySkills: async (params: SearchBySkillsApiV1RecruitmentCandidatesSearchSkillsGetParams): Promise<CandidateListResponse> => {
    return await api.searchBySkillsApiV1RecruitmentCandidatesSearchSkillsGet(params);
  },

  /**
   * Lista candidatos recentemente ativos
   */
  listRecentlyActive: async (params?: ListRecentlyActiveApiV1RecruitmentCandidatesRecentlyActiveGetParams): Promise<CandidateListResponse> => {
    return await api.listRecentlyActiveApiV1RecruitmentCandidatesRecentlyActiveGet(params);
  },

  /**
   * Retorna estatísticas dos candidatos
   */
  getStats: async (params?: GetCandidateStatsApiV1RecruitmentCandidatesStatsGetParams): Promise<CandidateStats> => {
    return await api.getCandidateStatsApiV1RecruitmentCandidatesStatsGet(params);
  },

  /**
   * Busca candidato por ID
   */
  getById: async (candidateId: string): Promise<CandidateResponse> => {
    return await api.getCandidateApiV1RecruitmentCandidatesCandidateIdGet(candidateId);
  },

  /**
   * Busca candidato por email
   */
  getByEmail: async (email: string): Promise<CandidateResponse> => {
    return await api.getCandidateByEmailApiV1RecruitmentCandidatesEmailEmailGet(email);
  },

  /**
   * Atualiza um candidato
   */
  update: async (candidateId: string, data: CandidateUpdate): Promise<CandidateResponse> => {
    return await api.updateCandidateApiV1RecruitmentCandidatesCandidateIdPut(candidateId, data);
  },

  /**
   * Deleta um candidato
   */
  delete: async (candidateId: string): Promise<void> => {
    await api.deleteCandidateApiV1RecruitmentCandidatesCandidateIdDelete(candidateId);
  },

  /**
   * Bloqueia um candidato
   */
  block: async (candidateId: string, data: CandidateBlock): Promise<CandidateResponse> => {
    return await api.blockCandidateApiV1RecruitmentCandidatesCandidateIdBlockPost(candidateId, data);
  },

  /**
   * Desbloqueia um candidato
   */
  unblock: async (candidateId: string): Promise<CandidateResponse> => {
    return await api.unblockCandidateApiV1RecruitmentCandidatesCandidateIdUnblockPost(candidateId);
  },

  /**
   * Arquiva um candidato
   */
  archive: async (candidateId: string): Promise<CandidateResponse> => {
    return await api.archiveCandidateApiV1RecruitmentCandidatesCandidateIdArchivePost(candidateId);
  },

  /**
   * Ativa um candidato arquivado
   */
  activate: async (candidateId: string): Promise<CandidateResponse> => {
    return await api.activateCandidateApiV1RecruitmentCandidatesCandidateIdActivatePost(candidateId);
  },

  /**
   * Atualiza tags de um candidato
   */
  updateTags: async (candidateId: string, tags: string[]): Promise<CandidateResponse> => {
    return await api.updateCandidateTagsApiV1RecruitmentCandidatesCandidateIdTagsPut(candidateId, tags);
  },

  /**
   * Adiciona nota a um candidato
   */
  addNote: async (candidateId: string, params: AddCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePostParams): Promise<CandidateResponse> => {
    return await api.addCandidateNoteApiV1RecruitmentCandidatesCandidateIdNotePost(candidateId, params);
  },

  /**
   * Mescla candidatos duplicados
   */
  merge: async (primaryId: string, secondaryId: string): Promise<CandidateResponse> => {
    return await api.mergeCandidatesApiV1RecruitmentCandidatesPrimaryIdMergeSecondaryIdPost(primaryId, secondaryId);
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
    return await api.createApplicationApiV1RecruitmentApplicationsPost(data);
  },

  /**
   * Lista candidaturas com filtros
   */
  list: async (params?: ListApplicationsApiV1RecruitmentApplicationsGetParams): Promise<ApplicationListResponse> => {
    return await api.listApplicationsApiV1RecruitmentApplicationsGet(params);
  },

  /**
   * Lista candidaturas por vaga
   */
  listByPosition: async (positionId: string, params?: ListByPositionApiV1RecruitmentApplicationsPositionPositionIdGetParams): Promise<ApplicationListResponse> => {
    return await api.listByPositionApiV1RecruitmentApplicationsPositionPositionIdGet(positionId, params);
  },

  /**
   * Lista candidaturas por candidato
   */
  listByCandidate: async (candidateId: string, params?: ListByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGetParams): Promise<ApplicationListResponse> => {
    return await api.listByCandidateApiV1RecruitmentApplicationsCandidateCandidateIdGet(candidateId, params);
  },

  /**
   * Lista candidaturas ativas
   */
  listActive: async (params?: ListActiveApiV1RecruitmentApplicationsActiveGetParams): Promise<ApplicationListResponse> => {
    return await api.listActiveApiV1RecruitmentApplicationsActiveGet(params);
  },

  /**
   * Lista candidaturas na shortlist
   */
  listShortlisted: async (positionId: string, params?: ListShortlistedApiV1RecruitmentApplicationsShortlistedPositionIdGetParams): Promise<ApplicationListResponse> => {
    return await api.listShortlistedApiV1RecruitmentApplicationsShortlistedPositionIdGet(positionId, params);
  },

  /**
   * Lista candidaturas favoritas
   */
  listFavorites: async (params?: ListFavoritesApiV1RecruitmentApplicationsFavoritesGetParams): Promise<ApplicationListResponse> => {
    return await api.listFavoritesApiV1RecruitmentApplicationsFavoritesGet(params);
  },

  /**
   * Retorna estatísticas das candidaturas
   */
  getStats: async (params?: GetApplicationStatsApiV1RecruitmentApplicationsStatsGetParams): Promise<ApplicationStats> => {
    return await api.getApplicationStatsApiV1RecruitmentApplicationsStatsGet(params);
  },

  /**
   * Busca candidatura por ID
   */
  getById: async (applicationId: string): Promise<ApplicationResponse> => {
    return await api.getApplicationApiV1RecruitmentApplicationsApplicationIdGet(applicationId);
  },

  /**
   * Atualiza uma candidatura
   */
  update: async (applicationId: string, data: ApplicationUpdate): Promise<ApplicationResponse> => {
    return await api.updateApplicationApiV1RecruitmentApplicationsApplicationIdPut(applicationId, data);
  },

  /**
   * Deleta uma candidatura
   */
  delete: async (applicationId: string): Promise<void> => {
    await api.deleteApplicationApiV1RecruitmentApplicationsApplicationIdDelete(applicationId);
  },

  /**
   * Avança candidatura para próxima etapa
   */
  advance: async (applicationId: string, data: ApplicationAdvance): Promise<ApplicationResponse> => {
    return await api.advanceStageApiV1RecruitmentApplicationsApplicationIdAdvancePost(applicationId, data);
  },

  /**
   * Rejeita uma candidatura
   */
  reject: async (applicationId: string, data: ApplicationReject): Promise<ApplicationResponse> => {
    return await api.rejectApplicationApiV1RecruitmentApplicationsApplicationIdRejectPost(applicationId, data);
  },

  /**
   * Envia proposta ao candidato
   */
  sendProposal: async (applicationId: string, data: ApplicationProposal): Promise<ApplicationResponse> => {
    return await api.sendProposalApiV1RecruitmentApplicationsApplicationIdProposalPost(applicationId, data);
  },

  /**
   * Aceita proposta
   */
  acceptProposal: async (applicationId: string, params?: AcceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPostParams): Promise<ApplicationResponse> => {
    return await api.acceptProposalApiV1RecruitmentApplicationsApplicationIdAcceptProposalPost(applicationId, params);
  },

  /**
   * Rejeita proposta
   */
  rejectProposal: async (applicationId: string, params?: RejectProposalApiV1RecruitmentApplicationsApplicationIdRejectProposalPostParams): Promise<ApplicationResponse> => {
    return await api.rejectProposalApiV1RecruitmentApplicationsApplicationIdRejectProposalPost(applicationId, params);
  },

  /**
   * Contrata candidato
   */
  hire: async (applicationId: string, data: ApplicationHire): Promise<ApplicationResponse> => {
    return await api.hireCandidateApiV1RecruitmentApplicationsApplicationIdHirePost(applicationId, data);
  },

  /**
   * Alterna favorito
   */
  toggleFavorite: async (applicationId: string): Promise<ApplicationResponse> => {
    return await api.toggleFavoriteApiV1RecruitmentApplicationsApplicationIdToggleFavoritePost(applicationId);
  },

  /**
   * Alterna shortlist
   */
  toggleShortlist: async (applicationId: string): Promise<ApplicationResponse> => {
    return await api.toggleShortlistApiV1RecruitmentApplicationsApplicationIdToggleShortlistPost(applicationId);
  },

  /**
   * Atualiza scores da candidatura
   */
  updateScores: async (applicationId: string, params: UpdateScoresApiV1RecruitmentApplicationsApplicationIdScorePutParams): Promise<ApplicationResponse> => {
    return await api.updateScoresApiV1RecruitmentApplicationsApplicationIdScorePut(applicationId, params);
  },

  /**
   * Recalcula matching da candidatura
   */
  recalculateMatching: async (applicationId: string): Promise<unknown> => {
    return await api.recalculateMatchingApiV1RecruitmentApplicationsApplicationIdMatchingPost(applicationId);
  },

  /**
   * Atualiza ranking das candidaturas de uma vaga
   */
  updateRanking: async (positionId: string): Promise<void> => {
    await api.updateRankingApiV1RecruitmentApplicationsPositionPositionIdUpdateRankingPost(positionId);
  },

  /**
   * Executa ação em lote nas candidaturas
   */
  bulkAction: async (data: ApplicationBulkAction): Promise<unknown> => {
    return await api.bulkActionApiV1RecruitmentApplicationsBulkActionPost(data);
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
    return await api.createInterviewApiV1RecruitmentInterviewsPost(data);
  },

  /**
   * Lista entrevistas com filtros
   */
  list: async (params?: ListInterviewsApiV1RecruitmentInterviewsGetParams): Promise<InterviewListResponse> => {
    return await api.listInterviewsApiV1RecruitmentInterviewsGet(params);
  },

  /**
   * Lista entrevistas de hoje
   */
  listToday: async (params?: ListTodayApiV1RecruitmentInterviewsTodayGetParams): Promise<InterviewListResponse> => {
    return await api.listTodayApiV1RecruitmentInterviewsTodayGet(params);
  },

  /**
   * Lista entrevistas próximas
   */
  listUpcoming: async (params?: ListUpcomingApiV1RecruitmentInterviewsUpcomingGetParams): Promise<InterviewListResponse> => {
    return await api.listUpcomingApiV1RecruitmentInterviewsUpcomingGet(params);
  },

  /**
   * Lista entrevistas pendentes de confirmação
   */
  listPendingConfirmation: async (): Promise<InterviewListResponse> => {
    return await api.listPendingConfirmationApiV1RecruitmentInterviewsPendingConfirmationGet();
  },

  /**
   * Lista entrevistas pendentes de resultado
   */
  listPendingResult: async (): Promise<InterviewListResponse> => {
    return await api.listPendingResultApiV1RecruitmentInterviewsPendingResultGet();
  },

  /**
   * Lista entrevistas por período
   */
  listByDateRange: async (params: ListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetParams): Promise<InterviewListResponse> => {
    return await api.listByDateRangeApiV1RecruitmentInterviewsByDateRangeGet(params);
  },

  /**
   * Lista entrevistas por candidatura
   */
  listByApplication: async (applicationId: string, params?: ListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetParams): Promise<InterviewListResponse> => {
    return await api.listByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGet(applicationId, params);
  },

  /**
   * Busca horários disponíveis para entrevistas
   */
  getAvailableSlots: async (params: GetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetParams): Promise<InterviewSlot[]> => {
    return await api.getAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGet(params);
  },

  /**
   * Busca calendário de entrevistas
   */
  getCalendar: async (interviewerId: string, params: GetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetParams): Promise<InterviewCalendar> => {
    return await api.getCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGet(interviewerId, params);
  },

  /**
   * Retorna estatísticas das entrevistas
   */
  getStats: async (params?: GetInterviewStatsApiV1RecruitmentInterviewsStatsGetParams): Promise<InterviewStats> => {
    return await api.getInterviewStatsApiV1RecruitmentInterviewsStatsGet(params);
  },

  /**
   * Busca entrevista por ID
   */
  getById: async (interviewId: string): Promise<InterviewResponse> => {
    return await api.getInterviewApiV1RecruitmentInterviewsInterviewIdGet(interviewId);
  },

  /**
   * Atualiza uma entrevista
   */
  update: async (interviewId: string, data: InterviewUpdate): Promise<InterviewResponse> => {
    return await api.updateInterviewApiV1RecruitmentInterviewsInterviewIdPut(interviewId, data);
  },

  /**
   * Deleta uma entrevista
   */
  delete: async (interviewId: string): Promise<void> => {
    await api.deleteInterviewApiV1RecruitmentInterviewsInterviewIdDelete(interviewId);
  },

  /**
   * Confirma presença do candidato
   */
  confirmCandidate: async (interviewId: string): Promise<InterviewResponse> => {
    return await api.confirmCandidateApiV1RecruitmentInterviewsInterviewIdConfirmCandidatePost(interviewId);
  },

  /**
   * Confirma presença do entrevistador
   */
  confirmInterviewer: async (interviewId: string): Promise<InterviewResponse> => {
    return await api.confirmInterviewerApiV1RecruitmentInterviewsInterviewIdConfirmInterviewerPost(interviewId);
  },

  /**
   * Inicia uma entrevista
   */
  start: async (interviewId: string): Promise<InterviewResponse> => {
    return await api.startInterviewApiV1RecruitmentInterviewsInterviewIdStartPost(interviewId);
  },

  /**
   * Completa uma entrevista
   */
  complete: async (interviewId: string, data: InterviewComplete): Promise<InterviewResponse> => {
    return await api.completeInterviewApiV1RecruitmentInterviewsInterviewIdCompletePost(interviewId, data);
  },

  /**
   * Cancela uma entrevista
   */
  cancel: async (interviewId: string, data: InterviewCancel): Promise<InterviewResponse> => {
    return await api.cancelInterviewApiV1RecruitmentInterviewsInterviewIdCancelPost(interviewId, data);
  },

  /**
   * Reagenda uma entrevista
   */
  reschedule: async (interviewId: string, data: InterviewReschedule): Promise<InterviewResponse> => {
    return await api.rescheduleInterviewApiV1RecruitmentInterviewsInterviewIdReschedulePost(interviewId, data);
  },

  /**
   * Marca candidato como ausente
   */
  markNoShow: async (interviewId: string): Promise<InterviewResponse> => {
    return await api.markNoShowApiV1RecruitmentInterviewsInterviewIdNoShowPost(interviewId);
  },

  /**
   * Adiciona avaliação à entrevista
   */
  addEvaluation: async (interviewId: string, data: InterviewEvaluation): Promise<InterviewResponse> => {
    return await api.addEvaluationApiV1RecruitmentInterviewsInterviewIdEvaluationPost(interviewId, data);
  },

  /**
   * Busca perguntas sugeridas por IA
   */
  getSuggestedQuestions: async (interviewId: string): Promise<unknown[]> => {
    return await api.getSuggestedQuestionsApiV1RecruitmentInterviewsInterviewIdQuestionsGet(interviewId);
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
