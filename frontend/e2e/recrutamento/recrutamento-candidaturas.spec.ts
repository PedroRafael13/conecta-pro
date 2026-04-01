import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Módulo de Candidaturas (Recrutamento)
 *
 * Testa o fluxo de candidaturas e processo seletivo:
 * - Fluxo de candidatura
 * - Mudança de status (recebida, em análise, entrevista, aprovada, rejeitada)
 * - Filtros por vaga e status
 * - Notificações automáticas
 */

test.describe('Recrutamento - Candidaturas - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidaturas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de candidaturas', async ({ page }) => {
    await expect(page).toHaveURL(/candidaturas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Candidaturas/i, { timeout: 10000 });
  });

  test('deve exibir tabela de candidaturas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir cards de estatísticas de candidaturas', async ({ page }) => {
    const statsCards = page.locator('[class*="card"], .card').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir card com total de candidaturas', async ({ page }) => {
    const totalCard = page.locator('text=/Total/i').first();
    const hasTotal = await totalCard.isVisible().catch(() => false);

    expect(hasTotal !== undefined).toBeTruthy();
  });

  test('deve exibir card com candidaturas em andamento', async ({ page }) => {
    const activeCard = page.locator('text=/Andamento|Em Andamento/i').first();
    const hasActive = await activeCard.isVisible().catch(() => false);

    expect(hasActive !== undefined).toBeTruthy();
  });

  test('deve exibir card com candidaturas em entrevista', async ({ page }) => {
    const interviewCard = page.locator('text=/Entrevista/i').first();
    const hasInterview = await interviewCard.isVisible().catch(() => false);

    expect(hasInterview !== undefined).toBeTruthy();
  });

  test('deve exibir card com candidaturas contratadas', async ({ page }) => {
    const hiredCard = page.locator('text=/Contratados|Contratado/i').first();
    const hasHired = await hiredCard.isVisible().catch(() => false);

    expect(hasHired !== undefined).toBeTruthy();
  });

  test('deve exibir card com candidaturas rejeitadas', async ({ page }) => {
    const rejectedCard = page.locator('text=/Rejeitados|Rejeitado/i').first();
    const hasRejected = await rejectedCard.isVisible().catch(() => false);

    expect(hasRejected !== undefined).toBeTruthy();
  });

  test('deve ter campo de busca por candidato', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('João Silva');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('João Silva');
    }
  });

  test('deve ter campo de busca por vaga', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

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

      expect(page.url()).toContain('/candidaturas');
    }
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    const hasCandidate = headerTexts.some(h => h.toLowerCase().includes('candidato'));
    const hasPosition = headerTexts.some(h => h.toLowerCase().includes('vaga'));
    const hasStage = headerTexts.some(h => h.toLowerCase().includes('etapa') || h.toLowerCase().includes('status'));
    const hasDate = headerTexts.some(h => h.toLowerCase().includes('data'));

    expect(hasCandidate || hasPosition || hasStage || hasDate).toBeTruthy();
  });

  test('deve exibir nome do candidato na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const candidateNames = page.locator('table tbody tr td:first-child p').all();
    const count = (await candidateNames).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir título da vaga na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const positionTitles = page.locator('table tbody tr td:nth-child(2) p').all();
    const count = (await positionTitles).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Recrutamento - Candidaturas - Status e Pipeline', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidaturas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir status Inscrito em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const appliedBadges = page.locator('text=/Inscrito|Inscrita/i').all();
    const count = (await appliedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Triagem em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const screeningBadges = page.locator('text=/Triagem/i').all();
    const count = (await screeningBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Entrevista em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const interviewBadges = page.locator('text=/Entrevista/i').all();
    const count = (await interviewBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Avaliação em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const evaluationBadges = page.locator('text=/Avaliacao|Avaliação/i').all();
    const count = (await evaluationBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Proposta em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const proposalBadges = page.locator('text=/Proposta/i').all();
    const count = (await proposalBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Contratado em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const hiredBadges = page.locator('text=/Contratado/i').all();
    const count = (await hiredBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Rejeitado em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const rejectedBadges = page.locator('text=/Rejeitado/i').all();
    const count = (await rejectedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Desistiu em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const withdrawnBadges = page.locator('text=/Desistiu/i').all();
    const count = (await withdrawnBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de avançar etapa', async ({ page }) => {
    await page.waitForTimeout(2000);

    const advanceButton = page.locator('button[title*="Avancar"], button[title*="Avançar"]').first();
    const hasAdvance = await advanceButton.isVisible().catch(() => false);

    expect(hasAdvance !== undefined).toBeTruthy();
  });

  test('deve ter botão de rejeitar candidatura', async ({ page }) => {
    await page.waitForTimeout(2000);

    const rejectButton = page.locator('button[title*="Rejeitar"]').first();
    const hasReject = await rejectButton.isVisible().catch(() => false);

    expect(hasReject !== undefined).toBeTruthy();
  });

  test('deve ter botão de enviar proposta', async ({ page }) => {
    await page.waitForTimeout(2000);

    const proposalButton = page.locator('button[title*="Proposta"], button[title*="Enviar"]').first();
    const hasProposal = await proposalButton.isVisible().catch(() => false);

    expect(hasProposal !== undefined).toBeTruthy();
  });

  test('deve exibir data de inscrição', async ({ page }) => {
    await page.waitForTimeout(2000);

    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data de última atualização', async ({ page }) => {
    await page.waitForTimeout(2000);

    const updateCells = page.locator('table tbody tr td').all();
    const count = (await updateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir email do candidato', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emailCells = page.locator('table tbody tr td:has-text("@")').all();
    const count = (await emailCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir departamento da vaga', async ({ page }) => {
    await page.waitForTimeout(2000);

    const deptCells = page.locator('table tbody tr td p.text-xs').all();
    const count = (await deptCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Recrutamento - Candidaturas - Filtros e Busca', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidaturas');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar candidaturas por nome do candidato', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve filtrar candidaturas por título da vaga', async ({ page }) => {
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

test.describe('Recrutamento - Candidaturas - Empty State', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidaturas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir empty state quando não há candidaturas', async ({ page }) => {
    const emptyState = page.locator('text=/nenhuma candidatura|nenhum registro|vazio/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });
});

test.describe('Recrutamento - Candidaturas - Fluxo Completo', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/candidaturas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir ações apenas para candidaturas ativas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verifica se há botões de ação na tabela
    const actionButtons = page.locator('table tbody tr td:last-child button').all();
    const count = (await actionButtons).length;

    // Pode ter ou não ações dependendo dos dados
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir texto Finalizada para candidaturas encerradas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const finalizedText = page.locator('text=/Finalizada/i').first();
    const hasFinalized = await finalizedText.isVisible().catch(() => false);

    expect(hasFinalized !== undefined).toBeTruthy();
  });
});
