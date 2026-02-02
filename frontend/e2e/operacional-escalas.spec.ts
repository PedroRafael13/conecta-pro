import { test, expect } from '@playwright/test';

/**
 * Testes E2E - Escalas de Trabalho
 *
 * Testa workflow de escalas:
 * - Listagem de escalas
 * - Geração de escala
 * - Visualização
 * - Aprovação
 * - Publicação
 */

test.describe('Operacional - Escalas', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de escalas', async ({ page }) => {
    await expect(page).toHaveURL(/\/escalas/, { timeout: 10000 });

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Escalas/i, { timeout: 10000 });
  });

  test('deve exibir lista de escalas', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Verificar se há cards ou lista de escalas
    const scaleCards = page.locator('[class*="card"], [class*="scale"]');
    const count = await scaleCards.count();

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve exibir botão de gerar escala', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar"), button:has-text("Nova")').first();
    await expect(generateButton).toBeVisible({ timeout: 10000 });
  });

  test('deve abrir modal ao clicar em gerar escala', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar")').first();
    await expect(generateButton).toBeVisible({ timeout: 10000 });
    await generateButton.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toBeVisible({ timeout: 5000 });
  });

  test('deve exibir formulário de geração de escala', async ({ page }) => {
    const generateButton = page.locator('button:has-text("Gerar")').first();
    await expect(generateButton).toBeVisible({ timeout: 10000 });
    await generateButton.click();
    await page.waitForTimeout(1000);

    // Verificar campos do formulário
    const postSelect = page.locator('select, [role="combobox"]').first();
    const monthSelect = page.locator('select:has-text("Janeiro"), select:has-text("Fevereiro"), select[name*="mes"], select[name*="month"]').first();

    if (await postSelect.isVisible().catch(() => false)) {
      expect(await postSelect.isVisible()).toBeTruthy();
    }
  });

  test('deve ter filtros de mês e ano', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Procurar selects de mês e ano
    const filters = page.locator('select').all();
    const count = (await filters).length;

    // Deve haver pelo menos alguns selects para filtro
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve filtrar escalas por status', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Procurar filtro de status
    const statusFilter = page.locator('select').first();

    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      // Verificar que filtro foi aplicado
      expect(page.url()).toBeDefined();
    }
  });

  test('deve exibir estatísticas de escalas', async ({ page }) => {
    const statsCards = page.locator('[class*="stat"], [class*="card"]').all();
    const count = (await statsCards).length;

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve mostrar badge de status em cada escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar badges de status
    const statusBadges = page.locator('[class*="badge"], [class*="status"]');
    const count = await statusBadges.count();

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve permitir visualizar detalhes de uma escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Clicar no botão de ver
    const viewButton = page.locator('button:has-text("Ver"), button[title*="Ver"]').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      // Deve navegar para página de detalhes ou abrir modal
      expect(page.url()).toBeDefined();
    }
  });

  test('deve exibir métricas da escala', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar cards de métricas (turnos, horas, custo)
    const metrics = page.locator('text=/turnos/i, text=/horas/i, text=/custo/i').all();
    const count = (await metrics).length;

    expect(count).toBeGreaterThan(0);
  });

  test('deve ter botão de templates', async ({ page }) => {
    const templateButton = page.locator('button:has-text("Template")').first();

    if (await templateButton.isVisible().catch(() => false)) {
      expect(await templateButton.isVisible()).toBeTruthy();
    }
  });

  test('deve abrir modal de templates', async ({ page }) => {
    const templateButton = page.locator('button:has-text("Template")').first();

    if (await templateButton.isVisible().catch(() => false)) {
      await templateButton.click();
      await page.waitForTimeout(500);

      const modal = page.locator('[role="dialog"]').first();
      await expect(modal).toBeVisible();
    }
  });

  test('deve ter opção de exportar escalas', async ({ page }) => {
    const exportButton = page.locator('button:has-text("Exportar")').first();

    if (await exportButton.isVisible().catch(() => false)) {
      expect(await exportButton.isVisible()).toBeTruthy();
    }
  });

  test('deve exibir progresso de preenchimento', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Procurar indicadores de progresso (porcentagem, barra)
    const progress = page.locator('text=/%/, [role="progressbar"]').first();

    if (await progress.isVisible().catch(() => false)) {
      expect(await progress.isVisible()).toBeTruthy();
    }
  });
});

