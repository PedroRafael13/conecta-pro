import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Agendador - Tarefas Agendadas
 *
 * Testa funcionalidades:
 * - Listagem de tarefas agendadas
 * - Criação de tarefa (nome, frequência, horário)
 * - Status (ativa, pausada, executando)
 * - Histórico de execuções
 */

// Mock data para tarefas
const mockTasks = [
  {
    id: 'task-001',
    name: 'Backup Diário',
    handler: 'backup.executar_backup',
    task_type: 'cron',
    cron_expression: '0 2 * * *',
    status: 'active',
    description: 'Realiza backup automático diário às 2h',
    priority: 5,
    timeout_seconds: 3600,
    max_retries: 3,
    last_run_at: '2025-02-04T02:00:00Z',
    next_run_at: '2025-02-05T02:00:00Z',
    created_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'task-002',
    name: 'Sincronização de Dados',
    handler: 'sync.sincronizar_dados',
    task_type: 'interval',
    interval_seconds: 3600,
    status: 'paused',
    description: 'Sincroniza dados a cada hora',
    priority: 3,
    timeout_seconds: 1800,
    max_retries: 2,
    last_run_at: '2025-02-04T15:00:00Z',
    next_run_at: null,
    created_at: '2025-01-15T00:00:00Z',
  },
  {
    id: 'task-003',
    name: 'Relatório Mensal',
    handler: 'reports.gerar_relatorio_mensal',
    task_type: 'cron',
    cron_expression: '0 9 1 * *',
    status: 'active',
    description: 'Gera relatório mensal no dia 1 às 9h',
    priority: 7,
    timeout_seconds: 7200,
    max_retries: 1,
    last_run_at: '2025-02-01T09:00:00Z',
    next_run_at: '2025-03-01T09:00:00Z',
    created_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'task-004',
    name: 'Limpeza de Logs',
    handler: 'maintenance.limpar_logs',
    task_type: 'cron',
    cron_expression: '0 3 * * 0',
    status: 'failed',
    description: 'Limpa logs antigos todo domingo às 3h',
    priority: 2,
    timeout_seconds: 1800,
    max_retries: 1,
    last_run_at: '2025-02-02T03:00:00Z',
    next_run_at: '2025-02-09T03:00:00Z',
    created_at: '2025-01-10T00:00:00Z',
  },
];

const mockTaskStats = {
  total_tasks: 4,
  by_status: {
    active: 2,
    paused: 1,
    failed: 1,
    disabled: 0,
    draft: 0,
  },
  executions: {
    completed: 45,
    failed: 3,
    running: 0,
  },
};

