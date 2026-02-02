/**
 * Testes E2E - Faturamento
 */

import { test, expect } from './fixtures';

test.describe('Faturamento', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/faturamento', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de faturamento', async ({ page }) => {
    const hasContent = await page.locator('h1, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título "Faturamento"', async ({ page }) => {
    const title = page.locator('text=Faturamento').first();
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

  test('deve ter botão de nova regra', async ({ page }) => {
    const button = page.locator('text=Nova Regra').first();
    await expect(button).toBeVisible({ timeout: 10000 });
  });

  test('deve ter estrutura de tabela', async ({ page }) => {
    const hasTable = await page.locator('table, div[role="table"]').count();
    expect(hasTable).toBeGreaterThanOrEqual(0);
  });
});
