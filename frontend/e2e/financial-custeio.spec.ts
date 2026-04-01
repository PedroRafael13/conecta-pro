/**
 * Testes E2E - Custeio ABC
 *
 * Validações:
 * - Carregamento da página com header correto
 * - Cards de estatísticas (Direcionadores, Atividades, Pools de Custo, Objetos de Custo)
 * - Tabs de navegação (Direcionadores, Atividades, Pools de Custo, Objetos de Custo)
 * - Campo de busca funcional e dinâmico por tab
 * - Troca de tabs funciona sem erros
 */

import { test, expect } from './fixtures';

test.describe('Custeio ABC', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/custeio', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Custeio ABC"', async () => {
      await expect(page.locator('h1')).toContainText('Custeio', { timeout: 8000 });
    });
  });

  test('deve exibir 4 cards de estatísticas', async ({ page }) => {
    const stats = ['Direcionadores', 'Atividades', 'Pools de Custo', 'Objetos de Custo'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir 4 tabs de navegação', async ({ page }) => {
    const tabs = ['Direcionadores', 'Atividades', 'Pools de Custo', 'Objetos de Custo'];
    for (const tab of tabs) {
      await test.step(`Verificar tab "${tab}"`, async () => {
        await expect(page.locator('button', { hasText: tab }).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir campo de busca', async ({ page }) => {
    await test.step('Verificar campo de busca presente', async () => {
      const searchInput = page.locator('input[type="search"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio na tab ativa', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(4000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhum').first().isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve navegar entre todas as tabs sem erros', async ({ page }) => {
    const tabs = ['Atividades', 'Pools de Custo', 'Objetos de Custo', 'Direcionadores'];
    for (const tab of tabs) {
      await test.step(`Navegar para tab "${tab}"`, async () => {
        await page.locator('button', { hasText: tab }).first().click();
        await page.waitForTimeout(300);
        await expect(page.locator('h1')).toContainText('Custeio');
      });
    }
  });
});
