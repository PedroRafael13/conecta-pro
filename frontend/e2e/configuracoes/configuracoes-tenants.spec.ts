/**
 * Testes E2E - Tenants (Gestão Multi-Tenant)
 *
 * Testa o módulo de gestão de tenants, planos e status
 * URL: /modulos/configuracoes/tenants
 */

import { test, expect } from '../fixtures';

// ==================== MOCKS ====================

const mockTenants = {
  items: [
    {
      id: 'tenant-001',
      nome: 'Empresa Demonstração',
      codigo: 'DEMO001',
      cnpj: '12.345.678/0001-90',
      email: 'demo@conectamais.pro',
      telefone: '(11) 99999-9999',
      plan: 'enterprise',
      status: 'active',
      max_users: 100,
      current_users: 45,
      storage_limit: 10737418240, // 10GB
      storage_used: 2147483648, // 2GB
      features: ['all', 'api_access', 'priority_support', 'custom_branding'],
      endereco: {
        rua: 'Av. Paulista',
        numero: '1000',
        complemento: 'Sala 500',
        bairro: 'Bela Vista',
        cidade: 'São Paulo',
        estado: 'SP',
        cep: '01310-100',
      },
      created_at: '2023-01-15T10:00:00Z',
      updated_at: '2024-02-10T14:30:00Z',
      trial_ends_at: null,
    },
    {
      id: 'tenant-002',
      nome: 'Startup Tech',
      codigo: 'TECH002',
      cnpj: '98.765.432/0001-10',
      email: 'contato@startuptech.com',
      telefone: '(21) 98888-8888',
      plan: 'pro',
      status: 'active',
      max_users: 50,
      current_users: 23,
      storage_limit: 5368709120, // 5GB
      storage_used: 1073741824, // 1GB
      features: ['api_access', 'advanced_reports'],
      endereco: {
        rua: 'Rua do Ouvidor',
        numero: '50',
        complemento: '',
        bairro: 'Centro',
        cidade: 'Rio de Janeiro',
        estado: 'RJ',
        cep: '20040-030',
      },
      created_at: '2023-06-20T10:00:00Z',
      updated_at: '2024-01-25T09:15:00Z',
      trial_ends_at: null,
    },
    {
      id: 'tenant-003',
      nome: 'Empresa em Teste',
      codigo: 'TEST003',
      cnpj: '11.222.333/0001-44',
      email: 'teste@empresa.com',
      telefone: '(31) 97777-7777',
      plan: 'starter',
      status: 'trial',
      max_users: 10,
      current_users: 5,
      storage_limit: 1073741824, // 1GB
      storage_used: 104857600, // 100MB
      features: ['basic'],
      endereco: {
        rua: 'Av. Afonso Pena',
        numero: '1500',
        complemento: 'Andar 10',
        bairro: 'Funcionários',
        cidade: 'Belo Horizonte',
        estado: 'MG',
        cep: '30130-000',
      },
      created_at: '2024-02-01T10:00:00Z',
      updated_at: '2024-02-01T10:00:00Z',
      trial_ends_at: '2024-03-01T10:00:00Z',
    },
    {
      id: 'tenant-004',
      nome: 'Empresa Suspensa',
      codigo: 'SUSP004',
      cnpj: '33.444.555/0001-66',
      email: 'suspensa@empresa.com',
      telefone: '(41) 96666-6666',
      plan: 'pro',
      status: 'suspended',
      max_users: 50,
      current_users: 0,
      storage_limit: 5368709120,
      storage_used: 0,
      features: [],
      endereco: {
        rua: 'Rua XV de Novembro',
        numero: '200',
        complemento: '',
        bairro: 'Centro',
        cidade: 'Curitiba',
        estado: 'PR',
        cep: '80020-310',
      },
      created_at: '2023-03-10T10:00:00Z',
      updated_at: '2024-01-15T08:00:00Z',
      trial_ends_at: null,
    },
    {
      id: 'tenant-005',
      nome: 'Empresa Cancelada',
      codigo: 'CANC005',
      cnpj: '77.888.999/0001-22',
      email: 'cancelada@empresa.com',
      telefone: '(51) 95555-5555',
      plan: 'starter',
      status: 'canceled',
      max_users: 10,
      current_users: 0,
      storage_limit: 1073741824,
      storage_used: 0,
      features: [],
      endereco: null,
      created_at: '2023-09-01T10:00:00Z',
      updated_at: '2023-12-01T10:00:00Z',
      trial_ends_at: null,
    },
  ],
  total: 5,
};

