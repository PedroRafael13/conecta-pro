/**
 * Service Layer - DIARISTS Core
 *
 * Gerenciamento de diaristas, alocações, agendamentos,
 * pagamentos, avaliações e estatísticas.
 */

import {
  // Diarists CRUD
  listDiaristsApiV1OperacionalDiaristasGet,
  getDiaristApiV1OperacionalDiaristasDiaristIdGet,
  getAvailableDiaristsApiV1OperacionalDiaristasAvailableGet,
  consultaCpfApiV1OperacionalDiaristasConsultaCpfCpfGet,
  // Assignments
  listAssignmentsApiV1OperacionalDiaristasAssignmentsGet,
  getAssignmentApiV1OperacionalDiaristasAssignmentsAssignmentIdGet,
  // Schedules
  listSchedulesApiV1OperacionalDiaristasSchedulesGet,
  getScheduleApiV1OperacionalDiaristasSchedulesScheduleIdGet,
  getTodaySchedulesApiV1OperacionalDiaristasSchedulesTodayGet,
  // Payments
  listPaymentsApiV1OperacionalDiaristasPaymentsGet,
  getPaymentApiV1OperacionalDiaristasPaymentsPaymentIdGet,
  getPendingPaymentsApiV1OperacionalDiaristasPaymentsPendingGet,
  getPayrollReportApiV1OperacionalDiaristasPaymentsPayrollReportGet,
  // Evaluations
  listEvaluationsApiV1OperacionalDiaristasEvaluationsGet,
  getEvaluationApiV1OperacionalDiaristasEvaluationsEvaluationIdGet,
  // Statistics
  getGeneralStatisticsApiV1OperacionalDiaristasStatisticsGeneralGet,
  getTopDiaristsApiV1OperacionalDiaristasStatisticsRankingGet,
  getDiaristMetricsApiV1OperacionalDiaristasDiaristIdMetricsGet,
  // AI
  suggestDiaristsApiV1OperacionalDiaristasAiSuggestGet,
  analyzeAvailabilityApiV1OperacionalDiaristasAiAvailabilityGet,
  analyzePerformanceApiV1OperacionalDiaristasAiPerformanceDiaristIdGet,
  optimizeScheduleApiV1OperacionalDiaristasAiOptimizeGet,
} from '@/api/diarists/generated/operacional-diaristas/operacional-diaristas';

import type {
  DiaristStatus,
  DiaristType,
  AssignmentStatus,
  ScheduleStatus,
  PaymentStatus,
} from '@/api/diarists/generated/models';

/**
 * Service: Diarists Core
 *
 * Operações principais do módulo de diaristas.
 */
export class DiaristCoreService {
  /**
   * Lista diaristas com filtros e paginação
   */
  static async listDiarists(params?: {
    skip?: number;
    limit?: number;
    status?: DiaristStatus;
    tipo?: DiaristType;
    search?: string;
  }) {
    return listDiaristsApiV1OperacionalDiaristasGet(params);
  }

  /**
   * Busca diarista por ID
   */
  static async getDiarist(diaristId: string) {
    return getDiaristApiV1OperacionalDiaristasDiaristIdGet(diaristId);
  }

  /**
   * Busca diaristas disponíveis para uma data
   */
  static async getAvailableDiarists(params: {
    data: string;
    tipo?: DiaristType;
  }) {
    return getAvailableDiaristsApiV1OperacionalDiaristasAvailableGet(params);
  }

  /**
   * Consulta CPF na base interna e externa
   */
  static async consultaCpf(cpf: string) {
    return consultaCpfApiV1OperacionalDiaristasConsultaCpfCpfGet(cpf);
  }

  /**
   * Lista alocações com filtros
   */
  static async listAssignments(params?: {
    diaristId?: string;
    status?: AssignmentStatus;
    skip?: number;
    limit?: number;
  }) {
    return listAssignmentsApiV1OperacionalDiaristasAssignmentsGet(
      params ? {
        diarist_id: params.diaristId,
        status: params.status,
        skip: params.skip,
        limit: params.limit,
      } : undefined
    );
  }

  /**
   * Busca alocação por ID
   */
  static async getAssignment(assignmentId: string) {
    return getAssignmentApiV1OperacionalDiaristasAssignmentsAssignmentIdGet(assignmentId);
  }

  /**
   * Lista agendamentos com filtros
   */
  static async listSchedules(params?: {
    diaristId?: string;
    dataInicio?: string;
    dataFim?: string;
    status?: ScheduleStatus;
    skip?: number;
    limit?: number;
  }) {
    return listSchedulesApiV1OperacionalDiaristasSchedulesGet(
      params ? {
        diarist_id: params.diaristId,
        data_inicio: params.dataInicio,
        data_fim: params.dataFim,
        status: params.status,
        skip: params.skip,
        limit: params.limit,
      } : undefined
    );
  }

  /**
   * Busca agendamento por ID
   */
  static async getSchedule(scheduleId: string) {
    return getScheduleApiV1OperacionalDiaristasSchedulesScheduleIdGet(scheduleId);
  }

