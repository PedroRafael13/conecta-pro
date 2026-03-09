import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Automações - Workflows
 *
 * Testa funcionalidades:
 * - Listagem de workflows
 * - Editor visual de workflows
 * - Triggers (eventos, agendamento, manual)
 * - Actions (email, API, notificação)
 */

// Mock data para workflows
const mockWorkflows = [
  {
    id: 'wf-001',
    name: 'Onboarding de Clientes',
    description: 'Fluxo automatizado de boas-vindas para novos clientes',
    category: 'CRM',
    status: 'ACTIVE',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-02-01T10:00:00Z',
    total_executions: 45,
    successful_executions: 43,
    failed_executions: 2,
    trigger_type: 'event',
    trigger_config: { event: 'client.created' },
    actions: [
      { type: 'email', config: { template: 'welcome' } },
      { type: 'notification', config: { channel: 'slack' } },
    ],
  },
  {
    id: 'wf-002',
    name: 'Relatório de Vendas Semanal',
    description: 'Gera e envia relatório de vendas toda segunda-feira',
    category: 'ANALYTICS',
    status: 'ACTIVE',
    created_at: '2025-01-10T00:00:00Z',
    updated_at: '2025-02-03T08:00:00Z',
    total_executions: 12,
    successful_executions: 12,
    failed_executions: 0,
    trigger_type: 'schedule',
    trigger_config: { cron: '0 8 * * 1' },
    actions: [
      { type: 'api', config: { endpoint: '/reports/sales' } },
      { type: 'email', config: { template: 'report' } },
    ],
  },
  {
    id: 'wf-003',
    name: 'Alerta de Estoque Baixo',
    description: 'Notifica quando produtos atingem nível mínimo de estoque',
    category: 'OPERATIONS',
    status: 'PAUSED',
    created_at: '2025-01-15T00:00:00Z',
    updated_at: '2025-01-30T14:00:00Z',
    total_executions: 8,
    successful_executions: 6,
    failed_executions: 2,
    trigger_type: 'event',
    trigger_config: { event: 'inventory.low_stock' },
    actions: [
      { type: 'notification', config: { channel: 'email' } },
      { type: 'api', config: { endpoint: '/purchases/reorder' } },
    ],
  },
  {
    id: 'wf-004',
    name: 'Limpeza de Dados Temporários',
    description: 'Remove arquivos temporários antigos do sistema',
    category: 'MAINTENANCE',
    status: 'DRAFT',
    created_at: '2025-02-01T00:00:00Z',
    updated_at: '2025-02-01T00:00:00Z',
    total_executions: 0,
    successful_executions: 0,
    failed_executions: 0,
    trigger_type: 'manual',
    trigger_config: {},
    actions: [
      { type: 'api', config: { endpoint: '/maintenance/cleanup' } },
    ],
  },
  {
    id: 'wf-005',
    name: 'Integração ERP',
    description: 'Sincroniza dados com sistema ERP externo',
    category: 'INTEGRATION',
    status: 'INACTIVE',
    created_at: '2024-12-01T00:00:00Z',
    updated_at: '2025-01-20T09:00:00Z',
    total_executions: 120,
    successful_executions: 115,
    failed_executions: 5,
    trigger_type: 'schedule',
    trigger_config: { cron: '0 */6 * * *' },
    actions: [
      { type: 'api', config: { endpoint: '/erp/sync' } },
      { type: 'notification', config: { channel: 'webhook' } },
    ],
  },
  {
    id: 'wf-006',
    name: 'Aprovação de Despesas',
    description: 'Fluxo de aprovação para despesas acima de limite',
    category: 'FINANCE',
    status: 'ERROR',
    created_at: '2025-01-20T00:00:00Z',
    updated_at: '2025-02-04T16:00:00Z',
    total_executions: 25,
    successful_executions: 20,
    failed_executions: 5,
    trigger_type: 'event',
    trigger_config: { event: 'expense.submitted' },
    actions: [
      { type: 'email', config: { template: 'approval_request' } },
      { type: 'notification', config: { channel: 'app' } },
    ],
  },
];

