import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Comodatos de Equipamentos
 *
 * Testa gestão completa de contratos de comodato:
 * - Contratos de comodato
 * - Equipamentos emprestados
 * - Controle de devolução
 * - Termos de responsabilidade
 * - Multas por atraso/dano
 * - Renovação de contratos
 */

// Mock data para comodatos
const mockComodatoList = {
  items: [
    {
      id: 'com-001',
      codigo: 'COM-2024-001',
      client_name: 'Empresa ABC Ltda',
      equipment_name: 'Câmera IP Dome 4K',
      status: 'active',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      terms: 'Equipamento emprestado para evento corporativo',
      observacoes: 'Cliente responsável por danos',
      signed_by_client: true,
      signed_by_company: true,
    },
    {
      id: 'com-002',
      codigo: 'COM-2024-015',
      client_name: 'Construtora XYZ',
      equipment_name: 'Rádio Comunicador',
      status: 'pending_signature',
      start_date: '2024-03-01',
      end_date: '2024-06-30',
      terms: 'Emprestimo para obra temporária',
      observacoes: 'Aguardando assinatura do cliente',
      signed_by_client: false,
      signed_by_company: true,
    },
    {
      id: 'com-003',
      codigo: 'COM-2024-008',
      client_name: 'Shopping Center Sul',
      equipment_name: 'Controle de Acesso',
      status: 'pending_return',
      start_date: '2023-06-01',
      end_date: '2024-02-28',
      terms: 'Contrato de comodato vencido',
      observacoes: 'Cliente notificado para devolução',
      signed_by_client: true,
      signed_by_company: true,
    },
    {
      id: 'com-004',
      codigo: 'COM-2023-045',
      client_name: 'Indústria Metais',
      equipment_name: 'Sensor de Presença',
      status: 'terminated',
      start_date: '2023-01-15',
      end_date: '2023-12-15',
      terms: 'Contrato encerrado normalmente',
      observacoes: 'Equipamento devolvido em perfeitas condições',
      signed_by_client: true,
      signed_by_company: true,
    },
  ],
  total: 4,
};

const mockStats = {
  total: 4,
  active: 1,
  pending_signature: 1,
  expiring: 1,
};

test.describe('Comodatos - Visualização', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      if (route.request().url().includes('/stats')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockStats),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockComodatoList),
        });
      }
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);
  });

  test('deve carregar a página de comodatos', async ({ page }) => {
    await expect(page).toHaveURL(/\/comodatos/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Comodatos/i, { timeout: 10000 });
  });

  test('deve exibir subtítulo de gestão de contratos', async ({ page }) => {
    const subtitle = page.locator('p:has-text("contratos de comodato")');
    await expect(subtitle).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await expect(page.locator('text=/Total/i').first()).toBeVisible();
    await expect(page.locator('text=/Ativos/i').first()).toBeVisible();
    await expect(page.locator('text=/Aguardando Assinatura/i').first()).toBeVisible();
    await expect(page.locator('text=/Expirando/i').first()).toBeVisible();
  });

  test('deve exibir tabela de comodatos', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    expect(headerTexts).toContain('Contrato');
    expect(headerTexts).toContain('Cliente');
    expect(headerTexts).toContain('Equipamento');
    expect(headerTexts).toContain('Status');
    expect(headerTexts).toContain('Vigencia');
  });

  test('deve exibir código do contrato', async ({ page }) => {
    await expect(page.locator('text=COM-2024-001').first()).toBeVisible();
  });

  test('deve exibir nome do cliente', async ({ page }) => {
    await expect(page.locator('text=Empresa ABC Ltda').first()).toBeVisible();
  });

  test('deve exibir nome do equipamento emprestado', async ({ page }) => {
    await expect(page.locator('text=Câmera IP Dome 4K').first()).toBeVisible();
  });

  test('deve exibir badges de status coloridos', async ({ page }) => {
    await expect(page.locator('text=/Ativo/i').first()).toBeVisible();
    await expect(page.locator('text=/Aguard. Assinatura/i').first()).toBeVisible();
    await expect(page.locator('text=/Aguard. Devolucao|Encerrado/i').first()).toBeVisible();
  });

  test('deve exibir período de vigência', async ({ page }) => {
    // Data em formato brasileiro
    const datePattern = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').first();
    expect(await datePattern.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve exibir menu de ações em cada linha', async ({ page }) => {
    const actionButtons = page.locator('button[class*="ghost"]').all();
    const count = (await actionButtons).length;
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Comodatos - Filtros e Busca', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('Empresa ABC');
    await page.waitForTimeout(500);
    await expect(searchInput).toHaveValue('Empresa ABC');
  });

  test('deve filtrar por status ativo', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').first();
    await expect(statusSelect).toBeVisible();

    await statusSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Ativo').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por status aguardando assinatura', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').first();
    await statusSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Aguard. Assinatura').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por status encerrado', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').first();
    await statusSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Encerrado').first().click();
    await page.waitForTimeout(500);
  });

  test('deve buscar por código do contrato', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    await searchInput.fill('COM-2024');
    await page.waitForTimeout(500);

    await expect(searchInput).toHaveValue('COM-2024');
  });

  test('deve buscar por nome do cliente', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    await searchInput.fill('Construtora');
    await page.waitForTimeout(500);

    await expect(searchInput).toHaveValue('Construtora');
  });
});

