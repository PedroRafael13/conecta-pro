/**
 * Testes E2E - Configurações do Sistema
 *
 * Testa o módulo de configurações globais e settings por tenant
 * URL: /modulos/configuracoes/configuracoes-sistema
 */

import { test, expect } from '../fixtures';

// ==================== MOCKS ====================

const mockSystemConfigs = {
  items: [
    {
      id: 'config-001',
      chave: 'app.name',
      valor: 'Conecta PRO',
      descricao: 'Nome da aplicação',
      category: 'system',
      value_type: 'string',
      admin_only: false,
      cacheable: true,
      requires_restart: false,
    },
    {
      id: 'config-002',
      chave: 'app.logo_url',
      valor: 'https://cdn.conectamais.pro/logo.png',
      descricao: 'URL do logotipo',
      category: 'application',
      value_type: 'string',
      admin_only: false,
      cacheable: true,
      requires_restart: false,
    },
    {
      id: 'config-003',
      chave: 'timezone.default',
      valor: 'America/Sao_Paulo',
      descricao: 'Fuso horário padrão',
      category: 'system',
      value_type: 'string',
      admin_only: true,
      cacheable: true,
      requires_restart: true,
    },
    {
      id: 'config-004',
      chave: 'language.default',
      valor: 'pt-BR',
      descricao: 'Idioma padrão do sistema',
      category: 'system',
      value_type: 'string',
      admin_only: false,
      cacheable: true,
      requires_restart: false,
    },
    {
      id: 'config-005',
      chave: 'company.name',
      valor: 'Conecta Mais Tecnologia',
      descricao: 'Nome da empresa',
      category: 'application',
      value_type: 'string',
      admin_only: false,
      cacheable: false,
      requires_restart: false,
    },
    {
      id: 'config-006',
      chave: 'company.cnpj',
      valor: '12.345.678/0001-90',
      descricao: 'CNPJ da empresa',
      category: 'application',
      value_type: 'string',
      admin_only: false,
      cacheable: false,
      requires_restart: false,
    },
    {
      id: 'config-007',
      chave: 'api_key.external',
      valor: 'sk_live_1234567890abcdef',
      descricao: 'Chave API externa',
      category: 'integrations',
      value_type: 'string',
      admin_only: true,
      cacheable: false,
      requires_restart: false,
    },
    {
      id: 'config-008',
      chave: 'features.max_upload_size',
      valor: 10485760,
      descricao: 'Tamanho máximo de upload (bytes)',
      category: 'features',
      value_type: 'integer',
      admin_only: false,
      cacheable: true,
      requires_restart: false,
    },
  ],
  total: 8,
};

const mockTenantSettings = {
  items: [
    {
      id: 'setting-001',
      chave: 'theme.color_primary',
      valor: '#0066CC',
      descricao: 'Cor primária do tema',
      category: 'appearance',
      value_type: 'string',
      is_custom: true,
    },
    {
      id: 'setting-002',
      chave: 'notifications.email_enabled',
      valor: true,
      descricao: 'Notificações por email ativadas',
      category: 'notifications',
      value_type: 'boolean',
      is_custom: false,
    },
    {
      id: 'setting-003',
      chave: 'billing.currency',
      valor: 'BRL',
      descricao: 'Moeda padrão',
      category: 'billing',
      value_type: 'string',
      is_custom: false,
    },
  ],
  total: 3,
};

const mockTenants = {
  items: [
    {
      id: 'tenant-001',
      nome: 'Empresa Demo',
      email: 'demo@conectamais.pro',
      plan: 'pro',
      status: 'active',
    },
    {
      id: 'tenant-002',
      nome: 'Empresa Teste',
      email: 'teste@empresa.com',
      plan: 'starter',
      status: 'trial',
    },
  ],
  total: 2,
};

// ==================== TESTES ====================

