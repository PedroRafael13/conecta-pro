/**
 * Testes E2E - Contas a Receber
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Cards de estatísticas visíveis
 * - Busca e filtros por status funcionais
 * - Modal de criação abre corretamente
 * - Estado vazio com busca inexistente
 */

import { test, expect } from './fixtures';

test.describe('Contas a Receber', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/contas-receber', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Contas a Receber"', async () => {
      await expect(page.locator('h1')).toContainText('Contas a Receber', { timeout: 8000 });
    });

    await test.step('Verificar botão "Nova Conta"', async () => {
      await expect(page.locator('button', { hasText: 'Nova Conta' })).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar botão "Atualizar"', async () => {
      await expect(page.locator('button', { hasText: 'Atualizar' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 4 cards de estatísticas', async ({ page }) => {
    const stats = ['Total', 'Vencendo Hoje', 'Atrasadas', 'Recebidas'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir filtros de busca', async ({ page }) => {
    await test.step('Verificar campo de busca principal', async () => {
      const searchInput = page.locator('input[placeholder*="Buscar"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar select de status', async () => {
      await expect(page.locator('text=Todos os status').first()).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar campo de filtro por cliente', async () => {
      await expect(page.locator('input[placeholder*="liente"]').first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhuma conta a receber encontrada').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });

    await test.step('Verificar colunas da tabela quando há dados', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      if (hasTable) {
        const columns = ['Cliente', 'Valor', 'Vencimento', 'Status'];
        for (const column of columns) {
          await expect(page.locator('th').filter({ hasText: column }).first()).toBeVisible({ timeout: 8000 });
        }
      }
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

  test('deve filtrar por status "Pendente"', async ({ page }) => {
    await test.step('Selecionar filtro de status "Pendente"', async () => {
      await page.locator('text=Todos os status').first().click();
      await page.locator('[role="option"]:has-text("Pendente")').click();
    });

    await test.step('Página continua funcional após filtro', async () => {
      await page.waitForTimeout(300);
      await expect(page.locator('h1')).toContainText('Contas a Receber');
    });
  });

  test('deve exibir estado vazio para busca sem resultado', async ({ page }) => {
    await test.step('Buscar por termo que não existe', async () => {
      const searchInput = page.locator('input[placeholder*="Buscar"]').first();
      await searchInput.fill('xxxxxxxxxxxxxxxxxxx-nao-existe-999');
      await page.waitForTimeout(600);
    });

    await test.step('Verificar mensagem de estado vazio', async () => {
      await expect(
        page.locator('text=Nenhuma conta a receber encontrada')
      ).toBeVisible({ timeout: 8000 });
    });
  });
});