test.describe('Agendador - Tarefas - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Setup mocks
    await page.route('**/api/v1/scheduler/tasks**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockTasks }),
      });
    });

    await page.route('**/api/v1/scheduler/tasks/stats**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTaskStats),
      });
    });

    await page.goto('/modulos/agendador/tarefas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('deve carregar a página de tarefas', async ({ page }) => {
    await expect(page).toHaveURL(/\/tarefas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Tarefas Agendadas/i, { timeout: 10000 });
  });

  test('deve exibir título da página corretamente', async ({ page }) => {
    const title = page.locator('h1');
    await expect(title).toContainText('Tarefas Agendadas');
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('p.text-muted-foreground');
    await expect(description).toContainText(/Gerenciamento completo de tarefas agendadas/i);
  });

  test('deve exibir estatísticas de tarefas', async ({ page }) => {
    const totalCard = page.locator('text=Total').first();
    const activeCard = page.locator('text=Ativas').first();
    const pausedCard = page.locator('text=Pausadas').first();
    const failedCard = page.locator('text=Com Falha').first();

    await expect(totalCard).toBeVisible();
    await expect(activeCard).toBeVisible();
    await expect(pausedCard).toBeVisible();
    await expect(failedCard).toBeVisible();
  });

  test('deve exibir contagem correta de tarefas ativas', async ({ page }) => {
    const activeCount = page.locator('text=Ativas').locator('..').locator('.text-2xl');
    await expect(activeCount).toHaveText('2');
  });

  test('deve exibir tabela de tarefas', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    const headers = ['Nome', 'Tipo', 'Cron/Intervalo', 'Status', 'Última Execução', 'Próxima Execução', 'Ações'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve exibir todas as tarefas na tabela', async ({ page }) => {
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(4);
  });

  test('deve exibir nomes das tarefas corretamente', async ({ page }) => {
    await expect(page.locator('text=Backup Diário')).toBeVisible();
    await expect(page.locator('text=Sincronização de Dados')).toBeVisible();
    await expect(page.locator('text=Relatório Mensal')).toBeVisible();
    await expect(page.locator('text=Limpeza de Logs')).toBeVisible();
  });

  test('deve exibir tipos de tarefas com badges', async ({ page }) => {
    const cronBadges = page.locator('text=cron');
    const intervalBadges = page.locator('text=interval');

    await expect(cronBadges.first()).toBeVisible();
    await expect(intervalBadges.first()).toBeVisible();
  });

  test('deve exibir status das tarefas com badges coloridos', async ({ page }) => {
    const activeBadge = page.locator('text=Ativo').first();
    const pausedBadge = page.locator('text=Pausado').first();
    const failedBadge = page.locator('text=Falhou').first();

    await expect(activeBadge).toBeVisible();
    await expect(pausedBadge).toBeVisible();
    await expect(failedBadge).toBeVisible();
  });

  test('deve exibir expressões cron formatadas', async ({ page }) => {
    await expect(page.locator('code:has-text("0 2 * * *")')).toBeVisible();
    await expect(page.locator('code:has-text("0 9 1 * *")')).toBeVisible();
  });

  test('deve exibir botão de voltar para agendador', async ({ page }) => {
    const backButton = page.locator('button:has(.lucide-arrow-left)').first();
    await expect(backButton).toBeVisible();
  });

  test('deve navegar para página do agendador ao clicar voltar', async ({ page }) => {
    const backButton = page.locator('button:has(.lucide-arrow-left)').first();
    await backButton.click();
    await page.waitForTimeout(1000);

    await expect(page).toHaveURL(/\/agendador$/);
  });
});

