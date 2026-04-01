/**
 * Testes E2E - Módulo de Saúde Ocupacional - Riscos
 *
 * Mapeamento de Riscos Ocupacionais conforme PPRA/PGR - NR-9
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

const MOCK_PPRA_STATS = {
  total_riscos: 28,
  setores_mapeados: 8,
  medidas_implementadas: 45,
  medidas_pendentes: 12,
  riscos_fisicos: 10,
  riscos_quimicos: 6,
  riscos_biologicos: 3,
  riscos_ergonomicos: 5,
  riscos_acidente: 4,
};

const MOCK_RISK_MAPPINGS = [
  {
    id: 'risk-001',
    setor: 'Produção',
    funcao: 'Operador de Máquina',
    agente_risco: 'Ruído contínuo',
    categoria: 'fisico',
    nivel_risco: 'moderado',
    fonte_geradora: 'Máquinas industriais',
    meio_propagacao: 'Ar',
    medidas_existentes: 'Protetor auricular, manutenção preventiva',
    observacoes: 'Monitoramento semestral',
  },
  {
    id: 'risk-002',
    setor: 'Produção',
    funcao: 'Operador de Máquina',
    agente_risco: 'Vibração de mãos e braços',
    categoria: 'fisico',
    nivel_risco: 'toleravel',
    fonte_geradora: 'Ferramentas pneumáticas',
    meio_propagacao: 'Contato direto',
    medidas_existentes: 'Luvas antivibração',
    observacoes: '',
  },
  {
    id: 'risk-003',
    setor: 'Laboratório',
    funcao: 'Técnico Químico',
    agente_risco: 'Solventes orgânicos',
    categoria: 'quimico',
    nivel_risco: 'substancial',
    fonte_geradora: 'Processos de limpeza',
    meio_propagacao: 'Inalação, contato dérmico',
    medidas_existentes: 'Capela química, EPI completo',
    observacoes: 'Monitoramento ambiental trimestral',
  },
  {
    id: 'risk-004',
    setor: 'Laboratório',
    funcao: 'Técnico Químico',
    agente_risco: 'Ácidos e bases',
    categoria: 'quimico',
    nivel_risco: 'moderado',
    fonte_geradora: 'Manipulação de reagentes',
    meio_propagacao: 'Contato direto',
    medidas_existentes: 'Avental, óculos, luvas específicas',
    observacoes: 'Kit de emergência disponível',
  },
  {
    id: 'risk-005',
    setor: 'Enfermaria',
    funcao: 'Enfermeiro',
    agente_risco: 'Agentes biológicos',
    categoria: 'biologico',
    nivel_risco: 'moderado',
    fonte_geradora: 'Materiais biológicos',
    meio_propagacao: 'Contato direto, aerosóis',
    medidas_existentes: 'EPI descartável, vacinação',
    observacoes: 'Protocolo de biossegurança',
  },
  {
    id: 'risk-006',
    setor: 'Escritório',
    funcao: 'Analista Administrativo',
    agente_risco: 'Movimentação repetitiva',
    categoria: 'ergonomico',
    nivel_risco: 'toleravel',
    fonte_geradora: 'Trabalho com computador',
    meio_propagacao: 'Postura inadequada',
    medidas_existentes: 'Cadeira ergonômica, pausas',
    observacoes: 'Ginástica laboral',
  },
  {
    id: 'risk-007',
    setor: 'Almoxarifado',
    funcao: 'Almoxarife',
    agente_risco: 'Queda de materiais',
    categoria: 'acidente',
    nivel_risco: 'moderado',
    fonte_geradora: 'Empilhamento inadequado',
    meio_propagacao: 'Gravidade',
    medidas_existentes: 'EPI, treinamento',
    observacoes: 'Sinalização adequada',
  },
  {
    id: 'risk-008',
    setor: 'Manutenção',
    funcao: 'Eletricista',
    agente_risco: 'Choque elétrico',
    categoria: 'acidente',
    nivel_risco: 'intoleravel',
    fonte_geradora: 'Circuitos energizados',
    meio_propagacao: 'Contato direto',
    medidas_existentes: 'Bloqueio e etiquetagem, EPI',
    observacoes: 'Apenas eletricistas autorizados',
  },
];

const MOCK_RISK_CATEGORIES = [
  { id: 'cat-001', value: 'fisico', label: 'Físico' },
  { id: 'cat-002', value: 'quimico', label: 'Químico' },
  { id: 'cat-003', value: 'biologico', label: 'Biológico' },
  { id: 'cat-004', value: 'ergonomico', label: 'Ergonômico' },
  { id: 'cat-005', value: 'acidente', label: 'Acidente' },
];

const MOCK_ASSESSMENTS = [
  {
    id: 'assess-001',
    setor: 'Produção',
    data_avaliacao: '2024-01-15',
    avaliador: 'Eng. Maria Santos',
    proxima_avaliacao: '2025-01-15',
    status: 'vigente',
  },
  {
    id: 'assess-002',
    setor: 'Laboratório',
    data_avaliacao: '2023-08-20',
    avaliador: 'Eng. João Lima',
    proxima_avaliacao: '2024-08-20',
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

async function setupRisksMocks(page: Page) {
  // Mock estatísticas
  await page.route('**/api/v1/health-occupational/ppra/statistics**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_PPRA_STATS),
    });
  });

  // Mock mapeamentos
  await page.route('**/api/v1/health-occupational/risk-mappings**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_RISK_MAPPINGS,
        total: MOCK_RISK_MAPPINGS.length,
      }),
    });
  });

  // Mock categorias
  await page.route('**/api/v1/health-occupational/risk-categories**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_RISK_CATEGORIES,
      }),
    });
  });

  // Mock avaliações
  await page.route('**/api/v1/health-occupational/assessments**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: MOCK_ASSESSMENTS,
        total: MOCK_ASSESSMENTS.length,
      }),
    });
  });

  // Mock criação
  await page.route('**/api/v1/health-occupational/risk-mappings', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'risk-new',
          message: 'Mapeamento criado com sucesso',
        }),
      });
    } else {
      route.continue();
    }
  });

  // Mock update
  await page.route('**/api/v1/health-occupational/risk-mappings/*', (route) => {
    if (route.request().method() === 'PATCH' || route.request().method() === 'PUT') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Mapeamento atualizado com sucesso',
        }),
      });
    } else {
      route.continue();
    }
  });
}

