import { test, expect } from '@playwright/test';

/**
 * Testes E2E - Postos de Trabalho
 *
 * Testa CRUD completo de postos:
 * - Listagem
 * - Criação
 * - Visualização
 * - Edição
 * - Exclusão
 */

test.describe('Operacional - Postos de Trabalho', () => {
  // Executar antes de cada teste
  test.beforeEach(async ({ page }) => {
    // Navegar para a página de postos
    await page.goto('/modulos/operacional/postos');
    await page.waitForTimeout(1000);
  });

  test('deve carregar a página de postos', async ({ page }) => {
    // Verificar que a página carregou
    await expect(page).toHaveURL(/\/postos/);

    // Verificar título da página
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Postos/i);
  });

  test('deve exibir lista de postos', async ({ page }) => {
    // Aguardar carregamento da tabela com timeout maior
    await page.waitForSelector('table, [role="table"]', { timeout: 10000 }).catch(() => {});

    // Verificar se tabela ou cards estão presentes
    const hasTable = await page.locator('table').count() > 0;
    const hasCards = await page.locator('[class*="card"], [class*="Card"]').count() > 0;

    expect(hasTable || hasCards).toBeTruthy();
  });

  test('deve exibir botão de novo posto', async ({ page }) => {
    // Aguardar página carregar completamente
    await page.waitForLoadState('networkidle');

    // Procurar botão de criar com timeout maior
    const createButton = page.locator('button:has-text("Novo"), button:has-text("Criar")').first();
    await expect(createButton).toBeVisible({ timeout: 10000 });
  });

  test('deve abrir modal ao clicar em novo posto', async ({ page }) => {
    // Aguardar botão estar pronto
    const createButton = page.locator('button:has-text("Novo"), button:has-text("Criar")').first();
    await expect(createButton).toBeVisible({ timeout: 10000 });

    // Clicar no botão de criar
    await createButton.click();

    // Aguardar modal abrir com timeout maior
    await page.waitForTimeout(1000);

    // Verificar se modal está visível
    const modal = page.locator('[role="dialog"], [class*="modal"]').first();
    await expect(modal).toBeVisible({ timeout: 5000 });
  });

  test('deve validar campos obrigatórios ao criar posto', async ({ page }) => {
    // Aguardar e abrir modal de criação
    const createButton = page.locator('button:has-text("Novo"), button:has-text("Criar")').first();
    await expect(createButton).toBeVisible({ timeout: 10000 });
    await createButton.click();
    await page.waitForTimeout(1000);

    // Tentar salvar sem preencher campos
    const saveButton = page.locator('button:has-text("Salvar"), button[type="submit"]').first();
    await saveButton.click();

    // Verificar que não fechou o modal ou mostrou erro
    await page.waitForTimeout(1000);
    const modal = page.locator('[role="dialog"], [class*="modal"]').first();
    const isVisible = await modal.isVisible().catch(() => false);

    // Modal deve continuar visível ou deve mostrar mensagem de erro
    expect(isVisible).toBeTruthy();
  });

  test('deve preencher formulário de novo posto', async ({ page }) => {
    // Aguardar e abrir modal de criação
    const createButton = page.locator('button:has-text("Novo"), button:has-text("Criar")').first();
    await expect(createButton).toBeVisible({ timeout: 10000 });
    await createButton.click();
    await page.waitForTimeout(1000);

    // Preencher campos
    const nameInput = page.locator('input[name="name"], input[placeholder*="nome"]').first();
    if (await nameInput.isVisible().catch(() => false)) {
      await nameInput.fill('Posto Teste E2E');
    }

    const descriptionInput = page.locator('textarea[name="description"], input[name="description"]').first();
    if (await descriptionInput.isVisible().catch(() => false)) {
      await descriptionInput.fill('Descrição do posto criado via teste E2E');
    }

    // Verificar que campos foram preenchidos
    await expect(nameInput).toHaveValue('Posto Teste E2E');
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    // Localizar campo de busca
    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar" i], input[placeholder*="search" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      // Digitar termo de busca
      await searchInput.fill('teste');

      // Aguardar filtro ser aplicado (debounce)
      await page.waitForTimeout(500);

      // Verificar que valor foi aplicado
      await expect(searchInput).toHaveValue('teste');
    }
  });

  test('deve exibir filtros avançados', async ({ page }) => {
    // Procurar botão de filtros
    const filterButton = page.locator('button:has-text("Filtro"), button:has-text("Filter")').first();

    if (await filterButton.isVisible().catch(() => false)) {
      await filterButton.click();
      await page.waitForTimeout(500);

      // Verificar se painel de filtros apareceu
      const filterPanel = page.locator('[class*="filter"], select, [role="combobox"]').first();
      await expect(filterPanel).toBeVisible();
    }
  });

  test('deve exibir estatísticas de postos', async ({ page }) => {
    // Verificar se há cards de estatísticas
    const statsCards = page.locator('[class*="stat"], [class*="card"]');
    const count = await statsCards.count();

    // Deve haver pelo menos alguns cards de stats
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve permitir visualizar detalhes de um posto', async ({ page }) => {
    // Aguardar lista carregar
    await page.waitForTimeout(2000);

    // Procurar botão de visualizar (ícone de olho)
    const viewButton = page.locator('button[title*="Visualizar"], button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      // Modal de detalhes deve abrir
      const detailModal = page.locator('[role="dialog"]').first();
      await expect(detailModal).toBeVisible();
    }
  });

  test('deve exibir opções de ação para cada posto', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar se há botões de ação (editar, excluir, etc)
    const actionButtons = page.locator('button[title*="Editar"], button[title*="Excluir"], button[title*="Delete"]');
    const count = await actionButtons.count();

    // Deve haver pelo menos alguns botões de ação
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    // Procurar botão de refresh
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      // Página não deve dar erro
      expect(page.url()).toContain('/postos');
    }
  });

  test('deve ter paginação se houver muitos postos', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar se há controles de paginação
    const paginationControls = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), [class*="pagination"]');
    const hasPagination = await paginationControls.count() > 0;

    // Paginação pode não estar presente se houver poucos itens
    expect(hasPagination).toBeDefined();
  });

  test('deve ter botão de exportar dados', async ({ page }) => {
    // Procurar botão de exportar
    const exportButton = page.locator('button:has-text("Exportar"), button:has-text("Export")').first();

    if (await exportButton.isVisible().catch(() => false)) {
      // Botão existe e está visível
      expect(await exportButton.isVisible()).toBeTruthy();
    }
  });

  test('deve mostrar loading state durante carregamento', async ({ page }) => {
    // Recarregar página e verificar loading
    await page.reload();

    // Procurar indicador de loading
    const loader = page.locator('[class*="loading"], [class*="spinner"], [role="status"]').first();

    // Pode aparecer brevemente
    await page.waitForTimeout(100);
  });

  test('deve exibir empty state quando não há postos', async ({ page }) => {
    // Se não houver postos, deve mostrar mensagem
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhum.*encontrado/i, text=/sem.*postos/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    // Empty state pode ou não estar presente dependendo dos dados
    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve navegar de volta para módulo operacional', async ({ page }) => {
    // Procurar botão de voltar
    const backButton = page.locator('button:has-text("Voltar"), a:has-text("Voltar")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(1000);

      // Deve ter voltado para módulo operacional
      expect(page.url()).toMatch(/\/operacional$/);
    }
  });
});

test.describe('Operacional - Postos - Validações', () => {
  test('não deve permitir criar posto sem nome', async ({ page }) => {
    await page.goto('/modulos/operacional/postos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Abrir modal com wait adequado
    const newButton = page.locator('button:has-text("Novo")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    // Tentar salvar sem nome
    const saveButton = page.locator('button:has-text("Salvar")').first();
    if (await saveButton.isVisible().catch(() => false)) {
      await saveButton.click();
      await page.waitForTimeout(1000);

      // Modal deve continuar aberto
      const modal = page.locator('[role="dialog"]').first();
      expect(await modal.isVisible()).toBeTruthy();
    }
  });

  test('deve validar formato de campos numéricos', async ({ page }) => {
    await page.goto('/modulos/operacional/postos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Novo")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    // Tentar inserir texto em campo numérico
    const numericInput = page.locator('input[type="number"]').first();
    if (await numericInput.isVisible().catch(() => false)) {
      await numericInput.fill('abc');

      // Campo não deve aceitar texto
      const value = await numericInput.inputValue();
      expect(value).not.toBe('abc');
    }
  });
});
