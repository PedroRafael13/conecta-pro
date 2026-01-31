/**
 * React Query Hooks para Bartolo AI Assistant
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { BartoloService } from '@/services/ai/bartolo.service';
import type {
  SendMessageRequest,
  SendMessageResponse,
  FeedbackRequest,
  WizardStartRequest,
  WizardInputRequest,
} from '@/types/generated/ai/conectaPROAIBartoloAPI.schemas';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'sonner';

// ==========================================
// Query Keys
// ==========================================

export const bartoloKeys = {
  all: ['bartolo'] as const,
  greeting: (userId: number, sessionId: string) =>
    [...bartoloKeys.all, 'greeting', userId, sessionId] as const,
  wizards: () => [...bartoloKeys.all, 'wizards'] as const,
  wizardStatus: (userId: number, wizardId: string) =>
    [...bartoloKeys.all, 'wizard-status', userId, wizardId] as const,
  modules: () => [...bartoloKeys.all, 'modules'] as const,
  moduleDetails: (moduleId: string) =>
    [...bartoloKeys.all, 'module', moduleId] as const,
  stats: () => [...bartoloKeys.all, 'stats'] as const,
  learningStats: () => [...bartoloKeys.all, 'learning-stats'] as const,
  learningPatterns: () => [...bartoloKeys.all, 'learning-patterns'] as const,
  health: () => [...bartoloKeys.all, 'health'] as const,
};

// ==========================================
// Queries
// ==========================================

/**
 * Hook para obter saudação personalizada do Bartolo
 */
export function useBartoloGreeting(sessionId: string, enabled = true) {
  const { user } = useAuth();
  const userId = Number(user?.id) || 0;

  return useQuery({
    queryKey: bartoloKeys.greeting(userId, sessionId),
    queryFn: () => BartoloService.getGreeting(userId, sessionId),
    enabled: enabled && !!user?.id,
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

/**
 * Hook para listar wizards disponíveis
 */
export function useBartoloWizards(enabled = true) {
  return useQuery({
    queryKey: bartoloKeys.wizards(),
    queryFn: () => BartoloService.listWizards(),
    enabled,
    staleTime: 1000 * 60 * 60, // 1 hora (wizards são estáticos)
  });
}

/**
 * Hook para obter status de wizard em andamento
 */
export function useWizardStatus(wizardId: string, enabled = true) {
  const { user } = useAuth();
  const userId = Number(user?.id) || 0;

  return useQuery({
    queryKey: bartoloKeys.wizardStatus(userId, wizardId),
    queryFn: () => BartoloService.getWizardStatus(userId, wizardId),
    enabled: enabled && !!user?.id && !!wizardId,
    refetchInterval: 2000, // Poll a cada 2 segundos quando wizard ativo
  });
}

/**
 * Hook para listar módulos do sistema
 */
export function useBartoloModules(enabled = true) {
  return useQuery({
    queryKey: bartoloKeys.modules(),
    queryFn: () => BartoloService.listModules(),
    enabled,
    staleTime: 1000 * 60 * 60, // 1 hora
  });
}

/**
 * Hook para obter detalhes de um módulo
 */
export function useModuleDetails(moduleId: string, enabled = true) {
  return useQuery({
    queryKey: bartoloKeys.moduleDetails(moduleId),
    queryFn: () => BartoloService.getModuleDetails(moduleId),
    enabled: enabled && !!moduleId,
    staleTime: 1000 * 60 * 30, // 30 minutos
  });
}

/**
 * Hook para obter estatísticas gerais do Bartolo
 */
export function useBartoloStats(enabled = true) {
  return useQuery({
    queryKey: bartoloKeys.stats(),
    queryFn: () => BartoloService.getStats(),
    enabled,
    staleTime: 1000 * 60 * 5, // 5 minutos
    refetchInterval: 1000 * 60 * 5, // Atualiza a cada 5 minutos
  });
}

/**
 * Hook para obter estatísticas de aprendizado
 */
export function useBartoloLearningStats(enabled = true) {
  return useQuery({
    queryKey: bartoloKeys.learningStats(),
    queryFn: () => BartoloService.getLearningStats(),
    enabled,
    staleTime: 1000 * 60 * 10, // 10 minutos
  });
}

/**
 * Hook para obter padrões aprendidos
 */
export function useBartoloLearningPatterns(enabled = true) {
  return useQuery({
    queryKey: bartoloKeys.learningPatterns(),
    queryFn: () => BartoloService.getLearnedPatterns(),
    enabled,
    staleTime: 1000 * 60 * 10, // 10 minutos
  });
}

/**
 * Hook para health check do Bartolo
 */
export function useBartoloHealth(enabled = true) {
  return useQuery({
    queryKey: bartoloKeys.health(),
    queryFn: () => BartoloService.checkHealth(),
    enabled,
    staleTime: 1000 * 30, // 30 segundos
    refetchInterval: 1000 * 60, // Verifica a cada 1 minuto
    retry: 3,
  });
}

// ==========================================
// Mutations
// ==========================================

/**
 * Hook para enviar mensagem ao Bartolo
 */
export function useSendMessage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = Number(user?.id) || 0;

  return useMutation({
    mutationFn: (request: SendMessageRequest) =>
      BartoloService.sendMessage(userId, request),
    onSuccess: (data) => {
      // Registra mensagem no cache se necessário
      // Pode ser usado para histórico de conversa
    },
    onError: (error: any) => {
      toast.error('Erro ao enviar mensagem', {
        description: error?.message || 'Tente novamente',
      });
    },
  });
}

/**
 * Hook para enviar feedback sobre resposta do Bartolo
 */
export function useSubmitFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (feedback: FeedbackRequest) =>
      BartoloService.submitFeedback(feedback),
    onSuccess: () => {
      toast.success('Feedback enviado com sucesso');
      // Invalida stats para atualizar
      queryClient.invalidateQueries({ queryKey: bartoloKeys.learningStats() });
    },
    onError: (error: any) => {
      toast.error('Erro ao enviar feedback', {
        description: error?.message || 'Tente novamente',
      });
    },
  });
}

