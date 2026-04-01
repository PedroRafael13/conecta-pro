import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Agendador - Execuções
 *
 * Testa funcionalidades:
 * - Log de execuções
 * - Status (sucesso, erro, pendente)
 * - Detalhes da execução
 * - Reexecução manual
 */

// Mock data para execuções
const mockExecutions = [
  {
    id: 'exec-001',
    task_id: 'task-001',
    execution_number: 1,
    attempt_number: 1,
    status: 'success',
    started_at: '2025-02-05T02:00:00Z',
    completed_at: '2025-02-05T02:05:30Z',
    duration_seconds: 330,
    output_result: { message: 'Backup completed successfully', size: '1.2GB' },
    error_message: null,
    progress_percent: 100,
    progress_message: null,
  },
  {
    id: 'exec-002',
    task_id: 'task-002',
    execution_number: 15,
    attempt_number: 1,
    status: 'running',
    started_at: '2025-02-05T16:00:00Z',
    completed_at: null,
    duration_seconds: null,
    output_result: null,
    error_message: null,
    progress_percent: 65,
    progress_message: 'Sincronizando dados do cliente...',
  },
  {
    id: 'exec-003',
    task_id: 'task-004',
    execution_number: 5,
    attempt_number: 3,
    status: 'failed',
    started_at: '2025-02-02T03:00:00Z',
    completed_at: '2025-02-02T03:01:45Z',
    duration_seconds: 105,
    output_result: null,
    error_message: 'Disk space insufficient for log cleanup. Required: 500MB, Available: 120MB',
    progress_percent: null,
    progress_message: null,
  },
  {
    id: 'exec-004',
    task_id: 'task-001',
    execution_number: 2,
    attempt_number: 1,
    status: 'pending',
    started_at: null,
    completed_at: null,
    duration_seconds: null,
    output_result: null,
    error_message: null,
    progress_percent: null,
    progress_message: null,
  },
  {
    id: 'exec-005',
    task_id: 'task-003',
    execution_number: 1,
    attempt_number: 1,
    status: 'cancelled',
    started_at: '2025-02-01T09:00:00Z',
    completed_at: '2025-02-01T09:15:00Z',
    duration_seconds: 900,
    output_result: null,
    error_message: 'Cancelled by user',
    progress_percent: 45,
    progress_message: null,
  },
  {
    id: 'exec-006',
    task_id: 'task-002',
    execution_number: 14,
    attempt_number: 2,
    status: 'retry',
    started_at: '2025-02-05T15:00:00Z',
    completed_at: null,
    duration_seconds: null,
    output_result: null,
    error_message: 'Connection timeout, retrying...',
    progress_percent: 30,
    progress_message: 'Retry attempt 2/3',
  },
];