test.describe('Configurações do Sistema', () => {
  test.beforeEach(async ({ page }) => {
    // Mock endpoints de configurações
    await page.route('**/api/v1/config/system-configs**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockSystemConfigs),
      });
    });

    await page.route('**/api/v1/config/tenants**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTenants),
      });
    });

    await page.route('**/api/v1/config/tenants/*/settings**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTenantSettings),
      });
    });

    // Navegar para a página
    await page.goto('/modulos/configuracoes/configuracoes-sistema', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  // ============ TESTES DE CARREGAMENTO ============

  test('deve carregar a página de configurações do sistema', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Configuracoes do Sistema');
    await expect(page.locator('text=Configs globais e settings por tenant')).toBeVisible();
  });

  test('deve exibir as abas Sistema e Tenant', async ({ page }) => {
    await expect(page.locator('button:has-text("Sistema")')).toBeVisible();
    await expect(page.locator('button:has-text("Tenant")')).toBeVisible();
  });

  test('deve carregar configurações do sistema na aba ativa', async ({ page }) => {
    // Verifica se as configurações são exibidas
    await expect(page.locator('code:has-text("app.name")')).toBeVisible();
    await expect(page.locator('code:has-text("app.logo_url")')).toBeVisible();
  });

  // ============ TESTES DE CONFIGURAÇÕES GERAIS ============

  test('deve exibir configuração de nome da aplicação', async ({ page }) => {
    await expect(page.locator('code:has-text("app.name")')).toBeVisible();
    await expect(page.locator('text=Nome da aplicação')).toBeVisible();
  });

  test('deve exibir configuração de fuso horário', async ({ page }) => {
    await expect(page.locator('code:has-text("timezone.default")')).toBeVisible();
    await expect(page.locator('text=Fuso horário padrão')).toBeVisible();
  });

  test('deve exibir configuração de idioma padrão', async ({ page }) => {
    await expect(page.locator('code:has-text("language.default")')).toBeVisible();
    await expect(page.locator('text=Idioma padrão')).toBeVisible();
  });

  test('deve exibir badge Admin para configurações restritas', async ({ page }) => {
    // timezone.default tem admin_only: true
    const timezoneRow = page.locator('div:has(code:has-text("timezone.default"))');
    await expect(timezoneRow.locator('text=Admin')).toBeVisible();
  });

  test('deve exibir badge Cache para configurações cacheáveis', async ({ page }) => {
    // app.name tem cacheable: true
    const appNameRow = page.locator('div:has(code:has-text("app.name"))');
    await expect(appNameRow.locator('text=Cache')).toBeVisible();
  });

  test('deve exibir badge Restart para configurações que requerem reinício', async ({ page }) => {
    // timezone.default tem requires_restart: true
    const timezoneRow = page.locator('div:has(code:has-text("timezone.default"))');
    await expect(timezoneRow.locator('text=Restart')).toBeVisible();
  });

  // ============ TESTES DE DADOS DA EMPRESA ============

  test('deve exibir configuração de nome da empresa', async ({ page }) => {
    await expect(page.locator('code:has-text("company.name")')).toBeVisible();
    await expect(page.locator('text=Nome da empresa')).toBeVisible();
  });

  test('deve exibir configuração de CNPJ da empresa', async ({ page }) => {
    await expect(page.locator('code:has-text("company.cnpj")')).toBeVisible();
    await expect(page.locator('text=CNPJ da empresa')).toBeVisible();
  });

  // ============ TESTES DE LOGOTIPO E BRANDING ============

  test('deve exibir configuração de URL do logotipo', async ({ page }) => {
    await expect(page.locator('code:has-text("app.logo_url")')).toBeVisible();
    await expect(page.locator('text=URL do logotipo')).toBeVisible();
  });

  // ============ TESTES DE SEGURANÇA E SENSIBILIDADE ============

  test('deve mascarar valores sensíveis como chaves API', async ({ page }) => {
    // api_key.external deve ter o valor mascarado
    const apiKeyRow = page.locator('div:has(code:has-text("api_key.external"))');
    await expect(apiKeyRow.locator('text=***')).toBeVisible();
  });

  test('deve exibir ícone de escudo para valores sensíveis', async ({ page }) => {
    const apiKeyRow = page.locator('div:has(code:has-text("api_key.external"))');
    await expect(apiKeyRow.locator('svg')).toBeVisible();
  });

  // ============ TESTES DE FILTROS E BUSCA ============

  test('deve permitir buscar configurações por termo', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por chave"]').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('app');
    await page.waitForTimeout(500);

    // Deve filtrar resultados
    await expect(page.locator('code:has-text("app.name")')).toBeVisible();
  });

  test('deve permitir filtrar por categoria', async ({ page }) => {
    const categorySelect = page.locator('button:has-text("Todas categorias")').first();
    await expect(categorySelect).toBeVisible();
  });

  test('deve ter opções de categoria no filtro', async ({ page }) => {
    await page.click('button:has-text("Todas categorias")');
    await expect(page.locator('text=Sistema')).toBeVisible();
    await expect(page.locator('text=Aplicacao')).toBeVisible();
    await expect(page.locator('text=Integracoes')).toBeVisible();
    await expect(page.locator('text=Seguranca')).toBeVisible();
  });

  // ============ TESTES DE AÇÕES ============

  test('deve exibir botão de atualizar configurações', async ({ page }) => {
    await expect(page.locator('button:has-text("Atualizar")').first()).toBeVisible();
  });

  test('deve exibir botão de nova configuração', async ({ page }) => {
    await expect(page.locator('button:has-text("Nova Config")')).toBeVisible();
  });

  test('deve exibir menu de ações para cada configuração', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await expect(firstMenu).toBeVisible();
  });

  // ============ TESTES DE ABA TENANT ============

  test('deve alternar para aba Tenant ao clicar', async ({ page }) => {
    await page.click('button:has-text("Tenant")');
    await page.waitForTimeout(1000);

    // Deve mostrar seletor de tenant
    await expect(page.locator('text=Selecione o Tenant')).toBeVisible();
  });

  test('deve exibir mensagem para selecionar tenant na aba Tenant', async ({ page }) => {
    await page.click('button:has-text("Tenant")');
    await page.waitForTimeout(1000);

    await expect(page.locator('text=Selecione um tenant')).toBeVisible();
    await expect(page.locator('text=Escolha um tenant acima para ver suas configuracoes')).toBeVisible();
  });

  test('deve ter seletor de tenant na aba Tenant', async ({ page }) => {
    await page.click('button:has-text("Tenant")');
    await page.waitForTimeout(1000);

    const tenantSelect = page.locator('button:has-text("Escolha um tenant...")');
    await expect(tenantSelect).toBeVisible();
  });

  // ============ TESTES DE AGRUPAMENTO ============

  test('deve agrupar configurações por categoria', async ({ page }) => {
    await expect(page.locator('text=Sistema')).toBeVisible();
    await expect(page.locator('text=Aplicacao')).toBeVisible();
  });

  test('deve exibir título de categoria para cada grupo', async ({ page }) => {
    const categoryTitles = page.locator('h2, h3, .card-title');
    await expect(categoryTitles.first()).toBeVisible();
  });

  // ============ TESTES DE ESTADO VAZIO ============

  test('deve exibir mensagem quando não houver configurações', async ({ page }) => {
    // Mock com lista vazia
    await page.route('**/api/v1/config/system-configs**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Nenhuma configuracao encontrada')).toBeVisible();
  });

  // ============ TESTES DE LOADING ============

  test('deve exibir indicador de carregamento durante fetch', async ({ page }) => {
    // A página já carregou, mas verificamos se o botão de atualizar funciona
    const refreshButton = page.locator('button:has-text("Atualizar")').first();
    await refreshButton.click();

    // Verifica se o estado de loading é aplicado
    await expect(page.locator('[class*="animate-spin"]')).toBeVisible();
  });

  // ============ TESTES DE ERRO ============

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await page.route('**/api/v1/config/system-configs**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Erro ao carregar configuracoes')).toBeVisible();
    await expect(page.locator('button:has-text("Tentar novamente")')).toBeVisible();
  });
});
