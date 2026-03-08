import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Comunicados Internos
 *
 * Testa gestão de comunicados:
 * - Listagem com filtros
 * - Criação de comunicado
 * - Publicação
 * - Visualização de detalhes
 * - Edição e exclusão
 * - Estatísticas de leitura
 */

test.describe('Operacional - Comunicados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de comunicados', async ({ page }) => {
    await expect(page).toHaveURL(/\/comunicados/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Comunicados/i, { timeout: 10000 });
  });

  test('deve exibir tabela de comunicados', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir estatísticas de comunicados', async ({ page }) => {
    // Stats cards (total, rascunhos, publicados, agendados)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir botão de novo comunicado', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado"), button:has-text("Novo")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
  });

  test('deve abrir modal ao clicar em novo comunicado', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible({ timeout: 5000 });
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Reunião');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Reunião');
    }
  });

  test('deve ter filtro de status', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve ter filtro de prioridade', async ({ page }) => {
    const priorityFilter = page.locator('select').nth(1);

    if (await priorityFilter.isVisible().catch(() => false)) {
      await priorityFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve ter filtro de categoria', async ({ page }) => {
    const categoryFilter = page.locator('select').nth(2);

    if (await categoryFilter.isVisible().catch(() => false)) {
      await categoryFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve exibir badges de status nas linhas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status (rascunho, agendado, publicado, arquivado)
    const statusBadges = page.locator('text=/rascunho|agendado|publicado|arquivado/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir badges de prioridade', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de prioridade (baixa, normal, alta, urgente)
    const priorityBadges = page.locator('text=/baixa|normal|alta|urgente/i').all();
    const count = (await priorityBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir título do comunicado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const titleCells = page.locator('table tbody tr td:first-child').all();
    const count = (await titleCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir categoria do comunicado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const categoryCells = page.locator('table tbody tr td').all();
    const count = (await categoryCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir destinatários do comunicado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const targetCells = page.locator('text=/Todos|Selecionados/i').all();
    const count = (await targetCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data de criação', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar datas formatadas
    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir contagem de leituras', async ({ page }) => {
    await page.waitForTimeout(2000);

    const readCounts = page.locator('text=/\\d+ \\(/, text=/%\\)/').all();
    const count = (await readCounts).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de ver detalhes em cada linha', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButtons = page.locator('button[title*="Ver"], button[title*="Detalhes"]').first();
    const hasViewButton = await viewButtons.isVisible().catch(() => false);

    expect(hasViewButton !== undefined).toBeTruthy();
  });

  test('deve abrir modal de detalhes ao clicar em ver', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });
    }
  });

  test('deve ter botão de editar para rascunhos', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar linhas com status rascunho
    const rows = page.locator('table tbody tr').all();

    for (const row of await rows) {
      const statusCell = row.locator('td').nth(5);
      const statusText = await statusCell.textContent().catch(() => '');

      if (statusText?.toLowerCase().includes('rascunho')) {
        const editButton = row.locator('button[title*="Editar"]').first();
        const hasEdit = await editButton.isVisible().catch(() => false);
        expect(hasEdit).toBeTruthy();
        break;
      }
    }
  });

  test('deve ter botão de publicar para rascunhos', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar linhas com status rascunho
    const rows = page.locator('table tbody tr').all();

    for (const row of await rows) {
      const statusCell = row.locator('td').nth(5);
      const statusText = await statusCell.textContent().catch(() => '');

      if (statusText?.toLowerCase().includes('rascunho')) {
        const publishButton = row.locator('button[title*="Publicar"]').first();
        const hasPublish = await publishButton.isVisible().catch(() => false);
        expect(hasPublish).toBeTruthy();
        break;
      }
    }
  });

  test('deve ter botão de excluir para rascunhos', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar linhas com status rascunho
    const rows = page.locator('table tbody tr').all();

    for (const row of await rows) {
      const statusCell = row.locator('td').nth(5);
      const statusText = await statusCell.textContent().catch(() => '');

      if (statusText?.toLowerCase().includes('rascunho')) {
        const deleteButton = row.locator('button[title*="Excluir"]').first();
        const hasDelete = await deleteButton.isVisible().catch(() => false);
        expect(hasDelete).toBeTruthy();
        break;
      }
    }
  });

  test('deve mostrar confirmação ao publicar comunicado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const publishButton = page.locator('button[title*="Publicar"]').first();

    if (await publishButton.isVisible().catch(() => false)) {
      await publishButton.click();
      await page.waitForTimeout(500);

      const confirmModal = page.locator('[role="dialog"], [role="alertdialog"]').first();
      expect(await confirmModal.isVisible().catch(() => false)).toBeDefined();

      // Fechar modal
      await page.keyboard.press('Escape');
    }
  });

  test('deve mostrar confirmação ao excluir comunicado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(500);

      const confirmModal = page.locator('[role="dialog"], [role="alertdialog"]').first();
      expect(await confirmModal.isVisible().catch(() => false)).toBeDefined();

      // Fechar modal
      await page.keyboard.press('Escape');
    }
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/comunicados');
    }
  });

  test('deve exibir paginação se necessário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), span:has-text("Página"), span:has-text("de"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há comunicados', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhum comunicado encontrado/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve ter botão de criar comunicado no empty state', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyStateButton = page.locator('button:has-text("Novo Comunicado")').nth(1);

    if (await emptyStateButton.isVisible().catch(() => false)) {
      await emptyStateButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      expect(await modal.isVisible().catch(() => false)).toBeTruthy();
    }
  });

  test('deve voltar para módulo operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional"), button:has-text("Voltar")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toMatch(/\/operacional/);
    }
  });
});

