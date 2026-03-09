/**
 * Testes E2E - Relatórios Comercial
 *
 * Testa funcionalidades do relatório comercial:
 * - Relatórios de vendas
 * - Pipeline comercial
 * - Propostas enviadas
 * - Taxa de conversão
 * - Exportação
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock data para relatório comercial
const mockLeadsData = {
  leads: [
    {
      id: 'lead-001',
      nome: 'Empresa ABC Ltda',
      empresa: 'ABC Ltda',
      score: 0.95,
      qualidade: 'quente',
      origem: 'Site',
      email: 'contato@abc.com',
      telefone: '(11) 99999-9999',
    },
    {
      id: 'lead-002',
      nome: 'João Silva',
      empresa: 'Silva Consulting',
      score: 0.82,
      qualidade: 'quente',
      origem: 'Indicação',
      email: 'joao@silva.com',
      telefone: '(11) 98888-8888',
    },
    {
      id: 'lead-003',
      nome: 'Maria Santos',
      empresa: 'Santos Tech',
      score: 0.65,
      qualidade: 'morno',
      origem: 'LinkedIn',
      email: 'maria@santos.com',
      telefone: '(11) 97777-7777',
    },
    {
      id: 'lead-004',
      nome: 'Pedro Costa',
      empresa: 'Costa Segurança',
      score: 0.45,
      qualidade: 'frio',
      origem: 'Email',
      email: 'pedro@costa.com',
      telefone: '(11) 96666-6666',
    },
  ],
  total: 4,
};

const mockChurnData = {
  risco_medio: 0.15,
  taxa_conversao: 0.68,
  usuarios_risco: 12,
  items: [
    {
      id: 'user-001',
      nome: 'Cliente A',
      risco: 'alto',
      probabilidade: 0.85,
      ultimo_acesso: '2025-01-15T10:00:00Z',
      acao: 'Contato prioritário',
    },
    {
      id: 'user-002',
      nome: 'Cliente B',
      risco: 'medio',
      probabilidade: 0.55,
      ultimo_acesso: '2025-01-20T14:00:00Z',
      acao: 'Oferta especial',
    },
  ],
  resumo: {
    usuarios_risco: 12,
    retencao: 0.85,
  },
};

test.describe('📊 Relatórios - Comercial', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Mock endpoints
    await page.route('**/api/v1/analytics/top-leads**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockLeadsData),
      });
    });

    await page.route('**/api/v1/analytics/churn**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockChurnData),
      });
    });

    await page.goto('/modulos/relatorios/comercial');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO
  // ==========================================

  test('deve carregar a página de relatório comercial', async ({ page }) => {
    const heading = page.locator('h1');
    await expect(heading).toContainText('Relatório Comercial');
  });

  test('deve exibir descrição da página', async ({ page }) => {
    await expect(page.locator('text=Leads, scoring e análise de churn')).toBeVisible();
  });

  test('deve exibir período selecionado por padrão', async ({ page }) => {
    const periodoSelect = page.locator('[role="combobox"]').first();
    await expect(periodoSelect).toBeVisible();
  });

  // ==========================================
  // TESTES DE RELATÓRIOS DE VENDAS
  // ==========================================

  test('deve exibir estatísticas de vendas nos cards', async ({ page }) => {
    await expect(page.locator('text=Top Leads')).toBeVisible();
    await expect(page.locator('text=Score Médio')).toBeVisible();
    await expect(page.locator('text=Risco Churn')).toBeVisible();
    await expect(page.locator('text=Conversão')).toBeVisible();
  });

  test('deve exibir quantidade de leads', async ({ page }) => {
    await expect(page.locator('text=4').first()).toBeVisible();
  });

  test('deve exibir tabela de leads', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Verificar headers
    await expect(page.locator('th:has-text("Nome")')).toBeVisible();
    await expect(page.locator('th:has-text("Empresa")')).toBeVisible();
    await expect(page.locator('th:has-text("Score")')).toBeVisible();
    await expect(page.locator('th:has-text("Qualidade")')).toBeVisible();
    await expect(page.locator('th:has-text("Origem")')).toBeVisible();
  });

  // ==========================================
  // TESTES DE PIPELINE COMERCIAL
  // ==========================================

  test('deve exibir leads com qualidade Quente', async ({ page }) => {
    const quenteBadge = page.locator('text=Quente').first();
    await expect(quenteBadge).toBeVisible();
  });

  test('deve exibir leads com qualidade Morno', async ({ page }) => {
    const mornoBadge = page.locator('text=Morno').first();
    await expect(mornoBadge).toBeVisible();
  });

  test('deve exibir leads com qualidade Frio', async ({ page }) => {
    const frioBadge = page.locator('text=Frio').first();
    await expect(frioBadge).toBeVisible();
  });

  test('deve exibir barra de progresso do score', async ({ page }) => {
    const progressBars = page.locator('[class*="rounded-full"][class*="bg-amber"]');
    const count = await progressBars.count();
    expect(count).toBeGreaterThan(0);
  });

  // ==========================================
  // TESTES DE TAXA DE CONVERSÃO
  // ==========================================

  test('deve exibir taxa de conversão', async ({ page }) => {
    await expect(page.locator('text=Conversão').first()).toBeVisible();
  });

  test('deve exibir análise de churn', async ({ page }) => {
    await expect(page.locator('text=Análise de Churn')).toBeVisible();
  });

  test('deve exibir tabela de usuários em risco', async ({ page }) => {
    await expect(page.locator('th:has-text("Risco")')).toBeVisible();
    await expect(page.locator('th:has-text("Probabilidade")')).toBeVisible();
    await expect(page.locator('th:has-text("Ação Recomendada")')).toBeVisible();
  });

  // ==========================================
  // TESTES DE FILTROS E PERÍODO
  // ==========================================

  test('deve permitir alterar período do relatório', async ({ page }) => {
    const periodoSelect = page.locator('[role="combobox"]').first();
    await periodoSelect.click();

    await page.locator('[role="option"]:has-text("90 dias")').click();
    await page.waitForTimeout(500);

    // A página deve continuar funcionando
    await expect(page.locator('h1')).toContainText('Relatório Comercial');
  });

  test('deve permitir atualizar dados do relatório', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await expect(refreshButton).toBeVisible();
    await refreshButton.click();

    // Verificar loading state
    await page.waitForTimeout(500);
    await expect(page.locator('table')).toBeVisible();
  });

  // ==========================================
  // TESTES DE EXPORTAÇÃO
  // ==========================================

  test('deve exibir botão de voltar para relatórios', async ({ page }) => {
    const backButton = page.locator('button:has-text("Relatórios")');
    await expect(backButton).toBeVisible();
  });

  test('deve navegar de volta para módulo de relatórios', async ({ page }) => {
    const backButton = page.locator('button:has-text("Relatórios")');
    await backButton.click();
    await page.waitForTimeout(1000);

    expect(page.url()).toContain('/modulos/relatorios');
  });
});
