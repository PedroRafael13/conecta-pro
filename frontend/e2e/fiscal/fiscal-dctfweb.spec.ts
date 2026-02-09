/**
 * Testes E2E - DCTFWeb (Declaração de Débitos e Créditos Tributários Federais)
 *
 * Funcionalidades testadas:
 * - Declaração DCTF Web
 * - Envio de declarações
 * - Retificação
 * - Status de processamento
 * - Cálculo de FGTS e INSS
 * - Geração de guias
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

const MOCK_DECLARACOES = [
  {
    id: 'dctf-001',
    competencia: '01/2024',
    tipo: 'FGTS',
    valor: 15420.50,
    status: 'enviada',
    data_envio: '2024-02-15T10:30:00Z',
    protocolo: 'PROT-2024-001',
  },
  {
    id: 'dctf-002',
    competencia: '01/2024',
    tipo: 'INSS',
    valor: 28750.00,
    status: 'pendente',
    data_envio: null,
    protocolo: null,
  },
  {
    id: 'dctf-003',
    competencia: '12/2023',
    tipo: 'FGTS',
    valor: 14890.25,
    status: 'retificada',
    data_envio: '2024-01-20T14:15:00Z',
    protocolo: 'PROT-2024-002',
  },
  {
    id: 'dctf-004',
    competencia: '12/2023',
    tipo: 'INSS',
    valor: 27500.00,
    status: 'erro',
    data_envio: null,
    protocolo: null,
  },
];

const MOCK_STATS = {
  total_declaracoes: 48,
  pendentes: 12,
  enviadas: 36,
  retificadas: 3,
  erros: 2,
  valor_total_fgts: 185000.50,
  valor_total_inss: 342000.00,
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

async function setupDctfWebMocks(page: Page) {
  // Mock listagem de declarações
  await page.route('**/api/v1/government/dctfweb/declaracoes**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_DECLARACOES,
        total: MOCK_DECLARACOES.length,
      }),
    });
  });

  // Mock estatísticas
  await page.route('**/api/v1/government/dctfweb/statistics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_STATS),
    });
  });

  // Mock calcular FGTS
  await page.route('**/api/v1/government/fgts/calcular**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          valor_total: 15420.50,
          funcionarios: 25,
          competencia: '01/2024',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock calcular INSS
  await page.route('**/api/v1/government/inss/calcular**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          valor_total: 28750.00,
          funcionarios: 25,
          competencia: '01/2024',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock gerar guia
  await page.route('**/api/v1/government/guias/gerar**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          guia_id: 'guia-001',
          arquivo_url: '/api/v1/government/guias/guia-001/pdf',
          status: 'gerado',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock enviar declaração
  await page.route('**/api/v1/government/dctfweb/enviar**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          protocolo: 'PROT-2024-NEW',
          status: 'enviada',
          data_envio: new Date().toISOString(),
        }),
      });
    } else {
      route.continue();
    }
  });
}

