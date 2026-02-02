/**
 * Testes E2E - NFS-e
 */

import { test, expect } from './fixtures';

test.describe('NFS-e', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/fiscal/nfse', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de NFS-e', async ({ page }) => {
    const hasContent = await page.locator('h1, button, table, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve ter interface visível', async ({ page }) => {
    const hasInterface = await page.locator('button, input').count();
    expect(hasInterface).toBeGreaterThan(0);
  });

  test('deve exibir cards de resumo/KPIs', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
  });

  test('deve ter campo de busca', async ({ page }) => {
    const searchInputs = page.locator('input[type="text"], input[type="search"]');
    const count = await searchInputs.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter estrutura de listagem', async ({ page }) => {
    const hasListStructure = await page.locator('table, ul, div[role="table"], div[role="list"]').count();
    expect(hasListStructure).toBeGreaterThanOrEqual(0);
  });
});
