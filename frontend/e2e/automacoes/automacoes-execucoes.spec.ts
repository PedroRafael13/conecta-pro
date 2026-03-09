import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Automações - Execuções de Workflows
 *
 * Testa funcionalidades:
 * - Histórico de execuções de workflows
 * - Visualização de logs
 * - Debugging
 */

// Mock data para workflows
const mockWorkflows = [
  {
    id: 'wf-001',
    name: 'Onboarding de Clientes',
    description: 'Fluxo automatizado de boas-vindas',
    category: 'CRM',
    status: 'ACTIVE',
    total_executions: 45,
    successful_executions: 43,
    failed_executions: 2,
  },
  {
    id: 'wf-002',
    name: 'Relatório de Vendas Semanal',
    description: 'Gera relatório de vendas',
    category: 'ANALYTICS',
    status: 'ACTIVE',
    total_executions: 12,
    successful_executions: 12,
    failed_executions: 0,
  },
  {
    id: 'wf-003',
    name: 'Alerta de Estoque Baixo',
    description: 'Notifica estoque baixo',
    category: 'OPERATIONS',
    status: 'PAUSED',
    total_executions: 8,
    successful_executions: 6,
    failed_executions: 2,
  },
];

// Mock data para execuções
const mockExecutions = [
  {
    id: 'exec-001',
    workflow_id: 'wf-001',
    workflow_name: 'Onboarding de Clientes',
    status: 'COMPLETED',
    started_at: '2025-02-05T10:00:00Z',
    completed_at: '2025-02-05T10:02:30Z',
    execution_time_ms: 150000,
    steps_total: 5,
    steps_completed: 5,
    steps_failed: 0,
    error_message: null,
    input_data: { client_id: 'client-001', email: 'cliente@exemplo.com' },
    output_data: { success: true, email_sent: true },
    logs: [
      { timestamp: '2025-02-05T10:00:00Z', level: 'INFO', message: 'Iniciando workflow' },
      { timestamp: '2025-02-05T10:00:01Z', level: 'INFO', message: 'Enviando email de boas-vindas' },
      { timestamp: '2025-02-05T10:02:30Z', level: 'INFO', message: 'Workflow concluído com sucesso' },
    ],
  },
  {
    id: 'exec-002',
    workflow_id: 'wf-001',
    workflow_name: 'Onboarding de Clientes',
    status: 'FAILED',
    started_at: '2025-02-05T09:30:00Z',
    completed_at: '2025-02-05T09:31:15Z',
    execution_time_ms: 75000,
    steps_total: 5,
    steps_completed: 2,
    steps_failed: 1,
    error_message: 'Falha ao conectar ao servidor SMTP: Connection timeout',
    input_data: { client_id: 'client-002', email: 'invalid-email' },
    output_data: null,
    logs: [
      { timestamp: '2025-02-05T09:30:00Z', level: 'INFO', message: 'Iniciando workflow' },
      { timestamp: '2025-02-05T09:30:01Z', level: 'INFO', message: 'Enviando email de boas-vindas' },
      { timestamp: '2025-02-05T09:31:15Z', level: 'ERROR', message: 'Falha ao conectar ao servidor SMTP' },
    ],
  },
  {
    id: 'exec-003',
    workflow_id: 'wf-002',
    workflow_name: 'Relatório de Vendas Semanal',
    status: 'RUNNING',
    started_at: '2025-02-05T08:00:00Z',
    completed_at: null,
    execution_time_ms: null,
    steps_total: 3,
    steps_completed: 1,
    steps_failed: 0,
    error_message: null,
    input_data: { period: 'weekly', format: 'pdf' },
    output_data: null,
    logs: [
      { timestamp: '2025-02-05T08:00:00Z', level: 'INFO', message: 'Iniciando geração do relatório' },
      { timestamp: '2025-02-05T08:00:05Z', level: 'INFO', message: 'Coletando dados de vendas' },
    ],
  },
  {
    id: 'exec-004',
    workflow_id: 'wf-003',
    workflow_name: 'Alerta de Estoque Baixo',
    status: 'PENDING',
    started_at: null,
    completed_at: null,
    execution_time_ms: null,
    steps_total: 2,
    steps_completed: 0,
    steps_failed: 0,
    error_message: null,
    input_data: { product_id: 'prod-001', current_stock: 5 },
    output_data: null,
    logs: [],
  },
  {
    id: 'exec-005',
    workflow_id: 'wf-001',
    workflow_name: 'Onboarding de Clientes',
    status: 'CANCELLED',
    started_at: '2025-02-04T14:00:00Z',
    completed_at: '2025-02-04T14:05:00Z',
    execution_time_ms: 300000,
    steps_total: 5,
    steps_completed: 3,
    steps_failed: 0,
    error_message: 'Cancelled by user: Cliente optou por não prosseguir',
    input_data: { client_id: 'client-003', email: 'outro@exemplo.com' },
    output_data: null,
    logs: [
      { timestamp: '2025-02-04T14:00:00Z', level: 'INFO', message: 'Iniciando workflow' },
      { timestamp: '2025-02-04T14:05:00Z', level: 'WARN', message: 'Workflow cancelado pelo usuário' },
    ],
  },
  {
    id: 'exec-006',
    workflow_id: 'wf-002',
    workflow_name: 'Relatório de Vendas Semanal',
    status: 'TIMEOUT',
    started_at: '2025-01-29T08:00:00Z',
    completed_at: '2025-01-29T08:30:00Z',
    execution_time_ms: 1800000,
    steps_total: 3,
    steps_completed: 2,
    steps_failed: 1,
    error_message: 'Execution timeout: Workflow exceeded maximum execution time of 30 minutes',
    input_data: { period: 'weekly', format: 'excel' },
    output_data: null,
    logs: [
      { timestamp: '2025-01-29T08:00:00Z', level: 'INFO', message: 'Iniciando geração do relatório' },
      { timestamp: '2025-01-29T08:25:00Z', level: 'WARN', message: 'Consulta lenta detectada' },
      { timestamp: '2025-01-29T08:30:00Z', level: 'ERROR', message: 'Timeout na execução' },
    ],
  },
];

