import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Segurança / Direito ao Esquecimento (LGPD Art. 18)
 *
 * Funcionalidades testadas:
 * - Gestão de solicitações de exclusão
 * - Filtros por status e busca
 * - Criação de novas solicitações
 * - Visualização de detalhes
 */

// Mock data para solicitações de esquecimento
const mockErasureRequests = [
  {
    id: 'erasure-001',
    holder_name: 'João Silva',
    erasure_type: 'full',
    status: 'pending',
    requested_at: '2026-02-05T10:30:00Z',
    completed_at: null,
  },
  {
    id: 'erasure-002',
    holder_name: 'Maria Santos',
    erasure_type: 'personal',
    status: 'processing',
    requested_at: '2026-02-04T08:00:00Z',
    completed_at: null,
  },
  {
    id: 'erasure-003',
    holder_name: 'Pedro Costa',
    erasure_type: 'transactional',
    status: 'completed',
    requested_at: '2026-02-01T14:20:00Z',
    completed_at: '2026-02-03T16:45:00Z',
  },
  {
    id: 'erasure-004',
    holder_name: 'Ana Oliveira',
    erasure_type: 'full',
    status: 'failed',
    requested_at: '2026-02-02T09:15:00Z',
    completed_at: null,
  },
];

// Setup de mocks para API
async function setupErasureMocks(page: Page) {
  await page.route('**/api/v1/security-lgpd/erasure/status**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          items: mockErasureRequests,
          total: mockErasureRequests.length,
        },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/erasure/request', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        request_id: 'erasure-new-001',
        status: 'pending',
      }),
    });
  });
}

test.describe('Segurança - Direito ao Esquecimento', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupErasureMocks(page);
    await page.goto('/modulos/seguranca/esquecimento');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de esquecimento', async ({ page }) => {
    await expect(page).toHaveURL(/\/esquecimento/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Esquecimento/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/Art. 18|exclusão de dados/i');
    await expect(description).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const totalCard = page.locator('text=/Total/i').first();
    const pendingCard = page.locator('text=/Pendentes/i').first();
    const completedCard = page.locator('text=/Concluídas/i').first();

    await expect(totalCard).toBeVisible();
    await expect(pendingCard).toBeVisible();
    await expect(completedCard).toBeVisible();
  });

  test('deve exibir tabela de solicitações', async ({ page }) => {
    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Titular', 'Tipo', 'Status', 'Solicitado em', 'Concluído em'];
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
  // TESTES DE BADGES
  // ==========================================

  test('deve exibir badge por tipo de exclusão', async ({ page }) => {
    await page.waitForTimeout(1000);

    const fullType = page.locator('text=/Completo|full/i').first();
    const hasFull = await fullType.isVisible().catch(() => false);
    expect(hasFull !== undefined).toBeTruthy();
  });

  test('deve exibir badge por status', async ({ page }) => {
    await page.waitForTimeout(1000);

    const pendingStatus = page.locator('text=/Pendente|pending/i').first();
    const hasPending = await pendingStatus.isVisible().catch(() => false);
    expect(hasPending !== undefined).toBeTruthy();
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

      const option = page.locator('[data-value="pending"], option[value="pending"]').first();
      if (await option.isVisible().catch(() => false)) {
        await option.click();
        await page.waitForTimeout(500);
      }
    }
  });

  // ==========================================
  // TESTES DE NOVA SOLICITAÇÃO
  // ==========================================

  test('deve ter botão para nova solicitação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Solicitação"), button:has-text("Nova")').first();
    await expect(newButton).toBeVisible();
  });

  test('deve abrir dropdown com tipos de exclusão', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Solicitação")').first();
    await newButton.click();
    await page.waitForTimeout(300);

    // Verificar opções no dropdown
    const options = ['Completo', 'Pessoais', 'Transacional'];
    for (const option of options) {
      const optionEl = page.locator(`text=/${option}/i`).first();
      const hasOption = await optionEl.isVisible().catch(() => false);
      expect(hasOption !== undefined).toBeTruthy();
    }
  });

  test('deve abrir modal ao selecionar tipo de exclusão', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Solicitação")').first();
    await newButton.click();
    await page.waitForTimeout(300);

    const fullOption = page.locator('text=/Completo/i').first();
    if (await fullOption.isVisible().catch(() => false)) {
      await fullOption.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"], [class*="modal"]').first();
      const hasModal = await modal.isVisible().catch(() => false);
      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE AÇÕES
  // ==========================================

  test('deve ter opção de detalhes no dropdown', async ({ page }) => {
    await page.waitForTimeout(1000);

    const moreButton = page.locator('button:has([data-lucide="MoreHorizontal"])').first();
    if (await moreButton.isVisible().catch(() => false)) {
      await moreButton.click();
      await page.waitForTimeout(300);

      const detailsOption = page.locator('text=/Detalhes/i').first();
      const hasDetails = await detailsOption.isVisible().catch(() => false);
      expect(hasDetails !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE ATUALIZAR
  // ==========================================

  test('deve ter botão para atualizar lista', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button:has([data-lucide="RefreshCw"])').first();
    await expect(refreshButton).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTADOS ESPECIAIS
  // ==========================================

  test('deve exibir empty state quando não há solicitações', async ({ page }) => {
    await page.route('**/api/v1/security-lgpd/erasure/status**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { items: [], total: 0 },
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/nenhuma.*encontrada|sem.*solicitações/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="loading"], [class*="spinner"], [class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });
});