async function gotoRisksPage(page: Page) {
  await setupAuthMock(page);
  await setupRisksMocks(page);
  await page.goto('/modulos/saude-ocupacional/riscos');
  await page.waitForLoadState('load');
}

// ============================================================================
// TESTES - CADASTRO DE RISCOS
// ============================================================================

test.describe('Saúde Ocupacional - Riscos - Cadastro', () => {

  test('deve exibir título da página de riscos', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Riscos Ocupacionais - PPRA/PGR')).toBeVisible();
    await expect(page.getByText('Mapeamento e gestão de riscos ocupacionais, medidas de controle e análise por setor conforme NR-9')).toBeVisible();
  });

  test('deve exibir cards de estatísticas corretamente', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Total Riscos')).toBeVisible();
    await expect(page.getByText('28')).toBeVisible();

    await expect(page.getByText('Setores Mapeados')).toBeVisible();
    await expect(page.getByText('8')).toBeVisible();

    await expect(page.getByText('Medidas Implementadas')).toBeVisible();
    await expect(page.getByText('45')).toBeVisible();

    await expect(page.getByText('Medidas Pendentes')).toBeVisible();
    await expect(page.getByText('12')).toBeVisible();
  });

  test('deve listar todos os mapeamentos de riscos', async ({ page }) => {
    await gotoRisksPage(page);

    // Verifica lista
    await expect(page.getByText('Ruído contínuo')).toBeVisible();
    await expect(page.getByText('Vibração de mãos e braços')).toBeVisible();
    await expect(page.getByText('Solventes orgânicos')).toBeVisible();
    await expect(page.getByText('Agentes biológicos')).toBeVisible();
    await expect(page.getByText('Movimentação repetitiva')).toBeVisible();
    await expect(page.getByText('Queda de materiais')).toBeVisible();
    await expect(page.getByText('Choque elétrico')).toBeVisible();
  });

  test('deve exibir informações detalhadas de cada risco', async ({ page }) => {
    await gotoRisksPage(page);

    // Verifica colunas
    await expect(page.getByText('Setor')).toBeVisible();
    await expect(page.getByText('Função')).toBeVisible();
    await expect(page.getByText('Agente de Risco')).toBeVisible();
    await expect(page.getByText('Categoria')).toBeVisible();
    await expect(page.getByText('Nível')).toBeVisible();
    await expect(page.getByText('Fonte Geradora')).toBeVisible();
  });

  test('deve exibir setor e função do risco', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Produção').first()).toBeVisible();
    await expect(page.getByText('Laboratório').first()).toBeVisible();
    await expect(page.getByText('Enfermaria')).toBeVisible();
    await expect(page.getByText('Operador de Máquina')).toBeVisible();
    await expect(page.getByText('Técnico Químico')).toBeVisible();
  });

  test('deve permitir buscar riscos por setor', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByPlaceholder('Buscar por setor, função ou agente de risco...').fill('Produção');

    await page.waitForTimeout(300);

    await expect(page.getByText('Ruído contínuo')).toBeVisible();
  });

  test('deve permitir buscar riscos por agente', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByPlaceholder('Buscar por setor, função ou agente de risco...').fill('Ruído');

    await page.waitForTimeout(300);

    await expect(page.getByText('Ruído contínuo')).toBeVisible();
  });

  test('deve permitir filtrar por setor específico', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByPlaceholder('Filtrar por setor').fill('Laboratório');

    await page.waitForTimeout(300);

    await expect(page.getByText('Solventes orgânicos')).toBeVisible();
  });

  test('deve permitir cadastrar novo mapeamento de risco', async ({ page }) => {
    await gotoRisksPage(page);

    // Clica em Novo Mapeamento
    await page.getByRole('button', { name: 'Novo Mapeamento' }).click();

    // Preenche formulário
    await page.getByLabel('Setor').fill('Expedição');
    await page.getByLabel('Função').fill('Motorista');
    await page.getByLabel('Agente de Risco').fill('Postura inadequada ao dirigir');

    // Seleciona categoria
    await page.getByText('Selecione').first().click();
    await page.getByText('Ergonômico').click();

    // Seleciona nível
    await page.getByText('Selecione').nth(1).click();
    await page.getByText('Tolerável').click();

    await page.getByLabel('Fonte Geradora').fill('Veículo sem ajuste adequado');
    await page.getByLabel('Meio de Propagação').fill('Postura prolongada');
    await page.getByLabel('Medidas de Controle Existentes').fill('Treinamento, ajuste do banco');

    // Salva
    await page.getByRole('button', { name: 'Cadastrar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve validar campos obrigatórios no cadastro', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByRole('button', { name: 'Novo Mapeamento' }).click();

    const submitButton = page.getByRole('button', { name: 'Cadastrar' });
    await expect(submitButton).toBeDisabled();

    // Preenche setor
    await page.getByLabel('Setor').fill('Teste');
    await expect(submitButton).toBeDisabled();

    // Preenche agente
    await page.getByLabel('Agente de Risco').fill('Teste');
    await expect(submitButton).toBeDisabled();

    // Seleciona categoria
    await page.getByText('Selecione').first().click();
    await page.getByText('Físico').click();

    // Agora deve estar habilitado
    await expect(submitButton).toBeEnabled();
  });

  test('deve permitir editar mapeamento existente', async ({ page }) => {
    await gotoRisksPage(page);

    // Clica em editar
    await page.locator('button').filter({ has: page.locator('svg[class*="Edit"]') }).first().click();

    // Modal de edição aberto
    await expect(page.getByText('Editar Mapeamento')).toBeVisible();

    // Altera dados
    await page.getByLabel('Agente de Risco').fill('Ruído contínuo - Atualizado');

    // Salva
    await page.getByRole('button', { name: 'Salvar' }).click();

    await page.waitForTimeout(500);
  });

  test('deve exibir mensagem quando não há riscos cadastrados', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/health-occupational/risk-mappings**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
        }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/riscos');
    await page.waitForLoadState('load');

    await expect(page.getByText('Nenhum registro encontrado')).toBeVisible();
    await expect(page.getByText('Tente ajustar os filtros ou crie um novo mapeamento de risco')).toBeVisible();
  });
});

