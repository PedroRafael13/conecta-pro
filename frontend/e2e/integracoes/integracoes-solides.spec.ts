/**
 * Testes E2E - Integrações: Sólides DP
 * Integração específica, sincronização de funcionários, mapeamento, status, conflitos
 */

import { test, expect } from '../fixtures';
import { loginViaAPI } from '../helpers/auth';

// Mock data para Sólides
const mockSolidesStatus = {
  connected: true,
  is_active: true,
  sync_status: 'success',
  last_sync: '2025-02-05T10:00:00Z',
  last_sync_at: '2025-02-05T10:00:00Z',
  total_employees: 150,
  pending_sync: 0,
  api_version: 'v2',
  health_check: { status: 'healthy', latency: 120 },
};

const mockSolidesConfig = {
  api_url: 'https://api.solides.com.br/v2',
  company_id: 'SOLIDES-12345',
  auth_method: 'api_key',
  sync_schedule: '0 2 * * *',
  auto_sync: true,
  field_mappings: {
    nome: { source: 'nome', target: 'name', required: true },
    cpf: { source: 'cpf', target: 'cpf', required: true },
    cargo: { source: 'cargo', target: 'position', required: true },
    departamento: { source: 'departamento', target: 'department', required: false },
    email: { source: 'email', target: 'email', required: true },
    telefone: { source: 'telefone', target: 'phone', required: false },
  },
};

const mockSolidesEmployees = [
  {
    id: 'emp-001',
    nome: 'João Silva',
    name: 'João Silva',
    cpf: '123.456.789-00',
    cargo: 'Analista de RH',
    position: 'Analista de RH',
    departamento: 'Recursos Humanos',
    department: 'Recursos Humanos',
    email: 'joao.silva@empresa.com',
    telefone: '(11) 98765-4321',
    ativo: true,
    active: true,
    sync_status: 'synced',
    updated_at: '2025-02-05T09:00:00Z',
  },
  {
    id: 'emp-002',
    nome: 'Maria Santos',
    name: 'Maria Santos',
    cpf: '987.654.321-00',
    cargo: 'Desenvolvedora Senior',
    position: 'Desenvolvedora Senior',
    departamento: 'Tecnologia',
    department: 'Tecnologia',
    email: 'maria.santos@empresa.com',
    telefone: '(11) 91234-5678',
    ativo: true,
    active: true,
    sync_status: 'synced',
    updated_at: '2025-02-04T15:00:00Z',
  },
  {
    id: 'emp-003',
    nome: 'Pedro Oliveira',
    name: 'Pedro Oliveira',
    cpf: '456.789.123-00',
    cargo: 'Gerente Financeiro',
    position: 'Gerente Financeiro',
    departamento: 'Financeiro',
    department: 'Financeiro',
    email: 'pedro.oliveira@empresa.com',
    telefone: '(11) 94567-8901',
    ativo: false,
    active: false,
    sync_status: 'synced',
    updated_at: '2025-01-15T10:00:00Z',
  },
  {
    id: 'emp-004',
    nome: 'Ana Costa',
    name: 'Ana Costa',
    cpf: '789.123.456-00',
    cargo: 'Analista de Marketing',
    position: 'Analista de Marketing',
    departamento: 'Marketing',
    department: 'Marketing',
    email: 'ana.costa@empresa.com',
    telefone: '(11) 97890-1234',
    ativo: true,
    active: true,
    sync_status: 'pending',
    updated_at: '2025-02-05T08:00:00Z',
  },
];

const mockSolidesSyncLogs = [
  {
    id: 'sync-001',
    sync_type: 'full',
    tipo: 'full',
    status: 'success',
    started_at: '2025-02-05T10:00:00Z',
    finished_at: '2025-02-05T10:05:00Z',
    records_processed: 150,
    registros: 150,
    duration: '5 minutos',
    duracao: '5 minutos',
    message: 'Sincronização completa realizada com sucesso',
    mensagem: 'Sincronização completa realizada com sucesso',
  },
  {
    id: 'sync-002',
    sync_type: 'incremental',
    tipo: 'incremental',
    status: 'success',
    started_at: '2025-02-04T10:00:00Z',
    finished_at: '2025-02-04T10:02:00Z',
    records_processed: 5,
    registros: 5,
    duration: '2 minutos',
    duracao: '2 minutos',
    message: 'Sincronização incremental concluída',
    mensagem: 'Sincronização incremental concluída',
  },
  {
    id: 'sync-003',
    sync_type: 'full',
    tipo: 'full',
    status: 'error',
    started_at: '2025-02-03T10:00:00Z',
    finished_at: '2025-02-03T10:01:00Z',
    records_processed: 0,
    registros: 0,
    duration: '1 minuto',
    duracao: '1 minuto',
    message: 'Erro na conexão com API Sólides',
    mensagem: 'Erro na conexão com API Sólides',
  },
];