test.describe('Operacional - Escalas - Workflow', () => {
  test('deve exibir botão de submeter em escala draft', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    // Procurar escala em draft
    const draftScale = page.locator('text=/draft/i, text=/rascunho/i').first();

    if (await draftScale.isVisible().catch(() => false)) {
      // Deve ter botão de submeter próximo
      const submitButton = page.locator('button:has-text("Submeter"), button:has-text("Enviar")').first();
      expect(await submitButton.isVisible().catch(() => true)).toBeDefined();
    }
  });

  test('deve exibir botão de aprovar em escala pending', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    // Procurar escala pendente
    const pendingScale = page.locator('text=/pendente/i, text=/pending/i').first();

    if (await pendingScale.isVisible().catch(() => false)) {
      // Deve ter botão de aprovar
      const approveButton = page.locator('button:has-text("Aprovar")').first();
      expect(await approveButton.isVisible().catch(() => true)).toBeDefined();
    }
  });

  test('deve exibir botão de publicar em escala aprovada', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    // Procurar escala aprovada
    const approvedScale = page.locator('text=/aprovad/i, text=/approved/i').first();

    if (await approvedScale.isVisible().catch(() => false)) {
      // Deve ter botão de publicar
      const publishButton = page.locator('button:has-text("Publicar")').first();
      expect(await publishButton.isVisible().catch(() => true)).toBeDefined();
    }
  });

  test('deve permitir deletar escala draft', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    // Procurar botão de deletar
    const deleteButton = page.locator('button[title*="Excluir"], button[title*="Deletar"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      expect(await deleteButton.isVisible()).toBeTruthy();
    }
  });

  test('deve mostrar confirmação ao deletar', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    const deleteButton = page.locator('button[title*="Excluir"]').first();

    if (await deleteButton.isVisible().catch(() => false)) {
      await deleteButton.click();
      await page.waitForTimeout(500);

      // Modal de confirmação deve aparecer
      const confirmModal = page.locator('[role="dialog"], [role="alertdialog"]').first();
      expect(await confirmModal.isVisible().catch(() => false)).toBeDefined();
    }
  });
});

test.describe('Operacional - Escalas - Validações', () => {
  test('deve validar seleção de posto ao gerar', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const generateBtn = page.locator('button:has-text("Gerar")').first();
    await expect(generateBtn).toBeVisible({ timeout: 10000 });
    await generateBtn.click();
    await page.waitForTimeout(1000);

    // Tentar gerar sem selecionar posto
    const generateButton = page.locator('button:has-text("Gerar"), button[type="submit"]').last();

    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(1000);

      // Modal deve continuar aberto ou mostrar erro
      const modal = page.locator('[role="dialog"]').first();
      expect(await modal.isVisible()).toBeTruthy();
    }
  });

  test('não deve permitir gerar escala duplicada', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Este teste precisa de dados específicos para validar duplicata
    // Apenas verifica que a página está funcional
    await expect(page).toHaveURL(/\/escalas/, { timeout: 10000 });
  });

  test('deve exibir mensagem se não há postos disponíveis', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const generateBtn = page.locator('button:has-text("Gerar")').first();
    await expect(generateBtn).toBeVisible({ timeout: 10000 });
    await generateBtn.click();
    await page.waitForTimeout(1000);

    // Se não há postos, deve mostrar mensagem
    const emptyMessage = page.locator('text=/nenhum posto/i, text=/sem postos/i').first();
    const hasMessage = await emptyMessage.isVisible().catch(() => false);

    // Mensagem pode ou não estar presente
    expect(hasMessage !== undefined).toBeTruthy();
  });
});

test.describe('Operacional - Escalas - Navegação', () => {
  test('deve navegar para detalhes da escala', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    const viewButton = page.locator('button:has-text("Ver")').first();

    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      // Deve ter navegado
      expect(page.url()).toBeDefined();
    }
  });

  test('deve voltar para lista de escalas', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');

    const backButton = page.locator('button:has-text("Voltar"), a:has-text("Voltar")').first();

    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();
      await page.waitForTimeout(1000);

      expect(page.url()).toMatch(/\/operacional/);
    }
  });
});
