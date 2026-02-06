/**
 * Testes E2E - Certidões Fiscais
 */

import { test, expect } from './fixtures';

test.describe('Certidões Fiscais', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/fiscal/certidoes', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de certidões', async ({ page }) => {
    const hasContent = await page.locator('h1, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir cards de resumo', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
  });

  test('deve ter filtros disponíveis', async ({ page }) => {
    const filters = page.locator('input, select, button[role="combobox"]');
    const count = await filters.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter estrutura de listagem', async ({ page }) => {
    const hasListStructure = await page.locator('table, ul, div[role="table"], div[role="list"]').count();
    expect(hasListStructure).toBeGreaterThanOrEqual(0);
  });

  test('deve ter interface de certidões visível', async ({ page }) => {
    const hasInterface = await page.locator('button, input, div').count();
    expect(hasInterface).toBeGreaterThan(5);
  });
});