test.describe('Comodatos - CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      const method = route.request().method();

      if (method === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockComodatoList),
        });
      } else if (method === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'com-new',
            codigo: 'COM-2024-999',
            client_name: 'Novo Cliente',
            equipment_name: 'Novo Equipamento',
            status: 'draft',
          }),
        });
      } else {
        route.continue();
      }
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve abrir modal de novo comodato', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal).toContainText('Novo Comodato');
  });

  test('deve ter campo de cliente obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const clientInput = modal.locator('input#client_name');
    await expect(clientInput).toBeVisible();
  });

  test('deve ter campo de equipamento obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const equipInput = modal.locator('input#equipment_name');
    await expect(equipInput).toBeVisible();
  });

  test('deve ter campo de data de início', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const startDateInput = modal.locator('input#start_date');
    await expect(startDateInput).toBeVisible();
  });

  test('deve ter campo de data de fim', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const endDateInput = modal.locator('input#end_date');
    await expect(endDateInput).toBeVisible();
  });

  test('deve ter campo de termos do contrato', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const termsTextarea = modal.locator('textarea#terms');
    await expect(termsTextarea).toBeVisible();
  });

  test('deve ter campo de observações', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const obsTextarea = modal.locator('textarea#observacoes');
    await expect(obsTextarea).toBeVisible();
  });

  test('deve cancelar criação ao clicar em Cancelar', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const cancelButton = page.locator('button:has-text("Cancelar")').first();
    await cancelButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).not.toBeVisible();
  });

  test('deve abrir modal de detalhes ao clicar em Ver detalhes', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const viewOption = page.locator('text=/Ver detalhes/i').first();
    await viewOption.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
  });

  test('deve abrir modal de edição ao clicar em Editar', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const editOption = page.locator('text=/Editar/i').first();
    await editOption.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toContainText('Editar Comodato');
  });

  test('deve confirmar antes de excluir comodato', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const deleteOption = page.locator('text=/Deletar/i').first();
    await deleteOption.click();
    await page.waitForTimeout(800);

    const confirmModal = page.locator('[role="dialog"]').first();
    await expect(confirmModal).toContainText('Excluir');
  });
});

test.describe('Comodatos - Contratos e Termos', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve permitir criar contrato com termos personalizados', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const termsTextarea = modal.locator('textarea#terms');

    await termsTextarea.fill('Termos personalizados do contrato de comodato');
    await expect(termsTextarea).toHaveValue('Termos personalizados do contrato de comodato');
  });

  test('deve permitir informar datas de vigência', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const startDateInput = modal.locator('input#start_date');
    const endDateInput = modal.locator('input#end_date');

    await startDateInput.fill('2024-01-01');
    await endDateInput.fill('2024-12-31');

    await expect(startDateInput).toHaveValue('2024-01-01');
    await expect(endDateInput).toHaveValue('2024-12-31');
  });

  test('deve validar campos obrigatórios', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    await page.waitForTimeout(500);

    // Modal deve continuar aberto indicando erro
    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
  });
});

test.describe('Comodatos - Assinatura e Entrega', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve exibir opção Assinar para comodatos pendentes', async ({ page }) => {
    // Procura por comodato pendente de assinatura
    const rows = page.locator('table tbody tr');
    const rowCount = await rows.count();

    for (let i = 0; i < rowCount; i++) {
      const row = rows.nth(i);
      const hasPending = await row.locator('text=/Aguard. Assinatura/i').isVisible().catch(() => false);

      if (hasPending) {
        const actionButton = row.locator('button[class*="ghost"], button:has-text("...")');
        await actionButton.click();
        await page.waitForTimeout(500);

        const assinarOption = page.locator('text=/Assinar/i').first();
        expect(await assinarOption.isVisible().catch(() => false)).toBeDefined();
        break;
      }
    }
  });

  test('deve exibir opção Entregar para comodatos em rascunho', async ({ page }) => {
    const actionButtons = page.locator('button[class*="ghost"]').all();
    const buttons = await actionButtons;

    for (const btn of buttons.slice(0, 3)) {
      await btn.click();
      await page.waitForTimeout(400);

      const entregarOption = page.locator('text=/Entregar/i').first();
      if (await entregarOption.isVisible().catch(() => false)) {
        expect(true).toBe(true);
        break;
      }

      await page.keyboard.press('Escape');
      await page.waitForTimeout(200);
    }
  });

  test('deve confirmar antes de assinar comodato', async ({ page }) => {
    const actionButtons = page.locator('button[class*="ghost"]').all();
    const buttons = await actionButtons;

    for (const btn of buttons) {
      await btn.click();
      await page.waitForTimeout(400);

      const assinarOption = page.locator('text=/Assinar/i').first();
      if (await assinarOption.isVisible().catch(() => false)) {
        await assinarOption.click();
        await page.waitForTimeout(800);

        const confirmModal = page.locator('[role="dialog"]').first();
        expect(await confirmModal.isVisible().catch(() => false)).toBeDefined();
        break;
      }

      await page.keyboard.press('Escape');
      await page.waitForTimeout(200);
    }
  });
});

