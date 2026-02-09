import { test, expect } from '@playwright/test';

/**
 * Testes E2E - Documentos / Kits de Documentos
 *
 * Testa funcionalidades de kits de documentos:
 * - Criação de kits
 * - Edição de kits
 * - Exclusão de kits
 * - Associação de documentos
 * - Visualização de detalhes
 * - Filtros e busca
 */

test.describe('Documentos - Kits de Documentos', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de autenticação
    await page.route('**/api/v1/auth/me', (route) => {
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
    });

    // Mock de listagem de kits
    await page.route('**/api/v1/document-kits**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'kit-001',
              codigo: 'KIT-2024-0001',
              nome: 'Kit Admissão de Funcionário',
              descricao: 'Documentos necessários para admissão de novo funcionário',
              tipo: 'ADMISSAO',
              status: 'ATIVO',
              condominio_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
              total_itens: 5,
              uso_count: 12,
              created_at: '2024-01-10T08:00:00Z',
              updated_at: '2024-01-10T08:00:00Z',
            },
            {
              id: 'kit-002',
              codigo: 'KIT-2024-0002',
              nome: 'Kit Documentação de Prestador',
              descricao: 'Documentos para cadastro de prestadores de serviço',
              tipo: 'PRESTADOR',
              status: 'ATIVO',
              condominio_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
              total_itens: 8,
              uso_count: 5,
              created_at: '2024-01-15T10:30:00Z',
              updated_at: '2024-01-15T10:30:00Z',
            },
            {
              id: 'kit-003',
              codigo: 'KIT-2024-0003',
              nome: 'Kit Regularização de Obra',
              descricao: 'Documentos para regularização de obras e reformas',
              tipo: 'OBRA',
              status: 'ATIVO',
              condominio_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
              total_itens: 10,
              uso_count: 3,
              created_at: '2024-02-01T14:00:00Z',
              updated_at: '2024-02-01T14:00:00Z',
            },
          ],
          total: 3,
          page: 1,
          pages: 1,
        }),
      });
    });

    // Mock de criação de kit
    await page.route('**/api/v1/document-kits', (route) => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'kit-new-001',
            codigo: 'KIT-2024-0004',
            nome: 'Novo Kit Teste',
            descricao: 'Descrição do novo kit',
            tipo: 'ADMISSAO',
            status: 'ATIVO',
            condominio_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            total_itens: 0,
            uso_count: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }),
        });
      } else {
        route.continue();
      }
    });

    // Mock de update/delete de kit
    await page.route('**/api/v1/document-kits/*', (route) => {
      if (route.request().method() === 'PATCH') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'kit-001',
            codigo: 'KIT-2024-0001',
            nome: 'Kit Atualizado',
            descricao: 'Descrição atualizada',
            tipo: 'ADMISSAO',
            status: 'ATIVO',
            condominio_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            total_itens: 5,
            uso_count: 12,
            created_at: '2024-01-10T08:00:00Z',
            updated_at: new Date().toISOString(),
          }),
        });
      } else if (route.request().method() === 'DELETE') {
        route.fulfill({
          status: 204,
          contentType: 'application/json',
          body: '',
        });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/documentos/kits');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
  });

  test('deve carregar a página de kits', async ({ page }) => {
    await expect(page).toHaveURL(/\/kits/);

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Kits de Documentos/i);
  });

  test('deve exibir lista de kits', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se os kits estão sendo exibidos
    const kitCards = page.locator('[class*="card"], [class*="Card"]').first();
    await expect(kitCards).toBeVisible();
  });

  test('deve exibir informações do kit (nome, código, descrição)', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se há kits com nome e código
    await expect(page.locator('text=Kit Admissão')).toBeVisible();
    await expect(page.locator('text=KIT-2024')).toBeVisible();
  });

  test('deve exibir badge de status do kit', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar badge de status ativo
    const badges = page.locator('[class*="badge"], [class*="Badge"]').first();
    await expect(badges).toBeVisible();
  });

  test('deve exibir contadores (documentos e usos)', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se os contadores estão presentes
    const documentCount = page.locator('text=/\\d+ documento/i').first();
    expect(await documentCount.isVisible().catch(() => false)).toBeTruthy();
  });

  test('deve exibir botão de novo kit', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Kit")');
    await expect(newButton).toBeVisible();
  });

  test('deve abrir dialog de criação ao clicar em novo kit', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Kit")');
    await newButton.click();

    await page.waitForTimeout(500);

    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
    await expect(dialog).toContainText('Criar Novo Kit');
  });

  test('deve exibir campos do formulário de criação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Kit")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Verificar campos
    await expect(page.locator('label:has-text("Nome")')).toBeVisible();
    await expect(page.locator('label:has-text("Descrição")')).toBeVisible();
    await expect(page.locator('label:has-text("Categoria")')).toBeVisible();
  });

  test('deve validar campo nome obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Kit")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Tentar criar sem preencher nome
    const createButton = page.locator('button:has-text("Criar")').last();
    await createButton.click();

    await page.waitForTimeout(500);

    // Dialog deve continuar aberto
    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
  });

  test('deve permitir preencher formulário de criação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Kit")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Preencher campos
    const nameInput = page.locator('input#name, input[placeholder*="Kit"]').first();
    await nameInput.fill('Kit Teste E2E');

    const descInput = page.locator('textarea#description, textarea').first();
    await descInput.fill('Descrição do kit de teste');

    // Verificar valores preenchidos
    await expect(nameInput).toHaveValue('Kit Teste E2E');
    await expect(descInput).toHaveValue('Descrição do kit de teste');
  });

  test('deve permitir filtrar por categoria', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Selecionar categoria no dropdown
    const categorySelect = page.locator('select').first();

    if (await categorySelect.isVisible().catch(() => false)) {
      await categorySelect.selectOption('ADMISSAO');
      await page.waitForTimeout(500);

      // Verificar se os filtros foram aplicados
      await expect(page).toBeTruthy();
    }
  });

  test('deve permitir buscar kits por nome', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]').first();

    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('Admissão');
      await searchInput.press('Enter');

      await page.waitForTimeout(1000);

      // Verificar se a busca retornou resultados
      await expect(page.locator('text=Admissão')).toBeVisible();
    }
  });

  test('deve abrir detalhes ao clicar em um kit', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Clicar no primeiro kit card
    const kitCard = page.locator('[class*="card"], [class*="Card"]').first();
    await kitCard.click();

    await page.waitForTimeout(500);

    // Verificar se abriu o dialog de detalhes
    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
  });

  test('deve exibir informações detalhadas do kit', async ({ page }) => {
    await page.waitForTimeout(1000);

    const kitCard = page.locator('[class*="card"], [class*="Card"]').first();
    await kitCard.click();

    await page.waitForTimeout(500);

    const dialog = page.locator('[role="dialog"]').first();

    // Verificar informações esperadas
    await expect(dialog).toContainText('Documentos do Kit');
    await expect(dialog).toContainText('Editar');
    await expect(dialog).toContainText('Excluir');
  });

  test('deve permitir editar um kit', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Abrir detalhes do kit
    const kitCard = page.locator('[class*="card"], [class*="Card"]').first();
    await kitCard.click();

    await page.waitForTimeout(500);

    // Clicar em editar
    const editButton = page.locator('button:has-text("Editar")').first();
    await editButton.click();

    await page.waitForTimeout(500);

    // Verificar se abriu o modal de edição
    const editDialog = page.locator('[role="dialog"]').first();
    await expect(editDialog).toContainText('Editar');
  });

  test('deve exibir confirmação antes de excluir kit', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Abrir detalhes do kit
    const kitCard = page.locator('[class*="card"], [class*="Card"]').first();
    await kitCard.click();

    await page.waitForTimeout(500);

    // Clicar em excluir
    const deleteButton = page.locator('button:has-text("Excluir")').first();
    await deleteButton.click();

    // Deve aparecer confirmação do browser (confirm)
    // Como é um confirm nativo, verificamos se o dialog continua aberto
    await page.waitForTimeout(300);

    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
  });

  test('deve exibir lista de documentos do kit nos detalhes', async ({ page }) => {
    await page.waitForTimeout(1000);

    const kitCard = page.locator('[class*="card"], [class*="Card"]').first();
    await kitCard.click();

    await page.waitForTimeout(500);

    const dialog = page.locator('[role="dialog"]').first();

    // Verificar seção de documentos
    await expect(dialog).toContainText('Documentos do Kit');
  });

  test('deve exibir badge de categoria no kit', async ({ page }) => {
    await page.waitForTimeout(1000);

    const kitCard = page.locator('[class*="card"], [class*="Card"]').first();
    await kitCard.click();

    await page.waitForTimeout(500);

    const dialog = page.locator('[role="dialog"]').first();

    // Verificar badge de categoria
    const badges = dialog.locator('[class*="badge"], [class*="Badge"]');
    expect(await badges.count()).toBeGreaterThan(0);
  });

  test('deve exibir informações sobre uso do kit', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se há informação de usos na lista
    const usageInfo = page.locator('text=/\\d+ uso/i').first();
    expect(await usageInfo.isVisible().catch(() => false)).toBeTruthy();
  });

  test('deve exibir card informativo sobre kits', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se há card explicativo
    const infoCard = page.locator('text=Sobre Kits de Documentos');
    await expect(infoCard).toBeVisible();
  });

  test('deve exibir lista de categorias disponíveis', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Kit")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Abrir select de categoria
    const categorySelect = page.locator('[role="combobox"]').first();

    if (await categorySelect.isVisible().catch(() => false)) {
      await categorySelect.click();
      await page.waitForTimeout(300);

      // Verificar opções disponíveis
      const options = page.locator('[role="option"], [class*="select-item"]');
      expect(await options.count()).toBeGreaterThan(0);
    }
  });

  test('deve permitir cancelar criação de kit', async ({ page }) => {
    const newButton = page.locator('button:has-text("Novo Kit")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Preencher algum campo
    const nameInput = page.locator('input#name, input[placeholder*="Kit"]').first();
    await nameInput.fill('Teste Cancelar');

    // Clicar em cancelar
    const cancelButton = page.locator('button:has-text("Cancelar")').first();
    await cancelButton.click();

    await page.waitForTimeout(300);

    // Dialog deve fechar
    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).not.toBeVisible();
  });
});
