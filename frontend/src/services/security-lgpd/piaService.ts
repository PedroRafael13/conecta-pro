/**
 * Privacy Impact Assessment (PIA/DPIA) Service
 * Avaliação de Impacto à Proteção de Dados (Art. 38 LGPD)
 *
 * Serviço para gestão de avaliações PIA/DPIA:
 * - Criação de avaliações de impacto
 * - Consulta de avaliações
 * - Gestão de categorias de risco
 * - Análise de conformidade
 */

import { getLgpdAvaliaçãoDeImpactoPiaDpia } from '@/types/generated/security-lgpd/lgpd-avaliação-de-impacto-pia-dpia/lgpd-avaliação-de-impacto-pia-dpia';
import type {
  PIARequest,
  StandardResponse,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';
import { AxiosResponse } from 'axios';

const piaApi = getLgpdAvaliaçãoDeImpactoPiaDpia();

/**
 * Service para avaliações de impacto PIA/DPIA
 */
export class PIAService {
  /**
   * Cria nova avaliação de impacto de privacidade
   * Conforme Art. 38 da LGPD
   */
  static async createPIA(
    request: PIARequest
  ): Promise<AxiosResponse<StandardResponse>> {
    return piaApi.createPIA(request);
  }

  /**
   * Consulta avaliação PIA/DPIA específica
   * @param assessmentId ID da avaliação
   */
  static async getPIA(
    assessmentId: string
  ): Promise<AxiosResponse<StandardResponse>> {
    return piaApi.getPIA(assessmentId);
  }

  /**
   * Lista categorias de risco disponíveis
   */
  static async listRiskCategories(): Promise<AxiosResponse<StandardResponse>> {
    return piaApi.listRiskCategories();
  }

  /**
   * Cria PIA simplificada para novo projeto
   */
  static async createSimplePIA(
    projectName: string,
    description: string,
    dataCategories: string[]
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.createPIA({
      project_name: projectName,
      description,
      data_categories: dataCategories,
    });
  }

  /**
   * Cria PIA completa com análise detalhada
   */
  static async createCompletePIA(
    projectName: string,
    description: string,
    dataCategories: string[],
    processingPurposes: string[],
    dataSubjects: string[],
    riskFactors: string[]
  ): Promise<AxiosResponse<StandardResponse>> {
    return this.createPIA({
      project_name: projectName,
      description,
      data_categories: dataCategories,
      processing_purposes: processingPurposes,
      data_subjects: dataSubjects,
      risk_factors: riskFactors,
    });
  }

  /**
   * Categorias de dados comuns
   */
  static getCommonDataCategories(): Array<{ value: string; label: string }> {
    return [
      { value: 'personal_identification', label: 'Dados de Identificação' },
      { value: 'contact', label: 'Dados de Contato' },
      { value: 'financial', label: 'Dados Financeiros' },
      { value: 'health', label: 'Dados de Saúde' },
      { value: 'location', label: 'Dados de Localização' },
      { value: 'biometric', label: 'Dados Biométricos' },
      { value: 'behavioral', label: 'Dados Comportamentais' },
      { value: 'professional', label: 'Dados Profissionais' },
      { value: 'education', label: 'Dados Educacionais' },
      { value: 'children', label: 'Dados de Crianças e Adolescentes' },
      { value: 'sensitive', label: 'Dados Sensíveis (Art. 5º, II)' },
    ];
  }

  /**
   * Finalidades de processamento comuns
   */
  static getCommonProcessingPurposes(): Array<{
    value: string;
    label: string;
  }> {
    return [
      { value: 'service_provision', label: 'Prestação de Serviços' },
      { value: 'contract_execution', label: 'Execução de Contrato' },
      { value: 'legal_compliance', label: 'Cumprimento de Obrigação Legal' },
      { value: 'marketing', label: 'Marketing e Comunicação' },
      { value: 'analytics', label: 'Análises e Estatísticas' },
      { value: 'security', label: 'Segurança da Informação' },
      { value: 'fraud_prevention', label: 'Prevenção de Fraudes' },
      { value: 'customer_support', label: 'Suporte ao Cliente' },
      { value: 'research', label: 'Pesquisa e Desenvolvimento' },
      { value: 'credit_analysis', label: 'Análise de Crédito' },
    ];
  }

  /**
   * Tipos de titulares comuns
   */
  static getCommonDataSubjects(): Array<{ value: string; label: string }> {
    return [
      { value: 'customers', label: 'Clientes' },
      { value: 'employees', label: 'Funcionários' },
      { value: 'suppliers', label: 'Fornecedores' },
      { value: 'partners', label: 'Parceiros' },
      { value: 'minors', label: 'Menores de Idade' },
      { value: 'patients', label: 'Pacientes' },
      { value: 'students', label: 'Estudantes' },
      { value: 'visitors', label: 'Visitantes' },
      { value: 'prospects', label: 'Prospects' },
    ];
  }

  /**
   * Fatores de risco comuns
   */
  static getCommonRiskFactors(): Array<{ value: string; label: string }> {
    return [
      { value: 'data_breach', label: 'Vazamento de Dados' },
      { value: 'unauthorized_access', label: 'Acesso Não Autorizado' },
      { value: 'data_loss', label: 'Perda de Dados' },
      { value: 'discrimination', label: 'Discriminação' },
      { value: 'identity_theft', label: 'Roubo de Identidade' },
      { value: 'financial_loss', label: 'Perda Financeira' },
      { value: 'reputation_damage', label: 'Dano à Reputação' },
      { value: 'privacy_violation', label: 'Violação de Privacidade' },
      { value: 'automated_decision', label: 'Decisões Automatizadas' },
      { value: 'third_party_sharing', label: 'Compartilhamento com Terceiros' },
      { value: 'international_transfer', label: 'Transferência Internacional' },
    ];
  }

  /**
   * Calcula nível de risco da avaliação
   */
  static calculateRiskLevel(assessment: any): 'low' | 'medium' | 'high' | 'critical' {
    let score = 0;

    // Dados sensíveis aumentam risco
    const sensitiveCategories = ['health', 'biometric', 'children', 'sensitive'];
    const hasSensitiveData = assessment.data_categories?.some((cat: string) =>
      sensitiveCategories.includes(cat)
    );
    if (hasSensitiveData) score += 3;

    // Múltiplos fatores de risco
    const riskCount = assessment.risk_factors?.length || 0;
    score += Math.min(riskCount, 5);

    // Múltiplos tipos de titulares
    const subjectsCount = assessment.data_subjects?.length || 0;
    if (subjectsCount > 5) score += 2;

    // Classificação
    if (score >= 8) return 'critical';
    if (score >= 5) return 'high';
    if (score >= 3) return 'medium';
    return 'low';
  }

  /**
   * Formata nível de risco
   */
  static formatRiskLevel(level: string): string {
    const formats: Record<string, string> = {
      low: 'Baixo',
      medium: 'Médio',
      high: 'Alto',
      critical: 'Crítico',
    };
    return formats[level] || level;
  }

  /**
   * Retorna cor do badge de risco
   */
  static getRiskColor(level: string): string {
    const colors: Record<string, string> = {
      low: 'green',
      medium: 'yellow',
      high: 'orange',
      critical: 'red',
    };
    return colors[level] || 'gray';
  }

  /**
   * Gera recomendações baseadas em risco
   */
  static getRecommendations(riskLevel: string): string[] {
    const recommendations: Record<string, string[]> = {
      critical: [
        'Implementar criptografia em repouso e trânsito',
        'Realizar auditoria de segurança completa',
        'Implementar controles de acesso rígidos',
        'Revisar e atualizar políticas de privacidade',
        'Considerar consulta com DPO',
        'Implementar monitoramento contínuo',
        'Documentar todas as medidas de segurança',
      ],
      high: [
        'Implementar criptografia de dados sensíveis',
        'Revisar controles de acesso',
        'Atualizar políticas de retenção',
        'Implementar logs de auditoria',
        'Treinar equipe em LGPD',
        'Revisar termos de consentimento',
      ],
      medium: [
        'Revisar medidas de segurança existentes',
        'Atualizar documentação de privacidade',
        'Implementar controles básicos',
        'Monitorar acessos a dados',
        'Atualizar políticas de backup',
      ],
      low: [
        'Manter medidas de segurança atuais',
        'Revisar periodicamente controles',
        'Documentar processos',
        'Manter equipe informada',
      ],
    };

    return recommendations[riskLevel] || [];
  }

  /**
   * Valida completude da avaliação
   */
  static validateAssessment(assessment: PIARequest): {
    valid: boolean;
    missing: string[];
  } {
    const missing: string[] = [];

    if (!assessment.project_name) missing.push('Nome do projeto');
    if (!assessment.description) missing.push('Descrição');
    if (!assessment.data_categories?.length) missing.push('Categorias de dados');
    if (!assessment.processing_purposes?.length) missing.push('Finalidades');
    if (!assessment.data_subjects?.length) missing.push('Tipos de titulares');
    if (!assessment.risk_factors?.length) missing.push('Fatores de risco');

    return {
      valid: missing.length === 0,
      missing,
    };
  }

  /**
   * Formata status da avaliação
   */
  static formatStatus(status: string): string {
    const formats: Record<string, string> = {
      draft: 'Rascunho',
      in_review: 'Em Revisão',
      approved: 'Aprovada',
      rejected: 'Rejeitada',
      requires_update: 'Requer Atualização',
    };
    return formats[status] || status;
  }
}

export default PIAService;
