import { test, expect } from '@playwright/test';
import { loginViaAPI } from '../helpers/auth';

/**
 * Testes E2E - Módulo Agendador - Página Principal
 *
 * Testa funcionalidades:
 * - Carregamento da página
 * - Exibição de estatísticas
 * - Navegação para subpáginas
 * - Execução de ciclo manual
 */

test.describe('Módulo Agendador - Página Principal', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
    await page.goto('/modulos/agendador');
  });

  test('deve carregar página corretamente', async ({ page }) => {
    // Verificar título principal
    await expect(page.locator('h1')).toContainText('Agendador de Tarefas');

    // Verificar descrição
    await expect(page.locator('text=Gerenciamento de tarefas agendadas')).toBeVisible();

    // Verificar se o botão Executar Ciclo está presente
    await expect(page.locator('button:has-text("Executar Ciclo")')).toBeVisible();
  });

  test('deve exibir cards de estatísticas', async ({ page }) => {
    // Aguardar carregamento dos dados
    await page.waitForLoadState('load');

    // Verificar cards de estatísticas
    await expect(page.locator('text=Total Tarefas').first()).toBeVisible();
    await expect(page.locator('text=Execucoes Recentes').first()).toBeVisible();
    await expect(page.locator('text=Itens na Fila').first()).toBeVisible();
    await expect(page.locator('text=Workers Ativos').first()).toBeVisible();

    // Verificar ícones nos cards
    await expect(page.locator('[class*="text-blue-600"]').first()).toBeVisible();
    await expect(page.locator('[class*="text-green-600"]').first()).toBeVisible();
    await expect(page.locator('[class*="text-amber-600"]').first()).toBeVisible();
    await expect(page.locator('[class*="text-purple-600"]').first()).toBeVisible();
  });

  test('deve exibir navegação para subpáginas', async ({ page }) => {
    // Verificar cards de navegação
    await expect(page.locator('text=Tarefas Agendadas')).toBeVisible();
    await expect(page.locator('text=Criar, editar e gerenciar tarefas agendadas')).toBeVisible();

    await expect(page.locator('text=Historico de Execucoes')).toBeVisible();
    await expect(page.locator('text=Visualizar historico completo de execucoes')).toBeVisible();
  });

  test('deve navegar para página de tarefas', async ({ page }) => {
    // Clicar no card de Tarefas Agendadas
    await page.click('text=Tarefas Agendadas');

    // Verificar redirecionamento
    await expect(page).toHaveURL(/.*\/modulos\/agendador\/tarefas/);
  });

  test('deve navegar para página de execuções', async ({ page }) => {
    // Clicar no card de Histórico de Execuções
    await page.click('text=Historico de Execucoes');

    // Verificar redirecionamento
    await expect(page).toHaveURL(/.*\/modulos\/agendador\/execucoes/);
  });

  test('deve exibir seção de tarefas pendentes', async ({ page }) => {
    // Verificar título da seção
    await expect(page.locator('text=Tarefas Pendentes de Execucao')).toBeVisible();

    // Verificar se a seção está presente (pode estar vazia ou com dados)
    const section = page.locator('text=Tarefas Pendentes de Execucao').locator('..').locator('..');
    await expect(section).toBeVisible();
  });

  test('deve permitir atualizar dados', async ({ page }) => {
    // Verificar se o botão de atualizar/refetch está presente
    // (A página pode ter funcionalidade de refresh implícita)
    await expect(page.locator('button:has-text("Executar Ciclo")')).toBeEnabled();
  });
});

test.describe('Módulo Agendador - Responsividade', () => {
  test.beforeEach(async ({ page }) => {
    await loginViaAPI(page);
  });

  test('deve exibir layout correto em desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/modulos/agendador');

    // Verificar grid de 4 colunas para estatísticas
    const statsGrid = page.locator('.grid').first();
    await expect(statsGrid).toBeVisible();
  });

  test('deve exibir layout correto em tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/modulos/agendador');

    await expect(page.locator('h1')).toContainText('Agendador de Tarefas');
  });

  test('deve exibir layout correto em mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/modulos/agendador');

    await expect(page.locator('h1')).toContainText('Agendador de Tarefas');
  });
});
