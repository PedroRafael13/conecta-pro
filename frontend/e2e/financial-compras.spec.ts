/**
 * Testes E2E - Compras
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Cards de estatísticas (Total Requisicoes, Total Ordens, Valor Total, Pendentes)
 * - Tabs de navegação (Requisicoes, Ordens) funcionais
 * - Campo de busca e filtro de status funcionais
 * - Modal de criação abre corretamente
 */

import { test, expect } from './fixtures';

test.describe('Compras', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/compras', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Compras"', async () => {
      await expect(page.locator('h1')).toContainText('Compras', { timeout: 8000 });
    });

    await test.step('Verificar botão de nova requisição', async () => {
      await expect(page.locator('button', { hasText: 'Nova Requisicao' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 4 cards de estatísticas', async ({ page }) => {
    const stats = ['Total Requisicoes', 'Total Ordens', 'Valor Total', 'Pendentes'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir 2 tabs de navegação', async ({ page }) => {
    await test.step('Verificar tab Requisicoes', async () => {
      await expect(page.locator('button', { hasText: 'Requisicoes' }).first()).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar tab Ordens', async () => {
      await expect(page.locator('button', { hasText: 'Ordens' }).first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir campo de busca e filtro de status', async ({ page }) => {
    await test.step('Verificar campo de busca', async () => {
      const searchInput = page.locator('input[placeholder*="codigo"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar select de status', async () => {
      await expect(page.locator('text=Status').first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio na tab Requisicoes', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhuma requisicao').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve abrir modal ao clicar em "Nova Requisicao"', async ({ page }) => {
    await test.step('Clicar no botão Nova Requisicao', async () => {
      await page.locator('button', { hasText: 'Nova Requisicao' }).click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve trocar para tab Ordens e mostrar botão Nova Ordem', async ({ page }) => {
    await test.step('Clicar na tab Ordens', async () => {
      await page.locator('button', { hasText: 'Ordens' }).first().click();
      await page.waitForTimeout(300);
    });

    await test.step('Verificar botão Nova Ordem visível', async () => {
      await expect(page.locator('button', { hasText: 'Nova Ordem' })).toBeVisible({ timeout: 8000 });
    });
  });
});