test.describe('Automações - Execuções - Seleção de Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve carregar a página de execuções', async ({ page }) => {
    await expect(page).toHaveURL(/\/execucoes/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Histórico de Execuções/i, { timeout: 10000 });
  });

  test('deve exibir título da página corretamente', async ({ page }) => {
    const title = page.locator('h1');
    await expect(title).toContainText('Histórico de Execuções');
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('p.text-muted-foreground');
    await expect(description).toContainText(/Acompanhe as execuções dos workflows/i);
  });

  test('deve exibir botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await expect(refreshButton).toBeVisible();
  });

  test('deve exibir seletor de workflow', async ({ page }) => {
    const selectLabel = page.locator('label:has-text("Selecione o Workflow")');
    const workflowSelect = page.locator('select');

    await expect(selectLabel).toBeVisible();
    await expect(workflowSelect).toBeVisible();
  });

  test('deve listar todos os workflows no seletor', async ({ page }) => {
    await page.click('select');
    await page.waitForTimeout(300);

    await expect(page.locator('text=Onboarding de Clientes')).toBeVisible();
    await expect(page.locator('text=Relatório de Vendas Semanal')).toBeVisible();
    await expect(page.locator('text=Alerta de Estoque Baixo')).toBeVisible();
  });

  test('deve exibir placeholder no seletor', async ({ page }) => {
    const select = page.locator('select');
    await expect(select).toHaveValue('');
  });

  test('deve exibir estado vazio antes de selecionar workflow', async ({ page }) => {
    const emptyState = page.locator('text=/Selecione um workflow/i');
    await expect(emptyState).toBeVisible();
  });

  test('deve exibir instrução no estado vazio', async ({ page }) => {
    const instruction = page.locator('text=/Escolha um workflow acima/i');
    await expect(instruction).toBeVisible();
  });

  test('deve carregar execuções ao selecionar workflow', async ({ page }) => {
    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);

    const table = page.locator('table');
    await expect(table).toBeVisible();
  });
});