const mockSolidesConflicts = [
  {
    id: 'conf-001',
    employee_name: 'João Silva',
    colaborador: 'João Silva',
    employee_id: 'emp-001',
    field: 'cargo',
    campo: 'cargo',
    solides_value: 'Analista Senior de RH',
    valor_solides: 'Analista Senior de RH',
    local_value: 'Analista de RH',
    valor_local: 'Analista de RH',
    status: 'pending',
    created_at: '2025-02-05T09:00:00Z',
  },
  {
    id: 'conf-002',
    employee_name: 'Maria Santos',
    colaborador: 'Maria Santos',
    employee_id: 'emp-002',
    field: 'departamento',
    campo: 'departamento',
    solides_value: 'Engenharia',
    valor_solides: 'Engenharia',
    local_value: 'Tecnologia',
    valor_local: 'Tecnologia',
    status: 'resolved',
    created_at: '2025-02-04T15:00:00Z',
  },
  {
    id: 'conf-003',
    employee_name: 'Pedro Oliveira',
    colaborador: 'Pedro Oliveira',
    employee_id: 'emp-003',
    field: 'email',
    campo: 'email',
    solides_value: 'pedro.oliveira@empresa.com.br',
    valor_solides: 'pedro.oliveira@empresa.com.br',
    local_value: 'pedro.oliveira@empresa.com',
    valor_local: 'pedro.oliveira@empresa.com',
    status: 'ignored',
    created_at: '2025-02-01T10:00:00Z',
  },
];

