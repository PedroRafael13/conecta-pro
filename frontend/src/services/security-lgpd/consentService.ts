/**
 * Consent Management Service
 * Gestão de Consentimentos LGPD (Art. 7, 8, 9)
 *
 * Serviço para gerenciamento completo de consentimentos:
 * - Registro de consentimento
 * - Consulta de consentimentos por titular
 * - Revogação de consentimento
 * - Listagem de finalidades
 * - Listagem de bases legais
 */

import { registerConsent as registerConsentApi, getConsents as getConsentsApi, revokeConsent as revokeConsentApi, listPurposes as listPurposesApi, listLegalBases as listLegalBasesApi } from '@/types/generated/security-lgpd/lgpd-consentimento/lgpd-consentimento';
import type {
  ConsentRequest,
  RevokeConsentParams,
  StandardResponse,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';


/**
 * Service para gestão de consentimentos LGPD
 */
export class ConsentService {
  /**
   * Registra novo consentimento do titular
   * Conforme Art. 7 da LGPD
   */
  static async registerConsent(
    request: ConsentRequest
  ): Promise<StandardResponse> {
    return registerConsentApi(request);
  }

  /**
   * Consulta todos os consentimentos de um titular
   * @param titularId UUID do titular dos dados
   */
  static async getConsents(
    titularId: string
  ): Promise<StandardResponse> {
    return getConsentsApi(titularId);
  }

  /**
   * Revoga um consentimento específico
   * @param consentId ID do consentimento
   * @param reason Motivo da revogação (mínimo 5 caracteres)
   */
  static async revokeConsent(
    consentId: string,
    reason: string
  ): Promise<StandardResponse> {
    const params: RevokeConsentParams = { reason };
    return revokeConsentApi(consentId, params);
  }

  /**
   * Lista finalidades de consentimento disponíveis
   */
  static async listPurposes(): Promise<StandardResponse> {
    return listPurposesApi();
  }

  /**
   * Lista bases legais LGPD disponíveis
   * Art. 7 a 11 da LGPD
   */
  static async listLegalBases(): Promise<StandardResponse> {
    return listLegalBasesApi();
  }

  /**
   * Valida se um consentimento está ativo
   * Helper para verificação rápida no frontend
   */
  static isConsentActive(consent: any): boolean {
    if (!consent) return false;

    const now = new Date();
    const expiresAt = consent.expires_at ? new Date(consent.expires_at) : null;

    return (
      consent.active === true &&
      consent.revoked === false &&
      (!expiresAt || expiresAt > now)
    );
  }

  /**
   * Calcula dias restantes até expiração
   */
  static getDaysUntilExpiration(expiresAt: string): number {
    const expires = new Date(expiresAt);
    const now = new Date();
    const diff = expires.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }

  /**
   * Formata base legal para exibição
   */
  static formatLegalBasis(basis: string): string {
    const formats: Record<string, string> = {
      'consent': 'Consentimento do Titular (Art. 7, I)',
      'legal_obligation': 'Cumprimento de Obrigação Legal (Art. 7, II)',
      'public_administration': 'Administração Pública (Art. 7, III)',
      'research': 'Estudos por Órgão de Pesquisa (Art. 7, IV)',
      'contract': 'Execução de Contrato (Art. 7, V)',
      'judicial_process': 'Processo Judicial (Art. 7, VI)',
      'life_protection': 'Proteção da Vida (Art. 7, VII)',
      'health_protection': 'Proteção à Saúde (Art. 7, VIII)',
      'legitimate_interest': 'Interesse Legítimo (Art. 7, IX)',
      'credit_protection': 'Proteção ao Crédito (Art. 7, X)',
    };

    return formats[basis] || basis;
  }

  /**
   * Formata finalidade para exibição
   */
  static formatPurpose(purpose: string): string {
    const formats: Record<string, string> = {
      'user_registration': 'Cadastro de Usuário',
      'service_provision': 'Prestação de Serviços',
      'marketing': 'Marketing e Publicidade',
      'analytics': 'Análise e Estatísticas',
      'security': 'Segurança da Informação',
      'legal_compliance': 'Compliance Legal',
      'communication': 'Comunicação com o Titular',
      'contract_execution': 'Execução de Contrato',
      'operational': 'Operações do Sistema',
    };

    return formats[purpose] || purpose;
  }
}

export default ConsentService;
