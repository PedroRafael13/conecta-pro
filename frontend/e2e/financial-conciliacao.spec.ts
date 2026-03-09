/**
 * Testes E2E - Conciliação Bancária
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - 4 tabs: Extrato Bancario, Contas Bancarias, Conciliacao, Importar OFX
 * - Extrato bancário com botão de sincronizar
 * - Contas bancárias com modal de criação
 * - Campo de busca funcional
 */

import { test, expect } from './fixtures';

test.describe('Conciliação Bancária', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/conciliacao', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 com "Concilia"', async () => {
      await expect(page.locator('h1')).toContainText('Concilia', { timeout: 8000 });
    });
  });

  test('deve exibir 4 tabs de navegação', async ({ page }) => {
    const tabs = ['Extrato Bancario', 'Contas Bancarias', 'Conciliacao', 'Importar OFX'];
    for (const tab of tabs) {
      await test.step(`Verificar tab "${tab}"`, async () => {
        await expect(page.locator('button', { hasText: tab }).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir campo de busca na tab Extrato Bancário', async ({ page }) => {
    await test.step('Verificar campo de busca', async () => {
      const searchInput = page.locator('input[type="search"], input[placeholder*="uscar"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir KPIs ou estado vazio na tab Extrato Bancário', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de KPIs ou mensagem de vazio', async () => {
      const hasKpi = await page.locator('text=Entradas').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Sincronizar').isVisible().catch(() => false);
      expect(hasKpi || hasEmpty).toBeTruthy();
    });
  });

  test('deve navegar para tab Contas Bancárias e exibir tabela ou vazio', async ({ page }) => {
    await test.step('Clicar na tab Contas Bancarias', async () => {
      await page.locator('button', { hasText: 'Contas Bancarias' }).first().click();
      await page.waitForTimeout(500);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhuma conta').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve abrir modal ao clicar em "Nova Conta"', async ({ page }) => {
    await test.step('Navegar para tab Contas Bancarias', async () => {
      await page.locator('button', { hasText: 'Contas Bancarias' }).first().click();
      await page.waitForTimeout(800);
    });

    await test.step('Clicar no botão Nova Conta', async () => {
      await page.locator('button', { hasText: 'Nova Conta' }).first().click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });
});