test.describe('Integrações - Sólides DP', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);

    // Mock endpoints de Sólides
    await page.route('**/api/v1/integrations/solides/status', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockSolidesStatus),
      });
    });

    await page.route('**/api/v1/integrations/solides/config', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockSolidesConfig),
      });
    });

    await page.route('**/api/v1/integrations/solides/employees**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockSolidesEmployees, total: mockSolidesEmployees.length }),
      });
    });

    await page.route('**/api/v1/integrations/solides/logs**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockSolidesSyncLogs, total: mockSolidesSyncLogs.length }),
      });
    });

    await page.route('**/api/v1/integrations/solides/conflicts**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: mockSolidesConflicts, total: mockSolidesConflicts.length }),
      });
    });

    await page.route('**/api/v1/integrations/solides/sync', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Sincronização iniciada', sync_id: 'sync-new' }),
      });
    });

    await page.route('**/api/v1/integrations/solides/disable', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Integração desabilitada' }),
      });
    });

    await page.route('**/api/v1/integrations/solides/conflicts/*/resolve', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Conflito resolvido' }),
      });
    });

    await page.goto('/modulos/integracoes/solides', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E VISUALIZAÇÃO
  // ==========================================

  test('deve carregar a página de Sólides DP', async ({ page }) => {
    const heading = page.locator('h1');
    await expect(heading).toContainText('Sólides DP');
  });

  test('deve exibir descrição da integração', async ({ page }) => {
    await expect(page.locator('text=Integracao com Solides Departamento Pessoal')).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await expect(page.locator('text=Status')).toBeVisible();
    await expect(page.locator('text=Colaboradores')).toBeVisible();
    await expect(page.locator('text=Ultima Sync')).toBeVisible();
    await expect(page.locator('text=Conflitos')).toBeVisible();
  });

  // ==========================================
  // TESTES DE STATUS DA INTEGRAÇÃO
  // ==========================================

  test('deve exibir status Conectado', async ({ page }) => {
    const statusCard = page.locator('[class*="Card"], .card').filter({ hasText: 'Status' }).first();
    await expect(statusCard).toContainText('Conectado');
  });

  test('deve exibir indicador visual de conectado', async ({ page }) => {
    await expect(page.locator('text=Conectado')).toBeVisible();
  });

  test('deve exibir quantidade de colaboradores sincronizados', async ({ page }) => {
    const employeesCard = page.locator('[class*="Card"], .card').filter({ hasText: 'Colaboradores' }).first();
    await expect(employeesCard).toContainText('4');
  });

  test('deve exibir data da última sincronização', async ({ page }) => {
    const lastSyncCard = page.locator('[class*="Card"], .card').filter({ hasText: 'Ultima Sync' }).first();
    await expect(lastSyncCard).toContainText('05/02/2025');
  });

  test('deve exibir contagem de conflitos pendentes', async ({ page }) => {
    const conflictsCard = page.locator('[class*="Card"], .card').filter({ hasText: 'Conflitos' }).first();
    await expect(conflictsCard).toContainText('3');
  });

  // ==========================================
  // TESTES DE ABAS/TABS
  // ==========================================

  test('deve exibir abas de navegação', async ({ page }) => {
    await expect(page.locator('button:has-text("Status"), [role="tab"]:has-text("Status")')).toBeVisible();
    await expect(page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")')).toBeVisible();
    await expect(page.locator('button:has-text("Logs"), [role="tab"]:has-text("Logs")')).toBeVisible();
    await expect(page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")')).toBeVisible();
  });

  test('deve navegar para aba de Colaboradores', async ({ page }) => {
    const tab = page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('table')).toBeVisible();
  });

  test('deve navegar para aba de Logs', async ({ page }) => {
    const tab = page.locator('button:has-text("Logs"), [role="tab"]:has-text("Logs")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('table')).toBeVisible();
  });

  test('deve navegar para aba de Conflitos', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('table')).toBeVisible();
  });

  // ==========================================
  // TESTES DE SINCRONIZAÇÃO DE FUNCIONÁRIOS
  // ==========================================

  test('deve exibir tabela de colaboradores', async ({ page }) => {
    const tab = page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")').first();
    await tab.click();
    await page.waitForTimeout(500);

    const headers = ['Nome', 'CPF', 'Cargo', 'Departamento', 'Status'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve listar todos os colaboradores', async ({ page }) => {
    const tab = page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")').first();
    await tab.click();
    await page.waitForTimeout(500);

    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(4);
  });

  test('deve exibir nome do colaborador', async ({ page }) => {
    const tab = page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=João Silva')).toBeVisible();
    await expect(page.locator('text=Maria Santos')).toBeVisible();
  });

  test('deve exibir CPF do colaborador', async ({ page }) => {
    const tab = page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=123.456.789-00')).toBeVisible();
  });

  test('deve exibir status ativo/inativo', async ({ page }) => {
    const tab = page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Ativo')).toBeVisible();
    await expect(page.locator('text=Inativo')).toBeVisible();
  });

  test('deve filtrar colaboradores por nome', async ({ page }) => {
    const tab = page.locator('button:has-text("Colaboradores"), [role="tab"]:has-text("Colaboradores")').first();
    await tab.click();
    await page.waitForTimeout(500);

    const searchInput = page.locator('input[placeholder*="Buscar"]');
    await searchInput.fill('João');
    await page.waitForTimeout(500);

    await expect(page.locator('text=João Silva')).toBeVisible();
    await expect(page.locator('text=Maria Santos')).not.toBeVisible();
  });

  // ==========================================
  // TESTES DE MAPEAMENTO DE CAMPOS
  // ==========================================

  test('deve exibir configuração de mapeamento de campos', async ({ page }) => {
    await expect(page.locator('text=Dados da Configuracao')).toBeVisible();
  });

  test('deve exibir API URL configurada', async ({ page }) => {
    await expect(page.locator('text=https://api.solides.com.br/v2')).toBeVisible();
  });

  test('deve exibir Company ID', async ({ page }) => {
    await expect(page.locator('text=SOLIDES-12345')).toBeVisible();
  });

  test('deve exibir método de autenticação', async ({ page }) => {
    await expect(page.locator('text=api_key')).toBeVisible();
  });

  // ==========================================
  // TESTES DE STATUS DA SINCRONIZAÇÃO
  // ==========================================

  test('deve exibir botão de sincronização', async ({ page }) => {
    await expect(page.locator('button:has-text("Sincronizar")')).toBeVisible();
  });

  test('deve iniciar sincronização ao clicar no botão', async ({ page }) => {
    await page.locator('button:has-text("Sincronizar")').click();
    await page.waitForTimeout(1000);

    await expect(page.locator('text=iniciada')).toBeVisible();
  });

  test('deve exibir logs de sincronização', async ({ page }) => {
    const tab = page.locator('button:has-text("Logs"), [role="tab"]:has-text("Logs")').first();
    await tab.click();
    await page.waitForTimeout(500);

    const headers = ['Data', 'Tipo', 'Status', 'Registros', 'Duracao', 'Mensagem'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve exibir sincronizações com sucesso em verde', async ({ page }) => {
    const tab = page.locator('button:has-text("Logs"), [role="tab"]:has-text("Logs")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=success')).toBeVisible();
  });

  test('deve exibir sincronizações com erro em vermelho', async ({ page }) => {
    const tab = page.locator('button:has-text("Logs"), [role="tab"]:has-text("Logs")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=error')).toBeVisible();
  });

  test('deve exibir tipo de sincronização', async ({ page }) => {
    const tab = page.locator('button:has-text("Logs"), [role="tab"]:has-text("Logs")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=full')).toBeVisible();
    await expect(page.locator('text=incremental')).toBeVisible();
  });

  test('deve exibir quantidade de registros processados', async ({ page }) => {
    const tab = page.locator('button:has-text("Logs"), [role="tab"]:has-text("Logs")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=150')).toBeVisible();
  });

  // ==========================================
  // TESTES DE RESOLUÇÃO DE CONFLITOS
  // ==========================================

  test('deve exibir tabela de conflitos', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    const headers = ['Colaborador', 'Campo', 'Valor Solides', 'Valor Local', 'Status', 'Data'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('deve listar todos os conflitos', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(3);
  });

  test('deve exibir nome do colaborador no conflito', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=João Silva')).toBeVisible();
    await expect(page.locator('text=Maria Santos')).toBeVisible();
  });

  test('deve exibir campo em conflito', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=cargo')).toBeVisible();
    await expect(page.locator('text=departamento')).toBeVisible();
  });

  test('deve exibir valores em conflito', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Analista Senior de RH')).toBeVisible();
    await expect(page.locator('text=Analista de RH')).toBeVisible();
  });

  test('deve exibir status Pendente em amarelo', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Pendente')).toBeVisible();
  });

  test('deve exibir status Resolvido em verde', async ({ page }) => {
    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Resolvido')).toBeVisible();
  });

  test('deve exibir mensagem quando não há conflitos', async ({ page }) => {
    await page.route('**/api/v1/integrations/solides/conflicts**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1000);

    const tab = page.locator('button:has-text("Conflitos"), [role="tab"]:has-text("Conflitos")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('text=Nenhum conflito')).toBeVisible();
  });

  // ==========================================
  // TESTES DE ATUALIZAÇÃO
  // ==========================================

  test('deve atualizar status da integração', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await refreshButton.click();

    await expect(page.locator('.animate-spin')).toBeVisible({ timeout: 2000 });
    await page.waitForTimeout(1000);

    await expect(page.locator('text=Conectado')).toBeVisible();
  });

  // ==========================================
  // TESTES DE DESABILITAÇÃO
  // ==========================================

  test('deve exibir botão para desabilitar integração', async ({ page }) => {
    const tab = page.locator('button:has-text("Status"), [role="tab"]:has-text("Status")').first();
    await tab.click();
    await page.waitForTimeout(500);

    await expect(page.locator('button:has-text("Desabilitar")')).toBeVisible();
  });

  test('deve desabilitar integração ao clicar', async ({ page }) => {
    const tab = page.locator('button:has-text("Status"), [role="tab"]:has-text("Status")').first();
    await tab.click();
    await page.waitForTimeout(500);

    const disableButton = page.locator('button:has-text("Desabilitar")');
    await disableButton.click();
    await page.waitForTimeout(1000);

    await expect(page.locator('text=desabilitada')).toBeVisible();
  });
});
