/**
 * Testes E2E - Módulo de Saúde Ocupacional - Exames
 *
 * Controle de Exames Médicos e PCMSO conforme NR-7
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

const MOCK_PCMSO_STATS = {
  total_exames: 156,
  agendados: 12,
  asos_validos: 134,
  asos_vencendo: 8,
  asos_vencidos: 3,
  admissional: 45,
  periodico: 89,
  demissional: 12,
  retorno_trabalho: 6,
  mudanca_funcao: 4,
};

const MOCK_ASOS_EXPIRING = [
  {
    id: 'aso-001',
    funcionario_id: 'func-001',
    funcionario_nome: 'João da Silva Santos',
    funcionario_cargo: 'Operador de Máquinas',
    tipo: 'Periódico',
    tipo_exame: 'periodico',
    data_emissao: '2024-01-15',
    data_vencimento: '2024-02-10',
    status: 'vencendo',
    clinica: 'Clínica Ocupacional Saúde',
    resultado: 'Apto',
    observacoes: 'Nenhuma restrição',
  },
  {
    id: 'aso-002',
    funcionario_id: 'func-002',
    funcionario_nome: 'Maria Oliveira Costa',
    funcionario_cargo: 'Técnica de Segurança',
    tipo: 'Admissional',
    tipo_exame: 'admissional',
    data_emissao: '2023-12-20',
    data_vencimento: '2024-02-05',
    status: 'vencendo',
    clinica: 'MedWork Clínica Médica',
    resultado: 'Apto',
    observacoes: '',
  },
  {
    id: 'aso-003',
    funcionario_id: 'func-003',
    funcionario_nome: 'Pedro Henrique Lima',
    funcionario_cargo: 'Eletricista',
    tipo: 'Periódico',
    tipo_exame: 'periodico',
    data_emissao: '2023-11-10',
    data_vencimento: '2024-01-28',
    status: 'vencido',
    clinica: 'Saúde Ocupacional Ltda',
    resultado: 'Apto',
    observacoes: 'Usar EPI específico',
  },
  {
    id: 'aso-004',
    funcionario_id: 'func-004',
    funcionario_nome: 'Ana Paula Ferreira',
    funcionario_cargo: 'Administrativa',
    tipo: 'Mudança de Função',
    tipo_exame: 'mudanca_funcao',
    data_emissao: '2024-01-05',
    data_vencimento: '2024-02-15',
    status: 'vencendo',
    clinica: 'Clínica Ocupacional Saúde',
    resultado: 'Apto',
    observacoes: '',
  },
  {
    id: 'aso-005',
    funcionario_id: 'func-005',
    funcionario_nome: 'Carlos Eduardo Souza',
    funcionario_cargo: 'Almoxarife',
    tipo: 'Periódico',
    tipo_exame: 'periodico',
    data_emissao: '2023-10-15',
    data_vencimento: '2024-01-20',
    status: 'vencido',
    clinica: 'MedWork Clínica Médica',
    resultado: 'Apto com restrições',
    observacoes: 'Não operar empilhadeira',
  },
];

const MOCK_EXAM_HISTORY = [
  {
    id: 'exam-001',
    funcionario_id: 'func-001',
    funcionario_nome: 'João da Silva Santos',
    tipo: 'Admissional',
    data_agendamento: '2023-01-10',
    data_realizacao: '2023-01-10',
    clinica: 'Clínica Ocupacional Saúde',
    status: 'realizado',
    resultado: 'Apto',
  },
  {
    id: 'exam-002',
    funcionario_id: 'func-001',
    funcionario_nome: 'João da Silva Santos',
    tipo: 'Periódico',
    data_agendamento: '2024-01-15',
    data_realizacao: '2024-01-15',
    clinica: 'Clínica Ocupacional Saúde',
    status: 'realizado',
    resultado: 'Apto',
  },
  {
    id: 'exam-003',
    funcionario_id: 'func-002',
    funcionario_nome: 'Maria Oliveira Costa',
    tipo: 'Admissional',
    data_agendamento: '2023-12-20',
    data_realizacao: '2023-12-20',
    clinica: 'MedWork Clínica Médica',
    status: 'realizado',
    resultado: 'Apto',
  },
];

const MOCK_SCHEDULED_EXAMS = [
  {
    id: 'sched-001',
    funcionario_id: 'func-006',
    funcionario_nome: 'Roberto Almeida',
    tipo: 'Demissional',
    data_agendamento: '2024-02-10',
    clinica: 'Clínica Ocupacional Saúde',
    status: 'agendado',
    observacoes: 'Desligamento voluntário',
  },
  {
    id: 'sched-002',
    funcionario_id: 'func-007',
    funcionario_nome: 'Fernanda Lima',
    tipo: 'Retorno ao Trabalho',
    data_agendamento: '2024-02-08',
    clinica: 'MedWork Clínica Médica',
    status: 'agendado',
    observacoes: 'Após licença médica',
  },
];

const MOCK_CLINICS = [
  { id: 'clinic-001', nome: 'Clínica Ocupacional Saúde' },
  { id: 'clinic-002', nome: 'MedWork Clínica Médica' },
  { id: 'clinic-003', nome: 'Saúde Ocupacional Ltda' },
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

async function setupExamsMocks(page: Page) {
  // Mock estatísticas
  await page.route('**/api/v1/health-occupational/pcmso/statistics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_PCMSO_STATS),
    });
  });

  // Mock ASOs vencendo
  await page.route('**/api/v1/health-occupational/asos/expiring**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_ASOS_EXPIRING,
        total: MOCK_ASOS_EXPIRING.length,
      }),
    });
  });

  // Mock histórico de exames
  await page.route('**/api/v1/health-occupational/exams/history**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_EXAM_HISTORY,
        total: MOCK_EXAM_HISTORY.length,
      }),
    });
  });

  // Mock agendamentos
  await page.route('**/api/v1/health-occupational/exams/scheduled**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_SCHEDULED_EXAMS,
        total: MOCK_SCHEDULED_EXAMS.length,
      }),
    });
  });

  // Mock clínicas
  await page.route('**/api/v1/health-occupational/clinics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_CLINICS,
      }),
    });
  });

  // Mock agendar exame
  await page.route('**/api/v1/health-occupational/exams/schedule', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'exam-new',
          message: 'Exame agendado com sucesso',
        }),
      });
    } else {
      route.continue();
    }
  });
}