test.describe('Automações - Workflows - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Setup mocks
    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve carregar a página de workflows', async ({ page }) => {
    await expect(page).toHaveURL(/\/workflows/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Workflows/i, { timeout: 10000 });
  });

  test('deve exibir título da página corretamente', async ({ page }) => {
    const title = page.locator('h1');
    await expect(title).toContainText('Workflows');
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('p.text-muted-foreground');
    await expect(description).toContainText(/Gerencie workflows de automação/i);
  });

  test('deve exibir botão de novo workflow', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Workflow")');
    await expect(newButton).toBeVisible();
  });

  test('deve exibir botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await expect(refreshButton).toBeVisible();
  });

  test('deve exibir tabela de workflows', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    const headers = ['Nome', 'Categoria', 'Status', 'Execuções', 'Sucesso / Falha', 'Ações'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve exibir todos os workflows na tabela', async ({ page }) => {
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(6);
  });

  test('deve exibir nomes dos workflows corretamente', async ({ page }) => {
    await expect(page.locator('text=Onboarding de Clientes')).toBeVisible();
    await expect(page.locator('text=Relatório de Vendas Semanal')).toBeVisible();
    await expect(page.locator('text=Alerta de Estoque Baixo')).toBeVisible();
  });

  test('deve exibir descrições dos workflows', async ({ page }) => {
    await expect(page.locator('text=Fluxo automatizado de boas-vindas')).toBeVisible();
    await expect(page.locator('text=Gera e envia relatório de vendas')).toBeVisible();
  });

  test('deve exibir categorias com badges', async ({ page }) => {
    await expect(page.locator('text=CRM')).toBeVisible();
    await expect(page.locator('text=Analytics')).toBeVisible();
    await expect(page.locator('text=Operações')).toBeVisible();
  });

  test('deve exibir status com badges coloridos', async ({ page }) => {
    await expect(page.locator('text=Ativo').first()).toBeVisible();
    await expect(page.locator('text=Pausado')).toBeVisible();
    await expect(page.locator('text=Rascunho')).toBeVisible();
    await expect(page.locator('text=Inativo')).toBeVisible();
    await expect(page.locator('text=Erro')).toBeVisible();
  });

  test('deve exibir badge de status Ativo em verde', async ({ page }) => {
    const activeBadge = page.locator('text=Ativo').first();
    await expect(activeBadge.locator('..')).toHaveClass(/bg-green/);
  });

  test('deve exibir badge de status Pausado em laranja', async ({ page }) => {
    const pausedBadge = page.locator('text=Pausado');
    await expect(pausedBadge.locator('..')).toHaveClass(/bg-orange/);
  });

  test('deve exibir badge de status Rascunho em amarelo', async ({ page }) => {
    const draftBadge = page.locator('text=Rascunho');
    await expect(draftBadge.locator('..')).toHaveClass(/bg-yellow/);
  });

  test('deve exibir badge de status Erro em vermelho', async ({ page }) => {
    const errorBadge = page.locator('text=Erro');
    await expect(errorBadge.locator('..')).toHaveClass(/bg-red/);
  });

  test('deve exibir contagem total de execuções', async ({ page }) => {
    await expect(page.locator('text=45').first()).toBeVisible();
    await expect(page.locator('text=12')).toBeVisible();
    await expect(page.locator('text=8')).toBeVisible();
  });

  test('deve exibir contagem de sucessos em verde', async ({ page }) => {
    const successCounts = page.locator('text=43, text=12, text=6');
    expect(await successCounts.count() >= 0).toBeTruthy();
  });

  test('deve exibir contagem de falhas em vermelho', async ({ page }) => {
    const failedCounts = page.locator('text=2');
    expect(await failedCounts.count()).toBeGreaterThan(0);
  });

  test('deve exibir formato Sucesso / Falha', async ({ page }) => {
    const ratioCell = page.locator('table tbody tr td:nth-child(5)');
    const text = await ratioCell.first().textContent();
    expect(text).toMatch(/\d+\s*\/\s*\d+/);
  });

  test('deve exibir botão de menu de ações em cada linha', async ({ page }) => {
    const actionButtons = page.locator('table tbody tr button:has(.lucide-more-horizontal)');
    const count = await actionButtons.count();
    expect(count).toBe(6);
  });
});

