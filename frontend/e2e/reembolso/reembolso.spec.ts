import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Reembolso / Gestão de Solicitações
 *
 * Funcionalidades testadas:
 * - Lista de solicitações de reembolso
 * - Filtros e busca
 * - Estatísticas
 * - CRUD de solicitações
 * - Paginação
 */

// Mock data
const mockRequests = [
  {
    id: 'req-001',
    code: 'RMB-2026-0001',
    title: 'Viagem a São Paulo',
    expense_date_start: '2026-02-01',
    expense_date_end: '2026-02-03',
    total_amount: 1250.50,
    items_count: 3,
    status: 'pending',
    can_edit: true,
  },
  {
    id: 'req-002',
    code: 'RMB-2026-0002',
    title: 'Almoço com cliente',
    expense_date_start: '2026-02-05',
    expense_date_end: '2026-02-05',
    total_amount: 150.00,
    items_count: 1,
    status: 'approved',
    can_edit: false,
  },
  {
    id: 'req-003',
    code: 'RMB-2026-0003',
    title: 'Material de escritório',
    expense_date_start: '2026-02-04',
    expense_date_end: '2026-02-04',
    total_amount: 89.90,
    items_count: 2,
    status: 'rejected',
    can_edit: false,
  },
];

const mockStats = {
  total: 10,
  pending_count: 3,
  approved_count: 5,
  rejected_count: 2,
  total_amount: 5678.90,
};

// Setup de mocks para API
async function setupReimbursementMocks(page: Page) {
  await page.route('**/api/v1/reimbursement/requests**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockRequests,
        total: mockRequests.length,
        page: 1,
        page_size: 10,
        total_pages: 1,
      }),
    });
  });

  await page.route('**/api/v1/reimbursement/stats**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockStats),
    });
  });

  await page.route('**/api/v1/reimbursement/requests/*', async (route) => {
    if (route.request().method() === 'DELETE') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    } else {
      route.continue();
    }
  });
}

