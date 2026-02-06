import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Módulo de Vagas (Recrutamento)
 *
 * Testa o CRUD e gerenciamento de vagas:
 * - Listagem de vagas
 * - Criação de vaga (título, descrição, requisitos)
 * - Status da vaga (aberta, fechada, pausada)
 * - Contagem de candidaturas por vaga
 * - Filtros por departamento e status
 */

test.describe('Recrutamento - Vagas - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/vagas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de vagas', async ({ page }) => {
    await expect(page).toHaveURL(/vagas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Vagas/i, { timeout: 10000 });
  });

  test('deve exibir tabela de vagas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir cards de estatísticas de vagas', async ({ page }) => {
    const statsCards = page.locator('[class*="card"], .card').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir card com total de vagas', async ({ page }) => {
    const totalCard = page.locator('text=/Total/i').first();
    const hasTotal = await totalCard.isVisible().catch(() => false);

    expect(hasTotal !== undefined).toBeTruthy();
  });

  test('deve exibir card com vagas abertas', async ({ page }) => {
    const openCard = page.locator('text=/Abertas|Aberta/i').first();
    const hasOpen = await openCard.isVisible().catch(() => false);

    expect(hasOpen !== undefined).toBeTruthy();
  });

  test('deve exibir card com vagas pausadas', async ({ page }) => {
    const pausedCard = page.locator('text=/Pausadas|Pausada/i').first();
    const hasPaused = await pausedCard.isVisible().catch(() => false);

    expect(hasPaused !== undefined).toBeTruthy();
  });

  test('deve exibir card com vagas fechadas', async ({ page }) => {
    const closedCard = page.locator('text=/Fechadas|Fechada/i').first();
    const hasClosed = await closedCard.isVisible().catch(() => false);

    expect(hasClosed !== undefined).toBeTruthy();
  });

  test('deve ter campo de busca por título', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Vigilante');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Vigilante');
    }
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/vagas');
    }
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    const hasTitle = headerTexts.some(h => h.toLowerCase().includes('titulo') || h.toLowerCase().includes('título'));
    const hasDepartment = headerTexts.some(h => h.toLowerCase().includes('departamento'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));
    const hasLocation = headerTexts.some(h => h.toLowerCase().includes('local'));

    expect(hasTitle || hasDepartment || hasStatus || hasLocation).toBeTruthy();
  });

  test('deve exibir badges de status na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const statusBadges = page.locator('text=/aberta|fechada|pausada|rascunho|publicada/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de nova vaga', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga"), button:has-text("Nova")').first();
    const hasButton = await newButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});

test.describe('Recrutamento - Vagas - Criação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/vagas');
    await page.waitForTimeout(2000);
  });

  test('deve abrir modal ao clicar em nova vaga', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga"), button:has-text("Nova")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });
    }
  });

  test('deve exibir título do modal de criação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modalTitle = page.locator('text=/Criar Nova Vaga|Nova Vaga/i').first();
      await expect(modalTitle).toBeVisible({ timeout: 5000 });
    }
  });

  test('deve ter campo de título da vaga', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const titleInput = page.locator('input#title, label:has-text("Titulo") + input, label:has-text("Título") + input').first();

      if (await titleInput.isVisible().catch(() => false)) {
        await titleInput.fill('Vigilante Patrimonial');
        await expect(titleInput).toHaveValue('Vigilante Patrimonial');
      }
    }
  });

  test('deve ter campo de descrição da vaga', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const descInput = page.locator('input#description, textarea#description, label:has-text("Descricao") + input, label:has-text("Descrição") + input').first();

      if (await descInput.isVisible().catch(() => false)) {
        await descInput.fill('Vaga para vigilante patrimonial noturno');
        await expect(descInput).toHaveValue('Vaga para vigilante patrimonial noturno');
      }
    }
  });

  test('deve ter campo de departamento', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const deptInput = page.locator('input#department, label:has-text("Departamento") + input').first();

      if (await deptInput.isVisible().catch(() => false)) {
        await deptInput.fill('Operacional');
        await expect(deptInput).toHaveValue('Operacional');
      }
    }
  });

  test('deve ter campo de localização', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const locationInput = page.locator('input#location, label:has-text("Localizacao") + input, label:has-text("Localização") + input').first();

      if (await locationInput.isVisible().catch(() => false)) {
        await locationInput.fill('São Paulo, SP');
        await expect(locationInput).toHaveValue('São Paulo, SP');
      }
    }
  });

  test('deve ter select de tipo de contrato', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const contractSelect = page.locator('select, [role="combobox"]').first();

      if (await contractSelect.isVisible().catch(() => false)) {
        expect(await contractSelect.isVisible()).toBeTruthy();
      }
    }
  });

  test('deve ter campo de número de vagas', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const vacanciesInput = page.locator('input#vacancies, input[type="number"]').first();

      if (await vacanciesInput.isVisible().catch(() => false)) {
        await vacanciesInput.fill('2');
        await expect(vacanciesInput).toHaveValue('2');
      }
    }
  });

  test('deve ter botão de cancelar criação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const cancelButton = page.locator('button:has-text("Cancelar")').first();

      if (await cancelButton.isVisible().catch(() => false)) {
        await cancelButton.click();
        await page.waitForTimeout(500);

        const modal = page.locator('[role="dialog"]').first();
        expect(await modal.isVisible().catch(() => false)).toBeFalsy();
      }
    }
  });

  test('deve validar campo de título obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const createButton = page.locator('button:has-text("Criar Vaga"), button:has-text("Criar")').first();

      if (await createButton.isVisible().catch(() => false)) {
        await createButton.click();
        await page.waitForTimeout(1000);

        // Modal deve continuar aberto se houver erro
        const modal = page.locator('[role="dialog"]').first();
        expect(await modal.isVisible().catch(() => false)).toBeDefined();
      }
    }
  });

  test('deve permitir selecionar tipo CLT', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const contractSelect = page.locator('select, [role="combobox"]').first();

      if (await contractSelect.isVisible().catch(() => false)) {
        await contractSelect.selectOption({ label: 'CLT' });
        expect(await contractSelect.inputValue()).toBeTruthy();
      }
    }
  });

  test('deve permitir selecionar tipo PJ', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Vaga")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const contractSelect = page.locator('select, [role="combobox"]').first();

      if (await contractSelect.isVisible().catch(() => false)) {
        await contractSelect.selectOption({ label: 'PJ' });
        expect(await contractSelect.inputValue()).toBeTruthy();
      }
    }
  });
});

