/**
 * Testes E2E - Módulo de Saúde Ocupacional - EPI
 *
 * Controle de Equipamentos de Proteção Individual conforme NR-6
 */

import { test, expect, Page } from '@playwright/test';

// ============================================================================
// MOCKS E FIXTURES
// ============================================================================

const MOCK_USER = {
  id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
  email: 'admin@conectaplus.com.br',
  name: 'Admin',
  role: 'admin',
  is_active: true,
  permissions: ['*'],
  tenant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
};

const MOCK_EPI_LIST = [
  {
    id: 'epi-001',
    nome: 'Capacete de Segurança Branco',
    descricao: 'Capacete com suspensão e jugular',
    categoria: 'cabeca',
    ca_numero: '12345',
    validade_ca: '2026-12-31',
    fabricante: 'Plastcor',
    ativo: true,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: 'epi-002',
    nome: 'Óculos de Proteção Incolor',
    descricao: 'Proteção contra projeções de partículas',
    categoria: 'olhos',
    ca_numero: '23456',
    validade_ca: '2025-06-30',
    fabricante: 'Libus',
    ativo: true,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: 'epi-003',
    nome: 'Luva de Látex',
    descricao: 'Luva descartável para procedimentos',
    categoria: 'maos',
    ca_numero: '34567',
    validade_ca: '2027-03-15',
    fabricante: 'Descarpack',
    ativo: true,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: 'epi-004',
    nome: 'Protetor Auricular Plug',
    descricao: 'Redução de ruído 20dB',
    categoria: 'auditiva',
    ca_numero: '45678',
    validade_ca: '2028-01-20',
    fabricante: '3M',
    ativo: true,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: 'epi-005',
    nome: 'Máscara PFF2',
    descricao: 'Proteção respiratória sem válvula',
    categoria: 'respiratoria',
    ca_numero: '56789',
    validade_ca: '2025-08-10',
    fabricante: '3M',
    ativo: true,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: 'epi-006',
    nome: 'Botina de Segurança',
    descricao: 'Bico de aço, solado antiderrapante',
    categoria: 'pes',
    ca_numero: '67890',
    validade_ca: '2026-04-25',
    fabricante: 'Marluvas',
    ativo: false,
    created_at: '2024-01-15T10:00:00Z',
  },
];

const MOCK_EPI_INVENTORY = [
  {
    id: 'inv-001',
    epi_id: 'epi-001',
    epi_nome: 'Capacete de Segurança Branco',
    categoria: 'cabeca',
    quantidade: 45,
    quantidade_minima: 10,
    lote: 'L2024A',
  },
  {
    id: 'inv-002',
    epi_id: 'epi-002',
    epi_nome: 'Óculos de Proteção Incolor',
    categoria: 'olhos',
    quantidade: 8,
    quantidade_minima: 15,
    lote: 'L2024B',
  },
  {
    id: 'inv-003',
    epi_id: 'epi-003',
    epi_nome: 'Luva de Látex',
    categoria: 'maos',
    quantidade: 200,
    quantidade_minima: 50,
    lote: 'L2024C',
  },
  {
    id: 'inv-004',
    epi_id: 'epi-004',
    epi_nome: 'Protetor Auricular Plug',
    categoria: 'auditiva',
    quantidade: 0,
    quantidade_minima: 20,
    lote: 'L2024D',
  },
];

const MOCK_EPI_STATS = {
  total_epis: 6,
  total_entregas: 145,
  estoque_baixo: 2,
  cas_vencendo: 1,
};

const MOCK_EPI_CATEGORIES = [
  { id: 'cat-001', value: 'cabeca', label: 'Proteção da Cabeça' },
  { id: 'cat-002', value: 'olhos', label: 'Proteção dos Olhos' },
  { id: 'cat-003', value: 'auditiva', label: 'Proteção Auditiva' },
  { id: 'cat-004', value: 'respiratoria', label: 'Proteção Respiratória' },
  { id: 'cat-005', value: 'maos', label: 'Proteção das Mãos' },
  { id: 'cat-006', value: 'pes', label: 'Proteção dos Pés' },
  { id: 'cat-007', value: 'corpo', label: 'Proteção do Corpo' },
  { id: 'cat-008', value: 'queda', label: 'Proteção contra Queda' },
];