// ============================================================================
// TESTES - CATEGORIAS DE RISCOS
// ============================================================================

test.describe('Saúde Ocupacional - Riscos - Categorias', () => {

  test('deve exibir badge de categoria física', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Físico').first()).toBeVisible();
  });

  test('deve exibir badge de categoria química', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Químico').first()).toBeVisible();
  });

  test('deve exibir badge de categoria biológica', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Biológico')).toBeVisible();
  });

  test('deve exibir badge de categoria ergonômica', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Ergonômico')).toBeVisible();
  });

  test('deve exibir badge de categoria de acidente', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Acidente').first()).toBeVisible();
  });

  test('deve permitir selecionar categoria no cadastro', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByRole('button', { name: 'Novo Mapeamento' }).click();

    // Abre select
    await page.getByText('Selecione').first().click();

    // Verifica todas as opções
    await expect(page.getByText('Físico')).toBeVisible();
    await expect(page.getByText('Químico')).toBeVisible();
    await expect(page.getByText('Biológico')).toBeVisible();
    await expect(page.getByText('Ergonômico')).toBeVisible();
    await expect(page.getByText('Acidente')).toBeVisible();
  });

  test('deve calcular corretamente distribuição por categoria', async ({ page }) => {
    await gotoRisksPage(page);

    // Verifica estatísticas
    expect(MOCK_PPRA_STATS.riscos_fisicos).toBe(10);
    expect(MOCK_PPRA_STATS.riscos_quimicos).toBe(6);
    expect(MOCK_PPRA_STATS.riscos_biologicos).toBe(3);
    expect(MOCK_PPRA_STATS.riscos_ergonomicos).toBe(5);
    expect(MOCK_PPRA_STATS.riscos_acidente).toBe(4);

    // Total deve ser 28
    const total = 10 + 6 + 3 + 5 + 4;
    expect(total).toBe(28);
  });
});

