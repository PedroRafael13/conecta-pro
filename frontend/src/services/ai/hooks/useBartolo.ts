/**
 * React Query hooks for Bartolo AI Assistant
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { BartoloService } from '../bartolo.service';
import type {
  SendMessageRequest,
  FeedbackRequest,
  WizardStartRequest,
  WizardInputRequest,
} from '@/types/generated/ai/conectaPROAIBartoloAPI.schemas';

/**
 * Hook para enviar mensagem ao Bartolo
 */
export function useSendMessage() {
  return useMutation({
    mutationFn: ({
      userId,
      request,
    }: {
      userId: number;
      request: SendMessageRequest;
    }) => BartoloService.sendMessage(userId, request),
  });
}

/**
 * Hook para obter saudação do Bartolo
 */
export function useBartoloGreeting(userId: number, sessionId: string) {
  return useQuery({
    queryKey: ['bartolo', 'greeting', userId, sessionId],
    queryFn: () => BartoloService.getGreeting(userId, sessionId),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para enviar feedback
 */
export function useSubmitFeedback() {
  return useMutation({
    mutationFn: (feedback: FeedbackRequest) =>
      BartoloService.submitFeedback(feedback),
  });
}

/**
 * Hook para iniciar wizard
 */
export function useStartWizard() {
  return useMutation({
    mutationFn: ({
      userId,
      request,
    }: {
      userId: number;
      request: WizardStartRequest;
    }) => BartoloService.startWizard(userId, request),
  });
}

/**
 * Hook para enviar input ao wizard
 */
export function useSendWizardInput() {
  return useMutation({
    mutationFn: ({
      userId,
      request,
    }: {
      userId: number;
      request: WizardInputRequest;
    }) => BartoloService.sendWizardInput(userId, request),
  });
}

/**
 * Hook para verificar status do wizard
 */
export function useWizardStatus(userId: number, wizardId: string) {
  return useQuery({
    queryKey: ['bartolo', 'wizard', 'status', wizardId],
    queryFn: () => BartoloService.getWizardStatus(userId, wizardId),
    refetchInterval: 2000, // Poll a cada 2 segundos
    enabled: !!wizardId,
  });
}

/**
 * Hook para cancelar wizard
 */
export function useCancelWizard() {
  return useMutation({
    mutationFn: ({ userId, wizardId }: { userId: number; wizardId: string }) =>
      BartoloService.cancelWizard(userId, wizardId),
  });
}

/**
 * Hook para obter padrões aprendidos
 */
export function useLearnedPatterns() {
  return useQuery({
    queryKey: ['bartolo', 'learning', 'patterns'],
    queryFn: () => BartoloService.getLearnedPatterns(),
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para obter estatísticas de aprendizado
 */
export function useLearningStats() {
  return useQuery({
    queryKey: ['bartolo', 'learning', 'stats'],
    queryFn: () => BartoloService.getLearningStats(),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para verificar saúde do Bartolo
 */
export function useBartoloHealth() {
  return useQuery({
    queryKey: ['bartolo', 'health'],
    queryFn: () => BartoloService.checkHealth(),
    refetchInterval: 30000, // 30 segundos
  });
}