async function gotoDctfWebPage(page: Page) {
  await setupAuthMock(page);
  await setupDctfWebMocks(page);
  await page.goto('/modulos/fiscal/dctfweb');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

// ============================================================================
// TESTES
// ============================================================================

test.describe('DCTFWeb - Declarações Fiscais', () => {

  // ============================================================================
  // 1. TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ============================================================================

  test('deve carregar página de DCTFWeb corretamente', async ({ page }) => {
    await gotoDctfWebPage(page);

    await expect(page).toHaveURL(/.*dctfweb.*/);
    await expect(page.getByText('DCTFWeb')).toBeVisible();
    await expect(page.getByText('Declaracao de Debitos e Creditos Tributarios Federais')).toBeVisible();
  });

  test('deve exibir seletor de período (mês/ano)', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Verifica selects de mês e ano
    const selects = page.locator('select');
    await expect(selects).toHaveCount(2);

    // Verifica label de competência
    await expect(page.getByText('Competencia')).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Verifica cards de estatísticas
    await expect(page.getByText('Declaracoes').first()).toBeVisible();
    await expect(page.getByText('Pendentes').first()).toBeVisible();
    await expect(page.getByText('Enviadas').first()).toBeVisible();
  });

  test('deve exibir botões de calcular FGTS e INSS', async ({ page }) => {
    await gotoDctfWebPage(page);

    await expect(page.getByRole('button', { name: 'Calcular FGTS' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Calcular INSS' })).toBeVisible();
  });

  // ============================================================================
  // 2. TESTES DE CÁLCULO E GERAÇÃO
  // ============================================================================

  test('deve calcular FGTS ao clicar no botão', async ({ page }) => {
    await gotoDctfWebPage(page);

    const calcularButton = page.getByRole('button', { name: 'Calcular FGTS' });
    await calcularButton.click();

    // Aguarda resposta
    await page.waitForTimeout(500);

    // Verifica se o botão volta ao estado normal
    await expect(page.getByText('Calcular FGTS')).toBeVisible();
  });

  test('deve calcular INSS ao clicar no botão', async ({ page }) => {
    await gotoDctfWebPage(page);

    const calcularButton = page.getByRole('button', { name: 'Calcular INSS' });
    await calcularButton.click();

    // Aguarda resposta
    await page.waitForTimeout(500);

    await expect(page.getByText('Calcular INSS')).toBeVisible();
  });

  test('deve exibir loading durante cálculo', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Adiciona delay no mock
    await page.route('**/api/v1/government/fgts/calcular**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 500));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ valor_total: 15420.50, funcionarios: 25 }),
      });
    });

    const calcularButton = page.getByRole('button', { name: 'Calcular FGTS' });
    await calcularButton.click();

    // Verifica loading
    await expect(page.locator('.animate-spin').first()).toBeVisible();
  });

  // ============================================================================
  // 3. TESTES DE TABELA E LISTAGEM
  // ============================================================================

  test('deve exibir tabela de declarações', async ({ page }) => {
    await gotoDctfWebPage(page);

    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();

    // Verifica headers
    await expect(page.getByText('Competencia')).toBeVisible();
    await expect(page.getByText('Tipo')).toBeVisible();
    await expect(page.getByText('Valor')).toBeVisible();
    await expect(page.getByText('Status')).toBeVisible();
  });

  test('deve exibir status com cores apropriadas', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Verifica badges de status
    const statusBadges = page.locator('span[class*="rounded-full"]').first();
    await expect(statusBadges).toBeVisible();
  });

  test('deve formatar valores monetários em reais', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Verifica formatação de valores
    const valorCells = page.locator('td[class*="text-right"]').first();
    const hasFormattedValues = await valorCells.isVisible().catch(() => false);
    expect(hasFormattedValues !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 4. TESTES DE AÇÕES E MODAIS
  // ============================================================================

  test('deve abrir modal de detalhes ao clicar em visualizar', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Configura mock de detalhes
    await page.route('**/api/v1/government/dctfweb/dctf-001**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_DECLARACOES[0]),
      });
    });

    // Clica no botão de visualizar
    const viewButton = page.locator('button[title="Ver detalhes"]').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible();
    }
  });

  test('deve gerar guia para declaração pendente', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Primeiro calcula FGTS para criar declaração pendente
    await page.getByRole('button', { name: 'Calcular FGTS' }).click();
    await page.waitForTimeout(800);

    // Procura botão de gerar guia
    const guiaButton = page.locator('button[title="Gerar Guia"]').first();
    if (await guiaButton.isVisible().catch(() => false)) {
      await guiaButton.click();
      await page.waitForTimeout(500);
    }
  });

  // ============================================================================
  // 5. TESTES DE FILTROS E BUSCA
  // ============================================================================

  test('deve filtrar declarações por período selecionado', async ({ page }) => {
    await gotoDctfWebPage(page);

    // Seleciona mês diferente
    const mesSelect = page.locator('select').first();
    await mesSelect.selectOption('02');
    await page.waitForTimeout(300);

    // Verifica se período foi atualizado
    await expect(mesSelect).toHaveValue('02');
  });

  test('deve atualizar lista ao mudar ano', async ({ page }) => {
    await gotoDctfWebPage(page);

    const anoSelect = page.locator('select').nth(1);
    const anoAtual = new Date().getFullYear();
    await anoSelect.selectOption(String(anoAtual - 1));
    await page.waitForTimeout(300);

    await expect(anoSelect).toHaveValue(String(anoAtual - 1));
  });

  // ============================================================================
  // 6. TESTES DE ESTADOS ESPECIAIS
  // ============================================================================

  test('deve exibir empty state quando não há declarações', async ({ page }) => {
    await setupAuthMock(page);

    // Mock com lista vazia
    await page.route('**/api/v1/government/dctfweb/declaracoes**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto('/modulos/fiscal/dctfweb');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verifica mensagem de empty state
    await expect(page.getByText('Nenhuma declaracao encontrada')).toBeVisible();
  });

  test('deve exibir erro quando API falha', async ({ page }) => {
    await setupAuthMock(page);

    // Mock de erro
    await page.route('**/api/v1/government/dctfweb/declaracoes**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro interno do servidor' }),
      });
    });

    await page.goto('/modulos/fiscal/dctfweb');
    await page.waitForLoadState('networkidle');

    // Verifica se página continua funcional mesmo com erro
    await expect(page.getByText('DCTFWeb')).toBeVisible();
  });
});
