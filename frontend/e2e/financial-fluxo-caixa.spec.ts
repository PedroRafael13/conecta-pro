/**
 * Testes E2E - Fluxo de Caixa
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Cards de estatísticas (Entradas, Saidas, Saldo Atual, Projecao 30d)
 * - Campo de busca funcional
 * - Modal de criação abre corretamente
 * - Estado vazio com busca inexistente
 */

import { test, expect } from './fixtures';

test.describe('Fluxo de Caixa', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/fluxo-caixa', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Fluxo de Caixa"', async () => {
      await expect(page.locator('h1')).toContainText('Fluxo de Caixa', { timeout: 8000 });
    });

    await test.step('Verificar botão "Novo Lancamento"', async () => {
      await expect(page.locator('button', { hasText: 'Novo Lancamento' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 4 cards de estatísticas', async ({ page }) => {
    const stats = ['Entradas', 'Saidas', 'Saldo Atual', 'Projecao 30d'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir campo de busca', async ({ page }) => {
    await test.step('Verificar campo de busca principal', async () => {
      const searchInput = page.locator('input[placeholder*="descricao"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhum lancamento').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });
  });

  test('deve abrir modal ao clicar em "Novo Lancamento"', async ({ page }) => {
    await test.step('Clicar no botão Novo Lancamento', async () => {
      await page.locator('button', { hasText: 'Novo Lancamento' }).click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir estado vazio para busca sem resultado', async ({ page }) => {
    await test.step('Aguardar dados carregarem', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Buscar por termo que não existe', async () => {
      const searchInput = page.locator('input[placeholder*="descricao"]').first();
      await searchInput.fill('xxxxxxxxxxxxxxxxxxx-nao-existe-999');
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar mensagem de estado vazio', async () => {
      await expect(
        page.locator('text=Nenhum lancamento').first()
      ).toBeVisible({ timeout: 8000 });
    });
  });
});