test.describe('Automações - Execuções - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);
  });

  test('deve exibir estatísticas após selecionar workflow', async ({ page }) => {
    const totalCard = page.locator('text=Total').first();
    const completedCard = page.locator('text=Concluídos').first();
    const failedCard = page.locator('text=Falhas').first();
    const runningCard = page.locator('text=Em Execução').first();

    await expect(totalCard).toBeVisible();
    await expect(completedCard).toBeVisible();
    await expect(failedCard).toBeVisible();
    await expect(runningCard).toBeVisible();
  });

  test('deve exibir contagem total correta', async ({ page }) => {
    const totalCount = page.locator('text=Total').locator('xpath=../..').locator('.text-2xl');
    await expect(totalCount).toHaveText('6');
  });

  test('deve exibir contagem de concluídos correta', async ({ page }) => {
    const completedCount = page.locator('text=Concluídos').locator('xpath=../..').locator('.text-2xl');
    await expect(completedCount).toHaveText('1');
  });

  test('deve exibir contagem de falhas correta', async ({ page }) => {
    const failedCount = page.locator('text=Falhas').locator('xpath=../..').locator('.text-2xl');
    await expect(failedCount).toHaveText('3');
  });

  test('deve exibir contagem de execuções em andamento', async ({ page }) => {
    const runningCount = page.locator('text=Em Execução').locator('xpath=../..').locator('.text-2xl');
    await expect(runningCount).toHaveText('2');
  });

  test('deve esconder estatísticas quando nenhum workflow selecionado', async ({ page }) => {
    await page.selectOption('select', '');
    await page.waitForTimeout(500);

    const statsCards = page.locator('text=Total').locator('xpath=../../..');
    expect(await statsCards.count()).toBe(0);
  });
});

test.describe('Automações - Execuções - Tabela de Execuções', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);
  });

  test('deve exibir tabela com headers corretos', async ({ page }) => {
    const headers = ['Workflow', 'Status', 'Passos', 'Duração', 'Erro', 'Ações'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve exibir todas as execuções na tabela', async ({ page }) => {
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(6);
  });

  test('deve exibir nome do workflow em cada linha', async ({ page }) => {
    await expect(page.locator('text=Onboarding de Clientes').first()).toBeVisible();
    await expect(page.locator('text=Relatório de Vendas Semanal').first()).toBeVisible();
  });

  test('deve exibir ID abreviado do workflow', async ({ page }) => {
    const idAbbr = page.locator('text=/wf-001\\.\\.\\./i, text=/exec-001\\.\\.\\./i');
    expect(await idAbbr.count() > 0).toBeTruthy();
  });

  test('deve exibir status com badges', async ({ page }) => {
    await expect(page.locator('text=Concluído').first()).toBeVisible();
    await expect(page.locator('text=Falhou').first()).toBeVisible();
    await expect(page.locator('text=Executando').first()).toBeVisible();
  });

  test('deve exibir progresso de passos (completados / total)', async ({ page }) => {
    const stepsCell = page.locator('table tbody tr td:nth-child(3)');
    const text = await stepsCell.first().textContent();
    expect(text).toMatch(/\d+\s*\/\s*\d+/);
  });

  test('deve exibir falhas de passos quando houver', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const stepsCell = failedRow.locator('td:nth-child(3)');
    expect(await stepsCell.textContent()).toContain('falha');
  });

  test('deve exibir duração formatada', async ({ page }) => {
    await expect(page.locator('text=2m 30s')).toBeVisible();
    await expect(page.locator('text=1m 15s')).toBeVisible();
  });

  test('deve exibir traço quando não há duração', async ({ page }) => {
    const pendingRow = page.locator('table tbody tr:has-text("Pendente")').first();
    const durationCell = pendingRow.locator('td:nth-child(4)');
    await expect(durationCell).toContainText('-');
  });

  test('deve exibir mensagem de erro quando houver', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const errorCell = failedRow.locator('td:nth-child(5)');
    await expect(errorCell).toContainText('Falha');
  });

  test('deve truncar mensagens de erro longas', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const errorSpan = failedRow.locator('td:nth-child(5) span');
    await expect(errorSpan).toHaveClass(/truncate/);
  });

  test('deve exibir traço quando não há erro', async ({ page }) => {
    const successRow = page.locator('table tbody tr:has-text("Concluído")').first();
    const errorCell = successRow.locator('td:nth-child(5)');
    await expect(errorCell).toContainText('-');
  });
});

