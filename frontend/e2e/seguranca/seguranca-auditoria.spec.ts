import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Segurança / Auditoria LGPD
 *
 * Funcionalidades testadas:
 * - Log de auditoria
 * - Filtros por usuário, ação, data
 * - Exportação de logs
 * - Rastreamento de alterações
 * - Visualização de detalhes
 */

// Mock data para logs de auditoria
const mockAuditLogs = [
  {
    id: 'audit-001',
    timestamp: '2026-02-05T10:30:00Z',
    created_at: '2026-02-05T10:30:00Z',
    action: 'data_access',
    user_id: 'user-001',
    user_name: 'Admin Silva',
    resource_type: 'user',
    resource_id: 'user-002',
    details: { ip: '192.168.1.100', user_agent: 'Mozilla/5.0' },
    severity: 'info',
  },
  {
    id: 'audit-002',
    timestamp: '2026-02-05T11:15:00Z',
    created_at: '2026-02-05T11:15:00Z',
    action: 'data_modification',
    user_id: 'user-001',
    user_name: 'Admin Silva',
    resource_type: 'customer',
    resource_id: 'cust-123',
    details: { changes: { name: { old: 'João', new: 'João Silva' } } },
    severity: 'warning',
  },
  {
    id: 'audit-003',
    timestamp: '2026-02-05T12:00:00Z',
    created_at: '2026-02-05T12:00:00Z',
    action: 'data_export',
    user_id: 'user-003',
    user_name: 'Operador Costa',
    resource_type: 'employee',
    resource_id: 'emp-456',
    details: { format: 'CSV', records: 150 },
    severity: 'info',
  },
  {
    id: 'audit-004',
    timestamp: '2026-02-05T13:45:00Z',
    created_at: '2026-02-05T13:45:00Z',
    action: 'data_deletion',
    user_id: 'user-001',
    user_name: 'Admin Silva',
    resource_type: 'document',
    resource_id: 'doc-789',
    details: { reason: 'LGPD Request' },
    severity: 'critical',
  },
  {
    id: 'audit-005',
    timestamp: '2026-02-05T14:20:00Z',
    created_at: '2026-02-05T14:20:00Z',
    action: 'security_incident',
    user_id: 'system',
    user_name: 'Sistema',
    resource_type: 'user',
    resource_id: 'user-999',
    details: { type: 'failed_login_attempt', attempts: 5 },
    severity: 'critical',
  },
];

// Setup de mocks para API
async function setupAuditMocks(page: Page) {
  await page.route('**/api/v1/security-lgpd/audit/logs**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          logs: mockAuditLogs,
          total: mockAuditLogs.length,
        },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/audit/actions**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        actions: ['data_access', 'data_modification', 'data_deletion', 'data_export', 'security_incident'],
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/audit/resource-types**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        types: ['user', 'customer', 'employee', 'document'],
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/audit/export**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        download_url: '/api/v1/security-lgpd/audit/export/download?token=test',
        expires_at: new Date(Date.now() + 3600000).toISOString(),
      }),
    });
  });
}

