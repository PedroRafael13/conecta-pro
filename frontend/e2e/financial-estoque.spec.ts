/**
 * Testes E2E - Estoque
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Cards de estatísticas (Total Itens, Valor Total, Abaixo do Minimo, Armazens)
 * - Tabs de navegação (Itens, Armazens, Movimentacoes) funcionais
 * - Campo de busca funcional
 * - Modal de movimentação abre corretamente
 */

import { test, expect } from './fixtures';

test.describe('Estoque', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/estoque', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Estoque"', async () => {
      await expect(page.locator('h1')).toContainText('Estoque', { timeout: 8000 });
    });

    await test.step('Verificar botão "Nova Movimentacao"', async () => {
      await expect(page.locator('button', { hasText: 'Nova Movimentacao' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 4 cards de estatísticas', async ({ page }) => {
    const stats = ['Total Itens', 'Valor Total', 'Abaixo do Minimo', 'Armazens'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir tabs de navegação', async ({ page }) => {
    const tabs = ['Itens', 'Armazens', 'Movimentacoes'];
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

  test('deve exibir tabela ou estado vazio na tab Itens', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhum item').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve abrir modal ao clicar em "Nova Movimentacao"', async ({ page }) => {
    await test.step('Clicar no botão Nova Movimentacao', async () => {
      await page.locator('button', { hasText: 'Nova Movimentacao' }).click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve navegar entre tabs sem erros', async ({ page }) => {
    const tabs = ['Itens', 'Armazens', 'Movimentacoes'];
    for (const tab of tabs) {
      await test.step(`Navegar para tab "${tab}"`, async () => {
        await page.locator('button', { hasText: tab }).first().click();
        await page.waitForTimeout(300);
        await expect(page.locator('h1')).toContainText('Estoque');
      });
    }
  });
});
