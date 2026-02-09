/**
 * Testes E2E - Clientes - Listagem
 *
 * Testes para a página de listagem de clientes do CRM
 * cobrindo: carregamento, filtros, ordenação, paginação e visualização
 */

import { test, expect } from '../fixtures';

test.describe('CRM - Clientes - Listagem', () => {
  test.beforeEach(async ({ page }) => {
    // Mock do endpoint de clientes para testes consistentes
    await page.route('**/api/v1/clients*', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: '1',
              nome: 'Condomínio Edifício Aurora',
              cnpj: '12.345.678/0001-90',
              email: 'contato@aurora.com.br',
              telefone: '(11) 3333-4444',
              tipo: 'condominio',
              status: 'active',
              endereco: 'Rua das Flores, 123 - São Paulo/SP',
              created_at: '2024-01-15T10:00:00Z',
            },
            {
              id: '2',
              nome: 'Empresa XYZ Ltda',
              cnpj: '98.765.432/0001-10',
              email: 'admin@xyz.com.br',
              telefone: '(11) 2222-3333',
              tipo: 'empresa',
              status: 'active',
              endereco: 'Av. Paulista, 1000 - São Paulo/SP',
              created_at: '2024-02-20T14:30:00Z',
            },
            {
              id: '3',
              nome: 'Residencial Jardins',
              cnpj: '',
              email: 'jardins@email.com',
              telefone: '(11) 5555-6666',
              tipo: 'residencial',
              status: 'suspended',
              endereco: 'Rua dos Jardins, 50 - São Paulo/SP',
              created_at: '2024-03-10T09:15:00Z',
            },
            {
              id: '4',
              nome: 'Condomínio Central Park',
              cnpj: '11.222.333/0001-44',
              email: 'sindico@centralpark.com',
              telefone: '(11) 7777-8888',
              tipo: 'condominio',
              status: 'blocked',
              endereco: 'Av. Central, 500 - São Paulo/SP',
              created_at: '2024-04-05T16:45:00Z',
            },
          ],
          total: 4,
          skip: 0,
          limit: 20,
        }),
      });
    });

    await page.goto('/modulos/crm/clientes', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
  });

  test('deve carregar a página de clientes com título correto', async ({ page }) => {
    // Verificar título da página
    const heading = page.locator('h1').first();
    await expect(heading).toContainText('Clientes');

    // Verificar subtítulo
    const subtitle = page.locator('p.text-muted-foreground').first();
    await expect(subtitle).toContainText('Gestao de clientes');
  });

  test('deve exibir cards de estatísticas com valores corretos', async ({ page }) => {
    // Verificar card Total Clientes
    const totalCard = page.locator('text=Total Clientes').locator('..').locator('..');
    await expect(totalCard).toBeVisible();

    // Verificar valor total (4 clientes no mock)
    const totalValue = page.locator('text=Total Clientes').locator('xpath=../../div[contains(@class,"text-2xl")]');
    await expect(totalValue).toHaveText('4');

    // Verificar card Ativos (2 ativos no mock)
    const ativosValue = page.locator('text=Ativos').locator('xpath=../../div[contains(@class,"text-2xl")]');
    await expect(ativosValue).toHaveText('2');

    // Verificar card Condomínios (2 condomínios no mock)
    const condominiosValue = page.locator('text=Condominios').locator('xpath=../../div[contains(@class,"text-2xl")]');
    await expect(condominiosValue).toHaveText('2');

    // Verificar card Bloqueados (1 bloqueado no mock)
    const bloqueadosValue = page.locator('text=Bloqueados').locator('xpath=../../div[contains(@class,"text-2xl")]');
    await expect(bloqueadosValue).toHaveText('1');
  });

  test('deve exibir tabela de clientes com colunas corretas', async ({ page }) => {
    // Verificar se a tabela existe
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // Verificar cabeçalhos das colunas
    const headers = ['Nome', 'CNPJ', 'Email', 'Tipo', 'Status', 'Acoes'];
    for (const header of headers) {
      const th = page.locator('th', { hasText: new RegExp(header, 'i') });
      await expect(th).toBeVisible();
    }
  });

  test('deve exibir dados dos clientes na tabela', async ({ page }) => {
    // Verificar primeiro cliente
    await expect(page.locator('td', { hasText: 'Condomínio Edifício Aurora' })).toBeVisible();
    await expect(page.locator('td', { hasText: '12.345.678/0001-90' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'contato@aurora.com.br' })).toBeVisible();

    // Verificar segundo cliente
    await expect(page.locator('td', { hasText: 'Empresa XYZ Ltda' })).toBeVisible();
    await expect(page.locator('td', { hasText: '98.765.432/0001-10' })).toBeVisible();
  });

  test('deve filtrar clientes por texto de busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();

    // Digitar termo de busca
    await searchInput.fill('Aurora');
    await page.waitForTimeout(500);

    // Verificar que apenas o cliente filtrado aparece
    await expect(page.locator('td', { hasText: 'Condomínio Edifício Aurora' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Empresa XYZ Ltda' })).not.toBeVisible();

    // Limpar busca
    await searchInput.clear();
    await page.waitForTimeout(500);

    // Verificar que todos os clientes aparecem novamente
    await expect(page.locator('td', { hasText: 'Condomínio Edifício Aurora' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Empresa XYZ Ltda' })).toBeVisible();
  });

  test('deve filtrar clientes por CNPJ', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();

    // Buscar por CNPJ
    await searchInput.fill('98.765.432/0001-10');
    await page.waitForTimeout(500);

    // Verificar resultado
    await expect(page.locator('td', { hasText: 'Empresa XYZ Ltda' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Condomínio Edifício Aurora' })).not.toBeVisible();
  });

  test('deve filtrar clientes por email', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();

    // Buscar por email
    await searchInput.fill('jardins@email.com');
    await page.waitForTimeout(500);

    // Verificar resultado
    await expect(page.locator('td', { hasText: 'Residencial Jardins' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Condomínio Edifício Aurora' })).not.toBeVisible();
  });

  test('deve filtrar clientes por status', async ({ page }) => {
    // Abrir dropdown de status
    const statusSelect = page.locator('[role="combobox"]').first();
    await statusSelect.click();
    await page.waitForTimeout(300);

    // Selecionar "Ativo"
    await page.locator('[role="option"]', { hasText: 'Ativo' }).click();
    await page.waitForTimeout(500);

    // Verificar que apenas ativos aparecem
    await expect(page.locator('td', { hasText: 'Condomínio Edifício Aurora' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Empresa XYZ Ltda' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Residencial Jardins' })).not.toBeVisible();

    // Resetar para todos
    await statusSelect.click();
    await page.waitForTimeout(300);
    await page.locator('[role="option"]', { hasText: 'Todos os status' }).click();
    await page.waitForTimeout(500);

    // Verificar que todos aparecem
    await expect(page.locator('td', { hasText: 'Residencial Jardins' })).toBeVisible();
  });

  test('deve exibir badges de status com cores corretas', async ({ page }) => {
    // Verificar badge "Ativo" (verde)
    const ativoBadge = page.locator('span', { hasText: 'Ativo' }).first();
    await expect(ativoBadge).toBeVisible();
    await expect(ativoBadge).toHaveClass(/bg-green/);

    // Verificar badge "Suspenso" (amarelo)
    const suspensoBadge = page.locator('span', { hasText: 'Suspenso' }).first();
    await expect(suspensoBadge).toBeVisible();
    await expect(suspensoBadge).toHaveClass(/bg-yellow/);

    // Verificar badge "Bloqueado" (vermelho)
    const bloqueadoBadge = page.locator('span', { hasText: 'Bloqueado' }).first();
    await expect(bloqueadoBadge).toBeVisible();
    await expect(bloqueadoBadge).toHaveClass(/bg-red/);
  });

  test('deve exibir badges de tipo com cores corretas', async ({ page }) => {
    // Verificar badge "condominio" (azul)
    const condominioBadge = page.locator('span', { hasText: 'condominio' }).first();
    await expect(condominioBadge).toBeVisible();
    await expect(condominioBadge).toHaveClass(/bg-blue/);

    // Verificar badge "empresa" (roxo)
    const empresaBadge = page.locator('span', { hasText: 'empresa' }).first();
    await expect(empresaBadge).toBeVisible();
    await expect(empresaBadge).toHaveClass(/bg-purple/);
  });

  test('deve ter botão de novo cliente funcional', async ({ page }) => {
    const novoButton = page.locator('button', { hasText: 'Novo Cliente' });
    await expect(novoButton).toBeVisible();
    await expect(novoButton).toBeEnabled();
  });

  test('deve ter botão de atualizar dados', async ({ page }) => {
    const refreshButton = page.locator('button', { hasText: 'Atualizar' });
    await expect(refreshButton).toBeVisible();
    await expect(refreshButton).toBeEnabled();

    // Clicar em atualizar
    await refreshButton.click();
    await page.waitForTimeout(500);

    // Verificar que a página ainda está carregada
    await expect(page.locator('h1').first()).toContainText('Clientes');
  });

  test('deve exibir menu de ações para cada cliente', async ({ page }) => {
    // Clicar no menu do primeiro cliente
    const menuButton = page.locator('button').filter({ has: page.locator('svg') }).first();
    await menuButton.click();
    await page.waitForTimeout(300);

    // Verificar opções do menu
    await expect(page.locator('text=Ver detalhes')).toBeVisible();
    await expect(page.locator('text=Editar')).toBeVisible();
    await expect(page.locator('text=Deletar')).toBeVisible();

    // Fechar menu com Escape
    await page.keyboard.press('Escape');
  });

  test('deve exibir estado vazio quando não há resultados na busca', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Buscar por nome"]').first();

    // Buscar termo inexistente
    await searchInput.fill('XYZ123INEXISTENTE');
    await page.waitForTimeout(500);

    // Verificar mensagem de estado vazio
    await expect(page.locator('text=Nenhum cliente encontrado')).toBeVisible();
    await expect(page.locator('text=Tente ajustar os filtros ou cadastre um novo cliente')).toBeVisible();
  });

  test('deve exibir loading state durante carregamento', async ({ page }) => {
    // Adicionar delay no mock para simular loading
    await page.route('**/api/v1/clients*', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0, skip: 0, limit: 20 }),
      });
    });

    // Recarregar página
    await page.reload();

    // Verificar spinner de loading
    const spinner = page.locator('.animate-spin');
    await expect(spinner).toBeVisible();
  });

  test('deve lidar com erro na API', async ({ page }) => {
    // Mock de erro
    await page.route('**/api/v1/clients*', (route) => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Erro interno do servidor' }),
      });
    });

    // Recarregar página
    await page.reload();
    await page.waitForTimeout(2000);

    // Verificar mensagem de erro
    await expect(page.locator('text=Erro ao carregar clientes')).toBeVisible();
    await expect(page.locator('button', { hasText: 'Tentar novamente' })).toBeVisible();
  });
});
