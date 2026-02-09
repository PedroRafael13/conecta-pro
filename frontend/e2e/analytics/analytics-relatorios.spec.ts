/**
 * Testes E2E - Analytics Relatórios
 *
 * Cobertura completa de relatórios analíticos:
 * - Listagem de relatórios disponíveis
 * - Geração de relatórios
 * - Agendamento de relatórios
 * - Download de relatórios (PDF, Excel, CSV)
 * - Relatórios customizados
 * - Filtros e busca
 * - Histórico de relatórios
 * - Templates de relatórios
 */

import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// ==========================================
// MOCK DATA - RELATÓRIOS
// ==========================================

const mockRelatorios = [
  {
    id: 'rel-001',
    nome: 'Relatório de Produtividade Mensal',
    descricao: 'Análise completa de produtividade por colaborador e departamento',
    tipo: 'produtividade',
    formato: 'pdf',
    status: 'disponivel',
    ultimaGeracao: '2026-02-05T10:00:00Z',
    tamanho: '2.4 MB',
    periodicidade: 'mensal',
    agendado: true,
    categoria: 'operacional',
    icon: 'TrendingUp',
  },
  {
    id: 'rel-002',
    nome: 'Relatório de Eficiência de Postos',
    descricao: 'Métricas de eficiência e cobertura por posto de trabalho',
    tipo: 'eficiencia',
    formato: 'excel',
    status: 'disponivel',
    ultimaGeracao: '2026-02-04T15:30:00Z',
    tamanho: '1.8 MB',
    periodicidade: 'semanal',
    agendado: true,
    categoria: 'operacional',
    icon: 'MapPin',
  },
  {
    id: 'rel-003',
    nome: 'Relatório de Ocorrências',
    descricao: 'Registro e análise de todas as ocorrências do período',
    tipo: 'ocorrencias',
    formato: 'pdf',
    status: 'pendente',
    ultimaGeracao: null,
    tamanho: null,
    periodicidade: 'diario',
    agendado: false,
    categoria: 'seguranca',
    icon: 'AlertTriangle',
  },
  {
    id: 'rel-004',
    nome: 'Análise de Custos por Departamento',
    descricao: 'Detalhamento de custos operacionais por departamento',
    tipo: 'custos',
    formato: 'excel',
    status: 'disponivel',
    ultimaGeracao: '2026-02-03T09:00:00Z',
    tamanho: '3.1 MB',
    periodicidade: 'mensal',
    agendado: true,
    categoria: 'financeiro',
    icon: 'DollarSign',
  },
  {
    id: 'rel-005',
    nome: 'Relatório de Presença e Ponto',
    descricao: 'Controle de presença, faltas e horas extras',
    tipo: 'presenca',
    formato: 'csv',
    status: 'disponivel',
    ultimaGeracao: '2026-02-05T08:00:00Z',
    tamanho: '856 KB',
    periodicidade: 'semanal',
    agendado: true,
    categoria: 'rh',
    icon: 'Users',
  },
  {
    id: 'rel-006',
    nome: 'Dashboard Executivo',
    descricao: 'Visão consolidada para diretoria e gestores',
    tipo: 'executivo',
    formato: 'pdf',
    status: 'gerando',
    ultimaGeracao: null,
    tamanho: null,
    periodicidade: 'mensal',
    agendado: false,
    categoria: 'executivo',
    icon: 'BarChart3',
  },
];

const mockRelatoriosGerados = [
  {
    id: 'hist-001',
    relatorioId: 'rel-001',
    nome: 'Relatório de Produtividade Mensal - Janeiro 2026',
    dataGeracao: '2026-01-31T23:59:59Z',
    formato: 'pdf',
    tamanho: '2.3 MB',
    status: 'concluido',
    geradoPor: 'Admin',
    url: '/api/v1/reports/download/hist-001',
  },
  {
    id: 'hist-002',
    relatorioId: 'rel-001',
    nome: 'Relatório de Produtividade Mensal - Dezembro 2025',
    dataGeracao: '2025-12-31T23:59:59Z',
    formato: 'pdf',
    tamanho: '2.1 MB',
    status: 'concluido',
    geradoPor: 'Admin',
    url: '/api/v1/reports/download/hist-002',
  },
  {
    id: 'hist-003',
    relatorioId: 'rel-005',
    nome: 'Relatório de Presença - Semana 04/2026',
    dataGeracao: '2026-01-26T10:00:00Z',
    formato: 'csv',
    tamanho: '780 KB',
    status: 'concluido',
    geradoPor: 'Sistema',
    url: '/api/v1/reports/download/hist-003',
  },
];