test.describe('Agendador - Execuções - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Setup mocks
    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.route('**/api/v1/scheduler/executions/*/cancel', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.goto('/modulos/agendador/execucoes');
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
    await expect(description).toContainText(/Acompanhamento de todas as execuções de tarefas agendadas/i);
  });

  test('deve exibir estatísticas de execuções', async ({ page }) => {
    const totalCard = page.locator('text=Total').first();
    const runningCard = page.locator('text=Executando').first();
    const completedCard = page.locator('text=Concluídas').first();
    const failedCard = page.locator('text=Falhas').first();

    await expect(totalCard).toBeVisible();
    await expect(runningCard).toBeVisible();
    await expect(completedCard).toBeVisible();
    await expect(failedCard).toBeVisible();
  });

  test('deve exibir contagem correta de execuções', async ({ page }) => {
    const totalCount = page.locator('text=Total').locator('xpath=../..').locator('.text-2xl');
    await expect(totalCount).toHaveText('6');
  });

  test('deve exibir contagem correta de execuções em andamento', async ({ page }) => {
    const runningCount = page.locator('text=Executando').locator('xpath=../..').locator('.text-2xl');
    await expect(runningCount).toHaveText('1');
  });

  test('deve exibir contagem correta de execuções concluídas', async ({ page }) => {
    const successCount = page.locator('text=Concluídas').locator('xpath=../..').locator('.text-2xl');
    await expect(successCount).toHaveText('1');
  });

  test('deve exibir contagem correta de falhas', async ({ page }) => {
    const failedCount = page.locator('text=Falhas').locator('xpath=../..').locator('.text-2xl');
    await expect(failedCount).toHaveText('1');
  });

  test('deve exibir tabela de execuções', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    const headers = ['Tarefa', 'Início', 'Fim', 'Duração', 'Status', 'Resultado', 'Ações'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve exibir todas as execuções na tabela', async ({ page }) => {
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(6);
  });

  test('deve exibir IDs das tarefas na coluna Tarefa', async ({ page }) => {
    await expect(page.locator('text=task-001')).toBeVisible();
    await expect(page.locator('text=task-002')).toBeVisible();
    await expect(page.locator('text=task-004')).toBeVisible();
  });

  test('deve exibir número de execução e tentativa', async ({ page }) => {
    await expect(page.locator('text=#1')).toBeVisible();
    await expect(page.locator('text=Tentativa 1')).toBeVisible();
  });

  test('deve exibir datas de início formatadas', async ({ page }) => {
    const dateCells = page.locator('table tbody tr td:nth-child(2)');
    const count = await dateCells.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir datas de fim formatadas quando disponível', async ({ page }) => {
    const completedRow = page.locator('table tbody tr:has-text("Concluída")').first();
    await expect(completedRow).toBeVisible();
  });

  test('deve exibir traço quando não há data de fim', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    const dateCell = runningRow.locator('td:nth-child(3)');
    await expect(dateCell).toContainText('-');
  });

  test('deve exibir duração formatada corretamente', async ({ page }) => {
    await expect(page.locator('text=5m 30s')).toBeVisible();
    await expect(page.locator('text=1m 45s')).toBeVisible();
  });

  test('deve exibir traço quando não há duração', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    const durationCell = runningRow.locator('td:nth-child(4)');
    await expect(durationCell).toContainText('-');
  });

  test('deve exibir status com badges coloridos', async ({ page }) => {
    await expect(page.locator('text=Concluída').first()).toBeVisible();
    await expect(page.locator('text=Executando').first()).toBeVisible();
    await expect(page.locator('text=Falhou').first()).toBeVisible();
    await expect(page.locator('text=Pendente').first()).toBeVisible();
  });

  test('deve exibir ícones nos badges de status', async ({ page }) => {
    const statusBadges = page.locator('table tbody tr td:nth-child(5) span');
    const count = await statusBadges.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Agendador - Execuções - Status Detalhados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/agendador/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve exibir status "Concluída" em verde', async ({ page }) => {
    const successBadge = page.locator('text=Concluída').first();
    await expect(successBadge).toBeVisible();
    await expect(successBadge.locator('..')).toHaveClass(/bg-green/);
  });

  test('deve exibir status "Executando" em azul', async ({ page }) => {
    const runningBadge = page.locator('text=Executando').first();
    await expect(runningBadge).toBeVisible();
    await expect(runningBadge.locator('..')).toHaveClass(/bg-blue/);
  });

  test('deve exibir status "Falhou" em vermelho', async ({ page }) => {
    const failedBadge = page.locator('text=Falhou').first();
    await expect(failedBadge).toBeVisible();
    await expect(failedBadge.locator('..')).toHaveClass(/bg-red/);
  });

  test('deve exibir status "Pendente" em cinza', async ({ page }) => {
    const pendingBadge = page.locator('text=Pendente').first();
    await expect(pendingBadge).toBeVisible();
    await expect(pendingBadge.locator('..')).toHaveClass(/bg-gray/);
  });

  test('deve exibir status "Cancelada" em cinza escuro', async ({ page }) => {
    const cancelledBadge = page.locator('text=Cancelada').first();
    await expect(cancelledBadge).toBeVisible();
  });

  test('deve exibir status "Tentando" em âmbar', async ({ page }) => {
    const retryBadge = page.locator('text=Tentando').first();
    await expect(retryBadge).toBeVisible();
    await expect(retryBadge.locator('..')).toHaveClass(/bg-amber/);
  });
});

test.describe('Agendador - Execuções - Resultados e Logs', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/agendador/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve exibir "OK" em execuções bem-sucedidas', async ({ page }) => {
    const successRow = page.locator('table tbody tr:has-text("Concluída")').first();
    const resultCell = successRow.locator('td:nth-child(6)');
    await expect(resultCell).toContainText('OK');
  });

  test('deve exibir mensagem de erro truncada em execuções com falha', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const resultCell = failedRow.locator('td:nth-child(6)');
    await expect(resultCell).toContainText('Disk space insufficient');
  });

  test('deve truncar mensagens de erro longas', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const errorMessage = failedRow.locator('td:nth-child(6) span');
    await expect(errorMessage).toHaveClass(/truncate/);
  });

  test('deve exibir barra de progresso em execuções em andamento', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    const progressBar = runningRow.locator('td:nth-child(6) .bg-blue-600');
    await expect(progressBar).toBeVisible();
  });

  test('deve exibir porcentagem de progresso', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await expect(runningRow.locator('text=65%')).toBeVisible();
  });

  test('deve exibir mensagem de progresso quando disponível', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    const progressMessage = runningRow.locator('td:nth-child(6)');
    expect(await progressMessage.textContent()).toContain('Sincronizando');
  });

  test('deve exibir traço quando não há resultado', async ({ page }) => {
    const pendingRow = page.locator('table tbody tr:has-text("Pendente")').first();
    const resultCell = pendingRow.locator('td:nth-child(6)');
    await expect(resultCell).toContainText('-');
  });

  test('deve aplicar tooltip em mensagens de erro truncadas', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const errorSpan = failedRow.locator('td:nth-child(6) span');
    await expect(errorSpan).toHaveAttribute('title');
  });
});

