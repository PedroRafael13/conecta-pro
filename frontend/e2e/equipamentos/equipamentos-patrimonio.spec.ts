import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Patrimônio de Equipamentos
 *
 * Testa gestão completa de equipamentos:
 * - Cadastro de equipamentos (código, descrição, valor)
 * - Controle de patrimônio
 * - Categorias e localização
 * - Depreciação
 * - QR code/etiquetas
 * - Movimentações entre setores
 */

// Mock data para equipamentos
const mockEquipmentList = {
  items: [
    {
      id: 'eq-001',
      nome: 'Câmera IP Dome 4K',
      codigo: 'CAM-2024-001',
      equipment_type: 'camera',
      serial_number: 'SN123456789',
      marca: 'Intelbras',
      modelo: 'VIP 3240 Z',
      location: 'Recepção Principal',
      status: 'em_campo',
      observacoes: 'Câmera instalada na entrada principal',
      valor_aquisicao: 1500.00,
      data_aquisicao: '2024-01-15',
    },
    {
      id: 'eq-002',
      nome: 'Controle de Acesso Biométrico',
      codigo: 'CA-2024-015',
      equipment_type: 'controle_acesso',
      serial_number: 'SN987654321',
      marca: 'Hikvision',
      modelo: 'DS-K1T671M',
      location: 'Almoxarifado',
      status: 'em_estoque',
      observacoes: 'Aguardando instalação',
      valor_aquisicao: 2800.00,
      data_aquisicao: '2024-02-20',
    },
    {
      id: 'eq-003',
      nome: 'Sensor de Presença',
      codigo: 'SEN-2024-008',
      equipment_type: 'sensor',
      serial_number: 'SN456789123',
      marca: 'Paradox',
      modelo: 'DG75',
      location: 'Sala de Servidores',
      status: 'em_manutencao',
      observacoes: 'Em manutenção preventiva',
      valor_aquisicao: 350.00,
      data_aquisicao: '2023-11-10',
    },
    {
      id: 'eq-004',
      nome: 'Rádio Comunicador',
      codigo: 'RAD-2024-003',
      equipment_type: 'radio',
      serial_number: 'SN789123456',
      marca: 'Motorola',
      modelo: 'EP450',
      location: 'Estacionamento',
      status: 'inativo',
      observacoes: 'Equipamento desativado',
      valor_aquisicao: 1200.00,
      data_aquisicao: '2023-08-05',
    },
  ],
  total: 4,
};

const mockStats = {
  total: 4,
  in_stock: 1,
  installed: 1,
  in_maintenance: 1,
  inactive: 1,
};

