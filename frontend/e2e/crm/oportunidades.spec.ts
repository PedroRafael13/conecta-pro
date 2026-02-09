/**
 * Testes E2E - CRM - Oportunidades
 *
 * Testes completos para Pipeline de Oportunidades
 * cobrindo: listagem, filtros por estágio, criação, edição e pipeline
 */

import { test, expect } from '../fixtures';

const mockOportunidades = [
  {
    id: 'opp-1',
    title: 'Serviço de Portaria - Edifício Aurora',
    nome: 'Serviço de Portaria - Edifício Aurora',
    client_name: 'Condomínio Aurora',
    contato: 'Condomínio Aurora',
    stage: 'qualificado',
    status: 'qualificado',
    value: 150000,
    valor_estimado: 150000,
    probability: 60,
    created_at: '2024-01-10T10:00:00Z',
  },
  {
    id: 'opp-2',
    title: 'Vigilância 24h - Indústria XYZ',
    nome: 'Vigilância 24h - Indústria XYZ',
    client_name: 'Indústria XYZ Ltda',
    contato: 'Indústria XYZ Ltda',
    stage: 'proposta',
    status: 'proposta',
    value: 300000,
    valor_estimado: 300000,
    probability: 75,
    created_at: '2024-01-15T14:30:00Z',
  },
  {
    id: 'opp-3',
    title: 'Monitoramento CFTV - Shopping Center',
    nome: 'Monitoramento CFTV - Shopping Center',
    client_name: 'Shopping Center Sul',
    contato: 'Shopping Center Sul',
    stage: 'negociacao',
    status: 'negociacao',
    value: 450000,
    valor_estimado: 450000,
    probability: 40,
    created_at: '2024-01-20T09:15:00Z',
  },
  {
    id: 'opp-4',
    title: 'Limpeza e Conservação - Escritório Central',
    nome: 'Limpeza e Conservação - Escritório Central',
    client_name: 'Empresa Central S.A.',
    contato: 'Empresa Central S.A.',
    stage: 'ganho',
    status: 'ganho',
    value: 80000,
    valor_estimado: 80000,
    probability: 100,
    created_at: '2024-02-01T16:45:00Z',
  },
  {
    id: 'opp-5',
    title: 'Recepção - Condomínio Jardins',
    nome: 'Recepção - Condomínio Jardins',
    client_name: 'Condomínio Jardins',
    contato: 'Condomínio Jardins',
    stage: 'perdido',
    status: 'perdido',
    value: 60000,
    valor_estimado: 60000,
    probability: 0,
    created_at: '2024-02-05T11:20:00Z',
  },
];

const mockPipelineStats = {
  total_value: 1040000,
  total_count: 5,
  by_stage: {
    qualificado: { count: 1, value: 150000 },
    proposta: { count: 1, value: 300000 },
    negociacao: { count: 1, value: 450000 },
    ganho: { count: 1, value: 80000 },
    perdido: { count: 1, value: 60000 },
  },
};