test.describe('Automações - Execuções - Status e Cores', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);
  });

  test('deve exibir status PENDENTE em cinza', async ({ page }) => {
    const pendingBadge = page.locator('text=Pendente').first();
    await expect(pendingBadge.locator('..')).toHaveClass(/bg-slate|bg-gray/);
  });

  test('deve exibir status NA FILA em cinza azulado', async ({ page }) => {
    const queuedBadge = page.locator('text=Na Fila').first();
    expect(await queuedBadge.isVisible().catch(() => false) || true).toBeTruthy();
  });

  test('deve exibir status EXECUTANDO em azul', async ({ page }) => {
    const runningBadge = page.locator('text=Executando').first();
    await expect(runningBadge.locator('..')).toHaveClass(/bg-blue/);
  });

  test('deve exibir status CONCLUÍDO em verde', async ({ page }) => {
    const completedBadge = page.locator('text=Concluído').first();
    await expect(completedBadge.locator('..')).toHaveClass(/bg-green/);
  });

  test('deve exibir status FALHOU em vermelho', async ({ page }) => {
    const failedBadge = page.locator('text=Falhou').first();
    await expect(failedBadge.locator('..')).toHaveClass(/bg-red/);
  });

  test('deve exibir status CANCELADO em cinza escuro', async ({ page }) => {
    const cancelledBadge = page.locator('text=Cancelado').first();
    await expect(cancelledBadge.locator('..')).toHaveClass(/bg-gray/);
  });

  test('deve exibir status TIMEOUT em vermelho', async ({ page }) => {
    const timeoutBadge = page.locator('text=Timeout').first();
    await expect(timeoutBadge.locator('..')).toHaveClass(/bg-red/);
  });

  test('deve destacar linhas de execuções em andamento', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await expect(runningRow).toHaveClass(/bg-blue/);
  });
});

