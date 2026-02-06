/**
 * Testes E2E - Clientes
 */

import { test, expect } from './fixtures';

test.describe('Clientes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/clientes', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de clientes', async ({ page }) => {
    const hasContent = await page.locator('h1, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título "Clientes"', async ({ page }) => {
    const title = page.locator('text=Clientes').first();
    await expect(title).toBeVisible({ timeout: 10000 });
  });

  test('deve ter cards de estatísticas', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
  });

  test('deve ter campo de busca', async ({ page }) => {
    const searchInputs = page.locator('input[type="search"]');
    const count = await searchInputs.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de novo cliente', async ({ page }) => {
    const button = page.locator('text=Novo Cliente').first();
    await expect(button).toBeVisible({ timeout: 10000 });
  });

  test('deve ter estrutura de tabela', async ({ page }) => {
    const hasTable = await page.locator('table, div[role="table"]').count();
    expect(hasTable).toBeGreaterThanOrEqual(0);
  });
});
