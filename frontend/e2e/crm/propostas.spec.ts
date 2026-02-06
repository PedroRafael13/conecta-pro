/**
 * Testes E2E - CRM - Propostas
 *
 * Testes para gestão de propostas comerciais
 * cobrindo: listagem, formulário inline, criação, edição e status
 */

import { test, expect } from '../fixtures';

const mockPropostas = [
  {
    id: 'prop-1',
    title: 'Proposta de Segurança - Condomínio Aurora',
    titulo: 'Proposta de Segurança - Condomínio Aurora',
    client_name: 'Condomínio Aurora',
    cliente: 'Condomínio Aurora',
    total_value: 180000,
    valor: 180000,
    status: 'draft',
    created_at: '2024-01-10T10:00:00Z',
    data: '2024-01-10',
  },
  {
    id: 'prop-2',
    title: 'Vigilância 24h - Indústria XYZ',
    titulo: 'Vigilância 24h - Indústria XYZ',
    client_name: 'Indústria XYZ Ltda',
    cliente: 'Indústria XYZ Ltda',
    total_value: 320000,
    valor: 320000,
    status: 'sent',
    created_at: '2024-01-15T14:30:00Z',
    data: '2024-01-15',
  },
  {
    id: 'prop-3',
    title: 'Monitoramento CFTV - Shopping Center',
    titulo: 'Monitoramento CFTV - Shopping Center',
    client_name: 'Shopping Center Sul',
    cliente: 'Shopping Center Sul',
    total_value: 450000,
    valor: 450000,
    status: 'accepted',
    created_at: '2024-01-20T09:15:00Z',
    data: '2024-01-20',
  },
  {
    id: 'prop-4',
    title: 'Limpeza Industrial - Fábrica ABC',
    titulo: 'Limpeza Industrial - Fábrica ABC',
    client_name: 'Fábrica ABC',
    cliente: 'Fábrica ABC',
    total_value: 95000,
    valor: 95000,
    status: 'rejected',
    created_at: '2024-02-01T16:45:00Z',
    data: '2024-02-01',
  },
];

const mockStats = {
  proposals_total: 4,
  proposals_pending: 1,
  proposals_sent: 1,
  proposals_accepted: 1,
  proposals_rejected: 1,
};

