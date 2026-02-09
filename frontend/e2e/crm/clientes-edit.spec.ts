/**
 * Testes E2E - Clientes - Edição
 *
 * Testes para edição de clientes existentes no CRM
 * cobrindo: abertura de modal, preenchimento de dados, atualização e exclusão
 */

import { test, expect } from '../fixtures';

const mockClient = {
  id: 'client-123',
  nome: 'Condomínio Edifício Teste',
  cnpj: '12.345.678/0001-90',
  email: 'contato@teste.com.br',
  telefone: '(11) 3333-4444',
  tipo: 'condominio',
  status: 'active',
  endereco: 'Rua Original, 100 - São Paulo/SP',
  created_at: '2024-01-15T10:00:00Z',
};

test.describe('CRM - Clientes - Edição', () => {
  test.beforeEach(async ({ page }) => {
    // Mock do endpoint de clientes
    await page.route('**/api/v1/clients*', (route) => {
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [mockClient],
            total: 1,
            skip: 0,
            limit: 20,
          }),
        });
      } else {
        route.continue();
      }
    });

    // Mock do endpoint de atualização
    await page.route('**/api/v1/clients/client-123', (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        const body = route.request().postDataJSON();
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            ...mockClient,
            ...body,
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

    await page.goto('/modulos/crm/clientes', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve abrir modal de edição ao clicar em editar', async ({ page }) => {
    // Abrir menu de ações
    const menuButton = page.locator('button').filter({ has: page.locator('svg') }).first();
    await menuButton.click();
    await page.waitForTimeout(300);

    // Clicar em Editar
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    // Verificar que o modal abriu com título correto
    await expect(page.locator('[role="dialog"]')).toBeVisible();
    await expect(page.locator('text=Editar Cliente')).toBeVisible();
  });

  test('deve preencher formulário com dados do cliente ao editar', async ({ page }) => {
    // Abrir menu e clicar em editar
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    // Verificar que os campos estão preenchidos com os dados do cliente
    await expect(page.locator('input#nome')).toHaveValue('Condomínio Edifício Teste');
    await expect(page.locator('input#cnpj')).toHaveValue('12.345.678/0001-90');
    await expect(page.locator('input#email')).toHaveValue('contato@teste.com.br');
    await expect(page.locator('input#telefone')).toHaveValue('(11) 3333-4444');
    await expect(page.locator('input#endereco')).toHaveValue('Rua Original, 100 - São Paulo/SP');
  });

  test('deve permitir alterar dados do cliente', async ({ page }) => {
    let requestBody: any = null;

    // Interceptar request
    await page.route('**/api/v1/clients/client-123', (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        requestBody = route.request().postDataJSON();
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            ...mockClient,
            ...requestBody,
            updated_at: new Date().toISOString(),
          }),
        });
      }
    });

    // Abrir menu e clicar em editar
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    // Alterar dados
    await page.locator('input#nome').fill('Condomínio Edifício Atualizado');
    await page.locator('input#email').fill('novo@email.com.br');
    await page.locator('input#telefone').fill('(11) 9999-8888');
    await page.locator('input#endereco').fill('Av. Nova, 200 - São Paulo/SP');

    // Alterar tipo
    await page.locator('[role="combobox"]').first().click();
    await page.waitForTimeout(300);
    await page.locator('[role="option"]', { hasText: 'Empresa' }).click();

    // Salvar
    await page.locator('button', { hasText: 'Salvar' }).click();
    await page.waitForTimeout(1000);

    // Verificar que o modal fechou
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();

    // Verificar dados enviados
    expect(requestBody).not.toBeNull();
    expect(requestBody.nome).toBe('Condomínio Edifício Atualizado');
    expect(requestBody.email).toBe('novo@email.com.br');
    expect(requestBody.telefone).toBe('(11) 9999-8888');
    expect(requestBody.endereco).toBe('Av. Nova, 200 - São Paulo/SP');
    expect(requestBody.tipo).toBe('empresa');
  });

  test('deve permitir cancelar edição sem salvar alterações', async ({ page }) => {
    // Abrir menu e clicar em editar
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    // Alterar um campo
    await page.locator('input#nome').fill('Nome Alterado Temporariamente');

    // Cancelar
    await page.locator('button', { hasText: 'Cancelar' }).click();
    await page.waitForTimeout(500);

    // Verificar que o modal fechou
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();

    // Abrir novamente e verificar que os dados originais estão lá
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    await expect(page.locator('input#nome')).toHaveValue('Condomínio Edifício Teste');
  });

  test('deve abrir modal de detalhes ao clicar em ver detalhes', async ({ page }) => {
    // Abrir menu de ações
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);

    // Clicar em Ver detalhes
    await page.locator('text=Ver detalhes').click();
    await page.waitForTimeout(500);

    // Verificar que o modal de detalhes abriu
    await expect(page.locator('[role="dialog"]')).toBeVisible();
    await expect(page.locator('text=Detalhes do Cliente')).toBeVisible();
  });

  test('deve exibir informações completas no modal de detalhes', async ({ page }) => {
    // Abrir detalhes
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Ver detalhes').click();
    await page.waitForTimeout(500);

    // Verificar todas as informações
    await expect(page.locator('text=Condomínio Edifício Teste')).toBeVisible();
    await expect(page.locator('text=12.345.678/0001-90')).toBeVisible();
    await expect(page.locator('text=contato@teste.com.br')).toBeVisible();
    await expect(page.locator('text=(11) 3333-4444')).toBeVisible();
    await expect(page.locator('text=Rua Original, 100 - São Paulo/SP')).toBeVisible();
    await expect(page.locator('text=Condomínio')).toBeVisible();
    await expect(page.locator('text=Ativo')).toBeVisible();
  });

  test('deve permitir fechar modal de detalhes', async ({ page }) => {
    // Abrir detalhes
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Ver detalhes').click();
    await page.waitForTimeout(500);

    // Fechar com ESC
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);

    // Verificar que fechou
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('deve abrir modal de confirmação ao tentar excluir', async ({ page }) => {
    // Abrir menu de ações
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);

    // Clicar em Deletar
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    // Verificar modal de confirmação
    await expect(page.locator('text=Deletar Cliente')).toBeVisible();
    await expect(page.locator('text=/permanentemente/')).toBeVisible();
  });

  test('deve permitir cancelar exclusão', async ({ page }) => {
    // Abrir menu e clicar em deletar
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    // Clicar em Cancelar
    await page.locator('button', { hasText: 'Cancelar' }).last().click();
    await page.waitForTimeout(500);

    // Verificar que voltou para a lista
    await expect(page.locator('text=Deletar Cliente')).not.toBeVisible();
  });

  test('deve excluir cliente após confirmação', async ({ page }) => {
    let deleteCalled = false;

    // Interceptar delete
    await page.route('**/api/v1/clients/client-123', (route) => {
      if (route.request().method() === 'DELETE') {
        deleteCalled = true;
        route.fulfill({
          status: 204,
          contentType: 'application/json',
          body: '',
        });
      }
    });

    // Abrir menu e clicar em deletar
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    // Confirmar exclusão
    await page.locator('button', { hasText: /^Deletar$/ }).click();
    await page.waitForTimeout(1000);

    // Verificar que o delete foi chamado
    expect(deleteCalled).toBe(true);

    // Verificar que o modal fechou
    await expect(page.locator('text=Deletar Cliente')).not.toBeVisible();
  });

  test('deve exibir loading durante exclusão', async ({ page }) => {
    // Mock com delay
    await page.route('**/api/v1/clients/client-123', async (route) => {
      if (route.request().method() === 'DELETE') {
        await new Promise(resolve => setTimeout(resolve, 1500));
        route.fulfill({ status: 204, body: '' });
      }
    });

    // Iniciar exclusão
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    // Confirmar
    await page.locator('button', { hasText: /^Deletar$/ }).click();

    // Verificar loading
    await expect(page.locator('button:disabled')).toBeVisible();
  });

  test('deve lidar com erro ao tentar excluir', async ({ page }) => {
    // Mock de erro
    await page.route('**/api/v1/clients/client-123', (route) => {
      if (route.request().method() === 'DELETE') {
        route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Cliente possui contratos ativos' }),
        });
      }
    });

    // Tentar excluir
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Deletar').click();
    await page.waitForTimeout(500);

    await page.locator('button', { hasText: /^Deletar$/ }).click();
    await page.waitForTimeout(1000);

    // Modal deve continuar aberto
    await expect(page.locator('text=Deletar Cliente')).toBeVisible();
  });

  test('deve manter estado do formulário durante loading de edição', async ({ page }) => {
    // Mock com delay
    await page.route('**/api/v1/clients/client-123', async (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        await new Promise(resolve => setTimeout(resolve, 1500));
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockClient),
        });
      }
    });

    // Abrir edição
    await page.locator('button').filter({ has: page.locator('svg') }).first().click();
    await page.waitForTimeout(300);
    await page.locator('text=Editar').click();
    await page.waitForTimeout(500);

    // Alterar e salvar
    await page.locator('input#nome').fill('Nome em Atualização');
    await page.locator('button', { hasText: 'Salvar' }).click();

    // Verificar loading
    await expect(page.locator('text=Salvando...')).toBeVisible();

    // Verificar que os campos estão desabilitados
    await expect(page.locator('input#nome')).toBeDisabled();
    await expect(page.locator('button', { hasText: 'Cancelar' })).toBeDisabled();
  });
});
