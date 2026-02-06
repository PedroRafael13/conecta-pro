/**
 * Interviews Hooks - Gestão de Entrevistas
 *
 * Re-exports dos hooks Orval do módulo recruitment
 */

import { useQuery } from '@tanstack/react-query';
import {
  getListInterviewsApiV1RecruitmentInterviewsGetQueryOptions,
  getGetInterviewApiV1RecruitmentInterviewsInterviewIdGetQueryOptions,
  getListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetQueryOptions,
  getListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetQueryOptions,
  getGetInterviewStatsApiV1RecruitmentInterviewsStatsGetQueryOptions,
  getGetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetQueryOptions,
  getGetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetQueryOptions,
  getGetSuggestedQuestionsApiV1RecruitmentInterviewsInterviewIdQuestionsGetQueryOptions,
  useCreateInterviewApiV1RecruitmentInterviewsPost,
  useUpdateInterviewApiV1RecruitmentInterviewsInterviewIdPut,
  useDeleteInterviewApiV1RecruitmentInterviewsInterviewIdDelete,
  useRescheduleInterviewApiV1RecruitmentInterviewsInterviewIdReschedulePost,
  useCancelInterviewApiV1RecruitmentInterviewsInterviewIdCancelPost,
  useCompleteInterviewApiV1RecruitmentInterviewsInterviewIdCompletePost,
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';
import type {
  ListInterviewsApiV1RecruitmentInterviewsGetParams,
  ListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetParams,
  ListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetParams,
  GetInterviewStatsApiV1RecruitmentInterviewsStatsGetParams,
  GetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetParams,
  GetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetParams,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';

// List & Read
export const useInterviews = (params?: ListInterviewsApiV1RecruitmentInterviewsGetParams) =>
  useQuery(getListInterviewsApiV1RecruitmentInterviewsGetQueryOptions(params));

export const useInterview = (interviewId: string) =>
  useQuery(getGetInterviewApiV1RecruitmentInterviewsInterviewIdGetQueryOptions(interviewId));

export const useInterviewsByApplication = (applicationId: string, params?: ListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetParams) =>
  useQuery(getListByApplicationApiV1RecruitmentInterviewsApplicationApplicationIdGetQueryOptions(applicationId, params));

export const useInterviewsByDateRange = (params: ListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetParams) =>
  useQuery(getListByDateRangeApiV1RecruitmentInterviewsByDateRangeGetQueryOptions(params));

export const useInterviewStats = (params?: GetInterviewStatsApiV1RecruitmentInterviewsStatsGetParams) =>
  useQuery(getGetInterviewStatsApiV1RecruitmentInterviewsStatsGetQueryOptions(params));

export const useAvailableSlots = (params: GetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetParams) =>
  useQuery(getGetAvailableSlotsApiV1RecruitmentInterviewsAvailableSlotsGetQueryOptions(params));

export const useInterviewCalendar = (interviewerId: string, params: GetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetParams) =>
  useQuery(getGetCalendarApiV1RecruitmentInterviewsCalendarInterviewerIdGetQueryOptions(interviewerId, params));

export const useSuggestedQuestions = (interviewId: string) =>
  useQuery(getGetSuggestedQuestionsApiV1RecruitmentInterviewsInterviewIdQuestionsGetQueryOptions(interviewId));

// Mutations
export const useCreateInterview = useCreateInterviewApiV1RecruitmentInterviewsPost;
export const useUpdateInterview = useUpdateInterviewApiV1RecruitmentInterviewsInterviewIdPut;
export const useDeleteInterview = useDeleteInterviewApiV1RecruitmentInterviewsInterviewIdDelete;
export const useRescheduleInterview = useRescheduleInterviewApiV1RecruitmentInterviewsInterviewIdReschedulePost;
export const useCancelInterview = useCancelInterviewApiV1RecruitmentInterviewsInterviewIdCancelPost;
export const useCompleteInterview = useCompleteInterviewApiV1RecruitmentInterviewsInterviewIdCompletePost;

// Re-export types
export type {
  InterviewCreate,
  InterviewUpdate,
  InterviewResponse,
  InterviewReschedule,
  InterviewCancel,
  InterviewComplete,
  InterviewEvaluation,
  InterviewStats,
  InterviewSlot,
  InterviewCalendar,
  InterviewListResponse,
} from '@/types/generated/recruitment/conectaPROMóduloRECRUITMENT.schemas';