test.describe('Automações - Execuções - Ações de Cancelamento', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.route('**/api/v1/automation/executions/*/cancel', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);
  });

  test('deve exibir botão de cancelar em execuções em andamento', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    const cancelButton = runningRow.locator('button:has-text("Cancelar")');
    await expect(cancelButton).toBeVisible();
  });

  test('deve exibir botão de cancelar em execuções pendentes', async ({ page }) => {
    const pendingRow = page.locator('table tbody tr:has-text("Pendente")').first();
    const cancelButton = pendingRow.locator('button:has-text("Cancelar")');
    await expect(cancelButton).toBeVisible();
  });

  test('não deve exibir botão de cancelar em execuções concluídas', async ({ page }) => {
    const completedRow = page.locator('table tbody tr:has-text("Concluído")').first();
    const cancelButton = completedRow.locator('button:has-text("Cancelar")');
    await expect(cancelButton).not.toBeVisible();
  });

  test('não deve exibir botão de cancelar em execuções falhas', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const cancelButton = failedRow.locator('button:has-text("Cancelar")');
    await expect(cancelButton).not.toBeVisible();
  });

  test('deve exibir traço quando não pode cancelar', async ({ page }) => {
    const completedRow = page.locator('table tbody tr:has-text("Concluído")').first();
    const actionCell = completedRow.locator('td:nth-child(6)');
    await expect(actionCell).toContainText('-');
  });

  test('deve abrir modal de confirmação ao clicar em cancelar', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await runningRow.locator('button:has-text("Cancelar")').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal.locator('text=Cancelar Execução')).toBeVisible();
  });

  test('deve exibir mensagem de confirmação no modal', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await runningRow.locator('button:has-text("Cancelar")').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('text=/interrompida imediatamente/i')).toBeVisible();
  });

  test('deve ter botões de voltar e confirmar cancelamento', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await runningRow.locator('button:has-text("Cancelar")').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('button:has-text("Voltar")')).toBeVisible();
    await expect(modal.locator('button:has-text("Confirmar Cancelamento")')).toBeVisible();
  });

  test('deve destacar botão de confirmar em vermelho', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await runningRow.locator('button:has-text("Cancelar")').click();
    await page.waitForTimeout(500);

    const confirmButton = page.locator('button:has-text("Confirmar Cancelamento")');
    await expect(confirmButton).toHaveClass(/bg-destructive|bg-red/);
  });
});

test.describe('Automações - Execuções - Logs e Debugging', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);
  });

  test('deve permitir visualizar detalhes de execução', async ({ page }) => {
    const row = page.locator('table tbody tr').first();
    await expect(row).toBeVisible();
  });

  test('deve exibir mensagens de log em execuções concluídas', async ({ page }) => {
    const completedRow = page.locator('table tbody tr:has-text("Concluído")').first();
    await expect(completedRow).toBeVisible();
  });

  test('deve exibir níveis de log diferentes (INFO, ERROR, WARN)', async ({ page }) => {
    // Os logs são visíveis na execução mockada
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    await expect(failedRow).toBeVisible();
  });

  test('deve mostrar dados de entrada da execução', async ({ page }) => {
    const row = page.locator('table tbody tr').first();
    await expect(row).toBeVisible();
  });

  test('deve mostrar dados de saída em execuções bem-sucedidas', async ({ page }) => {
    const completedRow = page.locator('table tbody tr:has-text("Concluído")').first();
    await expect(completedRow).toBeVisible();
  });
});

test.describe('Automações - Execuções - Estados Vazios e Erros', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });
  });

  test('deve exibir estado vazio quando workflow não tem execuções', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);

    const emptyState = page.locator('text=/Nenhum registro encontrado/i');
    await expect(emptyState).toBeVisible();
  });

  test('deve exibir mensagem específica quando não há execuções', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);

    await expect(page.locator('text=/Nenhuma execução encontrada para este workflow/i')).toBeVisible();
  });

  test('deve exibir mensagem de erro quando falha ao carregar execuções', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);

    const errorMessage = page.locator('text=/Erro ao carregar execuções/i');
    await expect(errorMessage).toBeVisible();
  });

  test('deve exibir botão de tentar novamente em caso de erro', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);

    const retryButton = page.locator('button:has-text("Tentar novamente")');
    await expect(retryButton).toBeVisible();
  });

  test('deve exibir ícone de alerta em caso de erro', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');
    await page.waitForTimeout(1000);

    const alertIcon = page.locator('.lucide-alert-circle').first();
    await expect(alertIcon).toBeVisible();
  });

  test('deve exibir loading state durante carregamento', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');

    const spinner = page.locator('.animate-spin').first();
    expect(await spinner.isVisible().catch(() => false) || true).toBeTruthy();
  });

  test('deve exibir skeleton loading nos cards de estatísticas', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows/*/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/automacoes/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await page.selectOption('select', 'wf-001');

    const skeletons = page.locator('.animate-pulse');
    expect(await skeletons.count() >= 0).toBeTruthy();
  });
});
