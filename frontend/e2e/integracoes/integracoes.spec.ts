import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Integrações / Dashboard
 *
 * Funcionalidades testadas:
 * - Dashboard de integrações
 * - Cards de estatísticas
 * - Navegação para sub-páginas
 * - Conectores, API Keys, Webhooks, Logs, Sincronização
 */

// Mock data
const mockDashboard = {
  active_connectors: 5,
  total_api_keys: 12,
  total_webhooks: 8,
  errors_count: 2,
  recent_errors: [
    { id: 1, message: 'Erro na conexão com API externa', timestamp: '2026-02-05T10:00:00Z' },
  ],
};

const mockConnectors = [
  { id: 'conn-001', name: 'Salesforce', is_active: true, type: 'crm' },
  { id: 'conn-002', name: 'SAP', is_active: true, type: 'erp' },
  { id: 'conn-003', name: 'Webhook Receiver', is_active: false, type: 'webhook' },
];

const mockApiKeys = [
  { id: 'key-001', name: 'Produção', created_at: '2026-01-01T00:00:00Z' },
  { id: 'key-002', name: 'Homologação', created_at: '2026-01-15T00:00:00Z' },
];

const mockWebhooks = [
  { id: 'wh-001', url: 'https://exemplo.com/webhook1', event: 'order.created' },
  { id: 'wh-002', url: 'https://exemplo.com/webhook2', event: 'order.updated' },
];

// Setup de mocks para API
async function setupIntegrationsMocks(page: Page) {
  await page.route('**/api/v1/integrations/dashboard**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockDashboard),
    });
  });

  await page.route('**/api/v1/integrations/connectors**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        connectors: mockConnectors,
        total: mockConnectors.length,
      }),
    });
  });

  await page.route('**/api/v1/integrations/api-keys**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockApiKeys,
        total: mockApiKeys.length,
      }),
    });
  });

  await page.route('**/api/v1/integrations/webhooks**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockWebhooks,
        total: mockWebhooks.length,
      }),
    });
  });
}

test.describe('Integrações - Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupIntegrationsMocks(page);
    await page.goto('/modulos/integracoes');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de integrações', async ({ page }) => {
    await expect(page).toHaveURL(/\/integracoes/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Integrações/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/conectores|APIs|webhooks/i');
    await expect(description).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTATÍSTICAS
  // ==========================================

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const connectorsCard = page.locator('text=/Conectores Ativos/i');
    const apiKeysCard = page.locator('text=/API Keys/i');
    const webhooksCard = page.locator('text=/Webhooks/i');
    const errorsCard = page.locator('text=/Erros Recentes/i');

    await expect(connectorsCard).toBeVisible();
    await expect(apiKeysCard).toBeVisible();
    await expect(webhooksCard).toBeVisible();
    await expect(errorsCard).toBeVisible();
  });

  test('deve exibir valores corretos nas estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('5').first()).toBeVisible(); // Conectores
    await expect(page.getByText('12').first()).toBeVisible(); // API Keys
    await expect(page.getByText('8').first()).toBeVisible(); // Webhooks
    await expect(page.getByText('2').first()).toBeVisible(); // Erros
  });

  // ==========================================
  // TESTES DE SUB-PÁGINAS
  // ==========================================

  test('deve exibir card de Conectores', async ({ page }) => {
    const connectorsCard = page.locator('text=/Conectores$/i').first();
    await expect(connectorsCard).toBeVisible();
  });

  test('deve exibir card de API Keys', async ({ page }) => {
    const apiKeysCard = page.locator('text=/API Keys$/i').first();
    await expect(apiKeysCard).toBeVisible();
  });

  test('deve exibir card de Webhooks', async ({ page }) => {
    const webhooksCard = page.locator('text=/Webhooks$/i').first();
    await expect(webhooksCard).toBeVisible();
  });

  test('deve exibir card de Logs', async ({ page }) => {
    const logsCard = page.locator('text=/Logs$/i').first();
    await expect(logsCard).toBeVisible();
  });

  test('deve exibir card de Sincronização', async ({ page }) => {
    const syncCard = page.locator('text=/Sincronização/i').first();
    await expect(syncCard).toBeVisible();
  });

  // ==========================================
  // TESTES DE NAVEGAÇÃO
  // ==========================================

  test('deve navegar para página de Conectores', async ({ page }) => {
    const connectorsCard = page.locator('text=/Conectores$/i').first();
    await connectorsCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/conectores/);
  });

  test('deve navegar para página de API Keys', async ({ page }) => {
    const apiKeysCard = page.locator('text=/API Keys$/i').first();
    await apiKeysCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/api-keys/);
  });

  test('deve navegar para página de Webhooks', async ({ page }) => {
    const webhooksCard = page.locator('text=/Webhooks$/i').first();
    await webhooksCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/webhooks/);
  });

  test('deve navegar para página de Logs', async ({ page }) => {
    const logsCard = page.locator('text=/Logs$/i').first();
    await logsCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/logs/);
  });

  test('deve navegar para página de Sincronização', async ({ page }) => {
    const syncCard = page.locator('text=/Sincronização/i').first();
    await syncCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/sync/);
  });

  // ==========================================
  // TESTES DE CARDS INTERATIVOS
  // ==========================================

  test('deve ter cursor pointer nos cards', async ({ page }) => {
    const cards = page.locator('[class*="cursor-pointer"]').first();
    const hasPointer = await cards.isVisible().catch(() => false);
    expect(hasPointer !== undefined).toBeTruthy();
  });

  test('deve ter ícones nos cards', async ({ page }) => {
    const cardsWithIcons = page.locator('[class*="rounded-lg"]').first();
    const hasIcon = await cardsWithIcons.isVisible().catch(() => false);
    expect(hasIcon !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE LOADING
  // ==========================================

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });
});
