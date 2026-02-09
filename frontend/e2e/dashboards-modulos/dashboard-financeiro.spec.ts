/**
 * Testes E2E - Dashboard Financeiro
 * Página: /modulos/financeiro
 * Total: 12 testes
 */

import { test, expect } from '../fixtures';

test.describe('Dashboard Financeiro', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard financeiro corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título Financeiro', async ({ page }) => {
    await expect(page.locator('h1').filter({ hasText: /Financeiro/i }).first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Receita', async ({ page }) => {
    await expect(page.locator('text=Receita').first()).toBeVisible({ timeout: 10000 });
    const receitaCard = page.locator('[class*="card"], [class*="Card"]').filter({ hasText: /Receita/ }).first();
    await expect(receitaCard).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Despesa', async ({ page }) => {
    await expect(page.locator('text=Despesa').first()).toBeVisible({ timeout: 10000 });
    const despesaCard = page.locator('[class*="card"], [class*="Card"]').filter({ hasText: /Despesa/ }).first();
    await expect(despesaCard).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Saldo', async ({ page }) => {
    await expect(page.locator('text=Saldo').first()).toBeVisible({ timeout: 10000 });
    const saldoCard = page.locator('[class*="card"], [class*="Card"]').filter({ hasText: /Saldo/ }).first();
    await expect(saldoCard).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Inadimplência', async ({ page }) => {
    await expect(page.locator('text=Inadimplência').first()).toBeVisible({ timeout: 10000 });
    const inadimplenciaCard = page.locator('[class*="card"], [class*="Card"]').filter({ hasText: /Inadimplência/ }).first();
    await expect(inadimplenciaCard).toBeVisible({ timeout: 10000 });
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

  test('deve ter link para Conciliação', async ({ page }) => {
    const link = page.locator('text=Conciliação').first();
    await expect(link).toBeVisible({ timeout: 10000 });
  });

  test('deve ter seção de Módulos Financeiros com cards', async ({ page }) => {
    await expect(page.locator('text=Módulos Financeiros').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter indicadores visuais nos cards de KPI', async ({ page }) => {
    // Verificar se há ícones nos cards de KPI
    const kpiIcons = await page.locator('[class*="text-green"], [class*="text-red"], [class*="text-blue"], [class*="text-yellow"]').count();
    expect(kpiIcons).toBeGreaterThan(0);
  });
});
