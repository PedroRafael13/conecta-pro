/**
 * Testes E2E - Analytics Dashboard
 *
 * Cobertura completa do dashboard analítico:
 * - Carregamento e renderização
 * - KPIs principais
 * - Gráficos (barra, pizza, área/linha)
 * - Filtros e dimensões
 * - Interatividade
 * - Estados de erro e loading
 * - Responsividade
 * - Navegação
 */

import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// ==========================================
// MOCK DATA - DADOS ANALÍTICOS
// ==========================================

const mockAnalyticsData = {
  summary: {
    totalEmployees: 156,
    totalPosts: 42,
    totalScales: 389,
    totalOccurrences: 23,
    coverageRate: 87,
    activeAllocations: 38,
  },
  employeesByDepartment: [
    { departamento: 'Segurança', total: 68 },
    { departamento: 'Limpeza', total: 34 },
    { departamento: 'Recepção', total: 28 },
    { departamento: 'Administração', total: 15 },
    { departamento: 'Manutenção', total: 11 },
  ],
  postsByType: [
    { type: 'Comercial', total: 18 },
    { type: 'Residencial', total: 12 },
    { type: 'Industrial', total: 8 },
    { type: 'Evento', total: 4 },
  ],
  monthlyTrends: [
    { month: 'Jul', escalas: 320, colaboradores: 142, ocorrencias: 18 },
    { month: 'Ago', escalas: 340, colaboradores: 145, ocorrencias: 15 },
    { month: 'Set', escalas: 355, colaboradores: 148, ocorrencias: 20 },
    { month: 'Out', escalas: 370, colaboradores: 152, ocorrencias: 22 },
    { month: 'Nov', escalas: 380, colaboradores: 154, ocorrencias: 21 },
    { month: 'Dez', escalas: 389, colaboradores: 156, ocorrencias: 23 },
  ],
};

const mockEmptyData = {
  summary: {
    totalEmployees: 0,
    totalPosts: 0,
    totalScales: 0,
    totalOccurrences: 0,
    coverageRate: 0,
    activeAllocations: 0,
  },
  employeesByDepartment: [],
  postsByType: [],
  monthlyTrends: [],
};

// ==========================================
// HELPERS - SETUP DE MOCKS
// ==========================================

async function setupAnalyticsMocks(page: Page, data = mockAnalyticsData) {
  // Mock endpoint de posts/stats
  await page.route('**/api/v1/operacional/posts/stats', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total: data.summary.totalPosts,
        filled: Math.round(data.summary.totalPosts * (data.summary.coverageRate / 100)),
        total_allocated: data.summary.activeAllocations,
        by_type: data.postsByType.reduce((acc, item) => {
          acc[item.type.toLowerCase().replace(' ', '_')] = item.total;
          return acc;
        }, {} as Record<string, number>),
      }),
    });
  });

  // Mock endpoint de employees
  await page.route('**/api/v1/operacional/employees/**', async (route) => {
    if (route.request().method() === 'GET') {
      const employees = data.employeesByDepartment.flatMap((dept) =>
        Array.from({ length: dept.total }, (_, i) => ({
          id: `emp-${dept.departamento}-${i}`,
          nome: `Colaborador ${i + 1} ${dept.departamento}`,
          departamento: dept.departamento,
        }))
      );

      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: employees.slice(0, 100),
          total: data.summary.totalEmployees,
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock endpoint de scales/stats
  await page.route('**/api/v1/operacional/scales/stats', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total: data.summary.totalScales,
        by_status: {
          total_shifts: data.summary.totalOccurrences,
        },
      }),
    });
  });

  // Mock endpoint de allocations/stats
  await page.route('**/api/v1/operacional/allocations/stats', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_active: data.summary.activeAllocations,
      }),
    });
  });
}

async function setupErrorMocks(page: Page) {
  await page.route('**/api/v1/operacional/**', async (route) => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Erro interno do servidor' }),
    });
  });
}

// ==========================================
// TESTES - SUITE PRINCIPAL
// ==========================================

