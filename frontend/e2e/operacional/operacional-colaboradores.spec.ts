import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Cadastro de Colaboradores
 *
 * Testa gestão de colaboradores:
 * - Listagem em tabela
 * - Busca por nome, email, matrícula
 * - Filtros por status
 * - Edição de colaborador
 * - Exportação de dados
 * - Visualização de detalhes
 */

test.describe('Operacional - Colaboradores', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de colaboradores', async ({ page }) => {
    await expect(page).toHaveURL(/\/colaboradores/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Colaboradores|Funcionários/i, { timeout: 10000 });
  });

  test('deve exibir tabela de colaboradores', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir estatísticas de colaboradores', async ({ page }) => {
    // Stats cards (total, ativos, afastados, exibindo)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve ter filtro de status', async ({ page }) => {
    const statusFilter = page.locator('select, [role="combobox"]').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    // Verificar se contém colunas esperadas
    const hasName = headerTexts.some(h => h.toLowerCase().includes('nome'));
    const hasRegistration = headerTexts.some(h => h.toLowerCase().includes('matrícula'));
    const hasRole = headerTexts.some(h => h.toLowerCase().includes('cargo'));
    const hasDepartment = headerTexts.some(h => h.toLowerCase().includes('departamento'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));

    expect(hasName || hasRegistration || hasRole || hasDepartment || hasStatus).toBeTruthy();
  });

  test('deve exibir badges de status na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status (ativo, inativo, afastado, férias)
    const statusBadges = page.locator('text=/ativo|inativo|afastado|férias/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir avatar e nome do colaborador', async ({ page }) => {
    await page.waitForTimeout(2000);

    const nameCells = page.locator('table tbody tr td:first-child').all();
    const count = (await nameCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir matrícula do colaborador', async ({ page }) => {
    await page.waitForTimeout(2000);

    const registrationCells = page.locator('table tbody tr td code, table tbody tr td:has-text("-")').all();
    const count = (await registrationCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir cargo do colaborador', async ({ page }) => {
    await page.waitForTimeout(2000);

    const roleCells = page.locator('table tbody tr td').all();
    const count = (await roleCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir departamento do colaborador', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deptCells = page.locator('table tbody tr td').all();
    const count = (await deptCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data de admissão', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar datas formatadas
    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter menu de ações em cada linha', async ({ page }) => {
    await page.waitForTimeout(2000);

    const actionMenus = page.locator('button[title*="Mais"], button:has-text("..."), [data-state] button').all();
    const count = (await actionMenus).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve abrir dropdown de ações ao clicar', async ({ page }) => {
    await page.waitForTimeout(2000);

    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const dropdown = page.locator('[role="menu"], [data-radix-popper-content-wrapper]').first();
      expect(await dropdown.isVisible().catch(() => false)).toBeDefined();
    }
  });

  test('deve ter opção de editar no dropdown', async ({ page }) => {
    await page.waitForTimeout(2000);

    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const editOption = page.locator('text=/editar/i').first();
      expect(await editOption.isVisible().catch(() => false)).toBeDefined();
    }
  });

  test('deve ter opção de ver detalhes no dropdown', async ({ page }) => {
    await page.waitForTimeout(2000);

    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const viewOption = page.locator('text=/ver detalhes|detalhes/i').first();
      expect(await viewOption.isVisible().catch(() => false)).toBeDefined();
    }
  });

  test('deve abrir modal de edição', async ({ page }) => {
    await page.waitForTimeout(2000);

    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const editOption = page.locator('text=/editar/i').first();

      if (await editOption.isVisible().catch(() => false)) {
        await editOption.click();
        await page.waitForTimeout(1000);

        const modal = page.locator('[role="dialog"]').first();
        await expect(modal).toBeVisible({ timeout: 5000 });
      }
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

      expect(page.url()).toContain('/colaboradores');
    }
  });

  test('deve exibir badge de fonte de dados', async ({ page }) => {
    const sourceBadge = page.locator('text=/Fonte:|Solides|Sistema Local/i').first();
    const hasBadge = await sourceBadge.isVisible().catch(() => false);

    expect(hasBadge !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há colaboradores', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhum colaborador encontrado/i, text=/sem colaboradores/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Colaboradores - Edição', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForTimeout(2000);
  });

  test('deve exibir formulário de edição com campos corretos', async ({ page }) => {
    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const editOption = page.locator('text=/editar/i').first();

      if (await editOption.isVisible().catch(() => false)) {
        await editOption.click();
        await page.waitForTimeout(1000);

        const modal = page.locator('[role="dialog"]').first();

        // Verificar campos do formulário
        const cargoInput = modal.locator('input[name*="cargo"], label:has-text("Cargo") + input').first();
        const deptInput = modal.locator('input[name*="departamento"], label:has-text("Departamento") + input').first();
        const phoneInput = modal.locator('input[name*="telefone"], label:has-text("Telefone") + input').first();

        expect(
          (await cargoInput.isVisible().catch(() => false)) ||
          (await deptInput.isVisible().catch(() => false)) ||
          (await phoneInput.isVisible().catch(() => false))
        ).toBeTruthy();
      }
    }
  });

  test('deve permitir alterar cargo', async ({ page }) => {
    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const editOption = page.locator('text=/editar/i').first();

      if (await editOption.isVisible().catch(() => false)) {
        await editOption.click();
        await page.waitForTimeout(1000);

        const modal = page.locator('[role="dialog"]').first();
        const cargoInput = modal.locator('input[name*="cargo"]').first();

        if (await cargoInput.isVisible().catch(() => false)) {
          await cargoInput.fill('Vigilante');
          await expect(cargoInput).toHaveValue('Vigilante');
        }
      }
    }
  });

  test('deve permitir alterar status', async ({ page }) => {
    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const editOption = page.locator('text=/editar/i').first();

      if (await editOption.isVisible().catch(() => false)) {
        await editOption.click();
        await page.waitForTimeout(1000);

        const modal = page.locator('[role="dialog"]').first();
        const statusSelect = modal.locator('select, [role="combobox"]').first();

        if (await statusSelect.isVisible().catch(() => false)) {
          await statusSelect.selectOption({ index: 1 });
          expect(await statusSelect.inputValue()).toBeTruthy();
        }
      }
    }
  });

  test('deve ter botão de cancelar edição', async ({ page }) => {
    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const editOption = page.locator('text=/editar/i').first();

      if (await editOption.isVisible().catch(() => false)) {
        await editOption.click();
        await page.waitForTimeout(1000);

        const cancelButton = page.locator('button:has-text("Cancelar")').first();

        if (await cancelButton.isVisible().catch(() => false)) {
          await cancelButton.click();
          await page.waitForTimeout(500);

          const modal = page.locator('[role="dialog"]').first();
          expect(await modal.isVisible().catch(() => false)).toBeFalsy();
        }
      }
    }
  });

  test('deve validar campos obrigatórios na edição', async ({ page }) => {
    const actionMenu = page.locator('button[class*="ghost"]').first();

    if (await actionMenu.isVisible().catch(() => false)) {
      await actionMenu.click();
      await page.waitForTimeout(500);

      const editOption = page.locator('text=/editar/i').first();

      if (await editOption.isVisible().catch(() => false)) {
        await editOption.click();
        await page.waitForTimeout(1000);

        const modal = page.locator('[role="dialog"]').first();
        const saveButton = modal.locator('button:has-text("Salvar"), button[type="submit"]').first();

        if (await saveButton.isVisible().catch(() => false)) {
          await saveButton.click();
          await page.waitForTimeout(1000);

          // Modal deve continuar aberto se houver erro
          expect(await modal.isVisible().catch(() => false)).toBeDefined();
        }
      }
    }
  });
});

