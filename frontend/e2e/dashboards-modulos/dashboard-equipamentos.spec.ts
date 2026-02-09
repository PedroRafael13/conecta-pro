/**
 * Testes E2E - Dashboard Equipamentos
 * Página: /modulos/equipamentos
 * Total: 12 testes
 */

import { test, expect } from '../fixtures';

test.describe('Dashboard Equipamentos', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/equipamentos', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard de equipamentos corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título do módulo Equipamentos', async ({ page }) => {
    await expect(page.locator('h1').filter({ hasText: /Equipamentos/i }).first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de Total Equipamentos', async ({ page }) => {
    await expect(page.locator('text=Total Equipamentos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de Em Estoque', async ({ page }) => {
    await expect(page.locator('text=Em Estoque').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de Em Manutenção', async ({ page }) => {
    await expect(page.locator('text=Em Manutenção').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de Alertas', async ({ page }) => {
    await expect(page.locator('text=Alertas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir descrição do módulo', async ({ page }) => {
    await expect(page.locator('text=Controle de patrimonio, comodatos de equipamentos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Patrimônio', async ({ page }) => {
    await expect(page.locator('text=Patrimonio').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Cadastro e controle de equipamentos do parque tecnologico').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Comodatos', async ({ page }) => {
    await expect(page.locator('text=Comodatos').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Gestao de equipamentos em comodato com clientes').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Manutenções', async ({ page }) => {
    await expect(page.locator('text=Manutencoes').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Manutencoes preventivas e corretivas dos equipamentos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir ícones nos cards de navegação', async ({ page }) => {
    const cardsWithIcons = await page.locator('[class*="cursor-pointer"] svg, [class*="cursor-pointer"] [class*="lucide"]').count();
    expect(cardsWithIcons).toBeGreaterThanOrEqual(3);
  });

  test('deve ter indicadores visuais de status nos cards', async ({ page }) => {
    // Verificar se há elementos com classes de cor indicando status
    const coloredElements = await page.locator('[class*="text-blue"], [class*="text-orange"], [class*="text-red"]').count();
    expect(coloredElements).toBeGreaterThan(0);
  });
});