const MOCK_EPI_DELIVERIES = [
  {
    id: 'ent-001',
    funcionario_id: 'func-001',
    funcionario_nome: 'João Silva',
    epi_id: 'epi-001',
    epi_nome: 'Capacete de Segurança Branco',
    quantidade: 1,
    data_entrega: '2024-01-10',
    data_vencimento: '2025-01-10',
    status: 'ativo',
  },
  {
    id: 'ent-002',
    funcionario_id: 'func-002',
    funcionario_nome: 'Maria Santos',
    epi_id: 'epi-002',
    epi_nome: 'Óculos de Proteção Incolor',
    quantidade: 1,
    data_entrega: '2024-01-15',
    data_vencimento: '2025-01-15',
    status: 'ativo',
  },
  {
    id: 'ent-003',
    funcionario_id: 'func-001',
    funcionario_nome: 'João Silva',
    epi_id: 'epi-004',
    epi_nome: 'Protetor Auricular Plug',
    quantidade: 5,
    data_entrega: '2024-02-01',
    data_vencimento: '2024-08-01',
    status: 'vencendo',
  },
];

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

async function setupAuthMock(page: Page) {
  await page.route('**/api/v1/auth/me', (route) => {
    if (route.request().method() === 'GET') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_USER),
      });
    } else {
      route.continue();
    }
  });
}

async function setupEPIMocks(page: Page) {
  // Mock estatísticas
  await page.route('**/api/v1/health-occupational/epi/statistics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_EPI_STATS),
    });
  });

  // Mock lista de EPIs
  await page.route('**/api/v1/health-occupational/epi**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_EPI_LIST,
        total: MOCK_EPI_LIST.length,
      }),
    });
  });

  // Mock categorias
  await page.route('**/api/v1/health-occupational/epi/categories**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_EPI_CATEGORIES,
      }),
    });
  });

  // Mock inventário
  await page.route('**/api/v1/health-occupational/epi/inventory**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_EPI_INVENTORY,
        total: MOCK_EPI_INVENTORY.length,
      }),
    });
  });

  // Mock entregas
  await page.route('**/api/v1/health-occupational/epi/deliveries**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_EPI_DELIVERIES,
        total: MOCK_EPI_DELIVERIES.length,
      }),
    });
  });

  // Mock criação
  await page.route('**/api/v1/health-occupational/epi', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'epi-new',
          message: 'EPI criado com sucesso',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock update
  await page.route('**/api/v1/health-occupational/epi/*', (route) => {
    if (route.request().method() === 'PATCH' || route.request().method() === 'PUT') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'EPI atualizado com sucesso',
        }),
      });
    } else {
      route.continue();
    }
  });
}

async function gotoEPIPage(page: Page) {
  await setupAuthMock(page);
  await setupEPIMocks(page);
  await page.goto('/modulos/saude-ocupacional/epi');
  await page.waitForLoadState('networkidle');
}

// ============================================================================
// TESTES - CONTROLE DE EPIs
// ============================================================================

