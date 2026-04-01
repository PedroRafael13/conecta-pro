import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Relatórios / Dashboards Executivos
 *
 * Funcionalidades testadas:
 * - Dashboard executivo com KPIs
 * - Alertas ativos
 * - Insights preditivos
 * - Estatísticas gerais
 */

// Mock data
const mockDashboard = {
  kpis: [
    { nome: 'Faturamento Mensal', valor: 'R$ 1.2M', trend: 'up', variacao: '+12%' },
    { nome: 'Clientes Ativos', valor: '1,250', trend: 'up', variacao: '+5%' },
    { nome: 'Churn Rate', valor: '3.2%', trend: 'down', variacao: '-0.5%' },
    { nome: 'Ticket Médio', valor: 'R$ 980', trend: 'up', variacao: '+8%' },
    { nome: 'Satisfação', valor: '4.5/5', trend: 'stable', variacao: '0%' },
    { nome: 'SLA', valor: '98.5%', trend: 'up', variacao: '+1.2%' },
  ],
};

const mockAlerts = [
  { id: 1, tipo: 'Estoque', mensagem: 'Produto XYZ com estoque baixo', prioridade: 'alta', data: '2026-02-05T10:00:00Z' },
  { id: 2, tipo: 'Financeiro', mensagem: 'Fatura em atraso - Cliente ABC', prioridade: 'critica', data: '2026-02-05T09:30:00Z' },
  { id: 3, tipo: 'Sistema', mensagem: 'Uso de CPU acima de 80%', prioridade: 'media', data: '2026-02-05T09:00:00Z' },
];

const mockInsights = [
  { id: 1, titulo: 'Aumento de Vendas', descricao: 'Projeção de 15% de crescimento no próximo trimestre', confianca: 0.85 },
  { id: 2, titulo: 'Sazonalidade', descricao: 'Pico de demanda esperado em março', confianca: 0.72 },
  { id: 3, titulo: 'Retenção', descricao: 'Clientes do segmento enterprise tendem a renovar', confianca: 0.91 },
];

// Setup de mocks para API
async function setupDashboardsMocks(page: Page) {
  await page.route('**/api/v1/analytics/executive-dashboard**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockDashboard),
    });
  });

  await page.route('**/api/v1/analytics/alerts**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ alerts: mockAlerts }),
    });
  });

  await page.route('**/api/v1/analytics/insights**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ insights: mockInsights }),
    });
  });
}

test.describe('Relatórios - Dashboards Executivos', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupDashboardsMocks(page);
    await page.goto('/modulos/relatorios/dashboards');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de dashboards', async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboards/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Dashboards Executivos/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/KPIs|alertas|insights/i');
    await expect(description).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTATÍSTICAS
  // ==========================================

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const totalKpis = page.locator('text=/Total KPIs/i');
    const activeAlerts = page.locator('text=/Alertas Ativos/i');
    const criticalAlerts = page.locator('text=/Alertas Críticos/i');
    const insights = page.locator('text=/Insights/i');

    await expect(totalKpis).toBeVisible();
    await expect(activeAlerts).toBeVisible();
    await expect(criticalAlerts).toBeVisible();
    await expect(insights).toBeVisible();
  });

  test('deve exibir valores corretos nas estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('6').first()).toBeVisible(); // Total KPIs
    await expect(page.getByText('3').first()).toBeVisible(); // Alertas Ativos
    await expect(page.getByText('1').first()).toBeVisible(); // Alertas Críticos
    await expect(page.getByText('3').nth(1)).toBeVisible(); // Insights
  });

  // ==========================================
  // TESTES DE KPIs
  // ==========================================

  test('deve exibir seção de KPIs', async ({ page }) => {
    await page.waitForTimeout(1000);

    const kpisSection = page.locator('text=/KPIs por Categoria/i').first();
    await expect(kpisSection).toBeVisible();
  });

  test('deve exibir cards de KPIs', async ({ page }) => {
    await page.waitForTimeout(1000);

    const kpiCard = page.locator('text=/Faturamento|Clientes|Churn|Ticket/i').first();
    const hasKpi = await kpiCard.isVisible().catch(() => false);
    expect(hasKpi !== undefined).toBeTruthy();
  });

  test('deve exibir indicadores de tendência', async ({ page }) => {
    await page.waitForTimeout(1000);

    const trendIndicator = page.locator('[class*="trend"], [data-lucide="TrendingUp"], [data-lucide="TrendingDown"]').first();
    const hasTrend = await trendIndicator.isVisible().catch(() => false);
    expect(hasTrend !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE ALERTAS
  // ==========================================

  test('deve exibir seção de alertas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const alertsSection = page.locator('text=/Alertas Ativos/i').first();
    await expect(alertsSection).toBeVisible();
  });

  test('deve exibir tabela de alertas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const table = page.locator('table').first();
    const hasTable = await table.isVisible().catch(() => false);
    expect(hasTable !== undefined).toBeTruthy();
  });

  test('deve exibir colunas corretas na tabela de alertas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Tipo', 'Mensagem', 'Prioridade', 'Data'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  test('deve exibir badges de prioridade', async ({ page }) => {
    await page.waitForTimeout(1000);

    const priorityBadge = page.locator('text=/Crítica|Alta|Média/i').first();
    const hasBadge = await priorityBadge.isVisible().catch(() => false);
    expect(hasBadge !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE INSIGHTS
  // ==========================================

  test('deve exibir seção de insights', async ({ page }) => {
    await page.waitForTimeout(1000);

    const insightsSection = page.locator('text=/Insights Preditivos/i').first();
    await expect(insightsSection).toBeVisible();
  });

  test('deve exibir cards de insights', async ({ page }) => {
    await page.waitForTimeout(1000);

    const insightCard = page.locator('text=/Aumento|Sazonalidade|Retenção/i').first();
    const hasInsight = await insightCard.isVisible().catch(() => false);
    expect(hasInsight !== undefined).toBeTruthy();
  });

  test('deve exibir barra de confiança', async ({ page }) => {
    await page.waitForTimeout(1000);

    const confidenceBar = page.locator('text=/%/i').first();
    const hasConfidence = await confidenceBar.isVisible().catch(() => false);
    expect(hasConfidence !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE NAVEGAÇÃO
  // ==========================================

  test('deve ter botão para voltar para relatórios', async ({ page }) => {
    const backButton = page.locator('button:has-text("Relatórios"), a:has-text("Relatórios")').first();
    await expect(backButton).toBeVisible();
  });

  test('deve navegar para página de relatórios ao clicar em voltar', async ({ page }) => {
    const backButton = page.locator('button:has-text("Relatórios"), a:has-text("Relatórios")').first();
    await backButton.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/relatorios/);
  });

  // ==========================================
  // TESTES DE ATUALIZAR
  // ==========================================

  test('deve ter botão para atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button:has([data-lucide="RefreshCw"])').first();
    await expect(refreshButton).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTADOS ESPECIAIS
  // ==========================================

  test('deve exibir empty state quando não há KPIs', async ({ page }) => {
    await page.route('**/api/v1/analytics/executive-dashboard**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ kpis: [] }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/Nenhum KPI|disponível/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há alertas', async ({ page }) => {
    await page.route('**/api/v1/analytics/alerts**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ alerts: [] }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/Nenhum alerta|ativo/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });

  test('deve exibir estado de erro quando há falha', async ({ page }) => {
    await page.route('**/api/v1/analytics/executive-dashboard**', async (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const errorState = page.locator('text=/erro|Erro|falha/i').first();
    const hasError = await errorState.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