/**
 * Hook para iniciar wizard
 */
export function useStartWizard() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = Number(user?.id) || 0;

  return useMutation({
    mutationFn: (request: WizardStartRequest) =>
      BartoloService.startWizard(userId, request),
    onSuccess: () => {
      toast.success('Wizard iniciado');
      // Invalida wizards para atualizar lista
      queryClient.invalidateQueries({ queryKey: bartoloKeys.wizards() });
    },
    onError: (error: any) => {
      toast.error('Erro ao iniciar wizard', {
        description: error?.message || 'Tente novamente',
      });
    },
  });
}

/**
 * Hook para enviar input ao wizard
 */
export function useSendWizardInput() {
  const { user } = useAuth();
  const userId = Number(user?.id) || 0;

  return useMutation({
    mutationFn: (request: WizardInputRequest) =>
      BartoloService.sendWizardInput(userId, request),
    onError: (error: any) => {
      toast.error('Erro ao processar input', {
        description: error?.message || 'Tente novamente',
      });
    },
  });
}

/**
 * Hook para cancelar wizard
 */
export function useCancelWizard() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = Number(user?.id) || 0;

  return useMutation({
    mutationFn: (wizardId: string) =>
      BartoloService.cancelWizard(userId, wizardId),
    onSuccess: () => {
      toast.success('Wizard cancelado');
      queryClient.invalidateQueries({ queryKey: bartoloKeys.wizards() });
    },
    onError: (error: any) => {
      toast.error('Erro ao cancelar wizard', {
        description: error?.message || 'Tente novamente',
      });
    },
  });
}

// ==========================================
// Custom Hooks Compostos
// ==========================================

/**
 * Hook completo para chat com Bartolo
 * Combina mensagens, greeting e sugestões
 */
export function useBartoloChat(sessionId: string, module?: string) {
  const sendMessage = useSendMessage();
  const greeting = useBartoloGreeting(sessionId);
  const submitFeedback = useSubmitFeedback();

  const suggestions = module
    ? BartoloService.getSuggestionsForModule(module)
    : BartoloService.getSuggestionsForModule('default');

  return {
    // Queries
    greeting: greeting.data,
    isLoadingGreeting: greeting.isLoading,

    // Mutations
    sendMessage: sendMessage.mutate,
    sendMessageAsync: sendMessage.mutateAsync,
    isSending: sendMessage.isPending,
    lastResponse: sendMessage.data,

    // Feedback
    submitFeedback: submitFeedback.mutate,
    isSubmittingFeedback: submitFeedback.isPending,

    // Sugestões contextuais
    suggestions,

    // Session ID helper
    sessionId,
  };
}
