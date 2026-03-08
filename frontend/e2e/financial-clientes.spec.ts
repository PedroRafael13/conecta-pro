/**
 * Testes E2E - Clientes
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Cards de estatísticas (Total de Clientes, Ativos, Inadimplentes)
 * - Campo de busca e filtros por status funcionais
 * - Modal de criação abre corretamente
 * - Estado vazio com busca inexistente
 */

import { test, expect } from './fixtures';

test.describe('Clientes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/clientes', { waitUntil: 'load' });
    // Aguarda o componente React hidratar e renderizar o conteúdo
    await page.locator('h1').waitFor({ state: 'visible', timeout: 15000 });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Clientes"', async () => {
      await expect(page.locator('h1')).toContainText('Clientes', { timeout: 8000 });
    });

    await test.step('Verificar botão "Novo Cliente"', async () => {
      await expect(page.locator('button', { hasText: 'Novo Cliente' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 3 cards de estatísticas', async ({ page }) => {
    const stats = ['Total de Clientes', 'Ativos', 'Inadimplentes'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir campo de busca e filtros de status', async ({ page }) => {
    await test.step('Verificar campo de busca', async () => {
      const searchInput = page.locator('input[placeholder*="nome"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar botões de filtro de status', async () => {
      await expect(page.locator('button', { hasText: 'Todos' }).first()).toBeVisible({ timeout: 8000 });
      await expect(page.locator('button', { hasText: 'Ativos' }).first()).toBeVisible({ timeout: 8000 });
      await expect(page.locator('button', { hasText: 'Inadimplentes' }).first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhum cliente encontrado').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });

    await test.step('Verificar colunas da tabela quando há dados', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      if (hasTable) {
        const columns = ['Nome', 'Status'];
        for (const column of columns) {
          await expect(page.locator('th').filter({ hasText: column }).first()).toBeVisible({ timeout: 8000 });
        }
      }
    });
  });

  test('deve abrir modal ao clicar em "Novo Cliente"', async ({ page }) => {
    await test.step('Clicar no botão Novo Cliente', async () => {
      await page.locator('button', { hasText: 'Novo Cliente' }).click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve filtrar por status "Ativos"', async ({ page }) => {
    await test.step('Clicar no botão de filtro "Ativos"', async () => {
      await page.locator('button', { hasText: 'Ativos' }).first().click();
      await page.waitForTimeout(300);
    });

    await test.step('Página continua funcional após filtro', async () => {
      await expect(page.locator('h1')).toContainText('Clientes');
    });
  });

  test('deve exibir estado vazio para busca sem resultado', async ({ page }) => {
    await test.step('Aguardar dados carregarem antes de buscar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Buscar por termo que não existe', async () => {
      const searchInput = page.locator('input[placeholder*="nome"]').first();
      await searchInput.fill('xxxxxxxxxxxxxxxxxxx-nao-existe-999');
      await page.waitForTimeout(600);
    });

    await test.step('Verificar mensagem de estado vazio', async () => {
      await expect(
        page.locator('text=Nenhum cliente encontrado')
      ).toBeVisible({ timeout: 8000 });
    });
  });
});
