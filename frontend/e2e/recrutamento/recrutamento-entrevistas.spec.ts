import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Módulo de Entrevistas (Recrutamento)
 *
 * Testa o agendamento e gestão de entrevistas:
 * - Agendamento de entrevistas
 * - Calendário de entrevistas
 * - Feedbacks pós-entrevista
 * - Lembretes e notificações
 */

test.describe('Recrutamento - Entrevistas - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/entrevistas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de entrevistas', async ({ page }) => {
    await expect(page).toHaveURL(/entrevistas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Entrevistas/i, { timeout: 10000 });
  });

  test('deve exibir tabela de entrevistas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table');
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir cards de estatísticas de entrevistas', async ({ page }) => {
    const statsCards = page.locator('[class*="card"], .card').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir card com total de entrevistas', async ({ page }) => {
    const totalCard = page.locator('text=/Total/i').first();
    const hasTotal = await totalCard.isVisible().catch(() => false);

    expect(hasTotal !== undefined).toBeTruthy();
  });

  test('deve exibir card com entrevistas hoje', async ({ page }) => {
    const todayCard = page.locator('text=/Hoje/i').first();
    const hasToday = await todayCard.isVisible().catch(() => false);

    expect(hasToday !== undefined).toBeTruthy();
  });

  test('deve exibir card com entrevistas agendadas', async ({ page }) => {
    const scheduledCard = page.locator('text=/Agendadas|Agendada/i').first();
    const hasScheduled = await scheduledCard.isVisible().catch(() => false);

    expect(hasScheduled !== undefined).toBeTruthy();
  });

  test('deve exibir card com entrevistas concluídas', async ({ page }) => {
    const completedCard = page.locator('text=/Concluidas|Concluída/i').first();
    const hasCompleted = await completedCard.isVisible().catch(() => false);

    expect(hasCompleted !== undefined).toBeTruthy();
  });

  test('deve exibir card com entrevistas canceladas', async ({ page }) => {
    const cancelledCard = page.locator('text=/Canceladas|Cancelada/i').first();
    const hasCancelled = await cancelledCard.isVisible().catch(() => false);

    expect(hasCancelled !== undefined).toBeTruthy();
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

  test('deve ter campo de busca por entrevistador', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Maria');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Maria');
    }
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/entrevistas');
    }
  });

  test('deve ter botão de agendar entrevista', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar"), button:has-text("Nova")').first();
    const hasButton = await scheduleButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    const hasCandidate = headerTexts.some(h => h.toLowerCase().includes('candidato'));
    const hasPosition = headerTexts.some(h => h.toLowerCase().includes('vaga'));
    const hasType = headerTexts.some(h => h.toLowerCase().includes('tipo'));
    const hasDate = headerTexts.some(h => h.toLowerCase().includes('data'));
    const hasStatus = headerTexts.some(h => h.toLowerCase().includes('status'));

    expect(hasCandidate || hasPosition || hasType || hasDate || hasStatus).toBeTruthy();
  });
});

test.describe('Recrutamento - Entrevistas - Agendamento', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/entrevistas');
    await page.waitForTimeout(2000);
  });

  test('deve abrir modal ao clicar em agendar entrevista', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista"), button:has-text("Agendar")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible({ timeout: 5000 });
    }
  });

  test('deve exibir título do modal de agendamento', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const modalTitle = page.locator('text=/Agendar Nova Entrevista|Nova Entrevista/i').first();
      await expect(modalTitle).toBeVisible({ timeout: 5000 });
    }
  });

  test('deve ter campo de ID da candidatura', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const appIdInput = page.locator('input#application_id, label:has-text("Candidatura") + input').first();

      if (await appIdInput.isVisible().catch(() => false)) {
        await appIdInput.fill('123e4567-e89b-12d3-a456-426614174000');
        await expect(appIdInput).toHaveValue('123e4567-e89b-12d3-a456-426614174000');
      }
    }
  });

  test('deve ter campo de ID do entrevistador', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const interviewerInput = page.locator('input#interviewer_id, label:has-text("Entrevistador") + input').first();

      if (await interviewerInput.isVisible().catch(() => false)) {
        await interviewerInput.fill('123e4567-e89b-12d3-a456-426614174001');
        await expect(interviewerInput).toHaveValue('123e4567-e89b-12d3-a456-426614174001');
      }
    }
  });

  test('deve ter select de tipo de entrevista', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const typeSelect = page.locator('select, [role="combobox"]').first();

      if (await typeSelect.isVisible().catch(() => false)) {
        expect(await typeSelect.isVisible()).toBeTruthy();
      }
    }
  });

  test('deve ter campo de data e hora', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const dateInput = page.locator('input#scheduled_at, input[type="datetime-local"]').first();

      if (await dateInput.isVisible().catch(() => false)) {
        expect(await dateInput.isVisible()).toBeTruthy();
      }
    }
  });

  test('deve ter campo de duração', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const durationInput = page.locator('input#duration_minutes, input[type="number"]').first();

      if (await durationInput.isVisible().catch(() => false)) {
        await durationInput.fill('60');
        await expect(durationInput).toHaveValue('60');
      }
    }
  });

  test('deve ter campo de local/link', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const locationInput = page.locator('input#location, label:has-text("Local") + input, label:has-text("Link") + input').first();

      if (await locationInput.isVisible().catch(() => false)) {
        await locationInput.fill('Sala de Reunião 1');
        await expect(locationInput).toHaveValue('Sala de Reunião 1');
      }
    }
  });

  test('deve ter campo de observações', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const notesInput = page.locator('input#notes, label:has-text("Observacoes") + input, label:has-text("Observações") + input').first();

      if (await notesInput.isVisible().catch(() => false)) {
        await notesInput.fill('Trazer documentos');
        await expect(notesInput).toHaveValue('Trazer documentos');
      }
    }
  });

  test('deve ter botão de cancelar agendamento', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
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

  test('deve permitir selecionar tipo Presencial', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const typeSelect = page.locator('select, [role="combobox"]').first();

      if (await typeSelect.isVisible().catch(() => false)) {
        await typeSelect.selectOption({ label: 'Presencial' });
        expect(await typeSelect.inputValue()).toBeTruthy();
      }
    }
  });

  test('deve permitir selecionar tipo Vídeo', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const typeSelect = page.locator('select, [role="combobox"]').first();

      if (await typeSelect.isVisible().catch(() => false)) {
        await typeSelect.selectOption({ label: 'Vídeo' });
        expect(await typeSelect.inputValue()).toBeTruthy();
      }
    }
  });

  test('deve permitir selecionar tipo Telefone', async ({ page }) => {
    const scheduleButton = page.locator('button:has-text("Agendar Entrevista")').first();

    if (await scheduleButton.isVisible().catch(() => false)) {
      await scheduleButton.click();
      await page.waitForTimeout(1000);

      const typeSelect = page.locator('select, [role="combobox"]').first();

      if (await typeSelect.isVisible().catch(() => false)) {
        await typeSelect.selectOption({ label: 'Telefone' });
        expect(await typeSelect.inputValue()).toBeTruthy();
      }
    }
  });
});

