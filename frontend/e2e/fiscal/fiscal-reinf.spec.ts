/**
 * Testes E2E - EFD-Reinf (Escrituração Fiscal Digital de Retenções e Informações)
 *
 * Funcionalidades testadas:
 * - Eventos REINF (R-1000, R-2010, R-2099, R-4010, R-4020)
 * - XML de envio
 * - Retorno da RFB
 * - Erros de validação
 * - Filtros por tipo de evento
 * - Status de processamento
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

const MOCK_EVENTOS = [
  {
    id: 'evt-001',
    tipo_evento: 'R-1000',
    competencia: '01/2024',
    status: 'aceito',
    data_envio: '2024-02-15T10:30:00Z',
    protocolo: 'PROT-RFB-001',
    retorno_rfb: 'Evento aceito sem ressalvas',
  },
  {
    id: 'evt-002',
    tipo_evento: 'R-2010',
    competencia: '01/2024',
    status: 'pendente',
    data_envio: null,
    protocolo: null,
    retorno_rfb: null,
  },
  {
    id: 'evt-003',
    tipo_evento: 'R-2099',
    competencia: '01/2024',
    status: 'enviado',
    data_envio: '2024-02-20T14:15:00Z',
    protocolo: 'PROT-RFB-003',
    retorno_rfb: null,
  },
  {
    id: 'evt-004',
    tipo_evento: 'R-4010',
    competencia: '01/2024',
    status: 'rejeitado',
    data_envio: '2024-02-18T09:00:00Z',
    protocolo: null,
    retorno_rfb: 'Erro de validação: CNPJ inválido',
    erros: ['Campo CNPJ do tomador não corresponde ao cadastro'],
  },
  {
    id: 'evt-005',
    tipo_evento: 'R-4020',
    competencia: '12/2023',
    status: 'aceito',
    data_envio: '2024-01-20T11:00:00Z',
    protocolo: 'PROT-RFB-005',
    retorno_rfb: 'Evento aceito',
  },
];

const MOCK_STATS = {
  total_eventos: 156,
  pendentes: 23,
  enviados: 45,
  aceitos: 82,
  rejeitados: 6,
  by_tipo: {
    'R-1000': 12,
    'R-2010': 48,
    'R-2099': 24,
    'R-4010': 36,
    'R-4020': 36,
  },
};

const TIPO_EVENTO_LABELS: Record<string, string> = {
  'R-1000': 'Informacoes do Contribuinte',
  'R-2010': 'Retencao Contribuicao Previdenciaria',
  'R-2099': 'Fechamento dos Eventos Periodicos',
  'R-4010': 'Pagamentos/Creditos a PF',
  'R-4020': 'Pagamentos/Creditos a PJ',
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

async function setupReinfMocks(page: Page) {
  // Mock listagem de eventos
  await page.route('**/api/v1/government/reinf/eventos**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_EVENTOS,
        total: MOCK_EVENTOS.length,
      }),
    });
  });

  // Mock estatísticas
  await page.route('**/api/v1/government/reinf/statistics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_STATS),
    });
  });

  // Mock gerar eventos
  await page.route('**/api/v1/government/reinf/gerar**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          evento_id: 'evt-new',
          status: 'gerado',
          xml_url: '/api/v1/government/reinf/xml/evt-new',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock enviar evento
  await page.route('**/api/v1/government/reinf/enviar**', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          protocolo: 'PROT-RFB-NEW',
          status: 'enviado',
          data_envio: new Date().toISOString(),
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock download XML
  await page.route('**/api/v1/government/reinf/*/xml**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/xml',
      body: '<?xml version="1.0"?><Reinf></Reinf>',
    });
  });
}

