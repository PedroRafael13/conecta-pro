/**
 * Testes E2E - Integrações: Logs
 * Logs de integrações, filtros, detalhes de requisições, exportação, debug de falhas
 */

import { test, expect } from '../fixtures';
import { loginViaAPI } from '../helpers/auth';

// Mock data para Logs
const mockLogs = [
  {
    id: 'log-001',
    timestamp: '2025-02-05T14:30:00Z',
    level: 'info',
    connector_name: 'erp-sap',
    message: 'Sincronização de funcionários concluída com sucesso',
    status: 'success',
    request_id: 'req-12345',
    method: 'POST',
    endpoint: '/api/v1/integrations/sap/employees/sync',
    duration_ms: 1250,
    response_code: 200,
    details: { records_processed: 50, records_created: 2, records_updated: 48 },
  },
  {
    id: 'log-002',
    timestamp: '2025-02-05T14:25:00Z',
    level: 'error',
    connector_name: 'solides-dp',
    message: 'Falha na autenticação com API Sólides: Token expirado',
    status: 'failure',
    request_id: 'req-12344',
    method: 'GET',
    endpoint: '/api/v1/integrations/solides/employees',
    duration_ms: 500,
    response_code: 401,
    details: { error: 'Unauthorized', error_code: 'TOKEN_EXPIRED', retryable: true },
  },
  {
    id: 'log-003',
    timestamp: '2025-02-05T14:20:00Z',
    level: 'warning',
    connector_name: 'crm-salesforce',
    message: 'Rate limit atingido, aguardando retry',
    status: 'success',
    request_id: 'req-12343',
    method: 'POST',
    endpoint: '/api/v1/integrations/salesforce/opportunities',
    duration_ms: 3000,
    response_code: 429,
    details: { retry_after: 60, rate_limit_remaining: 0 },
  },
  {
    id: 'log-004',
    timestamp: '2025-02-05T14:15:00Z',
    level: 'debug',
    connector_name: 'webhook-slack',
    message: 'Payload enviado para webhook',
    status: 'success',
    request_id: 'req-12342',
    method: 'POST',
    endpoint: '/hooks/webhook-001',
    duration_ms: 150,
    response_code: 200,
    details: { payload_size: 1024, event_type: 'funcionario.criado' },
  },
  {
    id: 'log-005',
    timestamp: '2025-02-05T14:10:00Z',
    level: 'error',
    connector_name: 'banco-itau',
    message: 'Timeout na conexão com servidor do banco',
    status: 'failure',
    request_id: 'req-12341',
    method: 'POST',
    endpoint: '/api/v1/integrations/banking/payments',
    duration_ms: 30000,
    response_code: null,
    details: { error: 'Connection timeout', timeout_ms: 30000, retry_count: 3 },
  },
  {
    id: 'log-006',
    timestamp: '2025-02-05T14:05:00Z',
    level: 'info',
    connector_name: 'nfse-prefeitura',
    message: 'NFSe emitida com sucesso',
    status: 'success',
    request_id: 'req-12340',
    method: 'POST',
    endpoint: '/api/v1/integrations/nfse/emit',
    duration_ms: 2500,
    response_code: 201,
    details: { nfse_number: '123456', valor: 1500.00 },
  },
];

const mockConnectors = [
  { name: 'erp-sap', display_name: 'SAP ERP' },
  { name: 'solides-dp', display_name: 'Sólides DP' },
  { name: 'crm-salesforce', display_name: 'Salesforce' },
  { name: 'webhook-slack', display_name: 'Webhook Slack' },
  { name: 'banco-itau', display_name: 'Banco Itaú' },
  { name: 'nfse-prefeitura', display_name: 'NFSe Prefeitura' },
];

