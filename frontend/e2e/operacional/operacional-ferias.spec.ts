import { test, expect } from '@playwright/test';

test.use({ storageState: 'e2e/.auth/user.json' });

test.describe('Operacional - Férias e Afastamentos', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/operacional/ferias', { waitUntil: 'load' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de férias', async ({ page }) => {
    const title = page.locator('h1, h2').filter({ hasText: /férias|afastamentos/i }).first();
    await expect(title).toBeVisible({ timeout: 15000 });
  });

  test('deve ter botão para nova solicitação', async ({ page }) => {
    const newBtn = page.getByRole('button', { name: /nova|solicitar|adicionar/i }).first();
    await expect(newBtn).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    const pendente = page.getByText(/pendente/i).first();
    await expect(pendente).toBeVisible({ timeout: 10000 });
  });

  test('deve ter campo de busca', async ({ page }) => {
    const search = page.locator('input[type="text"], input[placeholder*="buscar"], input[placeholder*="pesquisar"]').first();
    await expect(search).toBeVisible({ timeout: 10000 });
  });

  test('deve ter link de voltar', async ({ page }) => {
    const backLink = page.locator('a[href*="operacional"]').first();
    await expect(backLink).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir tabela ou lista de solicitações', async ({ page }) => {
    // Pode ser tabela ou lista vazia
    const content = page.locator('table, [data-testid="empty-state"], .empty-state, [class*="empty"]').first();
    const hasContent = await content.isVisible({ timeout: 5000 }).catch(() => false);

    if (!hasContent) {
      // Se não tem tabela, deve ter mensagem de lista vazia
      const emptyMsg = page.getByText(/nenhuma|sem solicitação|vazio|ainda não/i).first();
      await expect(emptyMsg).toBeVisible({ timeout: 10000 });
    }
  });
});
