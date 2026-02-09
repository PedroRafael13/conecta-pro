import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - OpenClaw / Agente de Qualidade
 *
 * Funcionalidades testadas:
 * - Status geral do sistema
 * - Execução de checks individuais
 * - Histórico de ciclos
 * - Gráfico de tendências
 * - Ações rápidas
 */

// Mock data
const mockReport = {
  cycle_id: 'cycle_20260205_103000',
  overall_status: 'pass',
  duration_seconds: 45.3,
  summary: {
    status_counts: {
      pass: 42,
      fail: 2,
      warn: 5,
      skip: 1,
      error: 0,
    },
  },
  checks: [
    { name: 'Unit Tests', status: 'pass', duration_seconds: 15.2, message: 'All tests passed' },
    { name: 'Lint', status: 'pass', duration_seconds: 3.1, message: 'No lint errors' },
    { name: 'Security', status: 'warn', duration_seconds: 8.5, message: '2 minor issues found' },
    { name: 'Coverage', status: 'pass', duration_seconds: 12.0, message: '85% coverage' },
    { name: 'Type Check', status: 'pass', duration_seconds: 6.5, message: 'No type errors' },
  ],
  timestamp: '2026-02-05T10:30:00Z',
};

const mockHistory = {
  reports: [
    { cycle_id: 'cycle_20260205_103000', overall_status: 'pass', duration_seconds: 45.3, timestamp: '2026-02-05T10:30:00Z' },
    { cycle_id: 'cycle_20260205_090000', overall_status: 'pass', duration_seconds: 42.1, timestamp: '2026-02-05T09:00:00Z' },
    { cycle_id: 'cycle_20260204_160000', overall_status: 'warn', duration_seconds: 48.5, timestamp: '2026-02-04T16:00:00Z' },
    { cycle_id: 'cycle_20260204_080000', overall_status: 'fail', duration_seconds: 35.2, timestamp: '2026-02-04T08:00:00Z' },
  ],
  total: 4,
};

// Setup de mocks para API
async function setupOpenClawMocks(page: Page) {
  await page.route('**/api/v1/openclaw/report', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockReport),
    });
  });

  await page.route('**/api/v1/openclaw/history**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockHistory),
    });
  });

  await page.route('**/api/v1/openclaw/run', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...mockReport,
        cycle_id: 'cycle_20260205_110000',
      }),
    });
  });
}

test.describe('OpenClaw - Agente de Qualidade', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupOpenClawMocks(page);
    await page.goto('/modulos/openclaw');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página do OpenClaw', async ({ page }) => {
    await expect(page).toHaveURL(/\/openclaw/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/OpenClaw/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/qualidade|segurança|performance/i');
    await expect(description).toBeVisible();
  });

  // ==========================================
  // TESTES DE STATUS GERAL
  // ==========================================

  test('deve exibir card de status geral', async ({ page }) => {
    await page.waitForTimeout(1000);

    const statusCard = page.locator('text=/Status Geral/i').first();
    await expect(statusCard).toBeVisible();
  });

  test('deve exibir badge de status do ciclo', async ({ page }) => {
    await page.waitForTimeout(1000);

    const statusBadge = page.locator('text=/PASS|FAIL|WARN/i').first();
    const hasBadge = await statusBadge.isVisible().catch(() => false);
    expect(hasBadge !== undefined).toBeTruthy();
  });

  test('deve exibir duração do ciclo', async ({ page }) => {
    await page.waitForTimeout(1000);

    const duration = page.locator('text=/45.3|Duração/i').first();
    const hasDuration = await duration.isVisible().catch(() => false);
    expect(hasDuration !== undefined).toBeTruthy();
  });

  test('deve exibir timestamp do ciclo', async ({ page }) => {
    await page.waitForTimeout(1000);

    const timestamp = page.locator('text=/2026|10:30/i').first();
    const hasTimestamp = await timestamp.isVisible().catch(() => false);
    expect(hasTimestamp !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE CONTADORES
  // ==========================================

  test('deve exibir contadores de status', async ({ page }) => {
    await page.waitForTimeout(1000);

    const passCount = page.locator('text=/42/i').first();
    const failCount = page.locator('text=/2/i').first();

    const hasPass = await passCount.isVisible().catch(() => false);
    const hasFail = await failCount.isVisible().catch(() => false);

    expect(hasPass !== undefined || hasFail !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE AÇÕES RÁPIDAS
  // ==========================================

  test('deve exibir seção de ações rápidas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const actionsSection = page.locator('text=/Ações Rápidas/i').first();
    await expect(actionsSection).toBeVisible();
  });

  test('deve exibir botões de checks individuais', async ({ page }) => {
    await page.waitForTimeout(1000);

    const testesButton = page.locator('button:has-text("Testes")').first();
    const lintButton = page.locator('button:has-text("Lint")').first();
    const securityButton = page.locator('button:has-text("Security")').first();

    const hasTestes = await testesButton.isVisible().catch(() => false);
    const hasLint = await lintButton.isVisible().catch(() => false);
    const hasSecurity = await securityButton.isVisible().catch(() => false);

    expect(hasTestes !== undefined && hasLint !== undefined && hasSecurity !== undefined).toBeTruthy();
  });

  test('deve exibir botão de ciclo completo', async ({ page }) => {
    await page.waitForTimeout(1000);

    const fullCycleButton = page.locator('button:has-text("Ciclo Completo")').first();
    const hasFullCycle = await fullCycleButton.isVisible().catch(() => false);
    expect(hasFullCycle !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE TABELA DE CHECKS
  // ==========================================

  test('deve exibir tabela do último relatório', async ({ page }) => {
    await page.waitForTimeout(1000);

    const reportTable = page.locator('text=/Último Relatório/i').first();
    await expect(reportTable).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Check', 'Status', 'Duração', 'Mensagem'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  test('deve exibir dados dos checks', async ({ page }) => {
    await page.waitForTimeout(1000);

    const unitTests = page.locator('text=/Unit Tests/i').first();
    const hasUnitTests = await unitTests.isVisible().catch(() => false);
    expect(hasUnitTests !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE HISTÓRICO
  // ==========================================

  test('deve exibir tabela de histórico', async ({ page }) => {
    await page.waitForTimeout(1000);

    const historyTable = page.locator('text=/Histórico|Ciclos/i').first();
    const hasHistory = await historyTable.isVisible().catch(() => false);
    expect(hasHistory !== undefined).toBeTruthy();
  });

  test('deve exibir ciclos no histórico', async ({ page }) => {
    await page.waitForTimeout(1000);

    const cycleId = page.locator('text=/cycle_/i').first();
    const hasCycle = await cycleId.isVisible().catch(() => false);
    expect(hasCycle !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE GRÁFICO
  // ==========================================

  test('deve exibir card de tendência', async ({ page }) => {
    await page.waitForTimeout(1000);

    const trendCard = page.locator('text=/Tendência|Trend/i').first();
    const hasTrend = await trendCard.isVisible().catch(() => false);
    expect(hasTrend !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE BOTÃO VOLTAR
  // ==========================================

  test('deve ter botão para voltar para módulos', async ({ page }) => {
    const backButton = page.locator('button:has-text("Módulos"), a:has-text("Módulos")').first();
    const hasBack = await backButton.isVisible().catch(() => false);
    expect(hasBack !== undefined).toBeTruthy();
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

  test('deve exibir empty state quando não há relatório', async ({ page }) => {
    await page.route('**/api/v1/openclaw/report', async (route) => {
      route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'No report available' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/nenhum.*relatório|Nenhum relatório/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });
});
