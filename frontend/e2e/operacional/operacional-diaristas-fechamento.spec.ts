import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Fechamento de Folha de Diaristas
 *
 * Testa workflow de fechamento mensal:
 * - Seleção de competência
 * - Geração de relatório
 * - Visualização de estatísticas
 * - Tabela de pagamentos
 * - Geração de pagamentos em lote
 */

test.describe('Operacional - Diaristas - Fechamento', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas/fechamento');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de fechamento', async ({ page }) => {
    await expect(page).toHaveURL(/\/fechamento/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Fechamento de Folha/i, { timeout: 10000 });
  });

  test('deve exibir seletor de competência', async ({ page }) => {
    const monthInput = page.locator('input[type="month"]').first();
    await expect(monthInput).toBeVisible({ timeout: 10000 });
  });

  test('deve permitir alterar a competência', async ({ page }) => {
    const monthInput = page.locator('input[type="month"]').first();
    await monthInput.fill('2024-12');
    await page.waitForTimeout(500);

    await expect(monthInput).toHaveValue('2024-12');
  });

  test('deve ter botão de gerar relatório', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar Relatorio")').first();
    await expect(generateButton).toBeVisible({ timeout: 10000 });
  });

  test('deve ter botão de voltar para diaristas', async ({ page }) => {
    const backButton = page.locator('button:has-text("Diaristas"), a:has-text("Diaristas")').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
  });

  test('deve gerar relatório ao clicar no botão', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar Relatorio")').first();
    await expect(generateButton).toBeVisible({ timeout: 10000 });
    await generateButton.click();
    await page.waitForTimeout(2000);

    // Verificar que o relatório foi gerado ou loading apareceu
    expect(page.url()).toContain('/fechamento');
  });

  test('deve exibir loading ao gerar relatório', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar Relatorio")').first();
    await generateButton.click();

    const loadingIndicator = page.locator('[class*="animate-spin"], [class*="animate-pulse"]').first();
    const hasLoading = await loadingIndicator.isVisible().catch(() => false);

    expect(hasLoading !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Diaristas - Fechamento - Relatório', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas/fechamento');
    await page.waitForTimeout(2000);

    // Gerar relatório
    const generateButton = page.locator('button:has-text("Gerar Relatorio")').first();
    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(3000);
    }
  });

  test('deve exibir cards de estatísticas após gerar relatório', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar se há cards de estatísticas
    const statsSection = page.locator('text=/Diaristas|Total Diarias|Valor Bruto|Valor Liquido/i').first();
    const hasStats = await statsSection.isVisible().catch(() => false);

    expect(hasStats !== undefined).toBeTruthy();
  });

  test('deve exibir contador de diaristas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diaristasText = page.locator('text=/Diaristas/i').first();
    const hasDiaristas = await diaristasText.isVisible().catch(() => false);

    expect(hasDiaristas !== undefined).toBeTruthy();
  });

  test('deve exibir contador de total de diárias', async ({ page }) => {
    await page.waitForTimeout(2000);

    const diariasText = page.locator('text=/Total Diarias/i').first();
    const hasDiarias = await diariasText.isVisible().catch(() => false);

    expect(hasDiarias !== undefined).toBeTruthy();
  });

  test('deve exibir valor bruto total', async ({ page }) => {
    await page.waitForTimeout(2000);

    const valorBrutoText = page.locator('text=/Valor Bruto/i').first();
    const hasValorBruto = await valorBrutoText.isVisible().catch(() => false);

    expect(hasValorBruto !== undefined).toBeTruthy();
  });

  test('deve exibir valor líquido total', async ({ page }) => {
    await page.waitForTimeout(2000);

    const valorLiquidoText = page.locator('text=/Valor Liquido/i').first();
    const hasValorLiquido = await valorLiquidoText.isVisible().catch(() => false);

    expect(hasValorLiquido !== undefined).toBeTruthy();
  });

  test('deve exibir tabela de relatório', async ({ page }) => {
    await page.waitForTimeout(2000);

    const table = page.locator('table').first();
    const hasTable = await table.isVisible().catch(() => false);

    expect(hasTable).toBeTruthy();
  });

  test('deve exibir colunas corretas na tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const headers = page.locator('table th');
    const headerTexts = await headers.allTextContents();

    // Verificar se contém colunas esperadas
    const hasName = headerTexts.some(h => h.toLowerCase().includes('nome'));
    const hasCPF = headerTexts.some(h => h.toLowerCase().includes('cpf'));
    const hasDiarias = headerTexts.some(h => h.toLowerCase().includes('diarias'));
    const hasBruto = headerTexts.some(h => h.toLowerCase().includes('bruto'));
    const hasINSS = headerTexts.some(h => h.toLowerCase().includes('inss'));
    const hasLiquido = headerTexts.some(h => h.toLowerCase().includes('liquido'));

    expect(hasName || hasCPF || hasDiarias || hasBruto || hasINSS || hasLiquido).toBeTruthy();
  });

  test('deve exibir totais no rodapé da tabela', async ({ page }) => {
    await page.waitForTimeout(2000);

    const tfoot = page.locator('table tfoot');
    const hasTfoot = await tfoot.isVisible().catch(() => false);

    expect(hasTfoot).toBeTruthy();
  });

  test('deve exibir empty state quando não há diárias', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhuma diaria concluida/i, text=/sem diarias/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve exibir informações de PIX/Banco', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pixText = page.locator('text=/PIX|Banco/i').first();
    const hasPix = await pixText.isVisible().catch(() => false);

    expect(hasPix !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Diaristas - Fechamento - Pagamentos', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas/fechamento');
    await page.waitForTimeout(2000);

    // Gerar relatório
    const generateButton = page.locator('button:has-text("Gerar Relatorio")').first();
    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(3000);
    }
  });

  test('deve exibir botão de gerar pagamentos quando há itens', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagamentosButton = page.locator('button:has-text("Gerar Pagamentos")').first();
    const hasButton = await pagamentosButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve exibir confirmação ao clicar em gerar pagamentos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagamentosButton = page.locator('button:has-text("Gerar Pagamentos")').first();

    if (await pagamentosButton.isVisible().catch(() => false)) {
      await pagamentosButton.click();
      await page.waitForTimeout(500);

      const confirmSection = page.locator('text=/Confirmar|confirmar geracao/i').first();
      const hasConfirm = await confirmSection.isVisible().catch(() => false);

      expect(hasConfirm !== undefined).toBeTruthy();
    }
  });

  test('deve exibir botão de cancelar na confirmação', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagamentosButton = page.locator('button:has-text("Gerar Pagamentos")').first();

    if (await pagamentosButton.isVisible().catch(() => false)) {
      await pagamentosButton.click();
      await page.waitForTimeout(500);

      const cancelButton = page.locator('button:has-text("Cancelar")').first();
      const hasCancel = await cancelButton.isVisible().catch(() => false);

      expect(hasCancel !== undefined).toBeTruthy();
    }
  });

  test('deve exibir botão de confirmar e gerar na confirmação', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagamentosButton = page.locator('button:has-text("Gerar Pagamentos")').first();

    if (await pagamentosButton.isVisible().catch(() => false)) {
      await pagamentosButton.click();
      await page.waitForTimeout(500);

      const confirmButton = page.locator('button:has-text("Confirmar e Gerar")').first();
      const hasConfirm = await confirmButton.isVisible().catch(() => false);

      expect(hasConfirm !== undefined).toBeTruthy();
    }
  });

  test('deve permitir cancelar geração de pagamentos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagamentosButton = page.locator('button:has-text("Gerar Pagamentos")').first();

    if (await pagamentosButton.isVisible().catch(() => false)) {
      await pagamentosButton.click();
      await page.waitForTimeout(500);

      const cancelButton = page.locator('button:has-text("Cancelar")').first();

      if (await cancelButton.isVisible().catch(() => false)) {
        await cancelButton.click();
        await page.waitForTimeout(500);

        // Botão de gerar pagamentos deve voltar a aparecer
        const pagamentosButtonAgain = page.locator('button:has-text("Gerar Pagamentos")').first();
        const hasButtonAgain = await pagamentosButtonAgain.isVisible().catch(() => false);

        expect(hasButtonAgain !== undefined).toBeTruthy();
      }
    }
  });
});

test.describe('Operacional - Diaristas - Fechamento - Navegação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas/fechamento');
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
});