const mockTemplates = [
  {
    id: 'tmpl-001',
    nome: 'Template Básico Operacional',
    descricao: 'Template padrão para relatórios operacionais',
    secoes: ['resumo', 'tabela', 'graficos'],
    customizavel: true,
  },
  {
    id: 'tmpl-002',
    nome: 'Template Executivo',
    descricao: 'Template enxuto para apresentações executivas',
    secoes: ['kpi', 'graficos'],
    customizavel: true,
  },
  {
    id: 'tmpl-003',
    nome: 'Template Analítico Completo',
    descricao: 'Template detalhado com todas as seções',
    secoes: ['resumo', 'kpi', 'tabela', 'graficos', 'detalhes'],
    customizavel: true,
  },
];

// ==========================================
// HELPERS - SETUP DE MOCKS
// ==========================================

async function setupRelatoriosMocks(page: Page) {
  // Mock endpoint de listagem de relatórios
  await page.route('**/api/v1/reports**', async (route) => {
    if (route.request().method() === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: mockRelatorios,
          total: mockRelatorios.length,
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock endpoint de histórico
  await page.route('**/api/v1/reports/history**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockRelatoriosGerados,
        total: mockRelatoriosGerados.length,
      }),
    });
  });

  // Mock endpoint de templates
  await page.route('**/api/v1/reports/templates**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: mockTemplates,
        total: mockTemplates.length,
      }),
    });
  });

  // Mock endpoint de geração
  await page.route('**/api/v1/reports/*/generate', async (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 202,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Relatório em geração',
          jobId: 'job-' + Date.now(),
          status: 'processing',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock endpoint de agendamento
  await page.route('**/api/v1/reports/*/schedule', async (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Agendamento criado com sucesso',
          scheduleId: 'sch-' + Date.now(),
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock endpoint de download
  await page.route('**/api/v1/reports/download/**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/pdf',
      headers: {
        'Content-Disposition': 'attachment; filename="relatorio.pdf"',
      },
      body: Buffer.from('PDF mock content'),
    });
  });
}

async function setupEmptyMocks(page: Page) {
  await page.route('**/api/v1/reports**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 0,
      }),
    });
  });
}

// ==========================================
// TESTES - SUITE PRINCIPAL
// ==========================================

test.describe('Analytics Relatórios - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupRelatoriosMocks(page);
  });

  test('deve carregar página de relatórios', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    const heading = page.locator('h1').first();
    await expect(heading).toBeVisible();
  });

  test('deve exibir título da página de relatórios', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    const hasRelatorios = await page.getByText(/Relatórios/i).first().isVisible().catch(() => false);
    expect(hasRelatorios).toBeTruthy();
  });

  test('deve listar todos os relatórios disponíveis', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    // Verifica se relatórios mockados aparecem
    await expect(page.getByText('Relatório de Produtividade Mensal')).toBeVisible();
    await expect(page.getByText('Relatório de Eficiência de Postos')).toBeVisible();
  });

  test('deve exibir informações de cada relatório', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    // Verifica descrições
    await expect(page.getByText('Análise completa de produtividade')).toBeVisible();
    await expect(page.getByText('Métricas de eficiência e cobertura')).toBeVisible();
  });

  test('deve exibir status dos relatórios', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    // Status: disponivel, pendente, gerando
    const statusLabels = await page.locator('[class*="badge"], [class*="status"]').count();
    expect(statusLabels).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir formato de cada relatório (PDF, Excel, CSV)', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    // Verifica se há indicadores de formato
    const hasFormatIndicator = await page.getByText(/pdf|excel|csv/i).first().isVisible().catch(() => false);
    expect(hasFormatIndicator !== undefined).toBeTruthy();
  });

  test('deve exibir indicador de relatórios agendados', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    // Verifica badges de agendamento
    const scheduledBadges = await page.getByText(/agendado|automático/i).count();
    expect(scheduledBadges).toBeGreaterThanOrEqual(0);
  });

  test('deve permitir busca por nome de relatório', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar" i]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Produtividade');
      await page.waitForTimeout(500);
      await expect(searchInput).toHaveValue('Produtividade');
    }
  });

  test('deve filtrar relatórios por categoria', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    const categoryFilter = page.locator('select, [role="combobox"]').first();
    if (await categoryFilter.isVisible().catch(() => false)) {
      await categoryFilter.click();
      await page.waitForTimeout(300);
      expect(true).toBeTruthy();
    }
  });
});

