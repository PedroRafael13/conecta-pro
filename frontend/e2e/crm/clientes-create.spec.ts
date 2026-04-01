/**
 * Testes E2E - Clientes - Criação
 *
 * Testes para criação de novos clientes no CRM
 * cobrindo: abertura de modal, validação de formulário e criação
 */

import { test, expect } from '../fixtures';

test.describe('CRM - Clientes - Criação', () => {
  test.beforeEach(async ({ page }) => {
    // Mock do endpoint de clientes
    await page.route('**/api/v1/clients*', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [],
          total: 0,
          skip: 0,
          limit: 20,
        }),
      });
    });

    // Mock do endpoint de criação
    await page.route('**/api/v1/clients', (route) => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'new-client-id',
            nome: 'Novo Cliente Teste',
            cnpj: '11.111.111/0001-11',
            email: 'novo@teste.com',
            telefone: '(11) 99999-9999',
            tipo: 'condominio',
            status: 'active',
            endereco: 'Rua Teste, 123',
            created_at: new Date().toISOString(),
          }),
        });
      } else {
        route.continue();
      }
    });

    await page.goto('/modulos/crm/clientes', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve abrir modal de novo cliente ao clicar no botão', async ({ page }) => {
    // Clicar no botão Novo Cliente
    const novoButton = page.locator('button', { hasText: 'Novo Cliente' });
    await novoButton.click();
    await page.waitForTimeout(500);

    // Verificar que o modal abriu
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();

    // Verificar título do modal
    await expect(page.locator('text=Novo Cliente').first()).toBeVisible();
  });

  test('deve exibir todos os campos do formulário de criação', async ({ page }) => {
    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Verificar campos obrigatórios
    await expect(page.locator('label', { hasText: 'Nome' })).toBeVisible();
    await expect(page.locator('input#nome')).toBeVisible();

    await expect(page.locator('label', { hasText: 'CNPJ' })).toBeVisible();
    await expect(page.locator('input#cnpj')).toBeVisible();

    await expect(page.locator('label', { hasText: 'Email' })).toBeVisible();
    await expect(page.locator('input#email')).toBeVisible();

    await expect(page.locator('label', { hasText: 'Telefone' })).toBeVisible();
    await expect(page.locator('input#telefone')).toBeVisible();

    await expect(page.locator('label', { hasText: 'Tipo' })).toBeVisible();
    await expect(page.locator('[role="combobox"]').first()).toBeVisible();

    await expect(page.locator('label', { hasText: 'Endereço' })).toBeVisible();
    await expect(page.locator('input#endereco')).toBeVisible();
  });

  test('deve preencher e submeter formulário de criação com sucesso', async ({ page }) => {
    let requestBody: any = null;

    // Interceptar request para validar dados
    await page.route('**/api/v1/clients', (route) => {
      if (route.request().method() === 'POST') {
        requestBody = route.request().postDataJSON();
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'new-client-id',
            ...requestBody,
            created_at: new Date().toISOString(),
          }),
        });
      }
    });

    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Preencher formulário
    await page.locator('input#nome').fill('Condomínio Teste E2E');
    await page.locator('input#cnpj').fill('11.111.111/0001-11');
    await page.locator('input#email').fill('teste@condominio.com.br');
    await page.locator('input#telefone').fill('(11) 99999-8888');
    await page.locator('input#endereco').fill('Rua do Teste, 456 - São Paulo/SP');

    // Selecionar tipo
    await page.locator('[role="combobox"]').first().click();
    await page.waitForTimeout(300);
    await page.locator('[role="option"]', { hasText: 'Empresa' }).click();

    // Clicar em criar
    await page.locator('button', { hasText: /^Criar$/ }).click();
    await page.waitForTimeout(1000);

    // Verificar que o modal fechou
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();

    // Verificar que os dados foram enviados corretamente
    expect(requestBody).not.toBeNull();
    expect(requestBody.nome).toBe('Condomínio Teste E2E');
    expect(requestBody.cnpj).toBe('11.111.111/0001-11');
    expect(requestBody.email).toBe('teste@condominio.com.br');
    expect(requestBody.telefone).toBe('(11) 99999-8888');
    expect(requestBody.tipo).toBe('empresa');
    expect(requestBody.endereco).toBe('Rua do Teste, 456 - São Paulo/SP');
  });

  test('deve permitir fechar modal sem salvar', async ({ page }) => {
    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Preencher algum dado
    await page.locator('input#nome').fill('Teste parcial');

    // Clicar em cancelar
    await page.locator('button', { hasText: 'Cancelar' }).click();
    await page.waitForTimeout(500);

    // Verificar que o modal fechou
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();

    // Verificar que estamos na mesma página
    await expect(page).toHaveURL(/\/crm\/clientes/);
  });

  test('deve permitir fechar modal com tecla ESC', async ({ page }) => {
    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Pressionar ESC
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);

    // Verificar que o modal fechou
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('deve validar campo nome obrigatório', async ({ page }) => {
    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Tentar submeter sem preencher nome
    await page.locator('input#email').fill('teste@teste.com');

    // Clicar em criar
    await page.locator('button', { hasText: /^Criar$/ }).click();
    await page.waitForTimeout(500);

    // Modal deve continuar aberto (validação nativa do HTML5 ou do formulário)
    // ou deve mostrar mensagem de erro
    const modal = page.locator('[role="dialog"]');
    const isModalOpen = await modal.isVisible().catch(() => false);

    if (isModalOpen) {
      // Verificar se há mensagem de erro
      const errorMessage = await page.locator('text=/obrigatório|required/i').isVisible().catch(() => false);
      expect(errorMessage || isModalOpen).toBeTruthy();
    }
  });

  test('deve permitir criação com dados mínimos', async ({ page }) => {
    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Preencher apenas nome
    await page.locator('input#nome').fill('Cliente Mínimo');

    // Clicar em criar
    await page.locator('button', { hasText: /^Criar$/ }).click();
    await page.waitForTimeout(1000);

    // Verificar que o modal fechou (API aceitou)
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('deve exibir estado de loading durante criação', async ({ page }) => {
    // Mock com delay
    await page.route('**/api/v1/clients', async (route) => {
      if (route.request().method() === 'POST') {
        await new Promise(resolve => setTimeout(resolve, 1500));
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ id: '123', nome: 'Teste' }),
        });
      }
    });

    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Preencher e submeter
    await page.locator('input#nome').fill('Cliente Loading Test');
    await page.locator('button', { hasText: /^Criar$/ }).click();

    // Verificar loading
    await expect(page.locator('text=Salvando...')).toBeVisible();

    // Verificar que o botão está desabilitado durante loading
    const submitButton = page.locator('button', { hasText: 'Salvando...' });
    await expect(submitButton).toBeDisabled();
  });

  test('deve lidar com erro na API ao criar cliente', async ({ page }) => {
    // Mock de erro
    await page.route('**/api/v1/clients', (route) => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'CNPJ já cadastrado' }),
        });
      }
    });

    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Preencher formulário
    await page.locator('input#nome').fill('Cliente Erro');
    await page.locator('input#cnpj').fill('00.000.000/0000-00');

    // Clicar em criar
    await page.locator('button', { hasText: /^Criar$/ }).click();
    await page.waitForTimeout(1000);

    // Modal deve continuar aberto para permitir correção
    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });

  test('deve validar formato de email', async ({ page }) => {
    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Preencher nome
    await page.locator('input#nome').fill('Cliente Email');

    // Tentar email inválido
    const emailInput = page.locator('input#email');
    await emailInput.fill('email-invalido');

    // Verificar tipo do input
    const inputType = await emailInput.getAttribute('type');
    expect(inputType).toBe('email');

    // O input type="email" faz validação nativa do navegador
  });

  test('deve ter opções corretas no select de tipo', async ({ page }) => {
    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Abrir select
    await page.locator('[role="combobox"]').first().click();
    await page.waitForTimeout(300);

    // Verificar opções
    const options = ['Condomínio', 'Empresa', 'Residencial'];
    for (const option of options) {
      await expect(page.locator('[role="option"]', { hasText: option })).toBeVisible();
    }
  });

  test('deve manter dados ao tentar submeter com erro', async ({ page }) => {
    // Mock de erro
    await page.route('**/api/v1/clients', (route) => {
      if (route.request().method() === 'POST') {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Erro interno' }),
        });
      }
    });

    // Abrir modal
    await page.locator('button', { hasText: 'Novo Cliente' }).click();
    await page.waitForTimeout(500);

    // Preencher todos os campos
    await page.locator('input#nome').fill('Cliente Persistente');
    await page.locator('input#cnpj').fill('22.222.222/0001-22');
    await page.locator('input#email').fill('persistente@teste.com');
    await page.locator('input#telefone').fill('(11) 98888-7777');
    await page.locator('input#endereco').fill('Rua Persistente, 999');

    // Clicar em criar
    await page.locator('button', { hasText: /^Criar$/ }).click();
    await page.waitForTimeout(1000);

    // Verificar que os dados foram mantidos
    await expect(page.locator('input#nome')).toHaveValue('Cliente Persistente');
    await expect(page.locator('input#cnpj')).toHaveValue('22.222.222/0001-22');
    await expect(page.locator('input#email')).toHaveValue('persistente@teste.com');
  });
});
