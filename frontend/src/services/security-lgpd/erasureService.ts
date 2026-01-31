/**
 * Data Erasure Service
 * Direito ao Esquecimento LGPD (Art. 18)
 *
 * Serviço para gestão de solicitações de exclusão de dados:
 * - Solicitação de exclusão (Art. 18, VI)
 * - Consulta de status
 * - Gestão de escopo de exclusão
 */

import { getLgpdDireitoAoEsquecimento } from '@/types/generated/security-lgpd/lgpd-direito-ao-esquecimento/lgpd-direito-ao-esquecimento';
import type {
  ErasureRequestSchema,
  ErasureRequestSchemaScope,
  StandardResponse,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';
import { AxiosResponse } from 'axios';

const erasureApi = getLgpdDireitoAoEsquecimento();

/**
 * Service para direito ao esquecimento LGPD
 */
export class ErasureService {
  /**
   * Solicita exclusão de dados do titular
   * Conforme Art. 18, VI da LGPD
   */
  static async requestErasure(
    request: ErasureRequestSchema
  ): Promise<AxiosResponse<StandardResponse>> {
    return erasureApi.requestErasure(request);
  }

  /**
   * Consulta status de solicitação de exclusão
   * @param requestId ID da solicitação
   */
  static async getErasureStatus(
    requestId: string
  ): Promise<AxiosResponse<StandardResponse>> {
    return erasureApi.getErasureStatus(requestId);
  }

  /**
   * Solicita exclusão total de dados
   * Remove todos os dados do titular
   */
  static async requestFullErasure(
    titularId: string,
    titularEmail: string,
    reason: string
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.requestErasure({
      titular_id: titularId,
      titular_email: titularEmail,
      reason,
      scope: 'all',
    });
  }

  /**
   * Solicita exclusão apenas de dados pessoais
   * Mantém dados transacionais anonimizados
   */
  static async requestPersonalDataErasure(
    titularId: string,
    titularEmail: string,
    reason: string
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.requestErasure({
      titular_id: titularId,
      titular_email: titularEmail,
      reason,
      scope: 'personal',
    });
  }

  /**
   * Solicita exclusão de dados transacionais
   * Mantém apenas dados necessários para compliance
   */
  static async requestTransactionalErasure(
    titularId: string,
    titularEmail: string,
    reason: string
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.requestErasure({
      titular_id: titularId,
      titular_email: titularEmail,
      reason,
      scope: 'transactional',
    });
  }

  /**
   * Formata escopo de exclusão para exibição
   */
  static formatScope(scope: ErasureRequestSchemaScope): string {
    const formats: Record<ErasureRequestSchemaScope, string> = {
      all: 'Todos os Dados',
      personal: 'Apenas Dados Pessoais',
      transactional: 'Apenas Dados Transacionais',
    };
    return formats[scope];
  }

  /**
   * Retorna descrição do escopo
   */
  static getScopeDescription(scope: ErasureRequestSchemaScope): string {
    const descriptions: Record<ErasureRequestSchemaScope, string> = {
      all: 'Remove todos os dados do titular, incluindo histórico e transações.',
      personal:
        'Remove dados de identificação pessoal, mantendo transações anonimizadas.',
      transactional:
        'Remove dados transacionais, mantendo apenas dados necessários para compliance.',
    };
    return descriptions[scope];
  }

  /**
   * Valida motivo de exclusão
   */
  static validateReason(reason: string): {
    valid: boolean;
    message?: string;
  } {
    if (!reason || reason.trim().length < 10) {
      return {
        valid: false,
        message: 'Motivo deve ter no mínimo 10 caracteres',
      };
    }

    if (reason.length > 500) {
      return {
        valid: false,
        message: 'Motivo deve ter no máximo 500 caracteres',
      };
    }

    return { valid: true };
  }

  /**
   * Formata status da solicitação
   */
  static formatStatus(status: string): string {
    const formats: Record<string, string> = {
      pending: 'Pendente',
      in_progress: 'Em Andamento',
      completed: 'Concluída',
      failed: 'Falhou',
      cancelled: 'Cancelada',
    };
    return formats[status] || status;
  }

  /**
   * Retorna cor do badge de status
   */
  static getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      pending: 'yellow',
      in_progress: 'blue',
      completed: 'green',
      failed: 'red',
      cancelled: 'gray',
    };
    return colors[status] || 'gray';
  }

  /**
   * Calcula tempo estimado para conclusão
   */
  static getEstimatedCompletionTime(scope: ErasureRequestSchemaScope): string {
    const times: Record<ErasureRequestSchemaScope, string> = {
      all: '5-7 dias úteis',
      personal: '2-3 dias úteis',
      transactional: '3-5 dias úteis',
    };
    return times[scope];
  }

  /**
   * Verifica se pode cancelar solicitação
   */
  static canCancel(status: string): boolean {
    return ['pending', 'in_progress'].includes(status);
  }

  /**
   * Lista motivos comuns de exclusão
   */
  static getCommonReasons(): Array<{ value: string; label: string }> {
    return [
      {
        value: 'Não utilizo mais os serviços',
        label: 'Não utilizo mais os serviços',
      },
      {
        value: 'Preocupação com privacidade',
        label: 'Preocupação com privacidade',
      },
      {
        value: 'Migração para outra plataforma',
        label: 'Migração para outra plataforma',
      },
      {
        value: 'Exercício do direito LGPD Art. 18',
        label: 'Exercício do direito LGPD Art. 18',
      },
      { value: 'Dados incorretos ou desatualizados', label: 'Dados incorretos ou desatualizados' },
      { value: 'outro', label: 'Outro motivo' },
    ];
  }

  /**
   * Gera aviso de impacto da exclusão
   */
  static getImpactWarning(scope: ErasureRequestSchemaScope): string[] {
    const warnings: Record<ErasureRequestSchemaScope, string[]> = {
      all: [
        'Sua conta será permanentemente excluída',
        'Todos os dados pessoais serão removidos',
        'Histórico de transações será apagado',
        'Acesso aos serviços será revogado',
        'Esta ação é IRREVERSÍVEL',
      ],
      personal: [
        'Dados de identificação serão removidos',
        'Transações serão anonimizadas',
        'Você não poderá acessar a conta após a exclusão',
        'Histórico será mantido de forma anônima para compliance',
      ],
      transactional: [
        'Dados transacionais serão removidos',
        'Dados pessoais básicos serão mantidos',
        'Histórico financeiro será apagado',
        'Relatórios anteriores não estarão mais disponíveis',
      ],
    };

    return warnings[scope];
  }
}

export default ErasureService;