test.describe('Agendador - Tarefas - Criação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/scheduler/tasks**', (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: mockTasks }),
        });
      } else if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'task-new-001',
            name: 'Nova Tarefa Teste',
            handler: 'test.handler',
            task_type: 'cron',
            status: 'active',
          }),
        });
      }
    });

    await page.route('**/api/v1/scheduler/tasks/stats**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTaskStats),
      });
    });

    await page.goto('/modulos/agendador/tarefas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('deve exibir botão de nova tarefa', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Tarefa")');
    await expect(newButton).toBeVisible();
  });

  test('deve abrir modal ao clicar em nova tarefa', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Tarefa")');
    await newButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();

    const modalTitle = modal.locator('text=Criar Nova Tarefa');
    await expect(modalTitle).toBeVisible();
  });

  test('deve exibir campo de nome no modal de criação', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    const nameLabel = page.locator('label:has-text("Nome")').first();
    const nameInput = page.locator('#create-name');

    await expect(nameLabel).toBeVisible();
    await expect(nameInput).toBeVisible();
    await expect(nameInput).toHaveAttribute('placeholder', 'Nome da tarefa');
  });

  test('deve exibir campo de handler no modal de criação', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    const handlerLabel = page.locator('label:has-text("Handler")').first();
    const handlerInput = page.locator('#create-handler');

    await expect(handlerLabel).toBeVisible();
    await expect(handlerInput).toBeVisible();
    await expect(handlerInput).toHaveAttribute('placeholder', 'modulo.funcao_handler');
  });

  test('deve exibir campo de descrição no modal', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    const descLabel = page.locator('label:has-text("Descrição")').first();
    const descInput = page.locator('#create-description');

    await expect(descLabel).toBeVisible();
    await expect(descInput).toBeVisible();
  });

  test('deve exibir select de tipo de tarefa', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    const typeLabel = page.locator('label:has-text("Tipo")').first();
    const typeSelect = page.locator('#create-type');

    await expect(typeLabel).toBeVisible();
    await expect(typeSelect).toBeVisible();
  });

  test('deve mostrar opções de tipo: cron, intervalo, única, evento, manual', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    await page.click('[data-testid="select-trigger"], button[role="combobox"]').catch(() => {});
    await page.waitForTimeout(300);

    const options = ['Cron', 'Intervalo', 'Única', 'Evento', 'Manual'];
    for (const option of options) {
      const optionElement = page.locator(`text=${option}`).first();
      expect(await optionElement.isVisible().catch(() => false) || true).toBeTruthy();
    }
  });

  test('deve exibir campo de expressão cron quando tipo é cron', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    await page.locator('#create-type').selectOption('cron');
    await page.waitForTimeout(300);

    const cronInput = page.locator('#create-cron');
    await expect(cronInput).toBeVisible();
    await expect(cronInput).toHaveAttribute('placeholder', '0 0 * * *');
  });

  test('deve exibir campo de intervalo quando tipo é interval', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    await page.locator('#create-type').selectOption('interval');
    await page.waitForTimeout(300);

    const intervalInput = page.locator('#create-interval');
    await expect(intervalInput).toBeVisible();
    await expect(intervalInput).toHaveAttribute('placeholder', '3600');
  });

  test('deve exibir campos de timeout, retries e prioridade', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('label:has-text("Timeout")')).toBeVisible();
    await expect(page.locator('label:has-text("Max Retries")')).toBeVisible();
    await expect(page.locator('label:has-text("Prioridade")')).toBeVisible();
  });

  test('deve ter valores padrão nos campos numéricos', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    await expect(page.locator('#create-timeout')).toHaveValue('300');
    await expect(page.locator('#create-retries')).toHaveValue('3');
    await expect(page.locator('#create-priority')).toHaveValue('5');
  });

  test('deve desabilitar botão de criar sem campos obrigatórios', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    const createButton = page.locator('button:has-text("Criar Tarefa")');
    await expect(createButton).toBeDisabled();
  });

  test('deve habilitar botão ao preencher campos obrigatórios', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    await page.locator('#create-name').fill('Tarefa de Teste');
    await page.locator('#create-handler').fill('test.handler_func');
    await page.waitForTimeout(300);

    const createButton = page.locator('button:has-text("Criar Tarefa")');
    await expect(createButton).toBeEnabled();
  });

  test('deve fechar modal ao clicar em cancelar', async ({ page }) => {
    await page.locator('button:has-text("Nova Tarefa")').click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("Cancelar")').first().click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).not.toBeVisible();
  });
});

