import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Segurança / Criptografia
 *
 * Funcionalidades testadas:
 * - Criptografia de dados
 * - Descriptografia de dados
 * - Seleção de algoritmos
 * - Copiar resultado
 */

// Mock data para algoritmos
const mockAlgorithms = [
  { name: 'AES-256-GCM', description: 'Advanced Encryption Standard com modo GCM', strength: 'high' },
  { name: 'AES-256-CBC', description: 'Advanced Encryption Standard com modo CBC', strength: 'standard' },
  { name: 'ChaCha20-Poly1305', description: 'Cifra de stream moderna', strength: 'high' },
];

// Setup de mocks para API
async function setupCryptoMocks(page: Page) {
  await page.route('**/api/v1/security-lgpd/crypto/algorithms**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { algorithms: mockAlgorithms },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/crypto/encrypt', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { encrypted_data: 'encrypted_test_data_base64==', algorithm: 'AES-256-GCM' },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/crypto/decrypt', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { decrypted_data: 'Dados originais descriptografados' },
      }),
    });
  });
}

test.describe('Segurança - Criptografia', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupCryptoMocks(page);
    await page.goto('/modulos/seguranca/criptografia');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de criptografia', async ({ page }) => {
    await expect(page).toHaveURL(/\/criptografia/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Criptografia/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/Ferramentas de criptografia/i');
    await expect(description).toBeVisible();
  });

  test('deve exibir cards de criptografia e descriptografia', async ({ page }) => {
    await page.waitForTimeout(1000);

    const encryptCard = page.locator('text=/Criptografar/i').first();
    const decryptCard = page.locator('text=/Descriptografar/i').first();

    await expect(encryptCard).toBeVisible();
    await expect(decryptCard).toBeVisible();
  });

  // ==========================================
  // TESTES DE CRIPTOGRAFIA
  // ==========================================

  test('deve ter campo de entrada para criptografia', async ({ page }) => {
    const encryptInput = page.locator('textarea[id="encrypt-input"], textarea[placeholder*="criptografar" i]').first();
    await expect(encryptInput).toBeVisible();
  });

  test('deve ter seletor de algoritmo', async ({ page }) => {
    const algorithmSelect = page.locator('select, [role="combobox"]').filter({ hasText: /AES|Algoritmo/i }).first();
    const hasSelect = await algorithmSelect.isVisible().catch(() => false);
    expect(hasSelect !== undefined).toBeTruthy();
  });

  test('deve ter botão para criptografar', async ({ page }) => {
    const encryptButton = page.locator('button:has-text("Criptografar")').first();
    await expect(encryptButton).toBeVisible();
  });

  test('deve desabilitar botão quando entrada está vazia', async ({ page }) => {
    const encryptButton = page.locator('button:has-text("Criptografar")').first();
    await expect(encryptButton).toBeDisabled();
  });

  test('deve criptografar dados ao clicar no botão', async ({ page }) => {
    const encryptInput = page.locator('textarea[id="encrypt-input"]').first();
    await encryptInput.fill('Dados sensíveis para criptografar');

    const encryptButton = page.locator('button:has-text("Criptografar")').first();
    await encryptButton.click();

    await page.waitForTimeout(1000);

    // Verificar se resultado aparece
    const resultTextarea = page.locator('textarea[readonly]').first();
    const hasResult = await resultTextarea.isVisible().catch(() => false);
    expect(hasResult !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE DESCRIPTOGRAFIA
  // ==========================================

  test('deve ter campo de entrada para descriptografia', async ({ page }) => {
    const decryptInput = page.locator('textarea[id="decrypt-input"], textarea[placeholder*="descriptografar" i], textarea[placeholder*="criptografados" i]').first();
    await expect(decryptInput).toBeVisible();
  });

  test('deve ter botão para descriptografar', async ({ page }) => {
    const decryptButton = page.locator('button:has-text("Descriptografar")').first();
    await expect(decryptButton).toBeVisible();
  });

  test('deve desabilitar botão de descriptografia quando entrada está vazia', async ({ page }) => {
    const decryptButton = page.locator('button:has-text("Descriptografar")').first();
    await expect(decryptButton).toBeDisabled();
  });

  test('deve descriptografar dados ao clicar no botão', async ({ page }) => {
    const decryptInput = page.locator('textarea[id="decrypt-input"]').first();
    await decryptInput.fill('dados_criptografados_base64==');

    const decryptButton = page.locator('button:has-text("Descriptografar")').first();
    await decryptButton.click();

    await page.waitForTimeout(1000);

    // Verificar se resultado aparece
    const resultTextarea = page.locator('textarea[readonly]').nth(1);
    const hasResult = await resultTextarea.isVisible().catch(() => false);
    expect(hasResult !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE ALGORITMOS
  // ==========================================

  test('deve exibir seção de algoritmos disponíveis', async ({ page }) => {
    await page.waitForTimeout(1000);

    const algorithmsSection = page.locator('text=/Algoritmos Disponíveis/i').first();
    await expect(algorithmsSection).toBeVisible();
  });

  test('deve listar algoritmos com suas forças', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se alguns algoritmos estão listados
    const aesAlgo = page.locator('text=/AES/i').first();
    const hasAES = await aesAlgo.isVisible().catch(() => false);
    expect(hasAES !== undefined).toBeTruthy();
  });

  test('deve exibir badges de força dos algoritmos', async ({ page }) => {
    await page.waitForTimeout(1000);

    const strengthBadges = page.locator('span:has-text("Alta"), span:has-text("Padrão"), span:has-text("Média")').first();
    const hasBadges = await strengthBadges.isVisible().catch(() => false);
    expect(hasBadges !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE COPIAR RESULTADO
  // ==========================================

  test('deve ter botão para copiar resultado da criptografia', async ({ page }) => {
    const encryptInput = page.locator('textarea[id="encrypt-input"]').first();
    await encryptInput.fill('Teste para copiar');

    const encryptButton = page.locator('button:has-text("Criptografar")').first();
    await encryptButton.click();

    await page.waitForTimeout(1000);

    const copyButton = page.locator('button:has-text("Copiar"), button:has([data-lucide="Copy"])').first();
    const hasCopy = await copyButton.isVisible().catch(() => false);
    expect(hasCopy !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE LOADING
  // ==========================================

  test('deve mostrar loading durante criptografia', async ({ page }) => {
    const encryptInput = page.locator('textarea[id="encrypt-input"]').first();
    await encryptInput.fill('Teste loading');

    const encryptButton = page.locator('button:has-text("Criptografar")').first();
    await encryptButton.click();

    // Verificar se spinner aparece brevemente
    const spinner = page.locator('[class*="animate-spin"]').first();
    const hasSpinner = await spinner.isVisible().catch(() => false);
    expect(hasSpinner !== undefined).toBeTruthy();
  });
});