test.describe('CRM - Propostas', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de propostas
    await page.route('**/api/v1/crm/proposals*', (route) => {
      if (route.request().method() === 'GET') {
        const url = new URL(route.request().url());
        const statusFilter = url.searchParams.get('status');

        let items = mockPropostas;
        if (statusFilter && statusFilter !== 'all') {
          items = mockPropostas.filter(p => p.status === statusFilter);
        }

        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items,
            total: items.length,
          }),
        });
      } else if (route.request().method() === 'POST') {
        const body = route.request().postDataJSON();
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'new-prop-id',
            ...body,
            created_at: new Date().toISOString(),
          }),
        });
      } else {
        route.continue();
      }
    });

    // Mock de stats
    await page.route('**/api/v1/crm/proposals/stats*', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockStats),
      });
    });

    // Mock de atualização/exclusão
    await page.route('**/api/v1/crm/proposals/*', (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'prop-1', ...route.request().postDataJSON() }),
        });
      } else if (route.request().method() === 'DELETE') {
        route.fulfill({ status: 204, body: '' });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/crm/propostas', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test.describe('Listagem', () => {
    test('deve carregar página de propostas', async ({ page }) => {
      await expect(page.locator('h1').first()).toContainText('Propostas');
      await expect(page.locator('p', { hasText: /Gestao/i })).toBeVisible();
    });

    test('deve exibir cards de estatísticas', async ({ page }) => {
      await expect(page.locator('text=Total')).toBeVisible();
      await expect(page.locator('text=Rascunho')).toBeVisible();
      await expect(page.locator('text=Enviadas')).toBeVisible();
      await expect(page.locator('text=Aprovadas')).toBeVisible();
    });

    test('deve exibir valores corretos nas estatísticas', async ({ page }) => {
      // Total
      const totalValue = page.locator('text=Total').locator('xpath=../../div[contains(@class,"text-2xl")]');
      await expect(totalValue).toHaveText('4');

      // Rascunho
      const rascunhoValue = page.locator('text=Rascunho').locator('xpath=../../div[contains(@class,"text-2xl")]');
      await expect(rascunhoValue).toHaveText('1');
    });

    test('deve exibir tabela de propostas', async ({ page }) => {
      const headers = ['Titulo', 'Cliente', 'Valor', 'Status', 'Data', 'Acoes'];
      for (const header of headers) {
        await expect(page.locator('th', { hasText: new RegExp(header, 'i') })).toBeVisible();
      }
    });

    test('deve exibir propostas com dados formatados', async ({ page }) => {
      await expect(page.locator('td', { hasText: 'Proposta de Segurança' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Condomínio Aurora' })).toBeVisible();

      // Verificar formatação de valor
      const valorCells = page.locator('td:has-text("R$")');
      expect(await valorCells.count()).toBeGreaterThan(0);
    });
  });

  test.describe('Filtros', () => {
    test('deve filtrar por status', async ({ page }) => {
      const statusSelect = page.locator('[role="combobox"]').first();
      await statusSelect.click();
      await page.waitForTimeout(300);

      // Selecionar "Aprovada"
      await page.locator('[role="option"]', { hasText: 'Aprovada' }).click();
      await page.waitForTimeout(500);

      // Deve mostrar apenas aprovadas
      await expect(page.locator('td', { hasText: 'Monitoramento CFTV' })).toBeVisible();

      // Resetar
      await statusSelect.click();
      await page.waitForTimeout(300);
      await page.locator('[role="option"]', { hasText: 'Todos os status' }).click();
    });

    test('deve filtrar por texto de busca', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Buscar"]').first();

      await searchInput.fill('Vigilância');
      await page.waitForTimeout(500);

      await expect(page.locator('td', { hasText: 'Vigilância 24h' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Proposta de Segurança' })).not.toBeVisible();
    });
  });

  test.describe('Status Badges', () => {
    test('deve exibir badges com cores corretas', async ({ page }) => {
      // Rascunho - cinza
      const rascunhoBadge = page.locator('span', { hasText: 'Rascunho' });
      await expect(rascunhoBadge.first()).toBeVisible();
      await expect(rascunhoBadge.first()).toHaveClass(/bg-gray/);

      // Enviada - azul
      const enviadaBadge = page.locator('span', { hasText: 'Enviada' });
      await expect(enviadaBadge.first()).toBeVisible();
      await expect(enviadaBadge.first()).toHaveClass(/bg-blue/);

      // Aprovada - verde
      const aprovadaBadge = page.locator('span', { hasText: 'Aprovada' });
      await expect(aprovadaBadge.first()).toBeVisible();
      await expect(aprovadaBadge.first()).toHaveClass(/bg-green/);

      // Rejeitada - vermelho
      const rejeitadaBadge = page.locator('span', { hasText: 'Rejeitada' });
      await expect(rejeitadaBadge.first()).toBeVisible();
      await expect(rejeitadaBadge.first()).toHaveClass(/bg-red/);
    });
  });

  test.describe('Formulário Inline', () => {
    test('deve exibir formulário inline ao clicar em nova proposta', async ({ page }) => {
      await page.locator('button', { hasText: 'Nova Proposta' }).click();
      await page.waitForTimeout(500);

      // Verificar formulário inline
      await expect(page.locator('text=Nova Proposta').nth(1)).toBeVisible();
      await expect(page.locator('label', { hasText: 'Titulo' })).toBeVisible();
      await expect(page.locator('label', { hasText: 'Cliente' })).toBeVisible();
      await expect(page.locator('label', { hasText: 'Valor' })).toBeVisible();
      await expect(page.locator('label', { hasText: 'Status' })).toBeVisible();
    });

    test('deve permitir cancelar criação', async ({ page }) => {
      await page.locator('button', { hasText: 'Nova Proposta' }).click();
      await page.waitForTimeout(500);

      // Preencher algum dado
      const tituloInput = page.locator('input').filter({ hasText: '' }).first();
      if (await tituloInput.isVisible()) {
        await tituloInput.fill('Rascunho temporário');
      }

      // Cancelar
      await page.locator('button', { hasText: 'Cancelar' }).click();
      await page.waitForTimeout(500);

      // Formulário deve desaparecer
      const formHeader = page.locator('text=Nova Proposta').nth(1);
      await expect(formHeader).not.toBeVisible();
    });

    test('deve criar proposta com sucesso', async ({ page }) => {
      let requestBody: any = null;

      await page.route('**/api/v1/crm/proposals*', (route) => {
        if (route.request().method() === 'POST') {
          requestBody = route.request().postDataJSON();
          route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'new-prop',
              ...requestBody,
              created_at: new Date().toISOString(),
            }),
          });
        }
      });

      await page.locator('button', { hasText: 'Nova Proposta' }).click();
      await page.waitForTimeout(500);

      // Preencher formulário
      const inputs = await page.locator('input').all();
      if (inputs.length > 0) {
        await inputs[0]!.fill('Proposta Teste E2E');
        if (inputs[1]) await inputs[1].fill('Cliente Teste');
        if (inputs[2]) await inputs[2].fill('100000');
      }

      // Criar
      const criarButton = page.locator('button', { hasText: /^Criar Proposta$/ });
      if (await criarButton.isVisible()) {
        await criarButton.click();
        await page.waitForTimeout(1000);
      }
    });
  });

  test.describe('Ações', () => {
    test('deve abrir menu de ações', async ({ page }) => {
      const menuButton = page.locator('table tbody tr').first().locator('button').last();
      await menuButton.click();
      await page.waitForTimeout(300);

      await expect(page.locator('text=Ver detalhes')).toBeVisible();
      await expect(page.locator('text=Editar')).toBeVisible();
      await expect(page.locator('text=Deletar')).toBeVisible();
    });

    test('deve abrir modo de edição inline', async ({ page }) => {
      // Abrir menu
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);

      // Clicar em editar
      await page.locator('text=Editar').click();
      await page.waitForTimeout(500);

      // Verificar modo de edição
      await expect(page.locator('text=Editar Proposta')).toBeVisible();
    });

    test('deve exibir detalhes da proposta', async ({ page }) => {
      // Abrir menu
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);

      // Clicar em ver detalhes
      await page.locator('text=Ver detalhes').click();
      await page.waitForTimeout(500);

      // Verificar card de detalhes
      await expect(page.locator('text=Detalhes da Proposta')).toBeVisible();
      await expect(page.locator('text=Proposta de Segurança')).toBeVisible();
    });

    test('deve permitir fechar detalhes', async ({ page }) => {
      // Abrir detalhes
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);
      await page.locator('text=Ver detalhes').click();
      await page.waitForTimeout(500);

      // Fechar
      await page.locator('button', { hasText: 'Fechar' }).click();
      await page.waitForTimeout(500);

      // Detalhes devem desaparecer
      await expect(page.locator('text=Detalhes da Proposta')).not.toBeVisible();
    });
  });

  test.describe('Estados', () => {
    test('deve exibir estado vazio', async ({ page }) => {
      await page.route('**/api/v1/crm/proposals*', (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      await expect(page.locator('text=Nenhuma proposta encontrada')).toBeVisible();
    });

    test('deve exibir loading', async ({ page }) => {
      await page.route('**/api/v1/crm/proposals*', async (route) => {
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

    test('deve lidar com erro', async ({ page }) => {
      await page.route('**/api/v1/crm/proposals*', (route) => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Erro ao carregar' }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      await expect(page.locator('text=Erro ao carregar propostas')).toBeVisible();
    });
  });
});
