/**
 * Financial AI Service
 * Análise financeira inteligente: fluxo de caixa, recebíveis, compras
 */

import { getFinancialFluxoDeCaixa } from '@/types/generated/ai/financial-fluxo-de-caixa/financial-fluxo-de-caixa';
import { getFinancialContasAReceber } from '@/types/generated/ai/financial-contas-a-receber/financial-contas-a-receber';
import { getFinancialCompras } from '@/types/generated/ai/financial-compras/financial-compras';

const cashflowApi = getFinancialFluxoDeCaixa();
const receivablesApi = getFinancialContasAReceber();
const purchasesApi = getFinancialCompras();

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
  ): Promise<any> {
    return cashflowApi.detectAnomaliesApiV1FinancialCashflowAiAnomaliesPost({
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
  ): Promise<any> {
    return cashflowApi.generateAiForecastApiV1FinancialCashflowAiForecastPost({
      condominio_id: condominioId,
      months_ahead: monthsAhead,
    });
  }

  /**
   * Identifica oportunidades de otimização
   */
  static async getCashflowOpportunities(condominioId: string): Promise<any> {
    return cashflowApi.getOpportunitiesApiV1FinancialCashflowAiOpportunitiesGet({
      condominio_id: condominioId,
    });
  }

  /**
   * Analisa riscos no fluxo de caixa
   */
  static async analyzeCashflowRisks(condominioId: string): Promise<any> {
    return cashflowApi.getRisksApiV1FinancialCashflowAiRisksGet({
      condominio_id: condominioId,
    });
  }

  /**
   * Sugestões de melhoria de fluxo de caixa
   */
  static async getCashflowSuggestions(condominioId: string): Promise<any> {
    return cashflowApi.getOptimizationSuggestionsApiV1FinancialCashflowAiSuggestionsGet({
      condominio_id: condominioId,
    });
  }

  // ========== CONTAS A RECEBER ==========

  /**
   * Prevê fluxo de caixa baseado em recebíveis
   */
  static async forecastReceivablesCashflow(
    condominioId: string,
    months?: number
  ): Promise<any> {
    return receivablesApi.getCashFlowForecastApiV1FinancialReceivablesAiCashFlowForecastGet({
      condominio_id: condominioId,
      months,
    });
  }

  /**
   * Define prioridades de cobrança
   */
  static async getCollectionPriorities(
    condominioId: string,
    limit?: number
  ): Promise<any> {
    return receivablesApi.getCollectionPrioritiesApiV1FinancialReceivablesAiCollectionPrioritiesGet({
      condominio_id: condominioId,
      limit,
    });
  }

  /**
   * Analisa risco de cliente
   */
  static async analyzeCustomerRisk(customerId: string): Promise<any> {
    return receivablesApi.getCustomerRiskApiV1FinancialReceivablesAiCustomerRiskCustomerIdGet(
      customerId
    );
  }

  /**
   * Análise de inadimplência
   */
  static async analyzeDelinquency(condominioId: string): Promise<any> {
    return receivablesApi.getDelinquencyAnalysisApiV1FinancialReceivablesAiDelinquencyAnalysisGet({
      condominio_id: condominioId,
    });
  }

  // ========== COMPRAS ==========

  /**
   * Prevê demanda de produtos
   */
  static async predictDemand(
    productId: string,
    monthsAhead?: number
  ): Promise<any> {
    return purchasesApi.predictDemandApiV1FinancialPurchasesAiPredictDemandPost({
      product_id: productId,
      months_ahead: monthsAhead,
    });
  }

  /**
   * Calcula ponto de reposição de estoque
   */
  static async calculateReorderPoint(productId: string): Promise<any> {
    return purchasesApi.calculateReorderPointApiV1FinancialPurchasesAiReorderPointProductIdGet(
      productId
    );
  }

  /**
   * Sugere fornecedores otimizados
   */
  static async suggestSuppliers(
    condominioId: string,
    productDescription: string,
    limit?: number
  ): Promise<any> {
    return purchasesApi.suggestSuppliersApiV1FinancialPurchasesAiSuggestSuppliersPost({
      condominio_id: condominioId,
      product_description: productDescription,
      limit,
    });
  }

  /**
   * Analisa desempenho de fornecedor
   */
  static async analyzeSupplier(supplierId: string): Promise<any> {
    return purchasesApi.analyzeSupplierApiV1FinancialPurchasesAiSupplierAnalysisSupplierIdGet(
      supplierId
    );
  }
}

export default FinancialAIService;