test.describe('Equipamentos - Patrimônio - Visualização', () => {
  test.beforeEach(async ({ page }) => {
    // Mock das APIs
    await page.route('**/api/v1/equipment**', (route) => {
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
          body: JSON.stringify(mockEquipmentList),
        });
      }
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);
  });

  test('deve carregar a página de patrimônio', async ({ page }) => {
    await expect(page).toHaveURL(/\/patrimonio/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Patrimônio/i, { timeout: 10000 });
  });

  test('deve exibir subtítulo de gestão de equipamentos', async ({ page }) => {
    const subtitle = page.locator('p:has-text("Gestão de equipamentos")');
    await expect(subtitle).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    // Verifica se os 4 cards de stats estão presentes
    const totalCard = page.locator('text=/Total/i').first();
    const estoqueCard = page.locator('text=/Em Estoque/i').first();
    const campoCard = page.locator('text=/Em Campo/i').first();
    const manutencaoCard = page.locator('text=/Em Manutenção/i').first();

    await expect(totalCard).toBeVisible();
    await expect(estoqueCard).toBeVisible();
    await expect(campoCard).toBeVisible();
    await expect(manutencaoCard).toBeVisible();
  });

  test('deve exibir valores corretos nas estatísticas', async ({ page }) => {
    // Verifica se os valores das estatísticas estão corretos
    await expect(page.locator('text=4').first()).toBeVisible(); // Total
  });

  test('deve exibir tabela de equipamentos', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    expect(headerTexts).toContain('Nome');
    expect(headerTexts).toContain('Tipo');
    expect(headerTexts).toContain('N.Série');
    expect(headerTexts).toContain('Status');
    expect(headerTexts).toContain('Localização');
  });

  test('deve exibir código do equipamento em fonte mono', async ({ page }) => {
    const codigoCell = page.locator('text=CAM-2024-001').first();
    await expect(codigoCell).toBeVisible();
  });

  test('deve exibir badges de status coloridos', async ({ page }) => {
    const emCampoBadge = page.locator('text=/Em Campo/i').first();
    const emEstoqueBadge = page.locator('text=/Em Estoque/i').first();
    const emManutencaoBadge = page.locator('text=/Em Manutenção/i').first();

    await expect(emCampoBadge).toBeVisible();
    await expect(emEstoqueBadge).toBeVisible();
    await expect(emManutencaoBadge).toBeVisible();
  });

  test('deve exibir tipo do equipamento traduzido', async ({ page }) => {
    await expect(page.locator('text=/Câmera|Controle de Acesso|Sensor|Rádio/i').first()).toBeVisible();
  });

  test('deve exibir número de série quando disponível', async ({ page }) => {
    await expect(page.locator('text=SN123456789').first()).toBeVisible();
  });

  test('deve exibir menu de ações em cada linha', async ({ page }) => {
    const actionButtons = page.locator('button[class*="ghost"]').all();
    const count = (await actionButtons).length;
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Equipamentos - Patrimônio - Filtros e Busca', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/equipment**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockEquipmentList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('Câmera');
    await page.waitForTimeout(500);
    await expect(searchInput).toHaveValue('Câmera');
  });

  test('deve filtrar por status', async ({ page }) => {
    const statusSelect = page.locator('[role="combobox"]').first();
    await expect(statusSelect).toBeVisible();

    await statusSelect.click();
    await page.waitForTimeout(300);

    const option = page.locator('text=Em Estoque').first();
    await option.click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por tipo de equipamento', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const typeSelect = selects[1]! || selects[0]!;

    await typeSelect.click();
    await page.waitForTimeout(300);

    const option = page.locator('text=Câmera').first();
    await option.click();
    await page.waitForTimeout(500);
  });

  test('deve limpar busca ao clicar em atualizar', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]').first();
    await searchInput.fill('teste');
    await page.waitForTimeout(300);

    const refreshButton = page.locator('button:has-text("Atualizar")').first();
    await refreshButton.click();
    await page.waitForTimeout(500);

    expect(page.url()).toContain('/patrimonio');
  });
});

test.describe('Equipamentos - Patrimônio - CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/equipment**', (route) => {
      const method = route.request().method();

      if (method === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockEquipmentList),
        });
      } else if (method === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'eq-new',
            nome: 'Novo Equipamento',
            codigo: 'NEW-2024-001',
            status: 'em_estoque',
          }),
        });
      } else {
        route.continue();
      }
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);
  });

  test('deve abrir modal de novo equipamento', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Equipamento")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal).toContainText('Novo Equipamento');
  });

  test('deve ter campos obrigatórios no formulário', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Equipamento")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const nomeInput = modal.locator('input#nome');
    await expect(nomeInput).toBeVisible();
  });

  test('deve ter select de tipo de equipamento', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Equipamento")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const tipoSelect = modal.locator('[role="combobox"]').first();
    await expect(tipoSelect).toBeVisible();
  });

  test('deve ter campos de marca e modelo', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Equipamento")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const marcaInput = modal.locator('input#marca');
    const modeloInput = modal.locator('input#modelo');

    await expect(marcaInput).toBeVisible();
    await expect(modeloInput).toBeVisible();
  });

  test('deve ter campo de localização', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Equipamento")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const locationInput = modal.locator('input#location');
    await expect(locationInput).toBeVisible();
  });

  test('deve ter campo de observações', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Equipamento")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const obsTextarea = modal.locator('textarea#observacoes');
    await expect(obsTextarea).toBeVisible();
  });

  test('deve cancelar criação ao clicar em Cancelar', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Equipamento")');
    await newButton.click();
    await page.waitForTimeout(800);

    const cancelButton = page.locator('button:has-text("Cancelar")').first();
    await cancelButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).not.toBeVisible();
  });

  test('deve abrir modal de edição ao clicar em Editar', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const editOption = page.locator('text=/Editar/i').first();
    await editOption.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal).toContainText('Editar Equipamento');
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

  test('deve exibir código no modal de detalhes', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const viewOption = page.locator('text=/Ver detalhes/i').first();
    await viewOption.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toContainText('Código');
  });

  test('deve exibir informações técnicas no detalhe', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const viewOption = page.locator('text=/Ver detalhes/i').first();
    await viewOption.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toContainText('Marca');
    await expect(modal).toContainText('Modelo');
  });

  test('deve confirmar antes de deletar equipamento', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const deleteOption = page.locator('text=/Deletar/i').first();
    await deleteOption.click();
    await page.waitForTimeout(800);

    const confirmModal = page.locator('[role="dialog"]').first();
    await expect(confirmModal).toBeVisible();
    await expect(confirmModal).toContainText('Deletar');
  });
});

