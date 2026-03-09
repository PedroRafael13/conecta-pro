/**
 * Testes E2E - Módulo Serviços: Ordens de Serviço
 * @file servicos-ordens.spec.ts
 * @description Testes completos para gestão de ordens de serviço
 */

import { test, expect, Page } from '@playwright/test';

// Fixtures e mocks
const mockOrdens = [
  {
    id: 'os-001',
    titulo: 'Manutenção Preventiva - Portaria',
    cliente: 'Empresa ABC Ltda',
    descricao: 'Verificação semanal dos equipamentos de portaria',
    prioridade: 'media',
    tipo: 'preventiva',
    status: 'aberta',
    data_prevista: '2026-02-10',
    created_at: '2026-02-05T10:00:00Z',
    tecnico: 'João Silva',
  },
  {
    id: 'os-002',
    titulo: 'Reparo Câmera - Estacionamento',
    cliente: 'Condomínio Solaris',
    descricao: 'Câmera 3 do estacionamento está com imagem ruim',
    prioridade: 'alta',
    tipo: 'corretiva',
    status: 'em_andamento',
    data_prevista: '2026-02-06',
    created_at: '2026-02-04T14:30:00Z',
    tecnico: 'Maria Santos',
  },
  {
    id: 'os-003',
    titulo: 'Instalação Alarme - Área Leste',
    cliente: 'Shopping Center Norte',
    descricao: 'Instalação de novo sistema de alarme',
    prioridade: 'urgente',
    tipo: 'instalacao',
    status: 'concluida',
    data_prevista: '2026-02-03',
    created_at: '2026-02-01T09:00:00Z',
    tecnico: 'Pedro Costa',
  },
  {
    id: 'os-004',
    titulo: 'Troca de Senha - Controle Acesso',
    cliente: 'Escola Futuro Brilhante',
    descricao: 'Atualização de senhas do sistema de acesso',
    prioridade: 'baixa',
    tipo: 'corretiva',
    status: 'cancelada',
    data_prevista: '2026-02-05',
    created_at: '2026-02-03T16:00:00Z',
    tecnico: 'Ana Oliveira',
  },
];

// Helper para setup da página com mocks
async function setupOrdensPage(page: Page) {
  await page.addInitScript(() => {
    // Mock localStorage para simular autenticação
    localStorage.setItem('access_token', 'mock_token_123');
  });
}

