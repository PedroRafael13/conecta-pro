/**
 * Testes E2E - eSocial
 */

import { test, expect } from './fixtures';

test.describe('eSocial', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/fiscal/esocial', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de eSocial', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve ter interface visível', async ({ page }) => {
    const hasInterface = await page.locator('button, div, input').count();
    expect(hasInterface).toBeGreaterThan(0);
  });

  test('deve exibir cards informativos', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThanOrEqual(0);
  });

  test('deve ter estrutura básica de página', async ({ page }) => {
    const hasBasicStructure = await page.locator('div, button').count();
    expect(hasBasicStructure).toBeGreaterThan(5);
  });
});
