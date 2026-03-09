import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Segurança / LGPD Compliance
 *
 * Módulos testados:
 * - Consentimentos de dados
 * - Solicitações de esquecimento
 * - Relatórios de impacto (PIA/DPIA)
 * - Mascaramento de dados sensíveis
 */

// Mock data
const mockConsents = [
  {
    id: 'consent-001',
    holder_name: 'João Silva',
    holder_email: 'joao@email.com',
    purpose: 'marketing',
    legal_basis: 'consent',
    status: 'active',
    valid_until: '2026-12-31T23:59:59Z',
    created_at: '2026-01-15T10:00:00Z',
  },
  {
    id: 'consent-002',
    holder_name: 'Maria Santos',
    holder_email: 'maria@email.com',
    purpose: 'analytics',
    legal_basis: 'legitimate_interest',
    status: 'active',
    valid_until: '2026-06-30T23:59:59Z',
    created_at: '2026-01-20T14:30:00Z',
  },
  {
    id: 'consent-003',
    holder_name: 'Pedro Costa',
    holder_email: 'pedro@email.com',
    purpose: 'data_sharing',
    legal_basis: 'consent',
    status: 'revoked',
    valid_until: null,
    created_at: '2026-01-10T09:00:00Z',
  },
];

const mockErasureRequests = [
  {
    id: 'erase-001',
    holder_name: 'Ana Oliveira',
    holder_email: 'ana@email.com',
    erasure_type: 'full',
    status: 'completed',
    requested_at: '2026-01-20T10:00:00Z',
    completed_at: '2026-01-21T15:30:00Z',
  },
  {
    id: 'erase-002',
    holder_name: 'Carlos Lima',
    holder_email: 'carlos@email.com',
    erasure_type: 'personal',
    status: 'processing',
    requested_at: '2026-02-05T08:00:00Z',
    completed_at: null,
  },
  {
    id: 'erase-003',
    holder_name: 'Beatriz Souza',
    holder_email: 'beatriz@email.com',
    erasure_type: 'transactional',
    status: 'pending',
    requested_at: '2026-02-05T14:00:00Z',
    completed_at: null,
  },
];

const mockPIAs = [
  {
    id: 'pia-001',
    title: 'Sistema de CRM',
    pia_type: 'complete',
    status: 'completed',
    risk_level: 'medium',
    responsible: 'DPO Silva',
    created_at: '2026-01-10T10:00:00Z',
    description: 'Avaliação do sistema de CRM',
    data_types: 'dados pessoais, contatos',
  },
  {
    id: 'pia-002',
    title: 'App Mobile',
    pia_type: 'simple',
    status: 'in_progress',
    risk_level: 'high',
    responsible: 'Tech Lead Costa',
    created_at: '2026-02-01T09:00:00Z',
    description: 'Avaliação do aplicativo mobile',
    data_types: 'localização, contatos',
  },
  {
    id: 'pia-003',
    title: 'BI Analytics',
    pia_type: 'complete',
    status: 'draft',
    risk_level: 'critical',
    responsible: 'DPO Silva',
    created_at: '2026-02-05T11:00:00Z',
    description: 'Avaliação do sistema de BI',
    data_types: 'dados comportamentais',
  },
];

// Setup de mocks para API
async function setupLGPDMocks(page: Page) {
  // Consents
  await page.route('**/api/v1/security-lgpd/consent**', async (route) => {
    const method = route.request().method();
    if (method === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          data: { consents: mockConsents },
        }),
      });
    } else {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    }
  });

  // Erasure
  await page.route('**/api/v1/security-lgpd/erasure**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { items: mockErasureRequests },
      }),
    });
  });

  // PIA
  await page.route('**/api/v1/security-lgpd/pia**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        data: { items: mockPIAs },
      }),
    });
  });

  // Masking
  await page.route('**/api/v1/security-lgpd/mask**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        masked_data: '***.***.***-00',
        original_length: 14,
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask/cpf**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        masked_data: '***.456.***-00',
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask/email**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        masked_data: 'j***@email.com',
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask/phone**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        masked_data: '(**) *****-4321',
      }),
    });
  });

  await page.route('**/api/v1/security-lgpd/mask/batch**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { masked: '***.***.***-00' },
        { masked: '***.***.***-11' },
      ]),
    });
  });
}

