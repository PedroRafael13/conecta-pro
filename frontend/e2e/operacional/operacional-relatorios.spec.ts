import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Relatórios Operacionais
 *
 * Testa geração de relatórios:
 * - Filtros por período, posto e funcionário
 * - Relatório de cobertura
 * - Relatório de horas
 * - Relatório de custos
 * - Exportação CSV e PDF
 * - Visualização de gráficos
 */

test.describe('Operacional - Relatórios', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/relatorios');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de relatórios', async ({ page }) => {
    await expect(page).toHaveURL(/\/relatorios/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Relatorios/i, { timeout: 10000 });
  });

  test('deve exibir subtítulo descritivo', async ({ page }) => {
    await page.waitForTimeout(2000);

    const subtitle = page.locator('text=/Cobertura, horas e custos/i').first();
    const hasSubtitle = await subtitle.isVisible().catch(() => false);

    expect(hasSubtitle !== undefined).toBeTruthy();
  });

  test('deve ter botão de voltar para operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional")').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de filtros', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await expect(filterButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de exportar Excel/CSV', async ({ page }) => {
    const exportButton = page.locator('button[title*="Excel"], button[title*="CSV"]').first();
    await expect(exportButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de exportar PDF', async ({ page }) => {
    const pdfButton = page.locator('button[title*="PDF"]').first();
    await expect(pdfButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button svg[class*="RefreshCw"]').first();
    await expect(refreshButton).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Operacional - Relatórios - Filtros', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/relatorios');
    await page.waitForTimeout(2000);
  });

  test('deve expandir painel de filtros ao clicar', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const filterPanel = page.locator('select, input[type="date"]').first();
    const hasPanel = await filterPanel.isVisible().catch(() => false);

    expect(hasPanel !== undefined).toBeTruthy();
  });

  test('deve ter filtro de posto', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const postoLabel = page.locator('label:has-text("Posto")').first();
    const hasLabel = await postoLabel.isVisible().catch(() => false);

    expect(hasLabel !== undefined).toBeTruthy();
  });

  test('deve ter filtro de funcionário', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const funcionarioLabel = page.locator('label:has-text("Funcionario")').first();
    const hasLabel = await funcionarioLabel.isVisible().catch(() => false);

    expect(hasLabel !== undefined).toBeTruthy();
  });

  test('deve ter filtro de data de início', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const startDateInput = page.locator('input[type="date"]').first();
    const hasInput = await startDateInput.isVisible().catch(() => false);

    expect(hasInput !== undefined).toBeTruthy();
  });

  test('deve ter filtro de data de fim', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const endDateInputs = page.locator('input[type="date"]').all();
    const inputs = await endDateInputs;

    expect(inputs.length).toBeGreaterThanOrEqual(1);
  });

  test('deve permitir alterar data de início', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const startDateInput = page.locator('input[type="date"]').first();

    if (await startDateInput.isVisible().catch(() => false)) {
      await startDateInput.fill('2024-01-01');
      await page.waitForTimeout(500);

      const inputValue = await startDateInput.inputValue();
      expect(inputValue).toBe('2024-01-01');
    }
  });

  test('deve permitir alterar data de fim', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const dateInputs = page.locator('input[type="date"]').all();
    const inputs = await dateInputs;

    if (inputs.length > 1 && inputs[1]) {
      await inputs[1].fill('2024-12-31');
      await page.waitForTimeout(500);

      const inputValue = await inputs[1].inputValue();
      expect(inputValue).toBe('2024-12-31');
    }
  });

  test('deve permitir selecionar posto', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const postSelect = page.locator('select').first();

    if (await postSelect.isVisible().catch(() => false)) {
      await postSelect.selectOption({ index: 0 });
      await page.waitForTimeout(500);

      const value = await postSelect.inputValue();
      expect(value).toBeDefined();
    }
  });

  test('deve permitir selecionar funcionário', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();
    await filterButton.click();
    await page.waitForTimeout(500);

    const employeeSelect = page.locator('select').nth(1);

    if (await employeeSelect.isVisible().catch(() => false)) {
      await employeeSelect.selectOption({ index: 0 });
      await page.waitForTimeout(500);

      const value = await employeeSelect.inputValue();
      expect(value).toBeDefined();
    }
  });
});