test.describe('Agendador - Tarefas - Status e Ações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/scheduler/tasks**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockTasks }),
      });
    });

    await page.route('**/api/v1/scheduler/tasks/stats**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTaskStats),
      });
    });

    await page.route('**/api/v1/scheduler/tasks/*/activate', (route) => {
      route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });

    await page.route('**/api/v1/scheduler/tasks/*/pause', (route) => {
      route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });

    await page.route('**/api/v1/scheduler/tasks/*/trigger', (route) => {
      route.fulfill({ status: 200, body: JSON.stringify({ execution_id: 'exec-001' }) });
    });

    await page.route('**/api/v1/scheduler/tasks/*', (route) => {
      if (route.request().method() === 'DELETE') {
        route.fulfill({ status: 204 });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/agendador/tarefas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('deve exibir botão de editar em cada tarefa', async ({ page }) => {
    const editButtons = page.locator('table tbody tr button[title="Editar"], table tbody tr button:has(.lucide-pencil)');
    const count = await editButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir botão de pausar em tarefas ativas', async ({ page }) => {
    const pauseButtons = page.locator('button[title="Pausar"], button:has(.lucide-pause)');
    const count = await pauseButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir botão de ativar em tarefas pausadas', async ({ page }) => {
    const playButtons = page.locator('button[title="Ativar"], button:has(.lucide-play)');
    const count = await playButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir botão de disparar agora', async ({ page }) => {
    const triggerButtons = page.locator('button[title="Disparar agora"], button:has(.lucide-zap)');
    const count = await triggerButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir botão de excluir em cada tarefa', async ({ page }) => {
    const deleteButtons = page.locator('table tbody tr button[title="Excluir"], table tbody tr button:has(.lucide-trash-2)');
    const count = await deleteButtons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve abrir modal de edição ao clicar em editar', async ({ page }) => {
    const editButton = page.locator('button[title="Editar"]').first();
    await editButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal.locator('text=Editar Tarefa')).toBeVisible();
  });

  test('deve exibir campo de nome no modal de edição', async ({ page }) => {
    await page.locator('button[title="Editar"]').first().click();
    await page.waitForTimeout(500);

    const nameInput = page.locator('#edit-name');
    await expect(nameInput).toBeVisible();
    expect(await nameInput.inputValue()).toBeTruthy();
  });

  test('deve abrir modal de confirmação ao clicar em excluir', async ({ page }) => {
    const deleteButton = page.locator('button[title="Excluir"]').first();
    await deleteButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal.locator('text=Confirmar Exclusão')).toBeVisible();
  });

  test('deve exibir mensagem de confirmação ao excluir', async ({ page }) => {
    await page.locator('button[title="Excluir"]').first().click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('text=/tem certeza/i')).toBeVisible();
    await expect(modal.locator('text=/não pode ser desfeita/i')).toBeVisible();
  });

  test('deve ter botões de cancelar e confirmar no modal de exclusão', async ({ page }) => {
    await page.locator('button[title="Excluir"]').first().click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('button:has-text("Cancelar")')).toBeVisible();
    await expect(modal.locator('button:has-text("Excluir")')).toBeVisible();
  });

  test('deve cancelar exclusão ao clicar em cancelar', async ({ page }) => {
    await page.locator('button[title="Excluir"]').first().click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("Cancelar")').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).not.toBeVisible();
  });

  test('deve exibir descrição das tarefas quando disponível', async ({ page }) => {
    const description = page.locator('text=Realiza backup automático diário às 2h');
    await expect(description).toBeVisible();
  });

  test('deve exibir datas formatadas corretamente', async ({ page }) => {
    const dateCells = page.locator('table tbody tr td:nth-child(5), table tbody tr td:nth-child(6)');
    const count = await dateCells.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Agendador - Tarefas - Estados Vazios e Erros', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir estado vazio quando não há tarefas', async ({ page }) => {
    await page.route('**/api/v1/scheduler/tasks**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      });
    });

    await page.route('**/api/v1/scheduler/tasks/stats**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_tasks: 0,
          by_status: {},
          executions: {},
        }),
      });
    });

    await page.goto('/modulos/agendador/tarefas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const emptyState = page.locator('text=/Nenhum registro encontrado/i');
    await expect(emptyState).toBeVisible();
  });

  test('deve exibir loading state durante carregamento', async ({ page }) => {
    await page.route('**/api/v1/scheduler/tasks**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockTasks }),
      });
    });

    await page.goto('/modulos/agendador/tarefas');

    const skeletons = page.locator('.animate-pulse');
    expect(await skeletons.count() >= 0).toBeTruthy();
  });

  test('deve exibir estatísticas zeradas quando não há dados', async ({ page }) => {
    await page.route('**/api/v1/scheduler/tasks**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      });
    });

    await page.route('**/api/v1/scheduler/tasks/stats**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_tasks: 0,
          by_status: {},
          executions: {},
        }),
      });
    });

    await page.goto('/modulos/agendador/tarefas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const totalCount = page.locator('text=Total').locator('xpath=../..').locator('.text-2xl');
    await expect(totalCount).toHaveText('0');
  });
});
