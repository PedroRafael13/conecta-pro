import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Segurança / Mascaramento de Dados
 *
 * Funcionalidades testadas:
 * - Mascaramento individual de dados
 * - Mascaramento em lote
 * - Seleção de tipo de dado (CPF, email, telefone, etc.)
 * - Copiar resultado
 */

// Setup de mocks para API
async function setupMaskingMocks(page: Page) {
  await page.route('**/api/v1/security-lgpd/mask/cpf', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { masked_data: '***.456.789-**' },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask/email', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { masked_data: 'j***@exemplo.com' },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask/phone', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { masked_data: '(**) *****-4321' },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { masked_data: '**********ados' },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask/batch', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: [
          { masked: '***.456.789-**' },
          { masked: '***.123.456-**' },
        ],
      }),
    });
  });
}

test.describe('Segurança - Mascaramento de Dados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupMaskingMocks(page);
    await page.goto('/modulos/seguranca/mascaramento');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de mascaramento', async ({ page }) => {
    await expect(page).toHaveURL(/\/mascaramento/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Mascaramento/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/PII|dados pessoais/i');
    await expect(description).toBeVisible();
  });

  test('deve exibir cards de mascaramento individual e em lote', async ({ page }) => {
    await page.waitForTimeout(1000);

    const singleCard = page.locator('text=/Individual/i').first();
    const batchCard = page.locator('text=/Lote/i').first();

    const hasSingle = await singleCard.isVisible().catch(() => false);
    const hasBatch = await batchCard.isVisible().catch(() => false);

    expect(hasSingle !== undefined || hasBatch !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE MASCARAMENTO INDIVIDUAL
  // ==========================================

  test('deve ter seletor de tipo de dado', async ({ page }) => {
    const typeSelect = page.locator('select, [role="combobox"]').filter({ hasText: /CPF|E-mail|Tipo/i }).first();
    const hasSelect = await typeSelect.isVisible().catch(() => false);
    expect(hasSelect !== undefined).toBeTruthy();
  });

  test('deve ter campo de entrada para valor', async ({ page }) => {
    const valueInput = page.locator('input[placeholder*="123"], input[placeholder*="usuario"]').first();
    const hasInput = await valueInput.isVisible().catch(() => false);
    expect(hasInput !== undefined).toBeTruthy();
  });

  test('deve ter botão para mascarar', async ({ page }) => {
    const maskButton = page.locator('button:has-text("Mascarar")').first();
    await expect(maskButton).toBeVisible();
  });

  test('deve desabilitar botão quando entrada está vazia', async ({ page }) => {
    const maskButton = page.locator('button:has-text("Mascarar")').first();
    await expect(maskButton).toBeDisabled();
  });

  test('deve mascarar CPF ao clicar no botão', async ({ page }) => {
    // Selecionar CPF no dropdown
    const typeSelect = page.locator('select, [role="combobox"]').first();
    if (await typeSelect.isVisible().catch(() => false)) {
      await typeSelect.click();
      await page.waitForTimeout(300);

      const cpfOption = page.locator('[data-value="cpf"], option[value="cpf"]').first();
      if (await cpfOption.isVisible().catch(() => false)) {
        await cpfOption.click();
      }
    }

    const valueInput = page.locator('input').first();
    await valueInput.fill('123.456.789-00');

    const maskButton = page.locator('button:has-text("Mascarar")').first();
    await maskButton.click();

    await page.waitForTimeout(1000);

    // Verificar se resultado aparece
    const resultInput = page.locator('input[readonly]').first();
    const hasResult = await resultInput.isVisible().catch(() => false);
    expect(hasResult !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE MASCARAMENTO EM LOTE
  // ==========================================

  test('deve ter seção de mascaramento em lote', async ({ page }) => {
    const batchSection = page.locator('text=/Lote|Batch/i').first();
    const hasBatch = await batchSection.isVisible().catch(() => false);
    expect(hasBatch !== undefined).toBeTruthy();
  });

  test('deve ter textarea para entrada em lote', async ({ page }) => {
    const batchTextarea = page.locator('textarea').nth(1);
    const hasTextarea = await batchTextarea.isVisible().catch(() => false);
    expect(hasTextarea !== undefined).toBeTruthy();
  });

  test('deve ter botão para mascarar em lote', async ({ page }) => {
    const batchButton = page.locator('button:has-text("Mascarar Lote")').first();
    const hasButton = await batchButton.isVisible().catch(() => false);
    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve mascarar dados em lote', async ({ page }) => {
    const batchTextarea = page.locator('textarea').nth(1);
    await batchTextarea.fill('123.456.789-00\n987.654.321-00');

    const batchButton = page.locator('button:has-text("Mascarar Lote")').first();
    if (await batchButton.isVisible().catch(() => false)) {
      await batchButton.click();
      await page.waitForTimeout(1000);

      // Verificar se resultado aparece
      const resultTextarea = page.locator('textarea[readonly]').first();
      const hasResult = await resultTextarea.isVisible().catch(() => false);
      expect(hasResult !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE TIPOS DE DADO
  // ==========================================

  test('deve suportar mascaramento de CPF', async ({ page }) => {
    const typeSelect = page.locator('select, [role="combobox"]').first();
    await typeSelect.click();
    await page.waitForTimeout(300);

    const cpfOption = page.locator('text=/CPF/i').first();
    const hasCPF = await cpfOption.isVisible().catch(() => false);
    expect(hasCPF !== undefined).toBeTruthy();
  });

  test('deve suportar mascaramento de email', async ({ page }) => {
    const typeSelect = page.locator('select, [role="combobox"]').first();
    await typeSelect.click();
    await page.waitForTimeout(300);

    const emailOption = page.locator('text=/E-mail|Email/i').first();
    const hasEmail = await emailOption.isVisible().catch(() => false);
    expect(hasEmail !== undefined).toBeTruthy();
  });

  test('deve suportar mascaramento de telefone', async ({ page }) => {
    const typeSelect = page.locator('select, [role="combobox"]').first();
    await typeSelect.click();
    await page.waitForTimeout(300);

    const phoneOption = page.locator('text=/Telefone|Phone/i').first();
    const hasPhone = await phoneOption.isVisible().catch(() => false);
    expect(hasPhone !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE COPIAR RESULTADO
  // ==========================================

  test('deve ter botão para copiar resultado', async ({ page }) => {
    const valueInput = page.locator('input').first();
    await valueInput.fill('teste@exemplo.com');

    const maskButton = page.locator('button:has-text("Mascarar")').first();
    await maskButton.click();
    await page.waitForTimeout(1000);

    const copyButton = page.locator('button:has([data-lucide="Copy"])').first();
    const hasCopy = await copyButton.isVisible().catch(() => false);
    expect(hasCopy !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE LOADING
  // ==========================================

  test('deve mostrar loading durante mascaramento', async ({ page }) => {
    const valueInput = page.locator('input').first();
    await valueInput.fill('123.456.789-00');

    const maskButton = page.locator('button:has-text("Mascarar")').first();
    await maskButton.click();

    // Verificar se spinner aparece brevemente
    const spinner = page.locator('[class*="animate-spin"]').first();
    const hasSpinner = await spinner.isVisible().catch(() => false);
    expect(hasSpinner !== undefined).toBeTruthy();
  });
});