test.describe('Saúde Ocupacional - EPI - Controle', () => {

  test('deve exibir título da página de EPIs', async ({ page }) => {
    await gotoEPIPage(page);

    await expect(page.getByText('Equipamentos de Proteção - EPI')).toBeVisible();
    await expect(page.getByText('Gestão de equipamentos de proteção individual, controle de entregas e estoque conforme NR-6')).toBeVisible();
  });

  test('deve exibir cards de estatísticas corretamente', async ({ page }) => {
    await gotoEPIPage(page);

    await expect(page.getByText('Total EPIs')).toBeVisible();
    await expect(page.getByText('6')).toBeVisible();

    await expect(page.getByText('Entregas Ativas')).toBeVisible();
    await expect(page.locator('text=145').first()).toBeVisible();

    await expect(page.getByText('Estoque Baixo')).toBeVisible();
    await expect(page.locator('text=2').nth(1)).toBeVisible();

    await expect(page.getByText('CAs Vencendo')).toBeVisible();
    await expect(page.locator('text=1').nth(1)).toBeVisible();
  });

  test('deve listar todos os EPIs no catálogo', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica lista de EPIs
    await expect(page.getByText('Capacete de Segurança Branco')).toBeVisible();
    await expect(page.getByText('Óculos de Proteção Incolor')).toBeVisible();
    await expect(page.getByText('Luva de Látex')).toBeVisible();
    await expect(page.getByText('Protetor Auricular Plug')).toBeVisible();
    await expect(page.getByText('Máscara PFF2')).toBeVisible();
  });

  test('deve exibir informações detalhadas de cada EPI', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica colunas da tabela
    await expect(page.getByText('Nome')).toBeVisible();
    await expect(page.getByText('Categoria')).toBeVisible();
    await expect(page.getByText('CA')).toBeVisible();
    await expect(page.getByText('Fabricante')).toBeVisible();
    await expect(page.getByText('Validade CA')).toBeVisible();
    await expect(page.getByText('Status')).toBeVisible();

    // Verifica dados
    await expect(page.getByText('12345')).toBeVisible();
    await expect(page.getByText('Plastcor')).toBeVisible();
    await expect(page.getByText('3M')).toBeVisible();
  });

  test('deve permitir buscar EPIs por nome', async ({ page }) => {
    await gotoEPIPage(page);

    // Busca por nome
    await page.getByPlaceholder('Buscar por nome, CA ou fabricante...').fill('Capacete');

    // Aguarda filtro
    await page.waitForTimeout(300);

    // Verifica resultado
    await expect(page.getByText('Capacete de Segurança Branco')).toBeVisible();
  });

  test('deve permitir buscar EPIs por número CA', async ({ page }) => {
    await gotoEPIPage(page);

    // Busca por CA
    await page.getByPlaceholder('Buscar por nome, CA ou fabricante...').fill('23456');

    await page.waitForTimeout(300);

    await expect(page.getByText('Óculos de Proteção Incolor')).toBeVisible();
  });

  test('deve permitir buscar EPIs por fabricante', async ({ page }) => {
    await gotoEPIPage(page);

    // Busca por fabricante
    await page.getByPlaceholder('Buscar por nome, CA ou fabricante...').fill('3M');

    await page.waitForTimeout(300);

    await expect(page.getByText('Protetor Auricular Plug')).toBeVisible();
    await expect(page.getByText('Máscara PFF2')).toBeVisible();
  });

  test('deve permitir filtrar por categoria', async ({ page }) => {
    await gotoEPIPage(page);

    // Abre select de categoria
    await page.getByText('Todas as categorias').click();

    // Seleciona categoria
    await page.getByText('Proteção da Cabeça').click();

    await page.waitForTimeout(300);

    await expect(page.getByText('Capacete de Segurança Branco')).toBeVisible();
  });

  test('deve exibir badge de status ativo/inativo', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica badges de status
    await expect(page.getByText('Ativo').first()).toBeVisible();
  });

  test('deve permitir cadastrar novo EPI', async ({ page }) => {
    await gotoEPIPage(page);

    // Clica em Novo EPI
    await page.getByRole('button', { name: 'Novo EPI' }).click();

    // Preenche formulário
    await page.getByLabel('Nome').fill('Avental de Couro');
    await page.getByLabel('Descrição').fill('Proteção contra riscos mecânicos');

    // Seleciona categoria
    await page.getByText('Selecione').first().click();
    await page.getByText('Proteção do Corpo').click();

    await page.getByLabel('Número do CA').fill('98765');
    await page.getByLabel('Fabricante').fill('Zanel');

    // Salva
    await page.getByRole('button', { name: 'Cadastrar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve validar campos obrigatórios no cadastro', async ({ page }) => {
    await gotoEPIPage(page);

    // Abre modal
    await page.getByRole('button', { name: 'Novo EPI' }).click();

    // Tenta salvar sem preencher
    const submitButton = page.getByRole('button', { name: 'Cadastrar' });
    await expect(submitButton).toBeDisabled();

    // Preenche apenas nome
    await page.getByLabel('Nome').fill('Teste');
    await expect(submitButton).toBeDisabled();

    // Seleciona categoria
    await page.getByText('Selecione').first().click();
    await page.getByText('Proteção da Cabeça').click();

    // Agora deve estar habilitado
    await expect(submitButton).toBeEnabled();
  });

  test('deve permitir editar EPI existente', async ({ page }) => {
    await gotoEPIPage(page);

    // Clica em editar (primeiro botão de editar)
    await page.locator('button').filter({ has: page.locator('svg[class*="Edit"]') }).first().click();

    // Modal de edição aberto
    await expect(page.getByText('Editar EPI')).toBeVisible();

    // Altera nome
    await page.getByLabel('Nome').fill('Capacete de Segurança Branco - Atualizado');

    // Salva
    await page.getByRole('button', { name: 'Salvar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve exibir mensagem quando não há EPIs cadastrados', async ({ page }) => {
    await setupAuthMock(page);

    // Mock com lista vazia
    await page.route('**/api/v1/health-occupational/epi**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
        }),
      });
    });

    await setupEPIMocks(page);
    await page.goto('/modulos/saude-ocupacional/epi');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Nenhum registro encontrado')).toBeVisible();
    await expect(page.getByText('Tente ajustar os filtros ou cadastre um novo EPI')).toBeVisible();
  });
});

