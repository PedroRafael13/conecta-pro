/**
 * Testes E2E - Conciliação Bancária
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Tabs de navegação (Contas Bancarias, Transacoes, Conciliacao)
 * - Campo de busca funcional
 * - Modal de criação de conta bancária abre corretamente
 * - Troca de tabs funciona
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

    await test.step('Verificar botão "Nova Conta"', async () => {
      await expect(page.locator('button', { hasText: 'Nova Conta' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 3 tabs de navegação', async ({ page }) => {
    const tabs = ['Contas Bancarias', 'Transacoes', 'Conciliacao'];
    for (const tab of tabs) {
      await test.step(`Verificar tab "${tab}"`, async () => {
        await expect(page.locator('button', { hasText: tab }).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir campo de busca', async ({ page }) => {
    await test.step('Verificar campo de busca', async () => {
      const searchInput = page.locator('input[placeholder*="contas"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio na tab Contas Bancarias', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhuma conta bancaria encontrada').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve abrir modal ao clicar em "Nova Conta"', async ({ page }) => {
    await test.step('Clicar no botão Nova Conta', async () => {
      await page.locator('button', { hasText: 'Nova Conta' }).click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve navegar para tab Transacoes', async ({ page }) => {
    await test.step('Clicar na tab Transacoes', async () => {
      await page.locator('button', { hasText: 'Transacoes' }).first().click();
      await page.waitForTimeout(300);
    });

    await test.step('Campo de busca muda para transações', async () => {
      await expect(page.locator('input[placeholder*="transacoes"]').first()).toBeVisible({ timeout: 8000 });
    });
  });
});