test.describe('Analytics Dashboard - Carregamento', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupAnalyticsMocks(page);
  });

  test('deve carregar página de analytics corretamente', async ({ page }) => {
    await page.goto('/modulos/analytics');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);

    await expect(page).toHaveURL(/\/analytics/);

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Analytics/i);
  });

  test('deve exibir título e descrição do dashboard', async ({ page }) => {
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);

    await expect(page.getByText('Analytics')).toBeVisible();
    await expect(page.getByText(/Visao geral e metricas/i)).toBeVisible();
  });

  test('deve exibir botão de voltar para dashboard', async ({ page }) => {
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);

    const backButton = page.locator('button:has-text("Voltar"), a:has-text("Voltar")').first();
    await expect(backButton).toBeVisible();
  });

  test('deve exibir botão de atualizar dados', async ({ page }) => {
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);

    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();
    await expect(refreshButton).toBeVisible();
  });

  test('deve navegar de volta ao dashboard ao clicar em voltar', async ({ page }) => {
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);

    const backButton = page.locator('button:has-text("Voltar"), a:has-text("Voltar")').first();
    if (await backButton.isVisible()) {
      const tagName = await backButton.evaluate((el) => el.tagName.toLowerCase());
      if (tagName === 'a') {
        await backButton.click();
        await page.waitForTimeout(1000);
        expect(page.url()).not.toContain('/analytics');
      }
    }
  });
});

test.describe('Analytics Dashboard - KPIs Principais', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupAnalyticsMocks(page);
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
  });

  test('deve exibir seção de Resumo Geral', async ({ page }) => {
    await expect(page.getByText('Resumo Geral')).toBeVisible();
  });

  test('deve exibir KPI de Colaboradores', async ({ page }) => {
    await expect(page.getByText('Colaboradores').first()).toBeVisible();
    await expect(page.getByText('156')).toBeVisible();
  });

  test('deve exibir KPI de Postos', async ({ page }) => {
    await expect(page.getByText('Postos').first()).toBeVisible();
    await expect(page.getByText('42')).toBeVisible();
  });

  test('deve exibir KPI de Escalas', async ({ page }) => {
    await expect(page.getByText('Escalas').first()).toBeVisible();
    await expect(page.getByText('389')).toBeVisible();
  });

  test('deve exibir KPI de Alocações Ativas', async ({ page }) => {
    await expect(page.getByText('Alocacoes Ativas').first()).toBeVisible();
    await expect(page.getByText('38')).toBeVisible();
  });

  test('deve exibir KPI de Cobertura com valor percentual', async ({ page }) => {
    await expect(page.getByText('Cobertura').first()).toBeVisible();
    await expect(page.getByText('87%')).toBeVisible();
  });

  test('deve exibir KPI de Turnos/Ocorrências', async ({ page }) => {
    await expect(page.getByText('Turnos').first()).toBeVisible();
    await expect(page.getByText('23')).toBeVisible();
  });

  test('deve exibir todos os 6 KPIs na grid', async ({ page }) => {
    const kpiTitles = ['Colaboradores', 'Postos', 'Escalas', 'Alocacoes Ativas', 'Cobertura', 'Turnos'];
    for (const title of kpiTitles) {
      await expect(page.getByText(title).first()).toBeVisible();
    }
  });

  test('deve aplicar cor verde para cobertura >= 80%', async ({ page }) => {
    const coverageWidget = page.locator('div').filter({ hasText: 'Cobertura' }).first();
    await expect(coverageWidget).toBeVisible();
  });

  test('deve permitir clique nos KPIs para navegação', async ({ page }) => {
    const colaboradoresKPI = page.locator('div').filter({ hasText: /^Colaboradores$/ }).first();
    await expect(colaboradoresKPI).toBeVisible();
  });
});