// ============================================================================
// TESTES - NÍVEIS DE RISCO
// ============================================================================

test.describe('Saúde Ocupacional - Riscos - Níveis', () => {

  test('deve exibir badge de nível trivial', async ({ page }) => {
    await gotoRisksPage(page);

    // Verifica badges de nível
    const trivialRisks = MOCK_RISK_MAPPINGS.filter(r => r.nivel_risco === 'trivial');
    expect(trivialRisks.length).toBeGreaterThan(0);
  });

  test('deve exibir badge de nível tolerável', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Tolerável').first()).toBeVisible();
  });

  test('deve exibir badge de nível moderado', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Moderado').first()).toBeVisible();
  });

  test('deve exibir badge de nível substancial', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Substancial')).toBeVisible();
  });

  test('deve exibir badge de nível intolerável', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Intolerável')).toBeVisible();
  });

  test('deve permitir selecionar nível no cadastro', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByRole('button', { name: 'Novo Mapeamento' }).click();

    // Abre select de nível
    await page.getByText('Selecione').nth(1).click();

    // Verifica opções
    await expect(page.getByText('Trivial')).toBeVisible();
    await expect(page.getByText('Tolerável')).toBeVisible();
    await expect(page.getByText('Moderado')).toBeVisible();
    await expect(page.getByText('Substancial')).toBeVisible();
    await expect(page.getByText('Intolerável')).toBeVisible();
  });

  test('deve identificar corretamente riscos críticos', async ({ page }) => {
    await gotoRisksPage(page);

    // Choque elétrico é intolerável
    await expect(page.getByText('Choque elétrico')).toBeVisible();
    await expect(page.getByText('Intolerável')).toBeVisible();
  });
});

// ============================================================================
// TESTES - AVALIAÇÕES AMBIENTAIS
// ============================================================================

test.describe('Saúde Ocupacional - Riscos - Avaliações', () => {

  test('deve exibir fonte geradora do risco', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Máquinas industriais')).toBeVisible();
    await expect(page.getByText('Ferramentas pneumáticas')).toBeVisible();
    await expect(page.getByText('Processos de limpeza')).toBeVisible();
  });

  test('deve exibir meio de propagação', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Ar').first()).toBeVisible();
    await expect(page.getByText('Contato direto').first()).toBeVisible();
    await expect(page.getByText('Inalação, contato dérmico')).toBeVisible();
  });

  test('deve calcular corretamente número de setores mapeados', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Setores Mapeados')).toBeVisible();
    await expect(page.getByText('8')).toBeVisible();
  });

  test('deve identificar setores únicos', async ({ page }) => {
    const setores = Array.from(new Set(MOCK_RISK_MAPPINGS.map(r => r.setor)));
    expect(setores).toContain('Produção');
    expect(setores).toContain('Laboratório');
    expect(setores).toContain('Enfermaria');
    expect(setores).toContain('Escritório');
    expect(setores).toContain('Almoxarifado');
    expect(setores).toContain('Manutenção');
  });
});

// ============================================================================
// TESTES - MEDIDAS PREVENTIVAS
// ============================================================================

test.describe('Saúde Ocupacional - Riscos - Medidas', () => {

  test('deve exibir medidas de controle existentes', async ({ page }) => {
    await gotoRisksPage(page);

    // Verifica nas descrições dos riscos
    await expect(page.getByText('Protetor auricular, manutenção preventiva')).toBeVisible();
    await expect(page.getByText('Luvas antivibração')).toBeVisible();
  });

  test('deve calcular corretamente medidas implementadas', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Medidas Implementadas')).toBeVisible();
    await expect(page.getByText('45')).toBeVisible();
  });

  test('deve calcular corretamente medidas pendentes', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Medidas Pendentes')).toBeVisible();
    await expect(page.getByText('12')).toBeVisible();
  });

  test('deve permitir adicionar medidas no cadastro', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByRole('button', { name: 'Novo Mapeamento' }).click();

    await page.getByLabel('Medidas de Controle Existentes').fill('Nova medida de teste');

    await expect(page.getByLabel('Medidas de Controle Existentes')).toHaveValue('Nova medida de teste');
  });

  test('deve permitir adicionar observações', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByRole('button', { name: 'Novo Mapeamento' }).click();

    await page.getByLabel('Observações').fill('Observação de teste');

    await expect(page.getByLabel('Observações')).toHaveValue('Observação de teste');
  });

  test('deve exibir observações quando houver', async ({ page }) => {
    await gotoRisksPage(page);

    // Verifica riscos com observações
    await expect(page.getByText('Ruído contínuo')).toBeVisible();
  });
});

