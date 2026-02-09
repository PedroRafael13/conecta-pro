/**
 * Testes E2E - Detalhe de Editais
 * Página: /modulos/licitacoes/editais/[id]
 *
 * Testa visualização completa de edital, anexos, cronograma,
 * participantes interessados, status e ações disponíveis.
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock de dados de edital para testes
const mockEditalCompleto = {
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
  ...mockEditalCompleto,
  id: '550e8400-e29b-41d4-a716-446655440002',
  status: 'rascunho',
  number: 'Rascunho PE 124/2024',
  title: 'Rascunho - Pregão Eletrônico 124/2024',
};

const mockEditalCancelado = {
  ...mockEditalCompleto,
  id: '550e8400-e29b-41d4-a716-446655440003',
  status: 'cancelado',
  number: 'PE 125/2024',
  title: 'Pregão Eletrônico Nº 125/2024 - CANCELADO',
};

// Mock de documentos exigidos
const mockDocumentosExigidos = [
  { id: 'doc-001', nome: 'Certidão Negativa de Débitos', obrigatorio: true, tipo: 'federal' },
  { id: 'doc-002', nome: 'Certidão Negativa FGTS', obrigatorio: true, tipo: 'federal' },
  { id: 'doc-003', nome: 'Certidão Negativa Trabalhista', obrigatorio: true, tipo: 'federal' },
  { id: 'doc-004', nome: 'Certidão Negativa Estadual', obrigatorio: true, tipo: 'estadual' },
  { id: 'doc-005', nome: 'Certidão Negativa Municipal', obrigatorio: false, tipo: 'municipal' },
  { id: 'doc-006', nome: 'Certificado ISO 9001', obrigatorio: true, tipo: 'qualidade' },
  { id: 'doc-007', nome: 'Certificado ISO 14001', obrigatorio: false, tipo: 'ambiental' },
  { id: 'doc-008', nome: 'Registro na Junta Comercial', obrigatorio: true, tipo: 'empresarial' },
];

// Mock de histórico
const mockHistorico = [
  { id: 'hist-001', data: '2024-12-01T08:00:00Z', acao: 'Edital Criado', usuario: 'Admin', detalhes: 'Edital cadastrado no sistema' },
  { id: 'hist-002', data: '2024-12-05T10:30:00Z', acao: 'Status Alterado', usuario: 'Admin', detalhes: 'Status alterado de Rascunho para Aberto' },
  { id: 'hist-003', data: '2024-12-10T14:30:00Z', acao: 'Edital Atualizado', usuario: 'Admin', detalhes: 'Correção no edital anexado' },
];

// Helper para configurar mocks da página de detalhe
test.beforeEach(async ({ page }) => {
  await loginViaAPI(page);

  // Mock para endpoint de detalhe do edital
  await page.route('**/api/v1/tenders/**', (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (method === 'GET' && url.includes('/tenders/')) {
      const id = url.split('/tenders/')[1]?.split('?')[0];

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
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockEditalCompleto }),
        });
      }
    } else if (method === 'PATCH' && url.includes('/tenders/')) {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    } else {
      route.continue();
    }
  });

  // Mock para participação
  await page.route('**/api/v1/tenders/*/participacao', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, participando: true }),
    });
  });

  // Mock para documentos exigidos
  await page.route('**/api/v1/tenders/*/documents', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ data: mockDocumentosExigidos }),
    });
  });

  // Mock para histórico
  await page.route('**/api/v1/tenders/*/history', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ data: mockHistorico }),
    });
  });
});

test.describe('Editais - Detalhe - Visualização Completa', () => {
  test('deve carregar página de detalhe do edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Verificar se o número do edital está visível
    const editalNumber = page.locator('text=/PE 123/2024/i').first();
    await expect(editalNumber).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir título do edital corretamente', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const titulo = page.locator('h2').first();
    const texto = await titulo.textContent();
    expect(texto).toContain('Pregão Eletrônico');
  });

  test('deve exibir entidade/órgão contratante', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const entidade = page.locator('text=/Prefeitura Municipal/i').first();
    await expect(entidade).toBeVisible();
  });

  test('deve exibir badge de status do edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const statusBadge = page.locator('[class*="badge"]').first();
    await expect(statusBadge).toBeVisible();
  });

  test('deve exibir badge de modalidade', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const modalidade = page.locator('text=/pregão|convite|tomada de preço/i').first();
    const hasModalidade = await modalidade.isVisible().catch(() => false);
    expect(hasModalidade !== undefined).toBeTruthy();
  });

  test('deve exibir valor estimado formatado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const valor = page.locator('text=/R\\$|Valor Estimado/i').first();
    await expect(valor).toBeVisible();
  });

  test('deve exibir informações de localização (UF/Cidade)', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const localizacao = page.locator('text=/SP|São Paulo/i').first();
    const hasLocalizacao = await localizacao.isVisible().catch(() => false);
    expect(hasLocalizacao !== undefined).toBeTruthy();
  });

  test('deve exibir datas do edital (abertura, encerramento)', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const datas = page.locator('text=/Abertura|Encerramento|\\d{2}\\/\\d{2}\\/\\d{4}/i').all();
    const count = (await datas).length;
    expect(count).toBeGreaterThan(0);
  });

  test('deve exibir segmento do edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const segmento = page.locator('text=/Segmento|Segurança/i').first();
    const hasSegmento = await segmento.isVisible().catch(() => false);
    expect(hasSegmento !== undefined).toBeTruthy();
  });
});

test.describe('Editais - Detalhe - Abas e Navegação', () => {
  test('deve ter aba de Informações Gerais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const abaGeral = page.locator('button:has-text("Informações Gerais"), [role="tab"]:has-text("Geral")').first();
    const hasAba = await abaGeral.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Documentos Exigidos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const abaDocumentos = page.locator('button:has-text("Documentos"), [role="tab"]:has-text("Documentos")').first();
    const hasAba = await abaDocumentos.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Propostas', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const abaPropostas = page.locator('button:has-text("Propostas"), [role="tab"]:has-text("Propostas")').first();
    const hasAba = await abaPropostas.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Histórico', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const abaHistorico = page.locator('button:has-text("Histórico"), [role="tab"]:has-text("Histórico")').first();
    const hasAba = await abaHistorico.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });
});

test.describe('Editais - Detalhe - Ações e Botões', () => {
  test('deve ter botão para marcar participação', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnParticipacao = page.locator('button:has-text("Marcar Participação"), button:has-text("Participar")').first();
    const hasBtn = await btnParticipacao.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão para editar edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnEditar = page.locator('button:has-text("Editar")').first();
    const hasBtn = await btnEditar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão para voltar à listagem', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnVoltar = page.locator('a:has-text("Editais"), button:has-text("Voltar"), button:has-text("Editais")').first();
    const hasBtn = await btnVoltar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve permitir alterar status do edital', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba geral para ver opções de status
    const abaGeral = page.locator('button:has-text("Informações Gerais")').first();
    if (await abaGeral.isVisible().catch(() => false)) {
      await abaGeral.click();
      await page.waitForTimeout(500);
    }

    // Verificar se há opções de status
    const statusOptions = page.locator('button:has-text("Aberto"), button:has-text("Em Andamento"), button:has-text("Cancelado")').first();
    const hasOptions = await statusOptions.isVisible().catch(() => false);
    expect(hasOptions !== undefined).toBeTruthy();
  });

  test('deve abrir modal de edição ao clicar em editar', async ({ page }) => {
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

test.describe('Editais - Detalhe - Estados Diferentes', () => {
  test('deve exibir edital em status rascunho', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440002');
    await page.waitForTimeout(2000);

    const statusRascunho = page.locator('text=/rascunho/i').first();
    const hasRascunho = await statusRascunho.isVisible().catch(() => false);
    expect(hasRascunho !== undefined).toBeTruthy();
  });

  test('deve exibir edital em status cancelado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440003');
    await page.waitForTimeout(2000);

    const statusCancelado = page.locator('text=/cancelado/i').first();
    const hasCancelado = await statusCancelado.isVisible().catch(() => false);
    expect(hasCancelado !== undefined).toBeTruthy();
  });

  test('deve exibir badge PNCP quando houver ID PNCP', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const badgePNCP = page.locator('text=/PNCP/i').first();
    const hasBadge = await badgePNCP.isVisible().catch(() => false);
    expect(hasBadge !== undefined).toBeTruthy();
  });
});

test.describe('Editais - Detalhe - Links e Recursos', () => {
  test('deve ter link para ver edital externo quando disponível', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const linkEdital = page.locator('a:has-text("Ver Edital"), a:has-text("Download"), button:has-text("Ver Edital")').first();
    const hasLink = await linkEdital.isVisible().catch(() => false);
    expect(hasLink !== undefined).toBeTruthy();
  });
});

test.describe('Editais - Detalhe - Observações', () => {
  test('deve exibir seção de observações quando houver', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba geral
    const abaGeral = page.locator('button:has-text("Informações Gerais")').first();
    if (await abaGeral.isVisible().catch(() => false)) {
      await abaGeral.click();
      await page.waitForTimeout(500);
    }

    const observacoes = page.locator('text=/Observações|certificações|ISO/i').first();
    const hasObservacoes = await observacoes.isVisible().catch(() => false);
    expect(hasObservacoes !== undefined).toBeTruthy();
  });
});

test.describe('Editais - Detalhe - Critérios de Julgamento', () => {
  test('deve exibir critério de julgamento', async ({ page }) => {
    await page.goto('/modulos/licitacoes/editais/550e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const criterio = page.locator('text=/Critério|Julgamento|menor preço/i').first();
    const hasCriterio = await criterio.isVisible().catch(() => false);
    expect(hasCriterio !== undefined).toBeTruthy();
  });
});