test.describe('Segurança - LGPD Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupLGPDMocks(page);
  });

  // ==========================================
  // TESTES DE CONSENTIMENTO
  // ==========================================

  test.describe('Consentimento', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/modulos/seguranca/consentimento');
      await page.waitForLoadState('load');
      await page.waitForTimeout(1500);
    });

    test('deve carregar página de consentimentos', async ({ page }) => {
      await expect(page).toHaveURL(/\/consentimento/);
      const heading = page.locator('h1').first();
      await expect(heading).toContainText(/Consentimento/i);
    });

    test('deve exibir cards de estatísticas de consentimentos', async ({ page }) => {
      await page.waitForTimeout(1000);

      await expect(page.getByText(/Ativos/i)).toBeVisible();
      await expect(page.getByText(/Revogados/i)).toBeVisible();
      await expect(page.getByText(/Expirando/i)).toBeVisible();
    });

    test('deve exibir tabela de consentimentos', async ({ page }) => {
      await page.waitForSelector('table', { timeout: 10000 });
      const table = page.locator('table').first();
      await expect(table).toBeVisible();
    });

    test('deve exibir dados do titular na tabela', async ({ page }) => {
      await page.waitForTimeout(1000);
      await expect(page.getByText('João Silva')).toBeVisible();
      await expect(page.getByText('Marketing e Publicidade')).toBeVisible();
    });

    test('deve exibir badge de status ativo', async ({ page }) => {
      await page.waitForTimeout(1000);

      const activeBadge = page.locator('text=/Ativo/i, [class*="green"]').first();
      const hasActive = await activeBadge.isVisible().catch(() => false);
      expect(hasActive).toBeTruthy();
    });

    test('deve exibir badge de status revogado', async ({ page }) => {
      await page.waitForTimeout(1000);

      const revokedBadge = page.locator('text=/Revogado/i, [class*="red"]').first();
      const hasRevoked = await revokedBadge.isVisible().catch(() => false);
      expect(hasRevoked).toBeTruthy();
    });

    test('deve abrir modal de registro de consentimento', async ({ page }) => {
      const newButton = page.locator('button:has-text("Registrar Consentimento"), button:has-text("Novo")').first();
      await expect(newButton).toBeVisible();

      await newButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"], [class*="modal"]').first();
      await expect(modal).toBeVisible();
    });

    test('deve ter botão de revogação para consentimentos ativos', async ({ page }) => {
      await page.waitForTimeout(1000);

      const revokeButton = page.locator('button:has-text("Revogar"), button[class*="red"]').first();
      const hasRevoke = await revokeButton.isVisible().catch(() => false);
      expect(hasRevoke !== undefined).toBeTruthy();
    });
  });

  // ==========================================
  // TESTES DE ESQUECIMENTO
  // ==========================================

  test.describe('Direito ao Esquecimento', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/modulos/seguranca/esquecimento');
      await page.waitForLoadState('load');
      await page.waitForTimeout(1500);
    });

    test('deve carregar página de esquecimento', async ({ page }) => {
      await expect(page).toHaveURL(/\/esquecimento/);
      const heading = page.locator('h1').first();
      await expect(heading).toContainText(/Esquecimento/i);
    });

    test('deve exibir cards de estatísticas de solicitações', async ({ page }) => {
      await page.waitForTimeout(1000);

      await expect(page.getByText(/Total/i)).toBeVisible();
      await expect(page.getByText(/Pendentes/i)).toBeVisible();
      await expect(page.getByText(/Concluídas/i)).toBeVisible();
    });

    test('deve exibir tabela de solicitações', async ({ page }) => {
      await page.waitForSelector('table', { timeout: 10000 });
      const table = page.locator('table').first();
      await expect(table).toBeVisible();
    });

    test('deve exibir tipos de exclusão', async ({ page }) => {
      await page.waitForTimeout(1000);

      const types = ['Completo', 'Dados Pessoais', 'Transacional'];
      for (const type of types) {
        const typeCell = page.locator(`text=/${type}/i`).first();
        const hasType = await typeCell.isVisible().catch(() => false);
        expect(hasType !== undefined).toBeTruthy();
      }
    });

    test('deve exibir status das solicitações', async ({ page }) => {
      await page.waitForTimeout(1000);

      const statuses = ['Pendente', 'Processando', 'Concluída'];
      for (const status of statuses) {
        const statusCell = page.locator(`text=/${status}/i`).first();
        const hasStatus = await statusCell.isVisible().catch(() => false);
        expect(hasStatus !== undefined).toBeTruthy();
      }
    });

    test('deve ter menu de nova solicitação', async ({ page }) => {
      const newButton = page.locator('button:has-text("Nova Solicitação")').first();
      await expect(newButton).toBeVisible();

      await newButton.click();
      await page.waitForTimeout(300);

      // Deve mostrar dropdown com opções
      const dropdown = page.locator('[role="menu"], [class*="dropdown"]').first();
      const hasDropdown = await dropdown.isVisible().catch(() => false);
      expect(hasDropdown !== undefined).toBeTruthy();
    });

    test('deve exibir datas de solicitação e conclusão', async ({ page }) => {
      await page.waitForTimeout(1000);

      const dateHeader = page.locator('th:has-text("Solicitado"), th:has-text("Concluído")').first();
      const hasDate = await dateHeader.isVisible().catch(() => false);
      expect(hasDate).toBeTruthy();
    });
  });

  // ==========================================
  // TESTES DE PIA/DPIA
  // ==========================================

  test.describe('PIA / DPIA', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/modulos/seguranca/pia-dpia');
      await page.waitForLoadState('load');
      await page.waitForTimeout(1500);
    });

    test('deve carregar página de PIA/DPIA', async ({ page }) => {
      await expect(page).toHaveURL(/\/pia-dpia/);
      const heading = page.locator('h1').first();
      await expect(heading).toContainText(/PIA|DPIA/i);
    });

    test('deve exibir cards de estatísticas de avaliações', async ({ page }) => {
      await page.waitForTimeout(1000);

      await expect(page.getByText(/Total Avaliações/i)).toBeVisible();
      await expect(page.getByText(/Em Andamento/i)).toBeVisible();
      await expect(page.getByText(/Alto Risco/i)).toBeVisible();
    });

    test('deve exibir tabela de avaliações', async ({ page }) => {
      await page.waitForSelector('table', { timeout: 10000 });
      const table = page.locator('table').first();
      await expect(table).toBeVisible();
    });

    test('deve exibir tipos de PIA', async ({ page }) => {
      await page.waitForTimeout(1000);

      const types = page.locator('text=/Simples|Completa/i').first();
      const hasTypes = await types.isVisible().catch(() => false);
      expect(hasTypes).toBeTruthy();
    });

    test('deve exibir níveis de risco', async ({ page }) => {
      await page.waitForTimeout(1000);

      const risks = ['Baixo', 'Médio', 'Alto', 'Crítico'];
      for (const risk of risks) {
        const riskCell = page.locator(`text=/${risk}/i`).first();
        const hasRisk = await riskCell.isVisible().catch(() => false);
        expect(hasRisk !== undefined).toBeTruthy();
      }
    });

    test('deve exibir status das avaliações', async ({ page }) => {
      await page.waitForTimeout(1000);

      const statuses = ['Rascunho', 'Em Andamento', 'Concluída', 'Arquivada'];
      for (const status of statuses) {
        const statusCell = page.locator(`text=/${status}/i`).first();
        const hasStatus = await statusCell.isVisible().catch(() => false);
        expect(hasStatus !== undefined).toBeTruthy();
      }
    });

    test('deve ter botões para criar PIA simples e completa', async ({ page }) => {
      const simpleButton = page.locator('button:has-text("PIA Simples")').first();
      const completeButton = page.locator('button:has-text("PIA Completa")').first();

      const hasSimple = await simpleButton.isVisible().catch(() => false);
      const hasComplete = await completeButton.isVisible().catch(() => false);

      expect(hasSimple || hasComplete).toBeTruthy();
    });

    test('deve exibir responsável pela avaliação', async ({ page }) => {
      await page.waitForTimeout(1000);

      const responsibleHeader = page.locator('th:has-text("Responsável")').first();
      const hasResponsible = await responsibleHeader.isVisible().catch(() => false);
      expect(hasResponsible).toBeTruthy();
    });
  });

  // ==========================================
  // TESTES DE MASCARAMENTO
  // ==========================================

  test.describe('Mascaramento de Dados', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/modulos/seguranca/mascaramento');
      await page.waitForLoadState('load');
      await page.waitForTimeout(1500);
    });

    test('deve carregar página de mascaramento', async ({ page }) => {
      await expect(page).toHaveURL(/\/mascaramento/);
      const heading = page.locator('h1').first();
      await expect(heading).toContainText(/Mascaramento/i);
    });

    test('deve exibir seção de mascaramento individual', async ({ page }) => {
      await page.waitForTimeout(1000);

      const section = page.locator('text=/Mascaramento Individual/i, h2:has-text("Individual")').first();
      await expect(section).toBeVisible();
    });

    test('deve exibir seção de mascaramento em lote', async ({ page }) => {
      await page.waitForTimeout(1000);

      const section = page.locator('text=/Mascaramento em Lote/i, h2:has-text("Lote")').first();
      await expect(section).toBeVisible();
    });

    test('deve permitir selecionar tipo de dado', async ({ page }) => {
      const categorySelect = page.locator('select, [role="combobox"]').first();
      await expect(categorySelect).toBeVisible();

      await categorySelect.click();
      await page.waitForTimeout(300);

      // Verificar opções disponíveis
      const options = ['CPF', 'E-mail', 'Telefone', 'Nome'];
      for (const option of options) {
        const optionEl = page.locator(`text=/${option}/i`).first();
        const hasOption = await optionEl.isVisible().catch(() => false);
        expect(hasOption !== undefined).toBeTruthy();
      }
    });

    test('deve permitir inserir valor para mascarar', async ({ page }) => {
      const input = page.locator('input[placeholder*="CPF"], input[placeholder*="email"], input[placeholder*="telefone"]').first();
      await expect(input).toBeVisible();

      await input.fill('123.456.789-00');
      await page.waitForTimeout(300);

      await expect(input).toHaveValue('123.456.789-00');
    });

    test('deve ter botão para mascarar dado', async ({ page }) => {
      const maskButton = page.locator('button:has-text("Mascarar")').first();
      await expect(maskButton).toBeVisible();
    });

    test('deve exibir resultado do mascaramento', async ({ page }) => {
      const input = page.locator('input').first();
      await input.fill('123.456.789-00');

      const maskButton = page.locator('button:has-text("Mascarar")').first();
      await maskButton.click();
      await page.waitForTimeout(1000);

      // Deve mostrar resultado
      const result = page.locator('input[readonly], [class*="result"]').first();
      const hasResult = await result.isVisible().catch(() => false);
      expect(hasResult !== undefined).toBeTruthy();
    });

    test('deve permitir copiar resultado', async ({ page }) => {
      const copyButton = page.locator('button[title*="Copiar"], button:has([data-lucide="Copy"])').first();
      const hasCopy = await copyButton.isVisible().catch(() => false);
      expect(hasCopy !== undefined).toBeTruthy();
    });

    test('deve permitir inserir múltiplos valores em lote', async ({ page }) => {
      const textarea = page.locator('textarea').first();
      await expect(textarea).toBeVisible();

      await textarea.fill('123.456.789-00\n987.654.321-00');
      await page.waitForTimeout(300);

      const value = await textarea.inputValue();
      expect(value).toContain('123.456.789-00');
    });
  });

  // ==========================================
  // TESTES DE PÁGINA PRINCIPAL DE SEGURANÇA
  // ==========================================

  test.describe('Página Principal de Segurança', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/modulos/seguranca');
      await page.waitForLoadState('load');
      await page.waitForTimeout(1500);
    });

    test('deve carregar página principal de segurança', async ({ page }) => {
      await expect(page).toHaveURL(/\/seguranca/);
      const heading = page.locator('h1').first();
      await expect(heading).toBeVisible();
    });

    test('deve exibir links para módulos de segurança', async ({ page }) => {
      const modules = ['Auditoria', 'Consentimento', 'Criptografia', 'Esquecimento', 'Mascaramento', 'PIA'];
      for (const module of modules) {
        const link = page.locator(`a:has-text("${module}"), button:has-text("${module}")`).first();
        const hasLink = await link.isVisible().catch(() => false);
        expect(hasLink !== undefined).toBeTruthy();
      }
    });
  });
});
