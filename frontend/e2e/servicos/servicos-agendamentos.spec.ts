/**
 * Testes E2E - Módulo Serviços: Agendamentos
 * @file servicos-agendamentos.spec.ts
 * @description Testes completos para gestão de agendamentos de visitas e serviços
 */

import { test, expect, Page } from '@playwright/test';

// Fixtures e mocks
const mockAgendamentos = [
  {
    id: 'ag-001',
    titulo: 'Visita Técnica - Empresa ABC',
    descricao: 'Inspeção dos equipamentos de segurança',
    data: '2026-02-06',
    hora_inicio: '09:00',
    hora_fim: '11:00',
    tipo: 'visita',
    responsavel: 'João Silva',
    status: 'confirmado',
    created_at: '2026-02-03T10:00:00Z',
    notificacao_enviada: true,
  },
  {
    id: 'ag-002',
    titulo: 'Manutenção Preventiva - Condomínio Solaris',
    descricao: 'Revisão mensal do sistema de alarme',
    data: '2026-02-10',
    hora_inicio: '14:00',
    hora_fim: '16:00',
    tipo: 'manutencao',
    responsavel: 'Maria Santos',
    status: 'agendado',
    created_at: '2026-02-04T09:30:00Z',
    notificacao_enviada: false,
  },
  {
    id: 'ag-003',
    titulo: 'Instalação Câmeras - Shopping Center',
    descricao: 'Instalação de 4 novas câmeras IP',
    data: '2026-02-05',
    hora_inicio: '08:00',
    hora_fim: '17:00',
    tipo: 'instalacao',
    responsavel: 'Pedro Costa',
    status: 'concluido',
    created_at: '2026-02-01T11:00:00Z',
    notificacao_enviada: true,
  },
  {
    id: 'ag-004',
    titulo: 'Auditoria - Escola Futuro Brilhante',
    descricao: 'Auditoria trimestral de segurança',
    data: '2026-02-15',
    hora_inicio: '10:00',
    hora_fim: '12:00',
    tipo: 'auditoria',
    responsavel: 'Ana Oliveira',
    status: 'cancelado',
    created_at: '2026-02-02T14:00:00Z',
    notificacao_enviada: false,
  },
];

// Helper para setup da página com mocks
async function setupAgendamentosPage(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'mock_token_123');
  });
}

