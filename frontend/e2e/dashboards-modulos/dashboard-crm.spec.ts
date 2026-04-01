/**
 * Testes E2E - Dashboard CRM
 * Página: /modulos/crm
 * Total: 12 testes
 */

import { test, expect } from '../fixtures';

test.describe('Dashboard CRM', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/crm', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar o dashboard CRM corretamente', async ({ page }) => {
    const hasContent = await page.locator('h1, h2, button, div').count();
    expect(hasContent).toBeGreaterThan(0);
  });

  test('deve exibir o título do módulo CRM', async ({ page }) => {
    await expect(page.locator('h1').filter({ hasText: /CRM/i }).first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Leads', async ({ page }) => {
    await expect(page.locator('text=Leads').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Gerenciar leads e captacao').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Oportunidades', async ({ page }) => {
    await expect(page.locator('text=Oportunidades').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Pipeline de vendas').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Clientes', async ({ page }) => {
    await expect(page.locator('text=Clientes').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Base de clientes ativos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de KPI - Propostas', async ({ page }) => {
    await expect(page.locator('text=Propostas').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Propostas comerciais').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de resumo - Win Rate', async ({ page }) => {
    await expect(page.locator('text=Win Rate').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de resumo - Ticket Medio', async ({ page }) => {
    await expect(page.locator('text=Ticket Medio').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de resumo - Ciclo Medio', async ({ page }) => {
    await expect(page.locator('text=Ciclo Medio').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir card de acesso rápido - Contatos', async ({ page }) => {
    await expect(page.locator('text=Contatos').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Gerenciar contatos vinculados a clientes').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar dados', async ({ page }) => {
    const refreshButton = page.locator('button').filter({ hasText: /Atualizar/i }).first();
    await expect(refreshButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter links de navegação para submódulos', async ({ page }) => {
    // Verificar se há pelo menos 4 cards de navegação (Leads, Oportunidades, Clientes, Propostas)
    const navCards = await page.locator('[class*="cursor-pointer"]').count();
    expect(navCards).toBeGreaterThanOrEqual(4);
  });
});