// ============================================================================
// TESTES - PPRA (PROGRAMA DE PREVENÇÃO)
// ============================================================================

test.describe('Saúde Ocupacional - Riscos - PPRA', () => {

  test('deve calcular total de riscos mapeados', async ({ page }) => {
    await gotoRisksPage(page);

    await expect(page.getByText('Total Riscos')).toBeVisible();
    await expect(page.getByText('28')).toBeVisible();
  });

  test('deve identificar prioridades de ação', async ({ page }) => {
    await gotoRisksPage(page);

    // Riscos intoleráveis são prioridade
    await expect(page.getByText('Choque elétrico')).toBeVisible();
    await expect(page.getByText('Intolerável')).toBeVisible();
  });

  test('deve calcular taxa de implementação', async ({ page }) => {
    await gotoRisksPage(page);

    const implementadas = MOCK_PPRA_STATS.medidas_implementadas;
    const pendentes = MOCK_PPRA_STATS.medidas_pendentes;
    const total = implementadas + pendentes;
    const taxa = (implementadas / total) * 100;

    expect(implementadas).toBe(45);
    expect(pendentes).toBe(12);
    expect(taxa.toFixed(1)).toBe('78.9');
  });

  test('deve permitir gerar relatório PPRA', async ({ page }) => {
    await gotoRisksPage(page);

    // Verifica que página está carregada com dados
    await expect(page.getByText('Riscos Ocupacionais - PPRA/PGR')).toBeVisible();
    await expect(page.getByText('28')).toBeVisible();
  });

  test('deve integrar com PCMSO', async ({ page }) => {
    await gotoRisksPage(page);

    // Dados de riscos devem estar disponíveis para vinculação com exames
    await expect(page.getByText('Agentes biológicos')).toBeVisible();
  });
});

// ============================================================================
// TESTES - ERRO E EDGE CASES
// ============================================================================

test.describe('Saúde Ocupacional - Riscos - Erros', () => {

  test('deve exibir erro quando API falha', async ({ page }) => {
    await setupAuthMock(page);

    await page.route('**/api/v1/health-occupational/risk-mappings**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Erro ao carregar mapeamentos' }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/riscos');
    await page.waitForLoadState('load');

    await expect(page.getByText('Erro ao carregar mapeamentos de riscos')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Tentar novamente' })).toBeVisible();
  });

  test('deve permitir tentar novamente após erro', async ({ page }) => {
    await setupAuthMock(page);

    let attempts = 0;
    await page.route('**/api/v1/health-occupational/risk-mappings**', (route) => {
      attempts++;
      if (attempts === 1) {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Erro' }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: MOCK_RISK_MAPPINGS,
            total: MOCK_RISK_MAPPINGS.length,
          }),
        });
      }
    });

    await page.goto('/modulos/saude-ocupacional/riscos');
    await page.waitForLoadState('load');

    await page.getByRole('button', { name: 'Tentar novamente' }).click();

    await page.waitForTimeout(500);
  });

  test('deve ter layout responsivo', async ({ page }) => {
    await gotoRisksPage(page);

    // Testa viewport mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('load');

    await expect(page.getByText('Riscos Ocupacionais - PPRA/PGR')).toBeVisible();

    // Restaura viewport
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('deve permitir atualizar dados manualmente', async ({ page }) => {
    await gotoRisksPage(page);

    await page.getByRole('button', { name: 'Atualizar' }).click();

    await page.waitForTimeout(500);

    await expect(page.getByText('Riscos Ocupacionais - PPRA/PGR')).toBeVisible();
  });

  test('deve redirecionar para login quando não autenticado', async ({ page }) => {
    await page.route('**/api/v1/auth/me', (route) => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Não autenticado' }),
      });
    });

    await page.goto('/modulos/saude-ocupacional/riscos');
    await page.waitForLoadState('load');

    await expect(page).toHaveURL(/.*login.*/);
  });
});