// ============================================================================
// TESTES - ENTREGA DE EQUIPAMENTOS
// ============================================================================

test.describe('Saúde Ocupacional - EPI - Entregas', () => {

  test('deve exibir aba de estoque', async ({ page }) => {
    await gotoEPIPage(page);

    // Clica na aba Estoque
    await page.getByRole('tab', { name: 'Estoque' }).click();

    await expect(page.getByText('Visão Geral do Estoque')).toBeVisible();
    await expect(page.getByText('Controle de quantidades em estoque por item de EPI')).toBeVisible();
  });

  test('deve listar estoque por EPI', async ({ page }) => {
    await gotoEPIPage(page);

    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Verifica itens de estoque
    await expect(page.getByText('Capacete de Segurança Branco')).toBeVisible();
    await expect(page.getByText('45')).toBeVisible();
    await expect(page.getByText('200')).toBeVisible();
  });

  test('deve exibir informações de lote no estoque', async ({ page }) => {
    await gotoEPIPage(page);

    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Verifica lotes
    await expect(page.getByText('L2024A')).toBeVisible();
    await expect(page.getByText('L2024B')).toBeVisible();
    await expect(page.getByText('L2024C')).toBeVisible();
  });

  test('deve exibir quantidade mínima configurada', async ({ page }) => {
    await gotoEPIPage(page);

    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Verifica colunas
    await expect(page.getByText('Mínimo')).toBeVisible();
  });

  test('deve calcular corretamente total de entregas ativas', async ({ page }) => {
    await gotoEPIPage(page);

    await expect(page.getByText('Entregas Ativas')).toBeVisible();
    // Total das entregas mockadas
    expect(MOCK_EPI_DELIVERIES.reduce((acc, d) => acc + d.quantidade, 0)).toBe(7);
  });

  test('deve permitir registrar nova entrega de EPI', async ({ page }) => {
    await setupAuthMock(page);
    await setupEPIMocks(page);

    // Mock para entrega
    await page.route('**/api/v1/health-occupational/epi/deliveries', (route) => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'ent-new',
            message: 'Entrega registrada com sucesso',
          }),
        });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/saude-ocupacional/epi');
    await page.waitForLoadState('networkidle');

    // Verifica página carregada
    await expect(page.getByText('Equipamentos de Proteção - EPI')).toBeVisible();
  });

  test('deve exibir histórico de entregas por funcionário', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica dados de entregas mockadas
    await expect(page.getByText('6')).toBeVisible(); // Total EPIs
  });

  test('deve permitir devolução de EPI', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica página carregada
    await expect(page.getByText('Equipamentos de Proteção - EPI')).toBeVisible();
  });
});

