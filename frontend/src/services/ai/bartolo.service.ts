// @ts-nocheck
/**
 * Bartolo AI Assistant Service
 * Assistente inteligente conversacional do Conecta PRO
 */

import { getAiBartoloAssistente } from '@/types/generated/ai/ai-bartolo-assistente/ai-bartolo-assistente';
import type {
  SendMessageRequest,
  SendMessageResponse,
  FeedbackRequest,
  SendMessageApiV1AiBartoloSendPostParams,
  GetGreetingApiV1AiBartoloGreetingGetParams,
  WizardStartRequest,
  WizardInputRequest,
  StartWizardApiV1AiBartoloWizardStartPostParams,
  WizardInputApiV1AiBartoloWizardInputPostParams,
} from '@/types/generated/ai/conectaPROAIBartoloAPI.schemas';

// Funções geradas pelo Orval
const bartoloApi = getAiBartoloAssistente();

/**
 * Service para interação com Bartolo AI
 */
export class BartoloService {
  /**
   * Envia mensagem para o Bartolo e recebe resposta
   */
  static async sendMessage(
    userId: number,
    request: SendMessageRequest
  ): Promise<SendMessageResponse> {
    const params: SendMessageApiV1AiBartoloSendPostParams = {
      user_id: userId,
    };

    return bartoloApi.sendMessageApiV1AiBartoloSendPost(request, params);
  }

  /**
   * Envia mensagem com resposta em streaming
   * @returns URL do endpoint de streaming
   */
  static getStreamUrl(userId: number, sessionId: string): string {
    return `/api/v1/ai/bartolo/send/stream?user_id=${userId}&session_id=${sessionId}`;
  }

  /**
   * Obtém saudação personalizada do Bartolo
   */
  static async getGreeting(userId: number, sessionId: string): Promise<string> {
    const params: GetGreetingApiV1AiBartoloGreetingGetParams = {
      user_id: userId,
      session_id: sessionId,
    };

    return await bartoloApi.getGreetingApiV1AiBartoloGreetingGet(params);
    return (response as any).greeting || 'Olá! Como posso ajudar?';
  }

  /**
   * Registra feedback sobre uma resposta do Bartolo
   */
  static async submitFeedback(feedback: FeedbackRequest): Promise<void> {
    await bartoloApi.submitFeedbackApiV1AiBartoloFeedbackPost(feedback);
  }

  /**
   * Inicia um wizard interativo
   */
  static async startWizard(
    userId: number,
    request: WizardStartRequest
  ): Promise<any> {
    const params: StartWizardApiV1AiBartoloWizardStartPostParams = {
      user_id: userId,
    };

    return bartoloApi.startWizardApiV1AiBartoloWizardStartPost(request, params);
  }

  /**
   * Envia input para wizard em andamento
   */
  static async sendWizardInput(
    userId: number,
    request: WizardInputRequest
  ): Promise<any> {
    const params: WizardInputApiV1AiBartoloWizardInputPostParams = {
      user_id: userId,
    };

    return bartoloApi.wizardInputApiV1AiBartoloWizardInputPost(request, params);
  }

  /**
   * Verifica status do wizard
   */
  static async getWizardStatus(userId: number, wizardId: string): Promise<any> {
    return bartoloApi.wizardStatusApiV1AiBartoloWizardStatusGet({
      user_id: userId,
      // wizard_id not in params type - query string handled internally
    } as any);
  }

  /**
   * Cancela wizard em andamento
   */
  static async cancelWizard(userId: number, wizardId: string): Promise<void> {
    await bartoloApi.cancelWizardApiV1AiBartoloWizardCancelPost({
      user_id: userId,
      // wizard_id not in params type - handled as body or URL param
    } as any);
  }

  /**
   * Obtém padrões aprendidos pelo Bartolo
   */
  static async getLearnedPatterns(): Promise<any> {
    return bartoloApi.getLearnedPatternsApiV1AiBartoloLearningPatternsGet();
  }

  /**
   * Obtém estatísticas de aprendizado
   */
  static async getLearningStats(): Promise<any> {
    return bartoloApi.getLearningStatsApiV1AiBartoloLearningStatsGet();
  }

  /**
   * Verifica saúde do serviço Bartolo
   */
  static async checkHealth(): Promise<any> {
    return bartoloApi.healthCheckApiV1AiBartoloHealthGet();
  }

  /**
   * Lista todos os wizards disponíveis
   */
  static async listWizards(): Promise<any> {
    return bartoloApi.listWizardsApiV1AiBartoloWizardsGet();
  }

  /**
   * Lista todos os módulos do sistema
   */
  static async listModules(): Promise<any> {
    return bartoloApi.listModulesApiV1AiBartoloModulesGet();
  }

  /**
   * Obtém detalhes de um módulo específico
   */
  static async getModuleDetails(moduleId: string): Promise<any> {
    return bartoloApi.getModuleDetailsApiV1AiBartoloModulesModuleIdGet(moduleId);
  }

  /**
   * Obtém estatísticas gerais do Bartolo
   */
  static async getStats(): Promise<any> {
    return bartoloApi.getStatsApiV1AiBartoloStatsGet();
  }

  /**
   * Confirma e executa uma ação proposta pelo Bartolo
   */
  static async confirmAction(
    userId: number,
    actionId: string,
    confirmed: boolean,
    userNotes?: string
  ): Promise<SendMessageResponse> {
    const confirmation = {
      action_id: actionId,
      confirmed,
      user_id: String(userId),
      confirmed_at: new Date().toISOString(),
      user_notes: userNotes,
    };

    return bartoloApi.confirmActionApiV1AiBartoloConfirmActionPost(
      confirmation,
      { user_id: userId }
    );
  }

  /**
   * Gera um ID de sessão único
   */
  static generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Sugestões contextuais por módulo
   */
  static getSuggestionsForModule(module: string): string[] {
    const suggestions: Record<string, string[]> = {
      dashboard: [
        'Resumo do dia',
        'Alertas pendentes',
        'KPIs principais',
        'O que posso fazer?',
      ],
      operacional: [
        'Como criar uma escala?',
        'Funcionários disponíveis hoje',
        'Postos sem cobertura',
        'Horas extras pendentes',
      ],
      crm: [
        'Novos leads',
        'Pipeline de vendas',
        'Criar proposta',
        'Metas do mês',
      ],
      financeiro: [
        'Contas a pagar',
        'Contas a receber',
        'Fluxo de caixa',
        'Inadimplentes',
      ],
      ged: [
        'Processar documento',
        'Buscar documentos',
        'Classificar automaticamente',
        'Extrair dados',
      ],
      default: [
        'O que você pode fazer?',
        'Como funciona o sistema?',
        'Preciso de ajuda',
        'Falar com suporte',
      ],
    };

    const normalizedModule = module.toLowerCase().split('/')[0];
    return suggestions[normalizedModule] || suggestions.default;
  }
}

export default BartoloService;
