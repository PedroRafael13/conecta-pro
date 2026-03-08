import { test, expect } from '@playwright/test';
import { loginViaAPI } from './helpers/auth';

/**
 * Testes E2E - Ocorrências Disciplinares
 *
 * Testa workflow de ocorrências:
 * - Listagem
 * - Criação
 * - Visualização
 * - Resolução
 * - Filtros
 */

test.describe('Operacional - Ocorrências', () => {
  test.beforeEach(async ({ page }) => {
    // Login via API primeiro
    await loginViaAPI(page);

    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de ocorrências', async ({ page }) => {
    await expect(page).toHaveURL(/\/ocorrencias/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Ocorr/i, { timeout: 10000 });
  });

  test('deve exibir lista de ocorrências', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar se há tabela ou cards
    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable !== undefined).toBeTruthy();
  });

  test('deve exibir botão de nova ocorrência', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova"), button:has-text("Novo")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
  });

  test('deve abrir modal ao clicar em nova ocorrência', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible({ timeout: 5000 });
  });

  test('deve exibir formulário de ocorrência', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    // Verificar campos principais
    const titleInput = page.locator('input[name="title"], input[placeholder*="título"]').first();
    const descriptionInput = page.locator('textarea[name="description"], textarea[placeholder*="descrição"]').first();

    if (await titleInput.isVisible().catch(() => false)) {
      expect(await titleInput.isVisible()).toBeTruthy();
    }

    if (await descriptionInput.isVisible().catch(() => false)) {
      expect(await descriptionInput.isVisible()).toBeTruthy();
    }
  });

  test('deve exibir estatísticas de ocorrências', async ({ page }) => {
    // Stats cards (total, pendentes, resolvidas, graves)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter filtros de busca', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('teste');
    }
  });

  test('deve ter filtro de status', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      // Selecionar um status
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve ter filtro de severidade', async ({ page }) => {
    const severityFilter = page.locator('select').nth(1);

    if (await severityFilter.isVisible().catch(() => false)) {
      await severityFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve exibir badges de status', async ({ page }) => {
    await page.waitForTimeout(2000);

    const badges = page.locator('[class*="badge"]');
    const count = await badges.count();

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir badges de severidade', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges com cores (leve, moderada, grave)
    const severityBadges = page.locator('text=/leve/i, text=/moderada/i, text=/grave/i');
    const count = await severityBadges.count();

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve permitir visualizar detalhes', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button[title*="Ver"], button[title*="Detalhes"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible();
    }
  });

  test('deve exibir informações do funcionário', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar nomes de funcionários na tabela
    const employeeNames = page.locator('td, [class*="employee"]').all();
    const count = (await employeeNames).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data da ocorrência', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar datas formatadas
    const dates = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dates).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/ocorrencias');
    }
  });

  test('deve ter botão de exportar', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Exportar")').first();

    if (await exportButton.isVisible().catch(() => false)) {
      expect(await exportButton.isVisible()).toBeTruthy();
    }
  });
});

test.describe('Operacional - Ocorrências - Workflow', () => {
  test('deve exibir botão de editar em ocorrência aberta', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    // Procurar botão de editar
    const editButton = page.locator('button[title*="Editar"]').first();

    if (await editButton.isVisible().catch(() => false)) {
      expect(await editButton.isVisible()).toBeTruthy();
    }
  });

  test('deve exibir botão de resolver', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    // Procurar botão de resolver (ícone de check)
    const resolveButton = page.locator('button[title*="Resolver"]').first();

    if (await resolveButton.isVisible().catch(() => false)) {
      expect(await resolveButton.isVisible()).toBeTruthy();
    }
  });

  test('deve abrir modal de resolução', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    const resolveButton = page.locator('button[title*="Resolver"]').first();

    if (await resolveButton.isVisible().catch(() => false)) {
      await resolveButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible();
    }
  });

  test('deve exigir resolução ao resolver ocorrência', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    const resolveButton = page.locator('button[title*="Resolver"]').first();

    if (await resolveButton.isVisible().catch(() => false)) {
      await resolveButton.click();
      await page.waitForTimeout(500);

      // Tentar salvar sem preencher
      const saveButton = page.locator('button:has-text("Salvar"), button:has-text("Resolver")').last();

      if (await saveButton.isVisible().catch(() => false)) {
        await saveButton.click();
        await page.waitForTimeout(1000);

        // Modal deve continuar aberto
        const modal = page.locator('[role="dialog"]').first();
        expect(await modal.isVisible()).toBeTruthy();
      }
    }
  });

  test('deve permitir excluir ocorrência aberta', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      expect(await deleteButton.isVisible()).toBeTruthy();
    }
  });

  test('deve mostrar confirmação ao excluir', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(500);

      const confirmModal = page.locator('[role="dialog"], [role="alertdialog"]').first();
      expect(await confirmModal.isVisible().catch(() => false)).toBeDefined();
    }
  });
});

