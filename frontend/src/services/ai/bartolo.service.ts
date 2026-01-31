/**
 * Bartolo AI Assistant Service
 * Assistente inteligente conversacional do Conecta PRO
 *
 * @deprecated Este service usa APIs que não foram migradas para Orval
 * TODO: Migrar para hooks Orval quando API estiver documentada
 */

import { axiosInstance } from '@/lib/axios-instance';

// Types temporários até migração
interface SendMessageRequest {
  message: string;
  context?: Record<string, unknown>;
}

interface SendMessageResponse {
  response: string;
  suggestions?: string[];
}

interface FeedbackRequest {
  rating: number;
  comment?: string;
}

/**
 * Service para interação com Bartolo AI
 */
export class BartoloService {
  private static BASE_PATH = '/api/v1/ai/bartolo';

  /**
   * Envia mensagem para o Bartolo e recebe resposta
   */
  static async sendMessage(
    userId: number,
    request: SendMessageRequest
  ): Promise<SendMessageResponse> {
    const { data } = await axiosInstance.post<SendMessageResponse>(
      `${this.BASE_PATH}/send`,
      request,
      { params: { user_id: userId } }
    );
    return data;
  }

  /**
   * Envia mensagem com resposta em streaming
   * @returns URL do endpoint de streaming
   */
  static getStreamUrl(userId: number, sessionId: string): string {
    return `${this.BASE_PATH}/send/stream?user_id=${userId}&session_id=${sessionId}`;
  }

  /**
   * Obtém saudação personalizada do Bartolo
   */
  static async getGreeting(userId: number, sessionId: string): Promise<string> {
    const { data } = await axiosInstance.get<{ greeting: string }>(
      `${this.BASE_PATH}/greeting`,
      { params: { user_id: userId, session_id: sessionId } }
    );
    return data.greeting || 'Olá! Como posso ajudar?';
  }

  /**
   * Registra feedback sobre uma resposta do Bartolo
   */
  static async submitFeedback(feedback: FeedbackRequest): Promise<void> {
    await axiosInstance.post(`${this.BASE_PATH}/feedback`, feedback);
  }

  /**
   * Inicia um wizard interativo
   */
  static async startWizard(
    userId: number,
    request: Record<string, unknown>
  ): Promise<unknown> {
    const { data } = await axiosInstance.post(
      `${this.BASE_PATH}/wizard/start`,
      request,
      { params: { user_id: userId } }
    );
    return data;
  }

  /**
   * Envia input para wizard em andamento
   */
  static async sendWizardInput(
    userId: number,
    request: Record<string, unknown>
  ): Promise<unknown> {
    const { data } = await axiosInstance.post(
      `${this.BASE_PATH}/wizard/input`,
      request,
      { params: { user_id: userId } }
    );
    return data;
  }

  /**
   * Verifica status do wizard
   */
  static async getWizardStatus(userId: number, wizardId: string): Promise<unknown> {
    const { data } = await axiosInstance.get(
      `${this.BASE_PATH}/wizard/status`,
      { params: { user_id: userId, wizard_id: wizardId } }
    );
    return data;
  }

  /**
   * Cancela wizard em andamento
   */
  static async cancelWizard(userId: number, wizardId: string): Promise<void> {
    await axiosInstance.post(
      `${this.BASE_PATH}/wizard/cancel`,
      {},
      { params: { user_id: userId, wizard_id: wizardId } }
    );
  }

  /**
   * Obtém padrões aprendidos pelo Bartolo
   */
  static async getLearnedPatterns(): Promise<unknown> {
    const { data } = await axiosInstance.get(`${this.BASE_PATH}/learning/patterns`);
    return data;
  }

  /**
   * Obtém estatísticas de aprendizado
   */
  static async getLearningStats(): Promise<unknown> {
    const { data } = await axiosInstance.get(`${this.BASE_PATH}/learning/stats`);
    return data;
  }

  /**
   * Verifica saúde do serviço Bartolo
   */
  static async checkHealth(): Promise<unknown> {
    const { data } = await axiosInstance.get(`${this.BASE_PATH}/health`);
    return data;
  }

  /**
   * Lista todos os wizards disponíveis
   */
  static async listWizards(): Promise<unknown> {
    const { data } = await axiosInstance.get(`${this.BASE_PATH}/wizards`);
    return data;
  }

  /**
   * Lista todos os módulos do sistema
   */
  static async listModules(): Promise<unknown> {
    const { data} = await axiosInstance.get(`${this.BASE_PATH}/modules`);
    return data;
  }

  /**
   * Obtém detalhes de um módulo específico
   */
  static async getModuleDetails(moduleId: string): Promise<unknown> {
    const { data } = await axiosInstance.get(`${this.BASE_PATH}/modules/${moduleId}`);
    return data;
  }

  /**
   * Obtém estatísticas gerais do Bartolo
   */
  static async getStats(): Promise<unknown> {
    const { data } = await axiosInstance.get(`${this.BASE_PATH}/stats`);
    return data;
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

    const { data } = await axiosInstance.post<SendMessageResponse>(
      `${this.BASE_PATH}/confirm-action`,
      confirmation,
      { params: { user_id: userId } }
    );
    return data;
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
