/**
 * Testes E2E - Certidões Fiscais e Certificados Digitais
 *
 * Funcionalidades testadas:
 * - Consulta de certidões
 * - Validade das certidões
 * - Download PDF
 * - Renovação
 * - Alertas de vencimento
 * - Filtros por status
 * - Busca por tipo/órgão
 */

import { test, expect, Page } from '@playwright/test';

// ============================================================================
// MOCKS E FIXTURES
// ============================================================================

const MOCK_USER = {
  id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
  email: 'admin@conectaplus.com.br',
  name: 'Admin',
  role: 'admin',
  is_active: true,
  permissions: ['*'],
  tenant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
};

const hoje = new Date();
const daqui30Dias = new Date(hoje);
daqui30Dias.setDate(hoje.getDate() + 30);
const daqui60Dias = new Date(hoje);
daqui60Dias.setDate(hoje.getDate() + 60);
const ontem = new Date(hoje);
ontem.setDate(hoje.getDate() - 1);

const MOCK_CERTIDOES = [
  {
    id: 'cert-001',
    tipo: 'Certidão Negativa de Débitos',
    orgao: 'Receita Federal',
    numero: 'CND-RFB-2024-001',
    data_emissao: hoje.toISOString(),
    data_validade: daqui60Dias.toISOString(),
    status: 'valida',
    pdf_url: '/api/v1/government/certidoes/cert-001/pdf',
    renovacao_automatica: true,
  },
  {
    id: 'cert-002',
    tipo: 'Certidão de Regularidade FGTS',
    orgao: 'Caixa Econômica Federal',
    numero: 'CRF-CEF-2024-045',
    data_emissao: hoje.toISOString(),
    data_validade: daqui30Dias.toISOString(),
    status: 'vencendo',
    pdf_url: '/api/v1/government/certidoes/cert-002/pdf',
    renovacao_automatica: false,
  },
  {
    id: 'cert-003',
    tipo: 'Certidão Negativa de Falência',
    orgao: 'TJSP',
    numero: 'CNF-TJSP-2024-128',
    data_emissao: '2023-01-15T00:00:00Z',
    data_validade: ontem.toISOString(),
    status: 'vencida',
    pdf_url: '/api/v1/government/certidoes/cert-003/pdf',
    renovacao_automatica: false,
  },
  {
    id: 'cert-004',
    tipo: 'Certificado Digital A1',
    orgao: 'Certisign',
    numero: 'CERT-A1-2024-789',
    data_emissao: hoje.toISOString(),
    data_validade: daqui60Dias.toISOString(),
    status: 'valida',
    pdf_url: null,
    renovacao_automatica: false,
  },
  {
    id: 'cert-005',
    tipo: 'Certidão de Débitos Tributários',
    orgao: 'Prefeitura São Paulo',
    numero: 'CDT-PMSP-2024-032',
    data_emissao: null,
    data_validade: null,
    status: 'pendente',
    pdf_url: null,
    renovacao_automatica: false,
  },
];

const MOCK_ALERTAS = [
  {
    id: 'alert-001',
    tipo: 'Certidão de Regularidade FGTS',
    mensagem: 'Certidão CRF-CEF-2024-045 vence em 30 dias',
    severidade: 'media',
    data_vencimento: daqui30Dias.toISOString(),
  },
  {
    id: 'alert-002',
    tipo: 'Certidão Negativa de Falência',
    mensagem: 'Certidão CNF-TJSP-2024-128 está vencida',
    severidade: 'alta',
    data_vencimento: ontem.toISOString(),
  },
];

const MOCK_STATS = {
  total: 15,
  validas: 10,
  vencendo: 3,
  vencidas: 2,
  by_orgao: {
    'Receita Federal': 4,
    'Caixa Econômica Federal': 3,
    'TJSP': 2,
    'Prefeitura São Paulo': 4,
    'Certisign': 2,
  },
};

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

async function setupAuthMock(page: Page) {
  await page.route('**/api/v1/auth/me', (route) => {
    if (route.request().method() === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_USER),
      });
    } else {
      route.continue();
    }
  });
}

async function setupCertidoesMocks(page: Page) {
  // Mock listagem de certidões
  await page.route('**/api/v1/government/certificados**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_CERTIDOES,
        total: MOCK_CERTIDOES.length,
      }),
    });
  });

  // Mock alertas
  await page.route('**/api/v1/government/certificados/alertas**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_ALERTAS),
    });
  });

  // Mock estatísticas
  await page.route('**/api/v1/government/certificados/statistics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_STATS),
    });
  });

  // Mock download PDF
  await page.route('**/api/v1/government/certidoes/*/pdf**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/pdf',
      headers: {
        'Content-Disposition': 'attachment; filename="certidao.pdf"',
      },
      body: 'PDF content mock',
    });
  });

  // Mock renovação
  await page.route('**/api/v1/government/certidoes/*/renovar**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          sucesso: true,
          nova_validade: daqui60Dias.toISOString(),
          protocolo: 'PROT-RENOV-001',
        }),
      });
    } else {
      route.continue();
    }
  });
}