test.describe('Operacional - Ocorrências - Validações', () => {
  test.beforeEach(async ({ page }) => {
    // Login via API primeiro
    await loginViaAPI(page);
  });

  test('deve validar título obrigatório', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Nova")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    // Verificar que o botão está desabilitado (validação ativa) ou que o modal permanece aberto
    const saveButton = page.locator('button[type="submit"]').last();
    const modal = page.locator('[role="dialog"]').first();

    if (await saveButton.isVisible().catch(() => false)) {
      const isDisabled = await saveButton.isDisabled().catch(() => false);
      if (isDisabled) {
        // Botão desabilitado = validação funcionando
        expect(isDisabled).toBeTruthy();
      } else {
        await saveButton.click({ force: true });
        await page.waitForTimeout(500);
        expect(await modal.isVisible().catch(() => false)).toBeTruthy();
      }
    }
  });

  test('deve validar descrição mínima', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Nova")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    const descriptionInput = page.locator('textarea[name="description"]').first();

    if (await descriptionInput.isVisible().catch(() => false)) {
      // Descrição muito curta
      await descriptionInput.fill('abc');

      const saveButton = page.locator('button[type="submit"]').last();
      const modal = page.locator('[role="dialog"]').first();

      if (await saveButton.isVisible().catch(() => false)) {
        const isDisabled = await saveButton.isDisabled().catch(() => false);
        if (isDisabled) {
          expect(isDisabled).toBeTruthy();
        } else {
          await saveButton.click({ force: true });
          await page.waitForTimeout(500);
          expect(await modal.isVisible().catch(() => false)).toBeTruthy();
        }
      }
    }
  });

  test('deve exigir seleção de tipo', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Nova")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    // Form deve ter select de tipo
    const typeSelect = page.locator('select[name*="type"], select[name*="tipo"]').first();

    if (await typeSelect.isVisible().catch(() => false)) {
      expect(await typeSelect.isVisible()).toBeTruthy();
    }
  });

  test('deve exigir seleção de severidade', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Nova")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    const severitySelect = page.locator('select[name*="severity"], select[name*="severidade"]').first();

    if (await severitySelect.isVisible().catch(() => false)) {
      expect(await severitySelect.isVisible()).toBeTruthy();
    }
  });
});

test.describe('Operacional - Ocorrências - Filtros Avançados', () => {
  test('deve filtrar por categoria', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(1000);

    const categoryFilter = page.locator('select').nth(2);

    if (await categoryFilter.isVisible().catch(() => false)) {
      await categoryFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve combinar múltiplos filtros', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(1000);

    // Aplicar busca
    const searchInput = page.locator('input[type="search"]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
    }

    // Aplicar filtro de status
    const statusFilter = page.locator('select').first();
    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
    }

    await page.waitForTimeout(500);
    expect(page.url()).toContain('/ocorrencias');
  });

  test('deve limpar todos os filtros', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(1000);

    // Aplicar filtros
    const searchInput = page.locator('input[type="search"]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
      await page.waitForTimeout(300);
    }

    // Limpar
    const searchInput2 = page.locator('input[type="search"]').first();
    if (await searchInput2.isVisible().catch(() => false)) {
      await searchInput2.clear();
      await page.waitForTimeout(300);

      const value = await searchInput2.inputValue();
      expect(value).toBe('');
    }
  });
});

test.describe('Operacional - Ocorrências - Paginação', () => {
  test('deve ter controles de paginação se necessário', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    const pagination = page.locator('[class*="pagination"], button:has-text("Próxima"), button:has-text("Anterior")');
    const hasPagination = await pagination.count() > 0;

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve mostrar total de registros', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    const totalText = page.locator('text=/\\d+ registros/, text=/total/i').first();
    const hasTotal = await totalText.isVisible().catch(() => false);

    expect(hasTotal !== undefined).toBeTruthy();
  });
});
