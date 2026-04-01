import { test, expect } from '@playwright/test';

test.use({ storageState: 'e2e/.auth/user.json' });

test.describe('Operacional - AI Command Center', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/operacional/ai-command-center', { waitUntil: 'load' });
  });

  test('deve carregar a página de AI Command Center', async ({ page }) => {
    await expect(page.locator('h1, [data-testid="page-title"]').filter({ hasText: /AI Command Center/i }).first()).toBeVisible({ timeout: 15000 });
  });

  test('deve exibir KPI cards', async ({ page }) => {
    // Aguardar carregamento
    await page.waitForTimeout(3000);
    const cards = page.locator('.grid .rounded-xl');
    await expect(cards.first()).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshBtn = page.getByRole('button', { name: /atualizar/i });
    await expect(refreshBtn).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir seção de agentes de IA', async ({ page }) => {
    await page.waitForTimeout(2000);
    const agentesSection = page.getByText(/Agentes de IA/i).first();
    await expect(agentesSection).toBeVisible({ timeout: 10000 });
  });

  test('deve ter link de voltar para operacional', async ({ page }) => {
    const backLink = page.getByRole('button', { name: /operacional/i });
    await expect(backLink).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir seção de previsão de cobertura', async ({ page }) => {
    await page.waitForTimeout(2000);
    const coverageSection = page.getByText(/Previsão de Cobertura/i).first();
    await expect(coverageSection).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir seção de top performers', async ({ page }) => {
    await page.waitForTimeout(2000);
    const topSection = page.getByText(/Top Performers/i).first();
    await expect(topSection).toBeVisible({ timeout: 10000 });
  });

  test('deve ter links rápidos para submódulos', async ({ page }) => {
    await page.waitForTimeout(2000);
    const escalasLink = page.getByText(/Ver Escalas/i).first();
    await expect(escalasLink).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Operacional - AI Command Center - Navegação', () => {
  test('deve ser acessível a partir do módulo operacional', async ({ page }) => {
    await page.goto('/modulos/operacional', { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    const aiLink = page.getByText(/AI Command Center/i).first();
    await expect(aiLink).toBeVisible({ timeout: 10000 });
  });
});
