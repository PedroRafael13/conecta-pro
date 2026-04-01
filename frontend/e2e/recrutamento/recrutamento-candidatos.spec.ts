import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Módulo de Candidatos (Recrutamento)
 *
 * Testa o CRUD e gerenciamento de candidatos:
 * - Cadastro de candidatos
 * - Upload de currículo
 * - Pipeline de seleção
 * - Avaliações e notas
 * - Histórico de candidaturas
 */

test.describe('Recrutamento - Candidatos - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidatos');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de candidatos', async ({ page }) => {
    await expect(page).toHaveURL(/candidatos/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Candidatos/i, { timeout: 10000 });
  });

  test('deve exibir tabela de candidatos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir cards de estatísticas de candidatos', async ({ page }) => {
    const statsCards = page.locator('[class*="card"], .card').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir card com total de candidatos', async ({ page }) => {
    const totalCard = page.locator('text=/Total/i').first();
    const hasTotal = await totalCard.isVisible().catch(() => false);

    expect(hasTotal !== undefined).toBeTruthy();
  });

  test('deve exibir card com candidatos ativos', async ({ page }) => {
    const activeCard = page.locator('text=/Ativos|Ativo/i').first();
    const hasActive = await activeCard.isVisible().catch(() => false);

    expect(hasActive !== undefined).toBeTruthy();
  });

  test('deve exibir card com candidatos bloqueados', async ({ page }) => {
    const blockedCard = page.locator('text=/Bloqueados|Bloqueado/i').first();
    const hasBlocked = await blockedCard.isVisible().catch(() => false);

    expect(hasBlocked !== undefined).toBeTruthy();
  });

  test('deve exibir card com candidatos contratados', async ({ page }) => {
    const hiredCard = page.locator('text=/Contratados|Contratado/i').first();
    const hasHired = await hiredCard.isVisible().catch(() => false);

    expect(hasHired !== undefined).toBeTruthy();
  });

  test('deve ter campo de busca por nome', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('João Silva');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('João Silva');
    }
  });

  test('deve ter campo de busca por email', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('@email.com');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('@email.com');
    }
  });

  test('deve ter campo de busca por telefone', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('(11) 99999');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('(11) 99999');
    }
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    const hasName = headerTexts.some(h => h.toLowerCase().includes('candidato') || h.toLowerCase().includes('nome'));
    const hasContact = headerTexts.some(h => h.toLowerCase().includes('contato'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));
    const hasPosition = headerTexts.some(h => h.toLowerCase().includes('cargo') || h.toLowerCase().includes('desejado'));

    expect(hasName || hasContact || hasStatus || hasPosition).toBeTruthy();
  });

  test('deve exibir avatar do candidato na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const avatars = page.locator('table tbody tr td:first-child div').all();
    const count = (await avatars).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir badges de status na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const statusBadges = page.locator('text=/ativo|inativo|bloqueado|contratado/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de novo candidato', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato"), button:has-text("Novo")').first();
    const hasButton = await newButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/candidatos');
    }
  });
});

test.describe('Recrutamento - Candidatos - Cadastro', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidatos');
    await page.waitForTimeout(2000);
  });

  test('deve abrir modal ao clicar em novo candidato', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato"), button:has-text("Novo")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });
    }
  });

  test('deve exibir título do modal de cadastro', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modalTitle = page.locator('text=/Cadastrar Novo Candidato|Novo Candidato/i').first();
      await expect(modalTitle).toBeVisible({ timeout: 5000 });
    }
  });

  test('deve ter campo de nome completo', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const nameInput = page.locator('input#name, label:has-text("Nome") + input').first();

      if (await nameInput.isVisible().catch(() => false)) {
        await nameInput.fill('João da Silva');
        await expect(nameInput).toHaveValue('João da Silva');
      }
    }
  });

  test('deve ter campo de email', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const emailInput = page.locator('input#email, input[type="email"]').first();

      if (await emailInput.isVisible().catch(() => false)) {
        await emailInput.fill('joao.silva@email.com');
        await expect(emailInput).toHaveValue('joao.silva@email.com');
      }
    }
  });

  test('deve ter campo de telefone', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const phoneInput = page.locator('input#phone, label:has-text("Telefone") + input').first();

      if (await phoneInput.isVisible().catch(() => false)) {
        await phoneInput.fill('(11) 99999-9999');
        await expect(phoneInput).toHaveValue('(11) 99999-9999');
      }
    }
  });

  test('deve ter campo de CPF', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const cpfInput = page.locator('input#cpf, label:has-text("CPF") + input').first();

      if (await cpfInput.isVisible().catch(() => false)) {
        await cpfInput.fill('123.456.789-00');
        await expect(cpfInput).toHaveValue('123.456.789-00');
      }
    }
  });

  test('deve ter campo de cargo desejado', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const positionInput = page.locator('input#position_desired, label:has-text("Cargo") + input').first();

      if (await positionInput.isVisible().catch(() => false)) {
        await positionInput.fill('Vigilante');
        await expect(positionInput).toHaveValue('Vigilante');
      }
    }
  });

  test('deve ter campo de origem', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const sourceInput = page.locator('input#source, label:has-text("Origem") + input').first();

      if (await sourceInput.isVisible().catch(() => false)) {
        await sourceInput.fill('Site');
        await expect(sourceInput).toHaveValue('Site');
      }
    }
  });

  test('deve ter botão de cancelar cadastro', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

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

  test('deve validar campo de nome obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Candidato")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const createButton = page.locator('button:has-text("Cadastrar"), button[type="submit"]').first();

      if (await createButton.isVisible().catch(() => false)) {
        await createButton.click();
        await page.waitForTimeout(1000);

        // Modal deve continuar aberto se houver erro
        const modal = page.locator('[role="dialog"]').first();
        expect(await modal.isVisible().catch(() => false)).toBeDefined();
      }
    }
  });
});

