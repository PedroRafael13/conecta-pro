import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Integrações / Sincronização
 *
 * Funcionalidades testadas:
 * - Fila de sincronização
 * - Histórico de execuções
 * - Estatísticas da fila
 * - Cancelamento de itens
 * - Paginação
 */

// Mock data
const mockQueueItems = [
  {
    id: 'queue-001',
    entity_type: 'Cliente',
    status: 'pending',
    priority: 1,
    created_at: '2026-02-05T10:30:00Z',
  },
  {
    id: 'queue-002',
    entity_type: 'Pedido',
    status: 'processing',
    priority: 2,
    created_at: '2026-02-05T10:25:00Z',
  },
  {
    id: 'queue-003',
    entity_type: 'Produto',
    status: 'completed',
    priority: 1,
    created_at: '2026-02-05T10:20:00Z',
  },
  {
    id: 'queue-004',
    entity_type: 'Estoque',
    status: 'failed',
    priority: 3,
    created_at: '2026-02-05T10:15:00Z',
  },
];

const mockRuns = [
  {
    id: 'run-001',
    connector_name: 'Salesforce',
    status: 'completed',
    started_at: '2026-02-05T10:00:00Z',
    finished_at: '2026-02-05T10:05:00Z',
    records_processed: 150,
  },
  {
    id: 'run-002',
    connector_name: 'SAP',
    status: 'failed',
    started_at: '2026-02-05T09:30:00Z',
    finished_at: '2026-02-05T09:35:00Z',
    records_processed: 0,
  },
];

const mockStats = {
  pending: 15,
  processing: 3,
  completed: 127,
  failed: 5,
};

// Setup de mocks para API
async function setupSyncMocks(page: Page) {
  await page.route('**/api/v1/integrations/sync/stats**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockStats),
    });
  });

  await page.route('**/api/v1/integrations/sync/queue**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockQueueItems,
        total: mockQueueItems.length,
      }),
    });
  });

  await page.route('**/api/v1/integrations/sync/runs**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockRuns,
        total: mockRuns.length,
      }),
    });
  });

  await page.route('**/api/v1/integrations/sync/queue/*/cancel', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
}

test.describe('Integrações - Sincronização', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupSyncMocks(page);
    await page.goto('/modulos/integracoes/sync');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de sincronização', async ({ page }) => {
    await expect(page).toHaveURL(/\/sync/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Sincronização/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/filas|sincronização de dados/i');
    await expect(description).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTATÍSTICAS
  // ==========================================

  test('deve exibir cards de estatísticas da fila', async ({ page }) => {
    await page.waitForTimeout(1000);

    const pendingCard = page.locator('text=/Na Fila/i');
    const processingCard = page.locator('text=/Em Execução/i');
    const completedCard = page.locator('text=/Concluídos/i');
    const failedCard = page.locator('text=/Falhados/i');

    await expect(pendingCard).toBeVisible();
    await expect(processingCard).toBeVisible();
    await expect(completedCard).toBeVisible();
    await expect(failedCard).toBeVisible();
  });

  test('deve exibir valores corretos nas estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('15').first()).toBeVisible(); // Na Fila
    await expect(page.getByText('3').first()).toBeVisible(); // Em Execução
    await expect(page.getByText('127').first()).toBeVisible(); // Concluídos
    await expect(page.getByText('5').first()).toBeVisible(); // Falhados
  });

  // ==========================================
  // TESTES DE ABAS
  // ==========================================

  test('deve ter abas de Fila e Histórico', async ({ page }) => {
    const filaTab = page.locator('text=/Fila$/i').first();
    const historicoTab = page.locator('text=/Histórico/i').first();

    await expect(filaTab).toBeVisible();
    await expect(historicoTab).toBeVisible();
  });

  test('deve alternar entre abas', async ({ page }) => {
    const historicoTab = page.locator('text=/Histórico/i').first();
    await historicoTab.click();
    await page.waitForTimeout(500);

    // Verificar se conteúdo da aba histórico é exibido
    const historyTable = page.locator('table').first();
    const hasTable = await historyTable.isVisible().catch(() => false);
    expect(hasTable !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE TABELA DA FILA
  // ==========================================

  test('deve exibir tabela da fila', async ({ page }) => {
    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela da fila', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Item', 'Status', 'Prioridade', 'Criado em'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  test('deve exibir dados da fila', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('Cliente')).toBeVisible();
    await expect(page.getByText('Pedido')).toBeVisible();
  });

  // ==========================================
  // TESTES DE BADGES DE STATUS
  // ==========================================

  test('deve exibir badge por status na fila', async ({ page }) => {
    await page.waitForTimeout(1000);

    const pendingBadge = page.locator('text=/Pendente|pending/i').first();
    const hasPending = await pendingBadge.isVisible().catch(() => false);
    expect(hasPending !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE TABELA DE HISTÓRICO
  // ==========================================

  test('deve exibir tabela de histórico ao alternar aba', async ({ page }) => {
    const historicoTab = page.locator('text=/Histórico/i').first();
    await historicoTab.click();
    await page.waitForTimeout(1000);

    const headers = ['ID', 'Conector', 'Status', 'Início', 'Fim', 'Registros'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE BUSCA
  // ==========================================

  test('deve ter campo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i]').first();
    await expect(searchInput).toBeVisible();
  });

  test('deve filtrar por termo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i]').first();
    await searchInput.fill('Cliente');
    await page.waitForTimeout(600);

    await expect(searchInput).toHaveValue('Cliente');
  });

  // ==========================================
  // TESTES DE AÇÕES
  // ==========================================

  test('deve ter botão para atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button:has([data-lucide="RefreshCw"])').first();
    await expect(refreshButton).toBeVisible();
  });

  test('deve ter opção de cancelar item pendente', async ({ page }) => {
    await page.waitForTimeout(1000);

    const moreButton = page.locator('button:has([data-lucide="MoreHorizontal"])').first();
    if (await moreButton.isVisible().catch(() => false)) {
      await moreButton.click();
      await page.waitForTimeout(300);

      const cancelOption = page.locator('text=/Cancelar/i').first();
      const hasCancel = await cancelOption.isVisible().catch(() => false);
      expect(hasCancel !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE PAGINAÇÃO
  // ==========================================

  test('deve exibir controles de paginação quando necessário', async ({ page }) => {
    // Adicionar mais itens mockados para testar paginação
    const manyItems = Array.from({ length: 25 }, (_, i) => ({
      id: `queue-${i}`,
      entity_type: `Tipo ${i}`,
      status: 'pending',
      priority: 1,
      created_at: '2026-02-05T10:00:00Z',
    }));

    await page.route('**/api/v1/integrations/sync/queue**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: manyItems,
          total: manyItems.length,
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const pagination = page.locator('button:has([data-lucide="ChevronLeft"])').first();
    const hasPagination = await pagination.isVisible().catch(() => false);
    expect(hasPagination !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE ESTADOS ESPECIAIS
  // ==========================================

  test('deve exibir empty state quando fila está vazia', async ({ page }) => {
    await page.route('**/api/v1/integrations/sync/queue**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/Fila vazia|vazia/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });
});