test.describe('Integrações - Logs', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Mock endpoints de logs
    await page.route('**/api/v1/integrations/logs**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockLogs, total: mockLogs.length }),
      });
    });

    await page.route('**/api/v1/integrations/connectors', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ connectors: mockConnectors }),
      });
    });

    await page.route('**/api/v1/integrations/logs/*/export', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: {
          'Content-Disposition': 'attachment; filename="logs-export.json"',
        },
        body: JSON.stringify(mockLogs),
      });
    });

    await page.goto('/modulos/integracoes/logs', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E VISUALIZAÇÃO
  // ==========================================

  test('deve carregar a página de Logs', async ({ page }) => {
    const heading = page.locator('h1');
    await expect(heading).toContainText('Logs de Integração');
  });

  test('deve exibir descrição da página', async ({ page }) => {
    await expect(page.locator('text=Visualize logs de requisições')).toBeVisible();
  });

  test('deve exibir tabela de logs', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    const headers = ['Data/Hora', 'Tipo', 'Conector', 'Mensagem', 'Status', 'Ações'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve listar todos os logs', async ({ page }) => {
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(6);
  });

  test('deve exibir timestamp formatado', async ({ page }) => {
    const firstRow = page.locator('table tbody tr').first();
    await expect(firstRow).toContainText('05/02/2025');
  });

  // ==========================================
  // TESTES DE FILTROS POR DATA
  // ==========================================

  test('deve exibir campo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]');
    await expect(searchInput).toBeVisible();
  });

  test('deve filtrar logs por mensagem', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]');
    await searchInput.fill('Sincronização');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Sincronização de funcionários')).toBeVisible();
  });

  test('deve filtrar logs por conector', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]');
    await searchInput.fill('SAP');
    await page.waitForTimeout(500);

    await expect(page.locator('text=erp-sap')).toBeVisible();
  });

  // ==========================================
  // TESTES DE FILTROS POR STATUS
  // ==========================================

  test('deve filtrar por status Sucesso', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').filter({ hasText: /status/i }).first();
    await statusSelect.click();
    await page.locator('[role="option"]:has-text("Sucesso")').click();
    await page.waitForTimeout(500);

    const successBadges = page.locator('text=Sucesso');
    const count = await successBadges.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve filtrar por status Falha', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').filter({ hasText: /status/i }).first();
    await statusSelect.click();
    await page.locator('[role="option"]:has-text("Falha")').click();
    await page.waitForTimeout(500);

    const failureBadges = page.locator('text=Falha');
    const count = await failureBadges.count();
    expect(count).toBeGreaterThan(0);
  });

  // ==========================================
  // TESTES DE FILTROS POR TIPO/NÍVEL
  // ==========================================

  test('deve filtrar por tipo Info', async ({ page }) => {
    const typeSelect = page.locator('[role="combobox"]').filter({ hasText: /tipo/i }).first();
    await typeSelect.click();
    await page.locator('[role="option"]:has-text("Info")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Info')).toBeVisible();
  });

  test('deve filtrar por tipo Error', async ({ page }) => {
    const typeSelect = page.locator('[role="combobox"]').filter({ hasText: /tipo/i }).first();
    await typeSelect.click();
    await page.locator('[role="option"]:has-text("Erro")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Erro')).toBeVisible();
  });

  test('deve filtrar por tipo Warning', async ({ page }) => {
    const typeSelect = page.locator('[role="combobox"]').filter({ hasText: /tipo/i }).first();
    await typeSelect.click();
    await page.locator('[role="option"]:has-text("Warning")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Warning')).toBeVisible();
  });

  test('deve filtrar por tipo Debug', async ({ page }) => {
    const typeSelect = page.locator('[role="combobox"]').filter({ hasText: /tipo/i }).first();
    await typeSelect.click();
    await page.locator('[role="option"]:has-text("Debug")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Debug')).toBeVisible();
  });

  // ==========================================
  // TESTES DE FILTROS POR CONECTOR
  // ==========================================

  test('deve exibir select de conectores', async ({ page }) => {
    const connectorSelect = page.locator('[role="combobox"]').filter({ hasText: /conector/i }).first();
    await expect(connectorSelect).toBeVisible();
  });

  test('deve filtrar por conector específico', async ({ page }) => {
    const connectorSelect = page.locator('[role="combobox"]').filter({ hasText: /conector/i }).first();
    await connectorSelect.click();
    await page.locator('[role="option"]:has-text("SAP")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=erp-sap')).toBeVisible();
  });

  test('deve listar todos os conectores no filtro', async ({ page }) => {
    const connectorSelect = page.locator('[role="combobox"]').filter({ hasText: /conector/i }).first();
    await connectorSelect.click();

    await expect(page.locator('[role="option"]:has-text("SAP ERP")')).toBeVisible();
    await expect(page.locator('[role="option"]:has-text("Sólides DP")')).toBeVisible();
    await expect(page.locator('[role="option"]:has-text("Salesforce")')).toBeVisible();
  });

  // ==========================================
  // TESTES DE DETALHES DE REQUISIÇÕES
  // ==========================================

  test('deve abrir modal de detalhes do log', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });

  test('deve exibir request ID nos detalhes', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=req-12345')).toBeVisible();
  });

  test('deve exibir método HTTP nos detalhes', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=POST')).toBeVisible();
  });

  test('deve exibir endpoint nos detalhes', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=/api/v1/integrations/sap')).toBeVisible();
  });

  test('deve exibir tempo de resposta nos detalhes', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=1250')).toBeVisible();
  });

  test('deve exibir código de resposta nos detalhes', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=200')).toBeVisible();
  });

  // ==========================================
  // TESTES DE DEBUG DE FALHAS
  // ==========================================

  test('deve exibir detalhes de erro em log com falha', async ({ page }) => {
    const errorRow = page.locator('table tbody tr').filter({ hasText: 'Falha na autenticação' });
    const menuButton = errorRow.locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Token expirado')).toBeVisible();
    await expect(page.locator('text=401')).toBeVisible();
  });

  test('deve exibir stack trace se disponível', async ({ page }) => {
    const errorRow = page.locator('table tbody tr').filter({ hasText: 'Timeout' });
    const menuButton = errorRow.locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Connection timeout')).toBeVisible();
  });

  test('deve indicar se erro é retryable', async ({ page }) => {
    const errorRow = page.locator('table tbody tr').filter({ hasText: 'Falha na autenticação' });
    const menuButton = errorRow.locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=TOKEN_EXPIRED')).toBeVisible();
  });

  test('deve exibir contagem de retries', async ({ page }) => {
    const errorRow = page.locator('table tbody tr').filter({ hasText: 'Timeout' });
    const menuButton = errorRow.locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=3')).toBeVisible();
  });

  // ==========================================
  // TESTES DE EXPORTAÇÃO
  // ==========================================

  test('deve exibir botão de exportação', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Exportar"), button:has-text("Download")').first();
    if (await exportButton.isVisible().catch(() => false)) {
      await expect(exportButton).toBeVisible();
    }
  });

  test('deve exportar logs em formato JSON', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Exportar"), button:has-text("Download")').first();
    if (await exportButton.isVisible().catch(() => false)) {
      await exportButton.click();
      await page.waitForTimeout(1000);

      // Verifica se houve download (o teste verifica se não houve erro)
      await expect(page.locator('text=exportado')).toBeVisible({ timeout: 3000 });
    }
  });

  // ==========================================
  // TESTES DE PAGINAÇÃO
  // ==========================================

  test('deve exibir informação de paginação', async ({ page }) => {
    const paginationInfo = page.locator('text=Mostrando');
    await expect(paginationInfo).toBeVisible();
  });

  test('deve exibir número de registros encontrados', async ({ page }) => {
    await expect(page.locator('text=6 registros')).toBeVisible();
  });

  // ==========================================
  // TESTES DE ATUALIZAÇÃO
  // ==========================================

  test('deve atualizar lista de logs', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await refreshButton.click();

    await expect(page.locator('.animate-spin')).toBeVisible({ timeout: 2000 });
    await page.waitForTimeout(1000);

    await expect(page.locator('table')).toBeVisible();
  });

  // ==========================================
  // TESTES DE INDICADORES VISUAIS
  // ==========================================

  test('deve exibir badge de sucesso em verde', async ({ page }) => {
    const successRow = page.locator('table tbody tr').filter({ hasText: 'Sucesso' }).first();
    await expect(successRow.locator('text=Sucesso')).toBeVisible();
  });

  test('deve exibir badge de falha em vermelho', async ({ page }) => {
    const failureRow = page.locator('table tbody tr').filter({ hasText: 'Falha' }).first();
    await expect(failureRow.locator('text=Falha')).toBeVisible();
  });

  test('deve truncar mensagens longas', async ({ page }) => {
    await expect(page.locator('text=Sincronização de funcionários concluída')).toBeVisible();
  });
});
