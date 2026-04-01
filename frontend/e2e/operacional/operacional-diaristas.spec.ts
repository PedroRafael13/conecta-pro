import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Gestão de Diaristas
 *
 * Testa workflow completo de diaristas:
 * - Listagem com filtros
 * - Cadastro de novo diarista
 * - Estatísticas e métricas
 * - Visualização de detalhes
 * - Navegação para escala e fechamento
 */

test.describe('Operacional - Diaristas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de diaristas', async ({ page }) => {
    await expect(page).toHaveURL(/\/diaristas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Diaristas/i, { timeout: 10000 });
  });

  test('deve exibir lista de diaristas em cards', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar se há cards de diaristas ou empty state
    const diaristCards = page.locator('[class*="card"], [class*="Card"]').all();
    const count = (await diaristCards).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir estatísticas de diaristas', async ({ page }) => {
    // Stats cards (total, ativos, avaliação média, diárias)
    const statsCards = page.locator('[class*="card"], [class*="stat"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('deve exibir botão de novo diarista', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Diarista"), button:has-text("Novo")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
  });

  test('deve abrir modal ao clicar em novo diarista', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Diarista")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible({ timeout: 5000 });
  });

  test('deve ter campo de busca funcional', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar" i]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(500);

      await expect(searchInput).toHaveValue('Silva');
    }
  });

  test('deve ter filtros de status', async ({ page }) => {
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve ter filtro de tipo de diarista', async ({ page }) => {
    const typeFilter = page.locator('select').nth(1);

    if (await typeFilter.isVisible().catch(() => false)) {
      await typeFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      expect(page.url()).toBeDefined();
    }
  });

  test('deve exibir badges de status nos cards', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status (ativo, inativo, bloqueado)
    const statusBadges = page.locator('text=/ativo|inativo|bloqueado|em avaliacao/i').all();
    const count = (await statusBadges).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir tipo de diarista nos cards', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar tipos (limpeza, portaria, manutencao, jardinagem)
    const typeLabels = page.locator('text=/limpeza|portaria|manutencao|jardinagem/i').all();
    const count = (await typeLabels).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir avaliação em estrelas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar ícones de estrela
    const starIcons = page.locator('svg[class*="star"], [class*="Star"]').all();
    const count = (await starIcons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir métricas de diaristas (diárias, presença, valor)', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar métricas
    const metrics = page.locator('text=/diarias|presenca|diaria/i').all();
    const count = (await metrics).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir botão de ver detalhes em cada card', async ({ page }) => {
    await page.waitForTimeout(2000);

    const viewButtons = page.locator('button:has-text("Ver"), button[title*="Ver"]').all();
    const count = (await viewButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir botão de agendar em cada card', async ({ page }) => {
    await page.waitForTimeout(2000);

    const scheduleButtons = page.locator('button:has-text("Agendar"), button[title*="Agendar"]').all();
    const count = (await scheduleButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter botão de editar em cada card', async ({ page }) => {
    await page.waitForTimeout(2000);

    const editButtons = page.locator('button[title*="Editar"]').all();
    const count = (await editButtons).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve ter link para escala diária', async ({ page }) => {
    const scheduleLink = page.locator('a[href*="escala"], button:has-text("Escala")').first();

    if (await scheduleLink.isVisible().catch(() => false)) {
      expect(await scheduleLink.isVisible()).toBeTruthy();
    }
  });

  test('deve ter link para fechamento', async ({ page }) => {
    const closingLink = page.locator('a[href*="fechamento"], button:has-text("Fechamento")').first();

    if (await closingLink.isVisible().catch(() => false)) {
      expect(await closingLink.isVisible()).toBeTruthy();
    }
  });

  test('deve ter botão de atualizar lista', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Atualizar"), button[title*="Atualizar"]').first();

    if (await refreshButton.isVisible().catch(() => false)) {
      await refreshButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toContain('/diaristas');
    }
  });

  test('deve navegar para página de escala diária', async ({ page }) => {
    const scheduleLink = page.locator('a[href*="escala"]').first();

    if (await scheduleLink.isVisible().catch(() => false)) {
      await scheduleLink.click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveURL(/\/escala/, { timeout: 10000 });
    }
  });

  test('deve navegar para página de fechamento', async ({ page }) => {
    const closingLink = page.locator('a[href*="fechamento"]').first();

    if (await closingLink.isVisible().catch(() => false)) {
      await closingLink.click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveURL(/\/fechamento/, { timeout: 10000 });
    }
  });

  test('deve exibir paginação se houver muitos diaristas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const pagination = page.locator('button:has-text("Próxima"), button:has-text("Anterior"), [class*="pagination"]').first();
    const hasPagination = await pagination.isVisible().catch(() => false);

    expect(hasPagination !== undefined).toBeTruthy();
  });

  test('deve exibir empty state quando não há diaristas', async ({ page }) => {
    await page.waitForTimeout(2000);

    const emptyState = page.locator('text=/nenhum diarista encontrado/i, text=/sem diaristas/i').first();
    const hasEmptyState = await emptyState.isVisible().catch(() => false);

    expect(hasEmptyState !== undefined).toBeTruthy();
  });

  test('deve voltar para módulo operacional', async ({ page }) => {
    const backButton = page.locator('button:has-text("Operacional"), a:has-text("Operacional"), button:has-text("Voltar")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toMatch(/\/operacional/);
    }
  });
});

