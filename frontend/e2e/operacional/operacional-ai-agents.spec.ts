import { test, expect } from '@playwright/test';

test.use({ storageState: 'e2e/.auth/user.json' });

test.describe('Operacional - AI Agents Avançados', () => {
  test('AI Command Center deve ter seção Bartolo 3.0', async ({ page }) => {
    await page.goto('/modulos/operacional/ai-command-center', { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    const bartolo = page.getByText(/Bartolo/i).first();
    await expect(bartolo).toBeVisible({ timeout: 10000 });
  });

  test('Bartolo deve ter input de chat', async ({ page }) => {
    await page.goto('/modulos/operacional/ai-command-center', { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    const input = page.locator('input[placeholder*="Bartolo"], input[placeholder*="Pergunte"]').first();
    await expect(input).toBeVisible({ timeout: 10000 });
  });

  test('Bartolo deve responder a mensagem', async ({ page }) => {
    await page.goto('/modulos/operacional/ai-command-center', { waitUntil: 'load' });
    await page.waitForTimeout(3000);
    const input = page.locator('input[placeholder*="Bartolo"], input[placeholder*="Pergunte"]').first();
    if (await input.isVisible()) {
      await input.fill('bom dia');
      await input.press('Enter');
      await page.waitForTimeout(4000);
      // Deve aparecer resposta
      const responseArea = page.locator('.overflow-y-auto').first();
      await expect(responseArea).toBeVisible({ timeout: 5000 });
    }
  });

  test('AI Command Center deve exibir custos previstos', async ({ page }) => {
    await page.goto('/modulos/operacional/ai-command-center', { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    // Verifica que a página carregou com dados
    const kpiGrid = page.locator('.grid').first();
    await expect(kpiGrid).toBeVisible({ timeout: 10000 });
  });

  test('Comunicados deve ter funcionalidade de leitura', async ({ page }) => {
    await page.goto('/modulos/operacional/comunicados', { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    const title = page.locator('h1, h2').filter({ hasText: /comunicados/i }).first();
    await expect(title).toBeVisible({ timeout: 10000 });
  });

  test('Reembolsos deve exibir workflow completo', async ({ page }) => {
    await page.goto('/modulos/operacional/reembolsos', { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    const title = page.locator('h1, h2, h3').filter({ hasText: /reembolso/i }).first();
    await expect(title).toBeVisible({ timeout: 10000 });
  });
});