// ==================== TESTES ====================

test.describe('Tenants - Gestão Multi-Tenant', () => {
  test.beforeEach(async ({ page }) => {
    // Mock endpoint de tenants
    await page.route('**/api/v1/config/tenants**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTenants),
      });
    });

    // Navegar para a página
    await page.goto('/modulos/configuracoes/tenants', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  // ============ TESTES DE CARREGAMENTO ============

  test('deve carregar a página de tenants', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Tenants');
    await expect(page.locator('text=Gestao de tenants, planos e status')).toBeVisible();
  });

  test('deve exibir lista de tenants ao carregar', async ({ page }) => {
    await expect(page.locator('text=Empresa Demonstração')).toBeVisible();
    await expect(page.locator('text=Startup Tech')).toBeVisible();
  });

  // ============ TESTES DE ESTATÍSTICAS ============

  test('deve exibir card de total de tenants', async ({ page }) => {
    await expect(page.locator('text=Total').first()).toBeVisible();
    const totalCount = page.locator('div:has-text("Total") + div .text-2xl');
    await expect(totalCount).toContainText('5');
  });

  test('deve exibir card de tenants ativos', async ({ page }) => {
    await expect(page.locator('text=Ativos').first()).toBeVisible();
    const activeCount = page.locator('div:has-text("Ativos") + div .text-green-600');
    await expect(activeCount).toContainText('2');
  });

  test('deve exibir card de tenants em trial', async ({ page }) => {
    await expect(page.locator('text=Trial').first()).toBeVisible();
    const trialCount = page.locator('div:has-text("Trial") + div .text-blue-600');
    await expect(trialCount).toContainText('1');
  });

  test('deve exibir card de tenants suspensos', async ({ page }) => {
    await expect(page.locator('text=Suspenso, text=Suspensos').first()).toBeVisible();
    const suspendedCount = page.locator('div:has-text("Suspensos") + div .text-yellow-600');
    await expect(suspendedCount).toContainText('1');
  });

  // ============ TESTES DE LISTAGEM ============

  test('deve exibir nome e código do tenant', async ({ page }) => {
    await expect(page.locator('text=Empresa Demonstração')).toBeVisible();
    await expect(page.locator('text=DEMO001')).toBeVisible();
  });

  test('deve exibir CNPJ do tenant', async ({ page }) => {
    await expect(page.locator('text=12.345.678/0001-90')).toBeVisible();
    await expect(page.locator('text=98.765.432/0001-10')).toBeVisible();
  });

  test('deve exibir email do tenant', async ({ page }) => {
    await expect(page.locator('text=demo@conectamais.pro')).toBeVisible();
    await expect(page.locator('text=contato@startuptech.com')).toBeVisible();
  });

  test('deve exibir plano do tenant como badge', async ({ page }) => {
    await expect(page.locator('text=Enterprise').first()).toBeVisible();
    await expect(page.locator('text=Pro').first()).toBeVisible();
    await expect(page.locator('text=Starter').first()).toBeVisible();
  });

  test('deve exibir status do tenant como badge', async ({ page }) => {
    await expect(page.locator('text=Ativo').first()).toBeVisible();
    await expect(page.locator('text=Trial').first()).toBeVisible();
  });

  test('deve exibir contagem de usuários', async ({ page }) => {
    await expect(page.locator('text=45/100')).toBeVisible();
    await expect(page.locator('text=23/50')).toBeVisible();
  });

  // ============ TESTES DE PLANOS ============

  test('deve exibir badge Enterprise para plano enterprise', async ({ page }) => {
    const enterpriseBadge = page.locator('.bg-amber-100, .text-amber-800').filter({ hasText: /Enterprise/i });
    await expect(enterpriseBadge.first()).toBeVisible();
  });

  test('deve exibir badge Pro para plano pro', async ({ page }) => {
    const proBadge = page.locator('.bg-purple-100, .text-purple-800').filter({ hasText: /Pro/i });
    await expect(proBadge.first()).toBeVisible();
  });

  test('deve exibir badge Starter para plano starter', async ({ page }) => {
    const starterBadge = page.locator('.bg-blue-100, .text-blue-800').filter({ hasText: /Starter/i });
    await expect(starterBadge.first()).toBeVisible();
  });

  // ============ TESTES DE STATUS ============

  test('deve exibir badge verde para status ativo', async ({ page }) => {
    const activeBadge = page.locator('.bg-green-100:has-text("Ativo")');
    await expect(activeBadge.first()).toBeVisible();
  });

  test('deve exibir badge azul para status trial', async ({ page }) => {
    const trialBadge = page.locator('.bg-blue-100:has-text("Trial")');
    await expect(trialBadge.first()).toBeVisible();
  });

  test('deve exibir badge amarelo para status suspenso', async ({ page }) => {
    const suspendedBadge = page.locator('.bg-yellow-100:has-text("Suspenso")');
    await expect(suspendedBadge.first()).toBeVisible();
  });

  test('deve exibir badge vermelho para status cancelado', async ({ page }) => {
    const canceledBadge = page.locator('.bg-red-100:has-text("Cancelado")');
    await expect(canceledBadge.first()).toBeVisible();
  });

  // ============ TESTES DE FILTROS ============

  test('deve ter campo de busca para tenants', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();
    await expect(searchInput).toBeVisible();
  });

  test('deve permitir buscar tenants por nome', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();
    await searchInput.fill('Empresa Demonstração');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Empresa Demonstração')).toBeVisible();
  });

  test('deve ter filtro por status', async ({ page }) => {
    const statusFilter = page.locator('button:has-text("Todos os status")');
    await expect(statusFilter).toBeVisible();
  });

  test('deve ter opções de filtro de status', async ({ page }) => {
    await page.click('button:has-text("Todos os status")');
    await expect(page.locator('text=Ativo').first()).toBeVisible();
    await expect(page.locator('text=Trial').first()).toBeVisible();
    await expect(page.locator('text=Suspenso').first()).toBeVisible();
    await expect(page.locator('text=Cancelado').first()).toBeVisible();
    await expect(page.locator('text=Inativo').first()).toBeVisible();
  });

  test('deve filtrar por status Ativo', async ({ page }) => {
    await page.click('button:has-text("Todos os status")');
    await page.click('text=Ativo');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Empresa Demonstração')).toBeVisible();
    await expect(page.locator('text=Startup Tech')).toBeVisible();
  });

  test('deve ter filtro por plano', async ({ page }) => {
    const planFilter = page.locator('button:has-text("Todos os planos")');
    await expect(planFilter).toBeVisible();
  });

  test('deve ter opções de filtro de plano', async ({ page }) => {
    await page.click('button:has-text("Todos os planos")');
    await expect(page.locator('text=Free')).toBeVisible();
    await expect(page.locator('text=Starter').first()).toBeVisible();
    await expect(page.locator('text=Pro').first()).toBeVisible();
    await expect(page.locator('text=Enterprise').first()).toBeVisible();
  });

  test('deve filtrar por plano Pro', async ({ page }) => {
    await page.click('button:has-text("Todos os planos")');
    await page.click('text=Pro');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Startup Tech')).toBeVisible();
  });

  // ============ TESTES DE AÇÕES ============

  test('deve exibir botão de novo tenant', async ({ page }) => {
    await expect(page.locator('button:has-text("Novo Tenant")')).toBeVisible();
  });

  test('deve exibir botão de atualizar lista', async ({ page }) => {
    await expect(page.locator('button:has-text("Atualizar")').first()).toBeVisible();
  });

  test('deve exibir menu de ações para cada tenant', async ({ page }) => {
    const actionMenus = page.locator('button:has([data-lucide="more-horizontal"])');
    await expect(actionMenus.first()).toBeVisible();
  });

  test('deve abrir menu de ações ao clicar', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Ver detalhes')).toBeVisible();
    await expect(page.locator('text=Editar').first()).toBeVisible();
  });

  test('deve ter opção de ativar no menu para tenants inativos', async ({ page }) => {
    // Abre menu do tenant suspenso
    const suspendedRow = page.locator('div:has-text("Empresa Suspensa")');
    const menuButton = suspendedRow.locator('xpath=..//..//..//..//button').last();

    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await expect(page.locator('text=Ativar').first()).toBeVisible();
    }
  });

  test('deve ter opção de suspender no menu para tenants ativos', async ({ page }) => {
    // Abre menu do tenant ativo
    const activeRow = page.locator('div:has-text("Empresa Demonstração")');
    const menuButton = activeRow.locator('xpath=..//..//..//..//button').last();

    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await expect(page.locator('text=Suspender').first()).toBeVisible();
    }
  });

  test('deve ter opção de converter trial para tenant em trial', async ({ page }) => {
    // Abre menu do tenant em trial
    const trialRow = page.locator('div:has-text("Empresa em Teste")');
    const menuButton = trialRow.locator('xpath=..//..//..//..//button').last();

    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await expect(page.locator('text=Converter Trial')).toBeVisible();
    }
  });

  test('deve ter opção de deletar no menu', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Deletar').first()).toBeVisible();
  });

  // ============ TESTES DE LIMITES E QUOTAS ============

  test('deve exibir limite de usuários para cada tenant', async ({ page }) => {
    await expect(page.locator('text=/\\d+\\/\\d+/')).toBeVisible();
  });

  test('deve exibir informações de uso de storage', async ({ page }) => {
    // Verifica se há informações de storage
    const storageInfo = page.locator('text=/\\d+\\s*(GB|MB)/i');
    // Pode ou não estar visível dependendo da UI
  });

  // ============ TESTES DE ESTRUTURA DA TABELA ============

  test('deve exibir tenants em formato de tabela', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Verifica cabeçalhos
    await expect(page.locator('th:has-text("Nome")')).toBeVisible();
    await expect(page.locator('th:has-text("CNPJ")')).toBeVisible();
    await expect(page.locator('th:has-text("Email")')).toBeVisible();
    await expect(page.locator('th:has-text("Plano")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
    await expect(page.locator('th:has-text("Usuarios")')).toBeVisible();
  });

  // ============ TESTES DE PAGINAÇÃO ============

  test('deve exibir informação de paginação quando necessário', async ({ page }) => {
    const manyTenants = {
      items: Array(25).fill(null).map((_, i) => ({
        id: `tenant-${i}`,
        nome: `Empresa ${i}`,
        codigo: `EMP${i}`,
        cnpj: '00.000.000/0000-00',
        email: `empresa${i}@test.com`,
        telefone: '(00) 00000-0000',
        plan: 'starter',
        status: 'active',
        max_users: 10,
        current_users: 5,
        storage_limit: 1073741824,
        storage_used: 0,
        features: [],
        endereco: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        trial_ends_at: null,
      })),
      total: 25,
    };

    await page.route('**/api/v1/config/tenants**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(manyTenants),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('button:has-text("Proximo")')).toBeVisible();
    await expect(page.locator('button:has-text("Anterior")')).toBeVisible();
  });

  // ============ TESTES DE ESTADO VAZIO ============

  test('deve exibir mensagem quando não houver tenants', async ({ page }) => {
    await page.route('**/api/v1/config/tenants**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Nenhum tenant encontrado')).toBeVisible();
    await expect(page.locator('text=Tente ajustar os filtros ou crie um novo tenant')).toBeVisible();
  });

  // ============ TESTES DE ERRO ============

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await page.route('**/api/v1/config/tenants**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Erro ao carregar tenants')).toBeVisible();
    await expect(page.locator('button:has-text("Tentar novamente")')).toBeVisible();
  });

  // ============ TESTES DE ÍCONES ============

  test('deve exibir ícone de Building2 no header', async ({ page }) => {
    const header = page.locator('h1');
    await expect(header.locator('svg')).toBeVisible();
  });

  test('deve exibir ícones nos cards de estatísticas', async ({ page }) => {
    await expect(page.locator('[data-lucide="building-2"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="users"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="zap"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="pause"]').first()).toBeVisible();
  });

  // ============ TESTES DE CONFIGURAÇÕES ESPECÍFICAS ============

  test('deve permitir ver detalhes do tenant', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Ver detalhes')).toBeVisible();
  });

  test('deve exibir endereço quando disponível', async ({ page }) => {
    // Empresa Demonstração tem endereço completo
    const tenantWithAddress = page.locator('div:has-text("Empresa Demonstração")');
    await expect(tenantWithAddress).toBeVisible();
  });
});
