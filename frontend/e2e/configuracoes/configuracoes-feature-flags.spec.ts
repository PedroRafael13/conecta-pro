/**
 * Testes E2E - Feature Flags
 *
 * Testa o módulo de controle de features e rollout gradual
 * URL: /modulos/configuracoes/feature-flags
 */

import { test, expect } from '../fixtures';

// ==================== MOCKS ====================

const mockFeatureFlags = {
  items: [
    {
      id: 'flag-001',
      nome: 'Novo Dashboard',
      codigo: 'NEW_DASHBOARD',
      descricao: 'Novo design do dashboard com gráficos interativos',
      ativo: true,
      flag_type: 'boolean',
      category: 'features',
      rollout_percentage: 100,
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-02-01T14:30:00Z',
    },
    {
      id: 'flag-002',
      nome: 'Relatórios Avançados',
      codigo: 'ADVANCED_REPORTS',
      descricao: 'Relatórios com filtros avançados e exportação',
      ativo: true,
      flag_type: 'gradual',
      category: 'features',
      rollout_percentage: 50,
      created_at: '2024-01-20T10:00:00Z',
      updated_at: '2024-02-05T09:15:00Z',
    },
    {
      id: 'flag-003',
      nome: 'Integração WhatsApp',
      codigo: 'WHATSAPP_INTEGRATION',
      descricao: 'Envio de notificações via WhatsApp Business API',
      ativo: false,
      flag_type: 'boolean',
      category: 'integrations',
      rollout_percentage: 0,
      created_at: '2024-01-25T10:00:00Z',
      updated_at: '2024-01-25T10:00:00Z',
    },
    {
      id: 'flag-004',
      nome: 'Modo Escuro',
      codigo: 'DARK_MODE',
      descricao: 'Tema escuro para toda a aplicação',
      ativo: true,
      flag_type: 'percentage',
      category: 'ui',
      rollout_percentage: 75,
      created_at: '2024-02-01T10:00:00Z',
      updated_at: '2024-02-10T16:45:00Z',
    },
    {
      id: 'flag-005',
      nome: 'Cache de Consultas',
      codigo: 'QUERY_CACHE',
      descricao: 'Cache inteligente para consultas frequentes',
      ativo: true,
      flag_type: 'boolean',
      category: 'performance',
      rollout_percentage: 100,
      created_at: '2024-02-05T10:00:00Z',
      updated_at: '2024-02-12T11:20:00Z',
    },
    {
      id: 'flag-006',
      nome: 'Manutenção Programada',
      codigo: 'MAINTENANCE_MODE',
      descricao: 'Ativa modo de manutenção do sistema',
      ativo: false,
      flag_type: 'boolean',
      category: 'maintenance',
      rollout_percentage: 0,
      created_at: '2024-02-10T10:00:00Z',
      updated_at: '2024-02-10T10:00:00Z',
    },
    {
      id: 'flag-007',
      nome: 'API v2 Experimental',
      codigo: 'API_V2_EXPERIMENTAL',
      descricao: 'Nova versão da API em fase de testes',
      ativo: true,
      flag_type: 'whitelist',
      category: 'experimental',
      rollout_percentage: 10,
      created_at: '2024-02-15T10:00:00Z',
      updated_at: '2024-02-20T13:10:00Z',
    },
  ],
  total: 7,
};

// ==================== TESTES ====================

