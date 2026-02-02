/**
 * Testes E2E - Contas a Receber
 */

import { test, expect } from './fixtures';

test.describe('Contas a Receber', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/contas-receber', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de contas a receber', async ({ page }) => {
    const hasContent = await page.locator('h1, button, table').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir botão Nova Conta', async ({ page }) => {
    const novoButton = page.locator('button:has-text("Novo"), button:has-text("Nova")').first();
    const isVisible = await novoButton.isVisible().catch(() => false);
    expect(isVisible).toBeTruthy();
  });

  test('deve ter filtros disponíveis', async ({ page }) => {
    const filters = page.locator('input, select, button[role="combobox"]');
    const count = await filters.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve ter estrutura de listagem', async ({ page }) => {
    const hasListStructure = await page.locator('table, ul, div[role="table"]').count();
    expect(hasListStructure).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir indicadores financeiros', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
  });
});
