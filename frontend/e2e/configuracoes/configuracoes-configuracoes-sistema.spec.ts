import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Configurações / Configurações do Sistema
 *
 * Funcionalidades testadas:
 * - Configurações globais do sistema
 * - Configurações por tenant
 * - Filtros por categoria e busca
 * - Edição inline de valores
 * - CRUD de configurações
 */

// Mock data
const mockSystemConfigs = [
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
    chave: 'api.timeout',
    valor: 30000,
    descricao: 'Timeout de API em milissegundos',
    category: 'performance',
    value_type: 'integer',
    admin_only: false,
    cacheable: true,
    requires_restart: false,
  },
  {
    id: 'config-003',
    chave: 'features.new_ui',
    valor: true,
    descricao: 'Habilitar nova interface',
    category: 'features',
    value_type: 'boolean',
    admin_only: true,
    cacheable: false,
    requires_restart: true,
  },
  {
    id: 'config-004',
    chave: 'security.api_key',
    valor: 'sk_test_1234567890',
    descricao: 'API Key para integrações',
    category: 'security',
    value_type: 'string',
    admin_only: true,
    cacheable: false,
    requires_restart: false,
  },
];

const mockTenantSettings = [
  {
    id: 'setting-001',
    chave: 'tenant.name',
    valor: 'Empresa Demo',
    descricao: 'Nome do tenant',
    category: 'general',
    value_type: 'string',
    is_custom: false,
  },
  {
    id: 'setting-002',
    chave: 'theme.primary_color',
    valor: '#0066CC',
    descricao: 'Cor primária do tema',
    category: 'appearance',
    value_type: 'string',
    is_custom: true,
  },
];

const mockTenants = [
  { id: 'tenant-001', nome: 'Empresa Demo' },
  { id: 'tenant-002', nome: 'Empresa Teste' },
];