  /**
   * Busca agendamentos de hoje
   */
  static async getTodaySchedules() {
    return getTodaySchedulesApiV1OperacionalDiaristasSchedulesTodayGet();
  }

  /**
   * Lista pagamentos com filtros
   */
  static async listPayments(params?: {
    diaristId?: string;
    status?: PaymentStatus;
    dataInicio?: string;
    dataFim?: string;
    skip?: number;
    limit?: number;
  }) {
    return listPaymentsApiV1OperacionalDiaristasPaymentsGet(
      params ? {
        diarist_id: params.diaristId,
        status: params.status,
        data_inicio: params.dataInicio,
        data_fim: params.dataFim,
        skip: params.skip,
        limit: params.limit,
      } : undefined
    );
  }

  /**
   * Busca pagamento por ID
   */
  static async getPayment(paymentId: string) {
    return getPaymentApiV1OperacionalDiaristasPaymentsPaymentIdGet(paymentId);
  }

  /**
   * Lista pagamentos pendentes
   */
  static async getPendingPayments() {
    return getPendingPaymentsApiV1OperacionalDiaristasPaymentsPendingGet();
  }

  /**
   * Gera relatório de folha de pagamento
   */
  static async getPayrollReport(competencia: string, condominioId?: string) {
    return getPayrollReportApiV1OperacionalDiaristasPaymentsPayrollReportGet({
      competencia,
      condominio_id: condominioId,
    });
  }

  /**
   * Lista avaliações com filtros
   */
  static async listEvaluations(params?: {
    diaristId?: string;
    notaMinima?: number;
    skip?: number;
    limit?: number;
  }) {
    return listEvaluationsApiV1OperacionalDiaristasEvaluationsGet(
      params ? {
        diarist_id: params.diaristId,
        nota_minima: params.notaMinima,
        skip: params.skip,
        limit: params.limit,
      } : undefined
    );
  }

  /**
   * Busca avaliação por ID
   */
  static async getEvaluation(evaluationId: string) {
    return getEvaluationApiV1OperacionalDiaristasEvaluationsEvaluationIdGet(evaluationId);
  }

  /**
   * Retorna estatísticas gerais
   */
  static async getGeneralStatistics(params?: {
    dataInicio?: string;
    dataFim?: string;
  }) {
    return getGeneralStatisticsApiV1OperacionalDiaristasStatisticsGeneralGet(
      params ? {
        data_inicio: params.dataInicio,
        data_fim: params.dataFim,
      } : undefined
    );
  }

  /**
   * Retorna ranking das melhores diaristas
   */
  static async getTopDiarists(limit?: number) {
    return getTopDiaristsApiV1OperacionalDiaristasStatisticsRankingGet({ limit });
  }

  /**
   * Retorna métricas de uma diarista
   */
  static async getDiaristMetrics(diaristId: string, params?: {
    dataInicio?: string;
    dataFim?: string;
  }) {
    return getDiaristMetricsApiV1OperacionalDiaristasDiaristIdMetricsGet(
      diaristId,
      params ? {
        data_inicio: params.dataInicio,
        data_fim: params.dataFim,
      } : undefined
    );
  }

  /**
   * Sugere diaristas usando IA
   */
  static async suggestDiarists(params: {
    data: string;
    tipo?: DiaristType;
    duracaoHoras?: number;
    priorizarConhecidas?: boolean;
  }) {
    return suggestDiaristsApiV1OperacionalDiaristasAiSuggestGet({
      data: params.data,
      tipo: params.tipo,
      duracao_horas: params.duracaoHoras,
      priorizar_conhecidas: params.priorizarConhecidas,
    });
  }

  /**
   * Analisa disponibilidade em período
   */
  static async analyzeAvailability(params: {
    dataInicio: string;
    dataFim: string;
    tipo?: DiaristType;
  }) {
    return analyzeAvailabilityApiV1OperacionalDiaristasAiAvailabilityGet({
      data_inicio: params.dataInicio,
      data_fim: params.dataFim,
      tipo: params.tipo,
    });
  }

  /**
   * Analisa performance de diarista
   */
  static async analyzePerformance(diaristId: string, params?: {
    dataInicio?: string;
    dataFim?: string;
  }) {
    return analyzePerformanceApiV1OperacionalDiaristasAiPerformanceDiaristIdGet(
      diaristId,
      params ? {
        data_inicio: params.dataInicio,
        data_fim: params.dataFim,
      } : undefined
    );
  }

  /**
   * Otimiza agendamentos usando IA
   */
  static async optimizeSchedule(params: {
    dataInicio: string;
    dataFim: string;
    budget?: number;
  }) {
    return optimizeScheduleApiV1OperacionalDiaristasAiOptimizeGet({
      data_inicio: params.dataInicio,
      data_fim: params.dataFim,
      budget: params.budget,
    });
  }
}

export const diaristCoreService = DiaristCoreService;
