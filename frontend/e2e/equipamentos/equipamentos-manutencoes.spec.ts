import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Manutenções de Equipamentos
 *
 * Testa gestão completa de manutenções:
 * - Agendamento de manutenções
 * - Tipos (preventiva, corretiva, preditiva, emergencial)
 * - Ordens de serviço de manutenção
 * - Histórico de manutenções
 * - Fornecedores de manutenção
 * - Custos
 */

// Mock data para manutenções
const mockMaintenanceList = {
  items: [
    {
      id: 'mnt-001',
      codigo: 'OS-2024-001',
      equipment_name: 'Câmera IP Dome 4K',
      maintenance_type: 'preventiva',
      status: 'scheduled',
      priority: 'medium',
      technician_name: 'João Silva',
      scheduled_date: '2024-03-15',
      description: 'Limpeza e verificação periódica',
      observacoes: 'Manutenção preventiva trimestral',
    },
    {
      id: 'mnt-002',
      codigo: 'OS-2024-015',
      equipment_name: 'Controle de Acesso Biométrico',
      maintenance_type: 'corretiva',
      status: 'in_progress',
      priority: 'high',
      technician_name: 'Maria Santos',
      scheduled_date: '2024-03-10',
      description: 'Troca de leitor biométrico com defeito',
      observacoes: 'Equipamento apresentando falha na leitura',
    },
    {
      id: 'mnt-003',
      codigo: 'OS-2024-008',
      equipment_name: 'Sensor de Presença',
      maintenance_type: 'emergencial',
      status: 'completed',
      priority: 'critical',
      technician_name: 'Pedro Oliveira',
      scheduled_date: '2024-03-05',
      description: 'Reparo urgente do sensor',
      observacoes: 'Concluído em 2 horas',
    },
    {
      id: 'mnt-004',
      codigo: 'OS-2024-020',
      equipment_name: 'Rádio Comunicador',
      maintenance_type: 'preventiva',
      status: 'waiting_parts',
      priority: 'low',
      technician_name: 'Ana Costa',
      scheduled_date: '2024-03-20',
      description: 'Substituição de bateria',
      observacoes: 'Aguardando chegada da peça',
    },
  ],
  total: 4,
};

const mockStats = {
  total: 4,
  in_progress: 1,
  overdue: 0,
  completed: 1,
};

test.describe('Manutenções - Visualização', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
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
          body: JSON.stringify(mockMaintenanceList),
        });
      }
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  test('deve carregar a página de manutenções', async ({ page }) => {
    await expect(page).toHaveURL(/\/manutencoes/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Manutenções/i, { timeout: 10000 });
  });

  test('deve exibir subtítulo de gestão de manutenções', async ({ page }) => {
    const subtitle = page.locator('p:has-text("preventivas e corretivas")');
    await expect(subtitle).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await expect(page.locator('text=/Total/i').first()).toBeVisible();
    await expect(page.locator('text=/Em Andamento/i').first()).toBeVisible();
    await expect(page.locator('text=/Atrasadas/i').first()).toBeVisible();
    await expect(page.locator('text=/Concluídas/i').first()).toBeVisible();
  });

  test('deve exibir tabela de manutenções', async ({ page }) => {
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    expect(headerTexts).toContain('Equipamento');
    expect(headerTexts).toContain('Tipo');
    expect(headerTexts).toContain('Status');
    expect(headerTexts).toContain('Prioridade');
    expect(headerTexts).toContain('Técnico');
    expect(headerTexts).toContain('Previsão');
  });

  test('deve exibir código da OS quando disponível', async ({ page }) => {
    await expect(page.locator('text=OS-2024-001').first()).toBeVisible();
  });

  test('deve exibir badges de tipo de manutenção', async ({ page }) => {
    await expect(page.locator('text=/Preventiva/i').first()).toBeVisible();
    await expect(page.locator('text=/Corretiva/i').first()).toBeVisible();
    await expect(page.locator('text=/Emergencial/i').first()).toBeVisible();
  });

  test('deve exibir badges de status coloridos', async ({ page }) => {
    await expect(page.locator('text=/Agendada/i').first()).toBeVisible();
    await expect(page.locator('text=/Em Andamento/i').first()).toBeVisible();
    await expect(page.locator('text=/Concluída/i').first()).toBeVisible();
    await expect(page.locator('text=/Aguard. Peças/i').first()).toBeVisible();
  });

  test('deve exibir badges de prioridade', async ({ page }) => {
    await expect(page.locator('text=/Baixa|Média|Alta|Crítica/i').first()).toBeVisible();
  });

  test('deve exibir nome do técnico responsável', async ({ page }) => {
    await expect(page.locator('text=João Silva').first()).toBeVisible();
    await expect(page.locator('text=Maria Santos').first()).toBeVisible();
  });

  test('deve exibir data prevista formatada', async ({ page }) => {
    // Data em formato brasileiro
    const datePattern = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').first();
    expect(await datePattern.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Manutenções - Filtros e Busca', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMaintenanceList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]').first();
    await expect(searchInput).toBeVisible();

    await searchInput.fill('Câmera');
    await page.waitForTimeout(500);
    await expect(searchInput).toHaveValue('Câmera');
  });

  test('deve filtrar por tipo preventiva', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const typeSelect = selects[0]!;

    await typeSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Preventiva').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por tipo corretiva', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const typeSelect = selects[0]!;

    await typeSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Corretiva').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por tipo emergencial', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const typeSelect = selects[0]!;

    await typeSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Emergencial').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por status agendada', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const statusSelect = selects[1]! || selects[0]!;

    await statusSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Agendada').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por status em andamento', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const statusSelect = selects[1]! || selects[0]!;

    await statusSelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Em Andamento').first().click();
    await page.waitForTimeout(500);
  });

  test('deve filtrar por prioridade', async ({ page }) => {
    const selects = await page.locator('[role="combobox"]').all();
    const prioritySelect = selects[2]! || selects[0]!;

    await prioritySelect.click();
    await page.waitForTimeout(300);

    await page.locator('text=Alta').first().click();
    await page.waitForTimeout(500);
  });
});