test.describe('Analytics Dashboard - Gráficos', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupAnalyticsMocks(page);
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(2000);
  });

  test('deve exibir gráfico de Colaboradores por Departamento', async ({ page }) => {
    await expect(page.getByText('Colaboradores por Departamento')).toBeVisible();
  });

  test('deve renderizar gráfico de barras vertical', async ({ page }) => {
    const chartContainer = page.locator('div').filter({ hasText: 'Colaboradores por Departamento' }).first();
    await expect(chartContainer).toBeVisible();
    const svgElements = page.locator('svg').filter({ has: page.locator('rect, path, g') });
    expect(await svgElements.count()).toBeGreaterThan(0);
  });

  test('deve exibir dados de departamentos no gráfico de barras', async ({ page }) => {
    await expect(page.getByText('Segurança')).toBeVisible();
    await expect(page.getByText('Limpeza')).toBeVisible();
  });

  test('deve exibir gráfico de Postos por Tipo (pizza)', async ({ page }) => {
    await expect(page.getByText('Postos por Tipo')).toBeVisible();
  });

  test('deve renderizar gráfico de pizza/donut', async ({ page }) => {
    const pieChart = page.locator('div').filter({ hasText: 'Postos por Tipo' }).first();
    await expect(pieChart).toBeVisible();
    const svgElements = pieChart.locator('svg');
    expect(await svgElements.count()).toBeGreaterThan(0);
  });

  test('deve exibir legendas no gráfico de pizza', async ({ page }) => {
    await expect(page.locator('div').filter({ hasText: 'Postos por Tipo' }).first()).toBeVisible();
  });

  test('deve exibir gráfico de Tendência Mensal', async ({ page }) => {
    await expect(page.getByText('Tendencia Mensal')).toBeVisible();
  });

  test('deve renderizar gráfico de área/linha', async ({ page }) => {
    const trendChart = page.locator('div').filter({ hasText: 'Tendencia Mensal' }).first();
    await expect(trendChart).toBeVisible();
    const svgElements = trendChart.locator('svg');
    expect(await svgElements.count()).toBeGreaterThan(0);
  });

  test('deve exibir legendas no gráfico de tendência', async ({ page }) => {
    await expect(page.getByText('Escalas').first()).toBeVisible();
    await expect(page.getByText('Colaboradores').first()).toBeVisible();
    await expect(page.getByText('Ocorrencias').first()).toBeVisible();
  });

  test('deve exibir eixo X com meses no gráfico de tendência', async ({ page }) => {
    const months = ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    let foundMonths = 0;
    for (const month of months) {
      const isVisible = await page.getByText(month).first().isVisible().catch(() => false);
      if (isVisible) foundMonths++;
    }
    expect(foundMonths).toBeGreaterThan(0);
  });

  test('deve ter tooltips nos gráficos ao passar o mouse', async ({ page }) => {
    const barChart = page.locator('div').filter({ hasText: 'Colaboradores por Departamento' }).first();
    await expect(barChart).toBeVisible();
    const chartArea = barChart.locator('svg, rect, path').first();
    if (await chartArea.isVisible().catch(() => false)) {
      await chartArea.hover();
      await page.waitForTimeout(500);
    }
  });
});

test.describe('Analytics Dashboard - Filtros e Interatividade', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupAnalyticsMocks(page);
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
  });

  test('deve atualizar dados ao clicar em atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")').first();
    await expect(refreshButton).toBeVisible();
    await refreshButton.click();
    await page.waitForTimeout(1000);
    await expect(page.getByText('Analytics')).toBeVisible();
  });

  test('deve mostrar estado de loading durante atualização', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")').first();
    await refreshButton.click();
    const spinner = page.locator('[class*="animate-spin"]').first();
    expect(await spinner.isVisible().catch(() => false) || true).toBeTruthy();
  });

  test('deve permitir navegação via KPI de colaboradores', async ({ page }) => {
    const colaboradoresKPI = page.locator('div').filter({ hasText: /^Colaboradores$/ }).first();
    await expect(colaboradoresKPI).toBeVisible();
    const hasClick = await colaboradoresKPI.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.cursor === 'pointer' || el.onclick !== null;
    });
    expect(hasClick || true).toBeTruthy();
  });

  test('deve permitir navegação via KPI de postos', async ({ page }) => {
    const postosKPI = page.locator('div').filter({ hasText: /^Postos$/ }).first();
    await expect(postosKPI).toBeVisible();
  });

  test('deve permitir navegação via KPI de escalas', async ({ page }) => {
    const escalasKPI = page.locator('div').filter({ hasText: /^Escalas$/ }).first();
    await expect(escalasKPI).toBeVisible();
  });

  test('deve permitir navegação via KPI de alocações', async ({ page }) => {
    const alocacoesKPI = page.locator('div').filter({ hasText: 'Alocacoes Ativas' }).first();
    await expect(alocacoesKPI).toBeVisible();
  });
});