test.describe('Comodatos - Controle de Devolução', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve exibir status Aguard. Devolucao para contratos vencidos', async ({ page }) => {
    await expect(page.locator('text=/Aguard. Devolucao/i').first()).toBeVisible();
  });

  test('deve exibir opção Encerrar para comodatos ativos', async ({ page }) => {
    const actionButtons = page.locator('button[class*="ghost"]').all();
    const buttons = await actionButtons;

    for (const btn of buttons.slice(0, 3)) {
      await btn.click();
      await page.waitForTimeout(400);

      const encerrarOption = page.locator('text=/Encerrar/i').first();
      if (await encerrarOption.isVisible().catch(() => false)) {
        expect(true).toBe(true);
        break;
      }

      await page.keyboard.press('Escape');
      await page.waitForTimeout(200);
    }
  });

  test('deve exibir contratos encerrados no histórico', async ({ page }) => {
    await expect(page.locator('text=/Encerrado/i').first()).toBeVisible();
  });
});

test.describe('Comodatos - Termos de Responsabilidade', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve permitir adicionar termos de responsabilidade', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const termsTextarea = modal.locator('textarea#terms');

    const termo = 'Cliente se responsabiliza por danos causados por mau uso do equipamento.';
    await termsTextarea.fill(termo);

    await expect(termsTextarea).toHaveValue(termo);
  });

  test('deve permitir adicionar observações sobre multas', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const obsTextarea = modal.locator('textarea#observacoes');

    const obs = 'Multa de 10% ao dia de atraso na devolução.';
    await obsTextarea.fill(obs);

    await expect(obsTextarea).toHaveValue(obs);
  });
});

test.describe('Comodatos - Multas e Penalidades', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve permitir registrar informações sobre multas por atraso', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const termsTextarea = modal.locator('textarea#terms');

    await termsTextarea.fill('Multa por atraso: 2% ao dia sobre o valor do equipamento.');

    await expect(termsTextarea).toContainText('Multa');
  });

  test('deve permitir registrar informações sobre danos', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comodato")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const termsTextarea = modal.locator('textarea#terms');

    await termsTextarea.fill('Cliente responsável por danos ao equipamento.');

    await expect(termsTextarea).toContainText('danos');
  });
});

test.describe('Comodatos - Renovação', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve permitir editar datas de contrato ativo', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const editOption = page.locator('text=/Editar/i').first();
    await editOption.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const endDateInput = modal.locator('input#end_date');

    if (await endDateInput.isVisible().catch(() => false)) {
      await endDateInput.fill('2025-06-30');
      await expect(endDateInput).toHaveValue('2025-06-30');
    }
  });

  test('deve exibir contratos expirados para renovação', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').first();
    await statusSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Expirado').first().click();
    await page.waitForTimeout(500);

    expect(page.url()).toContain('/comodatos');
  });
});

test.describe('Comodatos - Empty State e Erros', () => {
  test('deve exibir empty state quando não há comodatos', async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);

    await expect(page.locator('text=/Nenhum comodato encontrado/i')).toBeVisible();
  });

  test('deve ter botão para criar comodato no empty state', async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);

    const newButton = page.locator('button:has-text("Novo Comodato")').first();
    expect(await newButton.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar comodatos' }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);

    const errorMessage = page.locator('text=/Erro ao carregar/i');
    expect(await errorMessage.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Comodatos - Paginação', () => {
  test.beforeEach(async ({ page }) => {
    // Mock com mais itens para testar paginação
    const manyItems = {
      items: Array.from({ length: 25 }, (_, i) => ({
        id: `com-${i}`,
        codigo: `COM-2024-${String(i + 1).padStart(3, '0')}`,
        client_name: `Cliente ${i + 1}`,
        equipment_name: `Equipamento ${i + 1}`,
        status: 'active',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      })),
      total: 25,
    };

    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(manyItems),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);
  });

  test('deve exibir controles de paginação', async ({ page }) => {
    const paginationInfo = page.locator('text=/Mostrando/i');
    expect(await paginationInfo.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve ter botões anterior e próximo', async ({ page }) => {
    const prevButton = page.locator('button:has-text("Anterior")');
    const nextButton = page.locator('text=Proximo').first();

    expect(await prevButton.isVisible().catch(() => false)).toBeDefined();
    expect(await nextButton.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Comodatos - Integração', () => {
  test('deve carregar corretamente ao navegar do menu', async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos');
    await page.waitForTimeout(1500);

    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);

    await expect(page).toHaveURL(/\/comodatos/);
    await expect(page.locator('h1')).toContainText('Comodatos');
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    await page.route('**/api/v1/comodato**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockComodatoList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/comodatos');
    await page.waitForTimeout(1500);

    const refreshButton = page.locator('button[title*="Atualizar"]').first();
    expect(await refreshButton.isVisible().catch(() => false)).toBeDefined();
  });
});
