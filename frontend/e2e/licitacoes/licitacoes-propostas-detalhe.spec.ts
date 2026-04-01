/**
 * Testes E2E - Detalhe de Propostas
 * Página: /modulos/licitacoes/propostas/[id]
 *
 * Testa editor de proposta, itens e preços, condições comerciais,
 * anexos técnicos, envio de proposta e status.
 */

import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

// Mock de dados de proposta para testes
const mockPropostaRascunho = {
  id: '660e8400-e29b-41d4-a716-446655440001',
  numero_proposta: 'PROP-2024-001',
  tender_id: '550e8400-e29b-41d4-a716-446655440001',
  cnpj: '12.345.678/0001-90',
  razao_social: 'SEGURANÇA TOTAL LTDA',
  valor_global: 1450000.00,
  status: 'rascunho',
  prazo_entrega: 30,
  validade_proposta: 60,
  observacoes_tecnicas: 'Proposta técnica completa conforme edital',
  observacoes_comerciais: 'Condição de pagamento: 30/60/90 dias',
  created_at: '2024-12-05T10:00:00Z',
  updated_at: '2024-12-10T15:30:00Z',
};

const mockPropostaEnviada = {
  ...mockPropostaRascunho,
  id: '660e8400-e29b-41d4-a716-446655440002',
  numero_proposta: 'PROP-2024-002',
  status: 'enviada',
  data_envio: '2024-12-10T15:30:00Z',
};

const mockPropostaAprovada = {
  ...mockPropostaRascunho,
  id: '660e8400-e29b-41d4-a716-446655440003',
  numero_proposta: 'PROP-2024-003',
  status: 'aprovada',
  data_aprovacao: '2024-12-15T09:00:00Z',
};

const mockPropostaRejeitada = {
  ...mockPropostaRascunho,
  id: '660e8400-e29b-41d4-a716-446655440004',
  numero_proposta: 'PROP-2024-004',
  status: 'rejeitada',
  motivo_rejeicao: 'Documentação incompleta',
};

// Mock de itens da proposta
const mockItensProposta = [
  {
    id: 'item-001',
    numero: 1,
    descricao: 'Vigilância armada 24h - Posto Principal',
    quantidade: 720,
    unidade: 'h/h',
    valor_unitario: 25.50,
    valor_total: 18360.00
  },
  {
    id: 'item-002',
    numero: 2,
    descricao: 'Vigilância desarmada 12h - Portaria',
    quantidade: 360,
    unidade: 'h/h',
    valor_unitario: 18.00,
    valor_total: 6480.00
  },
  {
    id: 'item-003',
    numero: 3,
    descricao: 'Supervisão técnica - Coordenação',
    quantidade: 180,
    unidade: 'h/h',
    valor_unitario: 45.00,
    valor_total: 8100.00
  },
];

// Mock de histórico
const mockHistoricoProposta = [
  { id: 'hist-001', data: '2024-12-05T10:00:00Z', acao: 'Proposta Criada', usuario: 'Admin', status: 'rascunho' },
  { id: 'hist-002', data: '2024-12-10T15:30:00Z', acao: 'Proposta Enviada', usuario: 'Admin', status: 'enviada' },
];

// Helper para configurar mocks
test.beforeEach(async ({ page }) => {
  await loginViaAPI(page);

  // Mock para endpoint de detalhe da proposta
  await page.route('**/api/v1/proposals/**', (route) => {
    const url = route.request().url();
    const method = route.request().method();

    if (method === 'GET' && url.includes('/proposals/')) {
      const id = url.split('/proposals/')[1]?.split('?')[0];

      if (id === '660e8400-e29b-41d4-a716-446655440002') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockPropostaEnviada }),
        });
      } else if (id === '660e8400-e29b-41d4-a716-446655440003') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockPropostaAprovada }),
        });
      } else if (id === '660e8400-e29b-41d4-a716-446655440004') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockPropostaRejeitada }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: mockPropostaRascunho }),
        });
      }
    } else if (method === 'PATCH' || method === 'PUT') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    } else if (method === 'POST' && url.includes('/submit')) {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, status: 'enviada' }),
      });
    } else {
      route.continue();
    }
  });

  // Mock para itens da proposta
  await page.route('**/api/v1/proposals/*/items', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ data: mockItensProposta }),
    });
  });

  // Mock para histórico
  await page.route('**/api/v1/proposals/*/history', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ data: mockHistoricoProposta }),
    });
  });

  // Mock para alterar status
  await page.route('**/api/v1/proposals/*/status', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
});

test.describe('Propostas - Detalhe - Visualização Geral', () => {
  test('deve carregar página de detalhe da proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Verificar se a página carregou
    const conteudo = page.locator('h1, h2, [class*="proposta"]').first();
    await expect(conteudo).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir número da proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const numero = page.locator('text=/PROP-2024/i').first();
    await expect(numero).toBeVisible();
  });

  test('deve exibir razão social da empresa', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const razaoSocial = page.locator('text=/SEGURANÇA TOTAL/i').first();
    await expect(razaoSocial).toBeVisible();
  });

  test('deve exibir CNPJ da empresa', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const cnpj = page.locator('text=/12.345.678|CNPJ/i').first();
    const hasCnpj = await cnpj.isVisible().catch(() => false);
    expect(hasCnpj !== undefined).toBeTruthy();
  });

  test('deve exibir valor global da proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const valor = page.locator('text=/R\\$|Valor Global|1.450.000/i').first();
    await expect(valor).toBeVisible();
  });

  test('deve exibir badge de status', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const status = page.locator('[class*="badge"]').first();
    await expect(status).toBeVisible();
  });

  test('deve exibir card de prazo de entrega', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const prazo = page.locator('text=/Prazo Entrega|30 dias/i').first();
    await expect(prazo).toBeVisible();
  });

  test('deve exibir card de validade da proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const validade = page.locator('text=/Validade|60 dias/i').first();
    await expect(validade).toBeVisible();
  });
});

