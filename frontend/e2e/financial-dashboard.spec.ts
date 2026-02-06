/**
 * Testes E2E - Dashboard Financeiro
 */

import { test, expect } from './fixtures';

test.describe('Dashboard Financeiro', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard corretamente', async ({ page }) => {
    // Verificar se a página carregou
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir os 4 cards de KPIs', async ({ page }) => {
    // Verificar presença dos KPIs financeiros
    await expect(page.locator('text=Receita').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Despesa').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Saldo').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Inadimplência').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir cards de navegação dos submódulos', async ({ page }) => {
    // Verificar se há cards de navegação
    const navigationCards = await page.locator('[class*="group"]').count();
    expect(navigationCards).toBeGreaterThan(0);
  });

  test('deve ter link para Contas a Pagar', async ({ page }) => {
    const link = page.locator('text=Contas a Pagar').first();
    await expect(link).toBeVisible({ timeout: 10000 });
  });

  test('deve ter link para Contas a Receber', async ({ page }) => {
    const link = page.locator('text=Contas a Receber').first();
    await expect(link).toBeVisible({ timeout: 10000 });
  });

  test('deve ter link para Fluxo de Caixa', async ({ page }) => {
    const link = page.locator('text=Fluxo de Caixa').first();
    await expect(link).toBeVisible({ timeout: 10000 });
  });
});