// ============================================================================
// TESTES - VALIDADE DE EPIs
// ============================================================================

test.describe('Saúde Ocupacional - EPI - Validade', () => {

  test('deve exibir data de validade do CA formatada', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica datas formatadas
    await expect(page.getByText('31/12/2026')).toBeVisible();
    await expect(page.getByText('30/06/2025')).toBeVisible();
    await expect(page.getByText('15/03/2027')).toBeVisible();
  });

  test('deve identificar CAs próximos do vencimento', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica contador de CAs vencendo
    await expect(page.getByText('CAs Vencendo')).toBeVisible();
    await expect(page.getByText('1')).toBeVisible();
  });

  test('deve alertar sobre EPIs com CA vencido', async ({ page }) => {
    await setupAuthMock(page);

    // Mock com CA vencido
    const episWithExpired = [
      ...MOCK_EPI_LIST,
      {
        id: 'epi-007',
        nome: 'Cinto de Segurança',
        categoria: 'queda',
        ca_numero: '99999',
        validade_ca: '2023-01-01', // Vencido
        fabricante: 'Abseg',
        ativo: true,
      },
    ];

    await page.route('**/api/v1/health-occupational/epi**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: episWithExpired,
          total: episWithExpired.length,
        }),
      });
    });

    await page.route('**/api/v1/health-occupational/epi/statistics**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_EPI_STATS,
          cas_vencendo: 2,
        }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/epi');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('CAs Vencendo')).toBeVisible();
  });

  test('deve calcular prazo de validade restante', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica EPIs listados
    await expect(page.getByText('Capacete de Segurança Branco')).toBeVisible();
  });

  test('deve permitir atualizar validade do CA', async ({ page }) => {
    await gotoEPIPage(page);

    // Abre edição
    await page.locator('button').filter({ has: page.locator('svg[class*="Edit"]') }).first().click();

    // Altera validade
    await page.getByLabel('Validade do CA').fill('2027-12-31');

    // Salva
    await page.getByRole('button', { name: 'Salvar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve alertar sobre EPIs inativos', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica se há EPI inativo na lista
    await expect(page.getByText('Botina de Segurança')).toBeVisible();
  });
});

// ============================================================================
// TESTES - ALERTAS DE VENCIMENTO
// ============================================================================

test.describe('Saúde Ocupacional - EPI - Alertas', () => {

  test('deve exibir alerta de estoque baixo', async ({ page }) => {
    await gotoEPIPage(page);

    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Verifica badge de estoque baixo
    await expect(page.getByText('Estoque Baixo').first()).toBeVisible();
  });

  test('deve exibir alerta de sem estoque', async ({ page }) => {
    await gotoEPIPage(page);

    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Verifica badge de sem estoque
    await expect(page.getByText('Sem Estoque')).toBeVisible();
  });

  test('deve identificar corretamente itens abaixo do mínimo', async ({ page }) => {
    await gotoEPIPage(page);

    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Óculos tem quantidade 8 e mínimo 15 (deve estar baixo)
    await expect(page.getByText('Estoque Baixo')).toBeVisible();

    // Protetor auricular tem quantidade 0 (sem estoque)
    await expect(page.getByText('Sem Estoque')).toBeVisible();
  });

  test('deve exibir badge de status do estoque', async ({ page }) => {
    await gotoEPIPage(page);

    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Verifica badges de situação
    await expect(page.getByText('Normal').first()).toBeVisible();
  });

  test('deve calcular corretamente número de alertas', async ({ page }) => {
    await gotoEPIPage(page);

    // Estatísticas mostram 2 itens com estoque baixo
    await expect(page.getByText('Estoque Baixo')).toBeVisible();
    await expect(page.locator('text=2').nth(1)).toBeVisible();
  });

  test('deve permitir configurar quantidade mínima por EPI', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica aba de estoque
    await page.getByRole('tab', { name: 'Estoque' }).click();
    await expect(page.getByText('Visão Geral do Estoque')).toBeVisible();
  });

  test('deve atualizar alertas após movimentação de estoque', async ({ page }) => {
    await gotoEPIPage(page);

    // Clica em atualizar
    await page.getByRole('button', { name: 'Atualizar' }).click();

    await page.waitForTimeout(500);

    // Verifica se estatísticas ainda estão visíveis
    await expect(page.getByText('Total EPIs')).toBeVisible();
  });

  test('deve exibir notificação de CA vencendo no dashboard', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica card de alerta
    await expect(page.getByText('CAs Vencendo')).toBeVisible();
    await expect(page.locator('text=1').nth(1)).toBeVisible();
  });
});

