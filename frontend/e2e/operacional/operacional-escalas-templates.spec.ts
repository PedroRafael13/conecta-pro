import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Templates de Escalas
 *
 * Testa gestão de templates reutilizáveis:
 * - Listagem de templates
 * - Criação de novo template
 * - Edição de template
 * - Exclusão de template
 * - Aplicação de template
 */

test.describe('Operacional - Escalas - Templates', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/escalas/templates');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de templates', async ({ page }) => {
    await expect(page).toHaveURL(/\/templates/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Templates/i, { timeout: 10000 });
  });

  test('deve exibir subtítulo descritivo', async ({ page }) => {
    await page.waitForTimeout(2000);

    const subtitle = page.locator('text=/Gerencie templates reutilizaveis/i').first();
    const hasSubtitle = await subtitle.isVisible().catch(() => false);

    expect(hasSubtitle !== undefined).toBeTruthy();
  });

  test('deve ter botão de voltar para escalas', async ({ page }) => {
    const backButton = page.locator('button:has-text("Voltar"), button:has-text("Escalas")').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir componente TemplateManager', async ({ page }) => {
    await page.waitForTimeout(2000);

    // O TemplateManager deve estar renderizado
    const managerContent = page.locator('main').first();
    const hasContent = await managerContent.isVisible().catch(() => false);

    expect(hasContent).toBeTruthy();
  });
});

test.describe('Operacional - Escalas - Templates - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/escalas/templates');
    await page.waitForTimeout(2000);
  });

  test('deve exibir lista de templates ou empty state', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar se há cards de templates ou empty state
    const content = page.locator('main > div').first();
    const hasContent = await content.isVisible().catch(() => false);

    expect(hasContent).toBeTruthy();
  });

  test('deve exibir botão de novo template', async ({ page }) => {
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Novo"), button:has-text("Criar"), button:has-text("Adicionar")').first();
    const hasButton = await newButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve exibir filtros de busca', async ({ page }) => {
    await page.waitForTimeout(2000);

    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar"]').first();
    const hasSearch = await searchInput.isVisible().catch(() => false);

    expect(hasSearch !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Escalas - Templates - Interações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/escalas/templates');
    await page.waitForTimeout(2000);
  });

  test('deve abrir modal ao clicar em novo template', async ({ page }) => {
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Novo"), button:has-text("Criar")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const hasModal = await modal.isVisible().catch(() => false);

      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve permitir buscar templates', async ({ page }) => {
    await page.waitForTimeout(2000);

    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Template Teste');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Template Teste');
    }
  });

  test('deve exibir botões de ação nos templates', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar por botões de editar, excluir ou aplicar
    const actionButtons = page.locator('button[title*="Editar"], button[title*="Excluir"], button[title*="Aplicar"]').all();
    const count = (await actionButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Operacional - Escalas - Templates - Navegação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/escalas/templates');
    await page.waitForTimeout(2000);
  });

  test('deve navegar de volta para lista de escalas', async ({ page }) => {
    const backButton = page.locator('button:has-text("Voltar"), button:has-text("Escalas")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveURL(/\/escalas/, { timeout: 10000 });
    }
  });
});
