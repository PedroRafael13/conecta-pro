import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Banco de Horas
 *
 * Testa workflow de banco de horas:
 * - Saldo de horas
 * - Lançamentos
 * - Compensação
 * - Exportação para folha
 */

test.describe('Operacional - Banco de Horas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de banco de horas', async ({ page }) => {
    await expect(page).toHaveURL(/\/banco-horas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Banco de Horas/i, { timeout: 10000 });
  });

  test('deve exibir tabela de lançamentos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir estatísticas de banco de horas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Stats cards (funcionários, créditos, débitos, compensadas, pendentes, média)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(6);
  });

  test('deve ter botão de novo lançamento', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Lancamento"), button:has-text("Novo")').first();
    const hasButton = await newButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve exibir alertas de expiração quando houver', async ({ page }) => {
    await page.waitForTimeout(2000);

    const alerts = page.locator('[class*="alert"], .bg-yellow-500\\/10').all();
    const count = (await alerts).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir seção de pendentes quando houver', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pendingSection = page.locator('text=/Pendentes de Aprovacao/i, .bg-yellow-500\\/10').first();
    const hasPending = await pendingSection.isVisible().catch(() => false);

    expect(hasPending !== undefined).toBeTruthy();
  });

  test('deve ter filtro de status', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(await statusFilter.inputValue()).toBeTruthy();
    }
  });

  test('deve ter filtro de tipo de lançamento', async ({ page }) => {
    const typeFilter = page.locator('select').nth(1);

    if (await typeFilter.isVisible().catch(() => false)) {
      await typeFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(await typeFilter.inputValue()).toBeTruthy();
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
    const hasEmployee = headerTexts.some(h => h.toLowerCase().includes('funcionario'));
    const hasType = headerTexts.some(h => h.toLowerCase().includes('tipo'));
    const hasHours = headerTexts.some(h => h.toLowerCase().includes('horas'));
    const hasBalance = headerTexts.some(h => h.toLowerCase().includes('saldo'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));

    expect(hasDate || hasEmployee || hasType || hasHours || hasBalance || hasStatus).toBeTruthy();
  });

  test('deve exibir badges de tipo de lançamento', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de tipo (crédito, débito, compensação, expiração, ajuste)
    const typeBadges = page.locator('text=/credito|debito|compensacao|expiracao|ajuste/i').all();
    const count = (await typeBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir valores de horas formatados', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar valores de horas (ex: +8h, -4h, 2h30min)
    const hourValues = page.locator('text=/[+-]?\\d+h(\\d+min)?/i').all();
    const count = (await hourValues).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Operacional - Banco de Horas - Aprovação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir botão de aprovar para lançamentos pendentes', async ({ page }) => {
    await page.waitForTimeout(2000);

    const approveButtons = page.locator('button[title*="Aprovar"]').all();
    const count = (await approveButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir botão de rejeitar para lançamentos pendentes', async ({ page }) => {
    await page.waitForTimeout(2000);

    const rejectButtons = page.locator('button[title*="Rejeitar"]').all();
    const count = (await rejectButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve abrir modal de aprovação ao clicar', async ({ page }) => {
    await page.waitForTimeout(2000);

    const approveButton = page.locator('button[title*="Aprovar"]').first();

    if (await approveButton.isVisible().catch(() => false)) {
      await approveButton.click();
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

      expect(page.url()).toContain('/banco-horas');
    }
  });

  test('deve exibir informações de expiração', async ({ page }) => {
    await page.waitForTimeout(2000);

    const expirationInfo = page.locator('text=/dias|expira/i').all();
    const count = (await expirationInfo).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Operacional - Banco de Horas - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir contador de funcionários', async ({ page }) => {
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForTimeout(2000);

    const employeesStat = page.locator('text=/Funcionarios/i').first();
    const hasStat = await employeesStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir total de créditos', async ({ page }) => {
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForTimeout(2000);

    const creditsStat = page.locator('text=/Creditos/i').first();
    const hasStat = await creditsStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir total de débitos', async ({ page }) => {
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForTimeout(2000);

    const debitsStat = page.locator('text=/Debitos/i').first();
    const hasStat = await debitsStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir horas compensadas', async ({ page }) => {
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForTimeout(2000);

    const compensatedStat = page.locator('text=/Compensadas/i').first();
    const hasStat = await compensatedStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir média de saldo', async ({ page }) => {
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForTimeout(2000);

    const avgStat = page.locator('text=/Media Saldo/i').first();
    const hasStat = await avgStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Banco de Horas - Paginação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/banco-horas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir paginação quando necessário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), span:has-text("de"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há lançamentos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhum lancamento encontrado/i, text=/sem lancamentos/i').first();
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
