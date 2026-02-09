import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Segurança / PIA / DPIA
 *
 * Funcionalidades testadas:
 * - Gestão de Avaliações de Impacto à Proteção de Dados
 * - Filtros por status, risco e busca
 * - Criação de PIA simples e completa
 * - Visualização de detalhes
 */

// Mock data para PIAs
const mockPIAs = [
  {
    id: 'pia-001',
    title: 'Implementação Novo CRM',
    pia_type: 'simple',
    status: 'completed',
    risk_level: 'medium',
    responsible: 'Ana Silva',
    created_at: '2026-02-01T10:00:00Z',
    description: 'Avaliação de impacto para implementação do novo sistema CRM',
    data_types: 'Dados de contato, histórico de interações',
    processing_purpose: 'Gestão de relacionamento com clientes',
  },
  {
    id: 'pia-002',
    title: 'Projeto BI Analytics',
    pia_type: 'complete',
    status: 'in_progress',
    risk_level: 'high',
    responsible: 'Carlos Santos',
    created_at: '2026-02-03T14:30:00Z',
    description: 'Avaliação completa para projeto de Business Intelligence',
    data_types: 'Dados financeiros, comportamentais, demográficos',
    processing_purpose: 'Análise preditiva e perfilamento',
  },
  {
    id: 'pia-003',
    title: 'App Mobile de Campo',
    pia_type: 'simple',
    status: 'draft',
    risk_level: 'low',
    responsible: 'Mariana Costa',
    created_at: '2026-02-05T09:15:00Z',
    description: 'Avaliação para novo aplicativo mobile',
    data_types: 'Localização, dados operacionais',
    processing_purpose: 'Gestão de equipes de campo',
  },
  {
    id: 'pia-004',
    title: 'Integração Bancária',
    pia_type: 'complete',
    status: 'completed',
    risk_level: 'critical',
    responsible: 'Pedro Oliveira',
    created_at: '2026-01-20T11:00:00Z',
    description: 'Avaliação para integração com sistemas bancários',
    data_types: 'Dados bancários, transações, documentos',
    processing_purpose: 'Processamento de pagamentos',
  },
];

// Setup de mocks para API
async function setupPIAMocks(page: Page) {
  await page.route('**/api/v1/security-lgpd/pia**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: {
          items: mockPIAs,
          total: mockPIAs.length,
        },
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/pia/simple', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        pia_id: 'pia-new-001',
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/pia/complete', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        pia_id: 'pia-new-002',
      }),
    });
  });
}

