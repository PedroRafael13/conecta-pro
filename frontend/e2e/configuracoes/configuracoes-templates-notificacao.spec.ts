/**
 * Testes E2E - Templates de Notificação
 *
 * Testa o módulo de templates multi-canal para notificações do sistema
 * URL: /modulos/configuracoes/templates-notificacao
 */

import { test, expect } from '../fixtures';

// ==================== MOCKS ====================

const mockTemplates = {
  items: [
    {
      id: 'tpl-001',
      nome: 'Bem-vindo ao Sistema',
      codigo: 'WELCOME_EMAIL',
      descricao: 'Email de boas-vindas enviado após cadastro',
      channel: 'email',
      category: 'system',
      ativo: true,
      version: 3,
      subject: 'Bem-vindo ao Conecta PRO, {{nome}}!',
      body: '<h1>Olá {{nome}}!</h1><p>Bem-vindo ao Conecta PRO.</p>',
      variables: ['nome', 'empresa', 'login_url'],
      created_at: '2024-01-10T10:00:00Z',
      updated_at: '2024-02-05T14:30:00Z',
    },
    {
      id: 'tpl-002',
      nome: 'Recuperação de Senha',
      codigo: 'PASSWORD_RESET',
      descricao: 'Email para redefinição de senha',
      channel: 'email',
      category: 'security',
      ativo: true,
      version: 5,
      subject: 'Recuperação de Senha - Conecta PRO',
      body: '<p>Clique no link para redefinir sua senha: {{reset_link}}</p>',
      variables: ['nome', 'reset_link', 'expiry_hours'],
      created_at: '2024-01-12T10:00:00Z',
      updated_at: '2024-02-10T09:15:00Z',
    },
    {
      id: 'tpl-003',
      nome: 'Nova Ocorrência',
      codigo: 'NEW_OCCURRENCE_PUSH',
      descricao: 'Notificação push para novas ocorrências',
      channel: 'push',
      category: 'operational',
      ativo: true,
      version: 2,
      subject: 'Nova Ocorrência: {{titulo}}',
      body: '{{descricao}}',
      variables: ['titulo', 'descricao', 'posto', 'prioridade'],
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-02-08T11:20:00Z',
    },
    {
      id: 'tpl-004',
      nome: 'Lembrete de Pagamento',
      codigo: 'PAYMENT_REMINDER_SMS',
      descricao: 'SMS de lembrete de pagamento',
      channel: 'sms',
      category: 'financial',
      ativo: false,
      version: 1,
      subject: '',
      body: 'Olá {{nome}}! Seu boleto no valor de {{valor}} vence em {{data_vencimento}}.',
      variables: ['nome', 'valor', 'data_vencimento', 'codigo_barras'],
      created_at: '2024-01-20T10:00:00Z',
      updated_at: '2024-01-20T10:00:00Z',
    },
    {
      id: 'tpl-005',
      nome: 'Alerta de Segurança',
      codigo: 'SECURITY_ALERT',
      descricao: 'Alerta de atividade suspeita na conta',
      channel: 'email',
      category: 'security',
      ativo: true,
      version: 4,
      subject: 'Alerta de Segurança - Conecta PRO',
      body: '<p>Detectamos um login em {{device}} em {{location}}.</p>',
      variables: ['nome', 'device', 'location', 'ip_address', 'datetime'],
      created_at: '2024-01-25T10:00:00Z',
      updated_at: '2024-02-12T16:45:00Z',
    },
    {
      id: 'tpl-006',
      nome: 'Confirmação de Agendamento',
      codigo: 'APPOINTMENT_CONFIRM_WHATSAPP',
      descricao: 'Confirmação de agendamento via WhatsApp',
      channel: 'whatsapp',
      category: 'operational',
      ativo: true,
      version: 2,
      subject: '',
      body: 'Olá {{nome}}! Sua visita está agendada para {{data}} às {{hora}}.',
      variables: ['nome', 'data', 'hora', 'endereco', 'contato'],
      created_at: '2024-02-01T10:00:00Z',
      updated_at: '2024-02-15T13:10:00Z',
    },
    {
      id: 'tpl-007',
      nome: 'Notificação In-App',
      codigo: 'IN_APP_NOTIFICATION',
      descricao: 'Notificação dentro do aplicativo',
      channel: 'in_app',
      category: 'system',
      ativo: true,
      version: 1,
      subject: '{{titulo}}',
      body: '{{mensagem}}',
      variables: ['titulo', 'mensagem', 'acao_url'],
      created_at: '2024-02-10T10:00:00Z',
      updated_at: '2024-02-10T10:00:00Z',
    },
  ],
  total: 7,
};