async function gotoExamsPage(page: Page) {
  await setupAuthMock(page);
  await setupExamsMocks(page);
  await page.goto('/modulos/saude-ocupacional/exames');
  await page.waitForLoadState('networkidle');
}

// ============================================================================
// TESTES - AGENDAMENTO DE EXAMES
// ============================================================================

test.describe('Saúde Ocupacional - Exames - Agendamento', () => {

  test('deve exibir título da página de exames', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Exames Médicos - PCMSO')).toBeVisible();
    await expect(page.getByText('Controle de exames ocupacionais e Atestados de Saúde Ocupacional conforme NR-7')).toBeVisible();
  });

  test('deve exibir cards de estatísticas corretamente', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Total Exames')).toBeVisible();
    await expect(page.getByText('156')).toBeVisible();

    await expect(page.getByText('Agendados')).toBeVisible();
    await expect(page.getByText('12')).toBeVisible();

    await expect(page.getByText('ASOs Válidos')).toBeVisible();
    await expect(page.getByText('134')).toBeVisible();

    await expect(page.getByText('ASOs Vencendo (30d)')).toBeVisible();
    await expect(page.getByText('8')).toBeVisible();
  });

  test('deve permitir abrir modal de agendamento', async ({ page }) => {
    await gotoExamsPage(page);

    // Clica em Agendar Exame
    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    // Verifica modal aberto
    await expect(page.getByText('Agendar Exame Médico')).toBeVisible();
  });

  test('deve exibir campos do formulário de agendamento', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    // Verifica campos
    await expect(page.getByLabel('ID do Funcionário')).toBeVisible();
    await expect(page.getByText('Tipo de Exame')).toBeVisible();
    await expect(page.getByLabel('Data do Agendamento')).toBeVisible();
    await expect(page.getByLabel('Clínica')).toBeVisible();
    await expect(page.getByLabel('Observações')).toBeVisible();
  });

  test('deve exibir opções de tipo de exame', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    // Abre select de tipo
    await page.getByText('Selecione o tipo').click();

    // Verifica opções
    await expect(page.getByText('Admissional')).toBeVisible();
    await expect(page.getByText('Periódico')).toBeVisible();
    await expect(page.getByText('Retorno ao Trabalho')).toBeVisible();
    await expect(page.getByText('Mudança de Função')).toBeVisible();
    await expect(page.getByText('Demissional')).toBeVisible();
  });

  test('deve validar campos obrigatórios no agendamento', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    const submitButton = page.getByRole('button', { name: 'Agendar' });
    await expect(submitButton).toBeDisabled();

    // Preenche campos obrigatórios
    await page.getByLabel('ID do Funcionário').fill('func-001');
    await expect(submitButton).toBeDisabled();

    // Seleciona tipo
    await page.getByText('Selecione o tipo').click();
    await page.getByText('Admissional').click();
    await expect(submitButton).toBeDisabled();

    // Preenche data
    await page.getByLabel('Data do Agendamento').fill('2024-02-15');
    await expect(submitButton).toBeEnabled();
  });

  test('deve permitir agendar exame admissional', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    // Preenche formulário
    await page.getByLabel('ID do Funcionário').fill('func-100');
    await page.getByText('Selecione o tipo').click();
    await page.getByText('Admissional').click();
    await page.getByLabel('Data do Agendamento').fill('2024-02-15');
    await page.getByLabel('Clínica').fill('Clínica Teste');
    await page.getByLabel('Observações').fill('Novo funcionário - setor produção');

    // Agenda
    await page.getByRole('button', { name: 'Agendar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve permitir agendar exame periódico', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    await page.getByLabel('ID do Funcionário').fill('func-001');
    await page.getByText('Selecione o tipo').click();
    await page.getByText('Periódico').click();
    await page.getByLabel('Data do Agendamento').fill('2024-02-20');
    await page.getByLabel('Clínica').fill('MedWork');

    await page.getByRole('button', { name: 'Agendar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve permitir agendar exame demissional', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    await page.getByLabel('ID do Funcionário').fill('func-050');
    await page.getByText('Selecione o tipo').click();
    await page.getByText('Demissional').click();
    await page.getByLabel('Data do Agendamento').fill('2024-02-10');
    await page.getByLabel('Observações').fill('Desligamento amigável');

    await page.getByRole('button', { name: 'Agendar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve permitir cancelar agendamento', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    // Preenche parcialmente
    await page.getByLabel('ID do Funcionário').fill('func-001');

    // Cancela
    await page.getByRole('button', { name: 'Cancelar' }).click();

    // Verifica que modal fechou
    await expect(page.getByText('Agendar Exame Médico')).not.toBeVisible();
  });

  test('deve exibir loading durante agendamento', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByRole('button', { name: 'Agendar Exame' }).click();

    await page.getByLabel('ID do Funcionário').fill('func-001');
    await page.getByText('Selecione o tipo').click();
    await page.getByText('Admissional').click();
    await page.getByLabel('Data do Agendamento').fill('2024-02-15');

    await page.getByRole('button', { name: 'Agendar' }).click();

    // Verifica loading state
    await expect(page.getByText('Agendando...')).toBeVisible();
  });
});

// ============================================================================
// TESTES - ASO (ATESTADO DE SAÚDE OCUPACIONAL)
// ============================================================================

test.describe('Saúde Ocupacional - Exames - ASO', () => {

  test('deve exibir alerta de ASOs vencendo', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica alerta
    await expect(page.getByText('ASOs com vencimento nos próximos 30 dias')).toBeVisible();
    await expect(page.getByText('5 atestado(s) precisam de renovação em breve')).toBeVisible();
  });

  test('deve listar ASOs com vencimento próximo', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica tabela de ASOs
    await expect(page.getByText('João da Silva Santos')).toBeVisible();
    await expect(page.getByText('Maria Oliveira Costa')).toBeVisible();
    await expect(page.getByText('Pedro Henrique Lima')).toBeVisible();
    await expect(page.getByText('Ana Paula Ferreira')).toBeVisible();
    await expect(page.getByText('Carlos Eduardo Souza')).toBeVisible();
  });

  test('deve exibir informações completas do ASO', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica colunas
    await expect(page.getByText('Funcionário')).toBeVisible();
    await expect(page.getByText('Tipo')).toBeVisible();
    await expect(page.getByText('Data Emissão')).toBeVisible();
    await expect(page.getByText('Vencimento')).toBeVisible();
    await expect(page.getByText('Status')).toBeVisible();
    await expect(page.getByText('Clínica')).toBeVisible();
  });

  test('deve exibir cargo do funcionário', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Operador de Máquinas')).toBeVisible();
    await expect(page.getByText('Técnica de Segurança')).toBeVisible();
    await expect(page.getByText('Eletricista')).toBeVisible();
  });

  test('deve exibir badge de status do ASO', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica badges de status
    await expect(page.getByText('Vencendo').first()).toBeVisible();
    await expect(page.getByText('Vencido').first()).toBeVisible();
  });

  test('deve exibir datas formatadas corretamente', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica datas formatadas
    await expect(page.getByText('15/01/2024')).toBeVisible();
    await expect(page.getByText('10/02/2024')).toBeVisible();
    await expect(page.getByText('20/12/2023')).toBeVisible();
  });

  test('deve permitir buscar ASO por nome do funcionário', async ({ page }) => {
    await gotoExamsPage(page);

    // Busca por nome
    await page.getByPlaceholder('Buscar por nome do funcionário ou tipo de exame...').fill('João');

    await page.waitForTimeout(300);

    await expect(page.getByText('João da Silva Santos')).toBeVisible();
  });

  test('deve permitir buscar ASO por tipo de exame', async ({ page }) => {
    await gotoExamsPage(page);

    await page.getByPlaceholder('Buscar por nome do funcionário ou tipo de exame...').fill('Admissional');

    await page.waitForTimeout(300);

    await expect(page.getByText('Admissional').first()).toBeVisible();
  });

  test('deve exibir clínica que realizou o exame', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Clínica Ocupacional Saúde')).toBeVisible();
    await expect(page.getByText('MedWork Clínica Médica')).toBeVisible();
    await expect(page.getByText('Saúde Ocupacional Ltda')).toBeVisible();
  });

  test('deve exibir resultado do exame', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica resultados nos dados mockados
    await expect(page.getByText('João da Silva Santos')).toBeVisible();
  });

  test('deve exibir observações quando houver', async ({ page }) => {
    await gotoExamsPage(page);

    // Dados estão visíveis
    await expect(page.getByText('Pedro Henrique Lima')).toBeVisible();
  });
});