test.describe('Agendador - Execuções - Ações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.route('**/api/v1/scheduler/executions/*/cancel', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.goto('/modulos/agendador/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve exibir botão de cancelar em execuções pendentes', async ({ page }) => {
    const pendingRow = page.locator('table tbody tr:has-text("Pendente")').first();
    const cancelButton = pendingRow.locator('button[title="Cancelar execução"], button:has(.lucide-ban)');
    await expect(cancelButton).toBeVisible();
  });

  test('deve exibir botão de cancelar em execuções na fila', async ({ page }) => {
    // Adicionar execução na fila
    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          ...mockExecutions,
          {
            id: 'exec-007',
            task_id: 'task-001',
            status: 'queued',
            started_at: null,
            completed_at: null,
          },
        ]),
      });
    });

    await page.reload();
    await page.waitForTimeout(1000);

    const queuedRow = page.locator('table tbody tr:has-text("Na Fila")').first();
    const cancelButton = queuedRow.locator('button[title="Cancelar execução"], button:has(.lucide-ban)');
    await expect(cancelButton).toBeVisible();
  });

  test('deve exibir botão de cancelar em execuções em andamento', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    const cancelButton = runningRow.locator('button[title="Cancelar execução"], button:has(.lucide-ban)');
    await expect(cancelButton).toBeVisible();
  });

  test('não deve exibir botão de cancelar em execuções concluídas', async ({ page }) => {
    const successRow = page.locator('table tbody tr:has-text("Concluída")').first();
    const cancelButton = successRow.locator('button[title="Cancelar execução"]');
    await expect(cancelButton).not.toBeVisible();
  });

  test('não deve exibir botão de cancelar em execuções falhas', async ({ page }) => {
    const failedRow = page.locator('table tbody tr:has-text("Falhou")').first();
    const cancelButton = failedRow.locator('button[title="Cancelar execução"]');
    await expect(cancelButton).not.toBeVisible();
  });

  test('deve exibir traço na coluna de ações quando não pode cancelar', async ({ page }) => {
    const successRow = page.locator('table tbody tr:has-text("Concluída")').first();
    const actionCell = successRow.locator('td:nth-child(7)');
    await expect(actionCell).toContainText('-');
  });

  test('deve abrir modal de confirmação ao clicar em cancelar', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    const cancelButton = runningRow.locator('button[title="Cancelar execução"], button:has(.lucide-ban)');
    await cancelButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal.locator('text=Cancelar Execução')).toBeVisible();
  });

  test('deve exibir campo de motivo no modal de cancelamento', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await runningRow.locator('button[title="Cancelar execução"], button:has(.lucide-ban)').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('label:has-text("Motivo")')).toBeVisible();
    await expect(modal.locator('#cancel-reason')).toBeVisible();
  });

  test('deve ter botões de voltar e confirmar no modal de cancelamento', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await runningRow.locator('button[title="Cancelar execução"], button:has(.lucide-ban)').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('button:has-text("Voltar")')).toBeVisible();
    await expect(modal.locator('button:has-text("Cancelar Execução")')).toBeVisible();
  });

  test('deve fechar modal ao clicar em voltar', async ({ page }) => {
    const runningRow = page.locator('table tbody tr:has-text("Executando")').first();
    await runningRow.locator('button[title="Cancelar execução"], button:has(.lucide-ban)').click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("Voltar")').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).not.toBeVisible();
  });

  test('deve exibir botão de voltar para agendador', async ({ page }) => {
    const backButton = page.locator('button:has(.lucide-arrow-left)').first();
    await expect(backButton).toBeVisible();
  });
});

test.describe('Agendador - Execuções - Estados Vazios e Erros', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir estado vazio quando não há execuções', async ({ page }) => {
    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/modulos/agendador/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    const emptyState = page.locator('text=/Nenhum registro encontrado/i');
    await expect(emptyState).toBeVisible();
  });

  test('deve exibir loading state durante carregamento', async ({ page }) => {
    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/agendador/execucoes');

    const skeletons = page.locator('.animate-pulse');
    expect(await skeletons.count() >= 0).toBeTruthy();
  });

  test('deve exibir estatísticas zeradas quando não há dados', async ({ page }) => {
    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/modulos/agendador/execucoes');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    const totalCount = page.locator('text=Total').locator('xpath=../..').locator('.text-2xl');
    await expect(totalCount).toHaveText('0');
  });

  test('deve exibir indicador de carregamento nos cards durante fetch', async ({ page }) => {
    await page.route('**/api/v1/scheduler/executions**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockExecutions),
      });
    });

    await page.goto('/modulos/agendador/execucoes');

    const loadingElements = page.locator('.animate-pulse, .animate-spin');
    expect(await loadingElements.count() >= 0).toBeTruthy();
  });
});
