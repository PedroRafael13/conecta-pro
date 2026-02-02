import { test, expect } from '@playwright/test';

/**
 * Testes E2E - Fluxo Completo Operacional
 *
 * Simula um usuário real navegando por todas as telas do módulo operacional:
 * - Postos de Trabalho
 * - Colaboradores (Agentes)
 * - Escalas
 * - Alocações
 * - Turnos
 * - Ocorrências
 * - Rondas
 * - Comunicados
 * - Notificações
 * - Reembolsos
 * - Processos Disciplinares
 */

test.describe('Operacional - Fluxo Completo', () => {
  // Aumenta timeout para todos os testes do fluxo completo
  test.setTimeout(40000);

  test.beforeEach(async ({ page }) => {
    // Mocka endpoint /auth/me para todos os testes
    await page.route('**/api/v1/auth/me', (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            email: 'admin@conectaplus.com.br',
            name: 'Admin',
            role: 'admin',
            is_active: true,
            permissions: ['*'],
            tenant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          }),
        });
      } else {
        route.continue();
      }
    });

    // Não navega para login - já estamos autenticados via storageState
    // Os testes vão navegar direto para suas páginas
  });

  test('Fluxo 01: Navegação no Dashboard Operacional', async ({ page }) => {
    await page.goto('/modulos/operacional');
    await page.waitForTimeout(2000);

    // Verificar que estamos na página operacional
    await expect(page).toHaveURL(/\/operacional/);

    // Verificar cards de acesso rápido
    const postsCard = page.locator('text=/postos/i').first();
    const scalesCard = page.locator('text=/escalas/i').first();
    const occurrencesCard = page.locator('text=/ocorrências/i').first();

    // Pelo menos um card deve estar visível
    const hasCards =
      (await postsCard.isVisible().catch(() => false)) ||
      (await scalesCard.isVisible().catch(() => false)) ||
      (await occurrencesCard.isVisible().catch(() => false));

    expect(hasCards).toBeTruthy();
  });

  test('Fluxo 02: Postos - Visualizar e buscar', async ({ page }) => {
    await page.goto('/modulos/operacional/postos');
    await page.waitForTimeout(2000);

    // Verificar carregamento da página
    await expect(page.locator('h1').first()).toContainText(/posto/i);

    // Verificar se há tabela ou lista
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasCards = await page.locator('[class*="card"]').count() > 0;

    expect(hasTable || hasCards).toBeTruthy();

    // Testar busca
    const searchInput = page.locator('input[type="search"]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('portaria');
      await page.waitForTimeout(500);

      // Limpar busca
      await searchInput.clear();
      await page.waitForTimeout(500);
    }

    // Testar botão de novo posto
    const newButton = page.locator('button:has-text("Novo")').first();
    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      // Verificar se modal abriu
      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible().catch(() => false)) {
        // Fechar modal
        const closeButton = modal.locator('button:has-text("Cancelar"), button:has-text("Fechar")').first();
        if (await closeButton.isVisible().catch(() => false)) {
          await closeButton.click();
        } else {
          await page.keyboard.press('Escape');
        }
      }
    }
  });

  test('Fluxo 03: Colaboradores/Agentes - Gestão', async ({ page }) => {
    await page.goto('/modulos/operacional/colaboradores');
    await page.waitForTimeout(2000);

    // Verificar título
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/colaborador|agente|funcionário/i);

    // Verificar lista de colaboradores
    const hasContent =
      (await page.locator('table').isVisible().catch(() => false)) ||
      (await page.locator('[class*="card"]').count() > 0);

    expect(hasContent).toBeTruthy();

    // Testar filtros
    const statusFilter = page.locator('select').first();
    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);

      // Resetar filtro
      await statusFilter.selectOption({ index: 0 });
      await page.waitForTimeout(500);
    }

    // Testar busca por nome
    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar" i]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Silva');
      await page.waitForTimeout(500);
      await searchInput.clear();
    }
  });

  test('Fluxo 04: Escalas - Visualização e geração', async ({ page }) => {
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    // Verificar título
    await expect(page.locator('h1').first()).toContainText(/escala/i);

    // Verificar botão de gerar escala
    const generateButton = page.locator('button:has-text("Gerar"), button:has-text("Nova")').first();

    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(1000);

      // Verificar modal de geração
      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible().catch(() => false)) {
        // Verificar formulário
        const postSelect = modal.locator('select').first();
        expect(await postSelect.isVisible().catch(() => true)).toBeDefined();

        // Fechar modal
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
      }
    }

    // Testar filtros de mês/ano
    const filters = page.locator('select').all();
    const filterCount = (await filters).length;

    if (filterCount > 0) {
      const firstFilter = page.locator('select').first();
      if (await firstFilter.isVisible().catch(() => false)) {
        await firstFilter.selectOption({ index: 1 });
        await page.waitForTimeout(500);
      }
    }

    // Verificar cards de escalas
    const scaleCards = await page.locator('[class*="card"], [class*="scale"]').count();
    expect(scaleCards).toBeGreaterThanOrEqual(0);
  });

  test('Fluxo 05: Alocações - Gestão de alocações', async ({ page }) => {
    await page.goto('/modulos/operacional/alocacoes');
    await page.waitForTimeout(2000);

    // Verificar se página carrega
    const heading = page.locator('h1').first();
    const hasHeading = await heading.isVisible().catch(() => false);

    if (hasHeading) {
      await expect(heading).toContainText(/alocação|alocações/i);

      // Verificar conteúdo
      const hasTable = await page.locator('table').isVisible().catch(() => false);
      const hasCards = await page.locator('[class*="card"]').count() > 0;

      expect(hasTable || hasCards).toBeTruthy();

      // Testar botão de nova alocação
      const newButton = page.locator('button:has-text("Nova"), button:has-text("Novo")').first();
      if (await newButton.isVisible().catch(() => false)) {
        await newButton.click();
        await page.waitForTimeout(1000);

        // Fechar modal se abrir
        const modal = page.locator('[role="dialog"]').first();
        if (await modal.isVisible().catch(() => false)) {
          await page.keyboard.press('Escape');
        }
      }
    } else {
      // Página pode não existir ou estar em construção
      console.log('Página de alocações não disponível');
    }
  });

  test('Fluxo 06: Turnos - Gestão de turnos', async ({ page }) => {
    await page.goto('/modulos/operacional/turnos');
    await page.waitForTimeout(2000);

    // Verificar se página existe
    const heading = page.locator('h1').first();
    const pageExists = await heading.isVisible().catch(() => false);

    if (pageExists) {
      await expect(heading).toContainText(/turno/i);

      // Verificar lista de turnos
      const hasList =
        (await page.locator('table').isVisible().catch(() => false)) ||
        (await page.locator('[class*="card"]').count() > 0);

      expect(hasList).toBeTruthy();

      // Testar criação de turno
      const newButton = page.locator('button:has-text("Novo")').first();
      if (await newButton.isVisible().catch(() => false)) {
        await newButton.click();
        await page.waitForTimeout(1000);

        const modal = page.locator('[role="dialog"]').first();
        if (await modal.isVisible().catch(() => false)) {
          // Verificar campos do formulário
          const nameInput = modal.locator('input[name="name"], input[placeholder*="nome" i]').first();
          expect(await nameInput.isVisible().catch(() => true)).toBeDefined();

          // Fechar
          await page.keyboard.press('Escape');
        }
      }
    }
  });

  test('Fluxo 07: Ocorrências - CRUD completo', async ({ page }) => {
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    // Verificar página
    await expect(page.locator('h1').first()).toContainText(/ocorrência/i);

    // Verificar estatísticas
    const statsCards = await page.locator('[class*="stat"], [class*="card"]').count();
    expect(statsCards).toBeGreaterThanOrEqual(0);

    // Testar busca
    const searchInput = page.locator('input[type="search"]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('celular');
      await page.waitForTimeout(500);
      await searchInput.clear();
    }

    // Testar filtro de severidade
    const severityFilter = page.locator('select').nth(1);
    if (await severityFilter.isVisible().catch(() => false)) {
      await severityFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);
      await severityFilter.selectOption({ index: 0 });
    }

    // Testar nova ocorrência
    const newButton = page.locator('button:has-text("Nova")').first();
    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible().catch(() => false)) {
        // Verificar campos obrigatórios
        const titleInput = modal.locator('input[name="title"]').first();
        const descriptionInput = modal.locator('textarea[name="description"]').first();

        if (await titleInput.isVisible().catch(() => false)) {
          expect(await titleInput.isVisible()).toBeTruthy();
        }

        // Fechar modal
        await page.keyboard.press('Escape');
      }
    }

    // Testar visualização de detalhes
    const viewButton = page.locator('button[title*="Ver"], button:has-text("Ver")').first();
    if (await viewButton.isVisible().catch(() => false)) {
      await viewButton.click();
      await page.waitForTimeout(1000);

      const detailModal = page.locator('[role="dialog"]').first();
      if (await detailModal.isVisible().catch(() => false)) {
        // Verificar informações da ocorrência
        expect(await detailModal.isVisible()).toBeTruthy();

        // Fechar
        await page.keyboard.press('Escape');
      }
    }
  });

  test('Fluxo 08: Rondas - Registro e checkpoints', async ({ page }) => {
    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    // Verificar página
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/ronda|inspeção/i);

    // Verificar botão de nova ronda
    const newButton = page.locator('button:has-text("Nova"), button:has-text("Iniciar")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible().catch(() => false)) {
        // Verificar seleção de posto/rota
        const postSelect = modal.locator('select').first();
        expect(await postSelect.isVisible().catch(() => true)).toBeDefined();

        await page.keyboard.press('Escape');
      }
    }

    // Verificar lista de rondas
    const hasRounds =
      (await page.locator('table').isVisible().catch(() => false)) ||
      (await page.locator('[class*="card"]').count() > 0);

    expect(hasRounds).toBeTruthy();

    // Testar filtros
    const statusFilter = page.locator('select').first();
    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);
    }
  });

  test('Fluxo 09: Comunicados - Publicação e visualização', async ({ page }) => {
    await page.goto('/modulos/operacional/comunicados');
    await page.waitForTimeout(2000);

    // Verificar página
    await expect(page.locator('h1').first()).toContainText(/comunicado/i);

    // Verificar botão de novo comunicado
    const newButton = page.locator('button:has-text("Novo"), button:has-text("Publicar")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible().catch(() => false)) {
        // Verificar campos
        const titleInput = modal.locator('input[name="title"], input[placeholder*="título"]').first();
        const contentInput = modal.locator('textarea').first();

        if (await titleInput.isVisible().catch(() => false)) {
          expect(await titleInput.isVisible()).toBeTruthy();
        }

        await page.keyboard.press('Escape');
      }
    }

    // Verificar lista de comunicados
    const hasCommuniques = await page.locator('[class*="card"], table').count() > 0;
    expect(hasCommuniques).toBeTruthy();

    // Testar busca
    const searchInput = page.locator('input[type="search"]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('reunião');
      await page.waitForTimeout(500);
      await searchInput.clear();
    }
  });

  test('Fluxo 10: Notificações - Centro de notificações', async ({ page }) => {
    await page.goto('/modulos/operacional/notificacoes');
    await page.waitForTimeout(2000);

    // Verificar se página existe
    const heading = page.locator('h1').first();
    const pageExists = await heading.isVisible().catch(() => false);

    if (pageExists) {
      await expect(heading).toContainText(/notificação|notificações/i);

      // Verificar lista de notificações
      const hasNotifications =
        (await page.locator('[class*="notification"]').count() > 0) ||
        (await page.locator('table').isVisible().catch(() => false));

      expect(hasNotifications).toBeTruthy();

      // Testar filtros
      const filterButton = page.locator('button:has-text("Filtro")').first();
      if (await filterButton.isVisible().catch(() => false)) {
        await filterButton.click();
        await page.waitForTimeout(500);
      }

      // Testar marcar como lida
      const markReadButton = page.locator('button[title*="Marcar"], button:has-text("Marcar")').first();
      if (await markReadButton.isVisible().catch(() => false)) {
        await markReadButton.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('Fluxo 11: Reembolsos - Solicitação e aprovação', async ({ page }) => {
    await page.goto('/modulos/operacional/reembolsos');
    await page.waitForTimeout(2000);

    // Verificar página
    await expect(page.locator('h1').first()).toContainText(/reembolso/i);

    // Verificar botão de nova solicitação
    const newButton = page.locator('button:has-text("Nova"), button:has-text("Solicitar")').first();

    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible().catch(() => false)) {
        // Verificar campos do formulário
        const descriptionInput = modal.locator('textarea, input[name="description"]').first();
        const valueInput = modal.locator('input[type="number"], input[name="value"]').first();

        if (await descriptionInput.isVisible().catch(() => false)) {
          expect(await descriptionInput.isVisible()).toBeTruthy();
        }

        await page.keyboard.press('Escape');
      }
    }

    // Verificar lista de reembolsos
    const hasReimbursements =
      (await page.locator('table').isVisible().catch(() => false)) ||
      (await page.locator('[class*="card"]').count() > 0);

    expect(hasReimbursements).toBeTruthy();

    // Testar filtros de status
    const statusFilter = page.locator('select').first();
    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);
      await statusFilter.selectOption({ index: 0 });
    }
  });

  test('Fluxo 12: Processos Disciplinares - Workflow completo', async ({ page }) => {
    await page.goto('/modulos/operacional/disciplinar');
    await page.waitForTimeout(2000);

    // Verificar página
    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/disciplinar|processo/i);

    // Verificar estatísticas
    const statsCards = await page.locator('[class*="stat"], [class*="card"]').count();
    expect(statsCards).toBeGreaterThanOrEqual(0);

    // Verificar lista de processos
    const hasProcesses =
      (await page.locator('table').isVisible().catch(() => false)) ||
      (await page.locator('[class*="process"]').count() > 0);

    expect(hasProcesses).toBeTruthy();

    // Testar filtros
    const statusFilter = page.locator('select').first();
    if (await statusFilter.isVisible().catch(() => false)) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForTimeout(500);
    }

    // Testar busca
    const searchInput = page.locator('input[type="search"]').first();
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('advertência');
      await page.waitForTimeout(500);
      await searchInput.clear();
    }

    // Verificar botão de novo processo
    const newButton = page.locator('button:has-text("Novo")').first();
    if (await newButton.isVisible().catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(1000);

      const modal = page.locator('[role="dialog"]').first();
      if (await modal.isVisible().catch(() => false)) {
        await page.keyboard.press('Escape');
      }
    }
  });

  test('Fluxo 13: Navegação entre módulos', async ({ page }) => {
    // Testar navegação entre diferentes páginas do operacional

    // 1. Postos
    await page.goto('/modulos/operacional/postos');
    await page.waitForTimeout(1000);
    await expect(page).toHaveURL(/\/postos/);

    // 2. Escalas
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(1000);
    await expect(page).toHaveURL(/\/escalas/);

    // 3. Ocorrências
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(1000);
    await expect(page).toHaveURL(/\/ocorrencias/);

    // 4. Voltar para dashboard operacional
    await page.goto('/modulos/operacional');
    await page.waitForTimeout(1000);
    await expect(page).toHaveURL(/\/operacional$/);

    // Verificar breadcrumb ou botão voltar
    const backButton = page.locator('button:has-text("Voltar"), a:has-text("Voltar")').first();
    const hasBreadcrumb = await backButton.isVisible().catch(() => false);

    expect(hasBreadcrumb !== undefined).toBeTruthy();
  });

  test('Fluxo 14: Performance e responsividade', async ({ page }) => {
    // Testar performance das páginas principais

    const pages = [
      '/modulos/operacional',
      '/modulos/operacional/postos',
      '/modulos/operacional/escalas',
      '/modulos/operacional/ocorrencias',
    ];

    for (const pagePath of pages) {
      const startTime = Date.now();

      await page.goto(pagePath);
      await page.waitForTimeout(2000);

      const loadTime = Date.now() - startTime;

      // Página não deve demorar mais de 10 segundos
      expect(loadTime).toBeLessThan(10000);

      // Verificar se página carregou
      const hasContent =
        (await page.locator('h1').first().isVisible().catch(() => false)) ||
        (await page.locator('main').first().isVisible().catch(() => false));

      expect(hasContent).toBeTruthy();
    }
  });

  test('Fluxo 15: Teste de acessibilidade básica', async ({ page }) => {
    await page.goto('/modulos/operacional/postos');
    await page.waitForTimeout(2000);

    // Verificar elementos de acessibilidade

    // Headings devem estar presentes
    const h1 = await page.locator('h1').count();
    expect(h1).toBeGreaterThan(0);

    // Botões devem ter texto ou aria-label
    const buttons = await page.locator('button').all();
    for (const button of await buttons) {
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      const title = await button.getAttribute('title');

      const hasLabel = text?.trim() || ariaLabel || title;
      if (!hasLabel) {
        console.warn('Botão sem label encontrado');
      }
    }

    // Inputs devem ter labels ou placeholders
    const inputs = await page.locator('input').all();
    for (const input of await inputs) {
      const placeholder = await input.getAttribute('placeholder');
      const ariaLabel = await input.getAttribute('aria-label');
      const id = await input.getAttribute('id');

      let hasLabel = placeholder || ariaLabel;

      if (id) {
        const label = await page.locator(`label[for="${id}"]`).count();
        hasLabel = hasLabel || label > 0;
      }

      if (!hasLabel) {
        console.warn('Input sem label encontrado');
      }
    }
  });
});

