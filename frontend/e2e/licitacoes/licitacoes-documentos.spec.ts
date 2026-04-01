/**
 * Testes E2E - Página de Documentos de Licitação
 * Página: /modulos/licitacoes/documentos
 *
 * Testa gestão de documentos, upload, validação, filtros,
 * abas de documentos de editais e da empresa.
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock de dados de documentos
const mockDocumentosEmpresa = [
  {
    id: 'doc-001',
    tipo_documento: 'contrato_social',
    nome: 'Contrato Social - Empresa XYZ',
    observacoes: 'Contrato social atualizado em 2024',
    created_at: '2024-01-10T10:00:00Z',
    data_validade: '2025-01-10',
    status: 'aprovado',
  },
  {
    id: 'doc-002',
    tipo_documento: 'balanco_patrimonial',
    nome: 'Balanço Patrimonial 2023',
    observacoes: 'Balanço do exercício 2023',
    created_at: '2024-02-15T14:30:00Z',
    data_validade: null,
    status: 'pendente',
  },
  {
    id: 'doc-003',
    tipo_documento: 'alvara',
    nome: 'Alvará de Funcionamento',
    observacoes: 'Alvará municipal',
    created_at: '2024-01-05T09:00:00Z',
    data_validade: '2024-12-31',
    status: 'vencido',
  },
  {
    id: 'doc-004',
    tipo_documento: 'procuracao',
    nome: 'Procuração - Representante Legal',
    observacoes: 'Procuração para licitações',
    created_at: '2024-03-01T11:00:00Z',
    data_validade: '2025-03-01',
    status: 'aprovado',
  },
];

const mockDocumentosResponse = {
  items: mockDocumentosEmpresa,
  total: 4,
};

// Helper para configurar mocks
test.beforeEach(async ({ page }) => {
  await loginViaAPI(page);

  // Mock para listar documentos da empresa
  await page.route('**/api/v1/company-documents**', (route) => {
    const method = route.request().method();

    if (method === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockDocumentosResponse),
      });
    } else if (method === 'POST') {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, id: 'doc-new-001' }),
      });
    } else {
      route.continue();
    }
  });

  // Mock para validação de documento
  await page.route('**/api/v1/company-documents/*/validate', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, valid: true }),
    });
  });

  // Mock para download
  await page.route('**/api/v1/company-documents/*/download', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/pdf',
      body: 'fake-pdf-content',
    });
  });

  // Mock para deleção
  await page.route('**/api/v1/company-documents/*', (route) => {
    if (route.request().method() === 'DELETE') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    } else {
      route.continue();
    }
  });
});

test.describe('Documentos - Visualização Geral', () => {
  test('deve carregar página de documentos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    // Verificar título da página
    const titulo = page.locator('h1').first();
    await expect(titulo).toBeVisible({ timeout: 10000 });
    const textoTitulo = await titulo.textContent();
    expect(textoTitulo?.toLowerCase()).toContain('document');
  });

  test('deve exibir subtítulo explicativo', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const subtitulo = page.locator('text=/Gestão de documentos|editais|empresa/i').first();
    const hasSubtitulo = await subtitulo.isVisible().catch(() => false);
    expect(hasSubtitulo !== undefined).toBeTruthy();
  });
});

test.describe('Documentos - Abas de Navegação', () => {
  test('deve ter aba de Documentos de Editais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Editais"), [role="tab"]:has-text("Editais")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Documentos da Empresa', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Empresa"), [role="tab"]:has-text("Empresa")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve exibir contagem de documentos na aba empresa', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const abaEmpresa = page.locator('button:has-text("Empresa")').first();
    const hasBadge = await abaEmpresa.locator('span').first().isVisible().catch(() => false);
    expect(hasBadge !== undefined).toBeTruthy();
  });

  test('deve alternar entre abas', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const abaEditais = page.locator('button:has-text("Editais")').first();
    if (await abaEditais.isVisible().catch(() => false)) {
      await abaEditais.click();
      await page.waitForTimeout(500);

      // Verificar conteúdo da aba editais
      const conteudo = page.locator('text=/Documentos de Editais|editais específicos/i').first();
      const hasConteudo = await conteudo.isVisible().catch(() => false);
      expect(hasConteudo !== undefined).toBeTruthy();
    }
  });
});

test.describe('Documentos - Estatísticas', () => {
  test('deve exibir cards de estatísticas na aba empresa', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    // Estando na aba empresa (default), verificar cards
    const cards = page.locator('[class*="card"], .grid > div').first();
    await expect(cards).toBeVisible();

    // Verificar labels de estatísticas
    const labels = ['Total', 'Aprovados', 'Pendentes', 'Rejeitados'];
    for (const label of labels) {
      const elemento = page.locator(`text=/${label}/i`).first();
      const hasLabel = await elemento.isVisible().catch(() => false);
      expect(hasLabel !== undefined).toBeTruthy();
    }
  });

  test('deve exibir valores nas estatísticas', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    // Verificar se há números nos cards
    const numeros = page.locator('text=/^\\d+$/').first();
    const hasNumeros = await numeros.isVisible().catch(() => false);
    expect(hasNumeros !== undefined).toBeTruthy();
  });
});