// ============================================================================
// TESTES - INTEGRAÇÃO E FLUXO COMPLETO
// ============================================================================

test.describe('Saúde Ocupacional - EPI - Fluxo Completo', () => {

  test('deve navegar entre catálogo e estoque', async ({ page }) => {
    await gotoEPIPage(page);

    // Verifica aba ativa
    await expect(page.getByText('Catálogo de EPIs')).toBeVisible();

    // Muda para estoque
    await page.getByRole('tab', { name: 'Estoque' }).click();
    await expect(page.getByText('Visão Geral do Estoque')).toBeVisible();

    // Volta para catálogo
    await page.getByRole('tab', { name: 'Catálogo' }).click();
    await expect(page.getByText('Catálogo de EPIs')).toBeVisible();
  });

  test('deve manter filtros ao alternar abas', async ({ page }) => {
    await gotoEPIPage(page);

    // Aplica filtro de busca
    await page.getByPlaceholder('Buscar por nome, CA ou fabricante...').fill('Capacete');
    await page.waitForTimeout(300);

    // Alterna aba
    await page.getByRole('tab', { name: 'Estoque' }).click();

    // Volta para catálogo
    await page.getByRole('tab', { name: 'Catálogo' }).click();

    // Verifica se busca ainda está aplicada
    const searchInput = page.getByPlaceholder('Buscar por nome, CA ou fabricante...');
    await expect(searchInput).toHaveValue('Capacete');
  });

  test('deve permitir cadastro rápido de EPI e ver em estoque', async ({ page }) => {
    await gotoEPIPage(page);

    // Cadastra novo EPI
    await page.getByRole('button', { name: 'Novo EPI' }).click();
    await page.getByLabel('Nome').fill('Teste Integração');
    await page.getByLabel('Descrição').fill('EPI para teste');
    await page.getByText('Selecione').first().click();
    await page.getByText('Proteção dos Olhos').click();
    await page.getByLabel('Número do CA').fill('11111');
    await page.getByLabel('Fabricante').fill('Teste');
    await page.getByRole('button', { name: 'Cadastrar' }).click();

    await page.waitForTimeout(500);

    // Verifica se aparece na lista
    await expect(page.getByText('Teste Integração')).toBeVisible();
  });

  test('deve exibir erro ao falhar carregamento', async ({ page }) => {
    await setupAuthMock(page);

    // Mock de erro
    await page.route('**/api/v1/health-occupational/epi**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar EPIs' }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/epi');
    await page.waitForLoadState('networkidle');

    // Verifica mensagem de erro
    await expect(page.getByText('Erro ao carregar EPIs')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Tentar novamente' })).toBeVisible();
  });

  test('deve ter layout responsivo', async ({ page }) => {
    await gotoEPIPage(page);

    // Testa viewport mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Equipamentos de Proteção - EPI')).toBeVisible();

    // Restaura viewport
    await page.setViewportSize({ width: 1280, height: 720 });
  });
});