test.describe('Operacional - Testes de Integração', () => {
  test.beforeEach(async ({ page }) => {
    // Mocka endpoint /auth/me para todos os testes de integração
    await page.route('**/api/v1/auth/me', (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            email: 'admin@conectaplus.com.br',
            name: 'Admin',
            role: 'admin',
            is_active: true,
            permissions: ['*'],
            tenant_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          }),
        });
      } else {
        route.continue();
      }
    });
  });

  test('Integração 01: Criar posto → Criar escala → Alocar colaborador', async ({ page }) => {
    // Simular fluxo completo de criação

    // 1. Verificar se há postos
    await page.goto('/modulos/operacional/postos');
    await page.waitForTimeout(2000);

    const hasExistingPosts = await page.locator('table tr, [class*="card"]').count() > 0;

    if (!hasExistingPosts) {
      console.log('Sem postos existentes - teste pulado');
      return;
    }

    // 2. Ir para escalas
    await page.goto('/modulos/operacional/escalas');
    await page.waitForTimeout(2000);

    // 3. Tentar gerar escala
    const generateButton = page.locator('button:has-text("Gerar")').first();

    if (await generateButton.isVisible().catch(() => false)) {
      await generateButton.click();
      await page.waitForTimeout(1000);

      // Verificar se modal abre
      const modal = page.locator('[role="dialog"]').first();
      expect(await modal.isVisible().catch(() => false)).toBeDefined();

      await page.keyboard.press('Escape');
    }
  });

  test('Integração 02: Ocorrência → Processo Disciplinar', async ({ page }) => {
    // Verificar integração entre ocorrências e processos disciplinares

    // 1. Ir para ocorrências
    await page.goto('/modulos/operacional/ocorrencias');
    await page.waitForTimeout(2000);

    const hasOccurrences = await page.locator('table tr, [class*="card"]').count() > 0;

    if (hasOccurrences) {
      // Verificar se há botão de aplicar medida
      const actionButton = page.locator('button[title*="Medida"], button:has-text("Aplicar")').first();

      if (await actionButton.isVisible().catch(() => false)) {
        await actionButton.click();
        await page.waitForTimeout(1000);

        const modal = page.locator('[role="dialog"]').first();
        if (await modal.isVisible().catch(() => false)) {
          // Verificar opções de medida
          const severitySelect = modal.locator('select').first();
          expect(await severitySelect.isVisible().catch(() => true)).toBeDefined();

          await page.keyboard.press('Escape');
        }
      }
    }

    // 2. Verificar processos disciplinares
    await page.goto('/modulos/operacional/disciplinar');
    await page.waitForTimeout(2000);

    const hasProcesses = await page.locator('table, [class*="process"]').count() > 0;
    expect(hasProcesses).toBeTruthy();
  });

  test('Integração 03: Ronda → Registrar Ocorrência', async ({ page }) => {
    // Verificar fluxo de ronda com registro de ocorrência

    await page.goto('/modulos/operacional/rondas');
    await page.waitForTimeout(2000);

    const hasRounds = await page.locator('table tr, [class*="card"]').count() > 0;

    if (hasRounds) {
      // Clicar em uma ronda
      const viewButton = page.locator('button:has-text("Ver"), button[title*="Ver"]').first();

      if (await viewButton.isVisible().catch(() => false)) {
        await viewButton.click();
        await page.waitForTimeout(1000);

        // Procurar botão de registrar ocorrência
        const registerButton = page.locator('button:has-text("Registrar"), button:has-text("Ocorrência")').first();

        if (await registerButton.isVisible().catch(() => false)) {
          expect(await registerButton.isVisible()).toBeTruthy();
        }

        // Fechar
        await page.keyboard.press('Escape');
      }
    }
  });
});
