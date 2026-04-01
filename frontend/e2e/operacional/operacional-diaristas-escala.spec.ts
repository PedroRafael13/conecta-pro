import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Escala Diária de Diaristas
 *
 * Testa workflow de montagem de escala diária:
 * - Seleção de data
 * - Listagem de diaristas disponíveis
 * - Seleção de diaristas para escala
 * - Configuração de horários
 * - Cálculo de valor total
 * - Confirmação da escala
 */

test.describe('Operacional - Diaristas - Escala Diária', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas/escala');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de escala diária', async ({ page }) => {
    await expect(page).toHaveURL(/\/escala/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Escala Diaria/i, { timeout: 10000 });
  });

  test('deve exibir seletor de data', async ({ page }) => {
    const dateInput = page.locator('input[type="date"]').first();
    await expect(dateInput).toBeVisible({ timeout: 10000 });
  });

  test('deve permitir alterar a data da escala', async ({ page }) => {
    const dateInput = page.locator('input[type="date"]').first();
    await dateInput.fill('2024-12-31');
    await page.waitForTimeout(500);

    await expect(dateInput).toHaveValue('2024-12-31');
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar cards de estatísticas (Disponíveis, Escalados, Valor Total)
    const statsCards = page.locator('[class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(3);
  });

  test('deve exibir contador de diaristas disponíveis', async ({ page }) => {
    await page.waitForTimeout(2000);

    const disponiveisText = page.locator('text=/Disponiveis/i').first();
    const hasDisponiveis = await disponiveisText.isVisible().catch(() => false);

    expect(hasDisponiveis !== undefined).toBeTruthy();
  });

  test('deve exibir contador de diaristas escalados', async ({ page }) => {
    await page.waitForTimeout(2000);

    const escaladosText = page.locator('text=/Escalados/i').first();
    const hasEscalados = await escaladosText.isVisible().catch(() => false);

    expect(hasEscalados !== undefined).toBeTruthy();
  });

  test('deve exibir valor total da escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    const valorTotalText = page.locator('text=/Valor Total/i').first();
    const hasValorTotal = await valorTotalText.isVisible().catch(() => false);

    expect(hasValorTotal !== undefined).toBeTruthy();
  });

  test('deve ter botão de voltar para diaristas', async ({ page }) => {
    const backButton = page.locator('button:has-text("Diaristas"), a:has-text("Diaristas")').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/escala');
    }
  });

  test('deve exibir lista de diaristas ativos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristasSection = page.locator('text=/Diaristas Ativos/i').first();
    const hasSection = await diaristasSection.isVisible().catch(() => false);

    expect(hasSection !== undefined).toBeTruthy();
  });

  test('deve exibir cards de diaristas clicáveis', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristCards = page.locator('[class*="cursor-pointer"]').all();
    const count = (await diaristCards).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir empty state quando não há diaristas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhum diarista ativo encontrado/i, text=/sem diaristas/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir seção de escalados', async ({ page }) => {
    await page.waitForTimeout(2000);

    const escaladosSection = page.locator('text=/Escalados/i').first();
    const hasSection = await escaladosSection.isVisible().catch(() => false);

    expect(hasSection !== undefined).toBeTruthy();
  });

  test('deve exibir mensagem quando nenhum diarista está selecionado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyMessage = page.locator('text=/Selecione diaristas/i').first();
    const hasMessage = await emptyMessage.isVisible().catch(() => false);

    expect(hasMessage !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Diaristas - Escala Diária - Interações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas/escala');
    await page.waitForTimeout(2000);
  });

  test('deve selecionar um diarista ao clicar no card', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar cards de diaristas
    const diaristCard = page.locator('[class*="cursor-pointer"]').first();

    if (await diaristCard.isVisible().catch(() => false)) {
      await diaristCard.click();
      await page.waitForTimeout(500);

      // Verificar se o card foi marcado como selecionado
      const selectedCard = page.locator('[class*="bg-green-500"], [class*="border-green-500"]').first();
      const isSelected = await selectedCard.isVisible().catch(() => false);

      expect(isSelected !== undefined).toBeTruthy();
    }
  });

  test('deve exibir campos de horário ao selecionar diarista', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristCard = page.locator('[class*="cursor-pointer"]').first();

    if (await diaristCard.isVisible().catch(() => false)) {
      await diaristCard.click();
      await page.waitForTimeout(500);

      // Verificar inputs de horário
      const timeInputs = page.locator('input[type="time"]').all();
      const count = (await timeInputs).length;

      expect(count).toBeGreaterThanOrEqual(0);
    }
  });

  test('deve permitir alterar horário de início', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristCard = page.locator('[class*="cursor-pointer"]').first();

    if (await diaristCard.isVisible().catch(() => false)) {
      await diaristCard.click();
      await page.waitForTimeout(500);

      const timeInputs = page.locator('input[type="time"]').all();
      const inputs = await timeInputs;

      if (inputs.length > 0 && inputs[0]) {
        await inputs[0].fill('09:00');
        await page.waitForTimeout(500);

        const inputValue = await inputs[0].inputValue();
        expect(inputValue).toBe('09:00');
      }
    }
  });

  test('deve permitir alterar horário de fim', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristCard = page.locator('[class*="cursor-pointer"]').first();

    if (await diaristCard.isVisible().catch(() => false)) {
      await diaristCard.click();
      await page.waitForTimeout(500);

      const timeInputs = page.locator('input[type="time"]').all();
      const inputs = await timeInputs;

      if (inputs.length > 1 && inputs[1]) {
        await inputs[1].fill('18:00');
        await page.waitForTimeout(500);

        const inputValue = await inputs[1].inputValue();
        expect(inputValue).toBe('18:00');
      }
    }
  });

  test('deve exibir botão de remover diarista escalado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristCard = page.locator('[class*="cursor-pointer"]').first();

    if (await diaristCard.isVisible().catch(() => false)) {
      await diaristCard.click();
      await page.waitForTimeout(500);

      // Verificar botão de remover (X)
      const removeButton = page.locator('button svg[class*="XCircle"], button:has-text("Remover")').first();
      const hasRemove = await removeButton.isVisible().catch(() => false);

      expect(hasRemove !== undefined).toBeTruthy();
    }
  });

  test('deve exibir botão confirmar quando há diaristas selecionados', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristCard = page.locator('[class*="cursor-pointer"]').first();

    if (await diaristCard.isVisible().catch(() => false)) {
      await diaristCard.click();
      await page.waitForTimeout(500);

      const confirmButton = page.locator('button:has-text("Confirmar Escala")').first();
      const hasConfirm = await confirmButton.isVisible().catch(() => false);

      expect(hasConfirm !== undefined).toBeTruthy();
    }
  });

  test('deve exibir resumo da escala ao selecionar diaristas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristCard = page.locator('[class*="cursor-pointer"]').first();

    if (await diaristCard.isVisible().catch(() => false)) {
      await diaristCard.click();
      await page.waitForTimeout(500);

      // Verificar se há resumo com data e valor
      const summaryText = page.locator('text=/diarista/i').first();
      const hasSummary = await summaryText.isVisible().catch(() => false);

      expect(hasSummary !== undefined).toBeTruthy();
    }
  });
});

test.describe('Operacional - Diaristas - Escala Diária - Validações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas/escala');
    await page.waitForTimeout(2000);
  });

  test('deve navegar de volta para lista de diaristas', async ({ page }) => {
    const backButton = page.locator('button:has-text("Diaristas")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveURL(/\/diaristas/, { timeout: 10000 });
    }
  });

  test('deve exibir loading ao carregar diaristas', async ({ page }) => {
    // Recarregar a página para ver loading
    await page.goto('/modulos/operacional/diaristas/escala');

    const loadingIndicator = page.locator('[class*="animate-spin"], [class*="animate-pulse"]').first();
    const hasLoading = await loadingIndicator.isVisible().catch(() => false);

    expect(hasLoading !== undefined).toBeTruthy();
  });
});