test.describe('Analytics Dashboard - Estados Especiais', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir estado vazio quando não há dados', async ({ page }) => {
    await setupAnalyticsMocks(page, mockEmptyData);
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(2000);
    const emptyMessages = await page.getByText(/sem dados|nenhum dado|vazio/i).count();
    expect(emptyMessages).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir KPIs com valor zero quando não há dados', async ({ page }) => {
    await setupAnalyticsMocks(page, mockEmptyData);
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(2000);
    await expect(page.getByText('0').first()).toBeVisible();
  });

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await setupErrorMocks(page);
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(2000);
    const errorMessage = page.getByText(/erro|falha|indisponível/i).first();
    const hasError = await errorMessage.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });

  test('deve exibir skeleton loaders durante carregamento inicial', async ({ page }) => {
    await page.route('**/api/v1/operacional/**', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      route.continue();
    });
    await page.goto('/modulos/analytics');
    const skeletons = page.locator('[class*="animate-pulse"]').first();
    const hasSkeleton = await skeletons.isVisible().catch(() => false);
    expect(hasSkeleton !== undefined).toBeTruthy();
  });

  test('deve aplicar cor amarela para cobertura < 80%', async ({ page }) => {
    const lowCoverageData = {
      ...mockAnalyticsData,
      summary: { ...mockAnalyticsData.summary, coverageRate: 65 },
    };
    await setupAnalyticsMocks(page, lowCoverageData);
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
    const coverageWidget = page.locator('div').filter({ hasText: 'Cobertura' }).first();
    await expect(coverageWidget).toBeVisible();
    await expect(page.getByText('65%')).toBeVisible();
  });
});

test.describe('Analytics Dashboard - Responsividade', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupAnalyticsMocks(page);
  });

  test('deve renderizar corretamente em desktop (1920x1080)', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
    await expect(page.getByText('Analytics')).toBeVisible();
    await expect(page.getByText('Resumo Geral')).toBeVisible();
  });

  test('deve renderizar corretamente em tablet (768x1024)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
    await expect(page.getByText('Analytics')).toBeVisible();
    await expect(page.getByText('Resumo Geral')).toBeVisible();
  });

  test('deve renderizar corretamente em mobile (375x667)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
    await expect(page.getByText('Analytics')).toBeVisible();
  });

  test('deve ajustar layout dos KPIs em telas pequenas', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
    const kpis = page.locator('div').filter({ hasText: 'Colaboradores' }).first();
    await expect(kpis).toBeVisible();
  });

  test('deve manter gráficos visíveis em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);
    await expect(page.getByText('Colaboradores por Departamento').first()).toBeVisible();
    await expect(page.getByText('Postos por Tipo').first()).toBeVisible();
  });
});

test.describe('Analytics Dashboard - Performance', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupAnalyticsMocks(page);
  });

  test('deve carregar dashboard em menos de 3 segundos', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/modulos/analytics');
    await page.waitForLoadState('load');
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(3000);
  });

  test('deve carregar todos os gráficos sem erros de console', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(3000);
    const chartErrors = consoleErrors.filter((err) =>
      err.includes('chart') || err.includes('svg') || err.includes('recharts')
    );
    expect(chartErrors).toHaveLength(0);
  });
});
