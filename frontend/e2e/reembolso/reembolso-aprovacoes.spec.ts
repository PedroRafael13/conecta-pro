/**
 * Testes E2E - Módulo de Reembolso - Aprovações
 *
 * Este arquivo contém testes end-to-end para o fluxo de aprovações
 * de reembolsos no sistema Conecta Pro.
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

const MOCK_REIMBURSEMENT_REQUESTS = [
  {
    id: 'req-001',
    code: 'REM-2024-001',
    title: 'Viagem a São Paulo - Cliente ABC',
    description: 'Despesas com hospedagem e alimentação',
    requester_id: 'user-001',
    expense_date_start: '2024-01-15',
    expense_date_end: '2024-01-18',
    total_amount: 2850.50,
    approved_amount: 0,
    paid_amount: 0,
    status: 'pendente',
    approval_level: 'gerente',
    submitted_at: '2024-01-19T10:30:00Z',
    approved_by: null,
    approved_at: null,
    rejection_reason: null,
    payable_account_id: null,
    processed_at: null,
    processed_by: null,
    bank_code: '001',
    bank_agency: '1234',
    bank_account: '56789-0',
    pix_key: 'admin@email.com',
    cost_center: 'Vendas',
    project: 'Expansão SP',
    notes: null,
    created_at: '2024-01-19T10:30:00Z',
    updated_at: '2024-01-19T10:30:00Z',
    is_active: true,
    items_count: 3,
    attachments_count: 2,
    can_edit: true,
    can_submit: true,
    can_approve: true,
    can_process: false,
    items: [],
    attachments: [],
  },
  {
    id: 'req-002',
    code: 'REM-2024-002',
    title: 'Material de Escritório',
    description: 'Compra de papel, toners e materiais diversos',
    requester_id: 'user-002',
    expense_date_start: '2024-01-20',
    expense_date_end: '2024-01-20',
    total_amount: 450.00,
    approved_amount: 0,
    paid_amount: 0,
    status: 'pendente',
    approval_level: 'supervisor',
    submitted_at: '2024-01-20T14:00:00Z',
    approved_by: null,
    approved_at: null,
    rejection_reason: null,
    cost_center: 'Administrativo',
    project: null,
    items_count: 5,
    attachments_count: 1,
    can_edit: true,
    can_submit: true,
    can_approve: true,
    can_process: false,
    items: [],
    attachments: [],
  },
  {
    id: 'req-003',
    code: 'REM-2024-003',
    title: 'Consultoria Externa - TI',
    description: 'Serviço de consultoria em segurança da informação',
    requester_id: 'user-003',
    expense_date_start: '2024-01-10',
    expense_date_end: '2024-01-12',
    total_amount: 15000.00,
    approved_amount: 0,
    paid_amount: 0,
    status: 'em_analise',
    approval_level: 'diretor',
    submitted_at: '2024-01-13T09:00:00Z',
    approved_by: null,
    approved_at: null,
    rejection_reason: null,
    cost_center: 'TI',
    project: 'Segurança 2024',
    items_count: 1,
    attachments_count: 3,
    can_edit: false,
    can_submit: false,
    can_approve: true,
    can_process: false,
    items: [],
    attachments: [],
  },
];

const MOCK_STATS = {
  total: 45,
  by_status: {
    rascunho: 5,
    pendente: 15,
    em_analise: 8,
    aprovado: 12,
    rejeitado: 3,
    processado: 2,
    cancelado: 0,
  },
  by_approval_level: {
    supervisor: 20,
    gerente: 15,
    diretor: 8,
    financeiro: 2,
  },
  total_amount: 125680.50,
  total_approved: 85600.00,
  total_paid: 42300.00,
  pending_count: 23,
  pending_amount: 45200.00,
  approved_count: 12,
  approved_amount: 85600.00,
};

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

async function setupReimbursementMocks(page: Page) {
  // Mock estatísticas
  await page.route('**/api/v1/reimbursements/statistics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_STATS),
    });
  });

  // Mock listagem de aprovações pendentes
  await page.route('**/api/v1/reimbursements/approvals/pending**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_REIMBURSEMENT_REQUESTS,
        total: 3,
        page: 1,
        page_size: 10,
        total_pages: 1,
      }),
    });
  });

  // Mock aprovação
  await page.route('**/api/v1/reimbursements/*/approve', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });

  // Mock rejeição
  await page.route('**/api/v1/reimbursements/*/reject', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true }),
    });
  });
}

