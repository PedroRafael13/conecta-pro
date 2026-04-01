/**
 * Testes E2E - Relatórios Financeiro
 *
 * Testa funcionalidades do relatório financeiro:
 * - DRE (Demonstração do Resultado do Exercício)
 * - Fluxo de caixa
 * - Contas a pagar/receber
 * - Inadimplência
 * - Exportação
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock data para relatório financeiro
const mockForecastData = {
  receita_prevista: 150000.00,
  precisao: 0.92,
  scenarios: [
    {
      id: 'scen-001',
      periodo: '2025-01-01',
      valor_previsto: 50000.00,
      valor_real: 52000.00,
      precisao: 0.96,
    },
    {
      id: 'scen-002',
      periodo: '2025-02-01',
      valor_previsto: 55000.00,
      valor_real: 53000.00,
      precisao: 0.96,
    },
    {
      id: 'scen-003',
      periodo: '2025-03-01',
      valor_previsto: 45000.00,
      valor_real: null,
      precisao: 0.85,
    },
  ],
};

const mockFraudData = {
  total_alertas: 3,
  inadimplencia: 0.05,
  resumo: {
    valor_risco: 25000.00,
    taxa_deteccao: 0.98,
  },
  alertas: [
    {
      id: 'alert-001',
      tipo: 'Transação Suspeita',
      descricao: 'Valor acima do padrão do cliente',
      risco: 'alto',
      valor: 15000.00,
      data: '2025-02-04T10:00:00Z',
    },
    {
      id: 'alert-002',
      tipo: 'Pagamento Duplicado',
      descricao: 'Possível pagamento em duplicidade',
      risco: 'medio',
      valor: 8500.00,
      data: '2025-02-03T14:30:00Z',
    },
    {
      id: 'alert-003',
      tipo: 'Horário Irregular',
      descricao: 'Transação fora do horário comercial',
      risco: 'baixo',
      valor: 1500.00,
      data: '2025-02-02T22:15:00Z',
    },
  ],
};

test.describe('💰 Relatórios - Financeiro', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Mock endpoints
    await page.route('**/api/v1/analytics/forecast**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockForecastData),
      });
    });

    await page.route('**/api/v1/analytics/fraud**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockFraudData),
      });
    });

    await page.goto('/modulos/relatorios/financeiro');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO
  // ==========================================

  test('deve carregar a página de relatório financeiro', async ({ page }) => {
    const heading = page.locator('h1');
    await expect(heading).toContainText('Relatório Financeiro');
  });

  test('deve exibir descrição da página', async ({ page }) => {
    await expect(page.locator('text=Previsões, fraudes e indicadores financeiros')).toBeVisible();
  });

  test('deve exibir seletor de período', async ({ page }) => {
    const periodoSelect = page.locator('[role="combobox"]').first();
    await expect(periodoSelect).toBeVisible();
  });

  // ==========================================
  // TESTES DE DRE E INDICADORES
  // ==========================================

  test('deve exibir card de Receita Prevista', async ({ page }) => {
    await expect(page.locator('text=Receita Prevista')).toBeVisible();
  });

  test('deve exibir card de Precisão Forecast', async ({ page }) => {
    await expect(page.locator('text=Precisão Forecast')).toBeVisible();
  });

  test('deve exibir card de Alertas Fraude', async ({ page }) => {
    await expect(page.locator('text=Alertas Fraude')).toBeVisible();
  });

  test('deve exibir card de Índice Inadimplência', async ({ page }) => {
    await expect(page.locator('text=Índice Inadimplência')).toBeVisible();
  });

  // ==========================================
  // TESTES DE FLUXO DE CAIXA
  // ==========================================

  test('deve exibir seção de Previsão de Vendas', async ({ page }) => {
    await expect(page.locator('text=Previsão de Vendas')).toBeVisible();
  });

  test('deve exibir tabela de previsões', async ({ page }) => {
    await expect(page.locator('th:has-text("Período")')).toBeVisible();
    await expect(page.locator('th:has-text("Valor Previsto")')).toBeVisible();
    await expect(page.locator('th:has-text("Valor Real")')).toBeVisible();
    await expect(page.locator('th:has-text("Variação")')).toBeVisible();
    await expect(page.locator('th:has-text("Precisão")')).toBeVisible();
  });

  test('deve exibir valores monetários formatados', async ({ page }) => {
    // Verificar se existe algum valor formatado como moeda
    const currencyPattern = page.locator('text=/R\\$ [\\d.,]+/');
    const count = await currencyPattern.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir variação percentual', async ({ page }) => {
    const variationPattern = page.locator('text=/[+-]?\\d+\\.\\d+%/');
    const count = await variationPattern.count();
    expect(count).toBeGreaterThan(0);
  });

  // ==========================================
  // TESTES DE CONTAS A PAGAR/RECEBER
  // ==========================================

  test('deve exibir resumo de receita prevista', async ({ page }) => {
    await expect(page.locator('text=Receita Prevista').first()).toBeVisible();
  });

  test('deve exibir dados do período atual', async ({ page }) => {
    const periodoInfo = page.locator('text=/30 dias|90 dias|365 dias/');
    const count = await periodoInfo.count();
    expect(count).toBeGreaterThan(0);
  });

  // ==========================================
  // TESTES DE INADIMPLÊNCIA
  // ==========================================

  test('deve exibir seção de Análise de Fraude', async ({ page }) => {
    await expect(page.locator('text=Análise de Fraude')).toBeVisible();
  });

  test('deve exibir total de alertas', async ({ page }) => {
    await expect(page.locator('text=Total de Alertas')).toBeVisible();
  });

  test('deve exibir valor em risco', async ({ page }) => {
    await expect(page.locator('text=Valor em Risco')).toBeVisible();
  });

  test('deve exibir tabela de alertas de fraude', async ({ page }) => {
    await expect(page.locator('th:has-text("Tipo")')).toBeVisible();
    await expect(page.locator('th:has-text("Descrição")')).toBeVisible();
    await expect(page.locator('th:has-text("Risco")')).toBeVisible();
    await expect(page.locator('th:has-text("Valor")')).toBeVisible();
  });

  test('deve exibir badges de risco (Alto, Médio, Baixo)', async ({ page }) => {
    const altoBadge = page.locator('text=Alto').first();
    const medioBadge = page.locator('text=Médio').first();
    const baixoBadge = page.locator('text=Baixo').first();

    // Pelo menos um deve estar visível
    const hasAny = await altoBadge.isVisible().catch(() => false) ||
                   await medioBadge.isVisible().catch(() => false) ||
                   await baixoBadge.isVisible().catch(() => false);
    expect(hasAny).toBeTruthy();
  });

  // ==========================================
  // TESTES DE FILTROS
  // ==========================================

  test('deve permitir alterar período para trimestral', async ({ page }) => {
    const periodoSelect = page.locator('[role="combobox"]').first();
    await periodoSelect.click();

    await page.locator('[role="option"]:has-text("Trimestral")').click();
    await page.waitForTimeout(500);

    // A página deve continuar funcionando
    await expect(page.locator('h1')).toContainText('Relatório Financeiro');
  });

  test('deve permitir atualizar dados financeiros', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await expect(refreshButton).toBeVisible();
    await refreshButton.click();

    await page.waitForTimeout(500);
    await expect(page.locator('table')).toBeVisible();
  });
});