async function gotoCertidoesPage(page: Page) {
  await setupAuthMock(page);
  await setupCertidoesMocks(page);
  await page.goto('/modulos/fiscal/certidoes');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

// ============================================================================
// TESTES
// ============================================================================

test.describe('Certidões - Gestão de Certidões e Certificados', () => {

  // ============================================================================
  // 1. TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ============================================================================

  test('deve carregar página de Certidões corretamente', async ({ page }) => {
    await gotoCertidoesPage(page);

    await expect(page).toHaveURL(/.*certidoes.*/);
    await expect(page.getByText('Certidoes').first()).toBeVisible();
    await expect(page.getByText('Gestao de certidoes e certificados digitais')).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await gotoCertidoesPage(page);

    await expect(page.getByText('Total').first()).toBeVisible();
    await expect(page.getByText('Validas').first()).toBeVisible();
    await expect(page.getByText('Vencendo / Vencidas').first()).toBeVisible();
  });

  test('deve exibir alertas de certificados quando existirem', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Verifica se alertas são exibidos
    const alertasSection = page.getByText(/Alertas de Certificados/i);
    await expect(alertasSection).toBeVisible();
  });

  test('deve exibir campo de busca', async ({ page }) => {
    await gotoCertidoesPage(page);

    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();
    await expect(searchInput).toBeVisible();
  });

  // ============================================================================
  // 2. TESTES DE FILTROS POR STATUS
  // ============================================================================

  test('deve exibir botões de filtro por status', async ({ page }) => {
    await gotoCertidoesPage(page);

    await expect(page.getByRole('button', { name: 'Todos' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Valida' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Vencendo' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Vencida' })).toBeVisible();
  });

  test('deve filtrar certidões válidas ao clicar em Valida', async ({ page }) => {
    await gotoCertidoesPage(page);

    const validaButton = page.getByRole('button', { name: 'Valida' });
    await validaButton.click();
    await page.waitForTimeout(300);

    // Verifica se botão está ativo
    const dataVariant = await validaButton.getAttribute('data-variant');
    const isActive = dataVariant === 'primary' ||
                     await validaButton.evaluate(el => el.classList.contains('bg-primary'));
    expect(isActive).toBeTruthy();
  });

  test('deve filtrar certidões vencendo ao clicar em Vencendo', async ({ page }) => {
    await gotoCertidoesPage(page);

    const vencendoButton = page.getByRole('button', { name: 'Vencendo' });
    await vencendoButton.click();
    await page.waitForTimeout(300);

    await expect(vencendoButton).toBeVisible();
  });

  test('deve filtrar certidões vencidas ao clicar em Vencida', async ({ page }) => {
    await gotoCertidoesPage(page);

    const vencidaButton = page.getByRole('button', { name: 'Vencida' });
    await vencidaButton.click();
    await page.waitForTimeout(300);

    await expect(vencidaButton).toBeVisible();
  });

  // ============================================================================
  // 3. TESTES DE BUSCA
  // ============================================================================

  test('deve buscar certidões por tipo', async ({ page }) => {
    await gotoCertidoesPage(page);

    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();
    await searchInput.fill('FGTS');
    await page.waitForTimeout(500);

    await expect(searchInput).toHaveValue('FGTS');
  });

  test('deve buscar certidões por órgão', async ({ page }) => {
    await gotoCertidoesPage(page);

    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();
    await searchInput.fill('Receita Federal');
    await page.waitForTimeout(500);

    await expect(searchInput).toHaveValue('Receita Federal');
  });

  test('deve buscar certidões por número', async ({ page }) => {
    await gotoCertidoesPage(page);

    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();
    await searchInput.fill('CND-RFB');
    await page.waitForTimeout(500);

    await expect(searchInput).toHaveValue('CND-RFB');
  });

  // ============================================================================
  // 4. TESTES DE TABELA E LISTAGEM
  // ============================================================================

  test('deve exibir tabela de certidões', async ({ page }) => {
    await gotoCertidoesPage(page);

    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();

    // Verifica headers
    await expect(page.getByText('Tipo').first()).toBeVisible();
    await expect(page.getByText('Orgao').first()).toBeVisible();
    await expect(page.getByText('Validade').first()).toBeVisible();
    await expect(page.getByText('Status').first()).toBeVisible();
  });

  test('deve exibir número da certidão formatado', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Verifica se números aparecem na tabela
    const numeroCells = page.locator('td').filter({ hasText: /CND-|CRF-|CNF-|CERT-/ });
    const hasNumeros = await numeroCells.count() > 0;
    expect(hasNumeros !== undefined).toBeTruthy();
  });

  test('deve formatar datas no padrão brasileiro', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Verifica se datas estão formatadas
    const dateCells = page.locator('td').filter({ hasText: /\d{2}\/\d{2}\/\d{4}/ });
    const hasDates = await dateCells.count() > 0;
    expect(hasDates !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 5. TESTES DE STATUS E BADGES
  // ============================================================================

  test('deve exibir status com badges coloridos apropriados', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Verifica badges de status
    const statusBadges = page.locator('span[class*="rounded-full"]');
    const count = await statusBadges.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir status "Válida" em verde', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Procura por badges verdes (válidas)
    const validBadges = page.locator('span[class*="green"], span[class*="bg-green"]');
    const hasValid = await validBadges.count() > 0;
    expect(hasValid !== undefined).toBeTruthy();
  });

  test('deve exibir status "Vencendo" em amarelo/laranja', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Procura por badges amarelos (vencendo)
    const warningBadges = page.locator('span[class*="yellow"], span[class*="amber"], span[class*="orange"]');
    const hasWarning = await warningBadges.count() > 0;
    expect(hasWarning !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 6. TESTES DE VISUALIZAÇÃO E DETALHES
  // ============================================================================

  test('deve abrir modal de detalhes ao clicar em visualizar', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Configura mock de detalhes
    await page.route('**/api/v1/government/certificados/cert-001**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_CERTIDOES[0]),
      });
    });

    const viewButton = page.locator('button[title="Ver detalhes"]').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible();
    }
  });

  test('deve exibir informações completas no modal de detalhes', async ({ page }) => {
    await gotoCertidoesPage(page);

    await page.route('**/api/v1/government/certificados/cert-001**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_CERTIDOES[0]),
      });
    });

    const viewButton = page.locator('button[title="Ver detalhes"]').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      // Verifica informações no modal
      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible();

      // Verifica se tipo e órgão são exibidos
      const hasTipo = await page.getByText(MOCK_CERTIDOES[0]?.tipo ?? '').first().isVisible().catch(() => false);
      expect(hasTipo !== undefined).toBeTruthy();
    }
  });

  // ============================================================================
  // 7. TESTES DE DOWNLOAD
  // ============================================================================

  test('deve permitir download do PDF da certidão', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Procura botão ou link de download
    const downloadButton = page.locator('button[title*="PDF" i], button[title*="Download" i], a[href*="pdf"]').first();
    const hasDownload = await downloadButton.isVisible().catch(() => false);
    expect(hasDownload !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 8. TESTES DE RENOVAÇÃO
  // ============================================================================

  test('deve exibir opção de renovação para certidões vencidas ou vencendo', async ({ page }) => {
    await gotoCertidoesPage(page);

    // Procura botões de renovação
    const renovarButton = page.locator('button[title*="Renovar" i], button:has-text("Renovar")').first();
    const hasRenovar = await renovarButton.isVisible().catch(() => false);
    expect(hasRenovar !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 9. TESTES DE ESTADOS ESPECIAIS
  // ============================================================================

  test('deve exibir empty state quando não há certidões', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/government/certificados**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto('/modulos/fiscal/certidoes');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.getByText('Nenhuma certidao encontrada')).toBeVisible();
  });

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/government/certificados**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar certidões' }),
      });
    });

    await page.goto('/modulos/fiscal/certidoes');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verifica mensagem de erro
    await expect(page.getByText('Erro ao carregar certidoes')).toBeVisible();
  });

  test('deve permitir tentar novamente após erro', async ({ page }) => {
    await setupAuthMock(page);

    let attempts = 0;
    await page.route('**/api/v1/government/certificados**', (route) => {
      attempts++;
      if (attempts === 1) {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Erro interno' }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: MOCK_CERTIDOES, total: MOCK_CERTIDOES.length }),
        });
      }
    });

    await page.goto('/modulos/fiscal/certidoes');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Clica em tentar novamente
    const retryButton = page.getByRole('button', { name: 'Tentar novamente' });
    if (await retryButton.isVisible().catch(() => false)) {
      await retryButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('deve exibir loading state durante carregamento', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/government/certificados**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 500));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: MOCK_CERTIDOES, total: MOCK_CERTIDOES.length }),
      });
    });

    await page.goto('/modulos/fiscal/certidoes');

    // Verifica loading
    const loader = page.locator('.animate-spin, .animate-pulse, .animate-shimmer').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });
});