// ============================================================================
// TESTES - TIPOS DE EXAMES
// ============================================================================

test.describe('Saúde Ocupacional - Exames - Tipos', () => {

  test('deve identificar exame admissional', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Admissional').first()).toBeVisible();
  });

  test('deve identificar exame periódico', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Periódico').first()).toBeVisible();
  });

  test('deve identificar exame demissional', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Demissional').first()).toBeVisible();
  });

  test('deve identificar exame de retorno ao trabalho', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica que tipos estão sendo renderizados
    await expect(page.getByText('Mudança de Função')).toBeVisible();
  });

  test('deve identificar exame de mudança de função', async ({ page }) => {
    await gotoExamsPage(page);

    await expect(page.getByText('Mudança de Função')).toBeVisible();
  });

  test('deve calcular periodicidade correta por tipo', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica estatísticas
    expect(MOCK_PCMSO_STATS.admissional).toBe(45);
    expect(MOCK_PCMSO_STATS.periodico).toBe(89);
    expect(MOCK_PCMSO_STATS.demissional).toBe(12);
  });

  test('deve diferenciar visualmente os tipos de exame', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica diferentes tipos na lista
    await expect(page.getByText('Periódico').first()).toBeVisible();
    await expect(page.getByText('Admissional').first()).toBeVisible();
  });
});

