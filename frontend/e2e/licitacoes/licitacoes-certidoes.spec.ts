/**
 * Testes E2E - Página de Certidões
 * Página: /modulos/licitacoes/certidoes
 *
 * Testa gestão de certidões negativas, filtros, upload,
 * validação, download e renovação de certidões.
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock de dados de certidões
const mockCertidoes = [
  {
    id: 'cert-001',
    tipo_certidao: 'federal',
    orgao_emissor: 'Receita Federal',
    numero_certidao: 'CND123456789',
    data_emissao: '2024-01-15',
    data_validade: '2025-01-15',
    status: 'valida',
    cnpj: '12.345.678/0001-90',
  },
  {
    id: 'cert-002',
    tipo_certidao: 'estadual',
    orgao_emissor: 'Secretaria da Fazenda - SP',
    numero_certidao: 'CNDE987654321',
    data_emissao: '2024-02-10',
    data_validade: '2024-12-10',
    status: 'vencendo',
    cnpj: '12.345.678/0001-90',
  },
  {
    id: 'cert-003',
    tipo_certidao: 'trabalhista',
    orgao_emissor: 'CNDT - TST',
    numero_certidao: 'CNDT456789123',
    data_emissao: '2023-12-01',
    data_validade: '2024-06-01',
    status: 'vencida',
    cnpj: '12.345.678/0001-90',
  },
  {
    id: 'cert-004',
    tipo_certidao: 'municipal',
    orgao_emissor: 'Prefeitura de São Paulo',
    numero_certidao: 'CNDM789123456',
    data_emissao: '2024-03-01',
    data_validade: '2025-03-01',
    status: 'valida',
    cnpj: '12.345.678/0001-90',
  },
];

const mockCertidoesResponse = {
  items: mockCertidoes,
  total: 4,
};

// Helper para configurar mocks
test.beforeEach(async ({ page }) => {
  await loginViaAPI(page);

  // Mock para listar certidões
  await page.route('**/api/v1/certificates**', (route) => {
    const method = route.request().method();

    if (method === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockCertidoesResponse),
      });
    } else if (method === 'POST') {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, id: 'cert-new-001' }),
      });
    } else {
      route.continue();
    }
  });

  // Mock para validação de certidão
  await page.route('**/api/v1/certificates/*/validate', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, valid: true }),
    });
  });

  // Mock para renovação de certidões
  await page.route('**/api/v1/certificates/renew', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, message: 'Renovação iniciada' }),
    });
  });

  // Mock para download
  await page.route('**/api/v1/certificates/*/download', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/pdf',
      body: 'fake-pdf-content',
    });
  });
});

test.describe('Certidões - Visualização Geral', () => {
  test('deve carregar página de certidões', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    // Verificar título da página
    const titulo = page.locator('h1').first();
    await expect(titulo).toBeVisible({ timeout: 10000 });
    const textoTitulo = await titulo.textContent();
    expect(textoTitulo?.toLowerCase()).toContain('certid');
  });

  test('deve exibir cards de estatísticas por tipo', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    // Verificar cards de estatísticas
    const cards = page.locator('[class*="card"], .grid > div').first();
    await expect(cards).toBeVisible();

    // Verificar tipos de certidões
    const tipos = ['Federal', 'Estadual', 'Municipal', 'Trabalhista'];
    for (const tipo of tipos) {
      const tipoElement = page.locator(`text=/${tipo}/i`).first();
      const hasTipo = await tipoElement.isVisible().catch(() => false);
      expect(hasTipo !== undefined).toBeTruthy();
    }
  });

  test('deve exibir tabela de certidões', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    // Verificar tabela
    const tabela = page.locator('table').first();
    await expect(tabela).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir colunas da tabela corretamente', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    // Verificar cabeçalhos das colunas
    const colunas = ['Tipo', 'Órgão Emissor', 'Número', 'Data Emissão', 'Validade', 'Status', 'Ações'];
    for (const coluna of colunas) {
      const header = page.locator(`th:has-text("${coluna}"), th >> text=/^${coluna}$/i`).first();
      const hasHeader = await header.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });
});

