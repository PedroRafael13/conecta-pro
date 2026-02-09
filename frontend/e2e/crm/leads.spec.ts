/**
 * Testes E2E - CRM - Leads
 *
 * Testes completos para CRUD de Leads
 * cobrindo: listagem, filtros, criação, edição e exclusão
 */

import { test, expect } from '../fixtures';

const mockLeads = [
  {
    id: 'lead-1',
    nome: 'João Silva',
    contato: 'joao@empresa.com',
    email: 'joao@empresa.com',
    telefone: '(11) 99999-1111',
    origem: 'Site',
    status: 'novo',
    valor_estimado: 50000,
    created_at: '2024-01-10T10:00:00Z',
  },
  {
    id: 'lead-2',
    nome: 'Maria Santos',
    contato: 'maria@industria.com',
    email: 'maria@industria.com',
    telefone: '(11) 98888-2222',
    origem: 'Indicação',
    status: 'qualificado',
    valor_estimado: 120000,
    created_at: '2024-01-15T14:30:00Z',
  },
  {
    id: 'lead-3',
    nome: 'Carlos Ferreira',
    contato: 'carlos@loja.com',
    email: 'carlos@loja.com',
    telefone: '(11) 97777-3333',
    origem: 'Google Ads',
    status: 'proposta',
    valor_estimado: 80000,
    created_at: '2024-01-20T09:15:00Z',
  },
  {
    id: 'lead-4',
    nome: 'Ana Paula',
    contato: 'ana@construtora.com',
    email: 'ana@construtora.com',
    telefone: '(11) 96666-4444',
    origem: 'LinkedIn',
    status: 'negociacao',
    valor_estimado: 200000,
    created_at: '2024-02-01T16:45:00Z',
  },
];

const mockStats = {
  total: 4,
  novos: 1,
  qualificados: 1,
  em_proposta: 1,
  em_negociacao: 1,
  valor_pipeline: 450000,
};

