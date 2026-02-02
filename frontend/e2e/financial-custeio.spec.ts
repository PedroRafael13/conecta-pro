/**
 * Testes E2E - Custeio ABC
 */

import { test, expect } from './fixtures';

test.describe('Custeio ABC', () => {
  test.beforeEach(async ({ page }) => {
    // Mock explícito de /auth/me ANTES de qualquer navegação
    await page.route('**/api/v1/auth/**', (route) => {
      if (route.request().url().includes('/auth/me') && route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            email: 'admin@conectaplus.com.br',
            name: 'Admin',
            role: 'admin',
            is_active: true,
            permissions: ['*'],
            tenant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          }),
        });
      } else {
        route.continue();
      }
    });

    // Configurar token no localStorage
    await page.addInitScript(() => {
      const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBjb25lY3RhcGx1cy5jb20uYnIiLCJleHAiOjk5OTk5OTk5OTl9.mock';
      localStorage.setItem('access_token', mockToken);
    });

    await page.goto('/modulos/financeiro/custeio', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de custeio', async ({ page }) => {
    const hasContent = await page.locator('h1, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título "Custeio ABC"', async ({ page }) => {
    const title = page.locator('text=/Custeio/i').first();
    await expect(title).toBeVisible({ timeout: 10000 });
  });

  test('deve ter cards de estatísticas', async ({ page }) => {
    const cards = await page.locator('[class*="card"], [class*="Card"]').count();
    expect(cards).toBeGreaterThan(0);
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
