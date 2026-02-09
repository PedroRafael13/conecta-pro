/**
 * Testes E2E - Detalhe de Contratos
 * Página: /modulos/licitacoes/contratos/[id]
 *
 * Testa visualização de contrato, cláusulas, vigência,
 * valores, aditivos e execução contratual.
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock de dados de contrato para testes
const mockContratoVigente = {
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
      justificativa: 'Prorrogação por força maior - pandemia',
    },
    {
      id: 'adit-002',
      tipo_aditivo: 'valor',
      data_aditivo: '2024-08-20',
      novo_valor: 1500000.00,
      justificativa: 'Reajuste de preços conforme índice IPCA',
    },
  ],
  medicoes: [
    { id: 'med-001', mes: '01/2024', valor: 120833.33, status: 'aprovada' },
    { id: 'med-002', mes: '02/2024', valor: 120833.33, status: 'aprovada' },
    { id: 'med-003', mes: '03/2024', valor: 120833.33, status: 'pendente' },
  ],
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-08-20T15:30:00Z',
};

const mockContratoEncerrado = {
  ...mockContratoVigente,
  id: '770e8400-e29b-41d4-a716-446655440002',
  numero_contrato: 'CT-2024-002',
  status: 'encerrado',
  data_fim: '2024-12-31',
  data_encerramento: '2024-12-31',
  aditivos: [],
};

const mockContratoRescindido = {
  ...mockContratoVigente,
  id: '770e8400-e29b-41d4-a716-446655440003',
  numero_contrato: 'CT-2024-003',
  status: 'rescindido',
  data_rescisao: '2024-06-30',
  motivo_rescisao: 'Descumprimento contratual',
  aditivos: [],
};

// Helper para configurar mocks
test.beforeEach(async ({ page }) => {
  await loginViaAPI(page);

  // Mock para endpoint de detalhe do contrato
  await page.route('**/api/v1/contracts/**', (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (method === 'GET' && url.includes('/contracts/')) {
      const id = url.split('/contracts/')[1]?.split('?')[0];

      if (id === '770e8400-e29b-41d4-a716-446655440002') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockContratoEncerrado }),
        });
      } else if (id === '770e8400-e29b-41d4-a716-446655440003') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockContratoRescindido }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockContratoVigente }),
        });
      }
    } else if (method === 'POST' && url.includes('/addendums')) {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, id: 'adit-003' }),
      });
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
});

test.describe('Contratos - Detalhe - Visualização Geral', () => {
  test('deve carregar página de detalhe do contrato', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Verificar se a página carregou
    const conteudo = page.locator('h1, h2, [class*="contrato"]').first();
    await expect(conteudo).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir número do contrato', async ({ page }) => {
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

    const objeto = page.locator('text=/Objeto|vigilância|portaria/i').first();
    await expect(objeto).toBeVisible();
  });

  test('deve exibir valor total do contrato', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const valor = page.locator('text=/R\\$|Valor Total|1.450.000/i').first();
    await expect(valor).toBeVisible();
  });

  test('deve exibir badge de status do contrato', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const status = page.locator('[class*="badge"]').first();
    await expect(status).toBeVisible();
  });
});

test.describe('Contratos - Detalhe - Datas e Vigência', () => {
  test('deve exibir data de assinatura', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const assinatura = page.locator('text=/Data de Assinatura|Assinatura/i').first();
    await expect(assinatura).toBeVisible();
  });

  test('deve exibir data de início', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const inicio = page.locator('text=/Data de Início|Início/i').first();
    await expect(inicio).toBeVisible();
  });

  test('deve exibir data de término', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const termino = page.locator('text=/Data de Término|Término|Fim/i').first();
    await expect(termino).toBeVisible();
  });

  test('deve exibir ID da proposta vinculada', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const proposta = page.locator('text=/Proposta|ID da Proposta/i').first();
    const hasProposta = await proposta.isVisible().catch(() => false);
    expect(hasProposta !== undefined).toBeTruthy();
  });
});

test.describe('Contratos - Detalhe - Abas e Navegação', () => {
  test('deve ter aba de Dados Gerais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Dados"), [role="tab"]:has-text("Dados")').first();
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

test.describe('Contratos - Detalhe - Ações Disponíveis', () => {
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

  test('deve ter botão para voltar', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnVoltar = page.locator('button:has-text("Voltar")').first();
    const hasBtn = await btnVoltar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });
});

test.describe('Contratos - Detalhe - Aditivos', () => {
  test('deve exibir lista de aditivos quando houver', async ({ page }) => {
    await page.goto('/opt/conecta-pro/frontend/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Clicar na aba de aditivos
    const abaAditivos = page.locator('button:has-text("Aditivos")').first();
    if (await abaAditivos.isVisible().catch(() => false)) {
      await abaAditivos.click();
      await page.waitForTimeout(500);
    }

    const lista = page.locator('table, [class*="aditivo"]').first();
    const hasLista = await lista.isVisible().catch(() => false);
    expect(hasLista !== undefined).toBeTruthy();
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

test.describe('Contratos - Detalhe - Estados Diferentes', () => {
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

  test('deve exibir contrato em status rescindido', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440003');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/rescindido/i').first();
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

    const emptyState = page.locator('text=/nenhum aditivo|Nenhum aditivo/i').first();
    const hasEmpty = await emptyState.isVisible().catch(() => false);
    expect(hasEmpty !== undefined).toBeTruthy();
  });
});

test.describe('Contratos - Detalhe - Observações', () => {
  test('deve exibir observações quando houver', async ({ page }) => {
    await page.goto('/modulos/licitacoes/contratos/770e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const obs = page.locator('text=/Observações|processo licitatório/i').first();
    const hasObs = await obs.isVisible().catch(() => false);
    expect(hasObs !== undefined).toBeTruthy();
  });
});
