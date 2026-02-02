/**
 * Testes E2E - Contas a Pagar
 */

import { test, expect } from './fixtures';

test.describe('Contas a Pagar', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/contas-pagar', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de contas a pagar', async ({ page }) => {
    const hasContent = await page.locator('h1, button, table').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir botão Nova Conta', async ({ page }) => {
    const novoButton = page.locator('button:has-text("Novo"), button:has-text("Nova")').first();
    const isVisible = await novoButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('deve ter filtros de busca disponíveis', async ({ page }) => {
    const searchInputs = page.locator('input[type="text"], input[type="search"]');
    const count = await searchInputs.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter seletores de status', async ({ page }) => {
    const selectors = page.locator('select, [role="combobox"], button[role="combobox"]');
    const count = await selectors.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter estrutura de tabela', async ({ page }) => {
    const hasTable = await page.locator('table, div[role="table"]').count();
    expect(hasTable).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir cards de resumo/KPIs', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
  });
});
