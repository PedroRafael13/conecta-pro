/**
 * Testes E2E - Faturamento
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Cards de estatísticas (Total Regras, Ativas, Valor Fixo Total, Inativas)
 * - Campo de busca e filtro de status funcionais
 * - Modal de criação abre corretamente
 * - Estado vazio com busca inexistente
 */

import { test, expect } from './fixtures';

test.describe('Faturamento', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/faturamento', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Faturamento"', async () => {
      await expect(page.locator('h1')).toContainText('Faturamento', { timeout: 8000 });
    });

    await test.step('Verificar botão "Nova Regra"', async () => {
      await expect(page.locator('button', { hasText: 'Nova Regra' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 4 cards de estatísticas', async ({ page }) => {
    const stats = ['Total Regras', 'Ativas', 'Valor Fixo Total', 'Inativas'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir campo de busca e filtro de status', async ({ page }) => {
    await test.step('Verificar campo de busca', async () => {
      const searchInput = page.locator('input[placeholder*="nome"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar select de status', async () => {
      await expect(page.locator('text=Status').first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhuma regra').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve abrir modal ao clicar em "Nova Regra"', async ({ page }) => {
    await test.step('Clicar no botão Nova Regra', async () => {
      await page.locator('button', { hasText: 'Nova Regra' }).click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir estado vazio para busca sem resultado', async ({ page }) => {
    await test.step('Buscar por termo que não existe', async () => {
      const searchInput = page.locator('input[placeholder*="nome"]').first();
      await searchInput.fill('xxxxxxxxxxxxxxxxxxx-nao-existe-999');
      await page.waitForTimeout(600);
    });

    await test.step('Verificar mensagem de estado vazio', async () => {
      await expect(
        page.locator('text=Nenhuma regra').first()
      ).toBeVisible({ timeout: 8000 });
    });
  });
});