test.describe('Feature Flags', () => {
  test.beforeEach(async ({ page }) => {
    // Mock endpoint de feature flags
    await page.route('**/api/v1/config/feature-flags**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockFeatureFlags),
      });
    });

    // Navegar para a página
    await page.goto('/modulos/configuracoes/feature-flags', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  // ============ TESTES DE CARREGAMENTO ============

  test('deve carregar a página de feature flags', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Feature Flags');
    await expect(page.locator('text=Controle de features e rollout gradual')).toBeVisible();
  });

  test('deve exibir lista de feature flags ao carregar', async ({ page }) => {
    await expect(page.locator('text=Novo Dashboard')).toBeVisible();
    await expect(page.locator('text=Relatórios Avançados')).toBeVisible();
  });

  // ============ TESTES DE ESTATÍSTICAS ============

  test('deve exibir card de total de flags', async ({ page }) => {
    const totalCard = page.locator('div:has-text("Total"):has(~ div .text-2xl)').first();
    await expect(totalCard).toBeVisible();
  });

  test('deve exibir card de flags ativas', async ({ page }) => {
    await expect(page.locator('text=Ativas').first()).toBeVisible();
    await expect(page.locator('div:has-text("Ativas") + div .text-green-600')).toBeVisible();
  });

  test('deve exibir card de flags em rollout', async ({ page }) => {
    await expect(page.locator('text=Em Rollout').first()).toBeVisible();
    await expect(page.locator('div:has-text("Em Rollout") + div .text-orange-600')).toBeVisible();
  });

  test('deve exibir card de flags desabilitadas', async ({ page }) => {
    await expect(page.locator('text=Desabilitadas').first()).toBeVisible();
  });

  test('deve exibir contagem correta de flags ativas', async ({ page }) => {
    // 5 flags ativas no mock
    const activeCount = page.locator('div:has-text("Ativas") + div .text-2xl');
    await expect(activeCount).toContainText('5');
  });

  // ============ TESTES DE LISTAGEM ============

  test('deve exibir nome e código da feature flag', async ({ page }) => {
    await expect(page.locator('text=Novo Dashboard')).toBeVisible();
    await expect(page.locator('text=NEW_DASHBOARD')).toBeVisible();
  });

  test('deve exibir descrição da feature flag', async ({ page }) => {
    await expect(page.locator('text=Novo design do dashboard')).toBeVisible();
  });

  test('deve exibir tipo da feature flag como badge', async ({ page }) => {
    await expect(page.locator('text=boolean').first()).toBeVisible();
    await expect(page.locator('text=gradual')).toBeVisible();
  });

  test('deve exibir categoria da feature flag', async ({ page }) => {
    await expect(page.locator('text=Funcionalidades').first()).toBeVisible();
    await expect(page.locator('text=Integracoes').first()).toBeVisible();
  });

  // ============ TESTES DE STATUS ============

  test('deve exibir status Ativa para flags habilitadas', async ({ page }) => {
    const activeFlag = page.locator('div:has-text("Novo Dashboard")');
    await expect(activeFlag.locator('xpath=..//..//..//..//..//span[contains(text(), "Ativ")]')).toBeVisible();
  });

  test('deve exibir status Inativa para flags desabilitadas', async ({ page }) => {
    const inactiveFlag = page.locator('div:has-text("Integração WhatsApp")');
    await expect(inactiveFlag.locator('xpath=..//..//..//..//..//span[contains(text(), "Inativ")]')).toBeVisible();
  });

  test('deve exibir badge verde para flags ativas', async ({ page }) => {
    const greenBadges = page.locator('.bg-green-100, .text-green-800');
    await expect(greenBadges.first()).toBeVisible();
  });

  // ============ TESTES DE ROLLOUT ============

  test('deve exibir barra de progresso de rollout', async ({ page }) => {
    const progressBars = page.locator('[role="progressbar"], .progress, [class*="progress"]');
    await expect(progressBars.first()).toBeVisible();
  });

  test('deve exibir porcentagem de rollout', async ({ page }) => {
    await expect(page.locator('text=100%')).toBeVisible();
    await expect(page.locator('text=50%')).toBeVisible();
    await expect(page.locator('text=75%')).toBeVisible();
  });

  test('deve exibir rollout 0% para flags desabilitadas', async ({ page }) => {
    await expect(page.locator('text=0%').first()).toBeVisible();
  });

  // ============ TESTES DE FILTROS ============

  test('deve ter campo de busca para feature flags', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();
    await expect(searchInput).toBeVisible();
  });

  test('deve permitir buscar feature flags por nome', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();
    await searchInput.fill('Dashboard');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Novo Dashboard')).toBeVisible();
  });

  test('deve ter filtro por status', async ({ page }) => {
    const statusFilter = page.locator('button:has-text("Todos")').first();
    await expect(statusFilter).toBeVisible();
  });

  test('deve ter opções de filtro de status', async ({ page }) => {
    await page.click('button:has-text("Todos"):has(~ button, ~ div)');
    await expect(page.locator('text=Ativas')).toBeVisible();
    await expect(page.locator('text=Inativas')).toBeVisible();
  });

  test('deve ter filtro por categoria', async ({ page }) => {
    const categoryFilter = page.locator('button:has-text("Todas categorias")');
    await expect(categoryFilter).toBeVisible();
  });

  test('deve ter opções de categoria no filtro', async ({ page }) => {
    await page.click('button:has-text("Todas categorias")');
    await expect(page.locator('text=Funcionalidades')).toBeVisible();
    await expect(page.locator('text=Experimental')).toBeVisible();
    await expect(page.locator('text=Manutencao')).toBeVisible();
    await expect(page.locator('text=Performance')).toBeVisible();
    await expect(page.locator('text=Interface')).toBeVisible();
    await expect(page.locator('text=Integracoes')).toBeVisible();
  });

  test('deve filtrar por categoria Funcionalidades', async ({ page }) => {
    await page.click('button:has-text("Todas categorias")');
    await page.click('text=Funcionalidades');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Novo Dashboard')).toBeVisible();
    await expect(page.locator('text=Relatórios Avançados')).toBeVisible();
  });

  test('deve filtrar por categoria Integrações', async ({ page }) => {
    await page.click('button:has-text("Todas categorias")');
    await page.click('text=Integracoes');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Integração WhatsApp')).toBeVisible();
  });

  // ============ TESTES DE AÇÕES ============

  test('deve exibir botão de nova flag', async ({ page }) => {
    await expect(page.locator('button:has-text("Nova Flag")')).toBeVisible();
  });

  test('deve exibir botão de atualizar lista', async ({ page }) => {
    await expect(page.locator('button:has-text("Atualizar")').first()).toBeVisible();
  });

  test('deve exibir menu de ações para cada flag', async ({ page }) => {
    const actionMenus = page.locator('button:has([data-lucide="more-horizontal"])');
    await expect(actionMenus.first()).toBeVisible();
  });

  test('deve abrir menu de ações ao clicar', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Detalhes')).toBeVisible();
    await expect(page.locator('text=Editar')).toBeVisible();
  });

  test('deve ter opção de habilitar/desabilitar no menu', async ({ page }) => {
    // Abre menu de uma flag ativa
    const activeFlagMenu = page.locator('div:has-text("Novo Dashboard") + div button, div:has-text("Novo Dashboard") ~ div button').first();
    if (await activeFlagMenu.isVisible().catch(() => false)) {
      await activeFlagMenu.click();
      await expect(page.locator('text=Desabilitar, text=Habilitar').first()).toBeVisible();
    }
  });

  test('deve ter opção de deletar no menu', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Deletar').first()).toBeVisible();
  });

  // ============ TESTES DE TIPOS DE FLAG ============

  test('deve exibir badge boolean para flags booleanas', async ({ page }) => {
    await expect(page.locator('text=boolean').first()).toBeVisible();
  });

  test('deve exibir badge gradual para flags graduais', async ({ page }) => {
    await expect(page.locator('text=gradual').first()).toBeVisible();
  });

  test('deve exibir badge percentage para flags percentuais', async ({ page }) => {
    await expect(page.locator('text=percentage').first()).toBeVisible();
  });

  test('deve exibir badge whitelist para flags whitelist', async ({ page }) => {
    await expect(page.locator('text=whitelist').first()).toBeVisible();
  });

  // ============ TESTES DE PAGINAÇÃO ============

  test('deve exibir informação de paginação quando necessário', async ({ page }) => {
    // Com 7 itens e pageSize 20, não deve mostrar paginação
    // Vamos mockar mais dados para testar
    const manyFlags = {
      items: Array(25).fill(null).map((_, i) => ({
        id: `flag-${i}`,
        nome: `Feature ${i}`,
        codigo: `FEATURE_${i}`,
        descricao: `Descrição da feature ${i}`,
        ativo: i % 2 === 0,
        flag_type: 'boolean',
        category: 'features',
        rollout_percentage: 100,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      })),
      total: 25,
    };

    await page.route('**/api/v1/config/feature-flags**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(manyFlags),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('button:has-text("Proximo")')).toBeVisible();
    await expect(page.locator('button:has-text("Anterior")')).toBeVisible();
  });

  // ============ TESTES DE ESTADO VAZIO ============

  test('deve exibir mensagem quando não houver feature flags', async ({ page }) => {
    await page.route('**/api/v1/config/feature-flags**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Nenhuma feature flag encontrada')).toBeVisible();
    await expect(page.locator('text=Crie uma nova feature flag para comecar')).toBeVisible();
  });

  // ============ TESTES DE ERRO ============

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await page.route('**/api/v1/config/feature-flags**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Erro ao carregar feature flags')).toBeVisible();
  });

  // ============ TESTES DE ORDENAÇÃO ============

  test('deve exibir flags em formato de tabela', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Verifica cabeçalhos
    await expect(page.locator('th:has-text("Nome / Codigo")')).toBeVisible();
    await expect(page.locator('th:has-text("Tipo")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
    await expect(page.locator('th:has-text("Rollout")')).toBeVisible();
    await expect(page.locator('th:has-text("Categoria")')).toBeVisible();
  });

  // ============ TESTES DE ÍCONES ============

  test('deve exibir ícone de ToggleRight no header', async ({ page }) => {
    const header = page.locator('h1');
    await expect(header.locator('svg')).toBeVisible();
  });

  test('deve exibir ícones nos cards de estatísticas', async ({ page }) => {
    await expect(page.locator('[data-lucide="toggle-right"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="power"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="zap"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="ban"]').first()).toBeVisible();
  });
});
