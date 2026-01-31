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
    return MonitoringAPI.healthCheckApiV1CampoMonitoringMonitoringHealthGet();
  }

  /**
   * Verifica prontidão do sistema
   */
  async ready() {
    return MonitoringAPI.readinessCheckApiV1CampoMonitoringMonitoringReadyGet();
  }

  /**
   * Ping de conectividade
   */
  async ping() {
    return MonitoringAPI.pingApiV1CampoMonitoringMonitoringPingGet();
  }

  /**
   * Métricas do sistema
   */
  async metrics() {
    return MonitoringAPI.getMetricsApiV1CampoMonitoringMonitoringMetricsGet();
  }

  /**
   * Status detalhado dos serviços
   */
  async status() {
    return MonitoringAPI.systemStatusApiV1CampoMonitoringMonitoringStatusGet();
  }
}

export const monitoringService = new MonitoringService();
