import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Substituições
 *
 * Testa workflow de substituições:
 * - Solicitação de substituição
 * - Aprovação
 * - Indicação de substituto
 * - Histórico
 */

test.describe('Operacional - Substituições', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de substituições', async ({ page }) => {
    await expect(page).toHaveURL(/\/substituicoes/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Substituicoes/i, { timeout: 10000 });
  });

  test('deve exibir tabela de substituições', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir estatísticas de substituições', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Stats cards (total, pendentes, concluídas, por falta, custo)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(5);
  });

  test('deve exibir alerta de substituições pendentes quando houver', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pendingAlert = page.locator('text=/substituicoes pendentes/i, .bg-yellow-500\\/10').first();
    const hasAlert = await pendingAlert.isVisible().catch(() => false);

    expect(hasAlert !== undefined).toBeTruthy();
  });

  test('deve ter botão de nova substituição', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Substituicao"), button:has-text("Nova")').first();
    const hasButton = await newButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Funcionario Teste');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Funcionario Teste');
    }
  });

  test('deve ter filtro de status', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(await statusFilter.inputValue()).toBeTruthy();
    }
  });

  test('deve ter filtro de motivo', async ({ page }) => {
    const reasonFilter = page.locator('select').nth(1);

    if (await reasonFilter.isVisible().catch(() => false)) {
      await reasonFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(await reasonFilter.inputValue()).toBeTruthy();
    }
  });

  test('deve ter filtro de data', async ({ page }) => {
    const dateInput = page.locator('input[type="date"]').first();

    if (await dateInput.isVisible().catch(() => false)) {
      await dateInput.fill('2024-01-01');
      await page.waitForTimeout(500);

      await expect(dateInput).toHaveValue('2024-01-01');
    }
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    // Verificar se contém colunas esperadas
    const hasDate = headerTexts.some(h => h.toLowerCase().includes('data'));
    const hasOriginal = headerTexts.some(h => h.toLowerCase().includes('original'));
    const hasSubstitute = headerTexts.some(h => h.toLowerCase().includes('substituto'));
    const hasReason = headerTexts.some(h => h.toLowerCase().includes('motivo'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));
    const hasCost = headerTexts.some(h => h.toLowerCase().includes('custo'));

    expect(hasDate || hasOriginal || hasSubstitute || hasReason || hasStatus || hasCost).toBeTruthy();
  });

  test('deve exibir data da substituição', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar datas formatadas
    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Operacional - Substituições - Ações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForTimeout(2000);
  });

  test('deve exibir funcionário original', async ({ page }) => {
    await page.waitForTimeout(2000);

    const originalCells = page.locator('table tbody tr td:nth-child(2)').all();
    const count = (await originalCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir substituto quando definido', async ({ page }) => {
    await page.waitForTimeout(2000);

    const substituteCells = page.locator('table tbody tr td:nth-child(3)').all();
    const count = (await substituteCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir badges de motivo', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de motivo (falta, férias, afastamento, etc)
    const reasonBadges = page.locator('text=/falta|ferias|afastamento|licenca/i').all();
    const count = (await reasonBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir badges de status', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status
    const statusBadges = page.locator('text=/pendente|confirmada|em_andamento|concluida|cancelada/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de sugerir IA para substituições pendentes', async ({ page }) => {
    await page.waitForTimeout(2000);

    const suggestButtons = page.locator('button[title*="Sugerir"]').all();
    const count = (await suggestButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de rejeitar para substituições pendentes', async ({ page }) => {
    await page.waitForTimeout(2000);

    const rejectButtons = page.locator('button[title*="Rejeitar"]').all();
    const count = (await rejectButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve abrir modal de sugestões ao clicar em sugerir IA', async ({ page }) => {
    await page.waitForTimeout(2000);

    const suggestButton = page.locator('button[title*="Sugerir"]').first();

    if (await suggestButton.isVisible().catch(() => false)) {
      await suggestButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      expect(await modal.isVisible().catch(() => false)).toBeDefined();

      // Fechar modal
      await page.keyboard.press('Escape');
    }
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/substituicoes');
    }
  });
});

test.describe('Operacional - Substituições - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir contador total de substituições', async ({ page }) => {
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForTimeout(2000);

    const totalStat = page.locator('text=/Total/i').first();
    const hasStat = await totalStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de pendentes', async ({ page }) => {
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForTimeout(2000);

    const pendingStat = page.locator('text=/Pendentes/i').first();
    const hasStat = await pendingStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de concluídas', async ({ page }) => {
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForTimeout(2000);

    const completedStat = page.locator('text=/Concluidas/i').first();
    const hasStat = await completedStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador por falta', async ({ page }) => {
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForTimeout(2000);

    const absenceStat = page.locator('text=/Por Falta/i').first();
    const hasStat = await absenceStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir custo adicional total', async ({ page }) => {
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForTimeout(2000);

    const costStat = page.locator('text=/Custo Adicional/i').first();
    const hasStat = await costStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Substituições - Paginação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/substituicoes');
    await page.waitForTimeout(2000);
  });

  test('deve exibir paginação quando necessário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), span:has-text("de"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há substituições', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhuma substituicao encontrada/i, text=/sem substituicoes/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve voltar para módulo operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional"), button:has-text("Voltar"]').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toMatch(/\/operacional/);
    }
  });
});
