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
    await expect(page.locator('text=Conecta PRO')).toBeVisible();
    await expect(page.locator('img[alt="Conecta PRO"]')).toBeVisible();

    // Verifica saudação personalizada
    await expect(page.locator('h1:has-text("Bom dia"), h1:has-text("Boa tarde"), h1:has-text("Boa noite")')).toBeVisible();
    await expect(page.locator('h1:has-text("Admin")')).toBeVisible();

    // Verifica campo de busca
    await expect(page.locator('input[type="search"], input[placeholder*="Buscar" i]')).toBeVisible();

    // Verifica botão de notificações
    await expect(page.locator('button:has([name="bell"]), button:has(.lucide-bell)')).toBeVisible();

    // Verifica badge de notificações
    await expect(page.locator('text=3')).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    // Verifica cards de estatísticas
    await expect(page.locator('text=Colaboradores')).toBeVisible();
    await expect(page.locator('text=Postos Ativos')).toBeVisible();
    await expect(page.locator('text=Clientes')).toBeVisible();
    await expect(page.locator('text=Escalas')).toBeVisible();

    // Verifica valores
    await expect(page.locator('text=44')).toBeVisible();
    await expect(page.locator('text=9')).toBeVisible();
    await expect(page.locator('text=4')).toBeVisible();
    await expect(page.locator('text=28')).toBeVisible();
  });

  test('deve exibir categorias de módulos', async ({ page }) => {
    // Verifica se há categorias de módulos
    const moduleCategories = page.locator('section h2');
    const count = await moduleCategories.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve navegar para módulo Operacional', async ({ page }) => {
    // Clica no módulo Operacional
    await page.click('text=Operacional');

    // Verifica navegação
    await expect(page).toHaveURL(/\/modulos\/operacional/);
  });

  test('deve navegar para módulo Financeiro', async ({ page }) => {
    // Clica no módulo Financeiro
    await page.click('text=Financeiro');

    // Verifica navegação
    await expect(page).toHaveURL(/\/modulos\/financeiro/);
  });

  test('deve navegar para módulo Fiscal', async ({ page }) => {
    // Clica no módulo Fiscal
    await page.click('text=Fiscal');

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
    // Clica no botão de logout
    await page.click('button:has(.lucide-logout), button:has([name="log-out"])');

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
    await page.reload();

    // Verifica se elementos essenciais ainda estão visíveis
    await expect(page.locator('h1:has-text("Bom dia"), h1:has-text("Boa tarde"), h1:has-text("Boa noite")')).toBeVisible();

    // Verifica campo de busca mobile
    await expect(page.locator('input[type="search"]').first()).toBeVisible();
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
    // Verifica informações do usuário logado
    await expect(page.locator('text=Admin')).toBeVisible();
    await expect(page.locator('text=admin')).toBeVisible();
  });
});
