/**
 * Testes E2E - Dashboard Serviços
 * Página: /modulos/servicos
 * Total: 12 testes
 */

import { test, expect } from '../fixtures';

test.describe('Dashboard Serviços', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/servicos', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard de serviços corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título Serviços', async ({ page }) => {
    await expect(page.locator('h1').filter({ hasText: /Servicos/i }).first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - Contratos Ativos', async ({ page }) => {
    await expect(page.locator('text=Contratos Ativos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - OS Abertas', async ({ page }) => {
    await expect(page.locator('text=OS Abertas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - Agendamentos Hoje', async ({ page }) => {
    await expect(page.locator('text=Agendamentos Hoje').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de estatística - Alertas', async ({ page }) => {
    await expect(page.locator('text=Alertas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Contratos', async ({ page }) => {
    await expect(page.locator('text=Contratos').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Gestao de contratos de servico').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Ordens de Servico', async ({ page }) => {
    await expect(page.locator('text=Ordens de Servico').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Gestao de ordens de servico').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Agendamentos', async ({ page }) => {
    await expect(page.locator('text=Agendamentos').nth(0)).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Agendamentos de visitas e servicos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar dados', async ({ page }) => {
    const refreshButton = page.locator('button').filter({ hasText: /Atualizar/i }).first();
    await expect(refreshButton).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir descrição do módulo', async ({ page }) => {
    await expect(page.locator('text=Gestao de contratos, ordens de servico e agendamentos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir ícones coloridos nos cards de estatísticas', async ({ page }) => {
    // Verificar se há elementos com classes de cor
    const blueElements = await page.locator('[class*="text-blue"]').count();
    const purpleElements = await page.locator('[class*="text-purple"]').count();
    const greenElements = await page.locator('[class*="text-green"]').count();
    const orangeElements = await page.locator('[class*="text-orange"]').count();

    const totalColored = blueElements + purpleElements + greenElements + orangeElements;
    expect(totalColored).toBeGreaterThan(0);
  });
});
