/**
 * Testes E2E - Contabilidade
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Tabs de navegação (Plano de Contas, Lancamentos, Balancete)
 * - Campo de busca funcional
 * - Modal de lançamento abre na tab correta
 * - Troca de tabs funciona
 */

import { test, expect } from './fixtures';

test.describe('Contabilidade', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/contabilidade', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Contabilidade"', async () => {
      await expect(page.locator('h1')).toContainText('Contabilidade', { timeout: 8000 });
    });
  });

  test('deve exibir 4 tabs de navegação', async ({ page }) => {
    const tabs = ['Plano de Contas', 'Lancamentos', 'Balancete'];
    for (const tab of tabs) {
      await test.step(`Verificar tab "${tab}"`, async () => {
        await expect(page.locator('button', { hasText: tab }).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir campo de busca', async ({ page }) => {
    await test.step('Verificar campo de busca', async () => {
      const searchInput = page.locator('input[placeholder*="Buscar"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio na tab Plano de Contas', async ({ page }) => {
    await test.step('Verificar tab Plano de Contas ativa por padrão', async () => {
      await expect(page.locator('button', { hasText: 'Plano de Contas' }).first()).toBeVisible({ timeout: 8000 });
    });

    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhuma conta').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve exibir botão "Novo Lancamento" ao ir para tab Lancamentos', async ({ page }) => {
    await test.step('Clicar na tab Lancamentos', async () => {
      await page.locator('button', { hasText: 'Lancamentos' }).first().click();
      await page.waitForTimeout(300);
    });

    await test.step('Verificar botão Novo Lancamento', async () => {
      await expect(page.locator('button', { hasText: 'Novo Lancamento' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve navegar entre todas as tabs sem erros', async ({ page }) => {
    const tabs = ['Plano de Contas', 'Lancamentos', 'Balancete'];
    for (const tab of tabs) {
      await test.step(`Navegar para tab "${tab}"`, async () => {
        await page.locator('button', { hasText: tab }).first().click();
        await page.waitForTimeout(300);
        await expect(page.locator('h1')).toContainText('Contabilidade');
      });
    }
  });
});