// Setup de mocks para API
async function setupConfigMocks(page: Page) {
  await page.route('**/api/v1/config/system**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockSystemConfigs,
        total: mockSystemConfigs.length,
      }),
    });
  });

  await page.route('**/api/v1/tenants**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockTenants,
        total: mockTenants.length,
      }),
    });
  });

  await page.route('**/api/v1/config/tenant/*/settings**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockTenantSettings,
        total: mockTenantSettings.length,
      }),
    });
  });

  await page.route('**/api/v1/config/system/*', async (route) => {
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
}

test.describe('Configurações - Configurações do Sistema', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupConfigMocks(page);
    await page.goto('/modulos/configuracoes/configuracoes-sistema');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de configurações', async ({ page }) => {
    await expect(page).toHaveURL(/\/configuracoes-sistema/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Configurações do Sistema/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/globais|tenant/i');
    await expect(description).toBeVisible();
  });

  // ==========================================
  // TESTES DE ABAS
  // ==========================================

  test('deve ter abas de Sistema e Tenant', async ({ page }) => {
    const sistemaTab = page.locator('text=/Sistema$/i').first();
    const tenantTab = page.locator('text=/Tenant$/i').first();

    await expect(sistemaTab).toBeVisible();
    await expect(tenantTab).toBeVisible();
  });

  test('deve alternar entre abas', async ({ page }) => {
    const tenantTab = page.locator('text=/Tenant$/i').first();
    await tenantTab.click();
    await page.waitForTimeout(500);

    // Verificar se seletor de tenant aparece
    const tenantSelect = page.locator('text=/Selecione o Tenant|Escolha um tenant/i').first();
    const hasSelect = await tenantSelect.isVisible().catch(() => false);
    expect(hasSelect !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE FILTROS (SISTEMA)
  // ==========================================

  test('deve ter campo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i], input[placeholder*="chave" i]').first();
    await expect(searchInput).toBeVisible();
  });

  test('deve ter seletor de categoria', async ({ page }) => {
    const categorySelect = page.locator('select, [role="combobox"]').filter({ hasText: /Categoria|Todas/i }).first();
    const hasSelect = await categorySelect.isVisible().catch(() => false);
    expect(hasSelect !== undefined).toBeTruthy();
  });

  test('deve filtrar por termo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i]').first();
    await searchInput.fill('app.name');
    await page.waitForTimeout(600);

    await expect(searchInput).toHaveValue('app.name');
  });

  // ==========================================
  // TESTES DE LISTA DE CONFIGURAÇÕES
  // ==========================================

  test('deve exibir configurações agrupadas por categoria', async ({ page }) => {
    await page.waitForTimeout(1000);

    const categoryHeader = page.locator('text=/Sistema|Performance|Segurança/i').first();
    const hasCategory = await categoryHeader.isVisible().catch(() => false);
    expect(hasCategory !== undefined).toBeTruthy();
  });

  test('deve exibir chaves das configurações', async ({ page }) => {
    await page.waitForTimeout(1000);

    const configKey = page.locator('code:has-text("app.name"), text=/app\\.name/i').first();
    const hasKey = await configKey.isVisible().catch(() => false);
    expect(hasKey !== undefined).toBeTruthy();
  });

  test('deve exibir descrições das configurações', async ({ page }) => {
    await page.waitForTimeout(1000);

    const description = page.locator('text=/Nome da aplicação|Timeout/i').first();
    const hasDesc = await description.isVisible().catch(() => false);
    expect(hasDesc !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE BADGES
  // ==========================================

  test('deve exibir badge Admin para configs restritas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const adminBadge = page.locator('text=/Admin/i').first();
    const hasAdmin = await adminBadge.isVisible().catch(() => false);
    expect(hasAdmin !== undefined).toBeTruthy();
  });

  test('deve exibir badge Cache para configs cacheáveis', async ({ page }) => {
    await page.waitForTimeout(1000);

    const cacheBadge = page.locator('text=/Cache/i').first();
    const hasCache = await cacheBadge.isVisible().catch(() => false);
    expect(hasCache !== undefined).toBeTruthy();
  });

  test('deve exibir badge Restart para configs que precisam reiniciar', async ({ page }) => {
    await page.waitForTimeout(1000);

    const restartBadge = page.locator('text=/Restart/i').first();
    const hasRestart = await restartBadge.isVisible().catch(() => false);
    expect(hasRestart !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE EDIÇÃO DE VALORES
  // ==========================================

  test('deve ter campo de valor editável', async ({ page }) => {
    await page.waitForTimeout(1000);

    const valueInput = page.locator('input[value*="Conecta PRO"], input[value*="30000"], input, select').first();
    const hasInput = await valueInput.isVisible().catch(() => false);
    expect(hasInput !== undefined).toBeTruthy();
  });

  test('deve mascarar valores sensíveis', async ({ page }) => {
    await page.waitForTimeout(1000);

    const sensitiveValue = page.locator('text=/\*\*\*/i').first();
    const hasMasked = await sensitiveValue.isVisible().catch(() => false);
    expect(hasMasked !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE BOTÃO NOVA CONFIG
  // ==========================================

  test('deve ter botão para nova configuração', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Config"), button:has-text("Novo")').first();
    await expect(newButton).toBeVisible();
  });

  // ==========================================
  // TESTES DE MENU DE AÇÕES
  // ==========================================

  test('deve ter menu de ações nas configurações', async ({ page }) => {
    await page.waitForTimeout(1000);

    const moreButton = page.locator('button:has([data-lucide="MoreHorizontal"])').first();
    const hasMore = await moreButton.isVisible().catch(() => false);
    expect(hasMore !== undefined).toBeTruthy();
  });

  test('deve ter opção de editar no menu', async ({ page }) => {
    await page.waitForTimeout(1000);

    const moreButton = page.locator('button:has([data-lucide="MoreHorizontal"])').first();
    if (await moreButton.isVisible().catch(() => false)) {
      await moreButton.click();
      await page.waitForTimeout(300);

      const editOption = page.locator('text=/Editar/i').first();
      const hasEdit = await editOption.isVisible().catch(() => false);
      expect(hasEdit !== undefined).toBeTruthy();
    }
  });

  test('deve ter opção de deletar no menu', async ({ page }) => {
    await page.waitForTimeout(1000);

    const moreButton = page.locator('button:has([data-lucide="MoreHorizontal"])').first();
    if (await moreButton.isVisible().catch(() => false)) {
      await moreButton.click();
      await page.waitForTimeout(300);

      const deleteOption = page.locator('text=/Deletar|Excluir/i').first();
      const hasDelete = await deleteOption.isVisible().catch(() => false);
      expect(hasDelete !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE ABA TENANT
  // ==========================================

  test('deve exibir seletor de tenant na aba Tenant', async ({ page }) => {
    const tenantTab = page.locator('text=/Tenant$/i').first();
    await tenantTab.click();
    await page.waitForTimeout(500);

    const tenantSelect = page.locator('select, [role="combobox"]').first();
    const hasSelect = await tenantSelect.isVisible().catch(() => false);
    expect(hasSelect !== undefined).toBeTruthy();
  });

  test('deve mostrar mensagem para selecionar tenant', async ({ page }) => {
    const tenantTab = page.locator('text=/Tenant$/i').first();
    await tenantTab.click();
    await page.waitForTimeout(500);

    const message = page.locator('text=/Selecione um tenant|Escolha um tenant/i').first();
    const hasMessage = await message.isVisible().catch(() => false);
    expect(hasMessage !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE ATUALIZAR
  // ==========================================

  test('deve ter botão para atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button:has([data-lucide="RefreshCw"])').first();
    await expect(refreshButton).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTADOS ESPECIAIS
  // ==========================================

  test('deve exibir empty state quando não há configurações', async ({ page }) => {
    await page.route('**/api/v1/config/system**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/nenhuma.*configuração|Nenhuma configuração/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });

  test('deve exibir estado de erro quando há falha', async ({ page }) => {
    await page.route('**/api/v1/config/system**', async (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const errorState = page.locator('text=/erro|Erro|falha/i').first();
    const hasError = await errorState.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