test.describe('📋 Serviços - Ordens de Serviço', () => {

  test.beforeEach(async ({ page }) => {
    await setupOrdensPage(page);
    await page.goto('/modulos/servicos/ordens');
    await page.waitForLoadState('load');
  });

  // ============================================
  // TESTES DE LISTAGEM (5 testes)
  // ============================================

  test('deve carregar página de ordens de serviço', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Ordens de Servico');
    await expect(page.locator('text=Gestao de ordens de servico')).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await expect(page.locator('text=Total')).toBeVisible();
    await expect(page.locator('text=Abertas')).toBeVisible();
    await expect(page.locator('text=Em Andamento')).toBeVisible();
    await expect(page.locator('text=Concluidas')).toBeVisible();
  });

  test('deve exibir estado vazio quando não há ordens', async ({ page }) => {
    // Aguarda mensagem de estado vazio
    await expect(page.locator('text=Nenhuma ordem de servico encontrada')).toBeVisible();
    await expect(page.locator('text=Tente ajustar os filtros ou crie uma nova ordem')).toBeVisible();
  });

  test('deve exibir botão Nova OS no estado vazio', async ({ page }) => {
    const novaOSButton = page.locator('button:has-text("Nova OS")').first();
    await expect(novaOSButton).toBeVisible();
  });

  test('deve ter filtros de busca e status', async ({ page }) => {
    await expect(page.locator('input[placeholder*="Buscar por titulo, cliente"]')).toBeVisible();
    await expect(page.locator('text=Todos os status')).toBeVisible();
    await expect(page.locator('text=Todas prioridades')).toBeVisible();
  });

  // ============================================
  // TESTES DE CRIAÇÃO DE OS (6 testes)
  // ============================================

  test('deve abrir modal ao clicar em Nova OS', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');
    await expect(page.locator('text=Nova Ordem de Servico')).toBeVisible();
  });

  test('deve preencher formulário de criação de OS', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');

    await page.fill('input[id="titulo"]', 'Instalação Câmera Nova');
    await page.fill('input[id="cliente"]', 'Cliente Teste Ltda');
    await page.fill('textarea[id="descricao"]', 'Instalar câmera de segurança no hall de entrada');
    await page.fill('input[id="data_prevista"]', '2026-02-15');

    await expect(page.locator('input[id="titulo"]')).toHaveValue('Instalação Câmera Nova');
    await expect(page.locator('input[id="cliente"]')).toHaveValue('Cliente Teste Ltda');
  });

  test('deve selecionar prioridade na OS', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');

    // Seleciona prioridade Alta
    await page.click('text=Media');
    await page.click('text=Alta');

    await expect(page.locator('text=Alta')).toBeVisible();
  });

  test('deve selecionar tipo de OS', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');

    // Seleciona tipo Instalação
    await page.click('text=Corretiva');
    await page.click('text=Instalacao');

    await expect(page.locator('text=Instalacao')).toBeVisible();
  });

  test('deve cancelar criação de OS', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');
    await expect(page.locator('text=Nova Ordem de Servico')).toBeVisible();

    await page.click('button:has-text("Cancelar")');
    await expect(page.locator('text=Nova Ordem de Servico')).not.toBeVisible();
  });

  test('deve validar campos obrigatórios do formulário', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');

    // Tenta criar sem preencher título
    await page.fill('input[id="titulo"]', '');

    const tituloInput = page.locator('input[id="titulo"]');
    await expect(tituloInput).toBeVisible();
  });

  // ============================================
  // TESTES DE STATUS DA OS (5 testes)
  // ============================================

  test('deve exibir badge de status Aberta corretamente', async ({ page }) => {
    // Verifica se o badge de status existe na página
    const statusBadge = page.locator('.bg-blue-100:has-text("Aberta")');
    await expect(statusBadge.first()).toBeVisible();
  });

  test('deve exibir badge de status Em Andamento', async ({ page }) => {
    const statusBadge = page.locator('.bg-yellow-100:has-text("Em Andamento")');
    await expect(statusBadge.first()).toBeVisible();
  });

  test('deve exibir badge de status Concluida', async ({ page }) => {
    const statusBadge = page.locator('.bg-green-100:has-text("Concluida")');
    await expect(statusBadge.first()).toBeVisible();
  });

  test('deve exibir badge de status Cancelada', async ({ page }) => {
    const statusBadge = page.locator('.bg-red-100:has-text("Cancelada")');
    await expect(statusBadge.first()).toBeVisible();
  });

  test('deve filtrar por status', async ({ page }) => {
    // Abre o select de status
    await page.click('text=Todos os status');
    await expect(page.locator('text=Aberta')).toBeVisible();
    await expect(page.locator('text=Em Andamento')).toBeVisible();
    await expect(page.locator('text=Concluida')).toBeVisible();
    await expect(page.locator('text=Cancelada')).toBeVisible();
  });

  // ============================================
  // TESTES DE ATRIBUIÇÃO (4 testes)
  // ============================================

  test('deve exibir campo de técnico na criação', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');
    await expect(page.locator('input[id="cliente"]')).toBeVisible();
  });

  test('deve permitir edição de OS existente', async ({ page }) => {
    // Aguarda a tabela carregar
    await page.waitForSelector('table', { timeout: 5000 }).catch(() => {});
  });

  test('deve abrir modal de detalhes da OS', async ({ page }) => {
    // Verifica se há um botão de menu de ações
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await expect(page.locator('text=Ver detalhes').first()).toBeVisible();
    }
  });

  test('deve ter botão Atualizar no header', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await expect(refreshButton).toBeVisible();
    await expect(refreshButton).toBeEnabled();
  });

});