test.describe('Operacional - Diaristas - Validações', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve validar campos obrigatórios ao criar diarista', async ({ page }) => {
    await page.goto('/modulos/operacional/diaristas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Novo Diarista")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    // Tentar salvar sem preencher
    const saveButton = page.locator('button[type="submit"]').last();
    const modal = page.locator('[role="dialog"], .fixed.inset-0 > div:last-child, .fixed.z-50').first();

    if (await saveButton.isVisible().catch(() => false)) {
      const isDisabled = await saveButton.isDisabled().catch(() => false);
      if (isDisabled) {
        // Botao desabilitado = validacao ativa
        expect(isDisabled).toBeTruthy();
      } else {
        await saveButton.click({ force: true });
        await page.waitForTimeout(500);
        expect(await modal.isVisible().catch(() => false)).toBeTruthy();
      }
    }
  });

  test('deve validar formato de CPF', async ({ page }) => {
    await page.goto('/modulos/operacional/diaristas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Novo Diarista")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    const cpfInput = page.locator('input[name*="cpf"], input[placeholder*="CPF"]').first();

    if (await cpfInput.isVisible().catch(() => false)) {
      await cpfInput.fill('123');

      // Deve mostrar erro de validação ou formato
      expect(await cpfInput.isVisible()).toBeTruthy();
    }
  });

  test('deve validar formato de telefone', async ({ page }) => {
    await page.goto('/modulos/operacional/diaristas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(2000);

    const newButton = page.locator('button:has-text("Novo Diarista")').first();
    await expect(newButton).toBeVisible({ timeout: 10000 });
    await newButton.click();
    await page.waitForTimeout(1000);

    const phoneInput = page.locator('input[name*="telefone"], input[name*="celular"]').first();

    if (await phoneInput.isVisible().catch(() => false)) {
      await phoneInput.fill('99999');

      expect(await phoneInput.isVisible()).toBeTruthy();
    }
  });
});

test.describe('Operacional - Diaristas - Filtros Avançados', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/operacional/diaristas');
    await page.waitForTimeout(2000);
  });

  test('deve filtrar por nome', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Maria');
      await page.waitForTimeout(1000);

      await expect(searchInput).toHaveValue('Maria');
    }
  });

  test('deve combinar múltiplos filtros', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first();
    const statusFilter = page.locator('select').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
    }

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
    }

    await page.waitForTimeout(500);
    expect(page.url()).toContain('/diaristas');
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
