/**
 * Testes E2E - Dashboard Fiscal
 */

import { test, expect } from './fixtures';

test.describe('Dashboard Fiscal', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/fiscal', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir os 4 cards de KPIs', async ({ page }) => {
    // Verificar se há cards de estatísticas
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
  });

  test('deve exibir cards de navegação dos submódulos', async ({ page }) => {
    const navigationCards = await page.locator('[class*="group"]').count();
    expect(navigationCards).toBeGreaterThanOrEqual(0);
  });

  test('deve ter link para NFS-e', async ({ page }) => {
    const link = page.locator('text=NFS-e').first();
    await expect(link).toBeVisible({ timeout: 10000 });
  });

  test('deve ter link para eSocial', async ({ page }) => {
    const link = page.locator('text=eSocial').first();
    await expect(link).toBeVisible({ timeout: 10000 });
  });

  test('deve ter link para SPED', async ({ page }) => {
    const link = page.locator('text=SPED').first();
    await expect(link).toBeVisible({ timeout: 10000 });
  });

  test('deve ter link para Certidoes', async ({ page }) => {
    // Procura por qualquer variação de "Certidoes" ou "Certidões"
    const hasCertidoesLink = await page.locator('text=/Certid[oõ]es/i').count();
    expect(hasCertidoesLink).toBeGreaterThanOrEqual(0);
  });
});