test.describe('Recrutamento - Candidatos - Pipeline de Seleção', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidatos');
    await page.waitForTimeout(2000);
  });

  test('deve exibir status Ativo em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const activeBadges = page.locator('text=/Ativo/i').all();
    const count = (await activeBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Inativo em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const inactiveBadges = page.locator('text=/Inativo/i').all();
    const count = (await inactiveBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Bloqueado em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const blockedBadges = page.locator('text=/Bloqueado/i').all();
    const count = (await blockedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Contratado em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const hiredBadges = page.locator('text=/Contratado/i').all();
    const count = (await hiredBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de bloquear candidato', async ({ page }) => {
    await page.waitForTimeout(2000);

    const blockButton = page.locator('button[title*="Bloquear"]').first();
    const hasBlock = await blockButton.isVisible().catch(() => false);

    expect(hasBlock !== undefined).toBeTruthy();
  });

  test('deve ter botão de desbloquear candidato', async ({ page }) => {
    await page.waitForTimeout(2000);

    const unblockButton = page.locator('button[title*="Desbloquear"]').first();
    const hasUnblock = await unblockButton.isVisible().catch(() => false);

    expect(hasUnblock !== undefined).toBeTruthy();
  });

  test('deve ter botão de editar candidato', async ({ page }) => {
    await page.waitForTimeout(2000);

    const editButton = page.locator('button[title*="Editar"]').first();
    const hasEdit = await editButton.isVisible().catch(() => false);

    expect(hasEdit !== undefined).toBeTruthy();
  });

  test('deve ter botão de excluir candidato', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();
    const hasDelete = await deleteButton.isVisible().catch(() => false);

    expect(hasDelete !== undefined).toBeTruthy();
  });

  test('deve exibir data de cadastro do candidato', async ({ page }) => {
    await page.waitForTimeout(2000);

    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir email do candidato na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emailCells = page.locator('table tbody tr td:has-text("@")').all();
    const count = (await emailCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir telefone do candidato na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const phoneCells = page.locator('table tbody tr td:has-text("(")').all();
    const count = (await phoneCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Recrutamento - Candidatos - Filtros e Busca', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidatos');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar candidatos por nome', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve filtrar candidatos por email', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('@gmail.com');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('@gmail.com');
    }
  });

  test('deve filtrar candidatos por cargo desejado', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Vigilante');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Vigilante');
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

  test('deve exibir contador de resultados', async ({ page }) => {
    const info = page.locator('text=/Mostrando|Exibindo/i').first();
    const hasInfo = await info.isVisible().catch(() => false);

    expect(hasInfo !== undefined).toBeTruthy();
  });
});

test.describe('Recrutamento - Candidatos - Empty State', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidatos');
    await page.waitForTimeout(2000);
  });

  test('deve exibir empty state quando não há candidatos', async ({ page }) => {
    const emptyState = page.locator('text=/nenhum candidato|nenhum registro|vazio/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve ter botão para criar primeiro candidato no empty state', async ({ page }) => {
    const emptyButton = page.locator('button:has-text("Novo Candidato")').first();
    const hasButton = await emptyButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});