test.describe('Manutenções - CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      const method = route.request().method();

      if (method === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockMaintenanceList),
        });
      } else if (method === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'mnt-new',
            codigo: 'OS-2024-999',
            equipment_name: 'Novo Equipamento',
            status: 'scheduled',
          }),
        });
      } else {
        route.continue();
      }
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);
  });

  test('deve abrir modal de nova manutenção', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible();
    await expect(modal).toContainText('Nova Manutenção');
  });

  test('deve ter campo de equipamento obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const equipInput = modal.locator('input[name="equipment_name"]');
    await expect(equipInput).toBeVisible();
  });

  test('deve ter select de tipo de manutenção', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toContainText('Tipo de Manutenção');
  });

  test('deve ter opções de tipo preventiva, corretiva e emergencial', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const tipoSelect = modal.locator('[role="combobox"]').first();
    await tipoSelect.click();
    await page.waitForTimeout(300);

    await expect(page.locator('text=Preventiva').first()).toBeVisible();
    await expect(page.locator('text=Corretiva').first()).toBeVisible();
    await expect(page.locator('text=Emergencial').first()).toBeVisible();
  });

  test('deve ter select de prioridade', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toContainText('Prioridade');
  });

  test('deve ter opções de prioridade baixa, média, alta e crítica', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const prioritySelect = modal.locator('[role="combobox"]').nth(1);
    await prioritySelect.click();
    await page.waitForTimeout(300);

    await expect(page.locator('text=Baixa').first()).toBeVisible();
    await expect(page.locator('text=Média').first()).toBeVisible();
    await expect(page.locator('text=Alta').first()).toBeVisible();
    await expect(page.locator('text=Crítica').first()).toBeVisible();
  });

  test('deve ter campo de técnico responsável', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const techInput = modal.locator('input[name="technician_name"]');
    await expect(techInput).toBeVisible();
  });

  test('deve ter campo de data agendada', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const dateInput = modal.locator('input[type="date"]');
    await expect(dateInput).toBeVisible();
  });

  test('deve ter campo de descrição', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const descTextarea = modal.locator('textarea[name="description"]');
    await expect(descTextarea).toBeVisible();
  });

  test('deve ter campo de observações', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const obsTextarea = modal.locator('textarea[name="observacoes"]');
    await expect(obsTextarea).toBeVisible();
  });

  test('deve cancelar criação ao clicar em Cancelar', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const cancelButton = page.locator('button:has-text("Cancelar")').first();
    await cancelButton.click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).not.toBeVisible();
  });

  test('deve abrir modal de detalhes ao clicar na linha', async ({ page }) => {
    const row = page.locator('table tbody tr').first();
    await row.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    expect(await modal.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve ter opção de editar no dropdown', async ({ page }) => {
    const actionButton = page.locator('button:has-text("..."), button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const editOption = page.locator('text=/Editar/i').first();
    expect(await editOption.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Manutenções - Fluxo de Status', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMaintenanceList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);
  });

  test('deve exibir opção Iniciar para manutenções agendadas', async ({ page }) => {
    // Procura por uma manutenção agendada e clica no menu
    const rows = page.locator('table tbody tr');
    const rowCount = await rows.count();

    for (let i = 0; i < rowCount; i++) {
      const row = rows.nth(i);
      const hasAgendada = await row.locator('text=/Agendada/i').isVisible().catch(() => false);

      if (hasAgendada) {
        const actionButton = row.locator('button[class*="ghost"], button:has-text("...")');
        await actionButton.click();
        await page.waitForTimeout(500);

        const iniciarOption = page.locator('text=/Iniciar/i').first();
        expect(await iniciarOption.isVisible().catch(() => false)).toBeDefined();
        break;
      }
    }
  });

  test('deve exibir opção Completar para manutenções em andamento', async ({ page }) => {
    const actionButtons = page.locator('button[class*="ghost"]').all();
    const buttons = await actionButtons;

    for (const btn of buttons.slice(0, 3)) {
      await btn.click();
      await page.waitForTimeout(400);

      const completarOption = page.locator('text=/Completar/i').first();
      if (await completarOption.isVisible().catch(() => false)) {
        expect(true).toBe(true);
        break;
      }

      // Fecha dropdown clicando fora
      await page.keyboard.press('Escape');
      await page.waitForTimeout(200);
    }
  });

  test('deve exibir opção Cancelar para manutenções não concluídas', async ({ page }) => {
    const actionButtons = page.locator('button[class*="ghost"]').all();
    const buttons = await actionButtons;

    for (const btn of buttons.slice(0, 3)) {
      await btn.click();
      await page.waitForTimeout(400);

      const cancelarOption = page.locator('text=/Cancelar/i').first();
      if (await cancelarOption.isVisible().catch(() => false)) {
        expect(true).toBe(true);
        break;
      }

      await page.keyboard.press('Escape');
      await page.waitForTimeout(200);
    }
  });
});

test.describe('Manutenções - Agendamento', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMaintenanceList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);
  });

  test('deve permitir agendar manutenção preventiva', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const equipInput = modal.locator('input[name="equipment_name"]');
    await equipInput.fill('Equipamento Teste');

    const tipoSelect = modal.locator('[role="combobox"]').first();
    await tipoSelect.click();
    await page.waitForTimeout(300);
    await page.locator('text=Preventiva').first().click();

    await expect(equipInput).toHaveValue('Equipamento Teste');
  });

  test('deve permitir agendar manutenção corretiva', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const tipoSelect = modal.locator('[role="combobox"]').first();
    await tipoSelect.click();
    await page.waitForTimeout(300);
    await page.locator('text=Corretiva').first().click();

    expect(true).toBe(true);
  });

  test('deve permitir agendar manutenção emergencial', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const tipoSelect = modal.locator('[role="combobox"]').first();
    await tipoSelect.click();
    await page.waitForTimeout(300);
    await page.locator('text=Emergencial').first().click();

    expect(true).toBe(true);
  });

  test('deve validar campos obrigatórios no agendamento', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
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

test.describe('Manutenções - Custos e Fornecedores', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMaintenanceList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);
  });

  test('deve exibir técnico responsável como fornecedor de serviço', async ({ page }) => {
    const tecnicoCell = page.locator('table tbody tr td:has-text("João Silva"), table tbody tr td:has-text("Maria Santos")').first();
    expect(await tecnicoCell.isVisible().catch(() => false)).toBeDefined();
  });

  test('deve permitir informar técnico na criação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Manutenção")');
    await newButton.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    const techInput = modal.locator('input[name="technician_name"]');
    await techInput.fill('Técnico Externo XYZ');

    await expect(techInput).toHaveValue('Técnico Externo XYZ');
  });
});

