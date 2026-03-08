/**
 * Testes E2E - Fiscal
 *
 * Validações:
 * - Carregamento da página com header e botões corretos
 * - Cards de estatísticas (Total NF-e, Total NFS-e, Autorizadas, Pendentes)
 * - Tabs NF-e e NFS-e funcionais
 * - Campo de busca e filtro de status funcionais
 * - Modal de criação abre corretamente
 * - Troca de tab NF-e → NFS-e funciona
 */

import { test, expect } from './fixtures';

test.describe('Fiscal', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/financeiro/fiscal', { waitUntil: 'load' });
  });

  test('deve carregar página com header correto', async ({ page }) => {
    await test.step('Verificar título h1 "Fiscal"', async () => {
      await expect(page.locator('h1')).toContainText('Fiscal', { timeout: 8000 });
    });

    await test.step('Verificar botão "Nova Nota Fiscal"', async () => {
      await expect(page.locator('button', { hasText: 'Nova Nota Fiscal' })).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir 4 cards de estatísticas', async ({ page }) => {
    const stats = ['Total NF-e', 'Total NFS-e', 'Autorizadas', 'Pendentes'];
    for (const stat of stats) {
      await test.step(`Verificar card "${stat}"`, async () => {
        await expect(page.locator('text=' + stat).first()).toBeVisible({ timeout: 8000 });
      });
    }
  });

  test('deve exibir tabs NF-e e NFS-e', async ({ page }) => {
    await test.step('Verificar tab NF-e', async () => {
      await expect(page.locator('button', { hasText: 'NF-e' }).first()).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar tab NFS-e', async () => {
      await expect(page.locator('button', { hasText: 'NFS-e' }).first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir campo de busca e filtro de status', async ({ page }) => {
    await test.step('Verificar campo de busca', async () => {
      const searchInput = page.locator('input[placeholder*="numero"]').first();
      await expect(searchInput).toBeVisible({ timeout: 8000 });
    });

    await test.step('Verificar select de status', async () => {
      await expect(page.locator('text=Todos').first()).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve exibir tabela ou estado vazio', async ({ page }) => {
    await test.step('Aguardar conteúdo carregar', async () => {
      await page.waitForTimeout(2000);
    });

    await test.step('Verificar presença de tabela ou mensagem de vazio', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasEmpty = await page.locator('text=Nenhuma').isVisible().catch(() => false);
      expect(hasTable || hasEmpty).toBeTruthy();
    });

    await test.step('Verificar colunas da tabela quando há dados', async () => {
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      if (hasTable) {
        const columns = ['Numero', 'Destinatario', 'Valor', 'Status'];
        for (const column of columns) {
          await expect(page.locator('th').filter({ hasText: column }).first()).toBeVisible({ timeout: 8000 });
        }
      }
    });
  });

  test('deve abrir modal ao clicar em "Nova Nota Fiscal"', async ({ page }) => {
    await test.step('Clicar no botão Nova Nota Fiscal', async () => {
      await page.locator('button', { hasText: 'Nova Nota Fiscal' }).click();
    });

    await test.step('Verificar que modal abriu', async () => {
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible({ timeout: 8000 });
    });
  });

  test('deve trocar para tab NFS-e ao clicar', async ({ page }) => {
    await test.step('Clicar na tab NFS-e', async () => {
      await page.locator('button', { hasText: 'NFS-e' }).first().click();
      await page.waitForTimeout(300);
    });

    await test.step('Página continua funcional após troca de tab', async () => {
      await expect(page.locator('h1')).toContainText('Fiscal');
    });
  });
});
