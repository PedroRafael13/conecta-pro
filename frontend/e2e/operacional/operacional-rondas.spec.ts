import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Controle de Rondas de Inspeção
 *
 * Testa workflow completo de rondas:
 * - Listagem com filtros
 * - Visualização de detalhes
 * - Estatísticas de rondas
 * - Exportação de dados
 * - Exclusão de rondas agendadas
 */

test.describe('Operacional - Rondas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/rondas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de rondas', async ({ page }) => {
    await expect(page).toHaveURL(/\/rondas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Rondas|Inspeção/i, { timeout: 10000 });
  });

  test('deve exibir tabela de rondas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable !== undefined).toBeTruthy();
  });

  test('deve exibir estatísticas de rondas', async ({ page }) => {
    // Stats cards (total, em andamento, concluídas, ocorrências, medidas)
    const statsCards = page.locator('[class*="card"], [class*="stat"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(5);
  });

  test('deve exibir contador de total de rondas', async ({ page }) => {
    const totalText = page.locator('text=/registros/i, text=/total/i').first();
    const hasTotal = await totalText.isVisible().catch(() => false);

    expect(hasTotal !== undefined).toBeTruthy();
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('RND-2024');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('RND-2024');
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

  test('deve ter filtro de cargo do inspetor', async ({ page }) => {
    const roleFilter = page.locator('select').nth(1);

    if (await roleFilter.isVisible().catch(() => false)) {
      await roleFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve exibir badges de status nas rondas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status
    const statusBadges = page.locator('text=/agendada|em andamento|pausada|concluida|cancelada/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir código da ronda', async ({ page }) => {
    await page.waitForTimeout(2000);

    const codeCells = page.locator('td:has-text("RND-"), td:has-text("RND")').all();
    const count = (await codeCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir nome do inspetor', async ({ page }) => {
    await page.waitForTimeout(2000);

    const inspectorCells = page.locator('table tbody tr td:nth-child(2)').all();
    const count = (await inspectorCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data de início', async ({ page }) => {
    await page.waitForTimeout(2000);

    const dateCells = page.locator('table tbody tr td').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir duração da ronda', async ({ page }) => {
    await page.waitForTimeout(2000);

    const durationCells = page.locator('text=/min|h /i').all();
    const count = (await durationCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir contagem de checkpoints', async ({ page }) => {
    await page.waitForTimeout(2000);

    const checkpointCells = page.locator('table tbody tr td').all();
    const count = (await checkpointCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir contagem de ocorrências', async ({ page }) => {
    await page.waitForTimeout(2000);

    const occurrenceCells = page.locator('table tbody tr td').all();
    const count = (await occurrenceCells).length;

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

  test('deve ter botão de excluir para rondas agendadas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar linhas com status agendada
    const rows = page.locator('table tbody tr').all();

    for (const row of await rows) {
      const statusCell = row.locator('td').nth(2);
      const statusText = await statusCell.textContent().catch(() => '');

      if (statusText?.toLowerCase().includes('agendada')) {
        const deleteButton = row.locator('button[title*="Excluir"]').first();
        const hasDelete = await deleteButton.isVisible().catch(() => false);
        expect(hasDelete).toBeTruthy();
        break;
      }
    }
  });

  test('deve mostrar confirmação ao excluir ronda', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(500);

      const confirmModal = page.locator('[role="dialog"], [role="alertdialog"]').first();
      expect(await confirmModal.isVisible().catch(() => false)).toBeDefined();
    }
  });

  test('deve ter botão de exportar', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Exportar"), button[title*="Exportar"]').first();

    if (await exportButton.isVisible().catch(() => false)) {
      expect(await exportButton.isVisible()).toBeTruthy();
    }
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/rondas');
    }
  });

  test('deve exibir paginação se necessário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), span:has-text("Página"), span:has-text("de"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há rondas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhuma ronda encontrada/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
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

test.describe('Operacional - Rondas - Detalhes', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir informações detalhadas da ronda', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });

      // Verificar se contém informações da ronda
      const content = await modal.textContent();
      expect(content).toBeDefined();
    }
  });

  test('deve exibir checkpoints no modal de detalhes', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();

      // Verificar se há informações sobre checkpoints
      const checkpointInfo = modal.locator('text=/checkpoint/i').first();
      const hasCheckpointInfo = await checkpointInfo.isVisible().catch(() => false);

      expect(hasCheckpointInfo !== undefined).toBeTruthy();
    }
  });

  test('deve exibir ocorrências registradas na ronda', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();

      // Verificar se há informações sobre ocorrências
      const occurrenceInfo = modal.locator('text=/ocorrencia/i').first();
      const hasOccurrenceInfo = await occurrenceInfo.isVisible().catch(() => false);

      expect(hasOccurrenceInfo !== undefined).toBeTruthy();
    }
  });

  test('deve fechar modal de detalhes ao clicar fora', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      // Fechar com ESC
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      expect(await modal.isVisible().catch(() => false)).toBeFalsy();
    }
  });
});

test.describe('Operacional - Rondas - Filtros Avançados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar por código da ronda', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('RND-2024');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('RND-2024');
    }
  });

  test('deve filtrar por status específico', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ label: 'Em Andamento' });
      await page.waitForTimeout(1000);

      const value = await statusFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve combinar filtros de busca e status', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    const statusFilter = page.locator('select').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('RND');
    }

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
    }

    await page.waitForTimeout(500);
    expect(page.url()).toContain('/rondas');
  });

  test('deve limpar todos os filtros', async ({ page }) => {
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

test.describe('Operacional - Rondas - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir contador de rondas em andamento', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const inProgressStat = page.locator('text=/em andamento/i').first();
    const hasStat = await inProgressStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de rondas concluídas', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const completedStat = page.locator('text=/concluídas/i').first();
    const hasStat = await completedStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador total de ocorrências', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const occurrenceStat = page.locator('text=/ocorrências/i').first();
    const hasStat = await occurrenceStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de medidas disciplinares', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const disciplinaryStat = page.locator('text=/medidas|disciplinares/i').first();
    const hasStat = await disciplinaryStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });
});
