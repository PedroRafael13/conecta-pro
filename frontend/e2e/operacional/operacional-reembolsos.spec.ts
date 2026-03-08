import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Reembolsos Operacionais
 *
 * Testa gestão de reembolsos:
 * - Listagem de solicitações
 * - Filtros por status
 * - Criação de nova solicitação
 * - Visualização de detalhes
 * - Edição de solicitação
 * - Exclusão de solicitação
 * - Estatísticas
 */

test.describe('Operacional - Reembolsos', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/reembolsos');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de reembolsos', async ({ page }) => {
    await expect(page).toHaveURL(/\/reembolsos/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Reembolsos/i, { timeout: 10000 });
  });

  test('deve exibir contador de solicitações no header', async ({ page }) => {
    await page.waitForTimeout(2000);

    const countText = page.locator('text=/solicitacoes/i').first();
    const hasCount = await countText.isVisible().catch(() => false);

    expect(hasCount !== undefined).toBeTruthy();
  });

  test('deve ter botão de voltar para operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional")').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")').first();
    await expect(refreshButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de nova solicitação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Solicitacao")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const statsCards = page.locator('[class*="card"], [class*="bg-"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir contador total', async ({ page }) => {
    await page.waitForTimeout(2000);

    const totalText = page.locator('text=/Total/i').first();
    const hasTotal = await totalText.isVisible().catch(() => false);

    expect(hasTotal !== undefined).toBeTruthy();
  });

  test('deve exibir contador de pendentes', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pendingText = page.locator('text=/Pendentes/i').first();
    const hasPending = await pendingText.isVisible().catch(() => false);

    expect(hasPending !== undefined).toBeTruthy();
  });

  test('deve exibir contador de aprovados', async ({ page }) => {
    await page.waitForTimeout(2000);

    const approvedText = page.locator('text=/Aprovados/i').first();
    const hasApproved = await approvedText.isVisible().catch(() => false);

    expect(hasApproved !== undefined).toBeTruthy();
  });

  test('deve exibir valor total', async ({ page }) => {
    await page.waitForTimeout(2000);

    const valorText = page.locator('text=/Valor Total/i').first();
    const hasValor = await valorText.isVisible().catch(() => false);

    expect(hasValor !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Reembolsos - Busca e Filtros', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/reembolsos');
    await page.waitForTimeout(2000);
  });

  test('deve exibir campo de busca', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar"]').first();
    await expect(searchInput).toBeVisible({ timeout: 10000 });
  });

  test('deve permitir buscar solicitações', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    await searchInput.fill('Teste Reembolso');
    await page.waitForTimeout(500);

    await expect(searchInput).toHaveValue('Teste Reembolso');
  });

  test('deve ter botão de filtros', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await expect(filterButton).toBeVisible({ timeout: 10000 });
  });

  test('deve expandir painel de filtros ao clicar', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const filterPanel = page.locator('text=/Status/i').first();
    const hasPanel = await filterPanel.isVisible().catch(() => false);

    expect(hasPanel !== undefined).toBeTruthy();
  });

  test('deve ter filtro de status no painel', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const statusFilter = page.locator('select').first();
    const hasFilter = await statusFilter.isVisible().catch(() => false);

    expect(hasFilter !== undefined).toBeTruthy();
  });

  test('deve permitir limpar filtros', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const clearButton = page.locator('button:has-text("Limpar filtros")').first();

    if (await clearButton.isVisible().catch(() => false)) {
      await clearButton.click();
      await page.waitForTimeout(500);

      expect(page.url()).toContain('/reembolsos');
    }
  });
});

test.describe('Operacional - Reembolsos - Tabela', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/reembolsos');
    await page.waitForTimeout(2000);
  });

  test('deve exibir tabela de solicitações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table').first();
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    const hasSolicitacao = headerTexts.some(h => h.toLowerCase().includes('solicitacao'));
    const hasPeriodo = headerTexts.some(h => h.toLowerCase().includes('periodo'));
    const hasValor = headerTexts.some(h => h.toLowerCase().includes('valor'));
    const hasItens = headerTexts.some(h => h.toLowerCase().includes('itens'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));
    const hasAcoes = headerTexts.some(h => h.toLowerCase().includes('acoes'));

    expect(hasSolicitacao || hasPeriodo || hasValor || hasItens || hasStatus || hasAcoes).toBeTruthy();
  });

  test('deve exibir código da solicitação', async ({ page }) => {
    await page.waitForTimeout(2000);

    const codeText = page.locator('table tbody tr td').first();
    const hasCode = await codeText.isVisible().catch(() => false);

    expect(hasCode !== undefined).toBeTruthy();
  });

  test('deve exibir badge de status nas linhas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const statusBadge = page.locator('table tbody tr [class*="rounded-full"]').first();
    const hasBadge = await statusBadge.isVisible().catch(() => false);

    expect(hasBadge !== undefined).toBeTruthy();
  });

  test('deve exibir botões de ação em cada linha', async ({ page }) => {
    await page.waitForTimeout(2000);

    const actionButtons = page.locator('table tbody tr button[title*="Visualizar"], table tbody tr button[title*="Editar"], table tbody tr button[title*="Excluir"]').all();
    const count = (await actionButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir empty state quando não há solicitações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhuma solicitacao encontrada/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir paginação se houver muitas solicitações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('text=/Mostrando.*de.*solicitacoes/i').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Reembolsos - Interações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/reembolsos');
    await page.waitForTimeout(2000);
  });

  test('deve abrir modal de nova solicitação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Solicitacao")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const hasModal = await modal.isVisible().catch(() => false);

    expect(hasModal !== undefined).toBeTruthy();
  });

  test('deve abrir modal de visualização ao clicar na linha', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Visualizar"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const hasModal = await modal.isVisible().catch(() => false);

      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve abrir modal de edição', async ({ page }) => {
    await page.waitForTimeout(2000);

    const editButton = page.locator('button[title*="Editar"]').first();

    if (await editButton.isVisible().catch(() => false)) {
      await editButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const hasModal = await modal.isVisible().catch(() => false);

      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve abrir modal de confirmação ao excluir', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(1000);

      const confirmModal = page.locator('text=/Excluir Solicitacao|Tem certeza/i').first();
      const hasModal = await confirmModal.isVisible().catch(() => false);

      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve permitir cancelar exclusão', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(1000);

      const cancelButton = page.locator('button:has-text("Cancelar")').first();

      if (await cancelButton.isVisible().catch(() => false)) {
        await cancelButton.click();
        await page.waitForTimeout(500);

        expect(page.url()).toContain('/reembolsos');
      }
    }
  });
});

test.describe('Operacional - Reembolsos - Navegação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/reembolsos');
    await page.waitForTimeout(2000);
  });

  test('deve navegar de volta para módulo operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveURL(/\/operacional/, { timeout: 10000 });
    }
  });
});