// ==================== TESTES ====================

test.describe('Templates de Notificação', () => {
  test.beforeEach(async ({ page }) => {
    // Mock endpoint de templates
    await page.route('**/api/v1/config/notification-templates**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockTemplates),
      });
    });

    // Navegar para a página
    await page.goto('/modulos/configuracoes/templates-notificacao', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  // ============ TESTES DE CARREGAMENTO ============

  test('deve carregar a página de templates de notificação', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Templates de Notificacao');
    await expect(page.locator('text=Templates multi-canal para notificacoes do sistema')).toBeVisible();
  });

  test('deve exibir lista de templates ao carregar', async ({ page }) => {
    await expect(page.locator('text=Bem-vindo ao Sistema')).toBeVisible();
    await expect(page.locator('text=Recuperação de Senha')).toBeVisible();
  });

  // ============ TESTES DE ESTATÍSTICAS ============

  test('deve exibir card de total de templates', async ({ page }) => {
    await expect(page.locator('text=Total').first()).toBeVisible();
  });

  test('deve exibir card de templates ativos', async ({ page }) => {
    await expect(page.locator('text=Ativos').first()).toBeVisible();
  });

  test('deve exibir card de templates de Email', async ({ page }) => {
    await expect(page.locator('text=Email').first()).toBeVisible();
  });

  test('deve exibir card de templates Push/SMS', async ({ page }) => {
    await expect(page.locator('text=Push/SMS').first()).toBeVisible();
  });

  test('deve exibir contagem correta de templates por canal', async ({ page }) => {
    // 3 templates de email no mock
    const emailCount = page.locator('div:has-text("Email") + div .text-blue-600');
    await expect(emailCount).toContainText('3');
  });

  // ============ TESTES DE LISTAGEM ============

  test('deve exibir nome e código do template', async ({ page }) => {
    await expect(page.locator('text=Bem-vindo ao Sistema')).toBeVisible();
    await expect(page.locator('text=WELCOME_EMAIL')).toBeVisible();
  });

  test('deve exibir canal do template como badge', async ({ page }) => {
    await expect(page.locator('text=E-mail').first()).toBeVisible();
  });

  test('deve exibir categoria do template', async ({ page }) => {
    await expect(page.locator('text=Sistema').first()).toBeVisible();
    await expect(page.locator('text=Seguranca').first()).toBeVisible();
    await expect(page.locator('text=Operacional').first()).toBeVisible();
  });

  test('deve exibir versão do template', async ({ page }) => {
    await expect(page.locator('text=v3')).toBeVisible();
    await expect(page.locator('text=v5')).toBeVisible();
  });

  test('deve exibir status ativo/inativo do template', async ({ page }) => {
    await expect(page.locator('text=Ativo').first()).toBeVisible();
    await expect(page.locator('text=Inativo').first()).toBeVisible();
  });

  // ============ TESTES DE CANAIS ============

  test('deve exibir badge E-mail para canal email', async ({ page }) => {
    const emailBadges = page.locator('.bg-blue-100:has-text("E-mail")');
    await expect(emailBadges.first()).toBeVisible();
  });

  test('deve exibir badge SMS para canal sms', async ({ page }) => {
    const smsBadges = page.locator('.bg-green-100:has-text("SMS")');
    await expect(smsBadges.first()).toBeVisible();
  });

  test('deve exibir badge Push para canal push', async ({ page }) => {
    const pushBadges = page.locator('.bg-purple-100:has-text("Push")');
    await expect(pushBadges.first()).toBeVisible();
  });

  test('deve exibir badge WhatsApp para canal whatsapp', async ({ page }) => {
    const whatsappBadges = page.locator('.bg-emerald-100:has-text("WhatsApp")');
    await expect(whatsappBadges.first()).toBeVisible();
  });

  test('deve exibir badge In-App para canal in_app', async ({ page }) => {
    const inAppBadges = page.locator('.bg-orange-100:has-text("In-App")');
    await expect(inAppBadges.first()).toBeVisible();
  });

  // ============ TESTES DE FILTROS ============

  test('deve ter campo de busca para templates', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();
    await expect(searchInput).toBeVisible();
  });

  test('deve permitir buscar templates por nome', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();
    await searchInput.fill('Bem-vindo');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Bem-vindo ao Sistema')).toBeVisible();
  });

  test('deve ter filtro por canal', async ({ page }) => {
    const channelFilter = page.locator('button:has-text("Todos canais")');
    await expect(channelFilter).toBeVisible();
  });

  test('deve ter opções de canal no filtro', async ({ page }) => {
    await page.click('button:has-text("Todos canais")');
    await expect(page.locator('text=E-mail').first()).toBeVisible();
    await expect(page.locator('text=SMS')).toBeVisible();
    await expect(page.locator('text=Push')).toBeVisible();
    await expect(page.locator('text=WhatsApp').first()).toBeVisible();
    await expect(page.locator('text=In-App').first()).toBeVisible();
  });

  test('deve filtrar por canal Email', async ({ page }) => {
    await page.click('button:has-text("Todos canais")');
    await page.click('text=E-mail');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Bem-vindo ao Sistema')).toBeVisible();
    await expect(page.locator('text=Recuperação de Senha')).toBeVisible();
  });

  test('deve ter filtro por categoria', async ({ page }) => {
    const categoryFilter = page.locator('button:has-text("Todas")');
    await expect(categoryFilter.first()).toBeVisible();
  });

  test('deve ter opções de categoria no filtro', async ({ page }) => {
    await page.click('button:has-text("Todas"):has(~ button, ~ div)');
    await expect(page.locator('text=Sistema').first()).toBeVisible();
    await expect(page.locator('text=Operacional').first()).toBeVisible();
    await expect(page.locator('text=Financeiro').first()).toBeVisible();
    await expect(page.locator('text=Marketing').first()).toBeVisible();
    await expect(page.locator('text=Seguranca').first()).toBeVisible();
    await expect(page.locator('text=RH')).toBeVisible();
  });

  test('deve ter filtro por status', async ({ page }) => {
    const statusFilter = page.locator('button:has-text("Todos")');
    await expect(statusFilter.first()).toBeVisible();
  });

  test('deve filtrar por status Ativos', async ({ page }) => {
    await page.click('button:has-text("Todos"):has(~ button, ~ div)');
    await page.click('text=Ativos');
    await page.waitForTimeout(500);

    await expect(page.locator('text=Bem-vindo ao Sistema')).toBeVisible();
  });

  // ============ TESTES DE AÇÕES ============

  test('deve exibir botão de novo template', async ({ page }) => {
    await expect(page.locator('button:has-text("Novo Template")')).toBeVisible();
  });

  test('deve exibir botão de atualizar lista', async ({ page }) => {
    await expect(page.locator('button:has-text("Atualizar")').first()).toBeVisible();
  });

  test('deve exibir menu de ações para cada template', async ({ page }) => {
    const actionMenus = page.locator('button:has([data-lucide="more-horizontal"])');
    await expect(actionMenus.first()).toBeVisible();
  });

  test('deve abrir menu de ações ao clicar', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Preview')).toBeVisible();
    await expect(page.locator('text=Editar').first()).toBeVisible();
    await expect(page.locator('text=Clonar')).toBeVisible();
  });

  test('deve ter opção de ativar/desativar no menu', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Desativar, text=Ativar').first()).toBeVisible();
  });

  test('deve ter opção de deletar no menu', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Deletar').first()).toBeVisible();
  });

  // ============ TESTES DE VARIÁVEIS DINÂMICAS ============

  test('deve identificar templates com variáveis dinâmicas', async ({ page }) => {
    // Templates com {{variavel}} são detectados
    const welcomeTemplate = page.locator('div:has-text("Bem-vindo ao Sistema")');
    await expect(welcomeTemplate).toBeVisible();
  });

  // ============ TESTES DE PREVIEW ============

  test('deve ter opção de preview no menu de ações', async ({ page }) => {
    const firstMenu = page.locator('button:has([data-lucide="more-horizontal"])').first();
    await firstMenu.click();

    await expect(page.locator('text=Preview')).toBeVisible();
  });

  // ============ TESTES DE ESTRUTURA DA TABELA ============

  test('deve exibir templates em formato de tabela', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Verifica cabeçalhos
    await expect(page.locator('th:has-text("Nome / Codigo")')).toBeVisible();
    await expect(page.locator('th:has-text("Canal")')).toBeVisible();
    await expect(page.locator('th:has-text("Categoria")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
    await expect(page.locator('th:has-text("Versao")')).toBeVisible();
  });

  // ============ TESTES DE PAGINAÇÃO ============

  test('deve exibir informação de paginação quando necessário', async ({ page }) => {
    const manyTemplates = {
      items: Array(25).fill(null).map((_, i) => ({
        id: `tpl-${i}`,
        nome: `Template ${i}`,
        codigo: `TEMPLATE_${i}`,
        descricao: `Descrição do template ${i}`,
        channel: 'email',
        category: 'system',
        ativo: true,
        version: 1,
        subject: 'Assunto',
        body: 'Corpo',
        variables: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      })),
      total: 25,
    };

    await page.route('**/api/v1/config/notification-templates**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(manyTemplates),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('button:has-text("Proximo")')).toBeVisible();
    await expect(page.locator('button:has-text("Anterior")')).toBeVisible();
  });

  // ============ TESTES DE ESTADO VAZIO ============

  test('deve exibir mensagem quando não houver templates', async ({ page }) => {
    await page.route('**/api/v1/config/notification-templates**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Nenhum template encontrado')).toBeVisible();
    await expect(page.locator('text=Crie um novo template para comecar')).toBeVisible();
  });

  // ============ TESTES DE ERRO ============

  test('deve exibir mensagem de erro quando API falha', async ({ page }) => {
    await page.route('**/api/v1/config/notification-templates**', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await page.reload();
    await page.waitForTimeout(2000);

    await expect(page.locator('text=Erro ao carregar templates')).toBeVisible();
    await expect(page.locator('button:has-text("Tentar novamente")')).toBeVisible();
  });

  // ============ TESTES DE ÍCONES ============

  test('deve exibir ícone de Mail no header', async ({ page }) => {
    const header = page.locator('h1');
    await expect(header.locator('svg')).toBeVisible();
  });

  test('deve exibir ícones nos cards de estatísticas', async ({ page }) => {
    await expect(page.locator('[data-lucide="mail"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="power"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="bell"]').first()).toBeVisible();
  });

  test('deve exibir ícones de canal nos badges', async ({ page }) => {
    await expect(page.locator('[data-lucide="mail"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="message-square"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="bell"]').first()).toBeVisible();
    await expect(page.locator('[data-lucide="smartphone"]').first()).toBeVisible();
  });

  // ============ TESTES DE BADGES DE STATUS ============

  test('deve exibir badge verde para templates ativos', async ({ page }) => {
    const activeBadges = page.locator('.bg-green-100:has-text("Ativo")');
    await expect(activeBadges.first()).toBeVisible();
  });

  test('deve exibir badge cinza para templates inativos', async ({ page }) => {
    const inactiveBadges = page.locator('.bg-gray-100:has-text("Inativo")');
    await expect(inactiveBadges.first()).toBeVisible();
  });
});
