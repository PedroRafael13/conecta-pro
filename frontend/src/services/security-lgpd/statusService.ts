/**
 * LGPD Status Service
 * Monitoramento de Status e Health Check do Módulo LGPD
 *
 * Serviço para verificação de status:
 * - Status geral do módulo LGPD
 * - Health check dos componentes
 * - Monitoramento de compliance
 */

import { getLgpdStatus } from '@/types/generated/security-lgpd/lgpd-status/lgpd-status';
import type {
  StandardResponse,
  HealthCheck200,
} from '@/types/generated/security-lgpd/conectaPROLGPDSecurityAPI.schemas';
import { AxiosResponse } from 'axios';

const statusApi = getLgpdStatus();

/**
 * Service para status e health check LGPD
 */
export class StatusService {
  /**
   * Obtém status completo do módulo LGPD
   * Retorna status de todos os componentes de segurança
   */
  static async getLGPDStatus(): Promise<AxiosResponse<StandardResponse>> {
    return statusApi.getLGPDStatus();
  }

  /**
   * Realiza health check do módulo
   * Verifica se o módulo está operacional
   */
  static async healthCheck(): Promise<AxiosResponse<HealthCheck200>> {
    return statusApi.healthCheck();
  }

  /**
   * Verifica se módulo está saudável
   * Helper para verificação rápida
   */
  static async isHealthy(): Promise<boolean> {
    try {
      const response = await this.healthCheck();
      return response.data.status === 'healthy';
    } catch (error) {
      return false;
    }
  }

  /**
   * Obtém status de componentes específicos
   */
  static async getComponentsStatus(): Promise<{
    consent: boolean;
    encryption: boolean;
    audit: boolean;
    masking: boolean;
    erasure: boolean;
    pia: boolean;
  }> {
    try {
      const response = await this.getLGPDStatus();
      const data = response.data.data as any;

      return {
        consent: data?.components?.consent?.status === 'operational',
        encryption: data?.components?.encryption?.status === 'operational',
        audit: data?.components?.audit?.status === 'operational',
        masking: data?.components?.masking?.status === 'operational',
        erasure: data?.components?.erasure?.status === 'operational',
        pia: data?.components?.pia?.status === 'operational',
      };
    } catch (error) {
      return {
        consent: false,
        encryption: false,
        audit: false,
        masking: false,
        erasure: false,
        pia: false,
      };
    }
  }

  /**
   * Calcula score de compliance LGPD
   */
  static calculateComplianceScore(statusData: any): number {
    if (!statusData || !statusData.components) return 0;

    const components = statusData.components;
    const totalComponents = Object.keys(components).length;
    let operationalCount = 0;

    Object.values(components).forEach((component: any) => {
      if (component?.status === 'operational') {
        operationalCount++;
      }
    });

    return Math.round((operationalCount / totalComponents) * 100);
  }

  /**
   * Formata status do componente
   */
  static formatComponentStatus(status: string): string {
    const formats: Record<string, string> = {
      operational: 'Operacional',
      degraded: 'Degradado',
      down: 'Inativo',
      maintenance: 'Manutenção',
      unknown: 'Desconhecido',
    };
    return formats[status] || status;
  }

