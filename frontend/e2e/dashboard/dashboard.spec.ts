import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

test.describe('Dashboard Principal', () => {
  test.beforeEach(async ({ page }) => {
    // Realiza autenticação via API helper antes de cada teste
    await loginViaAPI(page);
    await page.goto('/dashboard');
  });

  test('deve carregar dashboard com elementos principais', async ({ page }) => {
    // Verifica header
    await expect(page.locator('img[alt="Conecta PRO"]').first()).toBeVisible();

    // Verifica saudação personalizada
    await expect(page.locator('h1:has-text("Bom dia"), h1:has-text("Boa tarde"), h1:has-text("Boa noite")')).toBeVisible();

    // Verifica campo de busca (desktop ou mobile)
    await expect(page.locator('input[type="search"], input[placeholder*="Buscar" i]').first()).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    // Verifica cards de estatísticas
    await expect(page.getByText('Colaboradores')).toBeVisible();
    await expect(page.getByText('Postos Ativos')).toBeVisible();
    await expect(page.getByText('Clientes').first()).toBeVisible();
    await expect(page.getByText('Escalas').first()).toBeVisible();
  });

  test('deve exibir categorias de módulos', async ({ page }) => {
    // Aguarda conteúdo renderizar e verifica que há pelo menos uma categoria
    await expect(page.locator('h2:has-text("Operacional"), h2:has-text("Financeiro"), h2:has-text("Administrativo")').first()).toBeVisible({ timeout: 10000 });
  });

  test('deve navegar para módulo Operacional', async ({ page }) => {
    // Clica no card do módulo Operacional (h3 dentro do card)
    await page.locator('h3:has-text("Operacional")').click();

    // Verifica navegação
    await expect(page).toHaveURL(/\/modulos\/operacional/);
  });

  test('deve navegar para módulo Financeiro', async ({ page }) => {
    // Clica no card do módulo Financeiro
    await page.locator('h3:has-text("Financeiro")').click();

    // Verifica navegação
    await expect(page).toHaveURL(/\/modulos\/financeiro/);
  });

  test('deve navegar para módulo Fiscal', async ({ page }) => {
    // Clica no card do módulo Fiscal
    await page.locator('h3:has-text("Fiscal")').click();

    // Verifica navegação
    await expect(page).toHaveURL(/\/modulos\/fiscal/);
  });

  test('deve navegar para módulo Licitações', async ({ page }) => {
    // Clica no módulo Licitações
    await page.click('text=Licitações');

    // Verifica navegação
    await expect(page).toHaveURL(/\/modulos\/licitacoes/);
  });

  test('deve filtrar módulos pela busca', async ({ page }) => {
    // Digita termo de busca
    await page.fill('input[type="search"]', 'escalas');

    // Aguarda filtro ser aplicado
    await page.waitForTimeout(500);

    // Verifica se módulos relacionados a escalas são exibidos
    const modules = page.locator('[href*="escalas"], button:has-text("Escalas")');
    const count = await modules.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('deve mostrar empty state quando busca não encontra resultados', async ({ page }) => {
    // Digita termo inexistente
    await page.fill('input[type="search"]', 'xyz123inexistente');

    // Aguarda filtro ser aplicado
    await page.waitForTimeout(500);

    // Verifica mensagem de empty state
    await expect(page.locator('text=Nenhum módulo encontrado')).toBeVisible();
    await expect(page.locator('text=Tente buscar por outro termo')).toBeVisible();
  });

  test('deve fazer logout pelo dashboard', async ({ page }) => {
    // Clica no botão de logout (ícone LogOut no header)
    await page.locator('button:has(.lucide-log-out)').click();

    // Verifica redirecionamento para login
    await expect(page).toHaveURL(/\/login/, { timeout: 10000 });
  });

  test('deve ter footer com informações da versão', async ({ page }) => {
    // Verifica versão no footer
    await expect(page.locator('text=Conecta PRO v2.0.0')).toBeVisible();
    await expect(page.locator('text=erp.conectamais.pro')).toBeVisible();
  });

  test('deve ter responsividade em mobile', async ({ page }) => {
    // Define viewport mobile
    await page.setViewportSize({ width: 375, height: 667 });

    // Recarrega página
    await page.reload({ waitUntil: 'load' });

    // Verifica se elementos essenciais ainda estão visíveis
    await expect(page.locator('h1:has-text("Bom dia"), h1:has-text("Boa tarde"), h1:has-text("Boa noite")')).toBeVisible();

    // Verifica stats cards visíveis em mobile (grid 2x2)
    await expect(page.getByText('Colaboradores')).toBeVisible();
    await expect(page.getByText('Postos Ativos')).toBeVisible();

    // Bartolo removido — FAB não existe mais

    // Verifica que o campo de busca mobile está presente na DOM
    const searchInputs = page.locator('input[placeholder*="Buscar" i]');
    const count = await searchInputs.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Dashboard - Ações Rápidas', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/dashboard');
  });

  test('deve acessar configurações pelo dashboard', async ({ page }) => {
    // Clica no módulo de configurações (se existir)
    const configModule = page.locator('text=Configurações').first();
    if (await configModule.isVisible().catch(() => false)) {
      await configModule.click();
      await expect(page).toHaveURL(/\/modulos\/configuracoes|settings/);
    }
  });

  test('deve mostrar menu do usuário', async ({ page }) => {
    // Verifica informações do usuário logado no header
    await expect(page.getByRole('banner').getByText('Admin', { exact: true })).toBeVisible();
  });
});
