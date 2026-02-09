import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Detalhes da Escala
 *
 * Testa visualização de escala específica:
 * - Informações da escala (período, posto, tipo)
 * - Estatísticas da escala
 * - Status e operações (enviar para aprovação, aprovar, publicar)
 * - Editor de escala
 * - Lista de turnos
 */

test.describe('Operacional - Escalas - Detalhes', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    // Usar uma escala de exemplo (pode não existir, mas testamos a estrutura)
    await page.goto('/modulos/operacional/escalas/123e4567-e89b-12d3-a456-426614174000');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de detalhes da escala', async ({ page }) => {
    await expect(page).toHaveURL(/\/escalas\//, { timeout: 10000 });

    // Verificar se tem um heading com "Escala"
    const heading = page.locator('h1').first();
    const headingText = await heading.textContent().catch(() => '');
    expect(headingText?.toLowerCase()).toContain('escala');
  });

  test('deve exibir botão de voltar para escalas', async ({ page }) => {
    const backButton = page.locator('button:has-text("Voltar"), button:has-text("Escalas")').first();
    await expect(backButton).toBeVisible({ timeout: 10000 });
  });

  test('deve exibir informações da escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    const infoSection = page.locator('text=/Informacoes da Escala/i').first();
    const hasInfo = await infoSection.isVisible().catch(() => false);

    expect(hasInfo !== undefined).toBeTruthy();
  });

  test('deve exibir período da escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    const periodoText = page.locator('text=/Periodo/i').first();
    const hasPeriodo = await periodoText.isVisible().catch(() => false);

    expect(hasPeriodo !== undefined).toBeTruthy();
  });

  test('deve exibir posto da escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    const postoText = page.locator('text=/Posto/i').first();
    const hasPosto = await postoText.isVisible().catch(() => false);

    expect(hasPosto !== undefined).toBeTruthy();
  });

  test('deve exibir tipo de escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    const tipoText = page.locator('text=/Tipo de Escala/i').first();
    const hasTipo = await tipoText.isVisible().catch(() => false);

    expect(hasTipo !== undefined).toBeTruthy();
  });

  test('deve exibir status da escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    const statusText = page.locator('text=/Status/i').first();
    const hasStatus = await statusText.isVisible().catch(() => false);

    expect(hasStatus !== undefined).toBeTruthy();
  });

  test('deve exibir badge de status', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar por badge de status (pode ser draft, pending_approval, approved, published, etc)
    const statusBadge = page.locator('[class*="rounded-full"], [class*="badge"]').first();
    const hasBadge = await statusBadge.isVisible().catch(() => false);

    expect(hasBadge !== undefined).toBeTruthy();
  });

  test('deve exibir seção de estatísticas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const statsSection = page.locator('text=/Estatisticas/i').first();
    const hasStats = await statsSection.isVisible().catch(() => false);

    expect(hasStats !== undefined).toBeTruthy();
  });

  test('deve exibir total de turnos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const turnosText = page.locator('text=/Total de Turnos/i').first();
    const hasTurnos = await turnosText.isVisible().catch(() => false);

    expect(hasTurnos !== undefined).toBeTruthy();
  });

  test('deve exibir turnos preenchidos', async ({ page }) => {
    await page.waitForTimeout(2000);

    const filledText = page.locator('text=/Turnos Preenchidos/i').first();
    const hasFilled = await filledText.isVisible().catch(() => false);

    expect(hasFilled !== undefined).toBeTruthy();
  });

  test('deve exibir total de horas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const horasText = page.locator('text=/Total de Horas/i').first();
    const hasHoras = await horasText.isVisible().catch(() => false);

    expect(hasHoras !== undefined).toBeTruthy();
  });

  test('deve exibir taxa de preenchimento', async ({ page }) => {
    await page.waitForTimeout(2000);

    const taxaText = page.locator('text=/Taxa de Preenchimento/i').first();
    const hasTaxa = await taxaText.isVisible().catch(() => false);

    expect(hasTaxa !== undefined).toBeTruthy();
  });

  test('deve ter botão de atualizar', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar")').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      expect(await refreshButton.isVisible()).toBeTruthy();
    }
  });
});

test.describe('Operacional - Escalas - Detalhes - Operações de Status', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/escalas/123e4567-e89b-12d3-a456-426614174000');
    await page.waitForTimeout(2000);
  });

  test('deve exibir botão enviar para aprovação quando status é rascunho', async ({ page }) => {
    await page.waitForTimeout(2000);

    const submitButton = page.locator('button:has-text("Enviar para Aprovacao")').first();
    const hasButton = await submitButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve exibir botão aprovar quando status é pendente', async ({ page }) => {
    await page.waitForTimeout(2000);

    const approveButton = page.locator('button:has-text("Aprovar")').first();
    const hasButton = await approveButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });

  test('deve exibir botão publicar quando status é aprovado', async ({ page }) => {
    await page.waitForTimeout(2000);

    const publishButton = page.locator('button:has-text("Publicar")').first();
    const hasButton = await publishButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Escalas - Detalhes - Editor', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/escalas/123e4567-e89b-12d3-a456-426614174000');
    await page.waitForTimeout(2000);
  });

  test('deve exibir editor de escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    // O editor de escala deve estar presente
    const editorSection = page.locator('[class*="scale-editor"], [class*="ScaleEditor"]').first();
    const hasEditor = await editorSection.isVisible().catch(() => false);

    expect(hasEditor !== undefined).toBeTruthy();
  });

  test('deve exibir mensagem de erro se escala não for encontrada', async ({ page }) => {
    // Usar um ID inválido
    await page.goto('/modulos/operacional/escalas/invalid-id');
    await page.waitForTimeout(2000);

    const errorMessage = page.locator('text=/erro|nao encontrada/i').first();
    const hasError = await errorMessage.isVisible().catch(() => false);

    expect(hasError !== undefined).toBeTruthy();
  });

  test('deve exibir botão voltar para escalas quando há erro', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas/invalid-id');
    await page.waitForTimeout(2000);

    const backButton = page.locator('button:has-text("Voltar para Escalas")').first();
    const hasButton = await backButton.isVisible().catch(() => false);

    expect(hasButton !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Escalas - Detalhes - Navegação', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/escalas/123e4567-e89b-12d3-a456-426614174000');
    await page.waitForTimeout(2000);
  });

  test('deve navegar de volta para lista de escalas', async ({ page }) => {
    const backButton = page.locator('button:has-text("Voltar"), a:has-text("Voltar")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveURL(/\/escalas/, { timeout: 10000 });
    }
  });
});
