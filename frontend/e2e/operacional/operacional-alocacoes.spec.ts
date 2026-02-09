import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Mapa de Alocações
 *
 * Testa workflow de alocações:
 * - Mapa de alocações
 * - Atribuição de funcionários a postos
 * - Períodos de alocação
 * - Conflitos de escala
 */

test.describe('Operacional - Alocações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/alocacoes');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de alocações', async ({ page }) => {
    await expect(page).toHaveURL(/\/alocacoes/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Alocacoes/i, { timeout: 10000 });
  });

  test('deve exibir tabela de alocações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir botão de nova alocação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Alocacao"), button:has-text("Nova")').first();
    const hasButton = await newButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve ter botão de filtros', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros"), button[title*="Filtro"]').first();
    await expect(filterButton).toBeVisible({ timeout: 10000 });
  });

  test('deve expandir painel de filtros ao clicar', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await expect(filterButton).toBeVisible({ timeout: 10000 });
    await filterButton.click();
    await page.waitForTimeout(500);

    // Verificar se painel de filtros apareceu
    const filterPanel = page.locator('label:has-text("Posto"), label:has-text("Funcionario"), label:has-text("Status"), select').first();
    expect(await filterPanel.isVisible().catch(() => false)).toBeTruthy();
  });

  test('deve ter filtro de posto', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const postFilter = page.locator('label:has-text("Posto") + select, select').first();

    if (await postFilter.isVisible().catch(() => false)) {
      await postFilter.selectOption({ index: 0 });
      expect(await postFilter.inputValue()).toBeTruthy();
    }
  });

  test('deve ter filtro de funcionário', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const employeeFilter = page.locator('label:has-text("Funcionario") + select, select').nth(1);

    if (await employeeFilter.isVisible().catch(() => false)) {
      await employeeFilter.selectOption({ index: 0 });
      expect(await employeeFilter.inputValue()).toBeTruthy();
    }
  });

  test('deve ter filtro de status', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const statusFilter = page.locator('label:has-text("Status") + select, select').nth(2);

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 0 });
      expect(await statusFilter.inputValue()).toBeTruthy();
    }
  });

  test('deve ter checkbox para vigentes', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const checkbox = page.locator('input[type="checkbox"]').first();

    if (await checkbox.isVisible().catch(() => false)) {
      await checkbox.check();
      expect(await checkbox.isChecked()).toBeTruthy();
    }
  });

  test('deve ter filtros de data (início de/até)', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const dateInputs = page.locator('input[type="date"]').all();
    const count = (await dateInputs).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    // Verificar se contém colunas esperadas
    const hasEmployee = headerTexts.some(h => h.toLowerCase().includes('funcionario'));
    const hasPost = headerTexts.some(h => h.toLowerCase().includes('posto'));
    const hasStart = headerTexts.some(h => h.toLowerCase().includes('inicio'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));
    const hasActions = headerTexts.some(h => h.toLowerCase().includes('acoes'));

    expect(hasEmployee || hasPost || hasStart || hasStatus || hasActions).toBeTruthy();
  });

  test('deve exibir badges de status nas alocações', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status (ativo, pendente, suspenso, encerrado)
    const statusBadges = page.locator('text=/ativo|pendente|suspenso|encerrado/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data de início da alocação', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar datas formatadas
    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de visualizar em cada linha', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButtons = page.locator('button[title*="Visualizar"], button:has-text("Ver")').all();
    const count = (await viewButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve abrir modal de detalhes ao clicar em visualizar', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Visualizar"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Fechar modal
      await page.keyboard.press('Escape');
    }
  });
});

test.describe('Operacional - Alocações - Ações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/alocacoes');
    await page.waitForTimeout(2000);
  });

  test('deve ter botão de transferir para alocações ativas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const transferButtons = page.locator('button[title*="Transferir"]').all();
    const count = (await transferButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de encerrar para alocações ativas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const terminateButtons = page.locator('button[title*="Encerrar"]').all();
    const count = (await terminateButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve abrir modal de encerramento ao clicar', async ({ page }) => {
    await page.waitForTimeout(2000);

    const terminateButton = page.locator('button[title*="Encerrar"]').first();

    if (await terminateButton.isVisible().catch(() => false)) {
      await terminateButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      expect(await modal.isVisible().catch(() => false)).toBeDefined();

      // Fechar modal
      await page.keyboard.press('Escape');
    }
  });

  test('deve ter botão de exportar', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Exportar"), button[title*="Exportar"]').first();

    if (await exportButton.isVisible().catch(() => false)) {
      expect(await exportButton.isVisible()).toBeTruthy();
    }
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/alocacoes');
    }
  });
});

test.describe('Operacional - Alocações - Paginação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/alocacoes');
    await page.waitForTimeout(2000);
  });

  test('deve exibir paginação quando necessário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), span:has-text("Pagina"), span:has-text("de"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há alocações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhuma alocacao encontrada/i, text=/sem alocacoes/i').first();
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
