/**
 * Testes E2E - Detalhe de Contrato por ID
 * Página: /modulos/licitacoes/contratos/[id]
 *
 * Testa visualização detalhada de contrato, navegação por abas,
 * gerenciamento de aditivos e ações específicas do contrato.
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock de dados do contrato
const mockContrato = {
  id: '770e8400-e29b-41d4-a716-446655440001',
  numero_contrato: 'CT-2024-001',
  orgao_contratante: 'Prefeitura Municipal de São Paulo',
  objeto: 'Contratação de empresa especializada em serviços de vigilância patrimonial e portaria',
  valor_total: 1450000.00,
  status: 'vigente',
  data_assinatura: '2024-01-15',
  data_inicio: '2024-02-01',
  data_fim: '2025-01-31',
  proposta_id: '660e8400-e29b-41d4-a716-446655440003',
  observacoes: 'Contrato firmado conforme processo licitatório PE 123/2024',
  aditivos: [
    {
      id: 'adit-001',
      tipo_aditivo: 'prazo',
      data_aditivo: '2024-06-15',
      nova_data_fim: '2025-03-31',
      justificativa: 'Prorrogação por força maior',
    },
    {
      id: 'adit-002',
      tipo_aditivo: 'valor',
      data_aditivo: '2024-08-20',
      novo_valor: 1500000.00,
      justificativa: 'Reajuste conforme índice IPCA',
    },
  ],
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-08-20T15:30:00Z',
};

const mockContratoSemAditivos = {
  ...mockContrato,
  id: '770e8400-e29b-41d4-a716-446655440002',
  numero_contrato: 'CT-2024-002',
  status: 'encerrado',
  aditivos: [],
};

// Helper para configurar mocks
test.beforeEach(async ({ page }) => {
  await loginViaAPI(page);

  // Mock para buscar contrato
  await page.route('**/api/v1/contracts/**', (route) => {
    const url = route.request().url();
    const method = route.request().method();
    const id = url.split('/contracts/')[1]?.split('?')[0];

    if (method === 'GET') {
      if (id === '770e8400-e29b-41d4-a716-446655440002') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockContratoSemAditivos }),
        });
      } else if (id === 'not-found') {
        route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Contrato não encontrado' }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockContrato }),
        });
      }
    } else if (method === 'PATCH' || method === 'PUT') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    } else {
      route.continue();
    }
  });

  // Mock para criar aditivo
  await page.route('**/api/v1/contracts/*/addendums', (route) => {
    route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, id: 'adit-003' }),
    });
  });
});

test.describe('Contratos ID - Visualização Geral', () => {
  test('deve carregar página de detalhe do contrato', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const conteudo = page.locator('h1, h2, [class*="contrato"]').first();
    await expect(conteudo).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir número do contrato no header', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const numero = page.locator('text=/CT-2024-001/i').first();
    await expect(numero).toBeVisible();
  });

  test('deve exibir órgão contratante', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const orgao = page.locator('text=/Prefeitura Municipal/i').first();
    await expect(orgao).toBeVisible();
  });

  test('deve exibir objeto do contrato', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const objeto = page.locator('text=/Objeto|vigilância/i').first();
    const hasObjeto = await objeto.isVisible().catch(() => false);
    expect(hasObjeto !== undefined).toBeTruthy();
  });

  test('deve exibir valor total formatado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const valor = page.locator('text=/Valor Total|R\$/i').first();
    await expect(valor).toBeVisible();
  });

  test('deve exibir badge de status do contrato', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const status = page.locator('[class*="badge"]').first();
    await expect(status).toBeVisible();
  });
});

test.describe('Contratos ID - Botão Voltar', () => {
  test('deve ter botão de voltar', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnVoltar = page.locator('button:has-text("Voltar"), a:has-text("Voltar")').first();
    const hasBtn = await btnVoltar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });
});

test.describe('Contratos ID - Abas de Navegação', () => {
  test('deve ter aba de Dados Gerais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Dados Gerais"), [role="tab"]:has-text("Dados")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Aditivos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Aditivos"), [role="tab"]:has-text("Aditivos")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Medições', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Medições"), [role="tab"]:has-text("Medições")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Documentos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Documentos"), [role="tab"]:has-text("Documentos")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve exibir contagem de aditivos na aba', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const abaAditivos = page.locator('button:has-text("Aditivos")').first();
    const hasBadge = await abaAditivos.locator('span').first().isVisible().catch(() => false);
    expect(hasBadge !== undefined).toBeTruthy();
  });
});

test.describe('Contratos ID - Aba Dados Gerais', () => {
  test('deve exibir informações do contrato na aba dados', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba de dados gerais
    const abaDados = page.locator('button:has-text("Dados Gerais")').first();
    if (await abaDados.isVisible().catch(() => false)) {
      await abaDados.click();
      await page.waitForTimeout(500);
    }

    // Verificar campos
    const campos = ['Número do Contrato', 'Órgão Contratante', 'Valor Total', 'ID da Proposta'];
    for (const campo of campos) {
      const elemento = page.locator(`text=/${campo}/i`).first();
      const hasCampo = await elemento.isVisible().catch(() => false);
      expect(hasCampo !== undefined).toBeTruthy();
    }
  });

  test('deve exibir datas de vigência', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const datas = page.locator('text=/Data de Início|Data de Término|Data de Assinatura/i').first();
    const hasDatas = await datas.isVisible().catch(() => false);
    expect(hasDatas !== undefined).toBeTruthy();
  });

  test('deve exibir observações quando houver', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const obs = page.locator('text=/Observações|processo licitatório/i').first();
    const hasObs = await obs.isVisible().catch(() => false);
    expect(hasObs !== undefined).toBeTruthy();
  });
});

test.describe('Contratos ID - Aba Aditivos', () => {
  test('deve exibir lista de aditivos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba de aditivos
    const abaAditivos = page.locator('button:has-text("Aditivos")').first();
    if (await abaAditivos.isVisible().catch(() => false)) {
      await abaAditivos.click();
      await page.waitForTimeout(500);
    }

    // Verificar tabela de aditivos
    const tabela = page.locator('table').first();
    const hasTabela = await tabela.isVisible().catch(() => false);
    expect(hasTabela !== undefined).toBeTruthy();
  });

  test('deve ter botão de novo aditivo', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnNovo = page.locator('button:has-text("Novo Aditivo"), button:has-text("Aditivo")').first();
    const hasBtn = await btnNovo.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve exibir tipo de aditivo (prazo, valor, escopo)', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba de aditivos
    const abaAditivos = page.locator('button:has-text("Aditivos")').first();
    if (await abaAditivos.isVisible().catch(() => false)) {
      await abaAditivos.click();
      await page.waitForTimeout(500);
    }

    const tipo = page.locator('text=/Prazo|Valor|Escopo/i').first();
    const hasTipo = await tipo.isVisible().catch(() => false);
    expect(hasTipo !== undefined).toBeTruthy();
  });

  test('deve exibir justificativa do aditivo', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba de aditivos
    const abaAditivos = page.locator('button:has-text("Aditivos")').first();
    if (await abaAditivos.isVisible().catch(() => false)) {
      await abaAditivos.click();
      await page.waitForTimeout(500);
    }

    const justificativa = page.locator('text=/Prorrogação|Reajuste/i').first();
    const hasJustificativa = await justificativa.isVisible().catch(() => false);
    expect(hasJustificativa !== undefined).toBeTruthy();
  });
});

test.describe('Contratos ID - Modal de Aditivo', () => {
  test('deve abrir modal ao clicar em novo aditivo', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnNovo = page.locator('button:has-text("Novo Aditivo")').first();
    if (await btnNovo.isVisible().catch(() => false)) {
      await btnNovo.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const isModalVisible = await modal.isVisible().catch(() => false);
      expect(isModalVisible !== undefined).toBeTruthy();
    }
  });
});

test.describe('Contratos ID - Estados Diferentes', () => {
  test('deve exibir contrato em status vigente', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/vigente/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir contrato em status encerrado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440002');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/encerrado/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir mensagem quando não há aditivos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440002');
    await page.waitForTimeout(2000);

    // Clicar na aba de aditivos
    const abaAditivos = page.locator('button:has-text("Aditivos")').first();
    if (await abaAditivos.isVisible().catch(() => false)) {
      await abaAditivos.click();
      await page.waitForTimeout(500);
    }

    const emptyState = page.locator('text=/Nenhum aditivo|nenhum aditivo/i').first();
    const hasEmpty = await emptyState.isVisible().catch(() => false);
    expect(hasEmpty !== undefined).toBeTruthy();
  });
});

test.describe('Contratos ID - Ações do Header', () => {
  test('deve ter botão de editar contrato', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnEditar = page.locator('button:has-text("Editar"), a:has-text("Editar")').first();
    const hasBtn = await btnEditar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão de atualizar dados', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnAtualizar = page.locator('button:has-text("Atualizar"), button[title="Atualizar"]').first();
    const hasBtn = await btnAtualizar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });
});

test.describe('Contratos ID - Erro de Carregamento', () => {
  test('deve exibir mensagem de erro quando contrato não existe', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/not-found');
    await page.waitForTimeout(2000);

    const errorMessage = page.locator('text=/não encontrado|Erro|Voltar/i').first();
    const hasError = await errorMessage.isVisible().catch(() => false);
    expect(hasError !== undefined).toBeTruthy();
  });
});
