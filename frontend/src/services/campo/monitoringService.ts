/**
 * Service Layer - Monitoring (CAMPO)
 * Monitoramento de saúde e métricas do sistema CAMPO
 */

import * as MonitoringAPI from '@/api/campo/generated/monitoring/monitoring';

export class MonitoringService {
  /**
   * Verifica saúde do sistema
   */
  async health() {
    return MonitoringAPI.healthCheckApiV1CampoMonitoringHealthGet();
  }

  /**
   * Verifica prontidão do sistema
   */
  async ready() {
    return MonitoringAPI.readinessCheckApiV1CampoMonitoringReadyGet();
  }

  /**
   * Ping de conectividade
   */
  async ping() {
    return MonitoringAPI.pingApiV1CampoMonitoringPingGet();
  }

  /**
   * Métricas do sistema
   */
  async metrics() {
    return MonitoringAPI.getMetricsApiV1CampoMonitoringMetricsGet();
  }

  /**
   * Status detalhado dos serviços
   */
  async status() {
    return MonitoringAPI.systemStatusApiV1CampoMonitoringStatusGet();
  }
}

export const monitoringService = new MonitoringService();
