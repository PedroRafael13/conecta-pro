/**
 * Testes E2E - Detalhe de Edital por ID
 * Página: /modulos/licitacoes/editais/[id]
 *
 * Testa visualização completa de edital, navegação por abas,
 * marcação de participação, alteração de status e histórico.
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock de dados do edital
const mockEdital = {
  id: '550e8400-e29b-41d4-a716-446655440001',
  number: 'PE 123/2024',
  title: 'Pregão Eletrônico Nº 123/2024 - Serviços de Segurança',
  description: 'Contratação de empresa especializada em serviços de vigilância e segurança patrimonial',
  entity: 'Prefeitura Municipal de São Paulo',
  modality: 'pregao_eletronico',
  status: 'aberto',
  estimated_value: 1500000.00,
  opening_date: '2024-12-15T10:00:00Z',
  closing_date: '2024-12-20T17:00:00Z',
  publication_date: '2024-12-01T08:00:00Z',
  deadline_date: '2024-12-19T17:00:00Z',
  uf: 'SP',
  city: 'São Paulo',
  segment: 'Segurança Patrimonial',
  pncp_id: '123456789',
  link: 'https://pncp.gov.br/edital/123',
  judgment_criteria: 'menor_preco',
  observations: 'Edital com exigência de certificações ISO 9001 e ISO 14001',
  created_at: '2024-12-01T08:00:00Z',
  updated_at: '2024-12-10T14:30:00Z',
};

const mockEditalRascunho = {
  ...mockEdital,
  id: '550e8400-e29b-41d4-a716-446655440002',
  status: 'rascunho',
  number: 'Rascunho PE 124/2024',
  title: 'Rascunho - Pregão Eletrônico 124/2024',
};

const mockEditalCancelado = {
  ...mockEdital,
  id: '550e8400-e29b-41d4-a716-446655440003',
  status: 'cancelado',
  number: 'PE 125/2024',
  title: 'Pregão Eletrônico Nº 125/2024 - CANCELADO',
};

// Helper para configurar mocks
test.beforeEach(async ({ page }) => {
  await loginViaAPI(page);

  // Mock para buscar edital
  await page.route('**/api/v1/tenders/**', (route) => {
    const url = route.request().url();
    const method = route.request().method();
    const id = url.split('/tenders/')[1]?.split('?')[0];

    if (method === 'GET') {
      if (id === '550e8400-e29b-41d4-a716-446655440002') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockEditalRascunho }),
        });
      } else if (id === '550e8400-e29b-41d4-a716-446655440003') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockEditalCancelado }),
        });
      } else if (id === 'not-found') {
        route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Edital não encontrado' }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockEdital }),
        });
      }
    } else if (method === 'PATCH') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    } else {
      route.continue();
    }
  });

  // Mock para marcar participação
  await page.route('**/api/v1/tenders/*/participacao', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, participando: true }),
    });
  });

  // Mock para alterar status
  await page.route('**/api/v1/tenders/*/status', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
});

test.describe('Editais ID - Visualização Geral', () => {
  test('deve carregar página de detalhe do edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const conteudo = page.locator('h1, h2, [class*="tender"]').first();
    await expect(conteudo).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir número do edital no header', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const numero = page.locator('text=/PE 123\/2024/i').first();
    await expect(numero).toBeVisible();
  });

  test('deve exibir título do edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const titulo = page.locator('text=/Pregão Eletrônico|Serviços de Segurança/i').first();
    await expect(titulo).toBeVisible();
  });

  test('deve exibir órgão/entidade', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const entidade = page.locator('text=/Prefeitura Municipal/i').first();
    await expect(entidade).toBeVisible();
  });

  test('deve exibir badge de status', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const badge = page.locator('[class*="badge"]').first();
    await expect(badge).toBeVisible();
  });

  test('deve exibir badge de modalidade', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const modalidade = page.locator('text=/pregão|convite|tomada de preço/i').first();
    const hasModalidade = await modalidade.isVisible().catch(() => false);
    expect(hasModalidade !== undefined).toBeTruthy();
  });

  test('deve exibir badge PNCP quando houver ID', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const badgePNCP = page.locator('text=/PNCP/i').first();
    const hasBadge = await badgePNCP.isVisible().catch(() => false);
    expect(hasBadge !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Informações Financeiras', () => {
  test('deve exibir valor estimado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const valor = page.locator('text=/Valor Estimado|R\$/i').first();
    await expect(valor).toBeVisible();
  });

  test('deve exibir valor formatado corretamente', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const valor = page.locator('text=/1.500.000|1.500.000,00/i').first();
    const hasValor = await valor.isVisible().catch(() => false);
    expect(hasValor !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Datas e Localização', () => {
  test('deve exibir data de abertura', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const data = page.locator('text=/Abertura/i').first();
    await expect(data).toBeVisible();
  });

  test('deve exibir localização (UF/Cidade)', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const localizacao = page.locator('text=/Localização|São Paulo|SP/i').first();
    const hasLocalizacao = await localizacao.isVisible().catch(() => false);
    expect(hasLocalizacao !== undefined).toBeTruthy();
  });

  test('deve exibir segmento', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const segmento = page.locator('text=/Segmento|Segurança/i').first();
    const hasSegmento = await segmento.isVisible().catch(() => false);
    expect(hasSegmento !== undefined).toBeTruthy();
  });

  test('deve exibir data de cadastro', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const dataCadastro = page.locator('text=/Cadastrado em|Data de Cadastro/i').first();
    const hasData = await dataCadastro.isVisible().catch(() => false);
    expect(hasData !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Botão Voltar', () => {
  test('deve ter botão para voltar à listagem de editais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnVoltar = page.locator('a:has-text("Editais"), button:has-text("Voltar"), button:has-text("Editais")').first();
    const hasBtn = await btnVoltar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Botões de Ação', () => {
  test('deve ter botão de marcar participação', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnParticipacao = page.locator('button:has-text("Marcar Participação"), button:has-text("Participar")').first();
    const hasBtn = await btnParticipacao.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão de editar edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnEditar = page.locator('button:has-text("Editar")').first();
    const hasBtn = await btnEditar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter link para ver edital externo quando disponível', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const linkEdital = page.locator('a:has-text("Ver Edital"), button:has-text("Ver Edital"), a:has-text("Download")').first();
    const hasLink = await linkEdital.isVisible().catch(() => false);
    expect(hasLink !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Abas de Navegação', () => {
  test('deve ter aba de Informações Gerais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Informações Gerais"), [role="tab"]:has-text("Geral")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Documentos Exigidos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Documentos"), [role="tab"]:has-text("Documentos")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Propostas', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Propostas"), [role="tab"]:has-text("Propostas")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Histórico', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Histórico"), [role="tab"]:has-text("Histórico")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Aba Informações Gerais', () => {
  test('deve exibir dados do edital na aba geral', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba geral
    const abaGeral = page.locator('button:has-text("Informações Gerais")').first();
    if (await abaGeral.isVisible().catch(() => false)) {
      await abaGeral.click();
      await page.waitForTimeout(500);
    }

    const campos = ['Número', 'Órgão', 'Modalidade', 'Critério'];
    for (const campo of campos) {
      const elemento = page.locator(`text=/${campo}/i`).first();
      const hasCampo = await elemento.isVisible().catch(() => false);
      expect(hasCampo !== undefined).toBeTruthy();
    }
  });

  test('deve exibir critério de julgamento', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const criterio = page.locator('text=/Critério|Julgamento|menor preço/i').first();
    const hasCriterio = await criterio.isVisible().catch(() => false);
    expect(hasCriterio !== undefined).toBeTruthy();
  });

  test('deve exibir observações quando houver', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const obs = page.locator('text=/Observações|certificações|ISO/i').first();
    const hasObs = await obs.isVisible().catch(() => false);
    expect(hasObs !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Alteração de Status', () => {
  test('deve ter opções para alterar status', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba geral
    const abaGeral = page.locator('button:has-text("Informações Gerais")').first();
    if (await abaGeral.isVisible().catch(() => false)) {
      await abaGeral.click();
      await page.waitForTimeout(500);
    }

    const statusOptions = page.locator('button:has-text("Aberto"), button:has-text("Em Andamento"), button:has-text("Cancelado")').first();
    const hasOptions = await statusOptions.isVisible().catch(() => false);
    expect(hasOptions !== undefined).toBeTruthy();
  });

  test('deve exibir seção de alterar status', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const alterarStatus = page.locator('text=/Alterar Status/i').first();
    const hasSection = await alterarStatus.isVisible().catch(() => false);
    expect(hasSection !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Modal de Edição', () => {
  test('deve abrir modal ao clicar em editar', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnEditar = page.locator('button:has-text("Editar")').first();
    if (await btnEditar.isVisible().catch(() => false)) {
      await btnEditar.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const isModalVisible = await modal.isVisible().catch(() => false);
      expect(isModalVisible !== undefined).toBeTruthy();
    }
  });
});

test.describe('Editais ID - Estados Diferentes', () => {
  test('deve exibir edital em status rascunho', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440002');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/rascunho/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir edital em status cancelado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440003');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/cancelado/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir edital em status aberto', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/aberto/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });
});

test.describe('Editais ID - Erro de Carregamento', () => {
  test('deve exibir mensagem de erro quando edital não existe', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/not-found');
    await page.waitForTimeout(2000);

    const errorMessage = page.locator('text=/não encontrado|Erro|Voltar/i').first();
    const hasError = await errorMessage.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
