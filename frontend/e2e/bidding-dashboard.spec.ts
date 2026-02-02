/**
 * Testes E2E - Dashboard de Licitações
 */

import { test, expect } from '@playwright/test';

test.describe('Dashboard de Licitações', () => {
  test.beforeEach(async ({ page }) => {
    // Navegar para o dashboard
    await page.goto('/modulos/licitacoes', { waitUntil: 'domcontentloaded' });
    // Aguardar estabilização (React Query, etc)
    await page.waitForTimeout(3000);
  });

  test('deve carregar o dashboard corretamente', async ({ page }) => {
    // Verificar se a página carregou verificando presença de qualquer KPI
    const kpis = page.locator('text=Editais, text=Propostas, text=Contratos, text=Certidões');
    const count = await kpis.count();

    // Teste passa se algum KPI apareceu (página carregou)
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir os 4 cards de KPIs', async ({ page }) => {
    // Verificar presença dos KPIs (com timeout generoso)
    await expect(page.locator('text=Editais').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Propostas').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Contratos').first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Certidões').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir cards de acesso rápido', async ({ page }) => {
    await expect(page.locator('text=Editais Recentes, text=Minhas Propostas, text=Contratos Ativos').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter links de navegação para editais', async ({ page }) => {
    // Apenas verifica se o link existe (não tenta clicar)
    const editaisLink = page.locator('a[href*="/licitacoes/editais"]').first();
    await expect(editaisLink).toBeVisible({ timeout: 10000 });
  });

  test('deve ter links de navegação para propostas', async ({ page }) => {
    // Apenas verifica se o link existe (não tenta clicar)
    const propostasLink = page.locator('a[href*="/licitacoes/propostas"]').first();
    await expect(propostasLink).toBeVisible({ timeout: 10000 });
  });

  test('deve ter links de navegação para contratos', async ({ page }) => {
    // Apenas verifica se o link existe (não tenta clicar)
    const contratosLink = page.locator('a[href*="/licitacoes/contratos"]').first();
    await expect(contratosLink).toBeVisible({ timeout: 10000 });
  });
});