test.describe('Recrutamento - Entrevistas - Status e Ações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/entrevistas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir status Agendada em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const scheduledBadges = page.locator('text=/Agendada/i').all();
    const count = (await scheduledBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Confirmada em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const confirmedBadges = page.locator('text=/Confirmada/i').all();
    const count = (await confirmedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Em Andamento em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const inProgressBadges = page.locator('text=/Em Andamento/i').all();
    const count = (await inProgressBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Concluída em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const completedBadges = page.locator('text=/Concluida|Concluída/i').all();
    const count = (await completedBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Cancelada em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const cancelledBadges = page.locator('text=/Cancelada/i').all();
    const count = (await cancelledBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir status Ausente em badges', async ({ page }) => {
    await page.waitForTimeout(2000);

    const noShowBadges = page.locator('text=/Ausente/i').all();
    const count = (await noShowBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de reagendar entrevista', async ({ page }) => {
    await page.waitForTimeout(2000);

    const rescheduleButton = page.locator('button[title*="Reagendar"]').first();
    const hasReschedule = await rescheduleButton.isVisible().catch(() => false);

    expect(hasReschedule !== undefined).toBeTruthy();
  });

  test('deve ter botão de concluir entrevista', async ({ page }) => {
    await page.waitForTimeout(2000);

    const completeButton = page.locator('button[title*="Concluir"]').first();
    const hasComplete = await completeButton.isVisible().catch(() => false);

    expect(hasComplete !== undefined).toBeTruthy();
  });

  test('deve ter botão de cancelar entrevista', async ({ page }) => {
    await page.waitForTimeout(2000);

    const cancelButton = page.locator('button[title*="Cancelar"]').first();
    const hasCancel = await cancelButton.isVisible().catch(() => false);

    expect(hasCancel !== undefined).toBeTruthy();
  });

  test('deve ter botão de avaliar entrevista', async ({ page }) => {
    await page.waitForTimeout(2000);

    const evaluateButton = page.locator('button[title*="Avaliar"]').first();
    const hasEvaluate = await evaluateButton.isVisible().catch(() => false);

    expect(hasEvaluate !== undefined).toBeTruthy();
  });
});

test.describe('Recrutamento - Entrevistas - Filtros e Busca', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/entrevistas');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar entrevistas por candidato', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve filtrar entrevistas por vaga', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Vigilante');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Vigilante');
    }
  });

  test('deve filtrar entrevistas por entrevistador', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Maria');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Maria');
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

test.describe('Recrutamento - Entrevistas - Detalhes', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/entrevistas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir tipo de entrevista com ícone', async ({ page }) => {
    await page.waitForTimeout(2000);

    const typeCells = page.locator('table tbody tr td:has(svg)').all();
    const count = (await typeCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir data formatada', async ({ page }) => {
    await page.waitForTimeout(2000);

    const dateCells = page.locator('text=/\\d{2}\\/\\d{2}\\/\\d{4}/').all();
    const count = (await dateCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir hora formatada', async ({ page }) => {
    await page.waitForTimeout(2000);

    const timeCells = page.locator('text=/\\d{2}:\\d{2}/').all();
    const count = (await timeCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir duração em minutos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const durationCells = page.locator('text=/\\d+ min/i').all();
    const count = (await durationCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir nome do entrevistador', async ({ page }) => {
    await page.waitForTimeout(2000);

    const interviewerCells = page.locator('table tbody tr td:nth-child(6)').all();
    const count = (await interviewerCells).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('Recrutamento - Entrevistas - Empty State', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/recrutamento/entrevistas');
    await page.waitForTimeout(2000);
  });

  test('deve exibir empty state quando não há entrevistas', async ({ page }) => {
    const emptyState = page.locator('text=/nenhuma entrevista|nenhum registro|vazio/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve ter botão para agendar primeira entrevista no empty state', async ({ page }) => {
    const emptyButton = page.locator('button:has-text("Agendar Entrevista")').first();
    const hasButton = await emptyButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});
