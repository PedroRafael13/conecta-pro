/**
 * Service Layer - DIARISTS Notifications
 *
 * Gerenciamento de notificações para diaristas:
 * - Envio manual e automático
 * - Lembretes e alertas
 * - Templates e canais
 * - Estatísticas
 */

// TODO: Implementar quando funções estiverem disponíveis na API
const getListarNotificacoes = async (...args: any[]): Promise<any> => { throw new Error('TODO: Implementar getListarNotificacoes'); };
const getListarNotificacoesDiarista = async (...args: any[]): Promise<any> => { throw new Error('TODO: Implementar getListarNotificacoesDiarista'); };
const getGetEstatisticas = async (...args: any[]): Promise<any> => { throw new Error('TODO: Implementar getGetEstatisticas'); };
const getListarTemplates = async (...args: any[]): Promise<any> => { throw new Error('TODO: Implementar getListarTemplates'); };
const getGetTemplate = async (...args: any[]): Promise<any> => { throw new Error('TODO: Implementar getGetTemplate'); };
const getListarCanais = async (...args: any[]): Promise<any> => { throw new Error('TODO: Implementar getListarCanais'); };

import type {
  TipoNotificacao,
  CanalNotificacao,
  StatusNotificacao,
} from '@/api/diarists/generated/models';

/**
 * Service: Diarist Notifications
 *
 * Operações de notificação para diaristas.
 */
export class DiaristNotificationService {
  /**
   * Lista notificações com filtros
   */
  static async listNotifications(params?: {
    diaristId?: string;
    tipo?: TipoNotificacao;
    status?: StatusNotificacao;
    limit?: number;
  }) {
    return getListarNotificacoes(params);
  }

  /**
   * Lista notificações de um diarista específico
   */
  static async getDiaristNotifications(diaristId: string, limit?: number) {
    return getListarNotificacoesDiarista(diaristId, { limit });
  }

  /**
   * Retorna estatísticas de notificações
   */
  static async getStatistics(params?: {
    dataInicio?: string;
    dataFim?: string;
  }) {
    return getGetEstatisticas(params);
  }

  /**
   * Lista templates disponíveis
   */
  static async listTemplates() {
    return getListarTemplates();
  }

  /**
   * Retorna template específico
   */
  static async getTemplate(tipo: TipoNotificacao) {
    return getGetTemplate(tipo);
  }

  /**
   * Lista canais de notificação disponíveis
   */
  static async listChannels() {
    return getListarCanais();
  }
}

export const diaristNotificationService = DiaristNotificationService;