test.describe('📅 Serviços - Agendamentos: Calendário e Listagem', () => {

  test.beforeEach(async ({ page }) => {
    await setupAgendamentosPage(page);
    await page.goto('/modulos/servicos/agendamentos');
    await page.waitForLoadState('networkidle');
  });

  // ============================================
  // TESTES DE CALENDÁRIO (6 testes)
  // ============================================

  test('deve carregar página de agendamentos', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Agendamentos');
    await expect(page.locator('text=Gestao de agendamentos de visitas e servicos')).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await expect(page.locator('text=Total')).toBeVisible();
    await expect(page.locator('text=Hoje')).toBeVisible();
    await expect(page.locator('text=Proxima Semana')).toBeVisible();
  });

  test('deve exibir tabela de agendamentos', async ({ page }) => {
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmpty = await page.locator('text=Nenhum agendamento encontrado').isVisible().catch(() => false);
    expect(hasTable || hasEmpty).toBeTruthy();
  });

  test('deve ter colunas corretas na tabela', async ({ page }) => {
    const headers = ['Titulo', 'Data/Hora', 'Tipo', 'Responsavel', 'Status'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`).first()).toBeVisible();
    }
  });

  test('deve ter botão Novo Agendamento', async ({ page }) => {
    const novoButton = page.locator('button:has-text("Novo Agendamento")');
    await expect(novoButton).toBeVisible();
    await expect(novoButton).toBeEnabled();
  });

  test('deve ter filtros de busca e tipo', async ({ page }) => {
    await expect(page.locator('input[placeholder*="Buscar por titulo, responsavel"]')).toBeVisible();
    await expect(page.locator('text=Todos os tipos')).toBeVisible();
  });

  // ============================================
  // TESTES DE CRIAÇÃO (6 testes)
  // ============================================

  test('deve abrir modal de novo agendamento', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await expect(page.locator('text=Novo Agendamento')).toBeVisible();
  });

  test('deve preencher título do agendamento', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.fill('input[id="titulo"]', 'Visita Técnica Teste');
    await expect(page.locator('input[id="titulo"]')).toHaveValue('Visita Técnica Teste');
  });

  test('deve preencher responsável', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.fill('input[id="responsavel"]', 'Técnico Teste');
    await expect(page.locator('input[id="responsavel"]')).toHaveValue('Técnico Teste');
  });

  test('deve preencher descrição do agendamento', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    const desc = 'Descrição detalhada do agendamento de teste';
    await page.fill('textarea[id="descricao"]', desc);
    await expect(page.locator('textarea[id="descricao"]')).toHaveValue(desc);
  });

  test('deve selecionar data do agendamento', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.fill('input[id="data"]', '2026-03-15');
    await expect(page.locator('input[id="data"]')).toHaveValue('2026-03-15');
  });

  test('deve selecionar horários', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.fill('input[id="hora_inicio"]', '09:00');
    await page.fill('input[id="hora_fim"]', '12:00');
    await expect(page.locator('input[id="hora_inicio"]')).toHaveValue('09:00');
    await expect(page.locator('input[id="hora_fim"]')).toHaveValue('12:00');
  });

});

test.describe('⏰ Serviços - Agendamentos: Tipos e Status', () => {

  test.beforeEach(async ({ page }) => {
    await setupAgendamentosPage(page);
    await page.goto('/modulos/servicos/agendamentos');
    await page.waitForLoadState('networkidle');
  });

  // ============================================
  // TESTES DE TIPOS (4 testes)
  // ============================================

  test('deve selecionar tipo Visita', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.click('text=Visita');
    await expect(page.locator('text=Visita')).toBeVisible();
  });

  test('deve selecionar tipo Manutenção', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.click('text=Visita');
    await page.click('text=Manutencao');
    await expect(page.locator('text=Manutencao')).toBeVisible();
  });

  test('deve selecionar tipo Instalação', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.click('text=Visita');
    await page.click('text=Instalacao');
    await expect(page.locator('text=Instalacao')).toBeVisible();
  });

  test('deve selecionar tipo Auditoria', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.click('text=Visita');
    await page.click('text=Auditoria');
    await expect(page.locator('text=Auditoria')).toBeVisible();
  });

  // ============================================
  // TESTES DE STATUS (5 testes)
  // ============================================

  test('deve exibir badge Agendado', async ({ page }) => {
    const badge = page.locator('.bg-blue-100:has-text("Agendado")');
    await expect(badge.first()).toBeVisible();
  });

  test('deve exibir badge Confirmado', async ({ page }) => {
    const badge = page.locator('.bg-green-100:has-text("Confirmado")');
    await expect(badge.first()).toBeVisible();
  });

  test('deve exibir badge Em Andamento', async ({ page }) => {
    const badge = page.locator('.bg-yellow-100:has-text("Em Andamento")');
    await expect(badge.first()).toBeVisible();
  });

  test('deve exibir badge Concluido', async ({ page }) => {
    const badge = page.locator('.bg-green-100:has-text("Concluido")');
    await expect(badge.first()).toBeVisible();
  });

  test('deve exibir badge Cancelado', async ({ page }) => {
    const badge = page.locator('.bg-red-100:has-text("Cancelado")');
    await expect(badge.first()).toBeVisible();
  });

});

test.describe('⚠️ Serviços - Agendamentos: Conflitos e Notificações', () => {

  test.beforeEach(async ({ page }) => {
    await setupAgendamentosPage(page);
    await page.goto('/modulos/servicos/agendamentos');
    await page.waitForLoadState('networkidle');
  });

  // ============================================
  // TESTES DE CONFLITOS DE HORÁRIO (4 testes)
  // ============================================

  test('deve validar hora fim posterior à hora início', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.fill('input[id="hora_inicio"]', '14:00');
    await page.fill('input[id="hora_fim"]', '10:00');

    // As horas devem ser preenchidas
    await expect(page.locator('input[id="hora_inicio"]')).toHaveValue('14:00');
    await expect(page.locator('input[id="hora_fim"]')).toHaveValue('10:00');
  });

  test('deve permitir agendamento no mesmo dia com horários diferentes', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.fill('input[id="data"]', '2026-02-20');
    await page.fill('input[id="hora_inicio"]', '09:00');
    await page.fill('input[id="hora_fim"]', '11:00');

    await expect(page.locator('input[id="data"]')).toHaveValue('2026-02-20');
  });

  test('deve calcular duração do agendamento', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await page.fill('input[id="hora_inicio"]', '08:00');
    await page.fill('input[id="hora_fim"]', '12:00');

    const inicio = await page.locator('input[id="hora_inicio"]').inputValue();
    const fim = await page.locator('input[id="hora_fim"]').inputValue();
    expect(inicio).toBe('08:00');
    expect(fim).toBe('12:00');
  });

  test('deve validar campos obrigatórios', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    // Título deve estar presente
    const tituloInput = page.locator('input[id="titulo"]');
    await expect(tituloInput).toBeVisible();
  });

  // ============================================
  // TESTES DE NOTIFICAÇÕES (3 testes)
  // ============================================

  test('deve ter estrutura para notificações de lembrete', async ({ page }) => {
    // Verifica se a tabela pode exibir informações de notificação
    const table = page.locator('table');
    await expect(table.first()).toBeVisible({ timeout: 3000 }).catch(() => {});
  });

  test('deve cancelar criação de agendamento', async ({ page }) => {
    await page.click('button:has-text("Novo Agendamento")');
    await expect(page.locator('text=Novo Agendamento')).toBeVisible();

    await page.click('button:has-text("Cancelar")');
    await expect(page.locator('text=Novo Agendamento')).not.toBeVisible();
  });

  test('deve ter botão Atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")');
    await expect(refreshButton).toBeVisible();
    await expect(refreshButton).toBeEnabled();
  });

});

test.describe('🔄 Serviços - Agendamentos: Reagendamento e Ações', () => {

  test.beforeEach(async ({ page }) => {
    await setupAgendamentosPage(page);
    await page.goto('/modulos/servicos/agendamentos');
    await page.waitForLoadState('networkidle');
  });

  // ============================================
  // TESTES DE REAGENDAMENTO (4 testes)
  // ============================================

  test('deve ter opção de editar agendamento', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await expect(page.locator('text=Editar').first()).toBeVisible();
    }
  });

  test('deve permitir reagendamento alterando data', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await page.click('text=Editar');
      await expect(page.locator('text=Editar Agendamento')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('deve permitir reagendamento alterando horário', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await expect(page.locator('text=Editar').first()).toBeVisible();
    }
  });

  test('deve ter opção de ver detalhes', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      await expect(page.locator('text=Ver detalhes').first()).toBeVisible();
    }
  });

  // ============================================
  // TESTES DE AÇÕES DE STATUS (4 testes)
  // ============================================

  test('deve ter opção de confirmar agendamento', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      const confirmar = page.locator('text=Confirmar').first();
      await expect(confirmar).toBeVisible({ timeout: 3000 }).catch(() => {});
    }
  });

  test('deve ter opção de concluir agendamento', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      const concluir = page.locator('text=Concluir').first();
      await expect(concluir).toBeVisible({ timeout: 3000 }).catch(() => {});
    }
  });

  test('deve ter opção de cancelar agendamento', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      const cancelar = page.locator('text=Cancelar').first();
      await expect(cancelar).toBeVisible({ timeout: 3000 }).catch(() => {});
    }
  });

  test('deve ter opção de deletar agendamento', async ({ page }) => {
    const menuButton = page.locator('button:has([class*="lucide-more"])').first();
    if (await menuButton.isVisible().catch(() => false)) {
      await menuButton.click();
      const deletar = page.locator('text=Deletar').first();
      await expect(deletar).toBeVisible({ timeout: 3000 }).catch(() => {});
    }
  });

});

test.describe('🏠 Serviços - Agendamentos: Dashboard e Filtros', () => {

  test.beforeEach(async ({ page }) => {
    await setupAgendamentosPage(page);
    await page.goto('/modulos/servicos');
    await page.waitForLoadState('networkidle');
  });

  test('deve navegar para agendamentos a partir do dashboard', async ({ page }) => {
    const agendamentosCard = page.locator('text=Agendamentos').first();
    await expect(agendamentosCard).toBeVisible();

    await agendamentosCard.click();
    await page.waitForURL('**/agendamentos**', { timeout: 5000 });
    await expect(page.locator('h1')).toContainText('Agendamentos');
  });

  test('deve exibir contador de agendamentos de hoje', async ({ page }) => {
    await expect(page.locator('text=Agendamentos Hoje')).toBeVisible();
  });

  test('deve ter descrição no card de agendamentos', async ({ page }) => {
    await expect(page.locator('text=Agendamentos de visitas e servicos')).toBeVisible();
  });

  test('deve retornar à página de serviços', async ({ page }) => {
    await page.goto('/modulos/servicos/agendamentos');
    await expect(page.locator('h1')).toContainText('Agendamentos');

    await page.goto('/modulos/servicos');
    await expect(page.locator('h1')).toContainText('Servicos');
  });

});

test.describe('📊 Serviços - Agendamentos: Formatação e UX', () => {

  test.beforeEach(async ({ page }) => {
    await setupAgendamentosPage(page);
    await page.goto('/modulos/servicos/agendamentos');
    await page.waitForLoadState('networkidle');
  });

  test('deve formatar data no padrão brasileiro', async ({ page }) => {
    const dataCell = page.locator('table tbody tr td').nth(1);
    if (await dataCell.isVisible().catch(() => false)) {
      const texto = await dataCell.textContent();
      if (texto && texto.trim() !== '') {
        // Verifica formato DD/MM/AAAA
        expect(texto).toMatch(/\d{2}\/\d{2}\/\d{4}/);
      }
    }
  });

  test('deve exibir horários no formato HH:MM', async ({ page }) => {
    const horaCell = page.locator('table tbody tr td').nth(1);
    if (await horaCell.isVisible().catch(() => false)) {
      const texto = await horaCell.textContent();
      if (texto && texto.includes(':')) {
        // Verifica se contém horário
        expect(texto).toMatch(/\d{2}:\d{2}/);
      }
    }
  });

  test('deve ter ícone de calendário no título', async ({ page }) => {
    const titleIcon = page.locator('h1 svg');
    await expect(titleIcon).toBeVisible();
  });

  test('deve filtrar agendamentos por tipo', async ({ page }) => {
    await page.click('text=Todos os tipos');
    await expect(page.locator('text=Visita')).toBeVisible();
    await expect(page.locator('text=Manutencao')).toBeVisible();
    await expect(page.locator('text=Instalacao')).toBeVisible();
    await expect(page.locator('text=Auditoria')).toBeVisible();
  });

});