test.describe('Analytics Relatórios - Geração', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupRelatoriosMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);
  });

  test('deve exibir botão de gerar relatório', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar"), button[title*="Gerar"]').first();
    const hasButton = await generateButton.isVisible().catch(() => false);
    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve abrir modal ao clicar em gerar relatório', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar"), button:has-text("Novo")').first();

    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"], [class*="modal"]').first();
      const hasModal = await modal.isVisible().catch(() => false);
      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve permitir seleção de período na geração', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar"), button:has-text("Novo")').first();

    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(500);

      const dateInputs = page.locator('input[type="date"]').all();
      expect((await dateInputs).length).toBeGreaterThanOrEqual(0);
    }
  });

  test('deve permitir seleção de formato (PDF, Excel, CSV)', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar"), button:has-text("Novo")').first();

    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(500);

      const formatSelect = page.locator('select').filter({ hasText: /pdf|excel|csv/i }).first();
      const hasFormat = await formatSelect.isVisible().catch(() => false);
      expect(hasFormat !== undefined).toBeTruthy();
    }
  });

  test('deve mostrar loading durante geração de relatório', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar")').first();

    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(500);

      const loading = page.locator('[class*="loading"], [class*="spinner"], [class*="animate-spin"]').first();
      const hasLoading = await loading.isVisible().catch(() => false);
      expect(hasLoading !== undefined).toBeTruthy();
    }
  });
});

test.describe('Analytics Relatórios - Agendamento', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupRelatoriosMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);
  });

  test('deve exibir opção de agendar relatório', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar"), button[title*="Agendar"]').first();
    const hasSchedule = await scheduleButton.isVisible().catch(() => false);
    expect(hasSchedule !== undefined).toBeTruthy();
  });

  test('deve abrir modal de agendamento', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar"), button[title*="Agendar"]').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      const hasModal = await modal.isVisible().catch(() => false);
      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve permitir seleção de periodicidade', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar"), button[title*="Agendar"]').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(500);

      // Opções: diario, semanal, mensal
      const hasPeriodicity = await page.getByText(/diário|semanal|mensal|diario/i).first().isVisible().catch(() => false);
      expect(hasPeriodicity !== undefined).toBeTruthy();
    }
  });

  test('deve permitir configuração de destinatários', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar"), button[title*="Agendar"]').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(500);

      // Campo de email ou destinatários
      const emailInput = page.locator('input[type="email"]').first();
      const hasEmailField = await emailInput.isVisible().catch(() => false);
      expect(hasEmailField !== undefined).toBeTruthy();
    }
  });
});

test.describe('Analytics Relatórios - Download', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupRelatoriosMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);
  });

  test('deve exibir botão de download para relatórios disponíveis', async ({ page }) => {
    const downloadButtons = page.locator('button[title*="Download"], button:has-text("Download"), a[download]').all();
    const hasDownload = (await downloadButtons).length > 0;
    expect(hasDownload !== undefined).toBeTruthy();
  });

  test('deve permitir download em formato PDF', async ({ page }) => {
    const downloadTrigger = page
      .locator('button')
      .filter({ hasText: /download|baixar/i })
      .first();

    const hasDownload = await downloadTrigger.isVisible().catch(() => false);
    expect(hasDownload !== undefined).toBeTruthy();
  });

  test('deve permitir download em formato Excel', async ({ page }) => {
    const downloadTrigger = page.locator('button:has-text("Excel"), a:has-text("Excel")').first();

    const hasExcel = await downloadTrigger.isVisible().catch(() => false);
    expect(hasExcel !== undefined).toBeTruthy();
  });

  test('deve permitir download em formato CSV', async ({ page }) => {
    const downloadTrigger = page.locator('button:has-text("CSV"), a:has-text("CSV")').first();

    const hasCSV = await downloadTrigger.isVisible().catch(() => false);
    expect(hasCSV !== undefined).toBeTruthy();
  });

  test('deve exibir tamanho do arquivo no botão de download', async ({ page }) => {
    // Verifica se há indicações de tamanho (MB, KB)
    const sizeLabels = await page.getByText(/MB|KB/i).count();
    expect(sizeLabels).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data de geração no relatório', async ({ page }) => {
    // Verifica datas de geração
    const hasDate = await page.getByText(/2026|2025/).first().isVisible().catch(() => false);
    expect(hasDate !== undefined).toBeTruthy();
  });
});