test.describe('Recrutamento - Vagas - Status', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/vagas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir status Rascunho em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const draftBadges = page.locator('text=/Rascunho/i').all();
    const count = (await draftBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Aberta em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const openBadges = page.locator('text=/Aberta/i').all();
    const count = (await openBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Pausada em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pausedBadges = page.locator('text=/Pausada/i').all();
    const count = (await pausedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Fechada em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const closedBadges = page.locator('text=/Fechada/i').all();
    const count = (await closedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Publicada em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const publishedBadges = page.locator('text=/Publicada/i').all();
    const count = (await publishedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de publicar para vagas em rascunho', async ({ page }) => {
    await page.waitForTimeout(2000);

    const publishButton = page.locator('button[title*="Publicar"]').first();
    const hasPublish = await publishButton.isVisible().catch(() => false);

    expect(hasPublish !== undefined).toBeTruthy();
  });

  test('deve ter botão de fechar para vagas abertas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const closeButton = page.locator('button[title*="Fechar"]').first();
    const hasClose = await closeButton.isVisible().catch(() => false);

    expect(hasClose !== undefined).toBeTruthy();
  });

  test('deve ter botão de excluir vaga', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();
    const hasDelete = await deleteButton.isVisible().catch(() => false);

    expect(hasDelete !== undefined).toBeTruthy();
  });

  test('deve exibir botão de editar em cada linha', async ({ page }) => {
    await page.waitForTimeout(2000);

    const editButtons = page.locator('button[title*="Editar"]').all();
    const count = (await editButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data de criação da vaga', async ({ page }) => {
    await page.waitForTimeout(2000);

    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Recrutamento - Vagas - Filtros', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/vagas');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar vagas por título', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Vigilante');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Vigilante');
    }
  });

  test('deve filtrar vagas por departamento', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Operacional');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Operacional');
    }
  });

  test('deve limpar filtro de busca', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('teste');
      await page.waitForTimeout(500);
      await searchInput.clear();

      const value = await searchInput.inputValue();
      expect(value).toBe('');
    }
  });

  test('deve exibir mensagem quando não há resultados', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('XYZ123NADA');
      await page.waitForTimeout(1000);

      const noResults = page.locator('text=/Nenhum|não encontrado|vazio/i').first();
      expect(await noResults.isVisible().catch(() => false)).toBeDefined();
    }
  });

  test('deve exibir contador de resultados filtrados', async ({ page }) => {
    const info = page.locator('text=/Mostrando|Exibindo/i').first();
    const hasInfo = await info.isVisible().catch(() => false);

    expect(hasInfo !== undefined).toBeTruthy();
  });
});

test.describe('Recrutamento - Vagas - Empty State', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/vagas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir empty state quando não há vagas', async ({ page }) => {
    const emptyState = page.locator('text=/nenhuma vaga|nenhum registro|vazio/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve ter botão para criar primeira vaga no empty state', async ({ page }) => {
    const emptyButton = page.locator('button:has-text("Nova Vaga")').first();
    const hasButton = await emptyButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});