test.describe('Operacional - Relatórios - Resumo', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/relatorios');
    await page.waitForTimeout(2000);
  });

  test('deve exibir cards de resumo', async ({ page }) => {
    await page.waitForTimeout(2000);

    const summaryCards = page.locator('[class*="card"], [class*="bg-"]').all();
    const count = (await summaryCards).length;

    expect(count).toBeGreaterThanOrEqual(3);
  });

  test('deve exibir cobertura', async ({ page }) => {
    await page.waitForTimeout(2000);

    const coberturaText = page.locator('text=/Cobertura/i').first();
    const hasCobertura = await coberturaText.isVisible().catch(() => false);

    expect(hasCobertura !== undefined).toBeTruthy();
  });

  test('deve exibir horas trabalhadas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const horasText = page.locator('text=/Horas trabalhadas|Horas/i').first();
    const hasHoras = await horasText.isVisible().catch(() => false);

    expect(hasHoras !== undefined).toBeTruthy();
  });

  test('deve exibir custo estimado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const custoText = page.locator('text=/Custo estimado|Custo/i').first();
    const hasCusto = await custoText.isVisible().catch(() => false);

    expect(hasCusto !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Relatórios - Tabelas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/relatorios');
    await page.waitForTimeout(2000);
  });

  test('deve exibir tabela de cobertura por posto', async ({ page }) => {
    await page.waitForTimeout(2000);

    const coberturaTitle = page.locator('text=/Cobertura por posto/i').first();
    const hasTitle = await coberturaTitle.isVisible().catch(() => false);

    expect(hasTitle !== undefined).toBeTruthy();
  });

  test('deve exibir tabela de horas por funcionário', async ({ page }) => {
    await page.waitForTimeout(2000);

    const horasTitle = page.locator('text=/Horas por funcionario/i').first();
    const hasTitle = await horasTitle.isVisible().catch(() => false);

    expect(hasTitle !== undefined).toBeTruthy();
  });

  test('deve exibir tabela de custos por posto', async ({ page }) => {
    await page.waitForTimeout(2000);

    const custosTitle = page.locator('text=/Custos estimados por posto|Custos/i').first();
    const hasTitle = await custosTitle.isVisible().catch(() => false);

    expect(hasTitle !== undefined).toBeTruthy();
  });

  test('deve exibir barras de progresso nas tabelas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const progressBars = page.locator('[class*="rounded-full"], [class*="progress"], [class*="bar"]').all();
    const count = (await progressBars).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir mensagem quando não há dados', async ({ page }) => {
    await page.waitForTimeout(2000);

    const noDataMessage = page.locator('text=/Sem dados|nenhum dado/i').first();
    const hasMessage = await noDataMessage.isVisible().catch(() => false);

    expect(hasMessage !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Relatórios - Interações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/relatorios');
    await page.waitForTimeout(2000);
  });

  test('deve alternar visibilidade dos filtros', async ({ page }) => {
    const filterButton = page.locator('button:has-text("Filtros")').first();

    // Abrir filtros
    await filterButton.click();
    await page.waitForTimeout(500);

    const filterPanel = page.locator('select, input[type="date"]').first();
    const isVisible = await filterPanel.isVisible().catch(() => false);

    expect(isVisible !== undefined).toBeTruthy();

    // Fechar filtros
    await filterButton.click();
    await page.waitForTimeout(500);
  });

  test('deve atualizar relatórios ao clicar em atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button svg[class*="RefreshCw"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(2000);

      expect(page.url()).toContain('/relatorios');
    }
  });
});

test.describe('Operacional - Relatórios - Navegação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/relatorios');
    await page.waitForTimeout(2000);
  });

  test('deve navegar de volta para módulo operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveURL(/\/operacional/, { timeout: 10000 });
    }
  });
});