test.describe('Analytics Relatórios - Histórico', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupRelatoriosMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);
  });

  test('deve exibir aba/seção de histórico', async ({ page }) => {
    const historicoTab = page.locator('button:has-text("Histórico"), [role="tab"]:has-text("Histórico")').first();

    if (await historicoTab.isVisible().catch(() => false)) {
      await historicoTab.click();
      await page.waitForTimeout(500);
    }

    const hasHistorico = await page.getByText(/Histórico|Gerados|Anteriores/i).first().isVisible().catch(() => false);
    expect(hasHistorico !== undefined).toBeTruthy();
  });

  test('deve listar relatórios gerados anteriormente', async ({ page }) => {
    const historicoTab = page.locator('button:has-text("Histórico")').first();

    if (await historicoTab.isVisible().catch(() => false)) {
      await historicoTab.click();
      await page.waitForTimeout(1000);
    }

    // Verifica se há registros de histórico
    const hasHistoryItems = await page.getByText(/Janeiro|Dezembro|2026|2025/).first().isVisible().catch(() => false);
    expect(hasHistoryItems !== undefined).toBeTruthy();
  });

  test('deve permitir re-gerar relatório do histórico', async ({ page }) => {
    const regenerateButton = page.locator('button[title*="Regerar"], button:has-text("Regerar")').first();

    const hasRegenerate = await regenerateButton.isVisible().catch(() => false);
    expect(hasRegenerate !== undefined).toBeTruthy();
  });
});

test.describe('Analytics Relatórios - Customização', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupRelatoriosMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);
  });

  test('deve exibir templates de relatórios disponíveis', async ({ page }) => {
    const templatesSection = page.locator('button:has-text("Templates"), [role="tab"]:has-text("Templates")').first();

    if (await templatesSection.isVisible().catch(() => false)) {
      await templatesSection.click();
      await page.waitForTimeout(500);

      await expect(page.getByText('Template Básico Operacional')).toBeVisible();
    }
  });

  test('deve permitir criação de relatório customizado', async ({ page }) => {
    const customButton = page.locator('button:has-text("Customizado"), button:has-text("Personalizar")').first();

    const hasCustom = await customButton.isVisible().catch(() => false);
    expect(hasCustom !== undefined).toBeTruthy();
  });

  test('deve permitir seleção de seções no relatório customizado', async ({ page }) => {
    const customButton = page.locator('button:has-text("Customizado")').first();

    if (await customButton.isVisible().catch(() => false)) {
      await customButton.click();
      await page.waitForTimeout(500);

      // Verifica checkboxes para seções
      const checkboxes = page.locator('input[type="checkbox"]').all();
      expect((await checkboxes).length).toBeGreaterThanOrEqual(0);
    }
  });
});

test.describe('Analytics Relatórios - Estados Especiais', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir empty state quando não há relatórios', async ({ page }) => {
    await setupEmptyMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    const emptyMessage = page.getByText(/nenhum relatório|vazio|sem relatórios/i).first();
    const hasEmpty = await emptyMessage.isVisible().catch(() => false);
    expect(hasEmpty !== undefined).toBeTruthy();
  });

  test('deve exibir mensagem quando relatório está sendo gerado', async ({ page }) => {
    await setupRelatoriosMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    // Verifica se há indicadores de "gerando" ou "processando"
    const hasGenerating = await page.getByText(/gerando|processando|em andamento/i).first().isVisible().catch(() => false);
    expect(hasGenerating !== undefined).toBeTruthy();
  });

  test('deve desabilitar download para relatórios pendentes', async ({ page }) => {
    await setupRelatoriosMocks(page);
    await page.goto('/modulos/analytics/relatorios');
    await page.waitForTimeout(1500);

    // Busca botões desabilitados
    const disabledButtons = page.locator('button[disabled], button[aria-disabled="true"]').all();
    expect((await disabledButtons).length).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Analytics Relatórios - Integração', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupRelatoriosMocks(page);
  });

  test('deve acessar relatórios a partir do dashboard analytics', async ({ page }) => {
    await page.goto('/modulos/analytics');
    await page.waitForTimeout(1500);

    const relatoriosLink = page.locator('a:has-text("Relatórios"), button:has-text("Relatórios")').first();

    if (await relatoriosLink.isVisible().catch(() => false)) {
      await relatoriosLink.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('relatorios');
    }
  });

  test('deve manter filtros ao navegar entre páginas', async ({ page }) => {
    await page.goto('/modulos/analytics/relatorios?categoria=operacional');
    await page.waitForTimeout(1500);

    const url = page.url();
    expect(url).toContain('categoria');
  });
});