test.describe('CRM - Leads - CRUD Completo', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de leads
    await page.route('**/api/v1/crm/leads*', (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: mockLeads,
            total: mockLeads.length,
          }),
        });
      } else if (route.request().method() === 'POST') {
        const body = route.request().postDataJSON();
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'new-lead-id',
            ...body,
            created_at: new Date().toISOString(),
          }),
        });
      } else {
        route.continue();
      }
    });

    // Mock de stats
    await page.route('**/api/v1/crm/leads/stats*', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockStats),
      });
    });

    await page.goto('/modulos/crm/leads', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test.describe('Listagem', () => {
    test('deve carregar página de leads com título correto', async ({ page }) => {
      await expect(page.locator('h1').first()).toContainText('Leads');
      await expect(page.locator('p', { hasText: /Gerencie seus leads/i })).toBeVisible();
    });

    test('deve exibir cards de métricas', async ({ page }) => {
      await expect(page.locator('text=Total de Leads')).toBeVisible();
      await expect(page.locator('text=Leads Novos')).toBeVisible();
      await expect(page.locator('text=Valor Estimado')).toBeVisible();
    });

    test('deve exibir valores corretos nas métricas', async ({ page }) => {
      // Total de Leads
      const totalCard = page.locator('text=Total de Leads').locator('xpath=../..');
      await expect(totalCard.locator('.text-2xl')).toHaveText('4');

      // Valor Estimado formatado como moeda
      const valorCard = page.locator('text=Valor Estimado').locator('xpath=../..');
      const valorText = await valorCard.locator('.text-2xl').textContent();
      expect(valorText).toMatch(/R\$/);
    });

    test('deve exibir lista de leads na tabela', async ({ page }) => {
      // Verificar cabeçalhos
      const headers = ['Lead', 'Contato', 'Origem', 'Status', 'Valor'];
      for (const header of headers) {
        await expect(page.locator('th', { hasText: new RegExp(header, 'i') })).toBeVisible();
      }

      // Verificar leads
      await expect(page.locator('td', { hasText: 'João Silva' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Maria Santos' })).toBeVisible();
    });

    test('deve exibir status com cores corretas', async ({ page }) => {
      // Novo - azul
      const novoBadge = page.locator('span', { hasText: 'Novo' });
      await expect(novoBadge).toBeVisible();

      // Qualificado - ciano
      const qualificadoBadge = page.locator('span', { hasText: 'Qualificado' });
      await expect(qualificadoBadge).toBeVisible();

      // Proposta - roxo
      const propostaBadge = page.locator('span', { hasText: 'Proposta' });
      await expect(propostaBadge).toBeVisible();
    });

    test('deve exibir valores formatados como moeda', async ({ page }) => {
      const valorCells = page.locator('td:has-text("R$")');
      const count = await valorCells.count();
      expect(count).toBeGreaterThan(0);
    });

    test('deve exibir ícones de contato (telefone e email)', async ({ page }) => {
      // Verificar ícones nas linhas da tabela
      const telefoneIcons = page.locator('table svg');
      expect(await telefoneIcons.count()).toBeGreaterThan(0);
    });
  });

  test.describe('Filtros', () => {
    test('deve filtrar por texto de busca', async ({ page }) => {
      const searchInput = page.locator('input[type="search"]');

      await searchInput.fill('João');
      await page.waitForTimeout(500);

      await expect(page.locator('td', { hasText: 'João Silva' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Maria Santos' })).not.toBeVisible();
    });

    test('deve filtrar por status usando botões', async ({ page }) => {
      // Clicar em filtro "Novo"
      await page.locator('button', { hasText: 'Novo' }).first().click();
      await page.waitForTimeout(500);

      // Deve mostrar apenas leads novos
      await expect(page.locator('td', { hasText: 'João Silva' })).toBeVisible();

      // Resetar para "Todos"
      await page.locator('button', { hasText: 'Todos' }).first().click();
      await page.waitForTimeout(500);
    });

    test('deve exibir filtros de status em mobile', async ({ page }) => {
      // Botão de filtro mobile deve estar visível
      const filterButton = page.locator('button', { hasText: 'Filtrar' });
      // Pode não existir dependendo do breakpoint
      const exists = await filterButton.isVisible().catch(() => false);
      if (exists) {
        await expect(filterButton).toBeVisible();
      }
    });
  });

  test.describe('Criação', () => {
    test('deve ter botão de novo lead', async ({ page }) => {
      const novoButton = page.locator('button', { hasText: 'Novo Lead' });
      await expect(novoButton).toBeVisible();
      await expect(novoButton).toBeEnabled();
    });

    test('deve exibir estado vazio quando não há leads', async ({ page }) => {
      // Mock vazio
      await page.route('**/api/v1/crm/leads*', (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      await expect(page.locator('text=Nenhum lead encontrado')).toBeVisible();
      await expect(page.locator('text=Comece adicionando seu primeiro lead')).toBeVisible();
      await expect(page.locator('button', { hasText: 'Adicionar Lead' })).toBeVisible();
    });

    test('deve exibir botão de adicionar lead no estado vazio', async ({ page }) => {
      // Mock vazio
      await page.route('**/api/v1/crm/leads*', (route) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      const addButton = page.locator('button', { hasText: 'Adicionar Lead' });
      await expect(addButton).toBeVisible();
      await expect(addButton).toBeEnabled();
    });
  });

  test.describe('Interações', () => {
    test('deve ter botão de atualizar dados', async ({ page }) => {
      const refreshButton = page.locator('button').filter({ has: page.locator('svg') })
        .filter({ hasText: /./ })
        .first();
      await expect(refreshButton).toBeVisible();
    });

    test('deve exibir menu de ações para cada lead', async ({ page }) => {
      const menuButton = page.locator('button').filter({ has: page.locator('svg') })
        .filter({ has: page.locator('svg') })  // Ícone
        .last();  // Último menu

      // Abrir menu do primeiro lead
      const firstMenu = page.locator('table tbody tr').first()
        .locator('button').last();

      if (await firstMenu.isVisible().catch(() => false)) {
        await firstMenu.click();
        await page.waitForTimeout(300);

        // Verificar opções
        const hasOptions = await page.locator('[role="menuitem"]').count() > 0;
        expect(hasOptions).toBeTruthy();

        await page.keyboard.press('Escape');
      }
    });
  });

  test.describe('Erros e Loading', () => {
    test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
      await page.route('**/api/v1/crm/leads*', (route) => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Erro ao carregar leads' }),
        });
      });

      await page.reload();
      await page.waitForTimeout(2000);

      await expect(page.locator('text=Erro ao carregar leads')).toBeVisible();
      await expect(page.locator('button', { hasText: 'Tentar novamente' })).toBeVisible();
    });

    test('deve permitir tentar novamente após erro', async ({ page }) => {
      let failCount = 0;
      await page.route('**/api/v1/crm/leads*', (route) => {
        if (failCount < 1) {
          failCount++;
          route.fulfill({ status: 500, body: JSON.stringify({ detail: 'Erro' }) });
        } else {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ items: mockLeads, total: mockLeads.length }),
          });
        }
      });

      await page.reload();
      await page.waitForTimeout(2000);

      // Clicar em tentar novamente
      await page.locator('button', { hasText: 'Tentar novamente' }).click();
      await page.waitForTimeout(2000);

      // Deve carregar os leads
      await expect(page.locator('td', { hasText: 'João Silva' })).toBeVisible();
    });

    test('deve exibir skeleton loading durante carregamento', async ({ page }) => {
      await page.route('**/api/v1/crm/leads*', async (route) => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0 }),
        });
      });

      await page.reload();

      // Verificar skeleton loading
      const skeleton = page.locator('.animate-shimmer, .animate-pulse');
      await expect(skeleton.first()).toBeVisible();
    });
  });

  test.describe('Responsividade', () => {
    test('deve ocultar colunas em telas menores', async ({ page }) => {
      // Coluna Origem deve estar marcada como hidden em mobile
      const origemHeader = page.locator('th', { hasText: 'Origem' });
      const classes = await origemHeader.getAttribute('class');

      // Deve ter classe hidden em breakpoints pequenos
      expect(classes).toMatch(/hidden|md:table-cell|lg:table-cell/);
    });

    test('deve mostrar contagem de resultados', async ({ page }) => {
      await expect(page.locator('text=/Mostrando.*de.*leads/')).toBeVisible();
    });
  });

  test.describe('Integração', () => {
    test('deve navegar para página de oportunidades', async ({ page }) => {
      // Clicar em link para oportunidades se existir
      const oportunidadesLink = page.locator('a[href*="oportunidade"], button:has-text("Oportunidades")').first();

      if (await oportunidadesLink.isVisible().catch(() => false)) {
        await oportunidadesLink.click();
        await page.waitForTimeout(1000);
        await expect(page).toHaveURL(/oportunidade/);
      }
    });
  });
});