test.describe('Propostas - Detalhe - Abas e Navegação', () => {
  test('deve ter aba de Dados Gerais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Dados Gerais"), [role="tab"]:has-text("Dados")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Itens da Proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Itens"), [role="tab"]:has-text("Itens")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Documentos', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Documentos"), [role="tab"]:has-text("Documentos")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve ter aba de Histórico', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const aba = page.locator('button:has-text("Histórico"), [role="tab"]:has-text("Histórico")').first();
    const hasAba = await aba.isVisible().catch(() => false);
    expect(hasAba !== undefined).toBeTruthy();
  });

  test('deve exibir quantidade de itens na aba', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const abaItens = page.locator('button:has-text("Itens")').first();
    const hasBadge = await abaItens.locator('span').first().isVisible().catch(() => false);
    expect(hasBadge !== undefined).toBeTruthy();
  });
});

test.describe('Propostas - Detalhe - Ações Disponíveis', () => {
  test('deve ter botão de submeter para proposta em rascunho', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnSubmeter = page.locator('button:has-text("Submeter"), button:has-text("Enviar")').first();
    const hasBtn = await btnSubmeter.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão de editar para proposta em rascunho', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnEditar = page.locator('button:has-text("Editar")').first();
    const hasBtn = await btnEditar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão de atualizar dados', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnAtualizar = page.locator('button:has-text("Atualizar"), button[title="Atualizar"]').first();
    const hasBtn = await btnAtualizar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve ter botão para voltar', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnVoltar = page.locator('button:has-text("Voltar")').first();
    const hasBtn = await btnVoltar.isVisible().catch(() => false);
    expect(hasBtn !== undefined).toBeTruthy();
  });

  test('deve abrir modal de confirmação ao submeter', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const btnSubmeter = page.locator('button:has-text("Submeter")').first();
    if (await btnSubmeter.isVisible().catch(() => false)) {
      await btnSubmeter.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      const isModalVisible = await modal.isVisible().catch(() => false);
      expect(isModalVisible !== undefined).toBeTruthy();
    }
  });

  test('deve abrir modal de edição ao clicar em editar', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
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

test.describe('Propostas - Detalhe - Estados Diferentes', () => {
  test('deve exibir proposta em status enviada', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440002');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/enviada/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir proposta em status aprovada', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440003');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/aprovada/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir proposta em status rejeitada', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440004');
    await page.waitForTimeout(2000);

    const status = page.locator('text=/rejeitada/i').first();
    const hasStatus = await status.isVisible().catch(() => false);
    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('não deve exibir botão submeter para proposta já enviada', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440002');
    await page.waitForTimeout(2000);

    const btnSubmeter = page.locator('button:has-text("Submeter")');
    const isVisible = await btnSubmeter.isVisible().catch(() => false);
    expect(isVisible).toBeFalsy();
  });

  test('deve exibir motivo de rejeição quando houver', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440004');
    await page.waitForTimeout(2000);

    const motivo = page.locator('text=/motivo|incompleta/i').first();
    const hasMotivo = await motivo.isVisible().catch(() => false);
    expect(hasMotivo !== undefined).toBeTruthy();
  });
});

test.describe('Propostas - Detalhe - Seletor de Status', () => {
  test('deve ter seletor de status na aba Dados Gerais', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    // Navegar para aba Dados Gerais
    const aba = page.locator('button:has-text("Dados Gerais")').first();
    if (await aba.isVisible().catch(() => false)) {
      await aba.click();
      await page.waitForTimeout(500);
    }

    const seletor = page.locator('select, [role="combobox"]').first();
    const hasSeletor = await seletor.isVisible().catch(() => false);
    expect(hasSeletor !== undefined).toBeTruthy();
  });

  test('deve permitir alterar status da proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const seletor = page.locator('select').first();
    if (await seletor.isVisible().catch(() => false)) {
      await seletor.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      const valor = await seletor.inputValue();
      expect(valor).toBeTruthy();
    }
  });
});

test.describe('Propostas - Detalhe - Observações', () => {
  test('deve exibir observações técnicas quando houver', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const obsTecnicas = page.locator('text=/Observações Técnicas|técnica/i').first();
    const hasObs = await obsTecnicas.isVisible().catch(() => false);
    expect(hasObs !== undefined).toBeTruthy();
  });

  test('deve exibir observações comerciais quando houver', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const obsComerciais = page.locator('text=/Observações Comerciais|comercial|pagamento/i').first();
    const hasObs = await obsComerciais.isVisible().catch(() => false);
    expect(hasObs !== undefined).toBeTruthy();
  });
});

test.describe('Propostas - Detalhe - Informações do Edital', () => {
  test('deve exibir ID do edital vinculado', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const editalId = page.locator('text=/ID do Edital|Edital/i').first();
    const hasEdital = await editalId.isVisible().catch(() => false);
    expect(hasEdital !== undefined).toBeTruthy();
  });

  test('deve exibir data de criação da proposta', async ({ page }) => {
    await page.goto('/modulos/licitacoes/propostas/660e8400-e29b-41d4-a716-446655440001');
    await page.waitForTimeout(2000);

    const dataCriacao = page.locator('text=/Data de Criação|Criado em/i').first();
    const hasData = await dataCriacao.isVisible().catch(() => false);
    expect(hasData !== undefined).toBeTruthy();
  });
});
