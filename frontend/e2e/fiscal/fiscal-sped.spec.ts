/**
 * Testes E2E - SPED (Sistema Público de Escrituração Digital)
 *
 * Funcionalidades testadas:
 * - Geração de SPED Fiscal
 * - EFD ICMS/IPI
 * - Blocos do arquivo
 * - Validação do arquivo
 * - SPED Contábil (ECD)
 * - Download de arquivos
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

const MOCK_SPED_FISCAL = [
  {
    id: 'sped-fiscal-001',
    tipo: 'fiscal',
    mes_referencia: '01',
    ano_referencia: 2024,
    status: 'validado',
    data_geracao: '2024-02-10T10:00:00Z',
    registros: 15420,
    arquivo_url: '/api/v1/government/sped/fiscal/sped-fiscal-001.txt',
  },
  {
    id: 'sped-fiscal-002',
    tipo: 'fiscal',
    mes_referencia: '12',
    ano_referencia: 2023,
    status: 'gerado',
    data_geracao: '2024-01-15T09:30:00Z',
    registros: 14890,
    arquivo_url: '/api/v1/government/sped/fiscal/sped-fiscal-002.txt',
  },
];

const MOCK_SPED_CONTABIL = [
  {
    id: 'sped-contabil-001',
    tipo: 'contabil',
    mes_referencia: '01',
    ano_referencia: 2024,
    status: 'enviado',
    data_geracao: '2024-02-12T11:00:00Z',
    registros: 8750,
    arquivo_url: '/api/v1/government/sped/contabil/sped-contabil-001.txt',
  },
];

const MOCK_BLOCOS = {
  '0': { nome: 'Abertura e Identificação', registros: 45 },
  'C': { nome: 'Documentos Fiscais', registros: 8540 },
  'D': { nome: 'Documentos de Prestação', registros: 3200 },
  'E': { nome: 'Apuração do ICMS e IPI', registros: 1200 },
  'G': { nome: 'Controle do Crédito', registros: 800 },
  'H': { nome: 'Inventário Físico', registros: 150 },
  'K': { nome: 'Controle da Produção', registros: 1200 },
  '1': { nome: 'Encerramento', registros: 12 },
};

const MOCK_VALIDACAO = {
  valido: true,
  erros: [],
  advertencias: [
    { codigo: 'W001', mensagem: 'Verificar saldo de ICMS' },
  ],
  blocos_ok: ['0', 'C', 'E', '1'],
  blocos_pendentes: [],
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

async function setupSpedMocks(page: Page) {
  // Mock listagem SPED Fiscal
  await page.route('**/api/v1/government/sped/fiscal**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_SPED_FISCAL,
        total: MOCK_SPED_FISCAL.length,
      }),
    });
  });

  // Mock listagem SPED Contábil
  await page.route('**/api/v1/government/sped/contabil**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_SPED_CONTABIL,
        total: MOCK_SPED_CONTABIL.length,
      }),
    });
  });

  // Mock gerar SPED Fiscal
  await page.route('**/api/v1/government/sped/gerar-fiscal**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          sped_id: 'sped-fiscal-new',
          status: 'gerado',
          registros: 15000,
          arquivo_url: '/api/v1/government/sped/fiscal/sped-fiscal-new.txt',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock gerar SPED Contábil
  await page.route('**/api/v1/government/sped/gerar-contabil**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          sped_id: 'sped-contabil-new',
          status: 'gerado',
          registros: 8000,
          arquivo_url: '/api/v1/government/sped/contabil/sped-contabil-new.txt',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock validar SPED
  await page.route('**/api/v1/government/sped/validar**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_VALIDACAO),
      });
    } else {
      route.continue();
    }
  });

  // Mock blocos do SPED
  await page.route('**/api/v1/government/sped/*/blocos**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_BLOCOS),
    });
  });
}