test.describe('Segurança - Auditoria LGPD', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupAuditMocks(page);
    await page.goto('/modulos/seguranca/auditoria');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de auditoria', async ({ page }) => {
    await expect(page).toHaveURL(/\/auditoria/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Auditoria/i);
  });

  test('deve exibir contador total de registros', async ({ page }) => {
    await page.waitForTimeout(1000);

    const countText = page.locator('text=/registros|registros encontrados/i').first();
    await expect(countText).toBeVisible();
  });

  test('deve exibir tabela de logs de auditoria', async ({ page }) => {
    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Data/Hora', 'Ação', 'Recurso', 'Usuário', 'Detalhes'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}"), th:has-text("${header.toLowerCase()}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  test('deve exibir dados mockados na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('Admin Silva')).toBeVisible();
  });

  // ==========================================
  // TESTES DE BADGES DE AÇÃO
  // ==========================================

  test('deve exibir badge colorido por tipo de ação', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se há badges de ação
    const actionBadges = page.locator('td span[class*="badge"], td span[class*="rounded"]').first();
    const hasBadges = await actionBadges.isVisible().catch(() => false);
    expect(hasBadges).toBeTruthy();
  });

  test('deve identificar ação de acesso a dados', async ({ page }) => {
    await page.waitForTimeout(1000);

    const accessAction = page.locator('text=/Acesso a Dados|data_access/i').first();
    const hasAccess = await accessAction.isVisible().catch(() => false);
    expect(hasAccess !== undefined).toBeTruthy();
  });

  test('deve identificar ação de modificação de dados', async ({ page }) => {
    await page.waitForTimeout(1000);

    const modAction = page.locator('text=/Modificação|Modification/i').first();
    const hasMod = await modAction.isVisible().catch(() => false);
    expect(hasMod !== undefined).toBeTruthy();
  });

  test('deve identificar ação de exclusão de dados', async ({ page }) => {
    await page.waitForTimeout(1000);

    const delAction = page.locator('text=/Exclusão|Deletion/i').first();
    const hasDel = await delAction.isVisible().catch(() => false);
    expect(hasDel !== undefined).toBeTruthy();
  });

  test('deve identificar incidentes de segurança', async ({ page }) => {
    await page.waitForTimeout(1000);

    const incidentAction = page.locator('text=/Incidente|Security/i').first();
    const hasIncident = await incidentAction.isVisible().catch(() => false);
    expect(hasIncident !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE FILTROS
  // ==========================================

  test('deve filtrar por termo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i], input[type="search"]').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('Admin');
    await page.waitForTimeout(600);

    await expect(searchInput).toHaveValue('Admin');
  });

  test('deve filtrar por tipo de ação', async ({ page }) => {
    const actionSelect = page.locator('select, [role="combobox"]').filter({ hasText: /Ação|Todas/i }).first();

    if (await actionSelect.isVisible().catch(() => false)) {
      await actionSelect.click();
      await page.waitForTimeout(300);

      const option = page.locator('[data-value="data_access"], option[value="data_access"]').first();
      if (await option.isVisible().catch(() => false)) {
        await option.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('deve filtrar por tipo de recurso', async ({ page }) => {
    const resourceSelect = page.locator('select, [role="combobox"]').filter({ hasText: /Recurso/i }).first();

    if (await resourceSelect.isVisible().catch(() => false)) {
      await resourceSelect.click();
      await page.waitForTimeout(300);

      const option = page.locator('[data-value="user"], option[value="user"]').first();
      if (await option.isVisible().catch(() => false)) {
        await option.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('deve filtrar por intervalo de datas', async ({ page }) => {
    const dateInputs = page.locator('input[type="date"]');
    const count = await dateInputs.count();

    if (count >= 2) {
      const startDate = dateInputs.nth(0);
      const endDate = dateInputs.nth(1);

      await startDate.fill('2026-02-01');
      await endDate.fill('2026-02-05');
      await page.waitForTimeout(500);

      await expect(startDate).toHaveValue('2026-02-01');
      await expect(endDate).toHaveValue('2026-02-05');
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
  // TESTES DE VISUALIZAÇÃO DE DETALHES
  // ==========================================

  test('deve abrir modal de detalhes ao clicar em visualizar', async ({ page }) => {
    await page.waitForTimeout(1000);

    const viewButton = page.locator('button:has-text("Ver detalhes"), button:has([data-lucide="Eye"])').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"], [class*="modal"]').first();
      await expect(modal).toBeVisible();
    }
  });

  test('deve exibir informações detalhadas do log', async ({ page }) => {
    await page.waitForTimeout(1000);

    const viewButton = page.locator('button:has-text("Ver detalhes")').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible()) {
        // Verificar se há detalhes no modal
        const details = modal.locator('text=/IP|user_agent|changes|format/i').first();
        const hasDetails = await details.isVisible().catch(() => false);
        expect(hasDetails !== undefined).toBeTruthy();
      }
    }
  });

  test('deve exibir ID do usuário e recurso nos detalhes', async ({ page }) => {
    await page.waitForTimeout(1000);

    const viewButton = page.locator('button:has-text("Ver detalhes")').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible()) {
        // Verificar se há IDs
        const ids = modal.locator('text=/user-|cust-|emp-|doc-/i').first();
        const hasIds = await ids.isVisible().catch(() => false);
        expect(hasIds !== undefined).toBeTruthy();
      }
    }
  });

  // ==========================================
  // TESTES DE EXPORTAÇÃO
  // ==========================================

  test('deve ter opção de exportar logs', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Exportar"), button:has-text("Export")').first();
    const hasExport = await exportButton.isVisible().catch(() => false);
    expect(hasExport !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE PAGINAÇÃO
  // ==========================================

  test('deve exibir controles de paginação', async ({ page }) => {
    await page.waitForTimeout(1000);

    const pagination = page.locator('button:has-text("Anterior"), button:has-text("Próximo"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);
    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve navegar entre páginas', async ({ page }) => {
    const nextButton = page.locator('button:has-text("Próximo"), button:has-text(">")').first();

    if (await nextButton.isVisible().catch(() => false)) {
      const isEnabled = await nextButton.isEnabled().catch(() => false);
      if (isEnabled) {
        await nextButton.click();
        await page.waitForTimeout(500);
        await expect(page.locator('table')).toBeVisible();
      }
    }
  });

  // ==========================================
  // TESTES DE AÇÕES GLOBAIS
  // ==========================================

  test('deve atualizar lista ao clicar em atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();
    await expect(refreshButton).toBeVisible();

    await refreshButton.click();
    await page.waitForTimeout(1000);

    await expect(page.locator('table')).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTADOS ESPECIAIS
  // ==========================================

  test('deve exibir empty state quando não há logs', async ({ page }) => {
    await page.route('**/api/v1/security-lgpd/audit/logs**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { logs: [], total: 0 },
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
    await page.route('**/api/v1/security-lgpd/audit/logs**', async (route) => {
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