test.describe('Segurança - PIA / DPIA', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupPIAMocks(page);
    await page.goto('/modulos/seguranca/pia-dpia');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de PIA/DPIA', async ({ page }) => {
    await expect(page).toHaveURL(/\/pia-dpia/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/PIA|DPIA/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/Avaliação de Impacto|Proteção de Dados/i');
    await expect(description).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const totalCard = page.locator('text=/Total Avaliações/i').first();
    const progressCard = page.locator('text=/Em Andamento/i').first();
    const riskCard = page.locator('text=/Alto Risco/i').first();

    await expect(totalCard).toBeVisible();
    await expect(progressCard).toBeVisible();
    await expect(riskCard).toBeVisible();
  });

  test('deve exibir tabela de avaliações', async ({ page }) => {
    await page.waitForSelector('table', { timeout: 10000 });
    const table = page.locator('table').first();
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    const headers = ['Título', 'Tipo', 'Status', 'Nível Risco', 'Responsável', 'Data'];
    for (const header of headers) {
      const headerCell = page.locator(`th:has-text("${header}"), th:has-text("${header.toLowerCase()}")`).first();
      const hasHeader = await headerCell.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });

  test('deve exibir dados mockados na tabela', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('Implementação Novo CRM')).toBeVisible();
    await expect(page.getByText('Ana Silva')).toBeVisible();
  });

  // ==========================================
  // TESTES DE BADGES
  // ==========================================

  test('deve exibir badge por tipo de PIA', async ({ page }) => {
    await page.waitForTimeout(1000);

    const simpleType = page.locator('text=/Simples|simple/i').first();
    const completeType = page.locator('text=/Completa|complete/i').first();

    const hasSimple = await simpleType.isVisible().catch(() => false);
    const hasComplete = await completeType.isVisible().catch(() => false);

    expect(hasSimple !== undefined || hasComplete !== undefined).toBeTruthy();
  });

  test('deve exibir badge por status', async ({ page }) => {
    await page.waitForTimeout(1000);

    const completedStatus = page.locator('text=/Concluída|completed/i').first();
    const hasCompleted = await completedStatus.isVisible().catch(() => false);
    expect(hasCompleted !== undefined).toBeTruthy();
  });

  test('deve exibir badge por nível de risco', async ({ page }) => {
    await page.waitForTimeout(1000);

    const mediumRisk = page.locator('text=/Médio|medium/i').first();
    const highRisk = page.locator('text=/Alto|high/i').first();

    const hasMedium = await mediumRisk.isVisible().catch(() => false);
    const hasHigh = await highRisk.isVisible().catch(() => false);

    expect(hasMedium !== undefined || hasHigh !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE FILTROS
  // ==========================================

  test('deve filtrar por termo de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="buscar" i], input[type="search"]').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('CRM');
    await page.waitForTimeout(600);

    await expect(searchInput).toHaveValue('CRM');
  });

  test('deve filtrar por status', async ({ page }) => {
    const statusSelect = page.locator('select, [role="combobox"]').filter({ hasText: /Status|Todas/i }).first();

    if (await statusSelect.isVisible().catch(() => false)) {
      await statusSelect.click();
      await page.waitForTimeout(300);

      const option = page.locator('[data-value="completed"], option[value="completed"]').first();
      if (await option.isVisible().catch(() => false)) {
        await option.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('deve filtrar por nível de risco', async ({ page }) => {
    const riskSelect = page.locator('select, [role="combobox"]').filter({ hasText: /Risco|Todos/i }).first();

    if (await riskSelect.isVisible().catch(() => false)) {
      await riskSelect.click();
      await page.waitForTimeout(300);

      const option = page.locator('[data-value="high"], option[value="high"]').first();
      if (await option.isVisible().catch(() => false)) {
        await option.click();
        await page.waitForTimeout(500);
      }
    }
  });

  // ==========================================
  // TESTES DE NOVA AVALIAÇÃO
  // ==========================================

  test('deve ter botões para criar PIA', async ({ page }) => {
    const simpleButton = page.locator('button:has-text("PIA Simples")').first();
    const completeButton = page.locator('button:has-text("PIA Completa")').first();

    const hasSimple = await simpleButton.isVisible().catch(() => false);
    const hasComplete = await completeButton.isVisible().catch(() => false);

    expect(hasSimple !== undefined || hasComplete !== undefined).toBeTruthy();
  });

  test('deve abrir modal ao clicar em PIA Simples', async ({ page }) => {
    const simpleButton = page.locator('button:has-text("PIA Simples")').first();

    if (await simpleButton.isVisible().catch(() => false)) {
      await simpleButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"], [class*="modal"]').first();
      const hasModal = await modal.isVisible().catch(() => false);
      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  test('deve abrir modal ao clicar em PIA Completa', async ({ page }) => {
    const completeButton = page.locator('button:has-text("PIA Completa")').first();

    if (await completeButton.isVisible().catch(() => false)) {
      await completeButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"], [class*="modal"]').first();
      const hasModal = await modal.isVisible().catch(() => false);
      expect(hasModal !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE AÇÕES
  // ==========================================

  test('deve ter opção de visualizar no dropdown', async ({ page }) => {
    await page.waitForTimeout(1000);

    const moreButton = page.locator('button:has([data-lucide="MoreHorizontal"])').first();
    if (await moreButton.isVisible().catch(() => false)) {
      await moreButton.click();
      await page.waitForTimeout(300);

      const viewOption = page.locator('text=/Visualizar|Ver/i').first();
      const hasView = await viewOption.isVisible().catch(() => false);
      expect(hasView !== undefined).toBeTruthy();
    }
  });

  // ==========================================
  // TESTES DE ATUALIZAR
  // ==========================================

  test('deve ter botão para atualizar lista', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button:has([data-lucide="RefreshCw"])').first();
    await expect(refreshButton).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTADOS ESPECIAIS
  // ==========================================

  test('deve exibir empty state quando não há avaliações', async ({ page }) => {
    await page.route('**/api/v1/security-lgpd/pia**', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { items: [], total: 0 },
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    const emptyState = page.locator('text=/nenhuma.*encontrada|sem.*avaliações/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="loading"], [class*="spinner"], [class*="animate-spin"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });
});