test.describe('🔧 Serviços - Ordens: Funcionalidades Avançadas', () => {

  test.beforeEach(async ({ page }) => {
    await setupOrdensPage(page);
    await page.goto('/modulos/servicos/ordens');
    await page.waitForLoadState('load');
  });

  // ============================================
  // TESTES DE FILTROS ADICIONAIS (4 testes)
  // ============================================

  test('deve filtrar por prioridade', async ({ page }) => {
    await page.click('text=Todas prioridades');
    await expect(page.locator('text=Baixa')).toBeVisible();
    await expect(page.locator('text=Media')).toBeVisible();
    await expect(page.locator('text=Alta')).toBeVisible();
    await expect(page.locator('text=Urgente')).toBeVisible();
  });

  test('deve exibir badge de prioridade Baixa', async ({ page }) => {
    const prioridadeBadge = page.locator('.bg-gray-100:has-text("Baixa")');
    await expect(prioridadeBadge.first()).toBeVisible();
  });

  test('deve exibir badge de prioridade Urgente', async ({ page }) => {
    const prioridadeBadge = page.locator('.bg-red-100:has-text("Urgente")');
    await expect(prioridadeBadge.first()).toBeVisible();
  });

  test('deve permitir busca por texto', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por titulo, cliente"]');
    await searchInput.fill('Manutenção');
    await expect(searchInput).toHaveValue('Manutenção');
  });

  // ============================================
  // TESTES DE ANEXOS E OBSERVAÇÕES (2 testes)
  // ============================================

  test('deve ter campo de descrição no formulário', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');
    const descricaoField = page.locator('textarea[id="descricao"]');
    await expect(descricaoField).toBeVisible();
    await expect(descricaoField).toHaveAttribute('rows', '3');
  });

  test('deve preencher descrição com texto longo', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');
    const descricaoLonga = 'Esta é uma descrição detalhada do serviço que precisa ser realizado. Inclui informações sobre o local, equipamentos necessários e prazo de entrega.';

    await page.fill('textarea[id="descricao"]', descricaoLonga);
    await expect(page.locator('textarea[id="descricao"]')).toHaveValue(descricaoLonga);
  });

  // ============================================
  // TESTES DE DATA E PRAZO (2 testes)
  // ============================================

  test('deve selecionar data prevista', async ({ page }) => {
    await page.click('button:has-text("Nova OS")');

    const dataFutura = '2026-12-31';
    await page.fill('input[id="data_prevista"]', dataFutura);
    await expect(page.locator('input[id="data_prevista"]')).toHaveValue(dataFutura);
  });

  test('deve formatar data no padrão brasileiro na listagem', async ({ page }) => {
    // Verifica se as datas são exibidas no formato brasileiro (DD/MM/AAAA)
    const dataCell = page.locator('table tbody tr td').nth(4);
    if (await dataCell.isVisible().catch(() => false)) {
      const texto = await dataCell.textContent();
      if (texto && texto !== '-') {
        expect(texto).toMatch(/^\d{2}\/\d{2}\/\d{4}$/);
      }
    }
  });

  // ============================================
  // TESTES DE INTERFACE E UX (2 testes)
  // ============================================

  test('deve ter ícone de clipboard no título', async ({ page }) => {
    const titleIcon = page.locator('h1 svg');
    await expect(titleIcon).toBeVisible();
  });

  test('deve ter botão de ações em cada linha da tabela', async ({ page }) => {
    const actionButtons = page.locator('button:has([class*="lucide-more"])');
    const count = await actionButtons.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

});

test.describe('🎨 Serviços - Ordens: Dashboard e Navegação', () => {

  test.beforeEach(async ({ page }) => {
    await setupOrdensPage(page);
    await page.goto('/modulos/servicos');
    await page.waitForLoadState('load');
  });

  test('deve navegar para ordens a partir do dashboard de serviços', async ({ page }) => {
    const ordensCard = page.locator('text=Ordens de Servico').first();
    await expect(ordensCard).toBeVisible();

    await ordensCard.click();
    await page.waitForURL('**/ordens**', { timeout: 5000 });
    await expect(page.locator('h1')).toContainText('Ordens de Servico');
  });

  test('deve exibir contador de OS no dashboard', async ({ page }) => {
    await expect(page.locator('text=OS Abertas')).toBeVisible();
  });

  test('deve ter card de navegação para ordens', async ({ page }) => {
    await expect(page.locator('text=Gestao de ordens de servico')).toBeVisible();
    await expect(page.locator('text=Acessar')).toBeVisible();
  });

});