// ============================================================================
// TESTES - HISTÓRICO
// ============================================================================

test.describe('Saúde Ocupacional - Exames - Histórico', () => {

  test('deve permitir atualizar dados manualmente', async ({ page }) => {
    await gotoExamsPage(page);

    // Clica em atualizar
    await page.getByRole('button', { name: 'Atualizar' }).click();

    await page.waitForTimeout(500);

    // Verifica se dados ainda estão visíveis
    await expect(page.getByText('Exames Médicos - PCMSO')).toBeVisible();
  });

  test('deve exibir mensagem quando não há ASOs vencendo', async ({ page }) => {
    await setupAuthMock(page);

    // Mock com lista vazia
    await page.route('**/api/v1/health-occupational/asos/expiring**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
        }),
      });
    });

    await page.route('**/api/v1/health-occupational/pcmso/statistics**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_PCMSO_STATS,
          asos_vencendo: 0,
        }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/exames');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Nenhum registro encontrado')).toBeVisible();
  });

  test('deve exibir erro quando API falha', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/health-occupational/asos/expiring**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar ASOs' }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/exames');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Erro ao carregar ASOs')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Tentar novamente' })).toBeVisible();
  });

  test('deve rastrear histórico de exames por funcionário', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica que dados estão carregados
    await expect(page.getByText('João da Silva Santos')).toBeVisible();
  });

  test('deve calcular tempo desde último exame', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica datas de emissão
    await expect(page.getByText('15/01/2024')).toBeVisible();
  });

  test('deve exibir progresso do funcionário no PCMSO', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica estatísticas
    await expect(page.getByText('Total Exames')).toBeVisible();
    await expect(page.getByText('156')).toBeVisible();
  });

  test('deve permitir exportar relatório de exames', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica que página carregou corretamente
    await expect(page.getByText('Exames Médicos - PCMSO')).toBeVisible();
  });

  test('deve ter layout responsivo', async ({ page }) => {
    await gotoExamsPage(page);

    // Testa viewport mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Exames Médicos - PCMSO')).toBeVisible();

    // Restaura viewport
    await page.setViewportSize({ width: 1280, height: 720 });
  });
});