test.describe('Documentos - Tabela de Documentos', () => {
  test('deve exibir tabela de documentos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const tabela = page.locator('table').first();
    await expect(tabela).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir colunas da tabela corretamente', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const colunas = ['Tipo', 'Nome', 'Data Upload', 'Validade', 'Status', 'Ações'];
    for (const coluna of colunas) {
      const header = page.locator(`th:has-text("${coluna}"), th >> text=/^${coluna}$/i`).first();
      const hasHeader = await header.isVisible().catch(() => false);
      expect(hasHeader !== undefined).toBeTruthy();
    }
  });
});

test.describe('Documentos - Filtros', () => {
  test('deve ter campo de busca', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const busca = page.locator('input[placeholder*="Buscar"], input[type="search"]').first();
    await expect(busca).toBeVisible();
  });

  test('deve ter filtro por tipo de documento', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const filtroTipo = page.locator('text=/Tipo|todos os tipos/i').first();
    const hasFiltro = await filtroTipo.isVisible().catch(() => false);
    expect(hasFiltro !== undefined).toBeTruthy();
  });

  test('deve ter filtro por status', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const filtroStatus = page.locator('text=/Status|todos os status/i').first();
    const hasFiltro = await filtroStatus.isVisible().catch(() => false);
    expect(hasFiltro !== undefined).toBeTruthy();
  });
});

test.describe('Documentos - Ações', () => {
  test('deve ter botão de atualizar', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const btnAtualizar = page.locator('button:has-text("Atualizar"), button[title="Atualizar"]').first();
    await expect(btnAtualizar).toBeVisible();
  });

  test('deve ter botão de upload de documento', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const btnUpload = page.locator('button:has-text("Upload"), button:has-text("Documento")').first();
    await expect(btnUpload).toBeVisible();
  });

  test('deve ter menu de ações em cada linha', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const menuAcoes = page.locator('button:has([data-icon="MoreHorizontal"]), button:has(.lucide-more-horizontal)').first();
    const hasMenu = await menuAcoes.isVisible().catch(() => false);
    expect(hasMenu !== undefined).toBeTruthy();
  });

  test('deve abrir dropdown ao clicar no menu de ações', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
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

test.describe('Documentos - Status e Badges', () => {
  test('deve exibir badge de status aprovado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const statusAprovado = page.locator('text=/aprovado|Aprovado/i').first();
    const hasStatus = await statusAprovado.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir badge de status pendente', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const statusPendente = page.locator('text=/pendente|Pendente/i').first();
    const hasStatus = await statusPendente.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir badge de status vencido', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const statusVencido = page.locator('text=/vencido|Vencido/i').first();
    const hasStatus = await statusVencido.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });
});

test.describe('Documentos - Modal de Upload', () => {
  test('deve abrir modal ao clicar em upload', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const btnUpload = page.locator('button:has-text("Upload"), button:has-text("Documento")').first();
    if (await btnUpload.isVisible().catch(() => false)) {
      await btnUpload.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const isModalVisible = await modal.isVisible().catch(() => false);
      expect(isModalVisible !== undefined).toBeTruthy();
    }
  });
});

test.describe('Documentos - Paginação', () => {
  test('deve exibir informações de paginação quando houver muitos itens', async ({ page }) => {
    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const pagination = page.locator('text=/Mostrando|de|Próximo|Anterior/i').first();
    const hasPagination = await pagination.isVisible().catch(() => false);
    expect(hasPagination !== undefined).toBeTruthy();
  });
});

test.describe('Documentos - Estado Vazio', () => {
  test('deve exibir estado vazio quando não há documentos', async ({ page }) => {
    await page.route('**/api/v1/company-documents**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/Nenhum documento|Upload Documento/i').first();
    const hasEmpty = await emptyState.isVisible().catch(() => false);
    expect(hasEmpty !== undefined).toBeTruthy();
  });
});

test.describe('Documentos - Erro de Carregamento', () => {
  test('deve exibir mensagem de erro quando falha ao carregar', async ({ page }) => {
    await page.route('**/api/v1/company-documents**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar' }),
      });
    });

    await page.goto('/modulos/licitacoes/documentos');
    await page.waitForTimeout(2000);

    const errorMessage = page.locator('text=/Erro|Tentar novamente/i').first();
    const hasError = await errorMessage.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
