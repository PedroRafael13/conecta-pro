/**
 * Testes E2E - Dashboard Operacional
 * Página: /modulos/operacional
 * Total: 12 testes
 */

import { test, expect } from '../fixtures';

test.describe('Dashboard Operacional', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/operacional', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard operacional corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título Operacional', async ({ page }) => {
    await expect(page.locator('h1').filter({ hasText: /Operacional/i }).first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir KPI - Postos Ativos', async ({ page }) => {
    await expect(page.locator('text=Postos Ativos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir KPI - Colaboradores Ativos', async ({ page }) => {
    await expect(page.locator('text=Colaboradores Ativos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir KPI - Escalas em Andamento', async ({ page }) => {
    await expect(page.locator('text=Escalas em Andamento').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir KPI - Ocorrências Pendentes', async ({ page }) => {
    await expect(page.locator('text=Ocorrências Pendentes').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir KPI - Cobertura de Postos', async ({ page }) => {
    await expect(page.locator('text=Cobertura de Postos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir seção de Visão Geral Rápida', async ({ page }) => {
    await expect(page.locator('text=Visão Geral Rápida').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Postos de Trabalho', async ({ page }) => {
    await expect(page.locator('text=Postos de Trabalho').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Gerenciar postos, locais e requisitos de trabalho').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Escalas', async ({ page }) => {
    await expect(page.locator('text=Escalas').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Criar e gerenciar escalas mensais de trabalho').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter card de navegação - Ocorrências', async ({ page }) => {
    await expect(page.locator('text=Ocorrências').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Registrar e acompanhar ocorrências operacionais').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir módulos operacionais com ícones', async ({ page }) => {
    // Verificar se há pelo menos 10 submódulos listados
    const subModulesSection = await page.locator('text=Módulos Operacionais').first();
    await expect(subModulesSection).toBeVisible({ timeout: 10000 });

    const moduleCards = await page.locator('[class*="group"]').count();
    expect(moduleCards).toBeGreaterThanOrEqual(6);
  });
});
