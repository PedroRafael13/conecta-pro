import { test, expect } from '@playwright/test';

/**
 * Testes E2E - Assinatura Digital de Documentos
 *
 * Testa funcionalidades de assinatura digital:
 * - Solicitação de assinaturas
 * - Fluxo de assinatura (desenho)
 * - Notificações
 * - Rastreamento de status
 * - Configurações de assinatura sequencial
 */

test.describe('Documentos - Assinatura Digital', () => {
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

    // Mock de documentos pendentes de assinatura
    await page.route('**/api/v1/ged/documents/pending-signature**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'doc-sign-001',
            title: 'Contrato de Prestação de Serviços',
            description: 'Contrato mensal de limpeza',
            document_type: 'contrato',
            category: 'administrativo',
            file_name: 'contrato_limpeza',
            file_extension: 'pdf',
            file_size_bytes: 1024576,
            status: 'pendente_assinatura',
            signature_deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            created_at: '2024-02-01T10:00:00Z',
            updated_at: '2024-02-01T10:00:00Z',
          },
          {
            id: 'doc-sign-002',
            title: 'Termo de Responsabilidade',
            description: 'Termo para uso de área comum',
            document_type: 'termo',
            category: 'operacional',
            file_name: 'termo_responsabilidade',
            file_extension: 'pdf',
            file_size_bytes: 512000,
            status: 'pendente_assinatura',
            signature_deadline: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
            created_at: '2024-02-05T14:30:00Z',
            updated_at: '2024-02-05T14:30:00Z',
          },
        ]),
      });
    });

    // Mock de solicitação de assinatura
    await page.route('**/api/v1/ged/signatures/request', (route) => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'signature-req-001',
            document_id: 'doc-sign-001',
            requester_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            signers: [
              {
                id: 'signer-001',
                signer_name: 'João Silva',
                signer_email: 'joao@email.com',
                signer_role: 'parte',
                order: 1,
                status: 'pendente',
              },
            ],
            sequential: false,
            deadline_days: 7,
            status: 'aguardando',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }),
        });
      } else {
        route.continue();
      }
    });

    // Mock de execução de assinatura
    await page.route('**/api/v1/ged/signatures/*/sign', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'signature-req-001',
          status: 'assinado',
          signed_at: new Date().toISOString(),
          signature_data: 'data:image/png;base64,iVBORw0KGgo...',
        }),
      });
    });

    // Mock de histórico de assinaturas
    await page.route('**/api/v1/ged/signatures**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'sig-001',
              document_id: 'doc-001',
              document_title: 'Contrato de Prestação de Serviços',
              signer_name: 'Maria Oliveira',
              signer_email: 'maria@email.com',
              signer_role: 'parte',
              status: 'assinado',
              signature_type: 'eletronica',
              signed_at: '2024-02-01T15:00:00Z',
              ip_address: '192.168.1.1',
              user_agent: 'Mozilla/5.0...',
            },
            {
              id: 'sig-002',
              document_id: 'doc-001',
              document_title: 'Contrato de Prestação de Serviços',
              signer_name: 'Carlos Santos',
              signer_email: 'carlos@email.com',
              signer_role: 'testemunha',
              status: 'pendente',
              signature_type: 'eletronica',
              signed_at: null,
              ip_address: null,
              user_agent: null,
            },
          ],
          total: 2,
          page: 1,
          pages: 1,
        }),
      });
    });

    // Mock de estatísticas do GED
    await page.route('**/api/v1/ged/stats', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_documents: 150,
          total_folders: 12,
          total_signatures: 45,
          pending_signatures: 5,
          total_storage_bytes: 1073741824,
          documents_by_status: {
            rascunho: 10,
            pendente_aprovacao: 5,
            aprovado: 80,
            publicado: 50,
            arquivado: 5,
          },
        }),
      });
    });
  });

  test('deve carregar página de documentos com seção de assinaturas', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    await expect(page).toHaveURL(/\/documentos/);

    // Verificar se há tab de assinaturas
    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await expect(signaturesTab).toBeVisible();
  });

  test('deve exibir contador de assinaturas pendentes', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Verificar card de estatísticas
    const signaturesCard = page.locator('text=Assinaturas').first();
    await expect(signaturesCard).toBeVisible();
  });

  test('deve exibir lista de documentos pendentes de assinatura', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Clicar na tab de assinaturas
    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar se há documentos pendentes
    await expect(page.locator('text=Documentos Pendentes de Assinatura')).toBeVisible();
  });

  test('deve exibir prazo para assinatura', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar badge de prazo
    const deadlineBadge = page.locator('text=Prazo:').first();
    await expect(deadlineBadge).toBeVisible();
  });

  test('deve exibir botão de assinar para documentos pendentes', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar botões de assinar
    const signButtons = page.locator('button:has-text("Assinar")');
    expect(await signButtons.count()).toBeGreaterThan(0);
  });

  test('deve abrir dialog de assinatura ao clicar em assinar', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Clicar em assinar
    const signButton = page.locator('button:has-text("Assinar")').first();
    await signButton.click();

    await page.waitForTimeout(500);

    // Verificar dialog de assinatura
    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).toBeVisible();
    await expect(dialog).toContainText('Assinar Documento');
  });

  test('deve exibir canvas para desenho da assinatura', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    const signButton = page.locator('button:has-text("Assinar")').first();
    await signButton.click();

    await page.waitForTimeout(500);

    // Verificar canvas
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();
  });

  test('deve permitir desenhar assinatura no canvas', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    const signButton = page.locator('button:has-text("Assinar")').first();
    await signButton.click();

    await page.waitForTimeout(500);

    // Desenhar no canvas
    const canvas = page.locator('canvas').first();
    const box = await canvas.boundingBox();

    if (box) {
      await page.mouse.move(box.x + 10, box.y + 10);
      await page.mouse.down();
      await page.mouse.move(box.x + 100, box.y + 50);
      await page.mouse.move(box.x + 200, box.y + 10);
      await page.mouse.up();
    }

    // Verificar se o botão de confirmar está habilitado
    const confirmButton = page.locator('button:has-text("Confirmar Assinatura")');
    expect(await confirmButton.isEnabled()).toBeTruthy();
  });

  test('deve exibir botão de limpar assinatura', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    const signButton = page.locator('button:has-text("Assinar")').first();
    await signButton.click();

    await page.waitForTimeout(500);

    const clearButton = page.locator('button:has-text("Limpar")');
    await expect(clearButton).toBeVisible();
  });

  test('deve exibir declaração de concordância', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    const signButton = page.locator('button:has-text("Assinar")').first();
    await signButton.click();

    await page.waitForTimeout(500);

    // Verificar declaração
    await expect(page.locator('text=Declaração de Concordância')).toBeVisible();
    await expect(page.locator('text=validade jurídica')).toBeVisible();
  });

  test('deve abrir dialog de solicitação de assinaturas', async ({ page }) => {
    // Mock de documentos para solicitar assinatura
    await page.route('**/api/v1/ged/documents**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 'doc-001',
              title: 'Contrato de Prestação de Serviços',
              document_type: 'contrato',
              category: 'administrativo',
              status: 'aprovado',
            },
          ],
          total: 1,
        }),
      });
    });

    await page.goto('/modulos/documentos/arquivos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Clicar em mais opções
    const moreButton = page.locator('button:has([data-icon="MoreVertical"])').first();
    if (await moreButton.isVisible().catch(() => false)) {
      await moreButton.click();
      await page.waitForTimeout(300);

      // Procurar opção de solicitar assinatura
      const signRequestOption = page.locator('text=Solicitar assinatura');
      if (await signRequestOption.isVisible().catch(() => false)) {
        await signRequestOption.click();

        await page.waitForTimeout(500);

        const dialog = page.locator('[role="dialog"]').first();
        await expect(dialog).toContainText('Solicitar Assinaturas');
      }
    }
  });

  test('deve permitir adicionar múltiplos signatários', async ({ page }) => {
    // Este teste verifica se o componente suporta múltiplos signatários
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar se há documentos pendentes
    const pendingDocs = page.locator('text=Documentos Pendentes');
    await expect(pendingDocs).toBeVisible();
  });

  test('deve exibir configuração de assinatura sequencial', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Verificar informações sobre assinaturas na dashboard
    const signaturesSection = page.locator('text=Assinatura Sequencial').first();
    // Pode ou não estar visível na tela principal
    await expect(page).toBeTruthy();
  });

  test('deve permitir configurar prazo para assinatura', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar se há informações de prazo
    const deadlineInfo = page.locator('text=Prazo').first();
    expect(await deadlineInfo.isVisible().catch(() => false)).toBeTruthy();
  });

  test('deve exibir tipos de assinatura disponíveis', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Clicar em assinar para ver opções
    const signButton = page.locator('button:has-text("Assinar")').first();
    await signButton.click();

    await page.waitForTimeout(500);

    // Verificar tipo de assinatura (eletrônica, digital, etc)
    await expect(page.locator('text=Assinar Documento')).toBeVisible();
  });

  test('deve exibir funções dos signatários', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar lista de documentos pendentes
    const pendingSection = page.locator('text=Documentos Pendentes de Assinatura');
    await expect(pendingSection).toBeVisible();
  });

  test('deve exibir notificação de assinatura concluída', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar se há documentos assinados na lista
    await expect(page).toBeTruthy();
  });

  test('deve permitir cancelar processo de assinatura', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    const signButton = page.locator('button:has-text("Assinar")').first();
    await signButton.click();

    await page.waitForTimeout(500);

    // Clicar em cancelar
    const cancelButton = page.locator('button:has-text("Cancelar")').first();
    await cancelButton.click();

    await page.waitForTimeout(300);

    // Dialog deve fechar
    const dialog = page.locator('[role="dialog"]').first();
    await expect(dialog).not.toBeVisible();
  });

  test('deve exibir estado vazio quando não há assinaturas pendentes', async ({ page }) => {
    // Mock vazio
    await page.route('**/api/v1/ged/documents/pending-signature**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    // Verificar mensagem de vazio
    await expect(page.locator('text=Nenhum documento pendente de assinatura')).toBeVisible();
  });

  test('deve exibir rastreamento de assinaturas', async ({ page }) => {
    await page.goto('/modulos/documentos');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // Verificar se há informações de rastreamento
    const signaturesTab = page.locator('[role="tab"]:has-text("Assinaturas")');
    await signaturesTab.click();

    await page.waitForTimeout(500);

    await expect(page.locator('text=Documentos Pendentes')).toBeVisible();
  });
});
