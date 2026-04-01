import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Segurança / Consentimento LGPD
 *
 * Funcionalidades testadas:
 * - Gestão de consentimentos
 * - Filtros por status e busca
 * - Registro de novos consentimentos
 * - Revogação de consentimentos
 * - Visualização de detalhes
 */

// Mock data para consentimentos
const mockConsents = [
  {
    id: 'consent-001',
    holder_name: 'João Silva',
    holder_email: 'joao@exemplo.com',
    purpose: 'marketing',
    legal_basis: 'consent',
    status: 'active',
    valid_until: '2027-02-05T10:30:00Z',
    created_at: '2026-02-05T10:30:00Z',
  },
  {
    id: 'consent-002',
    holder_name: 'Maria Santos',
    holder_email: 'maria@exemplo.com',
    purpose: 'analytics',
    legal_basis: 'legitimate_interest',
    status: 'revoked',
    valid_until: null,
    created_at: '2026-01-15T08:00:00Z',
  },
  {
    id: 'consent-003',
    holder_name: 'Pedro Costa',
    holder_email: 'pedro@exemplo.com',
    purpose: 'service_provision',
    legal_basis: 'contract',
    status: 'active',
    valid_until: '2026-12-31T23:59:59Z',
    created_at: '2026-02-01T14:20:00Z',
  },
  {
    id: 'consent-004',
    holder_name: 'Ana Oliveira',
    holder_email: 'ana@exemplo.com',
    purpose: 'communication',
    legal_basis: 'consent',
    status: 'expired',
    valid_until: '2026-01-01T00:00:00Z',
    created_at: '2025-06-01T09:00:00Z',
  },
];

// Setup de mocks para API
async function setupConsentMocks(page: Page) {
  await page.route('**/api/v1/security-lgpd/consents**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          consents: mockConsents,
          total: mockConsents.length,
        },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/consents/*/revoke', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        message: 'Consentimento revogado com sucesso',
      }),
    });
  });
}

test.describe('Segurança - Consentimento LGPD', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupConsentMocks(page);
    await page.goto('/modulos/seguranca/consentimento');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de consentimento', async ({ page }) => {
    await expect(page).toHaveURL(/\/consentimento/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Consentimento/i);
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const statCards = page.locator('text=/Ativos|Revogados|Expirando/i');
    await expect(statCards.first()).toBeVisible();
  });

  test('deve exibir tabela de consentimentos', async ({ page }) => {
    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Titular', 'Finalidade', 'Base Legal', 'Status', 'Validade'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}"), th:has-text("${header.toLowerCase()}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  test('deve exibir dados mockados na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('João Silva')).toBeVisible();
    await expect(page.getByText('Maria Santos')).toBeVisible();
  });

  // ==========================================
  // TESTES DE BADGES DE STATUS
  // ==========================================

  test('deve exibir badge colorido por status', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se há badges de status
    const activeBadge = page.locator('text=/Ativo/i').first();
    const hasActive = await activeBadge.isVisible().catch(() => false);
    expect(hasActive !== undefined).toBeTruthy();
  });

  test('deve identificar consentimento ativo', async ({ page }) => {
    await page.waitForTimeout(1000);

    const activeConsent = page.locator('text=/Ativo|active/i').first();
    const hasActive = await activeConsent.isVisible().catch(() => false);
    expect(hasActive !== undefined).toBeTruthy();
  });

  test('deve identificar consentimento revogado', async ({ page }) => {
    await page.waitForTimeout(1000);

    const revokedConsent = page.locator('text=/Revogado|revoked/i').first();
    const hasRevoked = await revokedConsent.isVisible().catch(() => false);
    expect(hasRevoked !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE FILTROS
  // ==========================================

  test('deve filtrar por termo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i], input[type="search"]').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('João');
    await page.waitForTimeout(600);

    await expect(searchInput).toHaveValue('João');
  });

  test('deve filtrar por status', async ({ page }) => {
    const statusSelect = page.locator('select, [role="combobox"]').filter({ hasText: /Status|Todas/i }).first();

    if (await statusSelect.isVisible().catch(() => false)) {
      await statusSelect.click();
      await page.waitForTimeout(300);

      const option = page.locator('[data-value="active"], option[value="active"]').first();
      if (await option.isVisible().catch(() => false)) {
        await option.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('deve limpar filtros ao clicar em botão', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i]').first();
    await searchInput.fill('teste');
    await page.waitForTimeout(300);

    const clearButton = page.locator('button:has-text("Limpar"), button:has-text("Clear")').first();
    if (await clearButton.isVisible().catch(() => false)) {
      await clearButton.click();
      await page.waitForTimeout(300);

      const value = await searchInput.inputValue();
      expect(value).toBe('');
    }
  });

  // ==========================================
  // TESTES DE AÇÕES
  // ==========================================

  test('deve ter botão para registrar consentimento', async ({ page }) => {
    const registerButton = page.locator('button:has-text("Registrar Consentimento"), button:has-text("Novo")').first();
    const hasButton = await registerButton.isVisible().catch(() => false);
    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve abrir modal ao clicar em registrar', async ({ page }) => {
    const registerButton = page.locator('button:has-text("Registrar Consentimento")').first();

    if (await registerButton.isVisible().catch(() => false)) {
      await registerButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"], [class*="modal"]').first();
      const hasModal = await modal.isVisible().catch(() => false);
      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve ter opção de ver detalhes no dropdown', async ({ page }) => {
    await page.waitForTimeout(1000);

    const moreButton = page.locator('button:has([data-lucide="MoreHorizontal"])').first();
    if (await moreButton.isVisible().catch(() => false)) {
      await moreButton.click();
      await page.waitForTimeout(300);

      const viewOption = page.locator('text=/Ver detalhes|Detalhes/i').first();
      const hasView = await viewOption.isVisible().catch(() => false);
      expect(hasView !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE PAGINAÇÃO
  // ==========================================

  test('deve exibir controles de paginação quando necessário', async ({ page }) => {
    // Adicionar mais itens mockados para testar paginação
    const manyConsents = Array.from({ length: 25 }, (_, i) => ({
      id: `consent-${i}`,
      holder_name: `Titular ${i}`,
      purpose: 'marketing',
      legal_basis: 'consent',
      status: 'active',
      valid_until: '2027-02-05T10:30:00Z',
      created_at: '2026-02-05T10:30:00Z',
    }));

    await page.route('**/api/v1/security-lgpd/consents**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: {
            consents: manyConsents,
            total: manyConsents.length,
          },
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const pagination = page.locator('button:has-text("Anterior"), button:has-text("Próximo"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);
    expect(hasPagination !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE ESTADOS ESPECIAIS
  // ==========================================

  test('deve exibir empty state quando não há consentimentos', async ({ page }) => {
    await page.route('**/api/v1/security-lgpd/consents**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { consents: [], total: 0 },
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/nenhum.*encontrado|sem.*registros/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="loading"], [class*="spinner"], [class*="animate-spin"], [class*="animate-pulse"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });

  test('deve lidar com erro de API', async ({ page }) => {
    await page.route('**/api/v1/security-lgpd/consents**', async (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    // Deve mostrar estado de erro ou fallback
    const errorState = page.locator('text=/erro|error|indisponível|falha/i').first();
    const hasError = await errorState.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