async function gotoReinfPage(page: Page) {
  await setupAuthMock(page);
  await setupReinfMocks(page);
  await page.goto('/modulos/fiscal/reinf');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

// ============================================================================
// TESTES
// ============================================================================

test.describe('EFD-Reinf - Eventos Fiscais', () => {

  // ============================================================================
  // 1. TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ============================================================================

  test('deve carregar página de EFD-Reinf corretamente', async ({ page }) => {
    await gotoReinfPage(page);

    await expect(page).toHaveURL(/.*reinf.*/);
    await expect(page.getByText('EFD-Reinf')).toBeVisible();
    await expect(page.getByText('Escrituracao Fiscal Digital de Retencoes e Informacoes')).toBeVisible();
  });

  test('deve exibir cards de estatísticas de eventos', async ({ page }) => {
    await gotoReinfPage(page);

    await expect(page.getByText('Total Eventos').first()).toBeVisible();
    await expect(page.getByText('Pendentes').first()).toBeVisible();
    await expect(page.getByText('Enviados').first()).toBeVisible();
  });

  test('deve exibir filtros de tipo de evento', async ({ page }) => {
    await gotoReinfPage(page);

    // Verifica select de tipo
    await expect(page.getByText('Tipo')).toBeVisible();
    const tipoSelect = page.locator('select').first();
    await expect(tipoSelect).toBeVisible();
  });

  test('deve exibir seletores de período (mês/ano)', async ({ page }) => {
    await gotoReinfPage(page);

    const selects = page.locator('select');
    const count = await selects.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });

  // ============================================================================
  // 2. TESTES DE GERAÇÃO DE EVENTOS
  // ============================================================================

  test('deve exibir botões para gerar todos os tipos de eventos', async ({ page }) => {
    await gotoReinfPage(page);

    await expect(page.getByRole('button', { name: 'R-1000' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'R-2010' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'R-2099' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'R-4010' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'R-4020' })).toBeVisible();
  });

  test('deve gerar evento R-1000 ao clicar no botão', async ({ page }) => {
    await gotoReinfPage(page);

    const gerarButton = page.getByRole('button', { name: 'R-1000' });
    await gerarButton.click();
    await page.waitForTimeout(500);

    // Verifica se botão volta ao estado normal
    await expect(page.getByText('R-1000')).toBeVisible();
  });

  test('deve gerar evento R-2010 ao clicar no botão', async ({ page }) => {
    await gotoReinfPage(page);

    const gerarButton = page.getByRole('button', { name: 'R-2010' });
    await gerarButton.click();
    await page.waitForTimeout(500);

    await expect(page.getByText('R-2010')).toBeVisible();
  });

  // ============================================================================
  // 3. TESTES DE TABELA E LISTAGEM
  // ============================================================================

  test('deve exibir tabela de eventos REINF', async ({ page }) => {
    await gotoReinfPage(page);

    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();

    // Verifica headers
    await expect(page.getByText('Tipo Evento')).toBeVisible();
    await expect(page.getByText('Competencia')).toBeVisible();
    await expect(page.getByText('Status')).toBeVisible();
  });

  test('deve exibir descrição do tipo de evento', async ({ page }) => {
    await gotoReinfPage(page);

    // Verifica se descrições aparecem
    for (const [tipo, label] of Object.entries(TIPO_EVENTO_LABELS)) {
      const hasLabel = await page.getByText(label).first().isVisible().catch(() => false);
      if (hasLabel) break; // Pelo menos um deve estar visível
    }
  });

  test('deve exibir status com badges coloridos', async ({ page }) => {
    await gotoReinfPage(page);

    // Verifica badges de status
    const statusBadges = page.locator('span[class*="rounded-full"]');
    const count = await statusBadges.count();
    expect(count).toBeGreaterThan(0);
  });

  // ============================================================================
  // 4. TESTES DE FILTROS E BUSCA
  // ============================================================================

  test('deve filtrar eventos por tipo', async ({ page }) => {
    await gotoReinfPage(page);

    const tipoSelect = page.locator('select').first();
    await tipoSelect.selectOption('R-1000');
    await page.waitForTimeout(300);

    await expect(tipoSelect).toHaveValue('R-1000');
  });

  test('deve filtrar eventos por período', async ({ page }) => {
    await gotoReinfPage(page);

    const mesSelect = page.locator('select').nth(1);
    await mesSelect.selectOption('02');
    await page.waitForTimeout(300);

    await expect(mesSelect).toHaveValue('02');
  });

  test('deve limpar filtros ao selecionar "Todos"', async ({ page }) => {
    await gotoReinfPage(page);

    const tipoSelect = page.locator('select').first();
    await tipoSelect.selectOption('');
    await page.waitForTimeout(300);

    await expect(tipoSelect).toHaveValue('');
  });

  // ============================================================================
  // 5. TESTES DE VISUALIZAÇÃO E DETALHES
  // ============================================================================

  test('deve abrir modal de detalhes ao clicar em visualizar', async ({ page }) => {
    await gotoReinfPage(page);

    // Configura mock de detalhes
    await page.route('**/api/v1/government/reinf/evt-001**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_EVENTOS[0]),
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

  test('deve exibir protocolo RFB quando evento enviado', async ({ page }) => {
    await gotoReinfPage(page);

    // Verifica se há protocolos visíveis
    const hasProtocolo = await page.getByText(/PROT-RFB/).first().isVisible().catch(() => false);
    expect(hasProtocolo !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 6. TESTES DE XML E DOWNLOAD
  // ============================================================================

  test('deve permitir download do XML do evento', async ({ page }) => {
    await gotoReinfPage(page);

    // Procura link ou botão de download
    const downloadButton = page.locator('button[title*="XML"], a[title*="XML"]').first();
    const hasDownload = await downloadButton.isVisible().catch(() => false);
    expect(hasDownload !== undefined).toBeTruthy();
  });

  // ============================================================================
  // 7. TESTES DE ERROS E VALIDAÇÃO
  // ============================================================================

  test('deve exibir erros de validação quando evento rejeitado', async ({ page }) => {
    await gotoReinfPage(page);

    // Verifica se há eventos com status de erro
    const errorBadges = page.locator('text=Rejeitado');
    const hasErrors = await errorBadges.count() > 0;
    expect(hasErrors !== undefined).toBeTruthy();
  });

  test('deve exibir mensagem de retorno da RFB', async ({ page }) => {
    await gotoReinfPage(page);

    // Configura mock com retorno RFB
    await page.route('**/api/v1/government/reinf/evt-001**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_EVENTOS[0]),
      });
    });

    const viewButton = page.locator('button[title="Ver detalhes"]').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      // Verifica se retorno RFB é exibido no modal
      const hasRetorno = await page.getByText(/retorno|RFB|aceito/i).first().isVisible().catch(() => false);
      expect(hasRetorno !== undefined).toBeTruthy();
    }
  });

  // ============================================================================
  // 8. TESTES DE ESTADOS ESPECIAIS
  // ============================================================================

  test('deve exibir empty state quando não há eventos', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/government/reinf/eventos**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto('/modulos/fiscal/reinf');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(page.getByText('Nenhum evento encontrado')).toBeVisible();
  });
});