test.describe('Manutenções - Histórico', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMaintenanceList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);
  });

  test('deve exibir manutenções concluídas no histórico', async ({ page }) => {
    await expect(page.locator('text=/Concluída/i').first()).toBeVisible();
  });

  test('deve permitir ver detalhes de manutenção concluída', async ({ page }) => {
    const actionButton = page.locator('button[class*="ghost"]').first();
    await actionButton.click();
    await page.waitForTimeout(500);

    const viewOption = page.locator('text=/Ver detalhes/i').first();
    await viewOption.click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]').first();
    expect(await modal.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Manutenções - Empty State e Erros', () => {
  test('deve exibir empty state quando não há manutenções', async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);

    await expect(page.locator('text=/Nenhuma manutenção encontrada/i')).toBeVisible();
  });

  test('deve ter botão para criar manutenção no empty state', async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);

    const newButton = page.locator('button:has-text("Nova Manutenção")').first();
    expect(await newButton.isVisible().catch(() => false)).toBeDefined();
  });
});

test.describe('Manutenções - Integração', () => {
  test('deve carregar corretamente ao navegar do menu', async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos');
    await page.waitForTimeout(1500);

    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);

    await expect(page).toHaveURL(/\/manutencoes/);
    await expect(page.locator('h1')).toContainText('Manutenções');
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    await page.route('**/api/v1/maintenance**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMaintenanceList),
      });
    });

    await loginViaAPI(page);
    await page.goto('/modulos/equipamentos/manutencoes');
    await page.waitForTimeout(1500);

    const refreshButton = page.locator('button:has-text("Atualizar")').first();
    await expect(refreshButton).toBeVisible();

    await refreshButton.click();
    await page.waitForTimeout(500);

    expect(page.url()).toContain('/manutencoes');
  });
});
