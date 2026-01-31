/**
 * React Query hooks for Financial AI
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { FinancialAIService } from '../financial.service';

// ========== FLUXO DE CAIXA ==========

export function useDetectCashflowAnomalies() {
  return useMutation({
    mutationFn: ({ condominioId, periodMonths }: { condominioId: string; periodMonths?: number }) =>
      FinancialAIService.detectCashflowAnomalies(condominioId, periodMonths),
  });
}

export function useForecastCashflow() {
  return useMutation({
    mutationFn: ({ condominioId, monthsAhead }: { condominioId: string; monthsAhead?: number }) =>
      FinancialAIService.forecastCashflow(condominioId, monthsAhead),
  });
}

export function useCashflowOpportunities(condominioId: string) {
  return useQuery({
    queryKey: ['financial-ai', 'cashflow', 'opportunities', condominioId],
    queryFn: () => FinancialAIService.getCashflowOpportunities(condominioId),
    enabled: !!condominioId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useCashflowRisks(condominioId: string) {
  return useQuery({
    queryKey: ['financial-ai', 'cashflow', 'risks', condominioId],
    queryFn: () => FinancialAIService.analyzeCashflowRisks(condominioId),
    enabled: !!condominioId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCashflowSuggestions(condominioId: string) {
  return useQuery({
    queryKey: ['financial-ai', 'cashflow', 'suggestions', condominioId],
    queryFn: () => FinancialAIService.getCashflowSuggestions(condominioId),
    enabled: !!condominioId,
    staleTime: 10 * 60 * 1000,
  });
}

// ========== CONTAS A RECEBER ==========

export function useForecastReceivablesCashflow() {
  return useMutation({
    mutationFn: ({ condominioId, months }: { condominioId: string; months?: number }) =>
      FinancialAIService.forecastReceivablesCashflow(condominioId, months),
  });
}

export function useCollectionPriorities(condominioId: string, limit?: number) {
  return useQuery({
    queryKey: ['financial-ai', 'receivables', 'collection-priorities', condominioId, limit],
    queryFn: () => FinancialAIService.getCollectionPriorities(condominioId, limit),
    enabled: !!condominioId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCustomerRiskAnalysis(customerId: string) {
  return useQuery({
    queryKey: ['financial-ai', 'receivables', 'customer-risk', customerId],
    queryFn: () => FinancialAIService.analyzeCustomerRisk(customerId),
    enabled: !!customerId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useDelinquencyAnalysis(condominioId: string) {
  return useQuery({
    queryKey: ['financial-ai', 'receivables', 'delinquency', condominioId],
    queryFn: () => FinancialAIService.analyzeDelinquency(condominioId),
    enabled: !!condominioId,
    staleTime: 5 * 60 * 1000,
  });
}

// ========== COMPRAS ==========

export function usePredictDemand() {
  return useMutation({
    mutationFn: ({ productId, monthsAhead }: { productId: string; monthsAhead?: number }) =>
      FinancialAIService.predictDemand(productId, monthsAhead),
  });
}

export function useReorderPoint(productId: string) {
  return useQuery({
    queryKey: ['financial-ai', 'purchases', 'reorder-point', productId],
    queryFn: () => FinancialAIService.calculateReorderPoint(productId),
    enabled: !!productId,
    staleTime: 30 * 60 * 1000,
  });
}

export function useSuggestSuppliers() {
  return useMutation({
    mutationFn: ({
      condominioId,
      productDescription,
      limit,
    }: {
      condominioId: string;
      productDescription: string;
      limit?: number;
    }) => FinancialAIService.suggestSuppliers(condominioId, productDescription, limit),
  });
}

export function useSupplierAnalysis(supplierId: string) {
  return useQuery({
    queryKey: ['financial-ai', 'purchases', 'supplier-analysis', supplierId],
    queryFn: () => FinancialAIService.analyzeSupplier(supplierId),
    enabled: !!supplierId,
    staleTime: 15 * 60 * 1000,
  });
}
