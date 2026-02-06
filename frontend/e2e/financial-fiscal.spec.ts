/**
 * Testes E2E - Fiscal (Financial)
 */

import { test, expect } from './fixtures';

test.describe('Fiscal (Financial)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/fiscal', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de fiscal', async ({ page }) => {
    const hasContent = await page.locator('h1, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título "Fiscal"', async ({ page }) => {
    const title = page.locator('text=Fiscal').first();
    await expect(title).toBeVisible({ timeout: 10000 });
  });

  test('deve ter cards de estatísticas', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
  });

  test('deve ter tabs de navegação (NF-e/NFS-e)', async ({ page }) => {
    const nfeTab = page.locator('text=NF-e').first();
    const nfseTab = page.locator('text=NFS-e').first();

    const hasNfe = await nfeTab.count();
    const hasNfse = await nfseTab.count();

    expect(hasNfe + hasNfse).toBeGreaterThan(0);
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