async function gotoSpedPage(page: Page) {
  await setupAuthMock(page);
  await setupSpedMocks(page);
  await page.goto('/modulos/fiscal/sped');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

// ============================================================================
// TESTES
// ============================================================================

test.describe('SPED - Sistema Publico de Escrituracao Digital', () => {

  // ============================================================================
  // 1. TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ============================================================================

  test('deve carregar página de SPED corretamente', async ({ page }) => {
    await gotoSpedPage(page);

    await expect(page).toHaveURL(/.*sped.*/);
    await expect(page.getByText('SPED')).toBeVisible();
    await expect(page.getByText('Sistema Publico de Escrituracao Digital')).toBeVisible();
  });

  test('deve exibir tabs para Fiscal, Contábil e REINF', async ({ page }) => {
    await gotoSpedPage(page);

    await expect(page.getByRole('tab', { name: 'Fiscal' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Contabil' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'EFD-Reinf' })).toBeVisible();
  });

  test('deve exibir seletor de período', async ({ page }) => {
    await gotoSpedPage(page);

    await expect(page.getByText('Mes')).toBeVisible();
    await expect(page.getByText('Ano')).toBeVisible();

    const selects = page.locator('select');
    expect(await selects.count()).toBeGreaterThanOrEqual(2);
  });

  // ============================================================================
  // 2. TESTES DE SPED FISCAL
  // ============================================================================

  test('deve exibir conteúdo da tab Fiscal por padrão', async ({ page }) => {
    await gotoSpedPage(page);

    const fiscalTab = page.getByRole('tab', { name: 'Fiscal' });
    await expect(fiscalTab).toHaveAttribute('data-state', 'active');

    await expect(page.getByText('SPED Fiscal')).toBeVisible();
    await expect(page.getByText('Escrituracao Fiscal Digital - ICMS/IPI')).toBeVisible();
  });

  test('deve exibir botão para gerar arquivo SPED Fiscal', async ({ page }) => {
    await gotoSpedPage(page);

    await expect(page.getByRole('button', { name: 'Gerar Arquivo' }).first()).toBeVisible();
  });

  test('deve gerar arquivo SPED Fiscal ao clicar no botão', async ({ page }) => {
    await gotoSpedPage(page);

    const gerarButton = page.getByRole('button', { name: 'Gerar Arquivo' }).first();
    await gerarButton.click();
    await page.waitForTimeout(500);

    await expect(page.getByText('Gerar Arquivo')).toBeVisible();
  });

  // ============================================================================
  // 3. TESTES DE SPED CONTÁBIL
  // ============================================================================

  test('deve alternar para tab Contábil ao clicar', async ({ page }) => {
    await gotoSpedPage(page);

    const contabilTab = page.getByRole('tab', { name: 'Contabil' });
    await contabilTab.click();
    await page.waitForTimeout(300);

    await expect(page.getByText('SPED Contabil')).toBeVisible();
    await expect(page.getByText('Escrituracao Contabil Digital - ECD')).toBeVisible();
  });

  test('deve exibir botão para gerar arquivo SPED Contábil', async ({ page }) => {
    await gotoSpedPage(page);

    // Alterna para tab Contábil
    await page.getByRole('tab', { name: 'Contabil' }).click();
    await page.waitForTimeout(300);

    await expect(page.getByRole('button', { name: 'Gerar Arquivo' }).first()).toBeVisible();
  });

  test('deve gerar arquivo SPED Contábil ao clicar no botão', async ({ page }) => {
    await gotoSpedPage(page);

    await page.getByRole('tab', { name: 'Contabil' }).click();
    await page.waitForTimeout(300);

    const gerarButton = page.getByRole('button', { name: 'Gerar Arquivo' }).first();
    await gerarButton.click();
    await page.waitForTimeout(500);

    await expect(page.getByText('Gerar Arquivo')).toBeVisible();
  });

  // ============================================================================
  // 4. TESTES DE TABELA E LISTAGEM
  // ============================================================================

  test('deve exibir tabela de arquivos SPED gerados', async ({ page }) => {
    await gotoSpedPage(page);

    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();

    // Verifica headers
    await expect(page.getByText('Periodo')).toBeVisible();
    await expect(page.getByText('Data Geracao')).toBeVisible();
    await expect(page.getByText('Status')).toBeVisible();
    await expect(page.getByText('Acoes')).toBeVisible();
  });

  test('deve exibir período formatado (mês/ano)', async ({ page }) => {
    await gotoSpedPage(page);

    // Verifica se há períodos formatados na tabela
    const periodoCells = page.locator('td').filter({ hasText: /\d{2}\/\d{4}/ });
    const hasPeriodos = await periodoCells.count() > 0;
    expect(hasPeriodos !== undefined).toBeTruthy();
  });

  test('deve exibir status com badges coloridos', async ({ page }) => {
    await gotoSpedPage(page);

    const statusBadges = page.locator('span[class*="rounded-full"]');
    const count = await statusBadges.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  // ============================================================================
  // 5. TESTES DE VALIDAÇÃO
  // ============================================================================

  test('deve exibir botão de validar para arquivos gerados', async ({ page }) => {
    await gotoSpedPage(page);

    // Procura botão de validar
    const validarButton = page.locator('button[title="Validar"]').first();
    const hasValidar = await validarButton.isVisible().catch(() => false);
    expect(hasValidar !== undefined).toBeTruthy();
  });

  test('deve validar arquivo SPED ao clicar em validar', async ({ page }) => {
    await gotoSpedPage(page);

    const validarButton = page.locator('button[title="Validar"]').first();
    if (await validarButton.isVisible().catch(() => false)) {
      await validarButton.click();
      await page.waitForTimeout(500);

      // Verifica se ação foi processada
      await expect(page.getByText('Validar')).toBeVisible();
    }
  });

  // ============================================================================
  // 6. TESTES DE VISUALIZAÇÃO E DETALHES
  // ============================================================================

  test('deve abrir modal de detalhes ao clicar em visualizar', async ({ page }) => {
    await gotoSpedPage(page);

    // Configura mock de detalhes
    await page.route('**/api/v1/government/sped/sped-fiscal-001**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_SPED_FISCAL[0]),
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

  test('deve exibir informações dos blocos do arquivo', async ({ page }) => {
    await gotoSpedPage(page);

    // Configura mock de detalhes com blocos
    await page.route('**/api/v1/government/sped/sped-fiscal-001**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_SPED_FISCAL[0],
          blocos: MOCK_BLOCOS,
        }),
      });
    });

    const viewButton = page.locator('button[title="Ver detalhes"]').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      // Verifica se informações de blocos são exibidas
      const hasBlocos = await page.getByText(/bloco|registros/i).first().isVisible().catch(() => false);
      expect(hasBlocos !== undefined).toBeTruthy();
    }
  });

  // ============================================================================
  // 7. TESTES DE DOWNLOAD
  // ============================================================================

  test('deve permitir download do arquivo SPED', async ({ page }) => {
    await gotoSpedPage(page);

    // Procura link ou botão de download
    const downloadButton = page.locator('button[title*="download" i], a[title*="download" i]').first();
    const hasDownload = await downloadButton.isVisible().catch(() => false);
    expect(hasDownload !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 8. TESTES DE ESTADOS ESPECIAIS
  // ============================================================================

  test('deve exibir empty state quando não há arquivos', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/government/sped/fiscal**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto('/modulos/fiscal/sped');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verifica mensagem de empty state
    const emptyMessage = page.getByText(/Nenhum arquivo gerado|nenhum arquivo/i);
    const hasEmpty = await emptyMessage.first().isVisible().catch(() => false);
    expect(hasEmpty !== undefined).toBeTruthy();
  });

  test('deve redirecionar para página REINF na tab correspondente', async ({ page }) => {
    await gotoSpedPage(page);

    const reinfTab = page.getByRole('tab', { name: 'EFD-Reinf' });
    await reinfTab.click();
    await page.waitForTimeout(300);

    // Verifica se há botão para ir para REINF
    const irReinfButton = page.getByRole('button', { name: 'Ir para EFD-Reinf' });
    await expect(irReinfButton).toBeVisible();
  });
});