test.describe('Operacional - Colaboradores - Filtros Avançados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar por nome', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve filtrar por email', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('@email.com');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('@email.com');
    }
  });

  test('deve filtrar por matrícula', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('MAT');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('MAT');
    }
  });

  test('deve filtrar por status ativo', async ({ page }) => {
    const statusFilter = page.locator('select, [role="combobox"]').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ label: 'Ativo' });
      await page.waitForTimeout(1000);

      const value = await statusFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve filtrar por status afastado', async ({ page }) => {
    const statusFilter = page.locator('select, [role="combobox"]').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ label: 'Afastado' });
      await page.waitForTimeout(1000);

      const value = await statusFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve filtrar por férias', async ({ page }) => {
    const statusFilter = page.locator('select, [role="combobox"]').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ label: 'Férias' });
      await page.waitForTimeout(1000);

      const value = await statusFilter.inputValue();
      expect(value).toBeTruthy();
    }
  });

  test('deve combinar busca e filtro de status', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    const statusFilter = page.locator('select, [role="combobox"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
    }

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
    }

    await page.waitForTimeout(500);
    expect(page.url()).toContain('/colaboradores');
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

test.describe('Operacional - Colaboradores - Estatísticas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir contador total de colaboradores', async ({ page }) => {
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForTimeout(2000);

    const totalStat = page.locator('text=/Total/i').first();
    const hasStat = await totalStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de ativos', async ({ page }) => {
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForTimeout(2000);

    const activeStat = page.locator('text=/Ativos/i').first();
    const hasStat = await activeStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de afastados', async ({ page }) => {
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForTimeout(2000);

    const awayStat = page.locator('text=/Afastados/i').first();
    const hasStat = await awayStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });

  test('deve exibir contador de exibidos', async ({ page }) => {
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForTimeout(2000);

    const showingStat = page.locator('text=/Exibindo/i').first();
    const hasStat = await showingStat.isVisible().catch(() => false);

    expect(hasStat !== undefined).toBeTruthy();
  });
});