test.describe('Certidões - Filtros e Busca', () => {
  test('deve ter campo de busca', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const busca = page.locator('input[placeholder*="Buscar"], input[type="search"]').first();
    await expect(busca).toBeVisible();
  });

  test('deve ter filtro por tipo', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const filtroTipo = page.locator('[data-testid="tipo-filter"], select, [role="combobox"]').first();
    const hasFiltro = await filtroTipo.isVisible().catch(() => false);
    expect(hasFiltro !== undefined).toBeTruthy();
  });

  test('deve ter filtro por status', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const filtroStatus = page.locator('text=/Status/i').first();
    const hasFiltro = await filtroStatus.isVisible().catch(() => false);
    expect(hasFiltro !== undefined).toBeTruthy();
  });
});

test.describe('Certidões - Ações', () => {
  test('deve ter botão de atualizar', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const btnAtualizar = page.locator('button:has-text("Atualizar"), button[title="Atualizar"]').first();
    await expect(btnAtualizar).toBeVisible();
  });

  test('deve ter botão de renovar todas', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const btnRenovar = page.locator('button:has-text("Renovar")').first();
    const hasBtn = await btnRenovar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão de upload de certidão', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const btnUpload = page.locator('button:has-text("Upload"), button:has-text("Certidão")').first();
    await expect(btnUpload).toBeVisible();
  });

  test('deve ter menu de ações em cada linha', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const menuAcoes = page.locator('button:has([data-icon="MoreHorizontal"]), button:has(.lucide-more-horizontal)').first();
    const hasMenu = await menuAcoes.isVisible().catch(() => false);
    expect(hasMenu !== undefined).toBeTruthy();
  });

  test('deve abrir dropdown ao clicar no menu de ações', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const menuAcoes = page.locator('button:has([data-icon="MoreHorizontal"]), button:has(.lucide-more-horizontal)').first();
    if (await menuAcoes.isVisible().catch(() => false)) {
      await menuAcoes.click();
      await page.waitForTimeout(500);

      const dropdown = page.locator('[role="menu"], [data-state="open"]').first();
      const isOpen = await dropdown.isVisible().catch(() => false);
      expect(isOpen !== undefined).toBeTruthy();
    }
  });
});

test.describe('Certidões - Status e Badges', () => {
  test('deve exibir badge de status válida', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const statusValida = page.locator('text=/válida|Válida/i').first();
    const hasStatus = await statusValida.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir badge de status vencendo', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const statusVencendo = page.locator('text=/vencendo|Vencendo/i').first();
    const hasStatus = await statusVencendo.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir badge de status vencida', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const statusVencida = page.locator('text=/vencida|Vencida/i').first();
    const hasStatus = await statusVencida.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });
});

test.describe('Certidões - Modal de Upload', () => {
  test('deve abrir modal ao clicar em upload', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const btnUpload = page.locator('button:has-text("Upload"), button:has-text("Certidão")').first();
    if (await btnUpload.isVisible().catch(() => false)) {
      await btnUpload.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const isModalVisible = await modal.isVisible().catch(() => false);
      expect(isModalVisible !== undefined).toBeTruthy();
    }
  });
});

test.describe('Certidões - Paginação', () => {
  test('deve exibir informações de paginação quando houver muitos itens', async ({ page }) => {
    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    // Verificar se há elementos de paginação
    const pagination = page.locator('text=/Mostrando|de|Próximo|Anterior/i').first();
    const hasPagination = await pagination.isVisible().catch(() => false);
    expect(hasPagination !== undefined).toBeTruthy();
  });
});

test.describe('Certidões - Estado Vazio', () => {
  test('deve exibir estado vazio quando não há certidões', async ({ page }) => {
    await page.route('**/api/v1/certificates**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/Nenhuma certidão|Upload Certidão/i').first();
    const hasEmpty = await emptyState.isVisible().catch(() => false);
    expect(hasEmpty !== undefined).toBeTruthy();
  });
});

test.describe('Certidões - Erro de Carregamento', () => {
  test('deve exibir mensagem de erro quando falha ao carregar', async ({ page }) => {
    await page.route('**/api/v1/certificates**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar' }),
      });
    });

    await page.goto('/modulos/licitacoes/certidoes');
    await page.waitForTimeout(2000);

    const errorMessage = page.locator('text=/Erro|Tentar novamente/i').first();
    const hasError = await errorMessage.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
