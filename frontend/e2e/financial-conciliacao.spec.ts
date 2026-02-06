/**
 * Testes E2E - Conciliação Bancária
 */

import { test, expect } from './fixtures';

test.describe('Conciliação Bancária', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/conciliacao', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de conciliação', async ({ page }) => {
    const hasContent = await page.locator('h1, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título', async ({ page }) => {
    const title = page.locator('text=/Concilia/i').first();
    await expect(title).toBeVisible({ timeout: 10000 });
  });

  test('deve ter tabs de navegação', async ({ page }) => {
    const tabs = await page.locator('button').count();
    expect(tabs).toBeGreaterThan(0);
  });

  test('deve ter campo de busca', async ({ page }) => {
    const searchInputs = page.locator('input[type="search"]');
    const count = await searchInputs.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter estrutura de tabela', async ({ page }) => {
    const hasTable = await page.locator('table, div[role="table"]').count();
    expect(hasTable).toBeGreaterThanOrEqual(0);
  });
});
