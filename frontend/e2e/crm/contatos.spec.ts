/**
 * Testes E2E - CRM - Contatos
 *
 * Testes para gestão de contatos de clientes
 * cobrindo: listagem, criação, edição e exclusão local
 */

import { test, expect } from '../fixtures';

test.describe('CRM - Contatos', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/modulos/crm/contatos', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test.describe('Listagem', () => {
    test('deve carregar página de contatos', async ({ page }) => {
      await expect(page.locator('h1').first()).toContainText('Contatos');
      await expect(page.locator('p', { hasText: /Gestao/i })).toBeVisible();
    });

    test('deve exibir cards de estatísticas', async ({ page }) => {
      await expect(page.locator('text=Total Contatos')).toBeVisible();
      await expect(page.locator('text=Ativos')).toBeVisible();
    });

    test('deve ter botão de novo contato', async ({ page }) => {
      const novoButton = page.locator('button', { hasText: 'Novo Contato' });
      await expect(novoButton).toBeVisible();
      await expect(novoButton).toBeEnabled();
    });

    test('deve exibir campo de busca', async ({ page }) => {
      const searchInput = page.locator('input[placeholder*="Buscar"]').first();
      await expect(searchInput).toBeVisible();
    });
  });

  test.describe('Formulário de Criação', () => {
    test('deve exibir formulário inline ao clicar em novo contato', async ({ page }) => {
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);

      // Verificar campos do formulário
      await expect(page.locator('text=Novo Contato').nth(1)).toBeVisible();
      await expect(page.locator('label', { hasText: 'Nome' })).toBeVisible();
      await expect(page.locator('label', { hasText: 'Email' })).toBeVisible();
      await expect(page.locator('label', { hasText: 'Telefone' })).toBeVisible();
      await expect(page.locator('label', { hasText: 'Cargo' })).toBeVisible();
      await expect(page.locator('label', { hasText: 'Cliente' })).toBeVisible();
    });

    test('deve criar contato com sucesso', async ({ page }) => {
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);

      // Preencher formulário
      await page.locator('input').filter({ hasText: '' }).first().fill('Contato Teste');

      const inputs = await page.locator('input').all();
      if (inputs.length > 1) await inputs[1]!.fill('contato@teste.com');
      if (inputs.length > 2) await inputs[2]!.fill('(11) 99999-8888');
      if (inputs.length > 3) await inputs[3]!.fill('Gerente');
      if (inputs.length > 4) await inputs[4]!.fill('Cliente Teste Ltda');

      // Criar
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Verificar que o contato foi adicionado
      await expect(page.locator('td', { hasText: 'Contato Teste' })).toBeVisible();

      // Stats devem atualizar
      await expect(page.locator('text=1')).toBeVisible();
    });

    test('deve validar campo nome obrigatório', async ({ page }) => {
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);

      // Tentar criar sem preencher nome
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(500);

      // Formulário deve continuar aberto
      await expect(page.locator('text=Novo Contato').nth(1)).toBeVisible();
    });

    test('deve permitir cancelar criação', async ({ page }) => {
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);

      await page.locator('input').filter({ hasText: '' }).first().fill('Temporário');

      await page.locator('button', { hasText: 'Cancelar' }).click();
      await page.waitForTimeout(500);

      // Formulário deve desaparecer
      await expect(page.locator('text=Novo Contato').nth(1)).not.toBeVisible();
    });
  });

  test.describe('Gestão de Contatos', () => {
    test('deve criar e exibir múltiplos contatos', async ({ page }) => {
      // Criar primeiro contato
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);

      const inputs1 = await page.locator('input').all();
      await inputs1[0]!.fill('João Silva');
      if (inputs1[1]) await inputs1[1].fill('joao@teste.com');
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Criar segundo contato
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);

      const inputs2 = await page.locator('input').all();
      await inputs2[0]!.fill('Maria Santos');
      if (inputs2[1]) await inputs2[1].fill('maria@teste.com');
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Verificar ambos na lista
      await expect(page.locator('td', { hasText: 'João Silva' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Maria Santos' })).toBeVisible();

      // Total deve ser 2
      const totalCard = page.locator('text=Total Contatos').locator('xpath=../../div[contains(@class,"text-2xl")]');
      await expect(totalCard).toHaveText('2');
    });

    test('deve filtrar contatos por busca', async ({ page }) => {
      // Criar contatos
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);
      const inputs = await page.locator('input').all();
      await inputs[0]!.fill('Carlos Ferreira');
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Buscar
      const searchInput = page.locator('input[placeholder*="Buscar"]').first();
      await searchInput.fill('Carlos');
      await page.waitForTimeout(500);

      // Deve mostrar apenas o filtrado
      await expect(page.locator('td', { hasText: 'Carlos Ferreira' })).toBeVisible();
    });

    test('deve editar contato existente', async ({ page }) => {
      // Criar contato
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);
      let inputs = await page.locator('input').all();
      await inputs[0]!.fill('Antigo Nome');
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Editar
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);
      await page.locator('text=Editar').click();
      await page.waitForTimeout(500);

      // Alterar nome
      inputs = await page.locator('input').all();
      await inputs[0]!.fill('Nome Atualizado');
      await page.locator('button', { hasText: 'Salvar' }).click();
      await page.waitForTimeout(1000);

      // Verificar atualização
      await expect(page.locator('td', { hasText: 'Nome Atualizado' })).toBeVisible();
      await expect(page.locator('td', { hasText: 'Antigo Nome' })).not.toBeVisible();
    });

    test('deve exibir detalhes do contato', async ({ page }) => {
      // Criar contato
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);
      const inputs = await page.locator('input').all();
      await inputs[0]!.fill('Detalhes Teste');
      if (inputs[1]) await inputs[1].fill('detalhes@teste.com');
      if (inputs[2]) await inputs[2].fill('(11) 97777-6666');
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Abrir detalhes
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);
      await page.locator('text=Ver detalhes').click();
      await page.waitForTimeout(500);

      // Verificar detalhes
      await expect(page.locator('text=Detalhes do Contato')).toBeVisible();
      await expect(page.locator('text=Detalhes Teste')).toBeVisible();
      await expect(page.locator('text=detalhes@teste.com')).toBeVisible();
    });

    test('deve excluir contato', async ({ page }) => {
      // Criar contato
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);
      const inputs = await page.locator('input').all();
      await inputs[0]!.fill('Para Excluir');
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Excluir
      await page.locator('table tbody tr').first().locator('button').last().click();
      await page.waitForTimeout(300);
      await page.locator('text=Remover').click();
      await page.waitForTimeout(1000);

      // Verificar exclusão
      await expect(page.locator('td', { hasText: 'Para Excluir' })).not.toBeVisible();
    });
  });

  test.describe('Estados', () => {
    test('deve exibir estado vazio inicial', async ({ page }) => {
      await expect(page.locator('text=Nenhum contato encontrado')).toBeVisible();
      await expect(page.locator('text=Adicione um novo contato para comecar')).toBeVisible();
    });

    test('deve exibir ícones de email e telefone na tabela', async ({ page }) => {
      // Criar contato com email e telefone
      await page.locator('button', { hasText: 'Novo Contato' }).click();
      await page.waitForTimeout(500);
      const inputs = await page.locator('input').all();
      await inputs[0]!.fill('Teste Icones');
      if (inputs[1]) await inputs[1].fill('email@teste.com');
      if (inputs[2]) await inputs[2].fill('(11) 99999-9999');
      await page.locator('button', { hasText: 'Criar Contato' }).click();
      await page.waitForTimeout(1000);

      // Verificar ícones
      const table = page.locator('table');
      await expect(table.locator('svg')).toBeVisible();
    });
  });
});
