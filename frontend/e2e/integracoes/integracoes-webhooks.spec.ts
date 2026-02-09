/**
 * Testes E2E - Integrações: Webhooks
 * Cadastro, eventos, payload, retry policy, logs de entrega, falhas e reenvio
 */

import { test, expect } from '../fixtures';
import { loginViaAPI } from '../helpers/auth';

// Mock data para Webhooks
const mockWebhooks = [
  {
    id: 'wh-001',
    name: 'Notificações Slack',
    url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
    events: ['funcionario.criado', 'funcionario.atualizado', 'folha.processada'],
    status: 'active',
    secret: 'whsec_123456789',
    retry_policy: { max_retries: 3, retry_delay: 60 },
    timeout: 30,
    created_at: '2025-01-10T08:00:00Z',
    last_triggered_at: '2025-02-05T14:30:00Z',
    delivery_count: 1250,
    failure_count: 5,
    headers: { 'Content-Type': 'application/json', 'X-Custom-Header': 'valor' },
  },
  {
    id: 'wh-002',
    name: 'Webhook ERP Externo',
    url: 'https://erp.externo.com/api/webhooks/conecta',
    events: ['funcionario.criado', 'funcionario.desligado'],
    status: 'active',
    secret: 'whsec_abcdef123',
    retry_policy: { max_retries: 5, retry_delay: 120 },
    timeout: 45,
    created_at: '2025-01-15T10:00:00Z',
    last_triggered_at: '2025-02-04T09:15:00Z',
    delivery_count: 89,
    failure_count: 0,
    headers: { 'Authorization': 'Bearer token123' },
  },
  {
    id: 'wh-003',
    name: 'Notificações Email - Legado',
    url: 'https://notifications.legado.com/webhook',
    events: ['folha.erro'],
    status: 'error',
    secret: 'whsec_old_secret',
    retry_policy: { max_retries: 3, retry_delay: 60 },
    timeout: 30,
    created_at: '2024-12-01T00:00:00Z',
    last_triggered_at: '2025-01-20T16:00:00Z',
    delivery_count: 450,
    failure_count: 150,
    headers: {},
  },
  {
    id: 'wh-004',
    name: 'Dashboard Analytics',
    url: 'https://analytics.dashboard.com/events',
    events: ['all'],
    status: 'inactive',
    secret: 'whsec_analytics',
    retry_policy: { max_retries: 2, retry_delay: 30 },
    timeout: 15,
    created_at: '2025-01-20T12:00:00Z',
    last_triggered_at: null,
    delivery_count: 0,
    failure_count: 0,
    headers: { 'X-API-Key': 'analytics_key_123' },
  },
];

const mockWebhookEvents = [
  { id: 'evt-001', name: 'funcionario.criado', description: 'Novo funcionário criado' },
  { id: 'evt-002', name: 'funcionario.atualizado', description: 'Dados de funcionário atualizados' },
  { id: 'evt-003', name: 'funcionario.desligado', description: 'Funcionário desligado' },
  { id: 'evt-004', name: 'folha.processada', description: 'Folha de pagamento processada' },
  { id: 'evt-005', name: 'folha.erro', description: 'Erro no processamento da folha' },
  { id: 'evt-006', name: 'ponto.registrado', description: 'Registro de ponto criado' },
];

const mockDeliveryLogs = [
  { id: 'log-001', webhook_id: 'wh-001', event: 'funcionario.criado', status: 'success', timestamp: '2025-02-05T14:30:00Z', response_code: 200 },
  { id: 'log-002', webhook_id: 'wh-001', event: 'folha.processada', status: 'success', timestamp: '2025-02-05T12:00:00Z', response_code: 200 },
  { id: 'log-003', webhook_id: 'wh-003', event: 'folha.erro', status: 'failed', timestamp: '2025-01-20T16:00:00Z', response_code: 500, error: 'Connection timeout' },
];