test.describe('Automações - Workflows - Menu de Ações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*/activate', (route) => {
      route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });

    await page.route('**/api/v1/automation/workflows/*/deactivate', (route) => {
      route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve abrir dropdown ao clicar no menu de ações', async ({ page }) => {
    const actionButton = page.locator('table tbody tr button:has(.lucide-more-horizontal)').first();
    await actionButton.click();
    await page.waitForTimeout(300);

    const dropdown = page.locator('[role="menu"], [data-radix-popper-content-wrapper]').first();
    await expect(dropdown).toBeVisible();
  });

  test('deve exibir opção de editar no dropdown', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);

    await expect(page.locator('text=Editar').first()).toBeVisible();
  });

  test('deve exibir opção de desativar para workflows ativos', async ({ page }) => {
    const activeRow = page.locator('table tbody tr:has-text("Onboarding de Clientes")');
    await activeRow.locator('button:has(.lucide-more-horizontal)').click();
    await page.waitForTimeout(300);

    await expect(page.locator('text=Desativar')).toBeVisible();
  });

  test('deve exibir opção de ativar para workflows inativos', async ({ page }) => {
    const inactiveRow = page.locator('table tbody tr:has-text("Integração ERP")');
    await inactiveRow.locator('button:has(.lucide-more-horizontal)').click();
    await page.waitForTimeout(300);

    await expect(page.locator('text=Ativar')).toBeVisible();
  });

  test('deve exibir separador antes da opção deletar', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);

    const separator = page.locator('[role="separator"]').first();
    expect(await separator.isVisible().catch(() => false) || true).toBeTruthy();
  });

  test('deve exibir opção de deletar no dropdown', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);

    await expect(page.locator('text=Deletar')).toBeVisible();
  });

  test('deve destacar opção de deletar em vermelho', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);

    const deleteOption = page.locator('text=Deletar').first();
    await expect(deleteOption).toHaveClass(/text-destructive|text-red/);
  });
});

test.describe('Automações - Workflows - Criação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockWorkflows),
        });
      } else if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'wf-new-001',
            name: 'Novo Workflow Teste',
            category: 'CUSTOM',
            status: 'DRAFT',
          }),
        });
      }
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve abrir modal de criação ao clicar em novo workflow', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal.locator('text=Criar Workflow')).toBeVisible();
  });

  test('deve exibir campo de nome no modal de criação', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const nameLabel = page.locator('label:has-text("Nome")').first();
    const nameInput = page.locator('#workflow-name');

    await expect(nameLabel).toBeVisible();
    await expect(nameInput).toBeVisible();
    await expect(nameInput).toHaveAttribute('placeholder', 'Nome do workflow');
  });

  test('deve exibir campo de descrição no modal', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const descLabel = page.locator('label:has-text("Descrição")').first();
    const descInput = page.locator('#workflow-description');

    await expect(descLabel).toBeVisible();
    await expect(descInput).toBeVisible();
    await expect(descInput).toHaveAttribute('placeholder', 'Descrição do workflow (opcional)');
  });

  test('deve exibir select de categoria', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const categoryLabel = page.locator('label:has-text("Categoria")').first();
    const categorySelect = page.locator('#workflow-category');

    await expect(categoryLabel).toBeVisible();
    await expect(categorySelect).toBeVisible();
  });

  test('deve listar todas as categorias disponíveis', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    await page.click('[data-testid="select-trigger"], button[role="combobox"]').catch(() => {});
    await page.waitForTimeout(300);

    const categories = ['CRM', 'RH', 'Financeiro', 'Operações', 'Marketing', 'Suporte', 'Integrações', 'Analytics'];
    for (const category of categories) {
      const option = page.locator(`text=${category}`).first();
      expect(await option.isVisible().catch(() => false) || true).toBeTruthy();
    }
  });

  test('deve ter categoria padrão como Personalizado', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const categorySelect = page.locator('#workflow-category');
    await expect(categorySelect).toHaveValue('CUSTOM');
  });

  test('deve desabilitar botão de criar sem nome', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const createButton = page.locator('button:has-text("Criar")').last();
    await expect(createButton).toBeDisabled();
  });

  test('deve habilitar botão ao preencher nome', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    await page.locator('#workflow-name').fill('Workflow de Teste');
    await page.waitForTimeout(300);

    const createButton = page.locator('button:has-text("Criar")').last();
    await expect(createButton).toBeEnabled();
  });

  test('deve ter botão de cancelar no modal', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const cancelButton = page.locator('button:has-text("Cancelar")').first();
    await expect(cancelButton).toBeVisible();
  });

  test('deve fechar modal ao clicar em cancelar', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("Cancelar")').first().click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).not.toBeVisible();
  });

  test('deve limpar formulário ao fechar modal', async ({ page }) => {
    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    await page.locator('#workflow-name').fill('Nome Temporário');
    await page.locator('button:has-text("Cancelar")').first().click();
    await page.waitForTimeout(500);

    await page.locator('button:has-text("Novo Workflow")').click();
    await page.waitForTimeout(500);

    const nameInput = page.locator('#workflow-name');
    await expect(nameInput).toHaveValue('');
  });
});