  /**
   * Retorna cor do badge de status
   */
  static getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      operational: 'green',
      degraded: 'yellow',
      down: 'red',
      maintenance: 'blue',
      unknown: 'gray',
    };
    return colors[status] || 'gray';
  }

  /**
   * Retorna ícone do status
   */
  static getStatusIcon(status: string): string {
    const icons: Record<string, string> = {
      operational: '✓',
      degraded: '⚠',
      down: '✗',
      maintenance: '🔧',
      unknown: '?',
    };
    return icons[status] || '?';
  }

  /**
   * Verifica uptime do módulo
   */
  static calculateUptime(statusData: any): string {
    if (!statusData?.uptime_seconds) return 'N/A';

    const seconds = statusData.uptime_seconds;
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    }
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  /**
   * Formata última verificação
   */
  static formatLastCheck(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `${diffMins}min atrás`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h atrás`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d atrás`;
  }

  /**
   * Retorna nomes dos componentes
   */
  static getComponentNames(): Record<string, string> {
    return {
      consent: 'Gestão de Consentimentos',
      encryption: 'Criptografia',
      audit: 'Trilha de Auditoria',
      masking: 'Mascaramento de Dados',
      erasure: 'Direito ao Esquecimento',
      pia: 'Avaliação de Impacto (PIA/DPIA)',
    };
  }

  /**
   * Retorna descrição dos componentes
   */
  static getComponentDescriptions(): Record<string, string> {
    return {
      consent: 'Registro e gestão de consentimentos LGPD (Art. 7, 8, 9)',
      encryption: 'Criptografia de dados sensíveis (AES-256-GCM)',
      audit: 'Trilha de auditoria com hash chain (Art. 46)',
      masking: 'Mascaramento de PII (CPF, email, telefone)',
      erasure: 'Processamento de solicitações de exclusão (Art. 18)',
      pia: 'Avaliações de impacto à privacidade (Art. 38)',
    };
  }

  /**
   * Gera recomendações baseadas em status
   */
  static getRecommendations(statusData: any): string[] {
    const recommendations: string[] = [];

    if (!statusData || !statusData.components) {
      recommendations.push('Não foi possível obter status dos componentes');
      return recommendations;
    }

    Object.entries(statusData.components).forEach(([component, data]: [string, any]) => {
      if (data?.status === 'down') {
        recommendations.push(
          `Componente ${this.getComponentNames()[component]} está inativo - Verificar urgentemente`
        );
      } else if (data?.status === 'degraded') {
        recommendations.push(
          `Componente ${this.getComponentNames()[component]} está degradado - Monitorar`
        );
      }
    });

    const score = this.calculateComplianceScore(statusData);
    if (score < 80) {
      recommendations.push(
        'Score de compliance abaixo de 80% - Revisar componentes críticos'
      );
    }

    if (recommendations.length === 0) {
      recommendations.push('Todos os componentes operacionais - Sistema saudável');
    }

    return recommendations;
  }

  /**
   * Verifica se precisa de atenção
   */
  static needsAttention(statusData: any): boolean {
    if (!statusData || !statusData.components) return true;

    return Object.values(statusData.components).some(
      (component: any) => component?.status === 'down' || component?.status === 'degraded'
    );
  }

  /**
   * Retorna nível de criticidade
   */
  static getCriticalityLevel(statusData: any): 'low' | 'medium' | 'high' | 'critical' {
    if (!statusData || !statusData.components) return 'critical';

    let downCount = 0;
    let degradedCount = 0;

    Object.values(statusData.components).forEach((component: any) => {
      if (component?.status === 'down') downCount++;
      if (component?.status === 'degraded') degradedCount++;
    });

    if (downCount >= 3) return 'critical';
    if (downCount >= 1) return 'high';
    if (degradedCount >= 2) return 'medium';
    return 'low';
  }

  /**
   * Formata nível de criticidade
   */
  static formatCriticality(level: string): string {
    const formats: Record<string, string> = {
      low: 'Baixa',
      medium: 'Média',
      high: 'Alta',
      critical: 'Crítica',
    };
    return formats[level] || level;
  }

  /**
   * Estatísticas resumidas
   */
  static getSummaryStats(statusData: any): {
    total: number;
    operational: number;
    degraded: number;
    down: number;
    complianceScore: number;
  } {
    if (!statusData || !statusData.components) {
      return {
        total: 0,
        operational: 0,
        degraded: 0,
        down: 0,
        complianceScore: 0,
      };
    }

    const components = Object.values(statusData.components);
    const stats = {
      total: components.length,
      operational: 0,
      degraded: 0,
      down: 0,
      complianceScore: 0,
    };

    components.forEach((component: any) => {
      if (component?.status === 'operational') stats.operational++;
      if (component?.status === 'degraded') stats.degraded++;
      if (component?.status === 'down') stats.down++;
    });

    stats.complianceScore = this.calculateComplianceScore(statusData);

    return stats;
  }
}

export default StatusService;