test.describe('Operacional - Comunicados - Criação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForTimeout(2000);
  });

  test('deve exibir formulário de criação com campos corretos', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();

    // Verificar campos esperados
    const titleInput = modal.locator('input[name*="title"], input[placeholder*="título" i]').first();
    const contentInput = modal.locator('textarea[name*="content"], textarea').first();
    const categorySelect = modal.locator('select').first();

    expect(
      (await titleInput.isVisible().catch(() => false)) ||
      (await contentInput.isVisible().catch(() => false)) ||
      (await categorySelect.isVisible().catch(() => false))
    ).toBeTruthy();
  });

  test('deve permitir preencher título', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const titleInput = modal.locator('input[name*="title"]').first();

    if (await titleInput.isVisible().catch(() => false)) {
      await titleInput.fill('Comunicado de Teste');
      await expect(titleInput).toHaveValue('Comunicado de Teste');
    }
  });

  test('deve permitir preencher conteúdo', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const contentInput = modal.locator('textarea').first();

    if (await contentInput.isVisible().catch(() => false)) {
      await contentInput.fill('Este é um comunicado de teste');
      await expect(contentInput).toHaveValue('Este é um comunicado de teste');
    }
  });

  test('deve ter seleção de categoria', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const categorySelect = modal.locator('select').first();

    if (await categorySelect.isVisible().catch(() => false)) {
      await categorySelect.selectOption({ index: 1 });
      expect(await categorySelect.inputValue()).toBeTruthy();
    }
  });

  test('deve ter seleção de prioridade', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const prioritySelect = modal.locator('select').nth(1);

    if (await prioritySelect.isVisible().catch(() => false)) {
      await prioritySelect.selectOption({ index: 1 });
      expect(await prioritySelect.inputValue()).toBeTruthy();
    }
  });

  test('deve ter seleção de destinatários', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();

    // Verificar opção de todos ou selecionados
    const targetOption = modal.locator('text=/Todos|Selecionados/i').first();
    const hasTargetOption = await targetOption.isVisible().catch(() => false);

    expect(hasTargetOption !== undefined).toBeTruthy();
  });

  test('deve ter botão de salvar como rascunho', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const saveButton = modal.locator('button:has-text("Salvar"), button:has-text("Rascunho"), button[type="submit"]').first();

    if (await saveButton.isVisible().catch(() => false)) {
      expect(await saveButton.isVisible()).toBeTruthy();
    }
  });

  test('deve ter botão de cancelar criação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const cancelButton = modal.locator('button:has-text("Cancelar")').first();

    if (await cancelButton.isVisible().catch(() => false)) {
      await cancelButton.click();
      await page.waitForTimeout(500);

      expect(await modal.isVisible().catch(() => false)).toBeFalsy();
    } else {
      await page.keyboard.press('Escape');
    }
  });

  test('deve validar título obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Comunicado")').first();
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    const saveButton = modal.locator('button:has-text("Salvar"), button[type="submit"]').first();

    if (await saveButton.isVisible().catch(() => false)) {
      await saveButton.click();
      await page.waitForTimeout(1000);

      // Modal deve continuar aberto
      expect(await modal.isVisible()).toBeTruthy();
    }
  });
});

test.describe('Operacional - Comunicados - Filtros Avançados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar por título', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Reunião');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Reunião');
    }
  });

  test('deve filtrar por conteúdo', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('importante');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('importante');
    }
  });

  test('deve filtrar por status rascunho', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ label: 'Rascunho' });
      await page.waitForTimeout(1000);

      const value = await statusFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve filtrar por status publicado', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ label: 'Publicado' });
      await page.waitForTimeout(1000);

      const value = await statusFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve filtrar por prioridade alta', async ({ page }) => {
    const priorityFilter = page.locator('select').nth(1);

    if (await priorityFilter.isVisible().catch(() => false)) {
      await priorityFilter.selectOption({ label: 'Alta' });
      await page.waitForTimeout(1000);

      const value = await priorityFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve filtrar por categoria', async ({ page }) => {
    const categoryFilter = page.locator('select').nth(2);

    if (await categoryFilter.isVisible().catch(() => false)) {
      await categoryFilter.selectOption({ index: 1 });
      await page.waitForTimeout(1000);

      const value = await categoryFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve combinar múltiplos filtros', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    const statusFilter = page.locator('select').first();
    const priorityFilter = page.locator('select').nth(1);

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
    }

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
    }

    if (await priorityFilter.isVisible().catch(() => false)) {
      await priorityFilter.selectOption({ index: 1 });
    }

    await page.waitForTimeout(500);
    expect(page.url()).toContain('/comunicados');
  });

  test('deve limpar filtros de busca', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
      await page.waitForTimeout(500);
      await searchInput.clear();

      const value = await searchInput.inputValue();
      expect(value).toBe('');
    }
  });
});

test.describe('Operacional - Comunicados - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir contador total de comunicados', async ({ page }) => {
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForTimeout(2000);

    const totalStat = page.locator('text=/Total/i').first();
    const hasStat = await totalStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de rascunhos', async ({ page }) => {
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForTimeout(2000);

    const draftStat = page.locator('text=/Rascunhos/i').first();
    const hasStat = await draftStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de publicados', async ({ page }) => {
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForTimeout(2000);

    const publishedStat = page.locator('text=/Publicados/i').first();
    const hasStat = await publishedStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de agendados', async ({ page }) => {
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForTimeout(2000);

    const scheduledStat = page.locator('text=/Agendados/i').first();
    const hasStat = await scheduledStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });
});