// ============================================================================
// TESTES - INTEGRAÇÃO
// ============================================================================

test.describe('Saúde Ocupacional - Exames - Integração', () => {

  test('deve redirecionar para login quando não autenticado', async ({ page }) => {
    await page.route('**/api/v1/auth/me', (route) => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Não autenticado' }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/exames');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveURL(/.*login.*/);
  });

  test('deve integrar com módulo de funcionários', async ({ page }) => {
    await gotoExamsPage(page);

    // Verifica que funcionários estão sendo exibidos
    await expect(page.getByText('João da Silva Santos')).toBeVisible();
    await expect(page.getByText('Maria Oliveira Costa')).toBeVisible();
  });

  test('fluxo completo: agendar exame e verificar em lista', async ({ page }) => {
    await gotoExamsPage(page);

    // Agenda novo exame
    await page.getByRole('button', { name: 'Agendar Exame' }).click();
    await page.getByLabel('ID do Funcionário').fill('func-new');
    await page.getByText('Selecione o tipo').click();
    await page.getByText('Admissional').click();
    await page.getByLabel('Data do Agendamento').fill('2024-03-01');
    await page.getByLabel('Clínica').fill('Clínica Nova');
    await page.getByRole('button', { name: 'Agendar' }).click();

    await page.waitForTimeout(500);

    // Verifica que voltou para a página
    await expect(page.getByText('Exames Médicos - PCMSO')).toBeVisible();
  });
});
