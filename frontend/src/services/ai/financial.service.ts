/**
 * Financial AI Service
 * Análise financeira inteligente: fluxo de caixa, recebíveis, compras
 */

import { customInstance } from '@/lib/axios-instance';

const CASHFLOW_BASE = '/api/v1/financial/cashflow/ai';
const RECEIVABLES_BASE = '/api/v1/financial/receivables/ai';
const PURCHASES_BASE = '/api/v1/financial/purchases/ai';

/**
 * Service para análise financeira com IA
 */
export class FinancialAIService {
  // ========== FLUXO DE CAIXA ==========

  /**
   * Detecta anomalias no fluxo de caixa
   */
  static async detectCashflowAnomalies(
    condominioId: string,
    periodMonths?: number
  ): Promise<unknown> {
    return customInstance.post(`${CASHFLOW_BASE}/anomalies`, {
      condominio_id: condominioId,
      period_months: periodMonths,
    });
  }

  /**
   * Prevê fluxo de caixa futuro
   */
  static async forecastCashflow(
    condominioId: string,
    monthsAhead?: number
  ): Promise<unknown> {
    return customInstance.post(`${CASHFLOW_BASE}/forecast`, {
      condominio_id: condominioId,
      months_ahead: monthsAhead,
    });
  }

  /**
   * Identifica oportunidades de otimização
   */
  static async getCashflowOpportunities(condominioId: string): Promise<unknown> {
    return customInstance.get(`${CASHFLOW_BASE}/opportunities`, {
      params: { condominio_id: condominioId },
    });
  }

  /**
   * Analisa riscos no fluxo de caixa
   */
  static async analyzeCashflowRisks(condominioId: string): Promise<unknown> {
    return customInstance.get(`${CASHFLOW_BASE}/risks`, {
      params: { condominio_id: condominioId },
    });
  }

  /**
   * Sugestões de melhoria de fluxo de caixa
   */
  static async getCashflowSuggestions(condominioId: string): Promise<unknown> {
    return customInstance.get(`${CASHFLOW_BASE}/suggestions`, {
      params: { condominio_id: condominioId },
    });
  }

  // ========== CONTAS A RECEBER ==========

  /**
   * Prevê fluxo de caixa baseado em recebíveis
   */
  static async forecastReceivablesCashflow(
    condominioId: string,
    months?: number
  ): Promise<unknown> {
    return customInstance.get(`${RECEIVABLES_BASE}/cash-flow-forecast`, {
      params: { condominio_id: condominioId, months },
    });
  }

  /**
   * Define prioridades de cobrança
   */
  static async getCollectionPriorities(
    condominioId: string,
    limit?: number
  ): Promise<unknown> {
    return customInstance.get(`${RECEIVABLES_BASE}/collection-priorities`, {
      params: { condominio_id: condominioId, limit },
    });
  }

  /**
   * Analisa risco de cliente
   */
  static async analyzeCustomerRisk(customerId: string): Promise<unknown> {
    return customInstance.get(
      `${RECEIVABLES_BASE}/customer-risk/${customerId}`
    );
  }

  /**
   * Análise de inadimplência
   */
  static async analyzeDelinquency(condominioId: string): Promise<unknown> {
    return customInstance.get(`${RECEIVABLES_BASE}/delinquency-analysis`, {
      params: { condominio_id: condominioId },
    });
  }

  // ========== COMPRAS ==========

  /**
   * Prevê demanda de produtos
   */
  static async predictDemand(
    productId: string,
    monthsAhead?: number
  ): Promise<unknown> {
    return customInstance.post(`${PURCHASES_BASE}/predict-demand`, {
      product_id: productId,
      months_ahead: monthsAhead,
    });
  }

  /**
   * Calcula ponto de reposição de estoque
   */
  static async calculateReorderPoint(productId: string): Promise<unknown> {
    return customInstance.get(
      `${PURCHASES_BASE}/reorder-point/${productId}`
    );
  }

  /**
   * Sugere fornecedores otimizados
   */
  static async suggestSuppliers(
    condominioId: string,
    productDescription: string,
    limit?: number
  ): Promise<unknown> {
    return customInstance.post(`${PURCHASES_BASE}/suggest-suppliers`, {
      condominio_id: condominioId,
      product_description: productDescription,
      limit,
    });
  }

  /**
   * Analisa desempenho de fornecedor
   */
  static async analyzeSupplier(supplierId: string): Promise<unknown> {
    return customInstance.get(
      `${PURCHASES_BASE}/supplier-analysis/${supplierId}`
    );
  }
}

export default FinancialAIService;
