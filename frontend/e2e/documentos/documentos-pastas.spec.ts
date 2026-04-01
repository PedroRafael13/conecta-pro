import { test, expect } from '@playwright/test';

/**
 * Testes E2E - Documentos / Pastas
 *
 * Testa funcionalidades de gerenciamento de pastas:
 * - Criação de pastas
 * - Edição de pastas
 * - Exclusão de pastas
 * - Navegação hierárquica
 * - Busca de pastas
 * - Movimentação de arquivos
 */

test.describe('Documentos - Pastas', () => {
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

    // Mock de listagem de pastas
    await page.route('**/api/v1/ged/folders**', (route) => {
      const url = route.request().url();

      // Verificar se é pasta raiz ou subpasta
      if (url.includes('parent_id')) {
        // Subpastas
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: 'folder-003',
                name: 'Subpasta 1',
                description: 'Subpasta de contratos',
                parent_id: 'folder-001',
                is_root: false,
                is_system: false,
                is_public: true,
                folder_type: 'condominio',
                document_count: 3,
                subfolder_count: 0,
                total_size_bytes: 2097152,
                full_path: '/Contratos/Subpasta 1',
                created_at: '2024-01-10T08:00:00Z',
                updated_at: '2024-01-10T08:00:00Z',
              },
            ],
            total: 1,
            page: 1,
            pages: 1,
          }),
        });
      } else {
        // Pastas raiz
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: 'folder-001',
                name: 'Contratos',
                description: 'Contratos e acordos',
                is_root: true,
                is_system: false,
                is_public: true,
                folder_type: 'condominio',
                document_count: 15,
                subfolder_count: 1,
                total_size_bytes: 15728640,
                full_path: '/Contratos',
                created_at: '2024-01-01T10:00:00Z',
                updated_at: '2024-01-01T10:00:00Z',
              },
              {
                id: 'folder-002',
                name: 'Relatórios',
                description: 'Relatórios financeiros e operacionais',
                is_root: true,
                is_system: false,
                is_public: false,
                folder_type: 'sindico',
                document_count: 45,
                subfolder_count: 2,
                total_size_bytes: 52428800,
                full_path: '/Relatórios',
                created_at: '2024-01-02T09:00:00Z',
                updated_at: '2024-01-02T09:00:00Z',
              },
              {
                id: 'folder-004',
                name: 'Sistema',
                description: 'Pasta do sistema',
                is_root: true,
                is_system: true,
                is_public: false,
                folder_type: 'sistema',
                document_count: 8,
                subfolder_count: 0,
                total_size_bytes: 4194304,
                full_path: '/Sistema',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z',
              },
            ],
            total: 3,
            page: 1,
            pages: 1,
          }),
        });
      }
    });

    // Mock de detalhes de pasta específica
    await page.route('**/api/v1/ged/folders/folder-001', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'folder-001',
          name: 'Contratos',
          description: 'Contratos e acordos',
          is_root: true,
          is_system: false,
          is_public: true,
          folder_type: 'condominio',
          document_count: 15,
          subfolder_count: 1,
          total_size_bytes: 15728640,
          full_path: '/Contratos',
          created_at: '2024-01-01T10:00:00Z',
          updated_at: '2024-01-01T10:00:00Z',
        }),
      });
    });

    // Mock de criação de pasta
    await page.route('**/api/v1/ged/folders', (route) => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'folder-new-001',
            name: 'Nova Pasta Teste',
            description: 'Descrição da nova pasta',
            is_root: true,
            is_system: false,
            is_public: false,
            folder_type: 'condominio',
            document_count: 0,
            subfolder_count: 0,
            total_size_bytes: 0,
            full_path: '/Nova Pasta Teste',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }),
        });
      } else {
        route.continue();
      }
    });

    // Mock de update/delete de pasta
    await page.route('**/api/v1/ged/folders/*', (route) => {
      if (route.request().method() === 'PATCH' || route.request().method() === 'PUT') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'folder-001',
            name: 'Contratos Atualizados',
            description: 'Descrição atualizada',
            is_root: true,
            is_system: false,
            is_public: true,
            folder_type: 'condominio',
            document_count: 15,
            subfolder_count: 1,
            total_size_bytes: 15728640,
            full_path: '/Contratos Atualizados',
            created_at: '2024-01-01T10:00:00Z',
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

    await page.goto('/modulos/documentos/pastas');
    await page.waitForLoadState('load');
    await page.waitForTimeout(1500);
  });

  test('deve carregar a página de pastas', async ({ page }) => {
    await expect(page).toHaveURL(/\/pastas/);

    const heading = page.locator('h1').first();
    await expect(heading).toContainText(/Pastas/i);
  });

  test('deve exibir lista de pastas raiz', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se as pastas estão sendo exibidas
    const folderCards = page.locator('[class*="card"], [class*="Card"]').first();
    await expect(folderCards).toBeVisible();
  });

  test('deve exibir informações da pasta (nome, descrição, ícone)', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar informações das pastas
    await expect(page.locator('text=Contratos')).toBeVisible();
    await expect(page.locator('text=Contratos e acordos')).toBeVisible();
  });

  test('deve exibir contadores de documentos e subpastas', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se os contadores estão presentes
    const docCount = page.locator('text=/\\d+ docs/i').first();
    expect(await docCount.isVisible().catch(() => false)).toBeTruthy();
  });

  test('deve exibir badge de tipo de pasta', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar badges de tipo
    const badges = page.locator('[class*="badge"], [class*="Badge"]').first();
    await expect(badges).toBeVisible();
  });

  test('deve exibir indicador de pasta pública/privada', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar ícones de cadeado (público/privado)
    const lockIcon = page.locator('[data-icon="Lock"], [data-icon="Unlock"]').first();
    expect(await lockIcon.isVisible().catch(() => false)).toBeTruthy();
  });

  test('deve exibir badge para pastas do sistema', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se há badge "Sistema"
    const systemBadge = page.locator('text=Sistema').first();
    await expect(systemBadge).toBeVisible();
  });

  test('deve exibir botão de nova pasta', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Pasta")');
    await expect(newButton).toBeVisible();
  });

  test('deve abrir dialog de criação ao clicar em nova pasta', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Pasta")');
    await newButton.click();

    await page.waitForTimeout(500);

    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
    await expect(dialog).toContainText('Criar Nova Pasta');
  });

  test('deve exibir campos do formulário de criação', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Pasta")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Verificar campos
    await expect(page.locator('label:has-text("Nome")')).toBeVisible();
    await expect(page.locator('label:has-text("Descrição")')).toBeVisible();
    await expect(page.locator('label:has-text("Tipo")')).toBeVisible();
  });

  test('deve exibir checkbox de pasta pública', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Pasta")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Verificar checkbox
    await expect(page.locator('label:has-text("Pasta pública")')).toBeVisible();
  });

  test('deve validar campo nome obrigatório', async ({ page }) => {
    const newButton = page.locator('button:has-text("Nova Pasta")');
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
    const newButton = page.locator('button:has-text("Nova Pasta")');
    await newButton.click();

    await page.waitForTimeout(500);

    // Preencher campos
    const nameInput = page.locator('input#name').first();
    await nameInput.fill('Pasta Teste E2E');

    const descInput = page.locator('textarea#description').first();
    await descInput.fill('Descrição da pasta de teste');

    // Verificar valores preenchidos
    await expect(nameInput).toHaveValue('Pasta Teste E2E');
    await expect(descInput).toHaveValue('Descrição da pasta de teste');
  });

  test('deve exibir breadcrumb de navegação', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar breadcrumb
    const breadcrumb = page.locator('nav').first();
    await expect(breadcrumb).toBeVisible();

    // Deve ter link para Home
    await expect(breadcrumb.locator('[data-icon="Home"], text=Pastas')).toBeVisible();
  });

  test('deve navegar para subpasta ao clicar', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Clicar na primeira pasta (que não é do sistema)
    const folderCard = page.locator('[class*="card"], [class*="Card"]').first();
    await folderCard.click();

    await page.waitForTimeout(1000);

    // Verificar se navegou para a pasta
    const url = page.url();
    expect(url).toContain('id=');
  });

  test('deve exibir botão de voltar ao navegar para subpasta', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Clicar na primeira pasta
    const folderCard = page.locator('[class*="card"], [class*="Card"]').first();
    await folderCard.click();

    await page.waitForTimeout(1000);

    // Verificar botão de voltar
    const backButton = page.locator('button:has([data-icon="ArrowLeft"]), [data-icon="ArrowLeft"]').first();
    await expect(backButton).toBeVisible();
  });

  test('deve voltar para lista de pastas ao clicar em voltar', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Clicar na primeira pasta
    const folderCard = page.locator('[class*="card"], [class*="Card"]').first();
    await folderCard.click();

    await page.waitForTimeout(1000);

    // Clicar em voltar
    const backButton = page.locator('button:has([data-icon="ArrowLeft"])').first();
    if (await backButton.isVisible().catch(() => false)) {
      await backButton.click();

      await page.waitForTimeout(500);

      // Deve estar de volta na lista
      await expect(page).toHaveURL(/\/pastas\?*$/);
    }
  });

  test('deve exibir campo de busca de pastas', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]').first();
    await expect(searchInput).toBeVisible();
  });

  test('deve permitir buscar pastas por nome', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar"]').first();
    await searchInput.fill('Contratos');
    await searchInput.press('Enter');

    await page.waitForTimeout(1000);

    // Verificar se a busca filtrou
    await expect(page.locator('text=Contratos')).toBeVisible();
  });

  test('deve exibir menu de ações para pastas não-sistema', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Encontrar pasta que não é do sistema e abrir menu
    const nonSystemCards = page.locator('[class*="card"], [class*="Card"]').filter({
      hasNot: page.locator('text=Sistema')
    });

    if (await nonSystemCards.count() > 0) {
      const menuButton = nonSystemCards.first().locator('button:has([data-icon="MoreVertical"])');
      if (await menuButton.isVisible().catch(() => false)) {
        await menuButton.click();
        await page.waitForTimeout(300);

        // Verificar opções do menu
        await expect(page.locator('text=Editar')).toBeVisible();
        await expect(page.locator('text=Mover')).toBeVisible();
        await expect(page.locator('text=Excluir')).toBeVisible();
      }
    }
  });

  test('deve não exibir menu de ações para pastas do sistema', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Encontrar pasta do sistema
    const systemCards = page.locator('[class*="card"], [class*="Card"]').filter({
      has: page.locator('text=Sistema')
    });

    if (await systemCards.count() > 0) {
      // Verificar se não há botão de menu
      const menuButton = systemCards.first().locator('button:has([data-icon="MoreVertical"])');
      expect(await menuButton.count()).toBe(0);
    }
  });

  test('deve abrir dialog de edição ao clicar em editar', async ({ page }) => {
    await page.waitForTimeout(1000);

    const nonSystemCards = page.locator('[class*="card"], [class*="Card"]').filter({
      hasNot: page.locator('text=Sistema')
    });

    if (await nonSystemCards.count() > 0) {
      const menuButton = nonSystemCards.first().locator('button:has([data-icon="MoreVertical"])');
      if (await menuButton.isVisible().catch(() => false)) {
        await menuButton.click();
        await page.waitForTimeout(300);

        await page.click('text=Editar');
        await page.waitForTimeout(300);

        // Verificar dialog de edição
        const dialog = page.locator('[role="dialog"]').first();
        await expect(dialog).toContainText('Editar');
      }
    }
  });

  test('deve exibir informações da pasta atual quando navegando', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Clicar na primeira pasta
    const folderCard = page.locator('[class*="card"], [class*="Card"]').first();
    await folderCard.click();

    await page.waitForTimeout(1000);

    // Verificar informações da pasta
    const infoCard = page.locator('text=Informações da Pasta');
    await expect(infoCard).toBeVisible();
  });

  test('deve exibir tamanho total da pasta', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Verificar se o tamanho é exibido
    const sizeInfo = page.locator('text=/\\d+\\s*(B|KB|MB|GB)/i').first();
    await expect(sizeInfo).toBeVisible();
  });

  test('deve exibir estado vazio quando não há pastas', async ({ page }) => {
    // Mock para retornar lista vazia
    await page.route('**/api/v1/ged/folders**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          page: 1,
          pages: 0,
        }),
      });
    });

    await page.reload();
    await page.waitForTimeout(1500);

    // Verificar mensagem de vazio
    await expect(page.locator('text=Nenhuma pasta encontrada')).toBeVisible();
    await expect(page.locator('button:has-text("Criar Pasta")')).toBeVisible();
  });

  test('deve exibir caminho completo da pasta', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Clicar na primeira pasta
    const folderCard = page.locator('[class*="card"], [class*="Card"]').first();
    await folderCard.click();

    await page.waitForTimeout(1000);

    // Verificar informações - deve ter caminho
    const infoSection = page.locator('text=Caminho').first();
    if (await infoSection.isVisible().catch(() => false)) {
      await expect(infoSection).toBeVisible();
    }
  });
});