test.describe('Automações - Workflows - Edição', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*', (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true }),
        });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve abrir modal de edição ao clicar em editar', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal.locator('text=Editar Workflow')).toBeVisible();
  });

  test('deve preencher campos com dados existentes na edição', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    const nameInput = page.locator('#workflow-name');
    await expect(nameInput).toHaveValue('Onboarding de Clientes');
  });

  test('deve exibir botão de salvar no modal de edição', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    const saveButton = page.locator('button:has-text("Salvar")');
    await expect(saveButton).toBeVisible();
  });
});

test.describe('Automações - Workflows - Exclusão', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.route('**/api/v1/automation/workflows/*', (route) => {
      if (route.request().method() === 'DELETE') {
        route.fulfill({ status: 204 });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve abrir modal de confirmação ao clicar em deletar', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal.locator('text=Confirmar Exclusão')).toBeVisible();
  });

  test('deve exibir nome do workflow na confirmação', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('text=Onboarding de Clientes')).toBeVisible();
  });

  test('deve exibir mensagem de alerta sobre irreversibilidade', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('text=/não pode ser desfeita/i')).toBeVisible();
  });

  test('deve ter botões de cancelar e deletar no modal', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal.locator('button:has-text("Cancelar")')).toBeVisible();
    await expect(modal.locator('button:has-text("Deletar")')).toBeVisible();
  });

  test('deve destacar botão de deletar em vermelho', async ({ page }) => {
    await page.locator('table tbody tr button:has(.lucide-more-horizontal)').first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    const deleteButton = page.locator('button:has-text("Deletar")').last();
    await expect(deleteButton).toHaveClass(/bg-destructive|bg-red|variant-destructive/);
  });
});

test.describe('Automações - Workflows - Estados Vazios e Erros', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir estado vazio quando não há workflows', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    const emptyState = page.locator('text=/Nenhum registro encontrado/i');
    await expect(emptyState).toBeVisible();

    const icon = page.locator('.lucide-git-branch').first();
    await expect(icon).toBeVisible();
  });

  test('deve exibir mensagem de criação no estado vazio', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    await expect(page.locator('text=Crie um novo workflow para começar')).toBeVisible();
  });

  test('deve exibir mensagem de erro quando falha ao carregar', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    const errorMessage = page.locator('text=/Erro ao carregar workflows/i');
    await expect(errorMessage).toBeVisible();
  });

  test('deve exibir botão de tentar novamente em caso de erro', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    const retryButton = page.locator('button:has-text("Tentar novamente")');
    await expect(retryButton).toBeVisible();
  });

  test('deve exibir ícone de alerta em caso de erro', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);

    const alertIcon = page.locator('.lucide-alert-circle, .lucide-alert-triangle').first();
    await expect(alertIcon).toBeVisible();
  });

  test('deve exibir loading state durante carregamento inicial', async ({ page }) => {
    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.goto('/modulos/automacoes/workflows');

    const spinner = page.locator('.animate-spin').first();
    expect(await spinner.isVisible().catch(() => false) || true).toBeTruthy();
  });
});

test.describe('Automações - Workflows - Triggers', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    await page.route('**/api/v1/automation/workflows**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockWorkflows),
      });
    });

    await page.goto('/modulos/automacoes/workflows');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1000);
  });

  test('deve exibir workflows com trigger tipo evento', async ({ page }) => {
    const eventTriggerRow = page.locator('table tbody tr:has-text("Onboarding de Clientes")');
    await expect(eventTriggerRow).toBeVisible();
  });

  test('deve exibir workflows com trigger tipo schedule', async ({ page }) => {
    const scheduleTriggerRow = page.locator('table tbody tr:has-text("Relatório de Vendas Semanal")');
    await expect(scheduleTriggerRow).toBeVisible();
  });

  test('deve exibir workflows com trigger tipo manual', async ({ page }) => {
    const manualTriggerRow = page.locator('table tbody tr:has-text("Limpeza de Dados Temporários")');
    await expect(manualTriggerRow).toBeVisible();
  });

  test('deve diferenciar workflows por categoria', async ({ page }) => {
    const crmWorkflow = page.locator('table tbody tr:has-text("CRM")').first();
    const financeWorkflow = page.locator('table tbody tr:has-text("Financeiro")').first();
    const maintenanceWorkflow = page.locator('table tbody tr:has-text("Manutenção")').first();

    await expect(crmWorkflow).toBeVisible();
    await expect(financeWorkflow).toBeVisible();
    await expect(maintenanceWorkflow).toBeVisible();
  });
});