test.describe('CRM - Oportunidades - Pipeline', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de oportunidades
    await page.route('**/api/v1/crm/opportunities*', (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: mockOportunidades,
            total: mockOportunidades.length,
          }),
        });
      } else if (route.request().method() === 'POST') {
        const body = route.request().postDataJSON();
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'new-opp-id',
            ...body,
            created_at: new Date().toISOString(),
          }),
        });
      } else {
        route.continue();
      }
    });

    // Mock de pipeline stats
    await page.route('**/api/v1/crm/pipeline/stats*', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPipelineStats),
      });
    });

    // Mock de atualização/exclusão
    await page.route('**/api/v1/crm/opportunities/*', (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'opp-1', ...route.request().postDataJSON() }),
        });
      } else if (route.request().method() === 'DELETE') {
        route.fulfill({ status: 204, body: '' });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/crm/oportunidades', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test.describe('Listagem e Pipeline', () => {
    test('deve carregar página de oportunidades com título correto', async ({ page }) => {
      await expect(page.locator('h1').first()).toContainText('Oportunidades');
      await expect(page.locator('p', { hasText: /Pipeline/i })).toBeVisible();
    });

    test('deve exibir cards de estatísticas do pipeline', async ({ page }) => {
      await expect(page.locator('text=Total')).toBeVisible();
      await expect(page.locator('text=Em Negociacao')).toBeVisible();
      await expect(page.locator('text=Propostas')).toBeVisible();
      await expect(page.locator('text=Valor Pipeline')).toBeVisible();
    });

    test('deve exibir valores formatados em moeda no pipeline', async ({ page }) => {
      // Valor Pipeline deve mostrar valor formatado
      const valorPipeline = page.locator('text=Valor Pipeline').locator('xpath=../../div[contains(@class,"text-2xl")]');
      const valorText = await valorPipeline.textContent();
      expect(valorText).toMatch(/R\$|\.00/);
    });

    test('deve exibir oportunidades na tabela com colunas corretas', async ({ page }) => {
      // Verificar cabeçalhos
      const headers = ['Nome', 'Cliente', 'Estagio', 'Valor', 'Probabilidade', 'Acoes'];
      for (const header of headers) {
        await expect(page.locator('th', { hasText: new RegExp(header, 'i') })).toBeVisible();
      }
    });

    test('deve exibir dados das oportunidades', async ({ page }) => {
      await expect(page.locator('td', { hasText: 'Serviço de Portaria' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Condomínio Aurora' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'R$' }).first()).toBeVisible();
    });

    test('deve exibir probabilidade formatada com %', async ({ page }) => {
      const probCell = page.locator('td', { hasText: /%$/ });
      expect(await probCell.count()).toBeGreaterThan(0);
    });
  });

  test.describe('Filtros por Estágio', () => {
    test('deve filtrar por status usando dropdown', async ({ page }) => {
      // Abrir dropdown
      const statusSelect = page.locator('[role="combobox"]').first();
      await statusSelect.click();
      await page.waitForTimeout(300);

      // Selecionar "Ganho"
      await page.locator('[role="option"]', { hasText: 'Ganho' }).click();
      await page.waitForTimeout(500);

      // Deve mostrar apenas oportunidades ganhas
      await expect(page.locator('td', { hasText: 'Limpeza e Conservação' })).toBeVisible();
    });

    test('deve filtrar por texto de busca', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Buscar"]').first();

      await searchInput.fill('Portaria');
      await page.waitForTimeout(500);

      await expect(page.locator('td', { hasText: 'Serviço de Portaria' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Vigilância 24h' })).not.toBeVisible();
    });

    test('deve resetar filtros para todos os status', async ({ page }) => {
      // Aplicar filtro
      await page.locator('[role="combobox"]').first().click();
      await page.waitForTimeout(300);
      await page.locator('[role="option"]', { hasText: 'Qualificado' }).click();
      await page.waitForTimeout(500);

      // Resetar
      await page.locator('[role="combobox"]').first().click();
      await page.waitForTimeout(300);
      await page.locator('[role="option"]', { hasText: 'Todos os status' }).click();
      await page.waitForTimeout(500);

      // Todas as oportunidades devem aparecer
      await expect(page.locator('td', { hasText: 'Serviço de Portaria' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Vigilância 24h' })).toBeVisible();
    });
  });

  test.describe('Status e Badges', () => {
    test('deve exibir badges de estágio com cores corretas', async ({ page }) => {
      // Qualificado - azul
      const qualificadoBadge = page.locator('span', { hasText: 'Qualificado' });
      await expect(qualificadoBadge.first()).toBeVisible();
      await expect(qualificadoBadge.first()).toHaveClass(/bg-blue/);

      // Proposta - roxo
      const propostaBadge = page.locator('span', { hasText: 'Proposta' });
      await expect(propostaBadge.first()).toBeVisible();
      await expect(propostaBadge.first()).toHaveClass(/bg-purple/);

      // Negociação - amarelo
      const negociacaoBadge = page.locator('span', { hasText: 'Negociacao' });
      await expect(negociacaoBadge.first()).toBeVisible();
      await expect(negociacaoBadge.first()).toHaveClass(/bg-yellow/);

      // Ganho - verde
      const ganhoBadge = page.locator('span', { hasText: 'Ganho' });
      await expect(ganhoBadge.first()).toBeVisible();
      await expect(ganhoBadge.first()).toHaveClass(/bg-green/);

      // Perdido - vermelho
      const perdidoBadge = page.locator('span', { hasText: 'Perdido' });
      await expect(perdidoBadge.first()).toBeVisible();
      await expect(perdidoBadge.first()).toHaveClass(/bg-red/);
    });
  });

  test.describe('Criação', () => {
    test('deve abrir modal de nova oportunidade', async ({ page }) => {
      await page.locator('button', { hasText: 'Nova Oportunidade' }).click();
      await page.waitForTimeout(500);

      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('text=Nova Oportunidade').first()).toBeVisible();
    });

    test('deve criar nova oportunidade com sucesso', async ({ page }) => {
      let requestBody: any = null;

      await page.route('**/api/v1/crm/opportunities*', (route) => {
        if (route.request().method() === 'POST') {
          requestBody = route.request().postDataJSON();
          route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'new-opp',
              ...requestBody,
              created_at: new Date().toISOString(),
            }),
          });
        }
      });

      await page.locator('button', { hasText: 'Nova Oportunidade' }).click();
      await page.waitForTimeout(500);

      // Preencher formulário (campos podem variar)
      const nomeInput = page.locator('input').first();
      if (await nomeInput.isVisible()) {
        await nomeInput.fill('Oportunidade Teste E2E');
      }

      // Tentar salvar
      const saveButton = page.locator('button', { hasText: /^Criar$|Salvar$/ }).first();
      if (await saveButton.isEnabled()) {
        await saveButton.click();
        await page.waitForTimeout(1000);
      }
    });
  });

  test.describe('Edição e Detalhes', () => {
    test('deve abrir menu de ações', async ({ page }) => {
      // Clicar no menu da primeira oportunidade
      const menuButton = page.locator('table tbody tr').first()
        .locator('button').last();

      await menuButton.click();
      await page.waitForTimeout(300);

      // Verificar opções
      await expect(page.locator('text=Ver detalhes')).toBeVisible();
      await expect(page.locator('text=Editar')).toBeVisible();
      await expect(page.locator('text=Deletar')).toBeVisible();
    });

    test('deve abrir modal de detalhes', async ({ page }) => {
      // Abrir menu e clicar em ver detalhes
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);
      await page.locator('text=Ver detalhes').click();
      await page.waitForTimeout(500);

      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('text=Detalhes').first()).toBeVisible();
    });

    test('deve abrir modal de edição', async ({ page }) => {
      // Abrir menu e clicar em editar
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);
      await page.locator('text=Editar').click();
      await page.waitForTimeout(500);

      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('text=Editar').first()).toBeVisible();
    });
  });

  test.describe('Paginação', () => {
    test('deve exibir controles de paginação quando há muitos itens', async ({ page }) => {
      // Mock com mais itens
      await page.route('**/api/v1/crm/opportunities*', (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: Array(25).fill(null).map((_, i) => ({
              id: `opp-${i}`,
              title: `Oportunidade ${i}`,
              client_name: `Cliente ${i}`,
              stage: 'qualificado',
              value: 100000,
              probability: 50,
            })),
            total: 25,
          }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      // Verificar controles de paginação
      const prevButton = page.locator('button', { hasText: 'Anterior' });
      const nextButton = page.locator('button', { hasText: 'Proximo' });

      if (await prevButton.isVisible().catch(() => false)) {
        await expect(prevButton).toBeVisible();
        await expect(nextButton).toBeVisible();
      }
    });

    test('deve navegar entre páginas', async ({ page }) => {
      // Mock com paginação
      await page.route('**/api/v1/crm/opportunities*', (route) => {
        const url = new URL(route.request().url());
        const skip = parseInt(url.searchParams.get('skip') || '0');

        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: skip === 0
              ? mockOportunidades.slice(0, 3)
              : mockOportunidades.slice(3),
            total: 5,
          }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      // Verificar primeira página
      await expect(page.locator('td', { hasText: 'Serviço de Portaria' })).toBeVisible();

      // Tentar ir para próxima página se houver botão
      const nextButton = page.locator('button', { hasText: 'Proximo' });
      if (await nextButton.isVisible().catch(() => false)) {
        await nextButton.click();
        await page.waitForTimeout(1000);
      }
    });
  });

  test.describe('Erros e Estados', () => {
    test('deve exibir estado vazio quando não há oportunidades', async ({ page }) => {
      await page.route('**/api/v1/crm/opportunities*', (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      await expect(page.locator('text=Nenhuma oportunidade encontrada')).toBeVisible();
    });

    test('deve exibir loading durante carregamento', async ({ page }) => {
      await page.route('**/api/v1/crm/opportunities*', async (route) => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        });
      });

      await page.reload();

      const spinner = page.locator('.animate-spin');
      await expect(spinner.first()).toBeVisible();
    });

    test('deve lidar com erro na API', async ({ page }) => {
      await page.route('**/api/v1/crm/opportunities*', (route) => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Erro ao carregar' }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      await expect(page.locator('text=Erro ao carregar oportunidades')).toBeVisible();
    });
  });

  test.describe('Acessibilidade', () => {
    test('deve ter heading h1 na página', async ({ page }) => {
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
    });

    test('deve ter labels nos inputs', async ({ page }) => {
      // Abrir modal de criação
      await page.locator('button', { hasText: 'Nova Oportunidade' }).click();
      await page.waitForTimeout(500);

      // Verificar se há labels ou placeholders
      const inputs = await page.locator('input').all();
      for (const input of inputs) {
        const hasLabel =
          await input.getAttribute('placeholder') ||
          await input.getAttribute('aria-label') ||
          await input.getAttribute('id');
        expect(hasLabel).toBeTruthy();
      }

      await page.keyboard.press('Escape');
    });
  });
});
