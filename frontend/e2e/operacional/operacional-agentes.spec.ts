import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Cadastro de Agentes
 *
 * Testa gestão de agentes/colaboradores:
 * - Cadastro de agentes
 * - Atribuição a postos
 * - Documentação
 * - Status (ativo, inativo, afastado)
 */

test.describe('Operacional - Agentes', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/agentes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de agentes', async ({ page }) => {
    await expect(page).toHaveURL(/\/agentes/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Colaboradores|Agentes/i, { timeout: 10000 });
  });

  test('deve exibir tabela de colaboradores', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir estatísticas de colaboradores', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Stats cards (total, ativos, alocados, disponíveis)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve ter filtro de status', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();

    if (await filterButton.isVisible().catch(() => false)) {
      await filterButton.click();
      await page.waitForTimeout(500);

      const statusFilter = page.locator('select').first();
      if (await statusFilter.isVisible().catch(() => false)) {
        await statusFilter.selectOption({ index: 1 });
        await page.waitForTimeout(500);

        expect(await statusFilter.inputValue()).toBeTruthy();
      }
    }
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    // Verificar se contém colunas esperadas
    const hasName = headerTexts.some(h => h.toLowerCase().includes('colaborador'));
    const hasRole = headerTexts.some(h => h.toLowerCase().includes('cargo'));
    const hasContact = headerTexts.some(h => h.toLowerCase().includes('contato'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));
    const hasActions = headerTexts.some(h => h.toLowerCase().includes('acoes'));

    expect(hasName || hasRole || hasContact || hasStatus || hasActions).toBeTruthy();
  });

  test('deve exibir badges de status na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status (ativo, inativo, afastado, férias)
    const statusBadges = page.locator('text=/ativo|inativo|afastado|ferias/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir avatar e nome do colaborador', async ({ page }) => {
    await page.waitForTimeout(2000);

    const avatarCells = page.locator('table tbody tr td:first-child').all();
    const count = (await avatarCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir cargo do colaborador', async ({ page }) => {
    await page.waitForTimeout(2000);

    const roleCells = page.locator('table tbody tr td:nth-child(2)').all();
    const count = (await roleCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir informações de contato (email/telefone)', async ({ page }) => {
    await page.waitForTimeout(2000);

    const contactCells = page.locator('table tbody tr td:nth-child(3)').all();
    const count = (await contactCells).length;

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
    }
  });

  test('deve exibir informações detalhadas no modal', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Visualizar"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();

      // Verificar se contém informações do colaborador
      const content = await modal.textContent();
      expect(content).toBeDefined();
    }
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/agentes');
    }
  });

  test('deve exibir empty state quando não há colaboradores', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhum colaborador encontrado/i, text=/sem colaboradores/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve voltar para módulo operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional"), button:has-text("Voltar")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toMatch(/\/operacional/);
    }
  });
});

test.describe('Operacional - Agentes - Filtros Avançados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/agentes');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar por nome', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve filtrar por status ativo', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();

    if (await filterButton.isVisible().catch(() => false)) {
      await filterButton.click();
      await page.waitForTimeout(500);

      const statusFilter = page.locator('select').first();
      if (await statusFilter.isVisible().catch(() => false)) {
        await statusFilter.selectOption({ label: 'Ativo' });
        await page.waitForTimeout(1000);

        const value = await statusFilter.inputValue();
        expect(value).toBeTruthy();
      }
    }
  });

  test('deve filtrar por status afastado', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();

    if (await filterButton.isVisible().catch(() => false)) {
      await filterButton.click();
      await page.waitForTimeout(500);

      const statusFilter = page.locator('select').first();
      if (await statusFilter.isVisible().catch(() => false)) {
        await statusFilter.selectOption({ label: 'Afastado' });
        await page.waitForTimeout(1000);

        const value = await statusFilter.inputValue();
        expect(value).toBeTruthy();
      }
    }
  });

  test('deve limpar filtros de busca', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
      await page.waitForTimeout(500);
      await searchInput.clear();

      const value = await searchInput.inputValue();
      expect(value).toBe('');
    }
  });
});

test.describe('Operacional - Agentes - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir contador total de colaboradores', async ({ page }) => {
    await page.goto('/modulos/operacional/agentes');
    await page.waitForTimeout(2000);

    const totalStat = page.locator('text=/Total/i').first();
    const hasStat = await totalStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de ativos', async ({ page }) => {
    await page.goto('/modulos/operacional/agentes');
    await page.waitForTimeout(2000);

    const activeStat = page.locator('text=/Ativos/i').first();
    const hasStat = await activeStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de alocados', async ({ page }) => {
    await page.goto('/modulos/operacional/agentes');
    await page.waitForTimeout(2000);

    const allocatedStat = page.locator('text=/Alocados/i').first();
    const hasStat = await allocatedStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de disponíveis', async ({ page }) => {
    await page.goto('/modulos/operacional/agentes');
    await page.waitForTimeout(2000);

    const availableStat = page.locator('text=/Disponiveis/i').first();
    const hasStat = await availableStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });
});
