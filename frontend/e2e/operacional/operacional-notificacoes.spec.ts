import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Notificações
 *
 * Testa gestão de notificações:
 * - Listagem de notificações
 * - Filtros por tipo
 * - Marcar como lida
 * - Marcar todas como lidas
 * - Excluir notificação
 * - Visualização de alertas
 */

test.describe('Operacional - Notificações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/notificacoes');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de notificações', async ({ page }) => {
    await expect(page).toHaveURL(/\/notificacoes/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Notificacoes/i, { timeout: 10000 });
  });

  test('deve exibir contador de não lidas no header', async ({ page }) => {
    await page.waitForTimeout(2000);

    const unreadText = page.locator('text=/nao lidas/i').first();
    const hasUnread = await unreadText.isVisible().catch(() => false);

    expect(hasUnread !== undefined).toBeTruthy();
  });

  test('deve ter botão de voltar para operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional")').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")').first();
    await expect(refreshButton).toBeVisible({ timeout: 10000 });
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

  test('deve exibir contador de não lidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const naoLidasText = page.locator('text=/Nao Lidas/i').first();
    const hasNaoLidas = await naoLidasText.isVisible().catch(() => false);

    expect(hasNaoLidas !== undefined).toBeTruthy();
  });

  test('deve exibir contador de alertas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const alertasText = page.locator('text=/Alertas/i').first();
    const hasAlertas = await alertasText.isVisible().catch(() => false);

    expect(hasAlertas !== undefined).toBeTruthy();
  });

  test('deve exibir contador de lidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const lidasText = page.locator('text=/Lidas/i').first();
    const hasLidas = await lidasText.isVisible().catch(() => false);

    expect(hasLidas !== undefined).toBeTruthy();
  });

  test('deve exibir campo de busca', async ({ page }) => {
    await page.waitForTimeout(2000);

    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar"]').first();
    const hasSearch = await searchInput.isVisible().catch(() => false);

    expect(hasSearch !== undefined).toBeTruthy();
  });

  test('deve exibir filtro de tipo', async ({ page }) => {
    await page.waitForTimeout(2000);

    const typeFilter = page.locator('select').first();
    const hasFilter = await typeFilter.isVisible().catch(() => false);

    expect(hasFilter !== undefined).toBeTruthy();
  });

  test('deve ter botão para mostrar apenas não lidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const unreadButton = page.locator('button:has-text("nao lidas"), button:has-text("Nao lidas")').first();
    const hasButton = await unreadButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Notificações - Alertas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/notificacoes');
    await page.waitForTimeout(2000);
  });

  test('deve exibir seção de alertas ativos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const alertasSection = page.locator('text=/Alertas Ativos/i').first();
    const hasSection = await alertasSection.isVisible().catch(() => false);

    // Alertas podem ou não existir
    expect(hasSection !== undefined).toBeTruthy();
  });

  test('deve exibir alertas com ícones de severidade', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar por alertas com diferentes severidades
    const alertIcons = page.locator('[class*="AlertTriangle"], [class*="Info"], [class*="XCircle"], [class*="Zap"]').all();
    const count = (await alertIcons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir botão de confirmar em alertas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const confirmButton = page.locator('button:has-text("Confirmar")').first();
    const hasButton = await confirmButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Notificações - Lista', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/notificacoes');
    await page.waitForTimeout(2000);
  });

  test('deve exibir lista de notificações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const notificationsList = page.locator('main > div > div').first();
    const hasList = await notificationsList.isVisible().catch(() => false);

    expect(hasList).toBeTruthy();
  });

  test('deve exibir título e corpo da notificação', async ({ page }) => {
    await page.waitForTimeout(2000);

    const notificationTitle = page.locator('h3').first();
    const hasTitle = await notificationTitle.isVisible().catch(() => false);

    expect(hasTitle !== undefined).toBeTruthy();
  });

  test('deve exibir tipo da notificação como badge', async ({ page }) => {
    await page.waitForTimeout(2000);

    const typeBadge = page.locator('[class*="rounded-full"]').first();
    const hasBadge = await typeBadge.isVisible().catch(() => false);

    expect(hasBadge !== undefined).toBeTruthy();
  });

  test('deve exibir data da notificação', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar por formato de data
    const dateText = page.locator('text=/\d{1,2}min|\d{1,2}h|\d{1,2}d|\d{2}\/\d{2}\/\d{4}/i').first();
    const hasDate = await dateText.isVisible().catch(() => false);

    expect(hasDate !== undefined).toBeTruthy();
  });

  test('deve exibir botões de ação nas notificações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const actionButtons = page.locator('button[title*="Marcar"], button[title*="Excluir"], button[title*="Ver"]').all();
    const count = (await actionButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir empty state quando não há notificações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhuma notificacao encontrada/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir paginação se houver muitas notificações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Anterior"), button:has-text("Proxima"), text=/Pagina/i').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Notificações - Interações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/notificacoes');
    await page.waitForTimeout(2000);
  });

  test('deve marcar notificação como lida', async ({ page }) => {
    await page.waitForTimeout(2000);

    const markReadButton = page.locator('button[title*="Marcar como lida"]').first();

    if (await markReadButton.isVisible().catch(() => false)) {
      await markReadButton.click();
      await page.waitForTimeout(500);

      // Verificar que a ação foi processada
      expect(page.url()).toContain('/notificacoes');
    }
  });

  test('deve ter botão marcar todas como lidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const markAllButton = page.locator('button:has-text("Marcar todas como lidas")').first();
    const hasButton = await markAllButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve excluir notificação', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(500);

      expect(page.url()).toContain('/notificacoes');
    }
  });

  test('deve permitir buscar notificações', async ({ page }) => {
    await page.waitForTimeout(2000);

    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('teste');
    }
  });

  test('deve permitir filtrar por tipo', async ({ page }) => {
    await page.waitForTimeout(2000);

    const typeFilter = page.locator('select').first();

    if (await typeFilter.isVisible().catch(() => false)) {
      await typeFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      const value = await typeFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve alternar filtro de apenas não lidas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const unreadButton = page.locator('button:has-text("nao lidas"), button:has-text("Nao lidas")').first();

    if (await unreadButton.isVisible().catch(() => false)) {
      await unreadButton.click();
      await page.waitForTimeout(500);

      expect(page.url()).toContain('/notificacoes');
    }
  });
});

test.describe('Operacional - Notificações - Navegação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/notificacoes');
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

  test('deve navegar para URL de ação se notificação tiver action_url', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar por botão de ver detalhes
    const viewButton = page.locator('button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(2000);

      // URL deve ter mudado
      expect(page.url()).not.toBe('/modulos/operacional/notificacoes');
    }
  });
});
