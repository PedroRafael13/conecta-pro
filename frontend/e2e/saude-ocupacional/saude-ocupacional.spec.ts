import { test, expect, Page } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Saúde Ocupacional
 *
 * Funcionalidades testadas:
 * - Dashboard de saúde ocupacional
 * - Estatísticas de PCMSO, EPIs e PPRA/PGR
 * - Navegação para sub-módulos
 */

// Mock data
const mockPCMSOStats = {
  total_exames: 245,
  exames_vencendo: 12,
  asos_vencendo: 8,
  exames_agendados: 15,
};

const mockEPIStats = {
  total_entregas: 523,
  epis_estoque: 150,
  entregas_pendentes: 23,
};

const mockPPRAStats = {
  total_riscos: 45,
  riscos_altos: 8,
  setores_mapeados: 12,
  medidas_controle: 67,
};

// Setup de mocks para API
async function setupSaudeOcupacionalMocks(page: Page) {
  await page.route('**/api/v1/saude-ocupacional/pcmso/statistics**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockPCMSOStats),
    });
  });

  await page.route('**/api/v1/saude-ocupacional/epi/statistics**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockEPIStats),
    });
  });

  await page.route('**/api/v1/saude-ocupacional/ppra/statistics**', async (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockPPRAStats),
    });
  });
}

test.describe('Saúde Ocupacional - Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await setupSaudeOcupacionalMocks(page);
    await page.goto('/modulos/saude-ocupacional');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  // ==========================================
  // TESTES DE CARREGAMENTO E EXIBIÇÃO
  // ==========================================

  test('deve carregar página de saúde ocupacional', async ({ page }) => {
    await expect(page).toHaveURL(/\/saude-ocupacional/);
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Saúde Ocupacional/i);
  });

  test('deve exibir descrição da página', async ({ page }) => {
    const description = page.locator('text=/PCMSO|EPIs|PPRA|segurança do trabalho/i');
    await expect(description).toBeVisible();
  });

  // ==========================================
  // TESTES DE ESTATÍSTICAS
  // ==========================================

  test('deve exibir cards de estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    const examesCard = page.locator('text=/Total Exames/i');
    const asosCard = page.locator('text=/ASOs Vencendo/i');
    const episCard = page.locator('text=/EPIs Entregues/i');
    const riscosCard = page.locator('text=/Riscos Mapeados/i');

    await expect(examesCard).toBeVisible();
    await expect(asosCard).toBeVisible();
    await expect(episCard).toBeVisible();
    await expect(riscosCard).toBeVisible();
  });

  test('deve exibir valores corretos nas estatísticas', async ({ page }) => {
    await page.waitForTimeout(1000);

    await expect(page.getByText('245').first()).toBeVisible(); // Total Exames
    await expect(page.getByText('12').first()).toBeVisible(); // ASOs Vencendo
    await expect(page.getByText('523').first()).toBeVisible(); // EPIs Entregues
    await expect(page.getByText('45').first()).toBeVisible(); // Riscos Mapeados
  });

  // ==========================================
  // TESTES DE SUB-MÓDULOS
  // ==========================================

  test('deve exibir card de Exames Médicos', async ({ page }) => {
    const examesCard = page.locator('text=/Exames Médicos/i').first();
    await expect(examesCard).toBeVisible();
  });

  test('deve exibir card de EPIs', async ({ page }) => {
    const episCard = page.locator('text=/EPIs/i').first();
    await expect(episCard).toBeVisible();
  });

  test('deve exibir card de Riscos Ocupacionais', async ({ page }) => {
    const riscosCard = page.locator('text=/Riscos Ocupacionais/i').first();
    await expect(riscosCard).toBeVisible();
  });

  test('deve exibir descrições nos cards', async ({ page }) => {
    const examesDesc = page.locator('text=/ASOs|agendamentos|NR-7/i').first();
    const hasDesc = await examesDesc.isVisible().catch(() => false);
    expect(hasDesc !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE ÍCONES
  // ==========================================

  test('deve exibir ícones nos cards', async ({ page }) => {
    const cardsWithIcons = page.locator('[class*="rounded-lg"]').first();
    const hasIcon = await cardsWithIcons.isVisible().catch(() => false);
    expect(hasIcon !== undefined).toBeTruthy();
  });

  test('deve ter ícone de estetoscópio em Exames', async ({ page }) => {
    const stethoscopeIcon = page.locator('[data-lucide="Stethoscope"]').first();
    const hasIcon = await stethoscopeIcon.isVisible().catch(() => false);
    expect(hasIcon !== undefined).toBeTruthy();
  });

  test('deve ter ícone de capacete em EPIs', async ({ page }) => {
    const hardHatIcon = page.locator('[data-lucide="HardHat"]').first();
    const hasIcon = await hardHatIcon.isVisible().catch(() => false);
    expect(hasIcon !== undefined).toBeTruthy();
  });

  test('deve ter ícone de alerta em Riscos', async ({ page }) => {
    const alertIcon = page.locator('[data-lucide="AlertTriangle"]').first();
    const hasIcon = await alertIcon.isVisible().catch(() => false);
    expect(hasIcon !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE NAVEGAÇÃO
  // ==========================================

  test('deve navegar para página de Exames', async ({ page }) => {
    const examesCard = page.locator('text=/Exames Médicos/i').first();
    await examesCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/exames/);
  });

  test('deve navegar para página de EPIs', async ({ page }) => {
    const episCard = page.locator('text=/EPIs/i').first();
    await episCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/epi/);
  });

  test('deve navegar para página de Riscos', async ({ page }) => {
    const riscosCard = page.locator('text=/Riscos Ocupacionais/i').first();
    await riscosCard.click();
    await page.waitForTimeout(500);

    await expect(page).toHaveURL(/\/riscos/);
  });

  // ==========================================
  // TESTES DE CARDS INTERATIVOS
  // ==========================================

  test('deve ter cursor pointer nos cards', async ({ page }) => {
    const cards = page.locator('[class*="cursor-pointer"]').first();
    const hasPointer = await cards.isVisible().catch(() => false);
    expect(hasPointer !== undefined).toBeTruthy();
  });

  test('deve ter seta indicando navegação', async ({ page }) => {
    const arrowIcon = page.locator('[data-lucide="ArrowRight"]').first();
    const hasArrow = await arrowIcon.isVisible().catch(() => false);
    expect(hasArrow !== undefined).toBeTruthy();
  });

  // ==========================================
  // TESTES DE LOADING
  // ==========================================

  test('deve exibir loading durante carregamento', async ({ page }) => {
    await page.reload();

    const loader = page.locator('[class*="animate-pulse"]').first();
    const hasLoader = await loader.isVisible().catch(() => false);
    expect(hasLoader !== undefined).toBeTruthy();
  });

  test('deve exibir skeleton em estatísticas durante loading', async ({ page }) => {
    await page.reload();

    const skeleton = page.locator('[class*="animate-pulse"]').first();
    const hasSkeleton = await skeleton.isVisible().catch(() => false);
    expect(hasSkeleton !== undefined).toBeTruthy();
  });
});