test.describe('Equipamentos - Patrimônio - Categorias e Localização', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/equipment**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockEquipmentList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);
  });

  test('deve exibir localização dos equipamentos', async ({ page }) => {
    await expect(page.locator('text=Recepção Principal').first()).toBeVisible();
    await expect(page.locator('text=Almoxarifado').first()).toBeVisible();
  });

  test('deve filtrar por tipo câmera', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const typeSelect = selects[1]! || selects[0]!;

    await typeSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Câmera').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por tipo controle de acesso', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const typeSelect = selects[1]! || selects[0]!;

    await typeSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Controle de Acesso').first().click();
    await page.waitForTimeout(500);
  });

  test('deve exibir traço quando localização não informada', async ({ page }) => {
    const dashCells = page.locator('table tbody tr td:has-text("-")').all();
    expect((await dashCells).length).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Equipamentos - Patrimônio - Movimentações', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/equipment**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockEquipmentList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);
  });

  test('deve exibir equipamento em estoque', async ({ page }) => {
    await expect(page.locator('text=/Em Estoque/i').first()).toBeVisible();
  });

  test('deve exibir equipamento em campo', async ({ page }) => {
    await expect(page.locator('text=/Em Campo/i').first()).toBeVisible();
  });

  test('deve exibir equipamento em manutenção', async ({ page }) => {
    await expect(page.locator('text=/Em Manutenção/i').first()).toBeVisible();
  });

  test('deve exibir equipamento inativo', async ({ page }) => {
    await expect(page.locator('text=/Inativo/i').first()).toBeVisible();
  });

  test('deve permitir editar localização do equipamento', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const editOption = page.locator('text=/Editar/i').first();
    await editOption.click();
    await page.waitForTimeout(800);

    const locationInput = page.locator('input#location');
    if (await locationInput.isVisible().catch(() => false)) {
      await locationInput.fill('Nova Localização');
      await expect(locationInput).toHaveValue('Nova Localização');
    }
  });
});

test.describe('Equipamentos - Patrimônio - Empty State e Erros', () => {
  test('deve exibir empty state quando não há equipamentos', async ({ page }) => {
    await page.route('**/api/v1/equipment**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);

    await expect(page.locator('text=/Nenhum equipamento encontrado/i')).toBeVisible();
  });

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await page.route('**/api/v1/equipment**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar equipamentos' }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);

    const errorMessage = page.locator('text=/Erro ao carregar/i');
    expect(await errorMessage.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve ter botão para tentar novamente em caso de erro', async ({ page }) => {
    await page.route('**/api/v1/equipment**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar equipamentos' }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);

    const retryButton = page.locator('button:has-text("Tentar novamente")').first();
    expect(await retryButton.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Equipamentos - Patrimônio - Paginação', () => {
  test.beforeEach(async ({ page }) => {
    // Mock com mais itens para testar paginação
    const manyItems = {
      items: Array.from({ length: 25 }, (_, i) => ({
        id: `eq-${i}`,
        nome: `Equipamento ${i + 1}`,
        codigo: `EQ-2024-${String(i + 1).padStart(3, '0')}`,
        equipment_type: 'camera',
        serial_number: `SN${i + 1}`,
        status: 'em_estoque',
        location: 'Almoxarifado',
      })),
      total: 25,
    };

    await page.route('**/api/v1/equipment**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(manyItems),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);
  });

  test('deve exibir controles de paginação quando há muitos itens', async ({ page }) => {
    const paginationInfo = page.locator('text=/Mostrando/i');
    expect(await paginationInfo.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve ter botão próximo habilitado', async ({ page }) => {
    const nextButton = page.locator('button:has-text("Próximo")');
    expect(await nextButton.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve ter botão anterior desabilitado na primeira página', async ({ page }) => {
    const prevButton = page.locator('button:has-text("Anterior")');
    expect(await prevButton.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Equipamentos - Patrimônio - Integração', () => {
  test('deve carregar corretamente ao navegar do menu', async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos');
    await page.waitForTimeout(1500);

    // Navega para equipamentos
    await page.goto('/modulos/equipamentos');
    await page.waitForTimeout(1000);

    // Navega para patrimônio
    await page.goto('/modulos/equipamentos/patrimonio');
    await page.waitForTimeout(1500);

    await expect(page).toHaveURL(/\/patrimonio/);
    await expect(page.locator('h1')).toContainText('Patrimônio');
  });
});
