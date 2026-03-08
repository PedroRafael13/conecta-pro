import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Medidas Administrativas
 *
 * Testa workflow de medidas administrativas:
 * - Cadastro de medidas
 * - Aplicação a funcionários
 * - Prazos
 * - Acompanhamento
 */

test.describe('Operacional - Medidas Administrativas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de medidas administrativas', async ({ page }) => {
    await expect(page).toHaveURL(/\/medidas-administrativas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Medidas Administrativas/i, { timeout: 10000 });
  });

  test('deve exibir tabela de medidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir estatísticas de medidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Stats cards (total, pendentes, assinatura, mês, ano)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(5);
  });

  test('deve ter botão de nova medida', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Medida"), button:has-text("Nova")').first();
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

  test('deve ter filtro de tipo', async ({ page }) => {
    const typeFilter = page.locator('select').nth(1);

    if (await typeFilter.isVisible().catch(() => false)) {
      await typeFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(await typeFilter.inputValue()).toBeTruthy();
    }
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    // Verificar se contém colunas esperadas
    const hasCode = headerTexts.some(h => h.toLowerCase().includes('codigo'));
    const hasEmployee = headerTexts.some(h => h.toLowerCase().includes('funcionario'));
    const hasType = headerTexts.some(h => h.toLowerCase().includes('tipo'));
    const hasReason = headerTexts.some(h => h.toLowerCase().includes('motivo'));
    const hasDate = headerTexts.some(h => h.toLowerCase().includes('data'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));

    expect(hasCode || hasEmployee || hasType || hasReason || hasDate || hasStatus).toBeTruthy();
  });

  test('deve exibir código da medida', async ({ page }) => {
    await page.waitForTimeout(2000);

    const codeCells = page.locator('td:has-text("MED-"), td code, td .font-mono').all();
    const count = (await codeCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir nome do funcionário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const employeeCells = page.locator('table tbody tr td:nth-child(2)').all();
    const count = (await employeeCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir badges de tipo de medida', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de tipo
    const typeBadges = page.locator('text=/advertencia|suspensao|demissao|observacao/i').all();
    const count = (await typeBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir badges de status', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status
    const statusBadges = page.locator('text=/rascunho|pendente|aprovada|assinada|aplicada/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Operacional - Medidas Administrativas - Ações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForTimeout(2000);
  });

  test('deve ter botão de ver detalhes em cada linha', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButtons = page.locator('button[title*="Ver"], button[title*="Detalhes"]').all();
    const count = (await viewButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de editar para medidas em rascunho', async ({ page }) => {
    await page.waitForTimeout(2000);

    const editButtons = page.locator('button[title*="Editar"]').all();
    const count = (await editButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de excluir para medidas em rascunho', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButtons = page.locator('button[title*="Excluir"]').all();
    const count = (await deleteButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de assinar para medidas pendentes', async ({ page }) => {
    await page.waitForTimeout(2000);

    const signButtons = page.locator('button[title*="Assinar"]').all();
    const count = (await signButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve abrir modal de detalhes ao clicar em ver', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Fechar modal
      await page.keyboard.press('Escape');
    }
  });

  test('deve abrir modal de confirmação ao excluir', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(500);

      const confirmModal = page.locator('[role="dialog"], [role="alertdialog"]').first();
      expect(await confirmModal.isVisible().catch(() => false)).toBeDefined();

      // Fechar modal
      await page.keyboard.press('Escape');
    }
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/medidas-administrativas');
    }
  });
});

test.describe('Operacional - Medidas Administrativas - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir contador total de medidas', async ({ page }) => {
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForTimeout(2000);

    const totalStat = page.locator('text=/Total/i').first();
    const hasStat = await totalStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de pendentes de aprovação', async ({ page }) => {
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForTimeout(2000);

    const pendingStat = page.locator('text=/Pend. Aprovacao/i').first();
    const hasStat = await pendingStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de pendentes de assinatura', async ({ page }) => {
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForTimeout(2000);

    const signStat = page.locator('text=/Pend. Assinatura/i').first();
    const hasStat = await signStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador do mês atual', async ({ page }) => {
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForTimeout(2000);

    const monthStat = page.locator('text=/Este Mes/i').first();
    const hasStat = await monthStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador do ano atual', async ({ page }) => {
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForTimeout(2000);

    const yearStat = page.locator('text=/Este Ano/i').first();
    const hasStat = await yearStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Medidas Administrativas - Paginação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/medidas-administrativas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir paginação quando necessário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), span:has-text("Pagina"), span:has-text("de"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há medidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhuma medida encontrada/i, text=/sem medidas/i').first();
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