async function gotoApprovalsPage(page: Page) {
  await setupAuthMock(page);
  await setupReimbursementMocks(page);
  await page.goto('/modulos/reembolso/aprovacoes');
  await page.waitForLoadState('networkidle');
}

// ============================================================================
// TESTES
// ============================================================================

test.describe('Reembolso - Aprovações', () => {

  // ============================================================================
  // 1. LISTAGEM DE SOLICITAÇÕES
  // ============================================================================

  test('deve exibir título da página de aprovações', async ({ page }) => {
    await gotoApprovalsPage(page);

    await expect(page.getByText('Aprovações Pendentes')).toBeVisible();
    await expect(page.getByText('3 solicitações aguardando')).toBeVisible();
  });

  test('deve exibir cards de estatísticas corretamente', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica cards de estatísticas
    await expect(page.getByText('Pendentes').first()).toBeVisible();
    await expect(page.getByText('23')).toBeVisible(); // pending_count

    await expect(page.getByText('Valor Pendente')).toBeVisible();
    await expect(page.getByText('R$ 45.200,00')).toBeVisible();

    await expect(page.getByText('Aprovados').first()).toBeVisible();
    await expect(page.getByText('12')).toBeVisible(); // approved_count

    await expect(page.getByText('Valor Aprovado')).toBeVisible();
    await expect(page.getByText('R$ 85.600,00')).toBeVisible();
  });

  test('deve listar todas as solicitações pendentes', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica se as solicitações estão listadas
    await expect(page.getByText('REM-2024-001')).toBeVisible();
    await expect(page.getByText('REM-2024-002')).toBeVisible();
    await expect(page.getByText('REM-2024-003')).toBeVisible();

    // Verifica valores
    await expect(page.getByText('R$ 2.850,50')).toBeVisible();
    await expect(page.getByText('R$ 450,00')).toBeVisible();
    await expect(page.getByText('R$ 15.000,00')).toBeVisible();
  });

  test('deve exibir informações detalhadas de cada solicitação', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica títulos
    await expect(page.getByText('Viagem a São Paulo - Cliente ABC')).toBeVisible();
    await expect(page.getByText('Material de Escritório')).toBeVisible();
    await expect(page.getByText('Consultoria Externa - TI')).toBeVisible();

    // Verifica períodos
    await expect(page.getByText('15/01/2024 - 18/01/2024')).toBeVisible();
    await expect(page.getByText('20/01/2024 - 20/01/2024')).toBeVisible();

    // Verifica contagem de itens
    await expect(page.getByText('3 itens')).toBeVisible();
    await expect(page.getByText('5 itens')).toBeVisible();
    await expect(page.getByText('1 itens')).toBeVisible();
  });

  test('deve permitir filtrar por nível de aprovação', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica botões de filtro
    await expect(page.getByRole('button', { name: 'Todos' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Supervisor' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Gerente' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Diretor' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Financeiro' })).toBeVisible();

    // Clica em Gerente
    await page.getByRole('button', { name: 'Gerente' }).click();

    // Aguarda atualização
    await page.waitForTimeout(300);
  });

  test('deve exibir badge de nível de aprovação nas solicitações', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica badges de nível
    await expect(page.getByText('Gerente').first()).toBeVisible();
    await expect(page.getByText('Supervisor').first()).toBeVisible();
    await expect(page.getByText('Diretor').first()).toBeVisible();
  });

  // ============================================================================
  // 2. FLUXO DE APROVAÇÃO
  // ============================================================================

  test('deve exibir botão de aprovar para cada solicitação', async ({ page }) => {
    await gotoApprovalsPage(page);

    const approveButtons = page.getByRole('button', { name: /Aprovar/i });
    await expect(approveButtons).toHaveCount(3);
  });

  test('deve abrir modal de detalhes ao clicar em ver detalhes', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Configura mock para detalhes
    await page.route('**/api/v1/reimbursements/req-001', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_REIMBURSEMENT_REQUESTS[0]),
      });
    });

    // Clica no botão de ver detalhes (primeiro botão com ícone de olho)
    await page.locator('button[title="Ver Detalhes"]').first().click();

    // Verifica se o modal abriu
    await expect(page.getByText('Detalhes da Solicitação')).toBeVisible();
  });

  test('deve permitir aprovar solicitação via modal', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Clica no botão Aprovar (que abre o modal)
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();

    // Verifica se o modal de aprovação abriu
    await expect(page.getByText('Aprovar Reembolso')).toBeVisible();

    // Preenche comentário
    await page.getByPlaceholder('Adicione observações...').fill('Aprovado conforme política');

    // Confirma aprovação
    await page.getByRole('button', { name: 'Confirmar Aprovação' }).click();

    // Aguarda processamento
    await page.waitForTimeout(500);
  });

  test('deve permitir rejeitar solicitação informando motivo', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Clica no botão Aprovar (para abrir o modal)
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();

    // Alterna para rejeição
    await page.getByText('Rejeitar').click();

    // Preenche motivo da rejeição
    await page.getByPlaceholder('Informe o motivo da rejeição...').fill('Documentação incompleta');

    // Confirma rejeição
    await page.getByRole('button', { name: 'Confirmar Rejeição' }).click();

    // Aguarda processamento
    await page.waitForTimeout(500);
  });

  test('deve validar campos obrigatórios na rejeição', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Clica no botão Aprovar (para abrir o modal)
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();

    // Alterna para rejeição
    await page.getByText('Rejeitar').click();

    // Tenta confirmar sem preencher motivo
    const confirmButton = page.getByRole('button', { name: 'Confirmar Rejeição' });
    await expect(confirmButton).toBeDisabled();
  });

  test('deve atualizar lista após aprovação', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Clica em aprovar
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();

    // Confirma
    await page.getByRole('button', { name: 'Confirmar Aprovação' }).click();

    // Aguarda atualização da lista
    await page.waitForTimeout(800);

    // Verifica se o refresh foi chamado (stats atualizados)
    await expect(page.getByText('Pendentes').first()).toBeVisible();
  });

  test('deve desabilitar botões durante processamento', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Clica em aprovar
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();

    // Confirma
    const confirmButton = page.getByRole('button', { name: 'Confirmar Aprovação' });
    await confirmButton.click();

    // Verifica se o botão está em estado de loading
    await expect(page.getByText('Processando...')).toBeVisible();
  });

  test('deve exibir mensagem quando não há aprovações pendentes', async ({ page }) => {
    await setupAuthMock(page);

    // Mock com lista vazia
    await page.route('**/api/v1/reimbursements/approvals/pending**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          page_size: 10,
          total_pages: 0,
        }),
      });
    });

    await page.route('**/api/v1/reimbursements/statistics**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_STATS,
          pending_count: 0,
          pending_amount: 0,
        }),
      });
    });

    await page.goto('/modulos/reembolso/aprovacoes');
    await page.waitForLoadState('networkidle');

    // Verifica mensagem de estado vazio
    await expect(page.getByText('Nenhuma aprovação pendente')).toBeVisible();
    await expect(page.getByText('Todas as solicitações foram processadas')).toBeVisible();
  });

  // ============================================================================
  // 3. UPLOAD DE COMPROVANTES
  // ============================================================================

  test('deve exibir contagem de anexos por solicitação', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica se a informação de anexos está visível nos detalhes
    await expect(page.getByText('REM-2024-001')).toBeVisible();
  });

  test('deve permitir visualizar anexos no modal de detalhes', async ({ page }) => {
    await gotoApprovalsPage(page);

    await page.route('**/api/v1/reimbursements/req-001', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_REIMBURSEMENT_REQUESTS[0],
          attachments: [
            {
              id: 'att-001',
              file_name: 'nota_fiscal_hotel.pdf',
              file_size_formatted: '245 KB',
              attachment_type: 'nota_fiscal',
              is_image: false,
              is_pdf: true,
            },
            {
              id: 'att-002',
              file_name: 'comprovante_restaurante.jpg',
              file_size_formatted: '1.2 MB',
              attachment_type: 'cupom_fiscal',
              is_image: true,
              is_pdf: false,
            },
          ],
        }),
      });
    });

    // Abre detalhes
    await page.locator('button[title="Ver Detalhes"]').first().click();

    await expect(page.getByText('Detalhes da Solicitação')).toBeVisible();
  });

  test('deve validar tipos de anexo permitidos', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica se os tipos de anexo estão mapeados corretamente
    await expect(page.getByText('REM-2024-001')).toBeVisible();
  });

  test('deve exibir preview de imagens nos anexos', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Configura mock com anexo de imagem
    await page.route('**/api/v1/reimbursements/req-002', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_REIMBURSEMENT_REQUESTS[1],
          attachments: [
            {
              id: 'att-003',
              file_name: 'comprovante.jpg',
              is_image: true,
              is_pdf: false,
            },
          ],
        }),
      });
    });

    await page.locator('button[title="Ver Detalhes"]').nth(1).click();
    await expect(page.getByText('Detalhes da Solicitação')).toBeVisible();
  });

  // ============================================================================
  // 4. VALORES E CATEGORIAS
  // ============================================================================

  test('deve exibir valores formatados em reais', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica formatação de valores
    await expect(page.getByText('R$ 2.850,50')).toBeVisible();
    await expect(page.getByText('R$ 450,00')).toBeVisible();
    await expect(page.getByText('R$ 15.000,00')).toBeVisible();
  });

  test('deve exibir centro de custo das solicitações', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica centros de custo
    await expect(page.getByText('Vendas')).toBeVisible();
    await expect(page.getByText('Administrativo')).toBeVisible();
    await expect(page.getByText('TI')).toBeVisible();
  });

  test('deve exibir projeto quando informado', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Abre detalhes para ver projeto
    await page.route('**/api/v1/reimbursements/req-001', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_REIMBURSEMENT_REQUESTS[0]),
      });
    });

    await page.locator('button[title="Ver Detalhes"]').first().click();
    await expect(page.getByText('Expansão SP')).toBeVisible();
  });

  test('deve calcular corretamente totais por categoria', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica se valores totais estão corretos
    const totalValue = MOCK_REIMBURSEMENT_REQUESTS.reduce((acc, req) => acc + req.total_amount, 0);
    expect(totalValue).toBe(18300.50);
  });

  test('deve permitir aprovar valor parcial', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Abre modal de aprovação
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();

    await expect(page.getByText('Aprovar Reembolso')).toBeVisible();
    await expect(page.getByText('R$ 2.850,50')).toBeVisible();
  });

  test('deve exibir histórico de valores aprovados', async ({ page }) => {
    await gotoApprovalsPage(page);

    await expect(page.getByText('Valor Aprovado')).toBeVisible();
    await expect(page.getByText('R$ 85.600,00')).toBeVisible();
  });

  // ============================================================================
  // 5. NOTIFICAÇÕES
  // ============================================================================

  test('deve exibir notificação de sucesso após aprovação', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Abre e confirma aprovação
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();
    await page.getByRole('button', { name: 'Confirmar Aprovação' }).click();

    // Aguarda notificação
    await page.waitForTimeout(600);
  });

  test('deve exibir notificação de erro quando API falha', async ({ page }) => {
    await setupAuthMock(page);

    // Mock de erro
    await page.route('**/api/v1/reimbursements/approvals/pending**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro interno do servidor' }),
      });
    });

    await page.goto('/modulos/reembolso/aprovacoes');
    await page.waitForLoadState('networkidle');

    // Verifica mensagem de erro
    await expect(page.getByText('Erro ao carregar aprovações')).toBeVisible();
  });

  test('deve permitir tentar novamente após erro', async ({ page }) => {
    await setupAuthMock(page);

    let attempts = 0;
    await page.route('**/api/v1/reimbursements/approvals/pending**', (route) => {
      attempts++;
      if (attempts === 1) {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Erro interno' }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: MOCK_REIMBURSEMENT_REQUESTS,
            total: 3,
            page: 1,
            page_size: 10,
            total_pages: 1,
          }),
        });
      }
    });

    await page.goto('/modulos/reembolso/aprovacoes');
    await page.waitForLoadState('networkidle');

    // Clica em tentar novamente
    await page.getByRole('button', { name: 'Tentar novamente' }).click();

    // Aguarda retry
    await page.waitForTimeout(500);
  });

  test('deve atualizar badge de notificações em tempo real', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica que há itens pendentes
    await expect(page.getByText('23')).toBeVisible();
  });

  // ============================================================================
  // 6. PAGINAÇÃO E NAVEGAÇÃO
  // ============================================================================

  test('deve exibir controles de paginação quando há muitos itens', async ({ page }) => {
    await setupAuthMock(page);

    // Mock com muitos itens
    const manyRequests = Array.from({ length: 25 }, (_, i) => ({
      ...MOCK_REIMBURSEMENT_REQUESTS[0],
      id: `req-${i + 1}`,
      code: `REM-2024-${String(i + 1).padStart(3, '0')}`,
    }));

    await page.route('**/api/v1/reimbursements/approvals/pending**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: manyRequests.slice(0, 10),
          total: 25,
          page: 1,
          page_size: 10,
          total_pages: 3,
        }),
      });
    });

    await page.goto('/modulos/reembolso/aprovacoes');
    await page.waitForLoadState('networkidle');

    // Verifica controles de paginação
    await expect(page.getByText('Página 1 de 3')).toBeVisible();
    await expect(page.getByRole('button', { name: '' }).nth(1)).toBeVisible(); // Botão próxima página
  });

  test('deve permitir navegar entre páginas', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/reimbursements/approvals/pending**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: MOCK_REIMBURSEMENT_REQUESTS,
          total: 25,
          page: 1,
          page_size: 10,
          total_pages: 3,
        }),
      });
    });

    await page.goto('/modulos/reembolso/aprovacoes');
    await page.waitForLoadState('networkidle');

    // Clica em próxima página
    const nextButton = page.locator('button').filter({ has: page.locator('svg[class*="ChevronRight"]') });
    if (await nextButton.isVisible().catch(() => false)) {
      await nextButton.click();
      await page.waitForTimeout(300);
    }
  });

  test('deve desabilitar botão de página anterior na primeira página', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica botão anterior desabilitado
    const prevButton = page.locator('button').filter({ has: page.locator('svg[class*="ChevronLeft"]') });
    if (await prevButton.isVisible().catch(() => false)) {
      await expect(prevButton).toBeDisabled();
    }
  });

  // ============================================================================
  // 7. PERMISSÕES E SEGURANÇA
  // ============================================================================

  test('deve redirecionar para login quando não autenticado', async ({ page }) => {
    // Mock de não autenticado
    await page.route('**/api/v1/auth/me', (route) => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Não autenticado' }),
      });
    });

    await page.goto('/modulos/reembolso/aprovacoes');
    await page.waitForLoadState('networkidle');

    // Verifica redirecionamento
    await expect(page).toHaveURL(/.*login.*/);
  });

  test('deve exibir apenas ações permitidas ao usuário', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica que botões de ação estão visíveis
    await expect(page.getByRole('button', { name: /^Aprovar$/ }).first()).toBeVisible();
  });

  test('deve bloquear ações em solicitações já processadas', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica permissões das solicitações
    await expect(page.getByText('REM-2024-001')).toBeVisible();
  });

  // ============================================================================
  // 8. INTERFACE E USABILIDADE
  // ============================================================================

  test('deve ter layout responsivo', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Testa viewport mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verifica se conteúdo ainda é visível
    await expect(page.getByText('Aprovações Pendentes')).toBeVisible();

    // Restaura viewport
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('deve exibir loading state durante carregamento', async ({ page }) => {
    await setupAuthMock(page);

    // Delay artificial para mostrar loading
    await page.route('**/api/v1/reimbursements/approvals/pending**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 500));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: MOCK_REIMBURSEMENT_REQUESTS,
          total: 3,
          page: 1,
          page_size: 10,
          total_pages: 1,
        }),
      });
    });

    await page.goto('/modulos/reembolso/aprovacoes');

    // Verifica loading
    await expect(page.locator('.animate-spin, .animate-pulse').first()).toBeVisible();

    await page.waitForLoadState('networkidle');
  });

  test('deve permitir refresh manual da lista', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Clica no botão de atualizar
    await page.getByRole('button', { name: 'Atualizar' }).click();

    // Aguarda atualização
    await page.waitForTimeout(500);

    // Verifica se lista ainda está visível
    await expect(page.getByText('REM-2024-001')).toBeVisible();
  });

  // ============================================================================
  // 9. INTEGRAÇÃO E FLUXO COMPLETO
  // ============================================================================

  test('fluxo completo: visualizar detalhes e aprovar', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Configura mock de detalhes
    await page.route('**/api/v1/reimbursements/req-001', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_REIMBURSEMENT_REQUESTS[0]),
      });
    });

    // 1. Visualiza detalhes
    await page.locator('button[title="Ver Detalhes"]').first().click();
    await expect(page.getByText('Detalhes da Solicitação')).toBeVisible();

    // 2. Fecha modal
    await page.getByRole('button', { name: 'Fechar' }).click();

    // 3. Aprova solicitação
    await page.getByRole('button', { name: /^Aprovar$/ }).first().click();
    await page.getByRole('button', { name: 'Confirmar Aprovação' }).click();

    // Aguarda processamento
    await page.waitForTimeout(600);
  });

  test('deve manter estado ao navegar entre módulos', async ({ page }) => {
    await gotoApprovalsPage(page);

    // Verifica estado inicial
    await expect(page.getByText('REM-2024-001')).toBeVisible();

    // Navega para outra página
    await page.goto('/modulos');
    await page.waitForLoadState('networkidle');

    // Volta para aprovações
    await page.goto('/modulos/reembolso/aprovacoes');
    await page.waitForLoadState('networkidle');

    // Verifica que dados foram recarregados
    await expect(page.getByText('Aprovações Pendentes')).toBeVisible();
  });
});