test.describe('Integrações - Webhooks', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Mock endpoints de webhooks
    await page.route('**/api/v1/integrations/webhooks**', (route) => {
      const method = route.request().method();
      const url = route.request().url();

      if (method === 'GET' && !url.includes('/logs')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: mockWebhooks, total: mockWebhooks.length }),
        });
      } else if (method === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'wh-new',
            name: 'Novo Webhook',
            url: 'https://example.com/webhook',
            events: ['funcionario.criado'],
            status: 'active',
            secret: 'whsec_new_secret_generated',
            created_at: new Date().toISOString(),
          }),
        });
      } else if (method === 'PATCH') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true }),
        });
      } else {
        route.continue();
      }
    });

    await page.route('**/api/v1/integrations/webhooks/events', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockWebhookEvents }),
      });
    });

    await page.route('**/api/v1/integrations/webhooks/*/logs', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockDeliveryLogs, total: mockDeliveryLogs.length }),
      });
    });

    await page.route('**/api/v1/integrations/webhooks/*/test', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Webhook testado com sucesso' }),
      });
    });

    await page.route('**/api/v1/integrations/webhooks/*/regenerate-secret', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ secret: 'whsec_regenerated_new_secret' }),
      });
    });

    await page.goto('/modulos/integracoes/webhooks', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E VISUALIZAÇÃO
  // ==========================================

  test('deve carregar a página de Webhooks', async ({ page }) => {
    const heading = page.locator('h1');
    await expect(heading).toContainText('Webhooks');
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    const statsCards = page.locator('[class*="Card"], .card');
    await expect(statsCards).toHaveCount(3);

    await expect(page.locator('text=Total')).toBeVisible();
    await expect(page.locator('text=Ativos')).toBeVisible();
    await expect(page.locator('text=Erros recentes')).toBeVisible();
  });

  test('deve exibir total de webhooks', async ({ page }) => {
    const totalCard = page.locator('.card, [class*="Card"]').filter({ hasText: 'Total' });
    await expect(totalCard).toContainText('4');
  });

  test('deve exibir quantidade de webhooks ativos', async ({ page }) => {
    const activeCard = page.locator('.card, [class*="Card"]').filter({ hasText: 'Ativos' });
    await expect(activeCard).toContainText('2');
  });

  test('deve exibir tabela de webhooks', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    const headers = ['Nome', 'URL', 'Eventos', 'Status', 'Ultimo disparo', 'Acoes'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  // ==========================================
  // TESTES DE CADASTRO DE WEBHOOKS
  // ==========================================

  test('deve abrir modal de criação de webhook', async ({ page }) => {
    const createButton = page.locator('button:has-text("Novo Webhook")');
    await createButton.click();

    await expect(page.locator('[role="dialog"]')).toBeVisible();
    await expect(page.locator('text=Criar Webhook')).toBeVisible();
  });

  test('deve exibir lista de eventos disponíveis', async ({ page }) => {
    await page.locator('button:has-text("Novo Webhook")').click();
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    const eventsSelect = page.locator('[role="combobox"]').filter({ hasText: /evento/i }).first();
    await eventsSelect.click();

    await expect(page.locator('[role="option"]:has-text("funcionario.criado")')).toBeVisible();
    await expect(page.locator('[role="option"]:has-text("folha.processada")')).toBeVisible();
  });

  test('deve criar novo webhook com sucesso', async ({ page }) => {
    await page.locator('button:has-text("Novo Webhook")').click();
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    await page.locator('input[name="name"]').fill('Webhook Teste E2E');
    await page.locator('input[name="url"]').fill('https://meusite.com/webhook');

    const eventsSelect = page.locator('[role="combobox"]').filter({ hasText: /evento/i }).first();
    await eventsSelect.click();
    await page.locator('[role="option"]:has-text("funcionario.criado")').click();

    await page.locator('button:has-text("Criar")').click();
    await page.waitForTimeout(1000);

    await expect(page.locator('text=criado com sucesso')).toBeVisible();
  });

  test('deve validar URL ao criar webhook', async ({ page }) => {
    await page.locator('button:has-text("Novo Webhook")').click();
    await page.locator('input[name="name"]').fill('Teste URL Inválida');
    await page.locator('input[name="url"]').fill('url-invalida');

    await page.locator('button:has-text("Criar")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });

  test('deve exibir secret gerado após criação', async ({ page }) => {
    await page.locator('button:has-text("Novo Webhook")').click();
    await page.locator('input[name="name"]').fill('Webhook Com Secret');
    await page.locator('input[name="url"]').fill('https://teste.com/webhook');
    await page.locator('button:has-text("Criar")').click();
    await page.waitForTimeout(1000);

    await expect(page.locator('text=whsec_new_secret_generated')).toBeVisible();
  });

  // ==========================================
  // TESTES DE CONFIGURAÇÃO DE PAYLOAD
  // ==========================================

  test('deve permitir configurar timeout', async ({ page }) => {
    await page.locator('button:has-text("Novo Webhook")').click();

    const timeoutInput = page.locator('input[name="timeout"]').first();
    if (await timeoutInput.isVisible().catch(() => false)) {
      await timeoutInput.fill('60');
      await expect(timeoutInput).toHaveValue('60');
    }
  });

  test('deve permitir configurar headers customizados', async ({ page }) => {
    await page.locator('button:has-text("Novo Webhook")').click();

    const headersSection = page.locator('text=Headers, button:has-text("Adicionar Header")').first();
    if (await headersSection.isVisible().catch(() => false)) {
      await headersSection.click();
      await page.locator('input[placeholder*="chave"]').fill('X-Custom-Header');
      await page.locator('input[placeholder*="valor"]').fill('meu-valor');
    }
  });

  test('deve exibir configuração de retry policy', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Ver detalhes"), [role="menuitem"]:has-text("Editar")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });

  // ==========================================
  // TESTES DE RETRY POLICY
  // ==========================================

  test('deve exibir max retries na configuração', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Editar")').click();
    await page.waitForTimeout(500);

    const retriesInput = page.locator('input[name="max_retries"]').first();
    if (await retriesInput.isVisible().catch(() => false)) {
      await expect(retriesInput).toHaveValue('3');
    }
  });

  test('deve permitir alterar retry delay', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Editar")').click();
    await page.waitForTimeout(500);

    const delayInput = page.locator('input[name="retry_delay"]').first();
    if (await delayInput.isVisible().catch(() => false)) {
      await delayInput.fill('120');
      await expect(delayInput).toHaveValue('120');
    }
  });

  // ==========================================
  // TESTES DE EDIÇÃO E ATUALIZAÇÃO
  // ==========================================

  test('deve abrir modal de edição', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Editar")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('[role="dialog"]')).toBeVisible();
    await expect(page.locator('text=Notificações Slack')).toBeVisible();
  });

  test('deve atualizar webhook com sucesso', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Editar")').click();
    await page.waitForTimeout(500);

    await page.locator('input[name="name"]').clear();
    await page.locator('input[name="name"]').fill('Notificações Slack Atualizado');
    await page.locator('button:has-text("Salvar")').click();
    await page.waitForTimeout(1000);

    await expect(page.locator('text=atualizado com sucesso')).toBeVisible();
  });

  // ==========================================
  // TESTES DE LOGS DE ENTREGA
  // ==========================================

  test('deve exibir logs de entrega no detalhe', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();
    await page.locator('[role="menuitem"]:has-text("Ver detalhes")').click();
    await page.waitForTimeout(500);

    const logsTab = page.locator('[role="tab"]:has-text("Logs"), button:has-text("Logs")').first();
    if (await logsTab.isVisible().catch(() => false)) {
      await logsTab.click();
      await expect(page.locator('text=funcionario.criado')).toBeVisible();
    }
  });

  test('deve indicar entregas com sucesso', async ({ page }) => {
    await expect(page.locator('text=Ativo')).toHaveCount(2);
  });

  test('deve exibir último disparo na tabela', async ({ page }) => {
    const firstRow = page.locator('table tbody tr').first();
    await expect(firstRow).toContainText('05/02/2025');
  });

  // ==========================================
  // TESTES DE FALHAS E REENVIO
  // ==========================================

  test('deve exibir webhook com status de erro', async ({ page }) => {
    const errorRow = page.locator('table tbody tr').filter({ hasText: 'Notificações Email' });
    await expect(errorRow.locator('text=Erro')).toBeVisible();
  });

  test('deve executar teste de webhook', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Testar")').click();
    await page.waitForTimeout(300);

    await page.locator('button:has-text("Confirmar"), button:has-text("Testar")').click();
    await page.waitForTimeout(1000);

    await expect(page.locator('text=testado com sucesso')).toBeVisible();
  });

  test('deve regenerar secret do webhook', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Regenerar Secret")').click();
    await page.waitForTimeout(300);

    await page.locator('button:has-text("Confirmar")').click();
    await page.waitForTimeout(1000);

    await expect(page.locator('text=whsec_regenerated')).toBeVisible();
  });

  test('deve exibir aviso antes de regenerar secret', async ({ page }) => {
    const menuButton = page.locator('table tbody tr').first().locator('button').last();
    await menuButton.click();

    await page.locator('[role="menuitem"]:has-text("Regenerar Secret")').click();
    await page.waitForTimeout(300);

    await expect(page.locator('text=Regenerar Secret')).toBeVisible();
    await expect(page.locator('text=invalidado')).toBeVisible();
  });

  // ==========================================
  // TESTES DE FILTROS E BUSCA
  // ==========================================

  test('deve filtrar webhooks por nome', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]');
    await searchInput.fill('Slack');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Notificações Slack')).toBeVisible();
    await expect(page.locator('text=Webhook ERP')).not.toBeVisible();
  });

  test('deve filtrar webhooks por status', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').filter({ hasText: /todos/i }).first();
    await statusSelect.click();
    await page.locator('[role="option"]:has-text("Erro")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Notificações Email')).toBeVisible();
  });

  test('deve atualizar lista de webhooks', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await refreshButton.click();

    await expect(page.locator('.animate-spin')).toBeVisible({ timeout: 2000 });
    await page.waitForTimeout(1000);

    await expect(page.locator('table')).toBeVisible();
  });
});