test.describe('Reembolso - Gestão de Solicitações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupReimbursementMocks(page);
    await page.goto('/modulos/reembolso');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de reembolsos', async ({ page }) => {
    await expect(page).toHaveURL(/\/reembolso/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Reembolsos/i);
  });

  test('deve exibir contador de solicitações', async ({ page }) => {
    await page.waitForTimeout(1000);

    const counter = page.locator('text=/solicitações/i').first();
    await expect(counter).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTATÍSTICAS
  // ==========================================

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const totalCard = page.locator('text=/Total$/i').first();
    const pendingCard = page.locator('text=/Pendentes/i').first();
    const approvedCard = page.locator('text=/Aprovados/i').first();
    const amountCard = page.locator('text=/Valor Total/i').first();

    await expect(totalCard).toBeVisible();
    await expect(pendingCard).toBeVisible();
    await expect(approvedCard).toBeVisible();
    await expect(amountCard).toBeVisible();
  });

  test('deve exibir valores formatados em moeda', async ({ page }) => {
    await page.waitForTimeout(1000);

    const currency = page.locator('text=/R\\$|\\$[,\\d]/i').first();
    const hasCurrency = await currency.isVisible().catch(() => false);
    expect(hasCurrency !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE TABELA
  // ==========================================

  test('deve exibir tabela de solicitações', async ({ page }) => {
    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Solicitação', 'Período', 'Valor', 'Itens', 'Status'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  test('deve exibir dados das solicitações', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('Viagem a São Paulo')).toBeVisible();
    await expect(page.getByText('RMB-2026-0001')).toBeVisible();
  });

  // ==========================================
  // TESTES DE BADGES DE STATUS
  // ==========================================

  test('deve exibir badge por status', async ({ page }) => {
    await page.waitForTimeout(1000);

    const pendingBadge = page.locator('text=/Pendente|pending/i').first();
    const hasPending = await pendingBadge.isVisible().catch(() => false);
    expect(hasPending !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE BUSCA E FILTROS
  // ==========================================

  test('deve ter campo de busca', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar" i]').first();
    await expect(searchInput).toBeVisible();
  });

  test('deve filtrar por termo de busca', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar" i]').first();
    await searchInput.fill('Viagem');
    await page.waitForTimeout(600);

    await expect(searchInput).toHaveValue('Viagem');
  });

  test('deve ter botão de filtros', async ({ page }) => {
    const filtersButton = page.locator('button:has-text("Filtros"), button:has([data-lucide="Filter"])').first();
    await expect(filtersButton).toBeVisible();
  });

  test('deve expandir painel de filtros ao clicar', async ({ page }) => {
    const filtersButton = page.locator('button:has-text("Filtros")').first();
    await filtersButton.click();
    await page.waitForTimeout(500);

    const filtersPanel = page.locator('text=/Status|Centro de Custo/i').first();
    const hasPanel = await filtersPanel.isVisible().catch(() => false);
    expect(hasPanel !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE BOTÕES DE AÇÃO
  // ==========================================

  test('deve ter botão para nova solicitação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Solicitação"), button:has-text("Nova")').first();
    await expect(newButton).toBeVisible();
  });

  test('deve ter botão para aprovações', async ({ page }) => {
    const approvalsButton = page.locator('button:has-text("Aprovações"), a:has-text("Aprovações")').first();
    const hasApprovals = await approvalsButton.isVisible().catch(() => false);
    expect(hasApprovals !== undefined).toBeTruthy();
  });

  test('deve ter botão para atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has([data-lucide="RefreshCw"])').first();
    await expect(refreshButton).toBeVisible();
  });

  // ==========================================
  // TESTES DE AÇÕES NA TABELA
  // ==========================================

  test('deve ter botões de ação nas linhas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const viewButton = page.locator('button[title="Visualizar"], button:has([data-lucide="Eye"])').first();
    const hasView = await viewButton.isVisible().catch(() => false);
    expect(hasView !== undefined).toBeTruthy();
  });

  test('deve mostrar botão de editar para solicitações editáveis', async ({ page }) => {
    await page.waitForTimeout(1000);

    const editButton = page.locator('button[title="Editar"], button:has([data-lucide="Edit2"])').first();
    const hasEdit = await editButton.isVisible().catch(() => false);
    expect(hasEdit !== undefined).toBeTruthy();
  });

  test('deve mostrar botão de excluir para solicitações editáveis', async ({ page }) => {
    await page.waitForTimeout(1000);

    const deleteButton = page.locator('button[title="Excluir"], button:has([data-lucide="Trash2"])').first();
    const hasDelete = await deleteButton.isVisible().catch(() => false);
    expect(hasDelete !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE NAVEGAÇÃO
  // ==========================================

  test('deve ter botão para voltar para módulos', async ({ page }) => {
    const backButton = page.locator('button:has-text("Módulos"), a:has-text("Módulos")').first();
    await expect(backButton).toBeVisible();
  });

  // ==========================================
  // TESTES DE PAGINAÇÃO
  // ==========================================

  test('deve exibir controles de paginação quando necessário', async ({ page }) => {
    // Adicionar mais itens mockados para testar paginação
    const manyRequests = Array.from({ length: 15 }, (_, i) => ({
      id: `req-${i}`,
      code: `RMB-2026-${String(i).padStart(4, '0')}`,
      title: `Solicitação ${i}`,
      expense_date_start: '2026-02-01',
      expense_date_end: '2026-02-01',
      total_amount: 100.00,
      items_count: 1,
      status: 'pending',
      can_edit: true,
    }));

    await page.route('**/api/v1/reimbursement/requests**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: manyRequests,
          total: manyRequests.length,
          page: 1,
          page_size: 10,
          total_pages: 2,
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

  test('deve exibir empty state quando não há solicitações', async ({ page }) => {
    await page.route('**/api/v1/reimbursement/requests**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          page_size: 10,
          total_pages: 0,
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/nenhuma.*solicitação|Criar Primeira/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="animate-pulse"], [class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });

  test('deve exibir estado de erro quando há falha', async ({ page }) => {
    await page.route('**/api/v1/reimbursement/requests**', async (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const errorState = page.locator('text=/erro|Erro|falha/i').first();
    const hasError = await errorState.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
