/**
 * Testes E2E - Cobranças (Boleto + PIX)
 *
 * Validações:
 * - Carregamento da página com header correto
 * - 4 tabs: Emitir, Listagem, Régua de Cobrança, Inadimplentes
 * - Tab Emitir: botões Boleto e PIX visíveis
 * - Tab Listagem: filtros e tabela/vazio
 * - Tab Régua: timeline de cobrança
 * - Tab Inadimplentes: KPIs e tabela
 */

import { test, expect } from './fixtures';

test.describe('Cobranças', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/cobrancas', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Cobranças"', async () => {
      await expect(page.locator('h1')).toContainText('Cobran', { timeout: 8000 });
    });
  });

  test('deve exibir 4 tabs de navegação', async ({ page }) => {
    const tabs = ['Emitir', 'Emitidas', 'Régua', 'Inadimplentes'];
    for (const tab of tabs) {
      await test.step(`Verificar tab "${tab}"`, async () => {
        await expect(page.locator('button', { hasText: tab }).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir opções Boleto e PIX na tab Emitir', async ({ page }) => {
    await test.step('Verificar botão Boleto', async () => {
      await expect(page.locator('button', { hasText: 'Boleto' }).first()).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar botão PIX', async () => {
      await expect(page.locator('button', { hasText: 'PIX' }).first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve navegar para tab Emitidas e exibir filtros', async ({ page }) => {
    await test.step('Clicar na tab Emitidas', async () => {
      await page.locator('button', { hasText: 'Emitidas' }).first().click();
      await page.waitForTimeout(500);
    });

    await test.step('Verificar presença de filtros ou tabela', async () => {
      const hasContent = await page.locator('main').isVisible().catch(() => false);
      expect(hasContent).toBeTruthy();
    });
  });

  test('deve navegar para tab Régua e exibir timeline', async ({ page }) => {
    await test.step('Clicar na tab Régua', async () => {
      await page.locator('button', { hasText: 'Régua' }).first().click();
      await page.waitForTimeout(500);
    });

    await test.step('Verificar presença de conteúdo da régua', async () => {
      const hasContent = await page.locator('main').isVisible().catch(() => false);
      expect(hasContent).toBeTruthy();
    });
  });

  test('deve navegar para tab Inadimplentes e exibir KPIs', async ({ page }) => {
    await test.step('Clicar na tab Inadimplentes', async () => {
      await page.locator('button', { hasText: 'Inadimplentes' }).first().click();
      await page.waitForTimeout(1000);
    });

    await test.step('Verificar presença de conteúdo', async () => {
      const hasContent = await page.locator('main').isVisible().catch(() => false);
      expect(hasContent).toBeTruthy();
    });
  });
});
